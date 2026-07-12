# -*- coding: utf-8 -*-
"""
CervicalAI — XAI + Uncertainty evaluation (Grad-CAM + MC Dropout).

Outputs:
  - models/xai_heatmaps/*.png   (Grad-CAM overlays for a sample of val/test)
  - models/uncertainty_report.json  (MC Dropout stats + flags)

Usage:
  python ml/scripts/eval_xai.py --ckpt models/best_cervical.pt --n 50
  python ml/scripts/eval_xai.py --demo  # works without real data (synthetic)

Requirements:
  pip install pytorch-grad-cam  (already in env)
"""
from __future__ import annotations
import argparse
import json
import pathlib
import random
from typing import List, Dict

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
import cv2

ROOT = pathlib.Path(__file__).parent.parent.parent
MODELS = ROOT / "models"
XAI_DIR = MODELS / "xai_heatmaps"
XAI_DIR.mkdir(parents=True, exist_ok=True)

CLASSES = ["NILM", "LSIL", "HSIL", "SCC", "KOIL"]

# ──────────────────────────────────────────────────────────────────────────────
# Grad-CAM (pytorch-grad-cam if available, else manual hook)
# ──────────────────────────────────────────────────────────────────────────────
def _get_target_layer(net, arch: str):
    if "efficientnet" in arch:
        return net.features[-1]
    if "resnet" in arch:
        return net.layer4
    # fallback
    return list(net.children())[-2]

def gradcam(net: torch.nn.Module, arch: str, x: torch.Tensor, class_idx: int | None = None) -> np.ndarray:
    """Return normalized CAM in [0,1] of shape (H,W) for input x (1,C,H,W)."""
    try:
        from pytorch_grad_cam import GradCAM
        from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

        target_layers = [_get_target_layer(net, arch)]
        cam = GradCAM(model=net, target_layers=target_layers)
        targets = [ClassifierOutputTarget(class_idx)] if class_idx is not None else None
        grayscale = cam(input_tensor=x, targets=targets)
        return grayscale[0]
    except Exception:
        # manual hook fallback
        feats, grads = {}, {}
        layer = _get_target_layer(net, arch)

        def fwd(_m, _i, o): feats["v"] = o.detach()
        def bwd(_m, gi, go): grads["v"] = go[0].detach()

        h1 = layer.register_forward_hook(fwd)
        h2 = layer.register_full_backward_hook(bwd)
        try:
            net.zero_grad(set_to_none=True)
            logits = net(x)
            if class_idx is None:
                class_idx = int(logits.argmax(1).item())
            logits[0, class_idx].backward()
        finally:
            h1.remove(); h2.remove()

        fmap = feats["v"][0]  # (C,h,w)
        w = grads["v"][0].mean(dim=(1, 2))
        cam = torch.relu((w[:, None, None] * fmap).sum(0))
        cam = cam.detach().cpu().numpy()
        if cam.max() <= 0:
            return np.zeros((x.shape[-2], x.shape[-1]), dtype=np.float32)
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        return cam


def overlay_heatmap(bgr: np.ndarray, cam: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    H, W = bgr.shape[:2]
    cam = cv2.resize(cam, (W, H))
    heat = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
    return cv2.addWeighted(bgr, 1 - alpha, heat, alpha, 0)


# ──────────────────────────────────────────────────────────────────────────────
# MC Dropout uncertainty
# ──────────────────────────────────────────────────────────────────────────────
def enable_mc_dropout(model: torch.nn.Module):
    """Force dropout layers to stay on at inference."""
    for m in model.modules():
        if isinstance(m, (torch.nn.Dropout, torch.nn.Dropout2d)):
            m.train()


@torch.no_grad()
def mc_dropout_predict(model: torch.nn.Module, x: torch.Tensor, n_samples: int = 20) -> Dict[str, np.ndarray]:
    """Return mean probs + std (uncertainty) over n forward passes with dropout on."""
    model.eval()
    enable_mc_dropout(model)
    probs = []
    for _ in range(n_samples):
        logits = model(x)
        p = torch.softmax(logits, dim=1)
        probs.append(p.cpu().numpy())
    probs = np.stack(probs, axis=0)  # (T,B,C)
    mean = probs.mean(axis=0)
    std = probs.std(axis=0)
    return {"mean": mean, "std": std, "samples": probs}


def uncertainty_flags(mean: np.ndarray, std: np.ndarray, topk: int = 1) -> Dict:
    """Flag uncertain cases: high entropy or high std on top class."""
    # entropy of mean
    eps = 1e-8
    ent = -(mean * np.log(mean + eps)).sum(axis=1)
    top_idx = mean.argmax(axis=1)
    top_std = std[np.arange(mean.shape[0]), top_idx]
    # thresholds (heuristic, tune on real data)
    uncertain = (ent > 1.2) | (top_std > 0.12)
    return {
        "entropy": ent.round(4).tolist(),
        "top_class_std": top_std.round(4).tolist(),
        "is_uncertain": uncertain.tolist(),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def load_ckpt(path: pathlib.Path):
    ck = torch.load(str(path), map_location="cpu", weights_only=False)
    arch = ck.get("arch", "efficientnet_b0")
    from torchvision import models as tvm
    if "efficientnet_b0" in arch:
        net = tvm.efficientnet_b0(weights=None)
        net.classifier[1] = torch.nn.Linear(net.classifier[1].in_features, len(CLASSES))
    elif "efficientnet_b3" in arch:
        net = tvm.efficientnet_b3(weights=None)
        net.classifier[1] = torch.nn.Linear(net.classifier[1].in_features, len(CLASSES))
    else:
        net = tvm.resnet18(weights=None)
        net.fc = torch.nn.Linear(net.fc.in_features, len(CLASSES))
    # Support both full ckpt and plain state_dict
    state = ck["state_dict"] if isinstance(ck, dict) and "state_dict" in ck else ck
    net.load_state_dict(state, strict=False)
    net.eval()
    # Merge metadata
    if isinstance(ck, dict):
        ck.setdefault("arch", arch)
        ck.setdefault("img_size", 224)
    return net, ck if isinstance(ck, dict) else {"arch": arch, "img_size": 224}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=str(MODELS / "best_cervical.pt"))
    ap.add_argument("--n", type=int, default=30, help="how many images to explain")
    ap.add_argument("--mc", type=int, default=20, help="MC dropout samples")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    dev = "cuda" if torch.cuda.is_available() else "cpu"

    # try real ckpt
    net = None
    ck = None
    if pathlib.Path(args.ckpt).exists():
        try:
            net, ck = load_ckpt(pathlib.Path(args.ckpt))
            net.to(dev)
            print(f"[xai] loaded {args.ckpt} ({ck.get('arch')})")
        except Exception as e:
            print("[xai] failed to load ckpt:", e)

    if net is None or args.demo:
        print("[xai] DEMO mode: using random-init model + synthetic images")
        from torchvision import models as tvm
        net = tvm.efficientnet_b0(weights=None)
        net.classifier[1] = torch.nn.Linear(net.classifier[1].in_features, len(CLASSES))
        net.eval().to(dev)
        ck = {"arch": "efficientnet_b0", "img_size": 224}

    img_size = ck.get("img_size", 224) if ck else 224

    # build a tiny pool of images (real or synthetic)
    imgs: List[np.ndarray] = []
    labels: List[int] = []
    paths: List[str] = []

    # try to pull from processed splits
    try:
        import csv
        for split in ["split_val.csv", "split_test.csv"]:
            p = ROOT / "data" / "processed" / split
            if p.exists():
                for r in list(csv.DictReader(open(p, encoding="utf-8")))[: args.n]:
                    try:
                        im = np.array(Image.open(r["path"]).convert("RGB"))
                        imgs.append(im)
                        labels.append(int(r["label5"]))
                        paths.append(r["path"])
                    except Exception:
                        pass
    except Exception:
        pass

    if not imgs:
        # synthetic
        print("[xai] no real images found — generating synthetic RGB noise")
        for i in range(args.n):
            imgs.append((np.random.rand(256, 256, 3) * 255).astype(np.uint8))
            labels.append(i % 5)
            paths.append(f"synthetic_{i}")

    # preprocess
    mean = np.array(ck.get("mean", [0.485, 0.456, 0.406]), dtype=np.float32)
    std = np.array(ck.get("std", [0.229, 0.224, 0.225]), dtype=np.float32)

    results = []
    for i, (img, y, pth) in enumerate(zip(imgs, labels, paths)):
        # resize + normalize
        small = cv2.resize(img, (img_size, img_size))
        x = (small.astype(np.float32) / 255.0 - mean) / std
        t = torch.from_numpy(x.transpose(2, 0, 1)[None]).to(dev)

        with torch.no_grad():
            logits = net(t)
            prob = torch.softmax(logits, dim=1)[0].cpu().numpy()
            pred = int(prob.argmax())

        # Grad-CAM for predicted class
        cam = gradcam(net, ck.get("arch", "efficientnet_b0"), t, class_idx=pred)
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        overlay = overlay_heatmap(bgr, cam)
        out_name = XAI_DIR / f"{i:03d}_cls{pred}_{CLASSES[pred]}.png"
        cv2.imwrite(str(out_name), overlay)

        # MC Dropout uncertainty
        mc = mc_dropout_predict(net, t, n_samples=args.mc)
        flags = uncertainty_flags(mc["mean"], mc["std"])

        rec = {
            "idx": i,
            "path": pth,
            "true": int(y),
            "pred": pred,
            "probs": prob.round(4).tolist(),
            "uncertainty": {
                "entropy": float(flags["entropy"][0]),
                "top_std": float(flags["top_class_std"][0]),
                "flag": bool(flags["is_uncertain"][0]),
            },
            "heatmap": str(out_name),
        }
        results.append(rec)

    report = {
        "n": len(results),
        "classes": CLASSES,
        "mc_samples": args.mc,
        "samples": results,
        "summary": {
            "flagged_uncertain": sum(r["uncertainty"]["flag"] for r in results),
            "avg_entropy": round(float(np.mean([r["uncertainty"]["entropy"] for r in results])), 4),
        },
    }
    (MODELS / "uncertainty_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[xai] wrote {len(results)} heatmaps -> {XAI_DIR}")
    print(f"[xai] uncertainty_report.json: {report['summary']}")


if __name__ == "__main__":
    main()

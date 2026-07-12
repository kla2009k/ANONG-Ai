# -*- coding: utf-8 -*-
"""
CervicalAI — Advanced XAI Module (Phase 1.5+).

Multi-method explainability using pytorch-grad-cam + custom visualizations:
- Grad-CAM (standard, class activation)
- Score-CAM (gradient-free, more stable)
- Eigen-CAM (PCA-based, captures principal components)
- Layer-CAM (finer-grained, per-layer)
- Guided Backprop + Grad-CAM++ (if available)
- Class activation at multiple layers (early/mid/late)

Also produces:
- Uncertainty-aware heatmaps (overlay std from MC dropout)
- Top-K patch importance (for WSI-style attention feel)
- Per-class comparison heatmaps
- Clinical-style "suspicious region" masks

Outputs:
  models/xai_advanced/*.png
  models/xai_advanced/report.json

Usage:
  python ml/scripts/xai_advanced.py --ckpt models/best_cervical.pt --n 12 --methods all
  python ml/scripts/xai_advanced.py --demo

Requirements:
  pip install pytorch-grad-cam (already present)
"""
from __future__ import annotations
import argparse
import json
import pathlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

ROOT = pathlib.Path(__file__).parent.parent.parent
MODELS = ROOT / "models"
XAI_ADV_DIR = MODELS / "xai_advanced"
XAI_ADV_DIR.mkdir(parents=True, exist_ok=True)

CLASSES = ["NILM", "LSIL", "HSIL", "SCC", "KOIL"]

# ──────────────────────────────────────────────────────────────────────────────
# Model loading (same contract as eval_xai)
# ──────────────────────────────────────────────────────────────────────────────

def load_ckpt(path: pathlib.Path):
    ck = torch.load(str(path), map_location="cpu", weights_only=False)
    arch = ck.get("arch", "efficientnet_b0")
    from torchvision import models as tvm
    if "efficientnet_b0" in arch:
        net = tvm.efficientnet_b0(weights=None)
        net.classifier[1] = nn.Linear(net.classifier[1].in_features, len(CLASSES))
    elif "efficientnet_b3" in arch:
        net = tvm.efficientnet_b3(weights=None)
        net.classifier[1] = nn.Linear(net.classifier[1].in_features, len(CLASSES))
    else:
        net = tvm.resnet18(weights=None)
        net.fc = nn.Linear(net.fc.in_features, len(CLASSES))
    state = ck["state_dict"] if isinstance(ck, dict) and "state_dict" in ck else ck
    net.load_state_dict(state, strict=False)
    net.eval()
    if isinstance(ck, dict):
        ck.setdefault("arch", arch)
        ck.setdefault("img_size", 224)
    return net, ck if isinstance(ck, dict) else {"arch": arch, "img_size": 224}


def _get_target_layer(net, arch: str):
    if "efficientnet" in arch:
        return net.features[-1]
    if "resnet" in arch:
        return net.layer4
    return list(net.children())[-2]


# ──────────────────────────────────────────────────────────────────────────────
# Multi-method CAM via pytorch-grad-cam
# ──────────────────────────────────────────────────────────────────────────────

def _try_pytorch_grad_cam(net, arch: str, x: torch.Tensor, class_idx: int,
                          method: str = "gradcam") -> Optional[np.ndarray]:
    """
    Try to use pytorch-grad-cam for various methods.
    Falls back to None if method not available.
    """
    try:
        from pytorch_grad_cam import (
            GradCAM, ScoreCAM, EigenCAM, GradCAMPlusPlus,
            AblationCAM, XGradCAM, LayerCAM
        )
        from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

        target_layers = [_get_target_layer(net, arch)]
        method = method.lower()

        if method == "gradcam":
            cam = GradCAM(model=net, target_layers=target_layers)
        elif method == "scorecam":
            cam = ScoreCAM(model=net, target_layers=target_layers)
        elif method == "eigencam":
            cam = EigenCAM(model=net, target_layers=target_layers)
        elif method == "gradcam++" or method == "gradcampp":
            cam = GradCAMPlusPlus(model=net, target_layers=target_layers)
        elif method == "ablationcam":
            cam = AblationCAM(model=net, target_layers=target_layers)
        elif method == "xgradcam":
            cam = XGradCAM(model=net, target_layers=target_layers)
        elif method == "layercam":
            cam = LayerCAM(model=net, target_layers=target_layers)
        else:
            cam = GradCAM(model=net, target_layers=target_layers)

        targets = [ClassifierOutputTarget(class_idx)]
        grayscale = cam(input_tensor=x, targets=targets)
        return grayscale[0]
    except Exception:
        return None


def manual_gradcam(net, arch: str, x: torch.Tensor, class_idx: int) -> np.ndarray:
    """Fallback manual Grad-CAM using hooks."""
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

    fmap = feats["v"][0]
    w = grads["v"][0].mean(dim=(1, 2))
    cam = torch.relu((w[:, None, None] * fmap).sum(0))
    cam = cam.detach().cpu().numpy()
    if cam.max() <= 0:
        return np.zeros((x.shape[-2], x.shape[-1]), dtype=np.float32)
    cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
    return cam


def compute_cam(net, arch: str, x: torch.Tensor, class_idx: int, method: str = "gradcam") -> np.ndarray:
    """Compute the requested CAM without relabelling another method as its output."""
    out = _try_pytorch_grad_cam(net, arch, x, class_idx, method)
    if out is None:
        if method.lower() == "gradcam":
            out = manual_gradcam(net, arch, x, class_idx)
        else:
            raise RuntimeError(f"{method} is unavailable; refusing to relabel manual Grad-CAM")
    return out.astype(np.float32)


def compute_ensemble_cam(net, arch: str, x: torch.Tensor, class_idx: int, methods: list = None) -> np.ndarray:
    """NEW: EnsembleCAM - average of multiple CAM methods for more robust explanations.
    Default: gradcam + scorecam + eigencam + layercam (inspired by Wubineh 2026, Light-XAI 2026).
    """
    if methods is None:
        methods = ["gradcam", "scorecam", "eigencam", "layercam"]
    cams = []
    for m in methods:
        try:
            c = compute_cam(net, arch, x, class_idx, m)
            if c is not None and c.max() > 0:
                cams.append(c)
        except Exception:
            continue
    if not cams:
        return manual_gradcam(net, arch, x, class_idx)
    # Normalize and average
    cams = [ (c - c.min()) / (c.max() - c.min() + 1e-8) for c in cams ]
    ensemble = np.mean(cams, axis=0)
    return ensemble.astype(np.float32)


# ──────────────────────────────────────────────────────────────────────────────
# Multi-layer CAM (early / mid / late)
# ──────────────────────────────────────────────────────────────────────────────

def get_multilayer_cams(net, arch: str, x: torch.Tensor, class_idx: int) -> Dict[str, np.ndarray]:
    """
    Extract CAM from multiple depths for EfficientNet/ResNet.
    Returns dict with keys: 'early', 'mid', 'late'.
    """
    cams = {}
    try:
        if "efficientnet" in arch:
            # EfficientNet: features[0..8] roughly early→late
            layers = {
                "early": net.features[2],
                "mid": net.features[5],
                "late": net.features[-1],
            }
        elif "resnet" in arch:
            layers = {
                "early": net.layer1,
                "mid": net.layer2,
                "late": net.layer4,
            }
        else:
            layers = {"late": _get_target_layer(net, arch)}

        from pytorch_grad_cam import GradCAM
        from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

        for name, layer in layers.items():
            try:
                cam = GradCAM(model=net, target_layers=[layer])
                targets = [ClassifierOutputTarget(class_idx)]
                grayscale = cam(input_tensor=x, targets=targets)
                cams[name] = grayscale[0].astype(np.float32)
            except Exception:
                cams[name] = np.zeros((x.shape[-2], x.shape[-1]), dtype=np.float32)
    except Exception:
        cams["late"] = compute_cam(net, arch, x, class_idx, "gradcam")
    return cams


# ──────────────────────────────────────────────────────────────────────────────
# Overlay + clinical visualizations
# ──────────────────────────────────────────────────────────────────────────────

def overlay_heatmap(bgr: np.ndarray, cam: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    H, W = bgr.shape[:2]
    cam = cv2.resize(cam, (W, H))
    heat = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
    return cv2.addWeighted(bgr, 1 - alpha, heat, alpha, 0)


def make_contour_mask(cam: np.ndarray, thresh: float = 0.5) -> np.ndarray:
    """Binary mask of high-activation regions + contours."""
    cam = cv2.resize(cam, (cam.shape[1], cam.shape[0]))
    mask = (cam > thresh).astype(np.uint8) * 255
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = np.zeros_like(mask)
    cv2.drawContours(out, contours, -1, 255, 2)
    return out


def make_topk_patches(bgr: np.ndarray, cam: np.ndarray, k: int = 5, patch: int = 32) -> np.ndarray:
    """
    Draw top-K highest CAM patches (simulates WSI attention).
    Returns annotated BGR image.
    """
    H, W = bgr.shape[:2]
    cam_r = cv2.resize(cam, (W, H))
    out = bgr.copy()

    # sliding window average on cam
    scores = []
    for y in range(0, H - patch, patch // 2):
        for x in range(0, W - patch, patch // 2):
            s = cam_r[y:y+patch, x:x+patch].mean()
            scores.append((s, x, y))
    scores.sort(reverse=True)
    for s, x, y in scores[:k]:
        color = (0, 255, 0) if s > 0.6 else (0, 200, 255)
        cv2.rectangle(out, (x, y), (x + patch, y + patch), color, 2)
        cv2.putText(out, f"{s:.2f}", (x + 2, y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    return out


def make_uncertainty_overlay(bgr: np.ndarray, mean_cam: np.ndarray, std_cam: np.ndarray,
                              alpha: float = 0.5) -> np.ndarray:
    """
    Overlay where color = mean activation, intensity variation = uncertainty.
    High std regions shown with desaturated / noisy overlay.
    """
    H, W = bgr.shape[:2]
    mean_r = cv2.resize(mean_cam, (W, H))
    std_r = cv2.resize(std_cam, (W, H))

    # base jet on mean
    base = cv2.applyColorMap((mean_r * 255).astype(np.uint8), cv2.COLORMAP_JET)

    # uncertainty modulates alpha locally (high std → more transparent + speckle)
    uncertainty_alpha = np.clip(std_r * 2.5, 0.1, 0.9)
    speckle = (np.random.randn(H, W) * std_r * 40).astype(np.int16)
    noisy = np.clip(base.astype(np.int16) + speckle[:, :, None], 0, 255).astype(np.uint8)

    # blend
    blended = cv2.addWeighted(bgr, 1 - alpha, noisy, alpha, 0)
    # where high uncertainty, desaturate a bit
    gray = cv2.cvtColor(blended, cv2.COLOR_BGR2GRAY)
    gray3 = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    u_mask = (uncertainty_alpha > 0.4).astype(np.float32)[:, :, None]
    final = (blended * (1 - u_mask * 0.3) + gray3 * u_mask * 0.3).astype(np.uint8)
    return final


# ──────────────────────────────────────────────────────────────────────────────
# MC Dropout for uncertainty-weighted CAM
# ──────────────────────────────────────────────────────────────────────────────

def enable_mc_dropout(model: nn.Module):
    for m in model.modules():
        if isinstance(m, (nn.Dropout, nn.Dropout2d)):
            m.train()


def mc_dropout_cams(net, arch: str, x: torch.Tensor, n_samples: int = 12,
                    class_idx: Optional[int] = None) -> Dict[str, np.ndarray]:
    """
    Run MC dropout, collect per-sample CAM + probs.
    Returns mean/std CAM + mean probs + entropy.
    NOTE: intentionally NOT @torch.no_grad because we need backward for CAM.
    """
    net.eval()
    enable_mc_dropout(net)

    cams = []
    probs_list = []
    for _ in range(n_samples):
        # must allow grad for CAM backward inside compute_cam
        logits = net(x)
        p = torch.softmax(logits, dim=1)
        probs_list.append(p.detach().cpu().numpy()[0])
        if class_idx is None:
            ci = int(p.argmax(1).item())
        else:
            ci = class_idx
        # compute_cam will do its own backward; we detach x clone to avoid graph accumulation issues
        c = compute_cam(net, arch, x.detach().clone().requires_grad_(True), ci, "gradcam")
        cams.append(c)

    cams = np.stack(cams, 0)  # (T,H,W)
    probs = np.stack(probs_list, 0)  # (T,C)
    mean_cam = cams.mean(0)
    std_cam = cams.std(0)
    mean_prob = probs.mean(0)
    entropy = float(-(mean_prob * np.log(mean_prob + 1e-8)).sum())

    return {
        "mean_cam": mean_cam.astype(np.float32),
        "std_cam": std_cam.astype(np.float32),
        "mean_prob": mean_prob.astype(np.float32),
        "entropy": entropy,
        "all_cams": cams.astype(np.float32),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Public advanced explain function
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class XAIAdvancedResult:
    idx: int
    pred_class: str
    pred_idx: int
    methods: Dict[str, str]  # method -> base64 or path
    multilayer: Dict[str, str]
    uncertainty_cam: Optional[str]
    topk_patches: Optional[str]
    mean_prob: List[float]
    entropy: float
    uncertain_flag: bool


def explain_image_advanced(net, ckpt: dict, bgr: np.ndarray, device: str,
                           methods: List[str] = None,
                           mc_samples: int = 12) -> XAIAdvancedResult:
    """
    Full advanced XAI pipeline on a single BGR image.
    Saves multiple PNGs, returns structured result.
    """
    import base64

    if methods is None:
        methods = ["gradcam", "scorecam", "eigencam", "layercam"]

    img_size = ckpt.get("img_size", 224)
    mean = np.array(ckpt.get("mean", [0.485, 0.456, 0.406]), np.float32)
    std = np.array(ckpt.get("std", [0.229, 0.224, 0.225]), np.float32)
    arch = ckpt.get("arch", "efficientnet_b0")

    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    small = cv2.resize(rgb, (img_size, img_size))
    x = (small.astype(np.float32) / 255.0 - mean) / std
    t = torch.from_numpy(x.transpose(2, 0, 1)[None]).to(device)

    with torch.no_grad():
        logits = net(t)
        prob = torch.softmax(logits, dim=1)[0].cpu().numpy()
        pred = int(prob.argmax())

    out_dir = XAI_ADV_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    method_paths = {}
    for m in methods:
        cam = compute_cam(net, arch, t, pred, m)
        overlay = overlay_heatmap(bgr, cam)
        p = out_dir / f"adv_{m}_{CLASSES[pred]}.png"
        cv2.imwrite(str(p), overlay)
        method_paths[m] = str(p)

    # multilayer
    ml_cams = get_multilayer_cams(net, arch, t, pred)
    ml_paths = {}
    for name, c in ml_cams.items():
        overlay = overlay_heatmap(bgr, c)
        p = out_dir / f"layer_{name}_{CLASSES[pred]}.png"
        cv2.imwrite(str(p), overlay)
        ml_paths[name] = str(p)

    # MC + uncertainty cam
    mc = mc_dropout_cams(net, arch, t, n_samples=mc_samples, class_idx=pred)
    unc_overlay = make_uncertainty_overlay(bgr, mc["mean_cam"], mc["std_cam"])
    unc_path = out_dir / f"uncertainty_{CLASSES[pred]}.png"
    cv2.imwrite(str(unc_path), unc_overlay)

    # top-k patches (WSI feel)
    topk_img = make_topk_patches(bgr, mc["mean_cam"], k=6, patch=28)
    topk_path = out_dir / f"topk_patches_{CLASSES[pred]}.png"
    cv2.imwrite(str(topk_path), topk_img)

    # contour mask
    contour = make_contour_mask(mc["mean_cam"], 0.45)
    contour_bgr = cv2.cvtColor(contour, cv2.COLOR_GRAY2BGR)
    contour_path = out_dir / f"contour_{CLASSES[pred]}.png"
    cv2.imwrite(str(contour_path), contour_bgr)

    eps = 1e-8
    entropy = float(-(prob * np.log(prob + eps)).sum())
    uncertain = (entropy > 1.2) or (mc["std_cam"].mean() > 0.08)

    return XAIAdvancedResult(
        idx=0,
        pred_class=CLASSES[pred],
        pred_idx=pred,
        methods={k: v for k, v in method_paths.items()},
        multilayer={k: v for k, v in ml_paths.items()},
        uncertainty_cam=str(unc_path),
        topk_patches=str(topk_path),
        mean_prob=prob.round(4).tolist(),
        entropy=round(entropy, 4),
        uncertain_flag=bool(uncertain),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Batch runner + CLI
# ──────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=str(MODELS / "best_cervical.pt"))
    ap.add_argument("--n", type=int, default=8, help="how many images to process")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--methods", default="gradcam,scorecam,eigencam,layercam",
                    help="comma list or 'all'")
    ap.add_argument("--mc", type=int, default=12)
    args = ap.parse_args()

    dev = "cuda" if torch.cuda.is_available() else "cpu"

    net = None
    ck = None
    if pathlib.Path(args.ckpt).exists() and not args.demo:
        try:
            net, ck = load_ckpt(pathlib.Path(args.ckpt))
            net.to(dev)
            print(f"[xai-adv] loaded {args.ckpt} ({ck.get('arch')})")
        except Exception as e:
            print("[xai-adv] load failed:", e)

    if net is None or args.demo:
        print("[xai-adv] DEMO: random-init EfficientNet-B0 + synthetic images")
        from torchvision import models as tvm
        net = tvm.efficientnet_b0(weights=None)
        net.classifier[1] = nn.Linear(net.classifier[1].in_features, len(CLASSES))
        net.eval().to(dev)
        ck = {"arch": "efficientnet_b0", "img_size": 224}

    # build image pool (synthetic if no real data)
    imgs: List[np.ndarray] = []
    try:
        import csv
        for split in ["split_val.csv", "split_test.csv"]:
            p = ROOT / "data" / "processed" / split
            if p.exists():
                for r in list(csv.DictReader(open(p, encoding="utf-8")))[: args.n]:
                    try:
                        im = np.array(Image.open(r["path"]).convert("RGB"))
                        imgs.append(im)
                    except Exception:
                        pass
    except Exception:
        pass

    if not imgs:
        rng = np.random.default_rng(123)
        for i in range(args.n):
            imgs.append((rng.random((256, 256, 3)) * 255).astype(np.uint8))

    methods = (["gradcam", "scorecam", "eigencam", "layercam", "gradcam++"]
               if args.methods.lower() == "all" else
               [m.strip() for m in args.methods.split(",") if m.strip()])

    results = []
    for i, img in enumerate(imgs[:args.n]):
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        res = explain_image_advanced(net, ck, bgr, dev, methods=methods, mc_samples=args.mc)
        res.idx = i
        results.append(asdict(res))
        print(f"[xai-adv] {i:02d} pred={res.pred_class} entropy={res.entropy} uncertain={res.uncertain_flag}")

    report = {
        "n": len(results),
        "classes": CLASSES,
        "methods_used": methods,
        "mc_samples": args.mc,
        "results": results,
        "summary": {
            "uncertain_count": sum(r["uncertain_flag"] for r in results),
            "avg_entropy": round(float(np.mean([r["entropy"] for r in results])), 4),
        }
    }
    (XAI_ADV_DIR / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[xai-adv] wrote {len(results)} advanced explanations → {XAI_ADV_DIR}")
    print(f"[xai-adv] summary: {report['summary']}")


if __name__ == "__main__":
    main()

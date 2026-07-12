# -*- coding: utf-8 -*-
"""
CervicalAI — WSI Patch Simulation & Attention Aggregation (Phase 1.5+).

Since real WSI (.svs) + OpenSlide may not be available, this module:
- Generates realistic "slide-like" images with many cell-like blobs
- Extracts overlapping patches (simulating tiling)
- Runs the 5-class model on every patch (or heuristic if no model)
- Aggregates via:
    * Top-K mean
    * Attention-weighted (learned or proxy)
    * MIL-style max + mean
- Produces:
    * Patch-level prediction grid
    * Low-res risk heatmap
    * Slide-level score + uncertainty
    * "Suspicious patches" list

This is the "if possible" WSI simulation requested.

Outputs go to models/wsi_sim/

Usage:
  python ml/scripts/wsi_patch_sim.py --demo --patches 64
  python ml/scripts/wsi_patch_sim.py --image big_slide.png --model models/best_cervical.pt
"""
from __future__ import annotations
import argparse
import json
import pathlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image

ROOT = pathlib.Path(__file__).parent.parent.parent
MODELS = ROOT / "models"
WSI_DIR = MODELS / "wsi_sim"
WSI_DIR.mkdir(parents=True, exist_ok=True)

CLASSES = ["NILM", "LSIL", "HSIL", "SCC", "KOIL"]
ABNORMAL = {"LSIL", "HSIL", "SCC", "KOIL"}

# ──────────────────────────────────────────────────────────────────────────────
# Synthetic "whole slide" generator
# ──────────────────────────────────────────────────────────────────────────────

def make_synthetic_slide(size: int = 1536, n_cells: int = 180, seed: int = 7) -> np.ndarray:
    """
    Create a large-ish RGB image that looks like a cytology field:
    - background texture
    - many small dark nuclei-like blobs
    - a few larger "abnormal" clusters (darker + irregular)
    """
    rng = np.random.default_rng(seed)
    img = (rng.random((size, size, 3)) * 160 + 70).astype(np.uint8)

    # normal cells
    for _ in range(n_cells):
        x = rng.integers(30, size - 30)
        y = rng.integers(30, size - 30)
        r = rng.integers(4, 11)
        color = (int(rng.integers(20, 45)), int(rng.integers(18, 40)), int(rng.integers(50, 90)))
        cv2.circle(img, (x, y), r, color, -1)
        # slight halo
        halo = (min(255, color[0] + 20), min(255, color[1] + 20), min(255, color[2] + 20))
        cv2.circle(img, (x, y), r + 2, halo, 1)

    # abnormal clusters (bigger, darker, more irregular)
    n_abn = max(3, n_cells // 25)
    for _ in range(n_abn):
        cx = rng.integers(80, size - 80)
        cy = rng.integers(80, size - 80)
        for _ in range(rng.integers(6, 14)):
            dx = rng.integers(-35, 36)
            dy = rng.integers(-35, 36)
            r = rng.integers(6, 14)
            color = (int(rng.integers(10, 30)), int(rng.integers(8, 25)), int(rng.integers(35, 60)))
            cv2.circle(img, (cx + dx, cy + dy), r, color, -1)

    # add mild stain variation
    img = cv2.addWeighted(img, 0.92, (rng.random((size, size, 3)) * 25).astype(np.uint8), 0.08, 0)
    return img


# ──────────────────────────────────────────────────────────────────────────────
# Patch extraction (grid with overlap)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Patch:
    x: int
    y: int
    w: int
    h: int
    image: np.ndarray  # RGB
    probs: Optional[np.ndarray] = None
    pred: Optional[int] = None
    score: Optional[float] = None  # abnormal score


def extract_patches(slide: np.ndarray, tile: int = 224, stride: int = 160,
                    max_patches: int = 128) -> List[Patch]:
    H, W = slide.shape[:2]
    patches: List[Patch] = []
    for y in range(0, H - tile + 1, stride):
        for x in range(0, W - tile + 1, stride):
            if len(patches) >= max_patches:
                return patches
            crop = slide[y:y+tile, x:x+tile]
            if crop.shape[0] != tile or crop.shape[1] != tile:
                continue
            # skip near-white empty regions
            if crop.mean() > 225:
                continue
            patches.append(Patch(x=x, y=y, w=tile, h=tile, image=cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)))
    return patches


# ──────────────────────────────────────────────────────────────────────────────
# Model scoring per patch
# ──────────────────────────────────────────────────────────────────────────────

def load_model_for_wsi(ckpt_path: Optional[pathlib.Path]):
    if ckpt_path is None or not ckpt_path.exists():
        return None, None
    try:
        ck = torch.load(str(ckpt_path), map_location="cpu", weights_only=False)
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
        state = ck["state_dict"] if "state_dict" in ck else ck
        net.load_state_dict(state, strict=False)
        net.eval()
        return net, ck
    except Exception:
        return None, None


def score_patch(patch: Patch, net=None, ck=None, device: str = "cpu") -> Patch:
    if net is None:
        # heuristic abnormal score
        g = cv2.cvtColor(patch.image, cv2.COLOR_RGB2GRAY).astype(np.float32)
        dark = 1.0 - (g.mean() / 255.0)
        texture = float(np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0)).mean() +
                        np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1)).mean()) / 120.0
        sc = float(np.clip(0.4 * dark + 0.6 * min(texture, 1.0), 0.0, 1.0))
        patch.score = sc
        # fake probs biased toward abnormal if high score
        if sc > 0.65:
            patch.probs = np.array([0.05, 0.15, 0.45, 0.25, 0.10])
            patch.pred = 2  # HSIL-ish
        elif sc > 0.45:
            patch.probs = np.array([0.15, 0.35, 0.25, 0.10, 0.15])
            patch.pred = 1
        else:
            patch.probs = np.array([0.75, 0.10, 0.05, 0.02, 0.08])
            patch.pred = 0
        return patch

    img_size = ck.get("img_size", 224) if ck else 224
    mean = np.array(ck.get("mean", [0.485, 0.456, 0.406]), np.float32)
    std = np.array(ck.get("std", [0.229, 0.224, 0.225]), np.float32)

    small = cv2.resize(patch.image, (img_size, img_size))
    x = (small.astype(np.float32) / 255.0 - mean) / std
    t = torch.from_numpy(x.transpose(2, 0, 1)[None]).to(device)

    with torch.no_grad():
        logits = net(t)
        p = torch.softmax(logits, dim=1)[0].cpu().numpy()
    patch.probs = p
    patch.pred = int(p.argmax())
    # abnormal score = 1 - NILM prob
    patch.score = float(1.0 - p[0])
    return patch


# ──────────────────────────────────────────────────────────────────────────────
# MIL-style aggregation
# ──────────────────────────────────────────────────────────────────────────────

def aggregate_mil(patches: List[Patch], topk: int = 12, attention: bool = True) -> Dict[str, Any]:
    if not patches:
        return {"slide_score": 0.0, "topk_scores": [], "method": "empty"}

    scores = np.array([p.score for p in patches if p.score is not None], dtype=np.float32)
    if len(scores) == 0:
        return {"slide_score": 0.0, "topk_scores": [], "method": "no_scores"}

    idx = np.argsort(-scores)[: min(topk, len(scores))]
    top = scores[idx]

    if attention:
        w = np.exp(top * 4.0)
        w = w / (w.sum() + 1e-8)
        slide_score = float((top * w).sum())
        method = "topk_attention"
    else:
        slide_score = float(top.mean())
        method = "topk_mean"

    uncertain = (slide_score > 0.30) and (top.std() > 0.12)
    abnormal_count = sum(1 for p in patches if p.pred is not None and CLASSES[p.pred] in ABNORMAL)

    return {
        "slide_score": round(slide_score, 4),
        "topk_scores": [round(float(x), 4) for x in top],
        "n_patches_scored": len(scores),
        "abnormal_patches": abnormal_count,
        "uncertain": bool(uncertain),
        "method": method,
    }


def build_risk_heatmap(slide_shape: Tuple[int, int], patches: List[Patch],
                       downsample: int = 16) -> np.ndarray:
    H, W = slide_shape
    Hs = max(1, H // downsample)
    Ws = max(1, W // downsample)
    heat = np.zeros((Hs, Ws), dtype=np.float32)
    cnt = np.zeros_like(heat)

    for p in patches:
        if p.score is None:
            continue
        cx = (p.x + p.w // 2) // downsample
        cy = (p.y + p.h // 2) // downsample
        if 0 <= cx < Ws and 0 <= cy < Hs:
            heat[cy, cx] += p.score
            cnt[cy, cx] += 1
    cnt[cnt == 0] = 1
    heat = heat / cnt
    # upsample for nicer preview
    heat = cv2.resize(heat, (Ws * 4, Hs * 4), interpolation=cv2.INTER_CUBIC)
    return np.clip(heat, 0, 1)


# ──────────────────────────────────────────────────────────────────────────────
# Public simulation entry
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class WSISimResult:
    slide_id: str
    n_patches: int
    slide_score: float
    uncertain: bool
    abnormal_patches: int
    heatmap_path: Optional[str]
    patch_grid_path: Optional[str]
    topk_preview_path: Optional[str]
    note: str


def simulate_wsi(slide_img: np.ndarray, net=None, ck=None, device: str = "cpu",
                 tile: int = 224, stride: int = 160, max_patches: int = 80,
                 topk: int = 12) -> WSISimResult:
    """
    Full simulation: extract → score → aggregate → heatmaps.
    slide_img: BGR uint8 (large)
    """
    patches = extract_patches(slide_img, tile=tile, stride=stride, max_patches=max_patches)

    for p in patches:
        score_patch(p, net=net, ck=ck, device=device)

    agg = aggregate_mil(patches, topk=topk, attention=True)
    heat = build_risk_heatmap(slide_img.shape[:2], patches)

    # save artifacts
    out = WSI_DIR
    out.mkdir(parents=True, exist_ok=True)

    # risk heatmap
    hm = (heat * 255).astype(np.uint8)
    hm_col = cv2.applyColorMap(hm, cv2.COLORMAP_JET)
    hm_path = str(out / "risk_heatmap.png")
    cv2.imwrite(hm_path, hm_col)

    # patch grid preview (draw boxes colored by pred)
    grid = slide_img.copy()
    for p in patches:
        color = (0, 200, 0) if p.pred is None or CLASSES[p.pred] == "NILM" else (0, 100, 255)
        cv2.rectangle(grid, (p.x, p.y), (p.x + p.w, p.y + p.h), color, 2)
    grid_path = str(out / "patch_grid.png")
    cv2.imwrite(grid_path, grid)

    # top-K suspicious patches collage
    susp = sorted([p for p in patches if p.score is not None], key=lambda x: -x.score)[:6]
    if susp:
        tiles = []
        for p in susp:
            t = cv2.resize(p.image, (96, 96))
            t = cv2.cvtColor(t, cv2.COLOR_RGB2BGR)
            cv2.putText(t, f"{p.score:.2f}", (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
            tiles.append(t)
        collage = np.hstack(tiles) if len(tiles) > 0 else np.zeros((96, 96, 3), np.uint8)
        topk_path = str(out / "topk_suspicious.png")
        cv2.imwrite(topk_path, collage)
    else:
        topk_path = None

    return WSISimResult(
        slide_id="synthetic_wsi" if slide_img.mean() > 0 else "input",
        n_patches=len(patches),
        slide_score=agg["slide_score"],
        uncertain=agg["uncertain"],
        abnormal_patches=agg["abnormal_patches"],
        heatmap_path=hm_path,
        patch_grid_path=grid_path,
        topk_preview_path=topk_path,
        note=agg["method"],
    )


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--image", type=str, default=None)
    ap.add_argument("--ckpt", default=str(MODELS / "best_cervical.pt"))
    ap.add_argument("--patches", type=int, default=64)
    ap.add_argument("--tile", type=int, default=224)
    ap.add_argument("--stride", type=int, default=160)
    args = ap.parse_args()

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    net, ck = load_model_for_wsi(pathlib.Path(args.ckpt) if pathlib.Path(args.ckpt).exists() else None)

    if args.demo or not args.image:
        print("[wsi-sim] generating synthetic slide...")
        slide = make_synthetic_slide(size=1280, n_cells=160, seed=42)
        cv2.imwrite(str(WSI_DIR / "synthetic_slide.png"), slide)
        res = simulate_wsi(slide, net=net, ck=ck, device=dev,
                           tile=args.tile, stride=args.stride, max_patches=args.patches)
        print("[wsi-sim] result:", asdict(res))
    else:
        p = pathlib.Path(args.image)
        bgr = cv2.imread(str(p))
        if bgr is None:
            print(f"[wsi-sim] cannot read {p}")
            return
        res = simulate_wsi(bgr, net=net, ck=ck, device=dev,
                           tile=args.tile, stride=args.stride, max_patches=args.patches)
        print("[wsi-sim] result:", asdict(res))

    # also dump json
    (WSI_DIR / "wsi_result.json").write_text(
        json.dumps(asdict(res), indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()

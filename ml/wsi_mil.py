#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CervicalAI — Whole-Slide Image (WSI) + Multiple Instance Learning (MIL) Sketch

Phase 2 Differentiator (Stretch for Phase 1.5).

REAL-WORLD REALITY (from DEEP_RESEARCH Finding 2.3):
- A single Pap slide can contain 50,000–300,000 cells.
- Clinical label is at SLIDE level (Bethesda category), not per-cell.
- This is a classic MIL problem: bag = slide, instances = patches/cells.

WHY WE STARTED WITH SINGLE-CELL (Phase 1):
- SIPaKMeD / Herlev / RepoMedUNM are single-cell crops → clean benchmark.
- Full WSI requires OpenSlide + tissue detection + patch extraction + aggregation.
- Much heavier (storage, RAM, time). Not required for POC.

THIS MODULE PROVIDES:
- Stub loader using OpenSlide (graceful fallback if not installed / no .svs).
- Patch extraction (histolab-style or simple grid).
- Attention-MIL sketch (no real weights; architecture only).
- Heatmap aggregation stub (slide-level risk map).
- Synthetic WSI generator for pipeline testing.

Dependencies (optional):
  pip install openslide-python histolab
  (also need openslide system lib on Windows: use conda or prebuilt)

On Windows without OpenSlide binary, this module degrades gracefully to stubs.

References:
- DEEP_RESEARCH Finding 2.3, 7, 37 (Nature Comms 2025 MIL + Att-Transformer).
- arXiv 2407.11486 "large foundation model for cervical cytopathology WSI".
- histolab, CLAM, DSMIL, TransMIL literature.
"""

from __future__ import annotations
import argparse
import pathlib
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any

import numpy as np
import cv2
from PIL import Image

# Optional imports — degrade gracefully
try:
    import openslide
    HAS_OPENSLIDE = True
except Exception:
    HAS_OPENSLIDE = False

try:
    # histolab is heavy; we only use a tiny subset if present
    from histolab.slide import Slide
    from histolab.tiler import GridTiler
    HAS_HISTOLAB = True
except Exception:
    HAS_HISTOLAB = False

# ──────────────────────────────────────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Patch:
    x: int
    y: int
    w: int
    h: int
    image: np.ndarray  # RGB uint8 (H,W,3)
    score: Optional[float] = None  # instance-level abnormal score


@dataclass
class SlideResult:
    slide_id: str
    n_patches: int
    topk_scores: List[float]
    slide_score: float
    uncertain: bool
    heatmap_path: Optional[str] = None
    note: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# WSI loading (stub)
# ──────────────────────────────────────────────────────────────────────────────

def load_wsi(path: pathlib.Path) -> Any:
    """Return openslide object or None if unavailable."""
    if not HAS_OPENSLIDE:
        print("[wsi] openslide not available — WSI I/O disabled.")
        return None
    try:
        return openslide.OpenSlide(str(path))
    except Exception as e:
        print(f"[wsi] failed to open {path}: {e}")
        return None


def get_level_dimensions(slide: Any, level: int = 0) -> Tuple[int, int]:
    if slide is None:
        return (4096, 4096)
    return slide.level_dimensions[level]


def read_region(slide: Any, x: int, y: int, w: int, h: int, level: int = 0) -> np.ndarray:
    """Read a region as RGB np.ndarray."""
    if slide is None:
        # synthetic placeholder
        return (np.random.rand(h, w, 3) * 200 + 30).astype(np.uint8)
    region = slide.read_region((x, y), level, (w, h)).convert("RGB")
    return np.array(region)


# ──────────────────────────────────────────────────────────────────────────────
# Patch extraction (grid or histolab)
# ──────────────────────────────────────────────────────────────────────────────

def extract_grid_patches(slide: Any, tile_size: int = 512, stride: int = 256,
                         max_patches: int = 200) -> List[Patch]:
    """Simple grid extraction with background skip heuristic."""
    W, H = get_level_dimensions(slide, 0)
    patches: List[Patch] = []
    for y in range(0, H - tile_size, stride):
        for x in range(0, W - tile_size, stride):
            if len(patches) >= max_patches:
                return patches
            img = read_region(slide, x, y, tile_size, tile_size)
            # crude tissue detection: skip near-white
            if img.mean() > 230:
                continue
            patches.append(Patch(x=x, y=y, w=tile_size, h=tile_size, image=img))
    return patches


def extract_histolab_patches(slide_path: pathlib.Path, tile_size: int = 512,
                             max_patches: int = 200) -> List[Patch]:
    """Use histolab GridTiler if available."""
    if not HAS_HISTOLAB:
        print("[wsi] histolab not available — falling back to grid.")
        fake = None
        return extract_grid_patches(fake, tile_size=tile_size, max_patches=max_patches)
    try:
        s = Slide(str(slide_path), processed_path=str(slide_path.parent / "processed"))
        tiler = GridTiler(tile_size=(tile_size, tile_size), level=0, check_tissue=True)
        patches = []
        for tile in tiler(s):
            if len(patches) >= max_patches:
                break
            arr = np.array(tile.image.convert("RGB"))
            patches.append(Patch(x=tile.coords[0], y=tile.coords[1], w=tile_size, h=tile_size, image=arr))
        return patches
    except Exception as e:
        print(f"[wsi] histolab failed: {e} — grid fallback.")
        return extract_grid_patches(None, tile_size=tile_size, max_patches=max_patches)


# ──────────────────────────────────────────────────────────────────────────────
# Instance classifier stub (plug in your 5-class model here)
# ──────────────────────────────────────────────────────────────────────────────

def instance_score(patch: Patch, model_forward_fn=None) -> float:
    """
    Return abnormal score [0,1] for a patch.
    In real code: run your EfficientNet (or MIL backbone) on patch → abnormal logit.
    Here: simple heuristic on darkness/texture (demo only).
    """
    import cv2
    if model_forward_fn is not None:
        return float(model_forward_fn(patch.image))
    g = cv2.cvtColor(patch.image, cv2.COLOR_RGB2GRAY).astype(np.float32)
    dark = 1.0 - (g.mean() / 255.0)
    texture = float(np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0)).mean() +
                    np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1)).mean()) / 100.0
    score = np.clip(0.3 * dark + 0.7 * min(texture, 1.0), 0.0, 1.0)
    return float(score)


# ──────────────────────────────────────────────────────────────────────────────
# MIL aggregation (mean top-K + attention stub)
# ──────────────────────────────────────────────────────────────────────────────

def mil_aggregate(scores: List[float], topk: int = 20, attention: bool = False) -> Dict[str, Any]:
    """
    Simple MIL: take top-K instance scores, mean or attention-weighted.
    attention=True → stub for learned attention (weights proportional to score here).
    """
    if not scores:
        return {"slide_score": 0.0, "topk": [], "note": "no patches"}
    s = np.array(scores, dtype=np.float32)
    k = min(topk, len(s))
    idx = np.argsort(-s)[:k]
    top_scores = s[idx].tolist()
    if attention:
        w = np.exp(s[idx] * 3)
        w = w / (w.sum() + 1e-8)
        slide_score = float((s[idx] * w).sum())
    else:
        slide_score = float(np.mean(top_scores))
    uncertain = (slide_score > 0.25) and (np.std(top_scores) > 0.15)
    return {
        "slide_score": round(slide_score, 4),
        "topk": [round(x, 4) for x in top_scores],
        "uncertain": bool(uncertain),
        "n_instances": len(scores),
        "method": "topk_mean" if not attention else "topk_attention_stub"
    }


# ──────────────────────────────────────────────────────────────────────────────
# Heatmap builder (low-res risk map)
# ──────────────────────────────────────────────────────────────────────────────

def build_risk_heatmap(patches: List[Patch], slide_w: int, slide_h: int,
                       downsample: int = 32) -> np.ndarray:
    """
    Create a coarse risk map at slide level (downsampled).
    Returns (H', W') float32 [0,1].
    """
    import cv2
    Hs = max(1, slide_h // downsample)
    Ws = max(1, slide_w // downsample)
    heat = np.zeros((Hs, Ws), dtype=np.float32)
    count = np.zeros_like(heat)
    for p in patches:
        if p.score is None:
            continue
        cx = (p.x + p.w // 2) // downsample
        cy = (p.y + p.h // 2) // downsample
        if 0 <= cx < Ws and 0 <= cy < Hs:
            heat[cy, cx] += p.score
            count[cy, cx] += 1
    count[count == 0] = 1
    heat = heat / count
    # upsample to nicer size
    heat = cv2.resize(heat, (Ws * 4, Hs * 4), interpolation=cv2.INTER_CUBIC)
    return np.clip(heat, 0, 1)


# ──────────────────────────────────────────────────────────────────────────────
# Full pipeline stub
# ──────────────────────────────────────────────────────────────────────────────

def process_wsi_stub(slide_path: Optional[pathlib.Path], max_patches: int = 100,
                     topk: int = 20) -> SlideResult:
    """
    End-to-end stub: load → extract → score → aggregate.
    If no real slide: uses synthetic grid.
    """
    slide = load_wsi(slide_path) if slide_path and slide_path.exists() else None
    patches = extract_grid_patches(slide, max_patches=max_patches)
    scores = []
    for p in patches:
        sc = instance_score(p)
        p.score = sc
        scores.append(sc)

    agg = mil_aggregate(scores, topk=topk, attention=True)
    W, H = get_level_dimensions(slide, 0)
    heat = build_risk_heatmap(patches, W, H)

    # save tiny preview heatmap
    out_dir = pathlib.Path("models/wsi_preview")
    out_dir.mkdir(parents=True, exist_ok=True)
    hm_path = None
    if len(heat) > 0:
        hm_img = (heat * 255).astype(np.uint8)
        hm_img = cv2.applyColorMap(hm_img, cv2.COLORMAP_JET)
        hm_path = str(out_dir / f"{slide_path.stem if slide_path else 'synthetic'}_risk.png")
        cv2.imwrite(hm_path, hm_img)

    return SlideResult(
        slide_id=slide_path.name if slide_path else "synthetic_wsi",
        n_patches=len(patches),
        topk_scores=agg["topk"],
        slide_score=agg["slide_score"],
        uncertain=agg["uncertain"],
        heatmap_path=hm_path,
        note=agg.get("method", "") + " | " + ("openslide" if slide else "synthetic")
    )


# ──────────────────────────────────────────────────────────────────────────────
# Synthetic WSI generator (for pipeline tests)
# ──────────────────────────────────────────────────────────────────────────────

def make_synthetic_wsi(size: int = 2048, n_abnormal: int = 8, seed: int = 123) -> np.ndarray:
    """Create a fake 'slide' RGB image with a few abnormal dark blobs."""
    rng = np.random.default_rng(seed)
    img = (rng.random((size, size, 3)) * 200 + 40).astype(np.uint8)
    for _ in range(n_abnormal):
        cx = rng.integers(100, size - 100)
        cy = rng.integers(100, size - 100)
        r = rng.integers(20, 60)
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < size and 0 <= y < size:
                        img[y, x] = [40, 30, 80]  # dark "abnormal" tint
    return img


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--slide", type=str, default=None)
    ap.add_argument("--max-patches", type=int, default=80)
    args = ap.parse_args()

    if args.demo or not args.slide:
        print("[wsi] synthetic WSI MIL demo...")
        fake = make_synthetic_wsi()
        # write a fake "slide" as png so we can pretend
        out = pathlib.Path("models/wsi_preview/synthetic_slide.png")
        out.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(fake).save(out)
        res = process_wsi_stub(None, max_patches=args.max_patches)
        print("[wsi] result:", res)
    else:
        p = pathlib.Path(args.slide)
        res = process_wsi_stub(p, max_patches=args.max_patches)
        print("[wsi] result:", res)


if __name__ == "__main__":
    main()

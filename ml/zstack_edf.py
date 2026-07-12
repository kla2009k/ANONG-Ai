#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CervicalAI — Z-stack / EDF (Extended Depth of Field) Support Stub

Phase 1.5 Differentiator: Multi-plane / multi-channel cytology input.

WHY THIS MATTERS (from DEEP_RESEARCH Finding 6):
- Cytology is inherently a 3D problem: cells distributed across several µm thickness.
- Depth of field of high-power objectives <1 µm.
- Chromatin texture (key malignancy cue) is 3D; 2D is a projection loss.
- Hologic Genius FDA-cleared 2024 uses "volumetric imaging" (z-stack) — market validated.
- True tomography (VisionGate Cell-CT) is too expensive for LMIC.

FEASIBLE PATH FOR LMIC (this module):
A) EDF fusion → single sharp 2D image (practical, works with existing 2D pipeline).
B) Multi-channel input (3–7 focal planes stacked as extra channels) → 2D CNN with more input channels.
C) Lightweight 3D-CNN / 2.5D attention (future, stubbed).

This file provides:
- EDF fusion (Laplacian pyramid + max selection, or simple focus measure).
- Z-stack loader (directory of planes or multi-page TIFF).
- Multi-channel tensor builder.
- Stub for 3D-CNN (placeholder, raises NotImplemented until data exists).
- Unit-test friendly synthetic generator.

No public z-stack Pap dataset ready-to-use (ISBI 2015 is tiny volume, 20 planes).
Real deployment needs scanner with z-stack capability or manual focal stepping.

References:
- DEEP_RESEARCH Finding 6, B7 (ISBI 2015 volume).
- "A framework for nucleus and overlapping cytoplasm segmentation in cervical cytology extended depth of field and volume images" — CMIG 2017.
- Hologic Genius volumetric (FDA DEN210035).
"""

from __future__ import annotations
import argparse
import pathlib
from typing import List, Tuple, Optional, Dict

import numpy as np
from PIL import Image
import cv2

# ──────────────────────────────────────────────────────────────────────────────
# Focus measure + EDF fusion (Laplacian energy)
# ──────────────────────────────────────────────────────────────────────────────

def laplacian_energy(gray: np.ndarray) -> np.ndarray:
    """Return per-pixel focus energy (Laplacian variance style)."""
    lap = cv2.Laplacian(gray.astype(np.float32), cv2.CV_32F, ksize=3)
    return np.abs(lap)


def edf_fuse_laplacian(planes: List[np.ndarray], kernel: int = 5) -> np.ndarray:
    """
    Fuse z-stack into one EDF image using max-selection on Laplacian energy.
    planes: list of HxWx3 uint8 RGB images (same size).
    Returns fused RGB uint8.
    """
    if not planes:
        raise ValueError("empty z-stack")
    if len(planes) == 1:
        return planes[0]

    # ensure same size
    H, W = planes[0].shape[:2]
    planes = [cv2.resize(p, (W, H)) for p in planes]

    energies = []
    for p in planes:
        g = cv2.cvtColor(p, cv2.COLOR_RGB2GRAY)
        en = laplacian_energy(g)
        # light blur to reduce noise in selection
        en = cv2.GaussianBlur(en, (kernel, kernel), 0)
        energies.append(en)

    stack = np.stack(energies, axis=0)  # (Z,H,W)
    best = np.argmax(stack, axis=0)     # (H,W)

    fused = np.zeros((H, W, 3), dtype=np.uint8)
    for z, p in enumerate(planes):
        mask = (best == z)
        fused[mask] = p[mask]
    return fused


def edf_fuse_pyramid(planes: List[np.ndarray], levels: int = 4) -> np.ndarray:
    """
    More advanced: Laplacian pyramid max selection (higher quality, slower).
    Fallback to simple if cv2.pyrDown issues.
    """
    if len(planes) <= 1:
        return planes[0] if planes else np.zeros((224, 224, 3), np.uint8)
    # simple wrapper → use laplacian max for robustness
    return edf_fuse_laplacian(planes)


# ──────────────────────────────────────────────────────────────────────────────
# Z-stack I/O
# ──────────────────────────────────────────────────────────────────────────────

def load_zstack_from_dir(dir_path: pathlib.Path, pattern: str = "*.png") -> List[np.ndarray]:
    """Load sorted planes from a directory (plane_000.png, plane_001.png ... or any glob order)."""
    files = sorted(dir_path.glob(pattern))
    planes = []
    for f in files:
        im = np.array(Image.open(f).convert("RGB"))
        planes.append(im)
    return planes


def load_zstack_multipage_tiff(path: pathlib.Path) -> List[np.ndarray]:
    """Load multi-page TIFF (each page = focal plane)."""
    planes = []
    with Image.open(path) as img:
        n = getattr(img, "n_frames", 1)
        for i in range(n):
            img.seek(i)
            planes.append(np.array(img.convert("RGB")))
    return planes


def save_zstack_as_multipage(planes: List[np.ndarray], out_path: pathlib.Path):
    """Save list of RGB arrays as multi-page TIFF."""
    pil_planes = [Image.fromarray(p) for p in planes]
    pil_planes[0].save(out_path, save_all=True, append_images=pil_planes[1:])


# ──────────────────────────────────────────────────────────────────────────────
# Multi-channel tensor builder (for 2D CNN with extra channels)
# ──────────────────────────────────────────────────────────────────────────────

def build_multichannel_tensor(planes: List[np.ndarray], target_size: int = 224,
                               max_planes: int = 7) -> np.ndarray:
    """
    Stack up to max_planes focal planes along channel dim → (C*Z, H, W) float32 normalized.
    If fewer planes, replicate last or pad with zeros (configurable).
    Returns shape (C*Z, H, W) ready for model forward (no batch dim).
    """
    if not planes:
        raise ValueError("no planes")
    # resize all
    resized = [cv2.resize(p, (target_size, target_size)) for p in planes[:max_planes]]
    # pad or truncate
    while len(resized) < max_planes:
        resized.append(resized[-1])
    resized = resized[:max_planes]

    # to float, normalize per-plane (ImageNet style) then concat channels
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    chans = []
    for p in resized:
        x = (p.astype(np.float32) / 255.0 - mean) / std  # (H,W,3)
        chans.append(x.transpose(2, 0, 1))  # (3,H,W)
    out = np.concatenate(chans, axis=0)  # (3*Z, H, W)
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Lightweight 3D stub (placeholder — requires real volume data + 3D backbone)
# ──────────────────────────────────────────────────────────────────────────────

class ZStack3DStub:
    """
    Placeholder for true 3D or 2.5D model.
    In Phase 2: replace with small 3D-CNN (e.g., r3d_18 or custom) or
    2.5D attention (process each plane, then temporal/axial attention).
    """

    def __init__(self, in_channels: int = 3, num_classes: int = 5):
        self.in_channels = in_channels
        self.num_classes = num_classes
        self._warned = False

    def forward(self, volume: np.ndarray) -> Dict[str, float]:
        """
        volume: (Z, C, H, W) or (C*Z, H, W) flattened channels.
        Returns dummy logits + note.
        """
        if not self._warned:
            print("[zstack] ZStack3DStub: real 3D model not implemented — returning heuristic.")
            self._warned = True
        # heuristic: average plane energy
        if volume.ndim == 4:
            z = volume.shape[0]
        else:
            z = max(1, volume.shape[0] // 3)
        score = float(np.clip(0.3 + 0.1 * (z - 1), 0.1, 0.9))
        return {
            "note": "STUB — no real 3D weights loaded",
            "dummy_abnormal_score": round(score, 4),
            "recommended_action": "Use EDF or multi-channel 2D path for Phase 1.5"
        }


# ──────────────────────────────────────────────────────────────────────────────
# Synthetic generator for testing (no real data needed)
# ──────────────────────────────────────────────────────────────────────────────

def make_synthetic_zstack(n_planes: int = 5, size: int = 256, seed: int = 42) -> List[np.ndarray]:
    """Create synthetic focal stack with a 'nucleus' that comes in/out of focus."""
    rng = np.random.default_rng(seed)
    planes = []
    cx, cy = size // 2, size // 2
    for i in range(n_planes):
        # base texture
        img = (rng.random((size, size, 3)) * 180 + 40).astype(np.uint8)
        # focus level: Gaussian blob sharpness changes with i
        sigma = 3 + abs(i - n_planes // 2) * 4
        focus = np.zeros((size, size), np.float32)
        for x in range(size):
            for y in range(size):
                d2 = (x - cx)**2 + (y - cy)**2
                focus[y, x] = np.exp(-d2 / (2 * sigma * sigma))
        focus = (focus * 255).astype(np.uint8)
        # paint into all channels with slight color
        for c in range(3):
            img[:, :, c] = np.clip(img[:, :, c] * 0.6 + focus * 0.4, 0, 255).astype(np.uint8)
        planes.append(img)
    return planes


def simulate_zstack_from_2d(rgb: np.ndarray, n_planes: int = 5, max_defocus: float = 5.0) -> List[np.ndarray]:
    """Simulate z-stack from a single 2D image by applying progressive Gaussian defocus blur.
    Useful for testing 2.5D pipeline without real multi-focal data.
    """
    planes = []
    for i in range(n_planes):
        sigma = (i - (n_planes - 1) / 2) * (max_defocus / max(1, n_planes - 1))
        sigma = abs(sigma)
        if sigma > 0.1:
            k = max(3, int(2 * round(3 * sigma) + 1))
            blurred = cv2.GaussianBlur(rgb, (k, k), sigmaX=sigma, sigmaY=sigma)
        else:
            blurred = rgb.copy()
        planes.append(blurred.astype(np.uint8))
    return planes


class ZStack25DStub:
    """Lightweight 2.5D simulation: process planes independently then fuse features (mean/max/attention stub).
    For real: replace with small 3D conv or per-plane backbone + LSTM/Transformer axial.
    """
    def __init__(self, base_2d_model=None, fusion: str = "mean"):
        self.base = base_2d_model
        self.fusion = fusion

    def forward_planes(self, planes_tensor) -> dict:
        """planes_tensor: (B, Z, C, H, W) or (B, Z*C, H, W) flattened.
        Returns fused logits + per-plane scores (stub).
        """
        import torch
        import torch.nn as nn
        if self.base is None:
            # heuristic stub
            if hasattr(planes_tensor, 'shape'):
                b = planes_tensor.shape[0]
                z = planes_tensor.shape[1] if planes_tensor.ndim == 5 else max(1, planes_tensor.shape[1] // 3)
            else:
                b, z = 1, 5
            score = 0.4 + 0.12 * (z - 1)
            return {"fused_score": float(torch.sigmoid(torch.tensor(score)).item()),
                    "per_plane": [round(0.3 + 0.1 * abs(i - z//2), 3) for i in range(z)],
                    "note": "2.5D stub (no base model)"}
        return {"note": "2.5D with base not fully wired in stub"}


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="run synthetic EDF + multi-channel demo")
    ap.add_argument("--planes", type=int, default=5)
    ap.add_argument("--out", default="models/zstack_demo")
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.demo:
        print("[zstack] generating synthetic z-stack...")
        planes = make_synthetic_zstack(n_planes=args.planes)
        for i, p in enumerate(planes):
            Image.fromarray(p).save(out / f"plane_{i:03d}.png")
        fused = edf_fuse_laplacian(planes)
        Image.fromarray(fused).save(out / "edf_fused.png")
        mc = build_multichannel_tensor(planes, target_size=224, max_planes=5)
        np.save(out / "multichannel.npy", mc)
        print(f"[zstack] wrote {len(planes)} planes + edf_fused.png + multichannel.npy → {out}")

        stub = ZStack3DStub()
        vol = mc.reshape(-1, 3, 224, 224) if mc.shape[0] > 3 else mc[None]
        res = stub.forward(vol)
        print("[zstack] 3D stub result:", res)

        # NEW: 2.5D + from-2D simulation demo
        print("[zstack] 2.5D simulation from single plane...")
        sim_planes = simulate_zstack_from_2d(planes[0], n_planes=5)
        Image.fromarray(sim_planes[2]).save(out / "sim_midplane.png")
        s25 = ZStack25DStub()
        # make dummy tensor (1,5,3,224,224)
        import torch, cv2
        dummy_vol = torch.randn(1, 5, 3, 224, 224)
        res25 = s25.forward_planes(dummy_vol)
        print("[zstack] 2.5D stub:", res25)
    else:
        print("Use --demo to generate synthetic z-stack test artifacts.")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
CervicalAI — Slide Quality Check Module (Phase 1.5+).

Detects poor-quality inputs that would degrade model reliability:
- Blur detection (Laplacian variance + FFT high-freq energy)
- Cellularity estimation (dark nuclei count via adaptive thresholding)
- Brightness / contrast / stain adequacy
- Edge / border artifact flagging
- Overall quality score + actionable flags

Outputs feed into predictor.py to REJECT or WARN before classification.

Usage:
  python ml/scripts/quality_check.py --demo
  python ml/scripts/quality_check.py --image path/to/slide.png

References:
- DEEP_RESEARCH Finding 5 (quality control is clinical prerequisite)
- ISO 15189 / CAP checklist for cytology slide adequacy
- Bethesda 2014 specimen adequacy criteria
"""
from __future__ import annotations
import argparse
import json
import pathlib
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple

import cv2
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).parent.parent.parent
MODELS = ROOT / "models"


@dataclass
class QualityResult:
    """Structured quality assessment result."""
    ok: bool
    overall_score: float  # 0-1, higher is better
    blur_score: float
    cellularity: float  # estimated nuclei count proxy
    brightness: float
    contrast: float
    issues: List[str]
    flags: Dict[str, bool]
    metrics: Dict[str, float]
    recommendation: str


# ──────────────────────────────────────────────────────────────────────────────
# Core quality detectors
# ──────────────────────────────────────────────────────────────────────────────

def detect_blur_laplacian(gray: np.ndarray) -> Tuple[float, bool]:
    """
    Laplacian variance blur metric.
    Low variance → blurry image (focus failure).
    Threshold tuned on cytology (~50-100 on 8-bit).
    """
    var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    is_blurry = var < 80.0
    return var, is_blurry


def detect_blur_fft(gray: np.ndarray, thresh: float = 10.0) -> Tuple[float, bool]:
    """
    FFT high-frequency energy.
    Blurry images lack high-freq content.
    """
    f = np.fft.fft2(gray.astype(np.float32))
    fshift = np.fft.fftshift(f)
    magnitude = np.abs(fshift)
    # high freq mask (outer ring)
    h, w = gray.shape
    cy, cx = h // 2, w // 2
    mask = np.ones((h, w), dtype=np.float32)
    r = int(min(h, w) * 0.1)  # inner 10% is low-freq
    cv2.circle(mask, (cx, cy), r, 0, -1)
    high_energy = float((magnitude * mask).mean())
    is_blurry = high_energy < thresh
    return high_energy, is_blurry


def estimate_cellularity(gray: np.ndarray, min_area: int = 50) -> Tuple[float, int]:
    """
    Rough cell/nuclei count proxy via adaptive thresholding + connected components.
    Returns (cellularity_score, estimated_count).
    Score is normalized log-count (0-1 range heuristic).
    """
    # Adaptive threshold for dark nuclei on varying stain
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        255 - blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    # Clean small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    num, labels, stats, _ = cv2.connectedComponentsWithStats(thresh, connectivity=8)
    # stats[:, cv2.CC_STAT_AREA] — skip background (label 0)
    areas = stats[1:, cv2.CC_STAT_AREA]
    big = areas[areas >= min_area]
    count = int(big.size)
    # normalize: log-scale, cap at ~5000 "cells" for score ~1.0
    score = float(np.clip(np.log1p(count) / np.log1p(5000), 0.0, 1.0))
    return score, count


def compute_brightness_contrast(gray: np.ndarray) -> Tuple[float, float]:
    """Mean brightness + RMS contrast."""
    bright = float(gray.mean())
    contrast = float(gray.std())
    return bright, contrast


def detect_stain_adequacy(bgr: np.ndarray) -> Tuple[float, bool]:
    """
    Simple stain color balance heuristic.
    Pap stain should have blue-purple nuclei + pink cytoplasm.
    Returns (balance_score, is_adequate).
    """
    b, g, r = cv2.split(bgr)
    # nuclei bias toward blue channel dominance in dark regions
    dark_mask = (bgr.mean(axis=2) < 120).astype(np.uint8)
    if dark_mask.sum() < 100:
        return 0.5, True  # too few dark pixels, don't penalize
    blue_dark = float(b[dark_mask == 1].mean())
    red_dark = float(r[dark_mask == 1].mean())
    # expect blue > red in nuclei
    balance = float(np.clip((blue_dark - red_dark + 50) / 100.0, 0.0, 1.0))
    adequate = balance > 0.2
    return balance, adequate


def detect_border_artifacts(bgr: np.ndarray) -> float:
    """
    Detect bright/white border artifacts (common in scanned slides).
    Returns fraction of border that is near-white.
    """
    h, w = bgr.shape[:2]
    border = 20
    top = bgr[:border, :, :].mean()
    bottom = bgr[-border:, :, :].mean()
    left = bgr[:, :border, :].mean()
    right = bgr[:, -border:, :].mean()
    avg_border = float(np.mean([top, bottom, left, right]))
    # high mean → white border artifact
    artifact_frac = float(np.clip((avg_border - 180) / 75.0, 0.0, 1.0))
    return artifact_frac


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def check_quality(bgr: np.ndarray, min_side: int = 160) -> QualityResult:
    """
    Full quality assessment pipeline.
    Input: BGR uint8 image (any size).
    Returns structured QualityResult.
    """
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    issues: List[str] = []
    flags: Dict[str, bool] = {}

    # 1. Size
    if min(h, w) < min_side:
        issues.append("small")
        flags["small"] = True
    else:
        flags["small"] = False

    # 2. Blur (dual method)
    lap_var, blurry_lap = detect_blur_laplacian(gray)
    fft_energy, blurry_fft = detect_blur_fft(gray)
    blur_score = float(np.clip(lap_var / 300.0, 0.0, 1.0))  # normalize heuristic
    if blurry_lap or blurry_fft:
        issues.append("blurry")
        flags["blurry"] = True
    else:
        flags["blurry"] = False

    # 3. Cellularity
    cellularity, cell_count = estimate_cellularity(gray)
    if cell_count < 30:
        issues.append("low_cellularity")
        flags["low_cellularity"] = True
    else:
        flags["low_cellularity"] = False

    # 4. Brightness / contrast
    bright, contrast = compute_brightness_contrast(gray)
    if bright < 35:
        issues.append("dark")
        flags["dark"] = True
    elif bright > 225:
        issues.append("bright")
        flags["bright"] = True
    else:
        flags["dark"] = flags["bright"] = False

    if contrast < 20:
        issues.append("low_contrast")
        flags["low_contrast"] = True
    else:
        flags["low_contrast"] = False

    # 5. Stain balance
    stain_bal, stain_ok = detect_stain_adequacy(bgr)
    if not stain_ok:
        issues.append("poor_stain")
        flags["poor_stain"] = True
    else:
        flags["poor_stain"] = False

    # 6. Border artifacts
    border_art = detect_border_artifacts(bgr)
    if border_art > 0.6:
        issues.append("border_artifact")
        flags["border_artifact"] = True
    else:
        flags["border_artifact"] = False

    # Composite score (weighted)
    # weights tuned heuristically for cytology
    score = (
        0.30 * blur_score +
        0.25 * cellularity +
        0.15 * (1.0 - abs(bright - 128) / 128.0) +
        0.15 * np.clip(contrast / 80.0, 0.0, 1.0) +
        0.10 * stain_bal +
        0.05 * (1.0 - border_art)
    )
    score = float(np.clip(score, 0.0, 1.0))

    ok = len(issues) == 0

    # Recommendation text
    if ok:
        rec = "คุณภาพภาพดี — ดำเนินการวิเคราะห์ได้"
    else:
        rec = "คุณภาพภาพไม่ผ่านเกณฑ์: " + ", ".join(issues) + " — ควรสแกนใหม่หรือปรับไฟล์"

    metrics = {
        "laplacian_var": round(lap_var, 2),
        "fft_high_energy": round(fft_energy, 2),
        "cell_count_est": cell_count,
        "brightness": round(bright, 1),
        "contrast": round(contrast, 1),
        "stain_balance": round(stain_bal, 3),
        "border_artifact": round(border_art, 3),
        "height": h,
        "width": w,
    }

    return QualityResult(
        ok=ok,
        overall_score=round(score, 4),
        blur_score=round(blur_score, 4),
        cellularity=round(cellularity, 4),
        brightness=round(bright, 1),
        contrast=round(contrast, 1),
        issues=issues,
        flags=flags,
        metrics=metrics,
        recommendation=rec,
    )


def check_quality_from_bytes(image_bytes: bytes) -> QualityResult:
    """Convenience: load bytes → BGR → check."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return check_quality(bgr)


# ──────────────────────────────────────────────────────────────────────────────
# Synthetic generator + CLI
# ──────────────────────────────────────────────────────────────────────────────

def make_synthetic_quality_samples(out_dir: pathlib.Path) -> List[Dict[str, Any]]:
    """Generate 4 synthetic slides with deliberate defects for testing."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    rng = np.random.default_rng(42)
    samples = []

    # 1. Good quality
    good = (rng.random((512, 512, 3)) * 120 + 60).astype(np.uint8)
    # add some dark nuclei-like blobs
    for _ in range(120):
        x, y = rng.integers(20, 492, 2)
        r = rng.integers(3, 8)
        cv2.circle(good, (x, y), r, (30, 25, 60), -1)
    cv2.imwrite(str(out_dir / "good_quality.png"), good)
    q = check_quality(good)
    samples.append({"name": "good_quality", "result": asdict(q)})

    # 2. Blurry
    blurry = cv2.GaussianBlur(good, (15, 15), 0)
    cv2.imwrite(str(out_dir / "blurry.png"), blurry)
    q = check_quality(blurry)
    samples.append({"name": "blurry", "result": asdict(q)})

    # 3. Low cellularity (almost empty)
    empty = (rng.random((512, 512, 3)) * 180 + 50).astype(np.uint8)
    cv2.imwrite(str(out_dir / "low_cellularity.png"), empty)
    q = check_quality(empty)
    samples.append({"name": "low_cellularity", "result": asdict(q)})

    # 4. Dark + low contrast
    dark = (rng.random((512, 512, 3)) * 30 + 15).astype(np.uint8)
    cv2.imwrite(str(out_dir / "dark_low_contrast.png"), dark)
    q = check_quality(dark)
    samples.append({"name": "dark_low_contrast", "result": asdict(q)})

    # 5. Bright border artifact
    border = good.copy()
    border[:30, :, :] = 240
    border[-30:, :, :] = 240
    border[:, :30, :] = 240
    border[:, -30:, :] = 240
    cv2.imwrite(str(out_dir / "border_artifact.png"), border)
    q = check_quality(border)
    samples.append({"name": "border_artifact", "result": asdict(q)})

    (out_dir / "quality_report.json").write_text(
        json.dumps({"samples": samples}, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return samples


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="generate synthetic quality samples + report")
    ap.add_argument("--image", type=str, default=None, help="analyze single image path")
    ap.add_argument("--out", default=str(MODELS / "quality_demo"))
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.demo:
        print("[quality] generating synthetic quality test set...")
        samples = make_synthetic_quality_samples(out)
        print(f"[quality] wrote {len(samples)} samples + quality_report.json → {out}")
        for s in samples:
            r = s["result"]
            print(f"  {s['name']}: ok={r['ok']} score={r['overall_score']} issues={r['issues']}")
    elif args.image:
        p = pathlib.Path(args.image)
        bgr = cv2.imread(str(p))
        if bgr is None:
            print(f"[quality] cannot read {p}")
            return
        q = check_quality(bgr)
        print(json.dumps(asdict(q), indent=2, ensure_ascii=False))
        (out / f"{p.stem}_quality.json").write_text(
            json.dumps(asdict(q), indent=2, ensure_ascii=False), encoding="utf-8"
        )
    else:
        print("Use --demo or --image path")


if __name__ == "__main__":
    import io
    main()

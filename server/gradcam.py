# -*- coding: utf-8 -*-
"""
CervicalAI — Grad-CAM thin wrapper (used by predictor when needed).

This is a convenience re-export. Real implementation lives in ml/scripts/eval_xai.py.
Also provides a pure-demo overlay generator used by the server when in demo mode.
"""
from __future__ import annotations
import numpy as np
from typing import Optional

def gradcam_overlay(net, ckpt: dict, bgr: np.ndarray, device: str) -> Optional[np.ndarray]:
    """Thin wrapper — delegates to eval_xai if available."""
    try:
        from ml.scripts.eval_xai import gradcam, overlay_heatmap
        import torch, cv2
        img_size = ckpt.get("img_size", 224)
        mean = np.array(ckpt.get("mean", [0.485, 0.456, 0.406]), np.float32)
        std = np.array(ckpt.get("std", [0.229, 0.224, 0.225]), np.float32)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        small = cv2.resize(rgb, (img_size, img_size))
        x = (small.astype(np.float32) / 255.0 - mean) / std
        t = torch.from_numpy(x.transpose(2, 0, 1)[None]).to(device)
        cam = gradcam(net, ckpt.get("arch", "efficientnet_b0"), t, class_idx=None)
        return overlay_heatmap(bgr, cam)
    except Exception:
        return None


def demo_overlay(bgr: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    """Pure-demo plausible heatmap (no model). Highlights darker 'nuclear' areas."""
    import cv2
    g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    g = (g - g.min()) / (g.max() - g.min() + 1e-6)
    # invert + gamma to spotlight nuclei-like dark blobs
    spot = (1.0 - g) ** 1.6
    spot = (spot * 255).astype(np.uint8)
    heat = cv2.applyColorMap(spot, cv2.COLORMAP_JET)
    return cv2.addWeighted(bgr, 1 - alpha, heat, alpha, 0)

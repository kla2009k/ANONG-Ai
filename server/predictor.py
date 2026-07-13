# -*- coding: utf-8 -*-
"""
CervicalAI — inference core (Phase 1 + Advanced 1.5).

Modes:
  - "demo": heuristic on image stats (no model file) — clearly labeled in API
  - "model": loads models/best_cervical.pt (EfficientNet transfer)

Core outputs:
  - 4-class cytology-grade probabilities (NILM/LSIL/HSIL/SCC)
  - independent koilocytosis-morphology assessment
  - quality gate (basic + advanced module)
  - MC Dropout uncertainty (improved)
  - Advanced XAI: multi-method CAM (Grad/Score/Eigen/Layer), uncertainty overlay, top-k patches
  - Conformal prediction sets + evidential vacuity/dissonance (if available)
  - Z-stack simulation (EDF + multi-channel) if caller provides planes
  - WSI patch simulation (grid + MIL aggregation) on large images

Checkpoint contract (from ml/scripts/train_classifier.py):
  { state_dict, arch, classes, img_size, mean, std, recall_hsil_scc, ... }
"""
from __future__ import annotations
import base64
import io
import pathlib
import hashlib
import sys
from typing import Dict, Any, List, Optional

import cv2
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# advanced modules (graceful import)
try:
    from ml.scripts.quality_check import check_quality as advanced_quality_check
    HAS_QUALITY = True
except Exception:
    HAS_QUALITY = False

try:
    from ml.scripts.xai_advanced import compute_cam, overlay_heatmap as adv_overlay, make_uncertainty_overlay, make_topk_patches
    HAS_XAI_ADV = True
except Exception:
    HAS_XAI_ADV = False

try:
    from ml.scripts.uncertainty_advanced import mc_dropout_predict as adv_mc, uncertainty_flags as adv_flags, conformal_classification_sets, evidential_predict
    HAS_UNC_ADV = True
except Exception:
    HAS_UNC_ADV = False

try:
    from ml.zstack_edf import edf_fuse_laplacian, build_multichannel_tensor
    HAS_ZSTACK = True
except Exception:
    HAS_ZSTACK = False

try:
    from ml.scripts.wsi_patch_sim import simulate_wsi, make_synthetic_slide
    HAS_WSI_SIM = True
except Exception:
    HAS_WSI_SIM = False

CLASSES = ["NILM", "LSIL", "HSIL", "SCC"]
CLASS_KEYS = CLASSES

_STATE: Dict[str, Any] = {
    "mode": "demo",
    "net": None,
    "ckpt": None,
    "device": "cpu",
    "koil_net": None,
    "koil_ckpt": None,
    "koil_mode": "unavailable",
}

LOW_CONF = 0.35  # flag if top prob < this


def _build_net(arch: str, n: int):
    from torchvision import models as tvm
    import torch.nn as nn
    if "efficientnet_b0" in arch:
        m = tvm.efficientnet_b0(weights=None)
        m.classifier[1] = nn.Linear(m.classifier[1].in_features, n)
    elif "efficientnet_b3" in arch:
        m = tvm.efficientnet_b3(weights=None)
        m.classifier[1] = nn.Linear(m.classifier[1].in_features, n)
    else:
        m = tvm.resnet18(weights=None)
        m.fc = nn.Linear(m.fc.in_features, n)
    return m


def load_model() -> Dict[str, Any]:
    """Attempt to load trained checkpoint; fall back to demo."""
    ckpt_path = MODELS / "best_cervical.pt"
    if ckpt_path.exists():
        try:
            import torch
            ck = torch.load(str(ckpt_path), map_location="cpu", weights_only=False)
            arch = ck.get("arch", "efficientnet_b0")
            n = len(ck.get("classes", [*CLASSES, "KOIL"]))
            net = _build_net(arch, n)
            net.load_state_dict(ck["state_dict"])
            net.eval()
            dev = "cuda" if torch.cuda.is_available() else "cpu"
            net.to(dev)
            _STATE.update(net=net, ckpt=ck, device=dev, mode="model")
            print(f"[predictor] loaded {arch}  recall_hsil_scc={ck.get('recall_hsil_scc')} on {dev}")
        except Exception as e:
            print("[predictor] model load failed, demo mode:", repr(e))
            _STATE["mode"] = "demo"
    else:
        _STATE["mode"] = "demo"

    koil_path = MODELS / "koil_sipakmed" / "best_koil_model.pt"
    _STATE.update(koil_net=None, koil_ckpt=None, koil_mode="unavailable")
    if koil_path.exists():
        try:
            import torch
            koil_ck = torch.load(str(koil_path), map_location="cpu", weights_only=False)
            koil_net = _build_net(koil_ck.get("arch", "efficientnet_b0"), len(koil_ck["classes"]))
            koil_net.load_state_dict(koil_ck["state_dict"])
            koil_net.eval()
            koil_net.to(_STATE["device"])
            _STATE.update(koil_net=koil_net, koil_ckpt=koil_ck, koil_mode="model")
            print("[predictor] loaded independent SIPaKMeD koilocytosis morphology model")
        except Exception as e:
            print("[predictor] KOIL model load failed:", repr(e))
    return {
        "mode": _STATE["mode"],
        "classes": CLASSES,
        "koil_mode": _STATE["koil_mode"],
        "koil_endpoint": "independent morphology one-vs-rest",
    }


def mode() -> str:
    return _STATE["mode"]


def status() -> Dict[str, Any]:
    return {
        "grade_mode": _STATE["mode"],
        "grade_classes": list(CLASSES),
        "koil_mode": _STATE["koil_mode"],
        "koil_endpoint": "koilocytosis morphology one-vs-rest",
        "koil_training_domain": "SIPaKMeD conventional Pap-smear cropped cells" if _STATE["koil_mode"] == "model" else None,
        "hpv_test": False,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Image helpers
# ──────────────────────────────────────────────────────────────────────────────
def _to_bgr(image_bytes: bytes, max_side: int = 800) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    scale = min(1.0, max_side / max(w, h))
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def _png_b64(bgr: np.ndarray) -> str:
    ok, buf = cv2.imencode(".png", bgr)
    return "data:image/png;base64," + base64.b64encode(buf.tobytes()).decode("ascii")


def _cam_diagnostics(cam: Optional[np.ndarray]) -> Dict[str, Any]:
    """Validate that a CAM contains finite, non-flat spatial evidence."""
    if cam is None:
        return {"valid": False, "reason": "missing_activation"}
    array = np.asarray(cam, dtype=np.float32)
    if array.ndim != 2 or array.size == 0:
        return {"valid": False, "reason": "invalid_shape", "shape": list(array.shape)}
    finite_mask = np.isfinite(array)
    finite_fraction = float(finite_mask.mean())
    if finite_fraction < 1.0:
        return {
            "valid": False,
            "reason": "non_finite_values",
            "finite_fraction": round(finite_fraction, 6),
        }
    minimum = float(array.min())
    maximum = float(array.max())
    std = float(array.std())
    dynamic_range = maximum - minimum
    positive_fraction = float((array > minimum + 1e-6).mean())
    diagnostics = {
        "valid": dynamic_range >= 1e-5 and std >= 1e-4 and positive_fraction >= 0.001,
        "reason": "ok",
        "min": round(minimum, 6),
        "max": round(maximum, 6),
        "std": round(std, 6),
        "dynamic_range": round(dynamic_range, 6),
        "positive_fraction": round(positive_fraction, 6),
    }
    if not diagnostics["valid"]:
        diagnostics["reason"] = "flat_activation"
    return diagnostics


def _select_primary_cam(cams: Dict[str, np.ndarray]) -> tuple[Optional[str], Optional[np.ndarray], Dict[str, Dict[str, Any]]]:
    """Pick the first valid class-aware CAM, or abstain when every map is degenerate."""
    diagnostics = {name: _cam_diagnostics(cam) for name, cam in cams.items()}
    for name in ("gradcam", "gradcam++", "layercam", "scorecam"):
        if name in cams and diagnostics[name]["valid"]:
            return name, cams[name], diagnostics
    return None, None, diagnostics


def _activation_region_overlay(
    bgr: np.ndarray, cam: np.ndarray
) -> tuple[Optional[np.ndarray], float, Optional[float]]:
    """Highlight the strongest valid CAM activations without claiming segmentation."""
    if not _cam_diagnostics(cam)["valid"]:
        return None, 0.0, None
    h, w = bgr.shape[:2]
    resized = cv2.resize(cam.astype(np.float32), (w, h))
    minimum = float(resized.min())
    maximum = float(resized.max())
    resized = (resized - minimum) / (maximum - minimum + 1e-8)
    threshold = max(0.55, float(np.quantile(resized, 0.80)))
    mask = (resized >= threshold).astype(np.uint8)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    filtered = np.zeros_like(mask)
    min_area = max(9, int(h * w * 0.002))
    for index in range(1, count):
        if int(stats[index, cv2.CC_STAT_AREA]) >= min_area:
            filtered[labels == index] = 1
    mask = filtered
    if not mask.any():
        return None, 0.0, round(threshold, 4)
    contours, _ = cv2.findContours(mask * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    overlay = bgr.copy()
    tint = np.zeros_like(bgr)
    tint[:, :] = (70, 60, 235)
    active = mask.astype(bool)
    overlay[active] = cv2.addWeighted(bgr, 0.45, tint, 0.55, 0)[active]
    cv2.drawContours(overlay, contours, -1, (0, 235, 255), 2)
    return overlay, round(float(mask.mean()), 4), round(threshold, 4)


def _fake_contours(bgr: np.ndarray, top_class: str, n: int = 6) -> List[Dict[str, Any]]:
    """Generate plausible fake nuclei contours for interactive demo.
    Returns list of {id, points:[[x,y],...], class, confidence, editable:true}
    These are SYNTHETIC — clearly demo only.
    """
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Find a few dark blobs as "nuclei" seeds
    _, dark = cv2.threshold(255 - gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(dark, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:max(12, n)]

    out = []
    rng = np.random.default_rng(int(hashlib.md5(str(top_class).encode()).hexdigest()[:8], 16) % (2**32))
    cls_bias = {"NILM": 0, "LSIL": 1, "HSIL": 2, "SCC": 3, "KOIL": 4}.get(top_class, 0)

    for i, c in enumerate(contours[:n]):
        if cv2.contourArea(c) < 40:
            continue
        # simplify + jitter for "organic" look
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True).reshape(-1, 2)
        # add small random jitter
        jitter = (rng.random(approx.shape) - 0.5) * 3
        approx = np.clip(approx + jitter, [0, 0], [w-1, h-1]).astype(int)
        # map to plausible class near top prediction
        cidx = int(np.clip(cls_bias + rng.integers(-1, 2), 0, 4))
        conf = float(np.clip(0.65 + rng.random() * 0.3, 0.5, 0.98))
        out.append({
            "id": f"c{i}",
            "points": approx.tolist(),
            "class": CLASSES[cidx],
            "confidence": round(conf, 3),
            "editable": True,
            "area_px": int(cv2.contourArea(c)),
        })
    # if too few, synthesize a couple
    while len(out) < 3:
        cx, cy = int(w * (0.3 + 0.4 * rng.random())), int(h * (0.3 + 0.4 * rng.random()))
        r = int(min(w, h) * (0.04 + 0.03 * rng.random()))
        pts = [[cx + int(r*np.cos(a)), cy + int(r*np.sin(a))] for a in np.linspace(0, 2*np.pi, 12, endpoint=False)]
        out.append({
            "id": f"s{len(out)}",
            "points": pts,
            "class": top_class,
            "confidence": round(0.6 + rng.random()*0.25, 3),
            "editable": True,
            "area_px": int(np.pi * r * r),
        })
    return out[:n]


def _quality(bgr: np.ndarray) -> Dict[str, Any]:
    """Basic quality (kept for backward compat)."""
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    bright = float(gray.mean())
    issues = []
    if min(h, w) < 160:
        issues.append("small")
    if blur < 50:
        issues.append("blurry")
    if bright < 40:
        issues.append("dark")
    elif bright > 220:
        issues.append("bright")
    return {"ok": len(issues) == 0, "issues": issues, "blur": round(blur, 1), "brightness": round(bright, 1)}


def _advanced_quality(bgr: np.ndarray) -> Dict[str, Any]:
    """Use advanced quality module if available; else fall back to basic."""
    if HAS_QUALITY:
        try:
            q = advanced_quality_check(bgr)
            return {
                "ok": q.ok,
                "overall_score": round(q.overall_score, 4),
                "issues": q.issues,
                "flags": q.flags,
                "metrics": q.metrics,
                "recommendation": q.recommendation,
                "source": "advanced",
            }
        except Exception:
            pass
    basic = _quality(bgr)
    basic["source"] = "basic"
    return basic


def _classifier_quality(bgr: np.ndarray) -> Dict[str, Any]:
    """Domain-aware quality profile for the Herlev single-cell crop classifier.

    Reference cut points were measured on the 917-image training/evaluation
    corpus at the model's 224 px input size. They are engineering guardrails,
    not clinically validated specimen-adequacy thresholds.
    """
    raw = _advanced_quality(bgr)
    h, w = bgr.shape[:2]
    model_view = cv2.resize(bgr, (224, 224), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(model_view, cv2.COLOR_BGR2GRAY)
    focus = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(gray.mean())
    contrast = float(gray.std())

    blocking: List[str] = []
    warnings: List[str] = []
    if min(h, w) < 64:
        blocking.append("severe_small_image")
    elif min(h, w) < 160:
        warnings.append("small_image")
    if focus < 2.0:
        blocking.append("severe_blur")
    elif focus < 8.448:
        warnings.append("below_reference_focus")
    if contrast < 8.0:
        blocking.append("severe_low_contrast")
    elif contrast < 14.691:
        warnings.append("below_reference_contrast")
    if brightness < 50:
        blocking.append("severe_darkness")
    elif brightness > 230:
        blocking.append("severe_brightness")
    elif brightness < 85.078 or brightness > 208.592:
        warnings.append("brightness_outside_reference_99pct")

    raw_flags = raw.get("flags") or {}
    if raw_flags.get("poor_stain"):
        warnings.append("possible_stain_shift")
    if raw_flags.get("border_artifact"):
        warnings.append("possible_border_artifact")

    status = "fail" if blocking else ("warning" if warnings else "pass")
    focus_score = float(np.clip((focus - 2.0) / (20.456 - 2.0), 0.0, 1.0))
    contrast_score = float(np.clip((contrast - 8.0) / (28.281 - 8.0), 0.0, 1.0))
    brightness_score = float(np.clip(1.0 - abs(brightness - 132.8) / 132.8, 0.0, 1.0))
    size_score = float(np.clip(min(h, w) / 160.0, 0.0, 1.0))
    overall = 0.40 * focus_score + 0.30 * contrast_score + 0.20 * brightness_score + 0.10 * size_score

    metrics = dict(raw.get("metrics") or {})
    metrics.update({
        "focus_laplacian_224": round(focus, 4),
        "brightness_224": round(brightness, 4),
        "contrast_224": round(contrast, 4),
    })
    return {
        "ok": status != "fail",
        "status": status,
        "profile": "single_cell_crop_herlev_v1",
        "overall_score": round(float(overall), 4),
        "blocking_issues": blocking,
        "warnings": warnings,
        "issues": blocking + warnings,
        "metrics": metrics,
        "reference": {
            "dataset": "Herlev 917 single-cell images",
            "focus_laplacian_224_p01": 8.448,
            "focus_laplacian_224_median": 20.456,
            "contrast_p01": 14.691,
            "brightness_p01_p99": [85.078, 208.592],
            "clinical_validation": False,
        },
        "source": "domain_profile_v1",
        "note": "Engineering input-quality guardrail; not Bethesda specimen adequacy assessment.",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Demo heuristic (transparent, not a claim)
# ──────────────────────────────────────────────────────────────────────────────
def _demo_classify(bgr: np.ndarray, image_bytes: bytes) -> list[Dict[str, Any]]:
    """Crude cytology-ish features -> four grade scores (clearly demo)."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # keep uint8 for OTSU; work on inverted for dark nuclei
    inv = (255 - gray).astype(np.uint8)
    _, dark = cv2.threshold(inv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    area = float(dark.sum()) / dark.size
    # texture energy (on float for sobel)
    gxf = gray.astype(np.float32)
    gx = cv2.Sobel(gxf, cv2.CV_32F, 1, 0); gy = cv2.Sobel(gxf, cv2.CV_32F, 0, 1)
    tex = float(np.abs(gx).mean() + np.abs(gy).mean())
    seed = int(hashlib.md5(image_bytes).hexdigest(), 16) % 1000 / 1000.0

    # base + feature nudge
    s = np.array([0.6, 0.5, 0.3, 0.2, 0.4], dtype=np.float32)  # NILM, LSIL, HSIL, SCC, KOIL
    s[0] += 0.8 * (1 - min(area * 3, 1))           # more normal if few dark regions
    s[1] += 0.9 * min(area * 2, 1)                 # LSIL nudge
    s[2] += 1.1 * min(tex / 60, 1) * min(area * 2, 1)  # HSIL ~ texture + dark
    s[3] += 0.8 * min(tex / 80, 1)                 # SCC ~ high texture
    s[4] += 0.7 * (0.6 if area > 0.12 else 0.0)    # KOIL heuristic

    # seeded jitter so output stable per image
    for i in range(5):
        s[i] += 0.2 * ((seed * (i + 1)) % 1.0)

    p = np.exp(s[:4]) / np.exp(s[:4]).sum()
    out = []
    for k, pp in zip(CLASSES, p):
        out.append({"key": k, "prob": round(float(pp), 4)})
    out.sort(key=lambda d: -d["prob"])
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Model path
# ──────────────────────────────────────────────────────────────────────────────
def _grade_probabilities(model_classes: list[str], probabilities: np.ndarray) -> list[Dict[str, Any]]:
    """Remove the unsupported legacy KOIL output and renormalize grade classes."""
    indexed = [
        (index, name, float(probabilities[index]))
        for index, name in enumerate(model_classes)
        if name in CLASSES
    ]
    if {name for _, name, _ in indexed} != set(CLASSES):
        raise ValueError(f"grade checkpoint does not contain the required classes: {model_classes}")
    denominator = sum(probability for _, _, probability in indexed)
    if denominator <= 0:
        raise ValueError("grade probabilities do not have positive mass")
    result = [
        {"key": name, "prob": round(probability / denominator, 4), "model_index": index}
        for index, name, probability in indexed
    ]
    return sorted(result, key=lambda item: -item["prob"])


def _model_classify(bgr: np.ndarray) -> list[Dict[str, Any]]:
    import torch
    net = _STATE["net"]; ck = _STATE["ckpt"]; dev = _STATE["device"]
    img_size = ck.get("img_size", 224)
    mean = np.array(ck.get("mean", [0.485, 0.456, 0.406]), np.float32)
    std = np.array(ck.get("std", [0.229, 0.224, 0.225]), np.float32)

    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    small = cv2.resize(rgb, (img_size, img_size))
    x = (small.astype(np.float32) / 255.0 - mean) / std
    t = torch.from_numpy(x.transpose(2, 0, 1)[None]).to(dev)

    with torch.no_grad():
        logits = net(t)
        probs = torch.softmax(logits, dim=1)[0].cpu().numpy()

    model_classes = list(ck.get("classes", [*CLASSES, "KOIL"]))
    return _grade_probabilities(model_classes, probs)


def _model_koil_assessment(bgr: np.ndarray) -> Dict[str, Any]:
    import torch

    net = _STATE["koil_net"]
    ck = _STATE["koil_ckpt"]
    device = _STATE["device"]
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    small = cv2.resize(rgb, (ck.get("img_size", 224), ck.get("img_size", 224)))
    mean = np.asarray(ck.get("mean", [0.485, 0.456, 0.406]), dtype=np.float32)
    std = np.asarray(ck.get("std", [0.229, 0.224, 0.225]), dtype=np.float32)
    normalized = (small.astype(np.float32) / 255.0 - mean) / std
    tensor = torch.from_numpy(normalized.transpose(2, 0, 1)[None]).to(device)
    with torch.no_grad():
        logits = net(tensor) / float(ck.get("temperature", 1.0))
        probabilities = torch.softmax(logits, dim=1)[0].cpu().numpy()
    index = int(ck["koil_index"])
    score = float(probabilities[index])
    threshold = float(ck["koil_threshold"])
    return {
        "status": "positive" if score >= threshold else "negative",
        "positive": bool(score >= threshold),
        "probability": round(score, 4),
        "threshold": round(threshold, 4),
        "decision_margin": round(score - threshold, 4),
        "mode": "model",
        "endpoint": "koilocytosis morphology one-vs-rest",
        "training_domain": "SIPaKMeD conventional Pap-smear cropped cells",
        "hpv_test": False,
        "domain_warning": "Not validated for ThinPrep and does not detect HPV DNA or RNA.",
    }


def _demo_koil_assessment(bgr: np.ndarray) -> Dict[str, Any]:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    dark_fraction = float((gray < np.percentile(gray, 35)).mean())
    score = min(0.95, max(0.05, 0.15 + dark_fraction))
    return {
        "status": "unvalidated_demo",
        "positive": False,
        "probability": round(score, 4),
        "threshold": None,
        "decision_margin": None,
        "mode": "heuristic_demo",
        "endpoint": "koilocytosis morphology one-vs-rest",
        "training_domain": None,
        "hpv_test": False,
        "domain_warning": "Demo heuristic only; no KOIL result is released.",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Public API — ADVANCED
# ──────────────────────────────────────────────────────────────────────────────
def analyze(image_bytes: bytes, want_heatmap: bool = True,
            zstack_planes: Optional[List[bytes]] = None,
            simulate_wsi: bool = False) -> Dict[str, Any]:
    """
    Main inference entry.
    - zstack_planes: list of raw image bytes (multiple focal planes) → EDF + multi-channel
    - simulate_wsi: if True and image is large, run patch grid + MIL aggregation
    """
    bgr = _to_bgr(image_bytes)

    # Advanced quality (preferred)
    quality = _classifier_quality(bgr)

    if _STATE["mode"] == "model" and _STATE["net"] is not None:
        cls = _model_classify(bgr)
        cls_mode = "model"
    else:
        cls = _demo_classify(bgr, image_bytes)
        cls_mode = "demo"

    top = cls[0]
    low_conf = top["prob"] < LOW_CONF

    if _STATE["koil_mode"] == "model" and _STATE["koil_net"] is not None:
        koil_assessment = _model_koil_assessment(bgr)
    else:
        koil_assessment = _demo_koil_assessment(bgr)
    koil_flag = bool(koil_assessment["positive"])

    # ── Z-stack simulation (EDF + multi-channel) ──────────────────────────────
    zstack_info = None
    if zstack_planes and HAS_ZSTACK and len(zstack_planes) >= 2:
        try:
            planes = []
            for pb in zstack_planes[:7]:
                im = Image.open(io.BytesIO(pb)).convert("RGB")
                planes.append(np.array(im))
            fused = edf_fuse_laplacian(planes)
            mc_tensor = build_multichannel_tensor(planes, target_size=224, max_planes=min(5, len(planes)))
            zstack_info = {
                "n_planes": len(planes),
                "edf_shape": list(fused.shape),
                "multichannel_shape": list(mc_tensor.shape),
                "fused_preview": _png_b64(cv2.cvtColor(fused, cv2.COLOR_RGB2BGR)),
            }
            # optionally bias classification toward "more abnormal" if EDF has high texture
            g = cv2.cvtColor(fused, cv2.COLOR_RGB2GRAY).astype(np.float32)
            tex = float(np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0)).mean() + np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1)).mean())
            if tex > 45 and cls_mode == "model":
                for d in cls:
                    if d["key"] in ("HSIL", "SCC"):
                        d["prob"] = round(min(0.98, d["prob"] + 0.06), 4)
                cls = sorted(cls, key=lambda x: -x["prob"])
                top = cls[0]
        except Exception as e:
            zstack_info = {"error": str(e)}

    # ── WSI patch simulation (if requested or image is large) ─────────────────
    wsi_info = None
    if (simulate_wsi or max(bgr.shape[:2]) >= 900) and HAS_WSI_SIM:
        try:
            res = simulate_wsi(bgr, net=_STATE.get("net"), ck=_STATE.get("ckpt"),
                               device=_STATE.get("device", "cpu"),
                               tile=224, stride=160, max_patches=48)
            wsi_info = {
                "slide_score": res.slide_score,
                "n_patches": res.n_patches,
                "abnormal_patches": res.abnormal_patches,
                "uncertain": res.uncertain,
                "heatmap_b64": _png_b64(cv2.imread(res.heatmap_path)) if res.heatmap_path else None,
                "note": res.note,
            }
            # if WSI says high slide_score, nudge top toward abnormal
            if res.slide_score > 0.45 and cls_mode == "model":
                for d in cls:
                    if d["key"] in ("HSIL", "SCC", "KOIL"):
                        d["prob"] = round(min(0.98, d["prob"] + 0.05), 4)
                cls = sorted(cls, key=lambda x: -x["prob"])
                top = cls[0]
        except Exception as e:
            wsi_info = {"error": str(e)}

    # ── Advanced Uncertainty (MC + conformal + evidential) ────────────────────
    uncertainty = None
    conformal_set = None
    evidential = None

    if _STATE["mode"] == "model":
        try:
            import torch
            ck = _STATE["ckpt"]
            img_size = ck.get("img_size", 224)
            mean = np.array(ck.get("mean", [0.485, 0.456, 0.406]), np.float32)
            std = np.array(ck.get("std", [0.229, 0.224, 0.225]), np.float32)
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            small = cv2.resize(rgb, (img_size, img_size))
            x = (small.astype(np.float32) / 255.0 - mean) / std
            t = torch.from_numpy(x.transpose(2, 0, 1)[None]).to(_STATE["device"])

            # prefer advanced MC
            if HAS_UNC_ADV:
                mc = adv_mc(_STATE["net"], t, n_samples=20)
                flags = adv_flags(mc["mean"], mc["std"])
                uncertainty = {
                    "entropy": round(float(flags["entropy"][0]), 4),
                    "top_std": round(float(flags["top_class_std"][0]), 4),
                    "flag": bool(flags["is_uncertain"][0]),
                    "source": "advanced_mc",
                }
                # conformal (single-point calibration on this sample — demo only)
                try:
                    conf = conformal_classification_sets(mc["mean"], np.array([0]), mc["mean"], alpha=0.1)
                    conformal_set = conf.get("prediction_sets", [None])[0]
                except Exception:
                    conformal_set = None
                # evidential
                try:
                    ev = evidential_predict(_STATE["net"], t)
                    evidential = {
                        "vacuity": round(float(ev["vacuity"][0, 0]), 4),
                        "dissonance": round(float(ev["dissonance"][0, 0]), 4),
                    }
                except Exception:
                    evidential = None
            else:
                # fallback to original eval_xai
                from ml.scripts.eval_xai import mc_dropout_predict, uncertainty_flags
                mc = mc_dropout_predict(_STATE["net"], t, n_samples=15)
                flags = uncertainty_flags(mc["mean"], mc["std"])
                uncertainty = {
                    "entropy": round(float(flags["entropy"][0]), 4),
                    "top_std": round(float(flags["top_class_std"][0]), 4),
                    "flag": bool(flags["is_uncertain"][0]),
                    "source": "legacy_mc",
                }
        except Exception:
            uncertainty = {"entropy": 0.8, "top_std": 0.1, "flag": low_conf}

    # ── Advanced XAI (multi-method + uncertainty overlay + top-k patches) ─────
    heatmap = None
    heatmap_source = None
    advanced_xai = None
    koil_xai = None

    if want_heatmap:
        if _STATE["mode"] == "model":
            try:
                import torch
                ck = _STATE["ckpt"]
                img_size = ck.get("img_size", 224)
                mean = np.array(ck.get("mean", [0.485, 0.456, 0.406]), np.float32)
                std = np.array(ck.get("std", [0.229, 0.224, 0.225]), np.float32)
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                small = cv2.resize(rgb, (img_size, img_size))
                x = (small.astype(np.float32) / 255.0 - mean) / std
                t = torch.from_numpy(x.transpose(2, 0, 1)[None]).to(_STATE["device"])
                # Classification is sorted for display, so use the checkpoint's
                # original output index for class-specific attribution.
                pred = int(top.get("model_index", CLASSES.index(top["key"])))

                if HAS_XAI_ADV:
                    methods = ["gradcam", "gradcam++", "layercam", "scorecam", "eigencam"]
                    raw_cams: Dict[str, np.ndarray] = {}
                    method_errors: Dict[str, str] = {}
                    for m in methods:
                        try:
                            raw_cams[m] = compute_cam(
                                _STATE["net"], ck.get("arch", "efficientnet_b0"), t, pred, m
                            )
                        except Exception as exc:
                            method_errors[m] = type(exc).__name__

                    primary_method, primary_cam, cam_diagnostics = _select_primary_cam(raw_cams)
                    cams = {
                        name: _png_b64(adv_overlay(bgr, cam))
                        for name, cam in raw_cams.items()
                        if cam_diagnostics[name]["valid"]
                    }

                    unc_b64 = None
                    if primary_cam is not None:
                        try:
                            # This visualizes uncertainty around the selected CAM; it is not
                            # a separately validated pixel-wise uncertainty estimator.
                            std_cam = np.clip(primary_cam * 0.15 + 0.05, 0.0, 0.3)
                            unc_ov = make_uncertainty_overlay(bgr, primary_cam, std_cam)
                            unc_b64 = _png_b64(unc_ov)
                        except Exception:
                            unc_b64 = None

                    topk_b64 = None
                    if primary_cam is not None:
                        try:
                            topk_img = make_topk_patches(bgr, primary_cam, k=5, patch=28)
                            topk_b64 = _png_b64(topk_img)
                        except Exception:
                            pass

                    activation_b64 = None
                    activation_coverage = 0.0
                    activation_threshold = None
                    if primary_cam is not None:
                        try:
                            activation_img, activation_coverage, activation_threshold = _activation_region_overlay(
                                bgr, primary_cam
                            )
                            if activation_img is not None:
                                activation_b64 = _png_b64(activation_img)
                        except Exception:
                            pass

                    advanced_xai = {
                        "ok": primary_cam is not None,
                        "primary_method": primary_method,
                        "failure_reason": None if primary_cam is not None else "no_valid_class_aware_cam",
                        "methods": cams,
                        "method_diagnostics": cam_diagnostics,
                        "method_errors": method_errors,
                        "uncertainty_overlay": unc_b64,
                        "topk_patches": topk_b64,
                        "activation_regions": activation_b64,
                        "activation_coverage": activation_coverage,
                        "activation_threshold": activation_threshold,
                        "activation_method": "top-20-percent-selected-cam-threshold",
                        "activation_disclaimer": "Attention boundary only; not cell or lesion segmentation.",
                    }
                    if primary_method is not None:
                        heatmap = cams[primary_method]
                        suffix = "" if primary_method == "gradcam" else "_fallback"
                        method_token = {
                            "gradcam": "gradcam",
                            "gradcam++": "gradcam_plus_plus",
                            "layercam": "layercam",
                            "scorecam": "scorecam",
                        }.get(primary_method, primary_method)
                        heatmap_source = f"advanced_{method_token}{suffix}"
                else:
                    # legacy single Grad-CAM
                    from ml.scripts.eval_xai import gradcam, overlay_heatmap
                    cam = gradcam(_STATE["net"], ck.get("arch", "efficientnet_b0"), t, class_idx=pred)
                    legacy_diagnostics = _cam_diagnostics(cam)
                    advanced_xai = {
                        "ok": legacy_diagnostics["valid"],
                        "primary_method": "gradcam" if legacy_diagnostics["valid"] else None,
                        "failure_reason": None if legacy_diagnostics["valid"] else legacy_diagnostics["reason"],
                        "methods": {},
                        "method_diagnostics": {"gradcam": legacy_diagnostics},
                    }
                    if legacy_diagnostics["valid"]:
                        heatmap = _png_b64(overlay_heatmap(bgr, cam))
                        heatmap_source = "legacy_gradcam"
            except Exception as exc:
                heatmap = None
                advanced_xai = {
                    "ok": False,
                    "primary_method": None,
                    "failure_reason": f"xai_pipeline_error:{type(exc).__name__}",
                    "methods": {},
                    "method_diagnostics": {},
                }
        else:
            # Demo heatmap
            try:
                g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
                g = (g - g.min()) / (g.max() - g.min() + 1e-6)
                spot = (1.0 - g) ** 1.5
                spot = (spot * 255).astype(np.uint8)
                heat = cv2.applyColorMap(spot, cv2.COLORMAP_JET)
                overlay = cv2.addWeighted(bgr, 0.55, heat, 0.45, 0)
                heatmap = _png_b64(overlay)
                heatmap_source = "demo_spotlight"
            except Exception:
                heatmap = None

    # A heuristic fallback is allowed only in explicit demo mode. Model mode
    # abstains rather than presenting a non-CAM visualization as an explanation.
    if want_heatmap and not heatmap and _STATE["mode"] != "model":
        try:
            g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
            g = (g - g.min()) / (g.max() - g.min() + 1e-6)
            spot = (1.0 - g) ** 1.5
            spot = (spot * 255).astype(np.uint8)
            heat = cv2.applyColorMap(spot, cv2.COLORMAP_JET)
            overlay = cv2.addWeighted(bgr, 0.55, heat, 0.45, 0)
            heatmap = _png_b64(overlay)
            heatmap_source = "fallback_spotlight"
        except Exception:
            pass

    if want_heatmap and _STATE["koil_mode"] == "model" and HAS_XAI_ADV:
        try:
            import torch

            koil_ck = _STATE["koil_ckpt"]
            image_size = int(koil_ck.get("img_size", 224))
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            small = cv2.resize(rgb, (image_size, image_size))
            mean = np.asarray(koil_ck.get("mean", [0.485, 0.456, 0.406]), dtype=np.float32)
            std = np.asarray(koil_ck.get("std", [0.229, 0.224, 0.225]), dtype=np.float32)
            normalized = (small.astype(np.float32) / 255.0 - mean) / std
            tensor = torch.from_numpy(normalized.transpose(2, 0, 1)[None]).to(_STATE["device"])
            koil_cam = compute_cam(
                _STATE["koil_net"],
                koil_ck.get("arch", "efficientnet_b0"),
                tensor,
                int(koil_ck["koil_index"]),
                "gradcam",
            )
            diagnostics = _cam_diagnostics(koil_cam)
            koil_xai = {
                "ok": diagnostics["valid"],
                "method": "gradcam",
                "target": "Koilocytotic morphology",
                "diagnostics": diagnostics,
                "heatmap": _png_b64(adv_overlay(bgr, koil_cam)) if diagnostics["valid"] else None,
                "disclaimer": "Class-specific attention map; not cell segmentation or proof of HPV infection.",
            }
        except Exception as exc:
            koil_xai = {
                "ok": False,
                "method": "gradcam",
                "target": "Koilocytotic morphology",
                "failure_reason": f"koil_xai_pipeline_error:{type(exc).__name__}",
                "heatmap": None,
                "disclaimer": "No KOIL explanation is released when attribution fails validation.",
            }

    # Synthetic contours are never returned alongside trained-model inference.
    contours = _fake_contours(bgr, top["key"], n=7) if _STATE["mode"] == "demo" else []

    # uncertainty viz
    unc_viz = None
    if uncertainty:
        unc_viz = {
            **uncertainty,
            "level": "high" if uncertainty.get("flag") else ("med" if uncertainty.get("entropy", 0) > 0.9 else "low"),
            "top_prob": round(float(top["prob"]), 4),
        }
    else:
        ent = round(float(-sum(p*np.log(p+1e-8) for p in [c["prob"] for c in cls])), 4)
        unc_viz = {
            "entropy": ent,
            "top_std": round(0.08 + (0.12 if low_conf else 0.0), 4),
            "flag": bool(low_conf),
            "level": "high" if low_conf else ("med" if ent > 1.1 else "low"),
            "top_prob": round(float(top["prob"]), 4),
        }

    out = {
        "mode": _STATE["mode"],
        "classification_mode": cls_mode,
        "quality": quality,
        "low_confidence": low_conf,
        "conf_threshold": LOW_CONF,
        "classification": cls,
        "top": top,
        "koilocyte": bool(koil_flag),
        "koil_assessment": koil_assessment,
        "uncertainty": uncertainty or unc_viz,
        "uncertainty_viz": unc_viz,
        "heatmap": heatmap,
        "heatmap_source": heatmap_source,
        "contours": contours,
        "contours_source": "synthetic_demo" if contours else None,
        "disclaimer": "Research pre-screen only; clinician confirmation is required. Not a diagnosis or HPV test.",
    }

    if conformal_set:
        out["conformal_set"] = conformal_set
    if evidential:
        out["evidential"] = evidential
    if zstack_info:
        out["zstack"] = zstack_info
    if wsi_info:
        out["wsi_simulation"] = wsi_info
    if advanced_xai:
        out["advanced_xai"] = advanced_xai
    if koil_xai:
        out["koil_xai"] = koil_xai

    return out


def apply_contour_edits(image_bytes: bytes, edits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply fake contour edits (class / points tweak) and return adjusted suggestion.
    This is a DEMO simulation — does not retrain or change the underlying model.
    """
    bgr = _to_bgr(image_bytes)
    # Recompute top class from current image (demo/model)
    if _STATE["mode"] == "model" and _STATE["net"] is not None:
        cls = _model_classify(bgr)
    else:
        cls = _demo_classify(bgr, image_bytes)
    top = cls[0]

    # Start from fresh fake contours then overlay client edits
    base = {c["id"]: c for c in _fake_contours(bgr, top["key"], n=8)}
    changed = 0
    for e in (edits or []):
        cid = e.get("id")
        if cid in base:
            c = base[cid].copy()
            if "class" in e and e["class"] in CLASSES:
                c["class"] = e["class"]
                changed += 1
            if "points" in e and isinstance(e["points"], list):
                c["points"] = e["points"]
                changed += 1
            base[cid] = c

    # Simple heuristic re-score: if user forced more HSIL/SCC/KOIL contours → nudge top
    edited = list(base.values())
    abnormal = sum(1 for c in edited if c["class"] in ("HSIL", "SCC", "KOIL"))
    if abnormal >= max(2, len(edited)//2):
        # push abnormal classes a bit higher in the returned list (UI only)
        for d in cls:
            if d["key"] in ("HSIL", "SCC", "KOIL"):
                d["prob"] = round(min(0.98, d["prob"] + 0.08), 4)
        cls = sorted(cls, key=lambda x: -x["prob"])

    return {
        "ok": True,
        "edited_count": changed,
        "contours": edited,
        "suggested_top": cls[0],
        "note": "การแก้ไข contour เป็น prototype demo — ยังไม่กระทบโมเดลจริง และไม่ใช่ฟีเจอร์ validated",
    }

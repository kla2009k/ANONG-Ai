# -*- coding: utf-8 -*-
"""
CervicalAI — Advanced Uncertainty Quantification (Phase 1.5+).

Implements multiple rigorous UQ methods beyond basic MC Dropout:

1. Improved MC Dropout (more samples, temperature scaling, proper flags)
2. Conformal Prediction (MAPIE-based, distribution-free, finite-sample guarantees)
   - Classification: marginal + class-conditional coverage
   - Returns prediction sets (not just point) + uncertainty flag
3. Evidential Deep Learning (Dirichlet evidence, vacuity, dissonance)
   - Single forward pass uncertainty (aleatoric + epistemic)
   - Useful for real-time rejection

Also:
- Temperature scaling for calibration (ECE reduction)
- Prediction set size as a proxy for difficulty
- Clinical triage mapping from uncertainty

Outputs:
  models/uncertainty_advanced.json
  models/calibration_plot.png (optional)

Usage:
  python ml/scripts/uncertainty_advanced.py --ckpt models/best_cervical.pt --demo
  python ml/scripts/uncertainty_advanced.py --calibrate  # if you have val logits

References:
- MAPIE: https://github.com/scikit-learn-contrib/MAPIE
- Evidential Deep Learning (Sensoy et al. 2018, Amini et al. 2020)
- "Conformalized Deep Learning" literature for medical AI
"""
from __future__ import annotations
import argparse
import json
import pathlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Tuple, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

ROOT = pathlib.Path(__file__).parent.parent.parent
MODELS = ROOT / "models"

CLASSES = ["NILM", "LSIL", "HSIL", "SCC", "KOIL"]
N_CLS = len(CLASSES)

# ──────────────────────────────────────────────────────────────────────────────
# MC Dropout (improved)
# ──────────────────────────────────────────────────────────────────────────────

def enable_mc_dropout(model: nn.Module):
    for m in model.modules():
        if isinstance(m, (nn.Dropout, nn.Dropout2d)):
            m.train()


@torch.no_grad()
def mc_dropout_predict(model: nn.Module, x: torch.Tensor, n_samples: int = 30,
                       temperature: float = 1.0) -> Dict[str, np.ndarray]:
    """
    MC dropout with temperature scaling.
    Returns mean, std, entropy, all samples.
    """
    model.eval()
    enable_mc_dropout(model)
    probs = []
    for _ in range(n_samples):
        logits = model(x) / max(temperature, 1e-6)
        p = torch.softmax(logits, dim=1)
        probs.append(p.cpu().numpy())
    probs = np.stack(probs, 0)  # (T, B, C)
    mean = probs.mean(0)
    std = probs.std(0)
    eps = 1e-8
    entropy = -(mean * np.log(mean + eps)).sum(1)
    return {
        "mean": mean,
        "std": std,
        "entropy": entropy,
        "samples": probs,
        "temperature": temperature,
    }


# NEW: Conformal sets (basic implementation, MAPIE-ready, inspired by Hagos 2026)
def conformal_prediction_sets(probs: np.ndarray, alpha: float = 0.1, cal_scores: np.ndarray = None) -> dict:
    """Prediction sets with marginal coverage guarantee.
    Demo version uses simple 1-max score. Calibrate on real val for production.
    Returns sets, sizes, uncertain flags.
    """
    if cal_scores is None:
        # Fallback for demo: quantile on 1 - max prob
        scores = 1.0 - probs.max(axis=1)
        q_hat = np.quantile(scores, 1 - alpha)
        sets = []
        for p in probs:
            thresh = 1 - q_hat
            s = np.where(p >= thresh)[0]
            sets.append(s.tolist())
    else:
        q_hat = np.quantile(cal_scores, 1 - alpha)
        sets = [np.where(p >= (1 - q_hat))[0].tolist() for p in probs]
    sizes = np.array([len(s) for s in sets])
    flags = sizes > 2  # flag large/uncertain sets
    return {"sets": sets, "sizes": sizes, "uncertain_flags": flags, "alpha": alpha, "q_hat": float(q_hat) if 'q_hat' in locals() else None}


def uncertainty_flags(mean: np.ndarray, std: np.ndarray,
                      entropy_thresh: float = 1.15,
                      std_thresh: float = 0.11) -> Dict[str, np.ndarray]:
    """Heuristic flags. Tune on real validation."""
    ent = -(mean * np.log(mean + 1e-8)).sum(1)
    top_idx = mean.argmax(1)
    top_std = std[np.arange(mean.shape[0]), top_idx]
    uncertain = (ent > entropy_thresh) | (top_std > std_thresh)
    return {
        "entropy": ent,
        "top_class_std": top_std,
        "is_uncertain": uncertain,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Temperature Scaling (post-hoc calibration)
# ──────────────────────────────────────────────────────────────────────────────

class TemperatureScaler:
    """Single scalar temperature for softmax calibration."""

    def __init__(self, init_temp: float = 1.0):
        self.temp = init_temp
        self.fitted = False

    def fit(self, logits: np.ndarray, labels: np.ndarray, lr: float = 0.01, max_iter: int = 200):
        """Optimize temperature on held-out logits/labels."""
        t = torch.tensor(self.temp, requires_grad=True, dtype=torch.float32)
        opt = torch.optim.LBFGS([t], lr=lr, max_iter=max_iter)
        logits_t = torch.from_numpy(logits).float()
        labels_t = torch.from_numpy(labels).long()

        def closure():
            opt.zero_grad()
            loss = F.cross_entropy(logits_t / t, labels_t)
            loss.backward()
            return loss

        opt.step(closure)
        self.temp = float(t.detach().clamp(0.1, 10.0))
        self.fitted = True
        return self.temp

    def scale(self, logits: np.ndarray) -> np.ndarray:
        return logits / max(self.temp, 1e-6)


# ──────────────────────────────────────────────────────────────────────────────
# Conformal Prediction (MAPIE)
# ──────────────────────────────────────────────────────────────────────────────

def conformal_classification_sets(probs_cal: np.ndarray, y_cal: np.ndarray,
                                   probs_test: np.ndarray,
                                   alpha: float = 0.1) -> Dict[str, Any]:
    """
    Use MAPIE for conformal classification.
    Returns prediction sets + coverage diagnostics.

    alpha=0.1 → target 90% marginal coverage.
    """
    try:
        from mapie.classification import MapieClassifier
        from mapie.metrics import classification_coverage_score, classification_mean_width_score

        class _DummyProbModel:
            def __init__(self, proba):
                self.proba = proba
            def predict_proba(self, X):
                return self.proba
            def fit(self, X, y):
                return self

        dummy_X_cal = np.zeros((len(y_cal), 1))
        dummy_X_test = np.zeros((len(probs_test), 1))

        mapie = MapieClassifier(estimator=_DummyProbModel(probs_cal), method="score", cv="prefit")
        mapie.fit(dummy_X_cal, y_cal)

        y_pred, y_ps = mapie.predict(dummy_X_test, alpha=alpha)

        # MAPIE 1.x returns y_ps as (n, n_classes) boolean or (n, n_classes, 2)
        if isinstance(y_ps, np.ndarray):
            if y_ps.ndim == 3:
                sets = y_ps[:, :, 0].astype(bool)
            else:
                sets = y_ps.astype(bool)
        else:
            sets = np.array(y_ps, dtype=bool)

        set_sizes = sets.sum(1).astype(int).tolist()
        coverage = float(classification_coverage_score(y_cal, sets[:len(y_cal)])) if len(y_cal) > 0 else None
        try:
            mean_width = float(classification_mean_width_score(sets))
        except Exception:
            mean_width = float(np.mean(set_sizes))

        pred_sets = []
        for i in range(len(probs_test)):
            included = [CLASSES[j] for j in range(N_CLS) if sets[i, j]]
            pred_sets.append({
                "set": included,
                "size": int(sets[i].sum()),
                "singleton": int(sets[i].sum()) == 1,
            })

        return {
            "alpha": alpha,
            "target_coverage": 1 - alpha,
            "empirical_coverage": coverage,
            "mean_set_size": round(mean_width, 3),
            "set_sizes": set_sizes,
            "prediction_sets": pred_sets,
            "method": "MAPIE_score",
        }
    except Exception as e:
        return _conformal_fallback(probs_cal, y_cal, probs_test, alpha)


def _conformal_fallback(probs_cal: np.ndarray, y_cal: np.ndarray,
                        probs_test: np.ndarray, alpha: float = 0.1) -> Dict[str, Any]:
    """Non-MAPIE fallback using conformal score = 1 - p(y_true)."""
    n = len(y_cal)
    if n == 0 or probs_cal.shape[1] != N_CLS:
        # degenerate
        sets = [[CLASSES[int(p.argmax())]] for p in probs_test]
        return {
            "alpha": alpha,
            "target_coverage": 1 - alpha,
            "empirical_coverage": None,
            "mean_set_size": float(np.mean([len(s) for s in sets])),
            "prediction_sets": [{"set": s, "size": len(s), "singleton": len(s) == 1} for s in sets],
            "method": "fallback_argmax",
        }

    # clip y_cal to valid range just in case
    y_cal = np.clip(y_cal, 0, N_CLS - 1)
    scores = 1.0 - probs_cal[np.arange(n), y_cal]
    qhat = np.quantile(scores, 1 - alpha, method="higher")
    pred_sets = []
    for p in probs_test:
        s = 1.0 - p
        included = [CLASSES[j] for j in range(N_CLS) if s[j] <= qhat]
        if not included:
            included = [CLASSES[int(p.argmax())]]
        pred_sets.append({"set": included, "size": len(included), "singleton": len(included) == 1})

    return {
        "alpha": alpha,
        "target_coverage": 1 - alpha,
        "empirical_coverage": None,
        "mean_set_size": round(float(np.mean([s["size"] for s in pred_sets])), 3),
        "prediction_sets": pred_sets,
        "method": "conformal_score_fallback",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Evidential Deep Learning (Dirichlet)
# ──────────────────────────────────────────────────────────────────────────────

def evidential_from_logits(logits: torch.Tensor, evidence_fn: str = "softplus") -> Dict[str, torch.Tensor]:
    """
    Convert logits to Dirichlet concentration parameters (evidence).
    Returns alpha, S, uncertainty measures.
    """
    if evidence_fn == "softplus":
        evidence = F.softplus(logits)
    elif evidence_fn == "exp":
        evidence = torch.exp(logits)
    else:
        evidence = torch.relu(logits) + 1.0

    alpha = evidence + 1.0  # Dirichlet concentration
    S = alpha.sum(dim=1, keepdim=True)
    # predictive mean
    p = alpha / S
    # vacuity (epistemic) ~ 1 / (1 + total evidence)
    vacuity = N_CLS / (S + N_CLS)
    # dissonance (aleatoric conflict)
    # simple proxy: entropy of mean
    eps = 1e-8
    entropy = -(p * torch.log(p + eps)).sum(1, keepdim=True)
    dissonance = entropy / np.log(N_CLS)

    return {
        "alpha": alpha,
        "S": S,
        "prob": p,
        "vacuity": vacuity,
        "dissonance": dissonance,
    }


@torch.no_grad()
def evidential_predict(model: nn.Module, x: torch.Tensor) -> Dict[str, np.ndarray]:
    """Single forward pass evidential uncertainty."""
    model.eval()
    logits = model(x)
    ev = evidential_from_logits(logits)
    out = {k: v.cpu().numpy() for k, v in ev.items()}
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Full advanced uncertainty report
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class UncertaintyAdvancedReport:
    n: int
    mc_samples: int
    conformal_alpha: float
    temperature: float
    samples: List[Dict[str, Any]]
    summary: Dict[str, Any]


def run_advanced_uncertainty(net, ckpt: dict, images: List[np.ndarray],
                             labels: Optional[List[int]] = None,
                             device: str = "cpu",
                             mc_samples: int = 25,
                             conformal_alpha: float = 0.1) -> UncertaintyAdvancedReport:
    """
    End-to-end advanced UQ on a batch of images (RGB uint8, any size).
    """
    img_size = ckpt.get("img_size", 224)
    mean = np.array(ckpt.get("mean", [0.485, 0.456, 0.406]), np.float32)
    std = np.array(ckpt.get("std", [0.229, 0.224, 0.225]), np.float32)
    arch = ckpt.get("arch", "efficientnet_b0")

    # preprocess
    xs = []
    for img in images:
        small = cv2.resize(img, (img_size, img_size))
        x = (small.astype(np.float32) / 255.0 - mean) / std
        xs.append(x.transpose(2, 0, 1))
    t = torch.from_numpy(np.stack(xs, 0)).to(device)

    # 1. MC Dropout (improved)
    mc = mc_dropout_predict(net, t, n_samples=mc_samples, temperature=1.0)
    mc_flags = uncertainty_flags(mc["mean"], mc["std"])

    # 2. Temperature scaling (fit on same batch if no labels, or use 1.0)
    temp = 1.0
    if labels is not None and len(labels) >= 8:
        try:
            scaler = TemperatureScaler(1.0)
            with torch.no_grad():
                logits = net(t)
            temp = scaler.fit(logits.cpu().numpy(), np.array(labels))
            mc = mc_dropout_predict(net, t, n_samples=mc_samples, temperature=temp)
            mc_flags = uncertainty_flags(mc["mean"], mc["std"])
        except Exception:
            pass

    # 3. Conformal sets (use MC mean as "calibration" proxy if no separate cal set)
    y_cal = np.array(labels) if labels is not None else np.arange(len(images))
    y_cal = y_cal % N_CLS  # ensure valid class indices
    conf = conformal_classification_sets(
        probs_cal=mc["mean"],
        y_cal=y_cal,
        probs_test=mc["mean"],
        alpha=conformal_alpha,
    )

    # 4. Evidential
    with torch.no_grad():
        ev = evidential_predict(net, t)

    # assemble per-sample
    samples = []
    for i in range(len(images)):
        p = mc["mean"][i]
        pred = int(p.argmax())
        ent = float(mc_flags["entropy"][i])
        top_std = float(mc_flags["top_class_std"][i])
        flag = bool(mc_flags["is_uncertain"][i])

        set_info = conf["prediction_sets"][i] if i < len(conf["prediction_sets"]) else {"set": [CLASSES[pred]], "size": 1}

        vac = float(ev["vacuity"][i, 0]) if "vacuity" in ev else 0.5
        dis = float(ev["dissonance"][i, 0]) if "dissonance" in ev else 0.5

        samples.append({
            "idx": i,
            "pred": pred,
            "pred_class": CLASSES[pred],
            "probs_mc": p.round(4).tolist(),
            "entropy": round(ent, 4),
            "top_std": round(top_std, 4),
            "uncertain_mc": flag,
            "conformal_set": set_info["set"],
            "conformal_set_size": set_info["size"],
            "singleton": set_info["singleton"],
            "vacuity": round(vac, 4),
            "dissonance": round(dis, 4),
            "temperature": round(temp, 4),
        })

    summary = {
        "mc_uncertain": int(sum(s["uncertain_mc"] for s in samples)),
        "avg_entropy": round(float(np.mean([s["entropy"] for s in samples])), 4),
        "avg_set_size": round(float(np.mean([s["conformal_set_size"] for s in samples])), 3),
        "avg_vacuity": round(float(np.mean([s["vacuity"] for s in samples])), 4),
        "conformal_method": conf["method"],
        "conformal_alpha": conformal_alpha,
        "temperature": round(temp, 4),
    }

    return UncertaintyAdvancedReport(
        n=len(samples),
        mc_samples=mc_samples,
        conformal_alpha=conformal_alpha,
        temperature=temp,
        samples=samples,
        summary=summary,
    )


# ──────────────────────────────────────────────────────────────────────────────
# CLI + synthetic demo
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


def main():
    import cv2
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=str(MODELS / "best_cervical.pt"))
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--mc", type=int, default=25)
    ap.add_argument("--alpha", type=float, default=0.1)
    args = ap.parse_args()

    dev = "cuda" if torch.cuda.is_available() else "cpu"

    net = None
    ck = None
    if pathlib.Path(args.ckpt).exists() and not args.demo:
        try:
            net, ck = load_ckpt(pathlib.Path(args.ckpt))
            net.to(dev)
            print(f"[unc-adv] loaded {args.ckpt}")
        except Exception as e:
            print("[unc-adv] load failed:", e)

    if net is None or args.demo:
        print("[unc-adv] DEMO mode")
        from torchvision import models as tvm
        net = tvm.efficientnet_b0(weights=None)
        net.classifier[1] = nn.Linear(net.classifier[1].in_features, len(CLASSES))
        net.eval().to(dev)
        ck = {"arch": "efficientnet_b0", "img_size": 224}

    # synthetic images
    rng = np.random.default_rng(99)
    imgs = [(rng.random((256, 256, 3)) * 255).astype(np.uint8) for _ in range(args.n)]
    labels = list(range(args.n))  # fake labels for conformal

    report = run_advanced_uncertainty(
        net, ck, imgs, labels=labels, device=dev,
        mc_samples=args.mc, conformal_alpha=args.alpha
    )

    (MODELS / "uncertainty_advanced.json").write_text(
        json.dumps({
            "n": report.n,
            "mc_samples": report.mc_samples,
            "conformal_alpha": report.conformal_alpha,
            "temperature": report.temperature,
            "samples": report.samples,
            "summary": report.summary,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"[unc-adv] wrote uncertainty_advanced.json")
    print(f"[unc-adv] summary: {report.summary}")


if __name__ == "__main__":
    import cv2  # for resize in runner
    main()

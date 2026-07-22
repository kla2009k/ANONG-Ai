#!/usr/bin/env python3
"""Build latest-model CRIC web charts and fold-specific Grad-CAM cases."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from torchvision.transforms import InterpolationMode
from torchvision.transforms import functional as TF


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.grade_research_v3 import GRADE_CLASSES, IMAGENET_MEAN, IMAGENET_STD, GradeResearchNet


MODELS = ROOT / "models" / "cric_grade_cv"
SPLITS = ROOT / "data" / "processed" / "cric_grade_grouped"
PUBLIC = ROOT / "web-react" / "public"
EVIDENCE = PUBLIC / "evidence" / "cric-latest"
GALLERY = PUBLIC / "cric-model-gallery"
COLORS = ["#54A88A", "#E7BF54", "#C44F79", "#B64A46"]
INK = "#3E2931"
MUTED = "#755E66"
PAPER = "#FFF9ED"
CLASSES = list(GRADE_CLASSES)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_oof() -> tuple[np.ndarray, np.ndarray, list[dict], list[float]]:
    labels, probabilities, records, fold_accuracy = [], [], [], []
    for fold in range(1, 6):
        arrays = np.load(MODELS / f"cric_b0_grouped_fold_{fold}_oof.npz")
        with (SPLITS / f"fold_{fold}" / "test.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        fold_labels = arrays["labels"].astype(np.int64)
        fold_probabilities = arrays["probabilities"].astype(np.float64)
        if len(rows) != len(fold_labels):
            raise RuntimeError(f"fold {fold} manifest and OOF length differ")
        if not np.array_equal(fold_labels, np.asarray([int(row["label5"]) for row in rows])):
            raise RuntimeError(f"fold {fold} labels do not align with its locked test manifest")
        predicted = fold_probabilities.argmax(1)
        fold_accuracy.append(float((predicted == fold_labels).mean()))
        for index, row in enumerate(rows):
            records.append({"fold": fold, "index": index, **row})
        labels.append(fold_labels)
        probabilities.append(fold_probabilities)
    return np.concatenate(labels), np.concatenate(probabilities), records, fold_accuracy


def unique_group_selection(indices: np.ndarray, records: list[dict], used: set[str], limit: int) -> list[int]:
    selected = []
    for index in indices.tolist():
        group = records[index]["group_id"]
        if group in used:
            continue
        used.add(group)
        selected.append(index)
        if len(selected) == limit:
            break
    return selected


def select_cases(labels: np.ndarray, probabilities: np.ndarray, records: list[dict]) -> list[int]:
    predicted = probabilities.argmax(1)
    confidence = probabilities.max(1)
    selected: list[int] = []
    for class_index in range(4):
        used: set[str] = set()
        correct = np.flatnonzero((labels == class_index) & (predicted == class_index) & (confidence >= 0.60))
        correct = correct[np.argsort(-confidence[correct])]
        errors = np.flatnonzero((labels == class_index) & (predicted != class_index) & (confidence >= 0.60))
        errors = errors[np.argsort(-confidence[errors])]
        abstained = np.flatnonzero((labels == class_index) & (confidence < 0.60))
        abstained = abstained[np.argsort(confidence[abstained])]
        class_cases = unique_group_selection(correct, records, used, 3)
        class_cases += unique_group_selection(errors, records, used, 1)
        class_cases += unique_group_selection(abstained, records, used, 1)
        if len(class_cases) != 5:
            raise RuntimeError(f"could not select five auditable cases for {CLASSES[class_index]}")
        selected.extend(class_cases)
    return selected


def image_tensor(image: Image.Image) -> torch.Tensor:
    resized = TF.resize(image, (224, 224), InterpolationMode.BILINEAR)
    return TF.normalize(TF.to_tensor(resized), IMAGENET_MEAN, IMAGENET_STD).unsqueeze(0)


def gradcam(model: GradeResearchNet, tensor: torch.Tensor, class_index: int) -> np.ndarray:
    activations: dict[str, torch.Tensor] = {}
    gradients: dict[str, torch.Tensor] = {}
    layer = model.features[-1]
    forward_hook = layer.register_forward_hook(lambda _m, _i, output: activations.__setitem__("value", output))
    backward_hook = layer.register_full_backward_hook(lambda _m, _gi, output: gradients.__setitem__("value", output[0]))
    try:
        model.zero_grad(set_to_none=True)
        score = model(tensor)["grade_logits"][0, class_index]
        score.backward()
        feature_map = activations["value"][0]
        weights = gradients["value"][0].mean(dim=(1, 2))
        cam = torch.relu((weights[:, None, None] * feature_map).sum(0)).detach().cpu().numpy()
    finally:
        forward_hook.remove()
        backward_hook.remove()
    if not np.isfinite(cam).all() or float(cam.max() - cam.min()) <= 1e-8:
        raise RuntimeError("degenerate Grad-CAM for selected CRIC case")
    return ((cam - cam.min()) / (cam.max() - cam.min())).astype(np.float32)


def save_case_assets(labels: np.ndarray, probabilities: np.ndarray, records: list[dict], selected: list[int]) -> list[dict]:
    GALLERY.mkdir(parents=True, exist_ok=True)
    output: list[dict] = []
    by_fold: dict[int, list[int]] = {}
    for index in selected:
        by_fold.setdefault(int(records[index]["fold"]), []).append(index)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    for fold, indices in sorted(by_fold.items()):
        checkpoint = torch.load(MODELS / f"cric_b0_grouped_fold_{fold}.pt", map_location=device, weights_only=False)
        model = GradeResearchNet("efficientnet_b0", pretrained=False, dropout=0.25).to(device)
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        for global_index in indices:
            row = records[global_index]
            true_index = int(labels[global_index])
            predicted_index = int(probabilities[global_index].argmax())
            confidence = float(probabilities[global_index].max())
            with Image.open(row["crop_path"]) as opened:
                original = opened.convert("RGB")
            tensor = image_tensor(original).to(device)
            cam = gradcam(model, tensor, predicted_index)
            original_array = np.asarray(original)
            resized_cam = cv2.resize(cam, original.size, interpolation=cv2.INTER_CUBIC)
            heat = cv2.applyColorMap(np.uint8(np.clip(resized_cam, 0, 1) * 255), cv2.COLORMAP_TURBO)
            heat = cv2.cvtColor(heat, cv2.COLOR_BGR2RGB)
            overlay = np.uint8(np.clip(original_array * 0.55 + heat * 0.45, 0, 255))
            stem = f"{CLASSES[true_index].lower()}-fold{fold}-{row['group_id']}-{row['cell_id']}"
            original_path = GALLERY / f"{stem}-original.jpg"
            cam_path = GALLERY / f"{stem}-gradcam.jpg"
            original.save(original_path, quality=94, optimize=True)
            Image.fromarray(overlay).save(cam_path, quality=94, optimize=True)
            status = "accepted_correct" if confidence >= 0.60 and true_index == predicted_index else "accepted_error" if confidence >= 0.60 else "abstained"
            output.append({
                "id": f"CRIC-OOF-{len(output) + 1:02d}",
                "fold": fold,
                "group_id": row["group_id"],
                "cell_id": int(row["cell_id"]),
                "original": f"cric-model-gallery/{original_path.name}",
                "gradcam": f"cric-model-gallery/{cam_path.name}",
                "true_label": CLASSES[true_index],
                "predicted_label": CLASSES[predicted_index],
                "correct": true_index == predicted_index,
                "confidence": confidence,
                "accepted_at_0_60": confidence >= 0.60,
                "review_status": status,
                "probabilities": {name: float(value) for name, value in zip(CLASSES, probabilities[global_index])},
                "cam_target": CLASSES[predicted_index],
                "cam_method": "Grad-CAM on fold-specific EfficientNet-B0 final convolutional block",
                "cam_disclaimer": "Post-hoc class activation; not cell segmentation or causal proof.",
                "original_sha256": sha256(original_path),
                "gradcam_sha256": sha256(cam_path),
            })
    lookup = {(item["fold"], item["group_id"], item["cell_id"]): item for item in output}
    ordered = [lookup[(records[index]["fold"], records[index]["group_id"], int(records[index]["cell_id"]))] for index in selected]
    for position, item in enumerate(ordered, 1):
        item["id"] = f"CRIC-OOF-{position:02d}"
    return ordered


def chart_style() -> None:
    plt.rcParams.update({"figure.facecolor": PAPER, "axes.facecolor": PAPER, "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "font.family": "DejaVu Sans"})


def save_charts(labels: np.ndarray, probabilities: np.ndarray, fold_accuracy: list[float], class_metrics: dict, selective: list[dict]) -> list[dict]:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    chart_style()
    predicted = probabilities.argmax(1)
    cm = confusion_matrix(labels, predicted, labels=range(4))
    figures = []

    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    image = ax.imshow(cm, cmap="RdPu")
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{cm[i, j]:,}\n{cm[i, j] / max(cm[i].sum(), 1):.1%}", ha="center", va="center", color="white" if cm[i, j] > cm.max() * 0.45 else INK, fontsize=10)
    ax.set_xticks(range(4), CLASSES); ax.set_yticks(range(4), CLASSES)
    ax.set_xlabel("Predicted grade"); ax.set_ylabel("True grade"); ax.set_title("CRIC pooled out-of-fold confusion matrix", weight="bold")
    fig.colorbar(image, ax=ax, fraction=0.045, label="Cell count"); fig.tight_layout()
    path = EVIDENCE / "cric_oof_confusion.png"; fig.savefig(path, dpi=180, bbox_inches="tight"); plt.close(fig)
    figures.append({"file": f"evidence/cric-latest/{path.name}", "title": "Pooled out-of-fold confusion matrix", "detail": "Counts and row percentages across all 10,003 CRIC cells; every prediction comes from the fold where its parent image was held out."})

    fig, ax = plt.subplots(figsize=(8, 4.8))
    x = np.arange(4); width = 0.24
    for offset, metric, color in ((-width, "precision", "#7D6FB2"), (0, "recall", "#C44F79"), (width, "f1", "#54A88A")):
        values = [class_metrics[name][metric] for name in CLASSES]
        bars = ax.bar(x + offset, values, width, label=metric.title(), color=color)
        ax.bar_label(bars, fmt="%.2f", fontsize=8, padding=2)
    ax.set_xticks(x, CLASSES); ax.set_ylim(0, 1.08); ax.set_ylabel("Score"); ax.set_title("Latest CRIC per-class performance", weight="bold"); ax.legend(frameon=False, ncol=3)
    ax.grid(axis="y", alpha=.2); fig.tight_layout()
    path = EVIDENCE / "cric_class_metrics.png"; fig.savefig(path, dpi=180, bbox_inches="tight"); plt.close(fig)
    figures.append({"file": f"evidence/cric-latest/{path.name}", "title": "Precision, recall, and F1 by grade", "detail": "NILM is strongest; SCC remains the principal safety limitation and is not hidden by aggregate accuracy."})

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    folds = np.arange(1, 6)
    bars = ax.bar(folds, fold_accuracy, color=["#54A88A" if value >= .90 else "#E7BF54" for value in fold_accuracy])
    ax.axhline(np.mean(fold_accuracy), color="#C44F79", linestyle="--", label=f"Mean {np.mean(fold_accuracy):.3f}")
    ax.bar_label(bars, labels=[f"{value:.1%}" for value in fold_accuracy], padding=3)
    ax.set_ylim(.78, .94); ax.set_xticks(folds, [f"F{fold}" for fold in folds]); ax.set_ylabel("Accuracy"); ax.set_title("Parent-image-disjoint accuracy by fold", weight="bold"); ax.legend(frameon=False)
    ax.grid(axis="y", alpha=.2); fig.tight_layout()
    path = EVIDENCE / "cric_fold_accuracy.png"; fig.savefig(path, dpi=180, bbox_inches="tight"); plt.close(fig)
    figures.append({"file": f"evidence/cric-latest/{path.name}", "title": "Accuracy across five held-out folds", "detail": "All folds are retained. Fold 4 shows the domain variability that would be hidden by reporting only the best split."})

    fig, left = plt.subplots(figsize=(8, 4.8)); right = left.twinx()
    threshold = [row["threshold"] for row in selective]
    accuracy = [row["selective_accuracy"] for row in selective]
    coverage = [row["coverage"] for row in selective]
    left.plot(threshold, accuracy, marker="o", color="#C44F79", label="Selective accuracy")
    right.plot(threshold, coverage, marker="s", color="#54A88A", label="Coverage")
    left.axvline(.60, color="#E7BF54", linestyle="--", label="Reported threshold 0.60")
    left.set_ylim(.85, 1.01); right.set_ylim(.45, 1.01); left.set_xlabel("Confidence threshold"); left.set_ylabel("Selective accuracy", color="#C44F79"); right.set_ylabel("Coverage", color="#54A88A")
    left.set_title("Accuracy-coverage trade-off", weight="bold"); left.grid(alpha=.2)
    lines = left.get_lines() + right.get_lines(); left.legend(lines, [line.get_label() for line in lines], frameon=False, loc="center right")
    fig.tight_layout(); path = EVIDENCE / "cric_selective_tradeoff.png"; fig.savefig(path, dpi=180, bbox_inches="tight"); plt.close(fig)
    figures.append({"file": f"evidence/cric-latest/{path.name}", "title": "Selective accuracy versus coverage", "detail": "At threshold 0.60, accuracy is 91.7% at 94.1% coverage. The rejected 5.9% require human review."})

    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    scc_mask = labels == 3
    scc_high_grade_capture = float((predicted[scc_mask] >= 2).mean())
    names = ["NILM exact", "LSIL exact", "HSIL exact", "SCC exact", "SCC→high-grade", "KOIL*"]
    values = [class_metrics[name]["recall"] for name in CLASSES] + [scc_high_grade_capture, 0.9624]
    bars = ax.barh(names, values, color=[*COLORS, "#E78A83", "#7D6FB2"])
    ax.bar_label(bars, labels=[f"{value:.1%}" for value in values], padding=4)
    ax.set_xlim(0, 1.08); ax.set_xlabel("Recall / sensitivity"); ax.set_title("Recall by evaluated endpoint", weight="bold"); ax.grid(axis="x", alpha=.2)
    ax.text(.01, -.23, "SCC→high-grade counts SCC predicted as HSIL or SCC. * KOIL uses separate SIPaKMeD data.", transform=ax.transAxes, fontsize=9, color=MUTED)
    fig.tight_layout(); path = EVIDENCE / "cric_recall_by_endpoint.png"; fig.savefig(path, dpi=180, bbox_inches="tight"); plt.close(fig)
    figures.append({"file": f"evidence/cric-latest/{path.name}", "title": "Recall by endpoint", "detail": "CRIC grade recalls and the independent SIPaKMeD KOIL sensitivity share a scale but not a dataset or label ontology."})
    return figures


def main() -> int:
    labels, probabilities, records, fold_accuracy = load_oof()
    predicted = probabilities.argmax(1)
    precision, recall, f1, support = precision_recall_fscore_support(labels, predicted, labels=range(4), zero_division=0)
    class_metrics = {name: {"precision": float(precision[i]), "recall": float(recall[i]), "f1": float(f1[i]), "support": int(support[i])} for i, name in enumerate(CLASSES)}
    confidence = probabilities.max(1)
    thresholds = np.linspace(.40, .95, 12)
    selective = []
    for threshold in thresholds:
        accepted = confidence >= threshold
        selective.append({"threshold": float(threshold), "coverage": float(accepted.mean()), "selective_accuracy": float((predicted[accepted] == labels[accepted]).mean()), "accepted": int(accepted.sum()), "abstained": int((~accepted).sum())})
    figures = save_charts(labels, probabilities, fold_accuracy, class_metrics, selective)
    selected = select_cases(labels, probabilities, records)
    cases = save_case_assets(labels, probabilities, records, selected)
    manifest = {
        "schema_version": "1.0",
        "dataset": "CRIC Cervix Cell Classification",
        "model": "EfficientNet-B0 hierarchical four-grade research candidate",
        "protocol": "Fold-specific checkpoint applied only to that fold's parent-image-disjoint OOF test cells; three-view TTA probabilities and single-view predicted-class Grad-CAM.",
        "selective_threshold": 0.60,
        "case_selection": "Per true grade: three accepted correct cases, one accepted error, and one abstained case, each from a different parent image.",
        "count": len(cases),
        "cases": cases,
    }
    (GALLERY / "index.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    evidence = {
        "schema_version": "1.0",
        "dataset": "CRIC Cervix Cell Classification",
        "cells": int(len(labels)),
        "parent_images": int(len({row["group_id"] for row in records})),
        "pooled_accuracy": float((predicted == labels).mean()),
        "macro_f1": float(np.mean(f1)),
        "fold_accuracy": fold_accuracy,
        "confusion_matrix": confusion_matrix(labels, predicted, labels=range(4)).tolist(),
        "class_metrics": class_metrics,
        "grouped_endpoints": {
            "high_grade_hsil_or_scc": {
                "captured": int(((labels >= 2) & (predicted >= 2)).sum()),
                "support": int((labels >= 2).sum()),
                "recall": float((predicted[labels >= 2] >= 2).mean()),
            },
            "scc_captured_as_high_grade": {
                "captured": int(((labels == 3) & (predicted >= 2)).sum()),
                "support": int((labels == 3).sum()),
                "recall": float((predicted[labels == 3] >= 2).mean()),
            },
        },
        "selective_curve": selective,
        "figures": figures,
        "limitations": ["Research candidate, not the deployed upload checkpoint.", "Conventional Pap-smear cells, not Thai ThinPrep clinical validation.", "SCC recall remains 50.3%.", "No molecular HPV endpoint."],
    }
    (EVIDENCE / "index.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"figures": len(figures), "gallery_cases": len(cases), "device": str(torch.device("cuda" if torch.cuda.is_available() else "cpu"))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

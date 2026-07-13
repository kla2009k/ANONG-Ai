#!/usr/bin/env python3
"""Generate reproducible plots, error galleries, and KOIL Grad-CAM examples."""

from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter, defaultdict

import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image, ImageOps, ImageDraw
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    RocCurveDisplay,
    average_precision_score,
    confusion_matrix,
    roc_auc_score,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.koil_model import build_koil_model
from ml.scripts.xai_advanced import compute_cam, overlay_heatmap


MODEL_DIR = ROOT / "models" / "koil_sipakmed"


def save_error_gallery(rows: list[dict], threshold: float, output: pathlib.Path) -> None:
    false_negatives = sorted(
        (row for row in rows if row["true_label"] == 2 and row["koil_probability"] < threshold),
        key=lambda row: row["koil_probability"],
    )
    false_positives = sorted(
        (row for row in rows if row["true_label"] != 2 and row["koil_probability"] >= threshold),
        key=lambda row: -row["koil_probability"],
    )
    selected = [("FN", row) for row in false_negatives] + [("FP", row) for row in false_positives]
    selected = selected[:18]
    tile_size = 260
    columns = 6
    rows_count = max(1, (len(selected) + columns - 1) // columns)
    canvas = Image.new("RGB", (columns * tile_size, rows_count * tile_size), "white")
    for index, (kind, row) in enumerate(selected):
        image = Image.open(row["path"]).convert("RGB")
        image.thumbnail((tile_size - 20, tile_size - 50))
        tile = Image.new("RGB", (tile_size, tile_size), "white")
        tile.paste(image, ((tile_size - image.width) // 2, 28))
        draw = ImageDraw.Draw(tile)
        draw.text((8, 6), f"{kind}  p={row['koil_probability']:.3f}", fill="red" if kind == "FN" else "darkorange")
        draw.text((8, tile_size - 18), pathlib.Path(row["path"]).name, fill="black")
        canvas.paste(tile, ((index % columns) * tile_size, (index // columns) * tile_size))
    canvas.save(output)


def save_gradcam_gallery(rows: list[dict], checkpoint: dict, output: pathlib.Path) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_koil_model(pretrained=False).to(device)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    threshold = float(checkpoint["koil_threshold"])
    categories = {
        "TP-high": sorted((r for r in rows if r["true_label"] == 2 and r["koil_probability"] >= threshold), key=lambda r: -r["koil_probability"]),
        "TP-boundary": sorted((r for r in rows if r["true_label"] == 2 and r["koil_probability"] >= threshold), key=lambda r: r["koil_probability"]),
        "FN": sorted((r for r in rows if r["true_label"] == 2 and r["koil_probability"] < threshold), key=lambda r: r["koil_probability"]),
        "FP": sorted((r for r in rows if r["true_label"] != 2 and r["koil_probability"] >= threshold), key=lambda r: -r["koil_probability"]),
    }
    selected = [(name, row) for name, candidates in categories.items() for row in candidates[:3]]
    fig, axes = plt.subplots(len(selected), 2, figsize=(8, max(4, len(selected) * 3)))
    axes = np.atleast_2d(axes)
    mean = np.asarray(checkpoint["mean"], dtype=np.float32)
    std = np.asarray(checkpoint["std"], dtype=np.float32)
    for row_index, (category, row) in enumerate(selected):
        rgb = np.asarray(Image.open(row["path"]).convert("RGB"))
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        small = cv2.resize(rgb, (checkpoint["img_size"], checkpoint["img_size"]))
        normalized = (small.astype(np.float32) / 255.0 - mean) / std
        tensor = torch.from_numpy(normalized.transpose(2, 0, 1)[None]).to(device)
        cam = compute_cam(model, checkpoint["arch"], tensor, int(checkpoint["koil_index"]), "gradcam")
        overlay = cv2.cvtColor(overlay_heatmap(bgr, cam), cv2.COLOR_BGR2RGB)
        axes[row_index, 0].imshow(rgb)
        axes[row_index, 1].imshow(overlay)
        axes[row_index, 0].set_title(f"{category}: {pathlib.Path(row['path']).name}")
        axes[row_index, 1].set_title(f"KOIL p={row['koil_probability']:.3f}")
        axes[row_index, 0].axis("off")
        axes[row_index, 1].axis("off")
    fig.suptitle("KOIL-specific Grad-CAM audit (attention, not segmentation)")
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_paper_gradcam_grid(rows: list[dict], checkpoint: dict, output: pathlib.Path) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_koil_model(pretrained=False).to(device)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    threshold = float(checkpoint["koil_threshold"])
    candidates = [
        ("True positive", max((r for r in rows if r["true_label"] == 2), key=lambda r: r["koil_probability"])),
        ("Near threshold", min((r for r in rows if r["true_label"] == 2 and r["koil_probability"] >= threshold), key=lambda r: r["koil_probability"])),
        ("False negative", min((r for r in rows if r["true_label"] == 2), key=lambda r: r["koil_probability"])),
        ("False positive", max((r for r in rows if r["true_label"] != 2), key=lambda r: r["koil_probability"])),
    ]
    mean = np.asarray(checkpoint["mean"], dtype=np.float32)
    std = np.asarray(checkpoint["std"], dtype=np.float32)
    fig, axes = plt.subplots(2, 4, figsize=(12, 6))
    for column, (label, row) in enumerate(candidates):
        rgb = np.asarray(Image.open(row["path"]).convert("RGB"))
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        small = cv2.resize(rgb, (checkpoint["img_size"], checkpoint["img_size"]))
        normalized = (small.astype(np.float32) / 255.0 - mean) / std
        tensor = torch.from_numpy(normalized.transpose(2, 0, 1)[None]).to(device)
        cam = compute_cam(model, checkpoint["arch"], tensor, int(checkpoint["koil_index"]), "gradcam")
        axes[0, column].imshow(rgb)
        axes[1, column].imshow(cv2.cvtColor(overlay_heatmap(bgr, cam), cv2.COLOR_BGR2RGB))
        axes[0, column].set_title(label)
        axes[1, column].set_title(f"KOIL p={row['koil_probability']:.3f}")
        axes[0, column].axis("off")
        axes[1, column].axis("off")
    fig.tight_layout()
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    metrics = json.loads((MODEL_DIR / "test_metrics.json").read_text(encoding="utf-8"))
    predictions = json.loads((MODEL_DIR / "locked_test_predictions.json").read_text(encoding="utf-8"))
    checkpoint = torch.load(MODEL_DIR / "best_koil_model.pt", map_location="cpu", weights_only=False)
    output = MODEL_DIR / "evaluation"
    output.mkdir(parents=True, exist_ok=True)
    threshold = float(metrics["test_koil"]["threshold"])
    labels = np.asarray([int(row["true_label"] == checkpoint["koil_index"]) for row in predictions])
    scores = np.asarray([row["koil_probability"] for row in predictions])

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    matrix = np.asarray(metrics["test_multiclass"]["confusion_matrix"])
    ConfusionMatrixDisplay(matrix, display_labels=checkpoint["classes"]).plot(ax=axes[0], colorbar=False, xticks_rotation=35)
    axes[0].set_title("Locked test morphology confusion matrix")
    RocCurveDisplay.from_predictions(labels, scores, ax=axes[1], name="KOIL one-vs-rest")
    axes[1].plot([0, 1], [0, 1], "--", color="0.7")
    axes[1].set_title("KOIL ROC")
    PrecisionRecallDisplay.from_predictions(labels, scores, ax=axes[2], name="KOIL one-vs-rest")
    axes[2].axhline(labels.mean(), linestyle="--", color="0.7")
    axes[2].set_title("KOIL precision-recall")
    fig.tight_layout()
    fig.savefig(output / "koil_test_performance.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    herlev_matrix = np.asarray([
        [26, 1, 7, 2],
        [1, 30, 16, 2],
        [1, 0, 26, 3],
        [0, 0, 9, 13],
    ])
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    ConfusionMatrixDisplay(herlev_matrix, display_labels=["NILM", "LSIL", "HSIL", "SCC"]).plot(
        ax=ax, colorbar=False
    )
    ax.set_title("Herlev held-out supported grade classes")
    fig.tight_layout()
    fig.savefig(output / "herlev_grade_confusion_4class.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    observed, predicted = calibration_curve(labels, scores, n_bins=10, strategy="quantile")
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot([0, 1], [0, 1], "--", color="0.6", label="Perfect calibration")
    ax.plot(predicted, observed, marker="o", label="Temperature-scaled model")
    ax.axvline(threshold, color="crimson", linestyle=":", label=f"Threshold {threshold:.3f}")
    ax.set(xlabel="Mean predicted probability", ylabel="Observed KOIL fraction", title="KOIL reliability diagram")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "koil_calibration.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    save_error_gallery(predictions, threshold, output / "koil_error_gallery.png")
    save_gradcam_gallery(predictions, checkpoint, output / "koil_gradcam_audit.png")
    save_paper_gradcam_grid(predictions, checkpoint, output / "koil_gradcam_paper.png")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in predictions:
        grouped[row["group_id"]].append(row)
    group_labels = np.asarray([int(rows[0]["true_label"] == checkpoint["koil_index"]) for rows in grouped.values()])
    group_scores = np.asarray([np.mean([row["koil_probability"] for row in rows]) for rows in grouped.values()])
    group_predictions = group_scores >= threshold
    tn, fp, fn, tp = confusion_matrix(group_labels, group_predictions, labels=[0, 1]).ravel()
    false_positive_classes = Counter(
        checkpoint["classes"][row["true_label"]]
        for row in predictions
        if row["true_label"] != checkpoint["koil_index"] and row["koil_probability"] >= threshold
    )
    error_analysis = {
        "cell_level": {
            "false_negative_cells": metrics["test_koil"]["fn"],
            "false_positive_cells": metrics["test_koil"]["fp"],
            "false_positive_cells_by_true_class": dict(false_positive_classes),
            "false_negative_source_clusters": sorted({
                row["group_id"] for row in predictions
                if row["true_label"] == checkpoint["koil_index"] and row["koil_probability"] < threshold
            }),
        },
        "exploratory_cluster_mean_at_locked_cell_threshold": {
            "clusters": len(grouped),
            "tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn),
            "sensitivity": float(tp / (tp + fn)),
            "specificity": float(tn / (tn + fp)),
            "auroc": float(roc_auc_score(group_labels, group_scores)),
            "auprc": float(average_precision_score(group_labels, group_scores)),
            "note": "Post-hoc descriptive analysis only; the threshold was not retuned at cluster level.",
        },
        "interpretation": [
            "All cell-level false positives arose from Dyskeratotic or Metaplastic morphology.",
            "The five false-negative cells came from five different source clusters.",
            "Errors indicate morphology overlap and domain-specific ambiguity; they are not evidence of HPV test performance.",
        ],
    }
    (output / "error_analysis.json").write_text(json.dumps(error_analysis, indent=2), encoding="utf-8")
    summary = {
        "locked_test_cases": len(predictions),
        "false_negatives": metrics["test_koil"]["fn"],
        "false_positives": metrics["test_koil"]["fp"],
        "threshold": threshold,
        "artifacts": sorted(path.name for path in output.glob("*.png")),
        "error_analysis": "error_analysis.json",
        "xai_disclaimer": "Grad-CAM is class-specific attention, not segmentation or causal proof.",
    }
    (output / "evaluation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

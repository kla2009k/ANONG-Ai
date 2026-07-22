#!/usr/bin/env python3
"""Aggregate five CRIC out-of-fold artifacts with group-bootstrap intervals."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.scripts.train_cric_grade_cv import metrics_from_predictions


def group_bootstrap(labels: np.ndarray, probabilities: np.ndarray, groups: np.ndarray,
                    iterations: int = 2000, seed: int = 20260722, selective_threshold: float = 0.60) -> dict:
    rng = np.random.default_rng(seed)
    unique = np.unique(groups)
    group_indices = {group: np.flatnonzero(groups == group) for group in unique}
    accuracy, macro_f1, selective_accuracy, selective_coverage = [], [], [], []
    for _ in range(iterations):
        sampled = rng.choice(unique, size=len(unique), replace=True)
        indices = np.concatenate([group_indices[group] for group in sampled])
        predicted = probabilities[indices].argmax(1)
        accuracy.append(float((predicted == labels[indices]).mean()))
        macro_f1.append(float(f1_score(labels[indices], predicted, average="macro", zero_division=0)))
        accepted = probabilities[indices].max(1) >= selective_threshold
        selective_coverage.append(float(accepted.mean()))
        selective_accuracy.append(float((predicted[accepted] == labels[indices][accepted]).mean()))
    return {
        "unit": "CRIC parent microscope image",
        "iterations": iterations,
        "accuracy_95_ci": [float(value) for value in np.quantile(accuracy, [0.025, 0.975])],
        "macro_f1_95_ci": [float(value) for value in np.quantile(macro_f1, [0.025, 0.975])],
        "selective_threshold": selective_threshold,
        "selective_accuracy_95_ci": [float(value) for value in np.quantile(selective_accuracy, [0.025, 0.975])],
        "selective_coverage_95_ci": [float(value) for value in np.quantile(selective_coverage, [0.025, 0.975])],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "processed" / "cric_grade_grouped")
    parser.add_argument("--models", type=Path, default=ROOT / "models" / "cric_grade_cv")
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--public-output", type=Path, default=ROOT / "web-react" / "public" / "evidence" / "cric_grade_5fold_summary.json")
    args = parser.parse_args()

    fold_metrics, labels, probabilities, triage, high_risk, groups = [], [], [], [], [], []
    for fold in range(1, 6):
        stem = f"cric_b0_grouped_fold_{fold}"
        result = json.loads((args.models / f"{stem}.json").read_text(encoding="utf-8"))
        arrays = np.load(args.models / f"{stem}_oof.npz")
        with (args.data / f"fold_{fold}" / "test.csv").open(encoding="utf-8", newline="") as handle:
            manifest = list(csv.DictReader(handle))
        manifest_labels = np.asarray([int(row["label5"]) for row in manifest])
        if len(manifest) != len(arrays["labels"]) or not np.array_equal(manifest_labels, arrays["labels"]):
            raise RuntimeError(f"fold {fold} OOF arrays do not align with the locked manifest")
        fold_metrics.append({"fold": fold, **result["test_tta"]})
        labels.append(arrays["labels"])
        probabilities.append(arrays["probabilities"])
        triage.append(arrays["triage_scores"])
        high_risk.append(arrays["high_risk_scores"])
        groups.extend(row["group_id"] for row in manifest)

    labels_array = np.concatenate(labels)
    probabilities_array = np.concatenate(probabilities)
    triage_array = np.concatenate(triage)
    high_risk_array = np.concatenate(high_risk)
    groups_array = np.asarray(groups)
    if len(np.unique(groups_array)) != 395:
        raise RuntimeError("expected every CRIC parent image exactly once across OOF test folds")
    pooled = metrics_from_predictions(labels_array, probabilities_array, triage_array, high_risk_array)
    numeric = ("accuracy", "balanced_accuracy", "macro_f1", "high_risk_exact_recall", "triage_head_recall_at_0_5")
    mean_sd = {
        metric: {
            "mean": float(np.mean([fold[metric] for fold in fold_metrics])),
            "sd": float(np.std([fold[metric] for fold in fold_metrics], ddof=1)),
        }
        for metric in numeric
    }
    bootstrap = group_bootstrap(labels_array, probabilities_array, groups_array, args.bootstrap)
    selective_60 = next(row for row in pooled["selective_prediction"] if abs(row["threshold"] - 0.60) < 1e-9)
    report = {
        "dataset": "CRIC Cervix Cell Classification",
        "doi": "10.6084/m9.figshare.c.4960286.v2",
        "endpoint": "NILM / LSIL / HSIL / SCC cell-grade classification",
        "model": "EfficientNet-B0 with hierarchical and ordinal auxiliary heads",
        "protocol": "five-fold parent-image-disjoint cross-validation with validation-selected checkpoints and three-view test TTA",
        "folds": fold_metrics,
        "mean_sd": mean_sd,
        "pooled_oof": pooled,
        "group_bootstrap": bootstrap,
        "claim_assessment": {
            "full_cohort_accuracy_above_90": pooled["accuracy"] >= 0.90,
            "selective_accuracy_above_90_at_threshold_0_60": selective_60["selective_accuracy"] >= 0.90,
            "selective_threshold": 0.60,
            "selective_accuracy": selective_60["selective_accuracy"],
            "selective_coverage": selective_60["coverage"],
            "required_wording": "Selective four-grade accuracy among accepted CRIC cases; remaining cases are abstained for human review.",
        },
        "limitations": [
            "CRIC is conventional Pap smear, not Thai ThinPrep clinical validation.",
            "SCC support is only 161 cells from 21 parent images and recall remains unstable.",
            "ASC-US and ASC-H were excluded rather than relabelled into unsupported categories.",
            "This endpoint does not detect molecular HPV infection.",
        ],
    }
    args.models.mkdir(parents=True, exist_ok=True)
    (args.models / "cric_b0_grouped_5fold_summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    public_summary = {
        "schema_version": "1.0",
        "dataset": report["dataset"],
        "doi": report["doi"],
        "endpoint": report["endpoint"],
        "protocol": report["protocol"],
        "cells": int(len(labels_array)),
        "parent_images": int(len(np.unique(groups_array))),
        "fold_accuracy": [fold["accuracy"] for fold in fold_metrics],
        "accuracy_mean": mean_sd["accuracy"]["mean"],
        "accuracy_sd": mean_sd["accuracy"]["sd"],
        "pooled_accuracy": pooled["accuracy"],
        "pooled_macro_f1": pooled["macro_f1"],
        "pooled_per_class_recall": pooled["per_class_recall"],
        "group_bootstrap": bootstrap,
        "selective_threshold": selective_60["threshold"],
        "selective_accuracy": selective_60["selective_accuracy"],
        "selective_coverage": selective_60["coverage"],
        "accepted": selective_60["accepted"],
        "abstained": selective_60["abstained"],
        "claim_boundary": report["claim_assessment"]["required_wording"],
        "limitations": report["limitations"],
    }
    args.public_output.parent.mkdir(parents=True, exist_ok=True)
    args.public_output.write_text(json.dumps(public_summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "pooled_accuracy": pooled["accuracy"],
        "accuracy_mean_sd": mean_sd["accuracy"],
        "macro_f1": pooled["macro_f1"],
        "per_class_recall": pooled["per_class_recall"],
        "accuracy_95_ci": bootstrap["accuracy_95_ci"],
        "selective_accuracy_95_ci": bootstrap["selective_accuracy_95_ci"],
        "selective_coverage_95_ci": bootstrap["selective_coverage_95_ci"],
        "selective_at_0_60": selective_60,
        "claim_assessment": report["claim_assessment"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

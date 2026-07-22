#!/usr/bin/env python3
"""Evaluate the locked CRIC fold ensemble on untouched APCData LBC images."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.cric_grade_data import CricCellDataset
from ml.grade_research_v3 import GradeResearchNet
from ml.scripts.aggregate_cric_grade_cv import group_bootstrap
from ml.scripts.train_cric_grade_cv import metrics_from_predictions


@torch.no_grad()
def predict(model, loader: DataLoader, device: torch.device, tta: bool = False) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    model.eval()
    grade, triage, high_risk, labels = [], [], [], []
    for batch in loader:
        image = batch["image"].to(device, non_blocking=True)
        variants = [image]
        if tta:
            variants.extend([torch.flip(image, (-1,)), torch.flip(image, (-2,))])
        outputs = [model(variant) for variant in variants]
        grade.append(torch.stack([torch.softmax(output["grade_logits"], 1) for output in outputs]).mean(0).cpu().numpy())
        triage.append(torch.stack([torch.sigmoid(output["triage_logit"]) for output in outputs]).mean(0).cpu().numpy())
        high_risk.append(torch.stack([torch.sigmoid(output["high_risk_logit"]) for output in outputs]).mean(0).cpu().numpy())
        labels.append(batch["label"].numpy())
    return np.concatenate(labels), np.concatenate(grade), np.concatenate(triage), np.concatenate(high_risk)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/processed/apcdata_external/external.csv")
    parser.add_argument("--models", type=Path, default=ROOT / "models/cric_grade_cv")
    parser.add_argument("--output", type=Path, default=ROOT / "models/cric_grade_cv/apcdata_external_summary.json")
    parser.add_argument("--public-output", type=Path, default=ROOT / "web-react/public/evidence/apcdata_external_summary.json")
    parser.add_argument("--batch", type=int, default=64)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--tta", action="store_true")
    args = parser.parse_args()

    dataset = CricCellDataset(
        args.manifest, image_size=224, crop_size=320, train=False,
        context_crop_size=960, include_context=False,
    )
    loader = DataLoader(dataset, batch_size=args.batch, shuffle=False, num_workers=args.workers,
                        pin_memory=torch.cuda.is_available())
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    member_probabilities, member_triage, member_high_risk = [], [], []
    labels = None
    for fold in range(1, 6):
        artifact = torch.load(args.models / f"cric_b0_grouped_fold_{fold}.pt", map_location="cpu", weights_only=False)
        model = GradeResearchNet("efficientnet_b0", pretrained=False, dropout=0.25).to(device)
        model.load_state_dict(artifact["state_dict"])
        current_labels, probabilities, triage, high_risk = predict(model, loader, device, tta=args.tta)
        if labels is not None and not np.array_equal(labels, current_labels):
            raise RuntimeError("external labels changed between ensemble members")
        labels = current_labels
        member_probabilities.append(probabilities)
        member_triage.append(triage)
        member_high_risk.append(high_risk)
    probabilities = np.mean(member_probabilities, axis=0)
    triage = np.mean(member_triage, axis=0)
    high_risk = np.mean(member_high_risk, axis=0)
    groups = np.asarray([row["group_id"] for row in dataset.rows])
    metrics = metrics_from_predictions(labels, probabilities, triage, high_risk)
    report = {
        "schema_version": "1.0",
        "evaluation_complete": True,
        "dataset": "APCData cervical cytology cells",
        "doi": "10.17632/ytd568rh3p.1",
        "modality": "liquid-based cytology by cytocentrifugation",
        "role": "untouched external domain evaluation; no fitting or validation selection",
        "model": "mean ensemble of five CRIC fold-specific EfficientNet-B0 checkpoints",
        "inference_views": 3 if args.tta else 1,
        "cells": len(dataset),
        "source_group_tokens": int(len(np.unique(groups))),
        "metrics": metrics,
        "group_bootstrap": group_bootstrap(labels, probabilities, groups, args.bootstrap),
        "limitations": [
            "APCData is liquid-based cytology by cytocentrifugation, not evidence from a Thai ThinPrep deployment.",
            "Public filenames yield 87 conservative source-group tokens while the dataset article reports 73 diagnosed studies; tokens are not claimed as patient identifiers.",
            "ASC-US and ASC-H cells are excluded because the CRIC endpoint has no corresponding output classes.",
            "No molecular HPV result is paired with these images.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    np.savez_compressed(args.output.with_suffix(".npz"), labels=labels, probabilities=probabilities,
                        triage_scores=triage, high_risk_scores=high_risk, groups=groups)
    public = {
        "schema_version": "1.0",
        "dataset": report["dataset"],
        "doi": report["doi"],
        "role": report["role"],
        "cells": report["cells"],
        "raw_accuracy": metrics["accuracy"],
        "balanced_accuracy": metrics["balanced_accuracy"],
        "macro_f1": metrics["macro_f1"],
        "per_class_recall": metrics["per_class_recall"],
        "confusion_matrix": metrics["confusion_matrix"],
        "claim_boundary": "External LBC transfer failure; not Thai ThinPrep validation and not an HPV molecular endpoint.",
    }
    args.public_output.parent.mkdir(parents=True, exist_ok=True)
    args.public_output.write_text(json.dumps(public, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"cells": len(dataset), "metrics": metrics, "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

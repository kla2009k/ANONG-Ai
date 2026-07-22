#!/usr/bin/env python3
"""Aggregate only fold-safe CRIC v4 members and enforce promotion gates."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.grade_v4_evaluation import average_member_predictions, promotion_gate
from ml.scripts.aggregate_cric_grade_cv import group_bootstrap
from ml.scripts.train_cric_grade_cv import metrics_from_predictions


def _load_member(path: Path) -> dict[str, np.ndarray]:
    arrays = np.load(path)
    return {key: arrays[key] for key in arrays.files}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data/processed/cric_grade_grouped")
    parser.add_argument("--models", type=Path, default=ROOT / "models/cric_grade_v4")
    parser.add_argument("--architecture", default="efficientnet_b0")
    parser.add_argument("--members", type=int, nargs="+", default=[1, 2])
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--external-lbc-summary", type=Path)
    args = parser.parse_args()

    pooled_labels, pooled_probabilities, pooled_triage, pooled_high_risk, pooled_groups = [], [], [], [], []
    fold_results = []
    parent_disjoint = True
    for fold in range(1, 6):
        members = []
        for member in args.members:
            stem = f"cric_v4_{args.architecture}_fold_{fold}_member_{member}"
            members.append(_load_member(args.models / f"{stem}_oof.npz"))
        ensemble = average_member_predictions(members)
        with (args.data / f"fold_{fold}/test.csv").open(encoding="utf-8", newline="") as handle:
            test_rows = list(csv.DictReader(handle))
        with (args.data / f"fold_{fold}/train.csv").open(encoding="utf-8", newline="") as handle:
            train_groups = {row["group_id"] for row in csv.DictReader(handle)}
        locked_groups = np.asarray([row["group_id"] for row in test_rows])
        parent_disjoint &= np.array_equal(ensemble["groups"], locked_groups)
        parent_disjoint &= not bool(set(locked_groups) & train_groups)
        metrics = metrics_from_predictions(
            ensemble["labels"], ensemble["probabilities"],
            ensemble["triage_scores"], ensemble["high_risk_scores"],
        )
        fold_results.append({"fold": fold, **metrics})
        pooled_labels.append(ensemble["labels"])
        pooled_probabilities.append(ensemble["probabilities"])
        pooled_triage.append(ensemble["triage_scores"])
        pooled_high_risk.append(ensemble["high_risk_scores"])
        pooled_groups.append(ensemble["groups"])

    labels = np.concatenate(pooled_labels)
    probabilities = np.concatenate(pooled_probabilities)
    triage = np.concatenate(pooled_triage)
    high_risk = np.concatenate(pooled_high_risk)
    groups = np.concatenate(pooled_groups)
    pooled = metrics_from_predictions(labels, probabilities, triage, high_risk)
    external_complete = False
    external_recall = None
    external_summary = None
    if args.external_lbc_summary and args.external_lbc_summary.exists():
        external_summary = json.loads(args.external_lbc_summary.read_text(encoding="utf-8"))
        external_complete = bool(external_summary.get("evaluation_complete"))
        external_recall = external_summary.get("per_class_recall")
        if external_recall is None:
            external_recall = external_summary.get("metrics", {}).get("per_class_recall")
    gate = promotion_gate(
        pooled["per_class_recall"], parent_disjoint, external_complete,
        external_per_class_recall=external_recall,
    )
    report = {
        "schema_version": "1.0",
        "status": "promotion_eligible" if gate["passed"] else "research_candidate_only",
        "model": f"multi-scale {args.architecture} fold-safe ensemble",
        "members_per_fold": args.members,
        "protocol": "five-fold parent-image-disjoint OOF; each ensemble member excludes the same held-out parent images",
        "folds": fold_results,
        "pooled_oof": pooled,
        "group_bootstrap": group_bootstrap(labels, probabilities, groups, args.bootstrap),
        "parent_disjoint_verified": parent_disjoint,
        "external_lbc": external_summary,
        "promotion_gate": gate,
    }
    args.models.mkdir(parents=True, exist_ok=True)
    output = args.models / f"cric_v4_{args.architecture}_ensemble_summary.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"], "accuracy": pooled["accuracy"],
        "per_class_recall": pooled["per_class_recall"], "promotion_gate": gate,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

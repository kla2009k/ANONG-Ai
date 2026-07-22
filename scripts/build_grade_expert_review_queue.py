#!/usr/bin/env python3
"""Build an auditable, explicitly unreviewed CRIC boundary-case queue."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CLASSES = ("NILM", "LSIL", "HSIL", "SCC")


def _portable_path(value: str) -> str:
    path = Path(value)
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return value


def _reason(true_index: int, predicted_index: int, margin: float) -> str:
    pair = {true_index, predicted_index}
    if pair <= {1, 2}:
        boundary = "LSIL-HSIL boundary"
    elif pair <= {2, 3}:
        boundary = "HSIL-SCC boundary"
    elif pair <= {0, 1}:
        boundary = "NILM-LSIL boundary"
    else:
        boundary = "cross-grade disagreement"
    state = "OOF error" if true_index != predicted_index else "low-margin OOF case"
    return f"{boundary}; {state}; margin={margin:.4f}"


def build_review_rows(manifest: list[dict[str, str]], labels: np.ndarray,
                      probabilities: np.ndarray, fold: int) -> list[dict[str, str]]:
    if len(manifest) != len(labels) or probabilities.shape != (len(labels), 4):
        raise ValueError("manifest, labels, and probabilities must align")
    rows = []
    for source, true_index, probability in zip(manifest, labels, probabilities):
        predicted_index = int(np.argmax(probability))
        ordered = np.sort(probability)
        margin = float(ordered[-1] - ordered[-2])
        error = predicted_index != int(true_index)
        if not error and margin >= 0.20:
            continue
        entropy = float(-(probability * np.log(np.clip(probability, 1e-12, 1))).sum())
        rows.append({
            "fold": str(fold),
            "group_id": source["group_id"],
            "cell_id": source["cell_id"],
            "image_path": _portable_path(source["path"]),
            "original_label": CLASSES[int(true_index)],
            "oof_prediction": CLASSES[predicted_index],
            "oof_confidence": f"{float(probability[predicted_index]):.6f}",
            "oof_margin": f"{margin:.6f}",
            "oof_entropy": f"{entropy:.6f}",
            "review_reason": _reason(int(true_index), predicted_index, margin),
            "review_status": "pending",
            "reviewer": "",
            "reviewed_label": "",
            "review_notes": "",
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data/processed/cric_grade_grouped")
    parser.add_argument("--models", type=Path, default=ROOT / "models/cric_grade_cv")
    parser.add_argument("--output", type=Path, default=ROOT / "review/grade_boundary_review_2026/queue.csv")
    parser.add_argument("--max-cases", type=int, default=120)
    args = parser.parse_args()

    candidates: list[dict[str, str]] = []
    for fold in range(1, 6):
        manifest_path = args.data / f"fold_{fold}/test.csv"
        with manifest_path.open(encoding="utf-8", newline="") as handle:
            manifest = list(csv.DictReader(handle))
        arrays = np.load(args.models / f"cric_b0_grouped_fold_{fold}_oof.npz")
        candidates.extend(build_review_rows(manifest, arrays["labels"], arrays["probabilities"], fold))

    candidates.sort(key=lambda row: (
        row["original_label"] == row["oof_prediction"],
        -float(row["oof_entropy"]),
    ))
    selected, seen_groups = [], set()
    for row in candidates:
        if row["group_id"] in seen_groups:
            continue
        selected.append(row)
        seen_groups.add(row["group_id"])
        if len(selected) >= args.max_cases:
            break
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(selected[0]) if selected else [])
        if selected:
            writer.writeheader()
            writer.writerows(selected)
    metadata = {
        "status": "pending_expert_review",
        "source": "locked CRIC parent-disjoint OOF predictions",
        "cases": len(selected),
        "unique_parent_images": len(seen_groups),
        "prohibition": "Do not describe these labels as expert-adjudicated until review_status and reviewer are completed.",
    }
    args.output.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

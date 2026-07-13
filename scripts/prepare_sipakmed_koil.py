#!/usr/bin/env python3
"""Create locked, group-disjoint SIPaKMeD train/validation/test manifests."""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.koil_data import index_sipakmed, group_stratified_split, split_summary


FIELDS = ["path", "source", "sipak_class", "sipak_label", "koil_label", "group_id", "split"]


def write_csv(path: pathlib.Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--classes-root",
        type=pathlib.Path,
        default=ROOT / "data" / "raw" / "sipakmed_official" / "classes",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=ROOT / "data" / "processed" / "sipakmed_koil_grouped",
    )
    parser.add_argument("--seed", type=int, default=20260713)
    args = parser.parse_args()

    rows = index_sipakmed(args.classes_root)
    splits = group_stratified_split(rows, seed=args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    for split, split_rows in splits.items():
        write_csv(args.output / f"{split}.csv", split_rows)
    write_csv(args.output / "index.csv", [row for name in ("train", "val", "test") for row in splits[name]])
    summary = {
        "dataset": "SIPaKMeD",
        "endpoint": "five morphology classes plus koilocytosis one-vs-rest",
        "split_unit": "original cluster image",
        "seed": args.seed,
        "test_set_policy": "locked after manifest creation; no threshold or model selection on test",
        "summary": split_summary(splits),
    }
    (args.output / "split_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

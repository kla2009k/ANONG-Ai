#!/usr/bin/env python3
"""Prepare APCData as an external LBC manifest without training leakage."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/apcdata_official"
LABEL_MAP = {"Negative": "NILM", "LSIL": "LSIL", "HSIL": "HSIL", "SCC": "SCC"}
FIELDS = ("path", "crop_path", "context_path", "source", "group_id", "cell_id", "bethesda", "label5", "nucleus_x", "nucleus_y")
CLASSES = ("NILM", "LSIL", "HSIL", "SCC")


def derive_study_id(filename: str) -> str:
    stem = Path(filename).stem
    field_match = re.match(r"^(\d{4})\b", stem)
    field_id = field_match.group(1) if field_match else hashlib.sha256(stem.encode()).hexdigest()[:8]
    if "IMAGE_" in stem.upper():
        return f"UNKNOWN_FIELD_{field_id}"
    body = re.sub(r"^\d{4}\s+", "", stem)
    coded = re.search(r"\b([CKT])\s*(\d{2,6})\b", body, flags=re.IGNORECASE)
    if coded:
        return f"{coded.group(1).upper()}{coded.group(2)}"
    numeric = re.search(r"\b(\d{3,5})\b", body)
    if numeric:
        return numeric.group(1)
    return f"UNKNOWN_FIELD_{field_id}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/apcdata_external")
    args = parser.parse_args()

    points = next(args.raw.rglob("APCData_points"), None)
    if points is None:
        raise RuntimeError("APCData_points was not found; download and extract the official archive first")
    image_by_prefix = {path.name[:4]: path for path in (points / "images").glob("*.jpg")}
    rows = []
    excluded = Counter()
    for annotation in sorted((points / "labels/csv").glob("*.csv")):
        image = image_by_prefix.get(annotation.stem)
        if image is None:
            raise RuntimeError(f"missing field image for {annotation.name}")
        group_id = f"apc-study-{derive_study_id(image.name)}"
        with annotation.open(encoding="utf-8-sig", newline="") as handle:
            for source in csv.DictReader(handle):
                grade = LABEL_MAP.get(source["bethesda_system"])
                if grade is None:
                    excluded[source["bethesda_system"]] += 1
                    continue
                rows.append({
                    "path": str(image.resolve()), "crop_path": "", "context_path": "", "source": "apcdata_external",
                    "group_id": group_id, "cell_id": source["cell_id"], "bethesda": grade,
                    "label5": str(CLASSES.index(grade)), "nucleus_x": source["nucleus_x"],
                    "nucleus_y": source["nucleus_y"],
                })
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = args.output / "external.csv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    archive = args.raw / "apcdata.zip"
    metadata = {
        "dataset": "APCData cervical cytology cells",
        "doi": "10.17632/ytd568rh3p.1",
        "license": "CC BY 4.0",
        "modality": "liquid-based cytology by cytocentrifugation",
        "role": "locked external domain evaluation; never used for fitting or validation selection",
        "field_images_available": len(image_by_prefix),
        "supported_cells": len(rows),
        "supported_class_counts": dict(Counter(row["bethesda"] for row in rows)),
        "excluded_cell_counts": dict(excluded),
        "derived_study_groups": len({row["group_id"] for row in rows}),
        "unknown_study_fields": len({row["group_id"] for row in rows if "UNKNOWN_FIELD" in row["group_id"]}),
        "grouping_warning": "Study IDs are parsed from filenames. UNKNOWN_FIELD entries remain separate fields; no patient identity is inferred.",
        "archive_sha256": sha256(archive) if archive.exists() else None,
        "evaluation_complete": False,
    }
    (args.output / "summary.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

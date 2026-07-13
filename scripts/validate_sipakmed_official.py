#!/usr/bin/env python3
"""Validate the downloaded official SIPaKMeD cropped-cell dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from collections import Counter, defaultdict

from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.koil_data import SIPAK_CLASSES, cluster_id_from_filename


EXPECTED = {
    "Superficial-Intermediate": {"cells": 831, "clusters": 126},
    "Parabasal": {"cells": 787, "clusters": 108},
    "Koilocytotic": {"cells": 825, "clusters": 238},
    "Dyskeratotic": {"cells": 813, "clusters": 223},
    "Metaplastic": {"cells": 793, "clusters": 271},
}


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--classes-root",
        type=pathlib.Path,
        default=ROOT / "data" / "raw" / "sipakmed_official" / "classes",
    )
    parser.add_argument(
        "--manifest",
        type=pathlib.Path,
        default=ROOT / "data" / "raw" / "sipakmed_official" / "provenance_manifest.json",
    )
    args = parser.parse_args()

    provenance = json.loads(args.manifest.read_text(encoding="utf-8"))
    recorded = {
        (record["class"], file["name"]): file
        for record in provenance["classes"]
        for file in record["files"]
        if file["name"].lower().endswith(".bmp")
    }
    hashes: dict[str, list[str]] = defaultdict(list)
    class_results = {}
    errors = []

    for class_name in SIPAK_CLASSES:
        files = sorted((args.classes_root / class_name / "CROPPED").glob("*.bmp"))
        clusters = {cluster_id_from_filename(path) for path in files}
        dimensions = Counter()
        for path in files:
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    dimensions[f"{image.width}x{image.height}"] += 1
            except Exception as error:
                errors.append(f"unreadable image {path}: {error}")
                continue
            digest = sha256(path)
            hashes[digest].append(f"{class_name}/{path.name}")
            entry = recorded.get((class_name, path.name))
            if entry is None:
                errors.append(f"missing provenance entry: {class_name}/{path.name}")
            elif digest != entry["sha256"] or path.stat().st_size != entry["bytes"]:
                errors.append(f"provenance mismatch: {class_name}/{path.name}")

        expected = EXPECTED[class_name]
        if len(files) != expected["cells"]:
            errors.append(f"{class_name}: expected {expected['cells']} cells, found {len(files)}")
        if len(clusters) != expected["clusters"]:
            errors.append(f"{class_name}: expected {expected['clusters']} clusters, found {len(clusters)}")
        class_results[class_name] = {
            "cells": len(files),
            "clusters": len(clusters),
            "distinct_dimensions": len(dimensions),
            "most_common_dimensions": dimensions.most_common(5),
        }

    duplicates = [paths for paths in hashes.values() if len(paths) > 1]
    cross_class_duplicates = [
        paths for paths in duplicates if len({path.split("/", 1)[0] for path in paths}) > 1
    ]
    if cross_class_duplicates:
        errors.append(f"found {len(cross_class_duplicates)} duplicate images across classes")

    result = {
        "dataset": "SIPaKMeD official CROPPED cells",
        "status": "PASS" if not errors else "FAIL",
        "classes": class_results,
        "total_cells": sum(item["cells"] for item in class_results.values()),
        "total_clusters": sum(item["clusters"] for item in class_results.values()),
        "exact_duplicate_sets": len(duplicates),
        "cross_class_duplicate_sets": len(cross_class_duplicates),
        "errors": errors,
    }
    output = args.classes_root.parent / "validation_report.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

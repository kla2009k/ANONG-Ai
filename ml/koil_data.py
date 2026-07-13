"""Leakage-safe SIPaKMeD indexing and group splitting utilities."""

from __future__ import annotations

import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


SIPAK_CLASSES = (
    "Superficial-Intermediate",
    "Parabasal",
    "Koilocytotic",
    "Dyskeratotic",
    "Metaplastic",
)
SIPAK_CLASS_TO_INDEX = {name: index for index, name in enumerate(SIPAK_CLASSES)}
IMAGE_SUFFIXES = {".bmp", ".jpg", ".jpeg", ".png", ".tif", ".tiff"}


def cluster_id_from_filename(path: Path) -> str:
    """Return the source cluster identifier from names such as ``084_03.bmp``."""
    match = re.match(r"^(\d+)[_-](\d+)", path.stem)
    if not match:
        raise ValueError(f"cannot derive SIPaKMeD cluster ID from {path.name!r}")
    return match.group(1)


def index_sipakmed(classes_root: Path) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for class_name in SIPAK_CLASSES:
        class_root = classes_root / class_name
        if not class_root.exists():
            raise FileNotFoundError(f"missing SIPaKMeD class directory: {class_root}")
        cropped = [
            path for path in class_root.rglob("*")
            if path.is_file()
            and path.suffix.lower() in IMAGE_SUFFIXES
            and "cropped" in {part.lower() for part in path.parts}
        ]
        if not cropped:
            raise ValueError(f"no CROPPED cell images found for {class_name}")
        for path in sorted(cropped):
            cluster = cluster_id_from_filename(path)
            rows.append({
                "path": str(path.resolve()),
                "source": "sipakmed",
                "sipak_class": class_name,
                "sipak_label": SIPAK_CLASS_TO_INDEX[class_name],
                "koil_label": int(class_name == "Koilocytotic"),
                "group_id": f"sipakmed:{class_name}:{cluster}",
            })
    return rows


def group_stratified_split(
    rows: Iterable[dict[str, str | int]],
    *,
    val_fraction: float = 0.15,
    test_fraction: float = 0.15,
    seed: int = 20260713,
) -> dict[str, list[dict[str, str | int]]]:
    """Split source clusters within each class; no cluster may cross a split."""
    if not 0 <= val_fraction < 1 or not 0 <= test_fraction < 1:
        raise ValueError("split fractions must be in [0, 1)")
    if val_fraction + test_fraction >= 1:
        raise ValueError("validation and test fractions must sum to less than 1")

    groups: dict[tuple[str, str], list[dict[str, str | int]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["sipak_class"]), str(row["group_id"]))].append(row)

    class_groups: dict[str, list[tuple[str, list[dict[str, str | int]]]]] = defaultdict(list)
    for (class_name, group_id), members in groups.items():
        class_groups[class_name].append((group_id, members))

    rng = random.Random(seed)
    result = {"train": [], "val": [], "test": []}
    for class_name in SIPAK_CLASSES:
        items = sorted(class_groups[class_name], key=lambda item: item[0])
        rng.shuffle(items)
        count = len(items)
        n_test = max(1, round(count * test_fraction)) if test_fraction else 0
        n_val = max(1, round(count * val_fraction)) if val_fraction else 0
        if count - n_test - n_val < 1:
            raise ValueError(f"not enough groups to split class {class_name}: {count}")
        assignments = (
            [("test", item) for item in items[:n_test]]
            + [("val", item) for item in items[n_test:n_test + n_val]]
            + [("train", item) for item in items[n_test + n_val:]]
        )
        for split, (_, members) in assignments:
            result[split].extend({**row, "split": split} for row in members)

    for split in result:
        result[split].sort(key=lambda row: str(row["path"]))
    assert_group_disjoint(result)
    return result


def assert_group_disjoint(splits: dict[str, list[dict[str, str | int]]]) -> None:
    group_sets = {
        split: {str(row["group_id"]) for row in rows}
        for split, rows in splits.items()
    }
    names = list(group_sets)
    for index, left in enumerate(names):
        for right in names[index + 1:]:
            overlap = group_sets[left] & group_sets[right]
            if overlap:
                raise ValueError(f"group leakage between {left} and {right}: {sorted(overlap)[:5]}")


def split_summary(splits: dict[str, list[dict[str, str | int]]]) -> dict:
    summary = {}
    for split, rows in splits.items():
        summary[split] = {
            "cells": len(rows),
            "clusters": len({str(row["group_id"]) for row in rows}),
            "cells_per_class": dict(Counter(str(row["sipak_class"]) for row in rows)),
            "clusters_per_class": dict(Counter(
                str(row["sipak_class"])
                for row in {str(r["group_id"]): r for r in rows}.values()
            )),
            "koil_cells": sum(int(row["koil_label"]) for row in rows),
        }
    return summary

"""CRIC four-grade data preparation with parent-image-disjoint splits."""

from __future__ import annotations

import csv
import random
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageOps
from sklearn.model_selection import StratifiedGroupKFold
from torch.utils.data import Dataset
from torchvision.transforms import InterpolationMode
from torchvision.transforms import functional as TF

from ml.grade_research_v3 import GRADE_CLASSES, IMAGENET_MEAN, IMAGENET_STD, random_stain_shift


CRIC_LABEL_MAP = {
    "Negative for intraepithelial lesion": "NILM",
    "LSIL": "LSIL",
    "HSIL": "HSIL",
    "SCC": "SCC",
}

MANIFEST_FIELDS = (
    "path", "crop_path", "context_path", "source", "group_id", "cell_id", "bethesda", "label5", "nucleus_x", "nucleus_y",
)


def supported_rows(annotation_path: Path, image_dir: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with Path(annotation_path).open(encoding="utf-8", newline="") as handle:
        for source in csv.DictReader(handle):
            grade = CRIC_LABEL_MAP.get(source["bethesda_system"])
            if grade is None:
                continue
            rows.append({
                "path": str((Path(image_dir) / source["image_filename"]).resolve()),
                "crop_path": "",
                "context_path": "",
                "source": "cric",
                "group_id": f"cric-image-{source['image_id']}",
                "cell_id": source["cell_id"],
                "bethesda": grade,
                "label5": str(GRADE_CLASSES.index(grade)),
                "nucleus_x": source["nucleus_x"],
                "nucleus_y": source["nucleus_y"],
            })
    return rows


def grouped_folds(rows: list[dict[str, str]], folds: int = 5, seed: int = 20260725) -> list[dict[str, list[dict[str, str]]]]:
    if folds < 3:
        raise ValueError("at least three folds are required for train/validation/test rotation")
    labels = np.asarray([int(row["label5"]) for row in rows])
    groups = np.asarray([row["group_id"] for row in rows])
    splitter = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=seed)
    test_indices = [test for _, test in splitter.split(np.zeros(len(rows)), labels, groups)]
    output = []
    all_indices = np.arange(len(rows))
    for fold in range(folds):
        test = test_indices[fold]
        validation = test_indices[(fold + 1) % folds]
        held_out = np.concatenate([test, validation])
        train = np.setdiff1d(all_indices, held_out, assume_unique=False)
        split = {
            "train": [rows[index] for index in train],
            "val": [rows[index] for index in validation],
            "test": [rows[index] for index in test],
        }
        assert_disjoint_groups(split)
        output.append(split)
    return output


def assert_disjoint_groups(split: dict[str, list[dict[str, str]]]) -> None:
    groups = {name: {row["group_id"] for row in rows} for name, rows in split.items()}
    for left, right in (("train", "val"), ("train", "test"), ("val", "test")):
        overlap = groups[left] & groups[right]
        if overlap:
            raise ValueError(f"group leakage between {left} and {right}: {sorted(overlap)[:3]}")


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def crop_around_nucleus(image: Image.Image, x: int, y: int, crop_size: int) -> Image.Image:
    half = crop_size // 2
    left, top = x - half, y - half
    right, bottom = left + crop_size, top + crop_size
    padding = (max(0, -left), max(0, -top), max(0, right - image.width), max(0, bottom - image.height))
    if any(padding):
        image = ImageOps.expand(image, border=padding, fill=(248, 241, 244))
        left, right = left + padding[0], right + padding[0]
        top, bottom = top + padding[1], bottom + padding[1]
    return image.crop((left, top, right, bottom))


def parent_balanced_sample_weights(
    rows: list[dict[str, str]], class_power: float = 0.5
) -> np.ndarray:
    """Balance rare classes while limiting cell-rich parent-image dominance."""
    if not rows:
        raise ValueError("rows must not be empty")
    if class_power < 0:
        raise ValueError("class_power must be non-negative")
    class_counts = Counter(int(row["label5"]) for row in rows)
    parent_counts = Counter(row["group_id"] for row in rows)
    weights = np.asarray([
        (len(rows) / class_counts[int(row["label5"])]) ** class_power
        / parent_counts[row["group_id"]]
        for row in rows
    ], dtype=np.float64)
    return weights / weights.mean()


def relative_crop_box(width: int, height: int, params: dict[str, float]) -> tuple[int, int, int, int]:
    """Convert shared relative crop parameters into an image-specific box."""
    crop_width = min(width, max(1, round(width * np.sqrt(params["scale"] * params["ratio"]))))
    crop_height = min(height, max(1, round(height * np.sqrt(params["scale"] / params["ratio"]))))
    top = round((height - crop_height) * params["top"])
    left = round((width - crop_width) * params["left"])
    return top, left, crop_height, crop_width


class CricCellDataset(Dataset):
    def __init__(self, csv_path: Path, image_size: int = 224, crop_size: int = 320,
                 train: bool = False, context_crop_size: int | None = None,
                 include_context: bool = True):
        with Path(csv_path).open(encoding="utf-8", newline="") as handle:
            self.rows = list(csv.DictReader(handle))
        self.image_size = image_size
        self.crop_size = crop_size
        self.context_crop_size = context_crop_size or crop_size * 3
        self.include_context = include_context
        self.train = train

    def __len__(self) -> int:
        return len(self.rows)

    def _transform(self, image: Image.Image, geometry: dict[str, float | bool] | None = None) -> torch.Tensor:
        if self.train:
            if geometry is None:
                raise ValueError("training geometry is required")
            top, left, height, width = relative_crop_box(image.width, image.height, geometry)
            image = TF.resized_crop(image, top, left, height, width, (self.image_size, self.image_size), InterpolationMode.BILINEAR)
            if geometry["hflip"]:
                image = TF.hflip(image)
            if geometry["vflip"]:
                image = TF.vflip(image)
            image = TF.rotate(image, float(geometry["angle"]), InterpolationMode.BILINEAR, fill=255)
            image = Image.fromarray(random_stain_shift(np.asarray(image), p=0.70))
        else:
            image = TF.resize(image, (self.image_size, self.image_size), InterpolationMode.BILINEAR)
        return TF.normalize(TF.to_tensor(image), IMAGENET_MEAN, IMAGENET_STD)

    def __getitem__(self, index: int) -> dict:
        row = self.rows[index]
        parent = None
        context = None
        context_path = row.get("context_path")
        if self.include_context and context_path and Path(context_path).exists():
            with Image.open(context_path) as opened:
                context = opened.convert("RGB")
        if self.include_context and context is None:
            with Image.open(row["path"]) as opened:
                parent = opened.convert("RGB")
            context = crop_around_nucleus(
                parent, int(row["nucleus_x"]), int(row["nucleus_y"]), self.context_crop_size
            )
        crop_path = row.get("crop_path")
        if crop_path and Path(crop_path).exists():
            with Image.open(crop_path) as opened:
                image = opened.convert("RGB")
        else:
            if parent is None:
                with Image.open(row["path"]) as opened:
                    parent = opened.convert("RGB")
            image = crop_around_nucleus(
                parent, int(row["nucleus_x"]), int(row["nucleus_y"]), self.crop_size
            )
        geometry = None
        if self.train:
            geometry = {
                "scale": random.uniform(0.78, 1.0),
                "ratio": random.uniform(0.90, 1.10),
                "top": random.random(),
                "left": random.random(),
                "hflip": random.random() < 0.5,
                "vflip": random.random() < 0.5,
                "angle": random.uniform(-20, 20),
            }
        image_tensor = self._transform(image, geometry)
        return {
            "image": image_tensor,
            "context_image": self._transform(context, geometry) if context is not None else image_tensor,
            "label": torch.tensor(int(row["label5"]), dtype=torch.long),
            "mask": torch.zeros((self.image_size, self.image_size), dtype=torch.long),
            "mask_available": torch.tensor(False, dtype=torch.bool),
            "index": torch.tensor(index, dtype=torch.long),
            "path": row["path"],
            "group_id": row["group_id"],
        }

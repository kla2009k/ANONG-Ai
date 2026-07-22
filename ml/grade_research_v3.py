"""Research-grade cervical cytology training components.

The grade endpoint is four-way (NILM/LSIL/HSIL/SCC). The fifth user-visible
output, KOIL, remains an independent morphology probability from the separately
trained SIPaKMeD model. This avoids forcing two labels that can coexist into one
softmax distribution.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import Dataset
from torchvision import models
from torchvision.transforms import InterpolationMode
from torchvision.transforms import functional as TF
from torchvision.transforms.transforms import RandomResizedCrop

from scripts.augmentations import random_stain_shift, simple_stain_normalize


GRADE_CLASSES = ("NILM", "LSIL", "HSIL", "SCC")
DISPLAY_OUTPUTS = (*GRADE_CLASSES, "KOIL")


def safety_selection_score(
    macro_f1: float,
    high_risk_recall: float,
    triage_recall: float,
    balanced_accuracy: float,
) -> float:
    """Rank validation checkpoints with recall weighted above exact grading."""
    return float(
        0.30 * macro_f1
        + 0.35 * high_risk_recall
        + 0.20 * triage_recall
        + 0.15 * balanced_accuracy
    )
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def combined_five_outputs(grade_probabilities: np.ndarray, koil_probability: float) -> list[dict]:
    """Return five display rows while preserving endpoint independence."""
    grade = np.asarray(grade_probabilities, dtype=np.float64)
    if grade.shape != (4,) or np.any(grade < 0) or not np.isfinite(grade).all():
        raise ValueError("grade_probabilities must contain four finite non-negative values")
    total = float(grade.sum())
    if total <= 0:
        raise ValueError("grade probabilities must have positive mass")
    if not 0 <= koil_probability <= 1:
        raise ValueError("koil_probability must be between zero and one")
    grade = grade / total
    rows = [
        {"key": name, "probability": float(value), "relationship": "mutually_exclusive_grade"}
        for name, value in zip(GRADE_CLASSES, grade)
    ]
    rows.append({
        "key": "KOIL",
        "probability": float(koil_probability),
        "relationship": "independent_morphology_endpoint",
    })
    return rows


def ordinal_targets(labels: torch.Tensor) -> torch.Tensor:
    """Encode four severity categories as three cumulative thresholds."""
    thresholds = torch.arange(3, device=labels.device).view(1, -1)
    return (labels.view(-1, 1) > thresholds).float()


def selective_metrics(labels: np.ndarray, probabilities: np.ndarray,
                      thresholds: Iterable[float] | None = None) -> list[dict]:
    """Accuracy conditional on confidence, always paired with retained coverage."""
    labels = np.asarray(labels, dtype=np.int64)
    probabilities = np.asarray(probabilities, dtype=np.float64)
    if probabilities.ndim != 2 or probabilities.shape[0] != labels.shape[0]:
        raise ValueError("labels and probabilities have incompatible shapes")
    thresholds = thresholds or np.linspace(0.40, 0.95, 12)
    confidence = probabilities.max(axis=1)
    predicted = probabilities.argmax(axis=1)
    rows = []
    for threshold in thresholds:
        accepted = confidence >= float(threshold)
        count = int(accepted.sum())
        rows.append({
            "threshold": float(threshold),
            "coverage": float(accepted.mean()),
            "accepted": count,
            "abstained": int(len(labels) - count),
            "selective_accuracy": float((predicted[accepted] == labels[accepted]).mean()) if count else None,
        })
    return rows


def update_hard_example_weights(base_weights: np.ndarray, losses: np.ndarray,
                                strength: float = 1.5, cap: float = 4.0) -> np.ndarray:
    """Increase sampling weight for repeatedly difficult training examples."""
    base = np.asarray(base_weights, dtype=np.float64)
    losses = np.asarray(losses, dtype=np.float64)
    if base.shape != losses.shape:
        raise ValueError("base_weights and losses must have the same shape")
    finite = np.nan_to_num(losses, nan=float(np.nanmedian(losses)), posinf=0.0, neginf=0.0)
    lo, hi = np.quantile(finite, [0.10, 0.90])
    normalized = np.clip((finite - lo) / max(hi - lo, 1e-8), 0.0, 1.0)
    weights = base * np.minimum(1.0 + strength * normalized, cap)
    return weights / max(weights.mean(), 1e-8)


def companion_mask_path(image_path: Path) -> Path:
    return image_path.with_name(f"{image_path.stem}-d.bmp")


class HerlevMaskDataset(Dataset):
    """Synchronized image/mask transforms with optional stain augmentation."""

    def __init__(self, csv_path: Path, image_size: int, train: bool,
                 stain_normalize: bool = False, stain_augment: bool = True):
        self.rows = list(csv.DictReader(Path(csv_path).open(encoding="utf-8")))
        self.image_size = image_size
        self.train = train
        self.stain_normalize = stain_normalize
        self.stain_augment = stain_augment

    def __len__(self):
        return len(self.rows)

    def _geometry(self, image: Image.Image, mask: Image.Image):
        if self.train:
            top, left, height, width = RandomResizedCrop.get_params(
                image, scale=(0.72, 1.0), ratio=(0.85, 1.18)
            )
            image = TF.resized_crop(image, top, left, height, width,
                                    (self.image_size, self.image_size), InterpolationMode.BILINEAR)
            mask = TF.resized_crop(mask, top, left, height, width,
                                   (self.image_size, self.image_size), InterpolationMode.NEAREST)
            if random.random() < 0.5:
                image, mask = TF.hflip(image), TF.hflip(mask)
            if random.random() < 0.35:
                image, mask = TF.vflip(image), TF.vflip(mask)
            angle = random.uniform(-18, 18)
            image = TF.rotate(image, angle, InterpolationMode.BILINEAR, fill=255)
            mask = TF.rotate(mask, angle, InterpolationMode.NEAREST, fill=0)
        else:
            image = TF.resize(image, (self.image_size, self.image_size), InterpolationMode.BILINEAR)
            mask = TF.resize(mask, (self.image_size, self.image_size), InterpolationMode.NEAREST)
        return image, mask

    def __getitem__(self, index):
        row = self.rows[index]
        image_path = Path(row["path"])
        image = Image.open(image_path).convert("RGB")
        mask_path = companion_mask_path(image_path)
        mask_available = mask_path.exists()
        mask = Image.open(mask_path).convert("L") if mask_available else Image.new("L", image.size, 0)
        image, mask = self._geometry(image, mask)

        rgb = np.asarray(image)
        if self.stain_normalize:
            rgb = simple_stain_normalize(rgb, mode="mean_std")
        if self.train and self.stain_augment:
            rgb = random_stain_shift(rgb, p=0.75)
            if random.random() < 0.3:
                rgb = cv2.GaussianBlur(rgb, (3, 3), 0)
        tensor = TF.normalize(TF.to_tensor(Image.fromarray(rgb)), IMAGENET_MEAN, IMAGENET_STD)
        mask_tensor = torch.from_numpy(np.asarray(mask, dtype=np.uint8).copy()).long().clamp(0, 4)
        return {
            "image": tensor,
            "label": torch.tensor(int(row["label5"]), dtype=torch.long),
            "mask": mask_tensor,
            "mask_available": torch.tensor(mask_available, dtype=torch.bool),
            "index": torch.tensor(index, dtype=torch.long),
            "path": str(image_path),
        }


class GradeResearchNet(nn.Module):
    """Four-grade model with hierarchical, ordinal and segmentation supervision."""

    def __init__(self, architecture: str = "efficientnet_b0", pretrained: bool = True,
                 dropout: float = 0.3, mask_classes: int = 5):
        super().__init__()
        self.architecture = architecture
        self.features, channels = self._backbone(architecture, pretrained)
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.dropout = nn.Dropout(dropout)
        self.grade_head = nn.Linear(channels, 4)
        self.triage_head = nn.Linear(channels, 1)
        self.high_risk_head = nn.Linear(channels, 1)
        self.ordinal_head = nn.Linear(channels, 3)
        self.segmentation_head = nn.Sequential(
            nn.Conv2d(channels, max(64, channels // 4), 1),
            nn.SiLU(),
            nn.Conv2d(max(64, channels // 4), mask_classes, 1),
        )

    @staticmethod
    def _backbone(architecture: str, pretrained: bool):
        if architecture.startswith("efficientnet_b"):
            constructor = getattr(models, architecture)
            weights_enum = getattr(models, f"EfficientNet_{architecture.split('_')[-1].upper()}_Weights")
            network = constructor(weights=weights_enum.IMAGENET1K_V1 if pretrained else None)
            return network.features, network.classifier[-1].in_features
        if architecture == "convnext_tiny":
            network = models.convnext_tiny(
                weights=models.ConvNeXt_Tiny_Weights.IMAGENET1K_V1 if pretrained else None
            )
            return network.features, network.classifier[-1].in_features
        raise ValueError(f"unsupported architecture: {architecture}")

    def forward(self, image):
        features = self.features(image)
        pooled = self.dropout(self.pool(features).flatten(1))
        return {
            "grade_logits": self.grade_head(pooled),
            "triage_logit": self.triage_head(pooled).squeeze(1),
            "high_risk_logit": self.high_risk_head(pooled).squeeze(1),
            "ordinal_logits": self.ordinal_head(pooled),
            "segmentation_logits": self.segmentation_head(features),
        }


def multitask_loss(outputs: dict, labels: torch.Tensor, masks: torch.Tensor,
                   mask_available: torch.Tensor, class_weights: torch.Tensor | None = None,
                   label_smoothing: float = 0.04, segmentation_weight: float = 0.15,
                   hierarchy_weight: float = 0.20, ordinal_weight: float = 0.15):
    per_sample = F.cross_entropy(
        outputs["grade_logits"], labels, weight=class_weights,
        label_smoothing=label_smoothing, reduction="none"
    )
    grade_loss = per_sample.mean()
    triage_target = (labels > 0).float()
    high_risk_target = (labels >= 2).float()
    hierarchy = (
        F.binary_cross_entropy_with_logits(outputs["triage_logit"], triage_target)
        + F.binary_cross_entropy_with_logits(outputs["high_risk_logit"], high_risk_target)
    ) / 2
    ordinal = F.binary_cross_entropy_with_logits(outputs["ordinal_logits"], ordinal_targets(labels))
    segmentation = torch.zeros((), device=labels.device)
    if mask_available.any():
        resized = F.interpolate(
            masks[mask_available].unsqueeze(1).float(),
            size=outputs["segmentation_logits"].shape[-2:], mode="nearest"
        ).squeeze(1).long()
        segmentation = F.cross_entropy(outputs["segmentation_logits"][mask_available], resized)
    total = grade_loss + hierarchy_weight * hierarchy + ordinal_weight * ordinal + segmentation_weight * segmentation
    return {
        "loss": total,
        "grade": grade_loss.detach(),
        "hierarchy": hierarchy.detach(),
        "ordinal": ordinal.detach(),
        "segmentation": segmentation.detach(),
        "per_sample_grade": per_sample.detach(),
    }

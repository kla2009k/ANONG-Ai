"""SIPaKMeD morphology model used for the independent koilocytosis endpoint."""

from __future__ import annotations

import torch.nn as nn
from torchvision import models

from ml.koil_data import SIPAK_CLASSES


def build_koil_model(pretrained: bool = True, dropout: float = 0.3) -> nn.Module:
    weights = models.EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
    model = models.efficientnet_b0(weights=weights)
    model.classifier[0] = nn.Dropout(dropout)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(SIPAK_CLASSES))
    return model

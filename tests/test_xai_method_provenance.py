import unittest
from unittest.mock import patch

import torch

from ml.scripts.xai_advanced import compute_cam


class TinyCamModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.features = torch.nn.Sequential(
            torch.nn.Conv2d(3, 4, 3, padding=1),
            torch.nn.ReLU(),
        )
        self.pool = torch.nn.AdaptiveAvgPool2d(1)
        self.classifier = torch.nn.Linear(4, 2)

    def forward(self, value):
        value = self.features(value)
        return self.classifier(self.pool(value).flatten(1))


class XaiMethodProvenanceTests(unittest.TestCase):
    def test_manual_fallback_is_allowed_for_gradcam(self):
        model = TinyCamModel().eval()
        image = torch.rand(1, 3, 16, 16)

        with patch("ml.scripts.xai_advanced._try_pytorch_grad_cam", return_value=None):
            cam = compute_cam(model, "custom", image, 0, "gradcam")

        self.assertEqual(cam.ndim, 2)
        self.assertTrue(torch.isfinite(torch.from_numpy(cam)).all())

    def test_other_methods_are_not_silently_relabelled_manual_gradcam(self):
        model = TinyCamModel().eval()
        image = torch.rand(1, 3, 16, 16)

        with patch("ml.scripts.xai_advanced._try_pytorch_grad_cam", return_value=None):
            with self.assertRaises(RuntimeError):
                compute_cam(model, "custom", image, 0, "scorecam")


if __name__ == "__main__":
    unittest.main()

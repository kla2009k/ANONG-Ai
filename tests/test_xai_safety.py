import unittest

import numpy as np

from server.predictor import (
    _activation_region_overlay,
    _cam_diagnostics,
    _select_primary_cam,
)


class CamDiagnosticsTests(unittest.TestCase):
    def test_zero_cam_is_rejected(self):
        diagnostics = _cam_diagnostics(np.zeros((32, 32), dtype=np.float32))

        self.assertFalse(diagnostics["valid"])
        self.assertEqual(diagnostics["reason"], "flat_activation")

    def test_non_finite_cam_is_rejected(self):
        cam = np.ones((16, 16), dtype=np.float32)
        cam[0, 0] = np.nan

        diagnostics = _cam_diagnostics(cam)

        self.assertFalse(diagnostics["valid"])
        self.assertEqual(diagnostics["reason"], "non_finite_values")

    def test_localized_cam_is_accepted(self):
        cam = np.zeros((32, 32), dtype=np.float32)
        cam[10:22, 12:24] = np.linspace(0.1, 1.0, 12, dtype=np.float32)[None, :]

        diagnostics = _cam_diagnostics(cam)

        self.assertTrue(diagnostics["valid"])
        self.assertGreater(diagnostics["std"], 0.01)


class CamSelectionTests(unittest.TestCase):
    def test_degenerate_gradcam_uses_valid_class_aware_fallback(self):
        fallback = np.zeros((32, 32), dtype=np.float32)
        fallback[8:24, 8:24] = np.linspace(0.05, 1.0, 16, dtype=np.float32)[None, :]

        method, cam, diagnostics = _select_primary_cam({
            "gradcam": np.zeros((32, 32), dtype=np.float32),
            "gradcam++": fallback,
            "layercam": np.flipud(fallback),
        })

        self.assertEqual(method, "gradcam++")
        self.assertIs(cam, fallback)
        self.assertFalse(diagnostics["gradcam"]["valid"])
        self.assertTrue(diagnostics["gradcam++"]["valid"])

    def test_all_degenerate_cams_abstain(self):
        method, cam, diagnostics = _select_primary_cam({
            "gradcam": np.zeros((16, 16), dtype=np.float32),
            "gradcam++": np.full((16, 16), np.nan, dtype=np.float32),
        })

        self.assertIsNone(method)
        self.assertIsNone(cam)
        self.assertFalse(diagnostics["gradcam"]["valid"])


class ActivationOverlayTests(unittest.TestCase):
    def test_zero_cam_does_not_return_original_as_an_explanation(self):
        image = np.full((64, 64, 3), 127, dtype=np.uint8)

        overlay, coverage, threshold = _activation_region_overlay(
            image, np.zeros((16, 16), dtype=np.float32)
        )

        self.assertIsNone(overlay)
        self.assertEqual(coverage, 0.0)
        self.assertIsNone(threshold)

    def test_valid_cam_returns_bounded_region(self):
        image = np.full((64, 64, 3), 127, dtype=np.uint8)
        cam = np.zeros((16, 16), dtype=np.float32)
        cam[4:12, 6:10] = np.linspace(0.1, 1.0, 8, dtype=np.float32)[:, None]

        overlay, coverage, threshold = _activation_region_overlay(image, cam)

        self.assertIsNotNone(overlay)
        self.assertEqual(overlay.shape, image.shape)
        self.assertGreater(coverage, 0.0)
        self.assertLess(coverage, 0.5)
        self.assertGreaterEqual(threshold, 0.55)


if __name__ == "__main__":
    unittest.main()

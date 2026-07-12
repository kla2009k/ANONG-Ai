import pathlib
import unittest

import cv2
import numpy as np

from server.predictor import _classifier_quality


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ClassifierQualityProfileTests(unittest.TestCase):
    def test_single_cell_crop_is_not_rejected_for_low_cellularity(self):
        image = np.full((224, 224, 3), 185, dtype=np.uint8)
        cv2.circle(image, (112, 112), 52, (95, 55, 120), -1)
        cv2.circle(image, (112, 112), 26, (55, 35, 90), -1)

        quality = _classifier_quality(image)

        self.assertNotEqual(quality["status"], "fail")
        self.assertNotIn("low_cellularity", quality["blocking_issues"])
        self.assertEqual(quality["profile"], "single_cell_crop_herlev_v1")

    def test_flat_image_is_a_hard_quality_failure(self):
        image = np.full((224, 224, 3), 128, dtype=np.uint8)

        quality = _classifier_quality(image)

        self.assertEqual(quality["status"], "fail")
        self.assertIn("severe_low_contrast", quality["blocking_issues"])

    def test_public_herlev_examples_are_warnings_or_passes_not_false_rejections(self):
        sample_dir = ROOT / "web-react" / "public" / "samples"
        paths = sorted(p for p in sample_dir.glob("s??_*.jpg") if "_cam" not in p.stem)
        self.assertEqual(len(paths), 8)

        results = [_classifier_quality(cv2.imread(str(path))) for path in paths]

        self.assertTrue(all(result["status"] in {"pass", "warning"} for result in results))
        self.assertTrue(all("low_cellularity" not in result["blocking_issues"] for result in results))


if __name__ == "__main__":
    unittest.main()

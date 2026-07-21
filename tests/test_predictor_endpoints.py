import unittest
from unittest.mock import patch

import numpy as np

from server import predictor
from server.predictor import CLASSES, _grade_probabilities


class PredictorEndpointTests(unittest.TestCase):
    def test_grade_output_excludes_legacy_koil_and_renormalizes(self):
        result = _grade_probabilities(
            ["NILM", "LSIL", "HSIL", "SCC", "KOIL"],
            np.asarray([0.1, 0.2, 0.3, 0.1, 0.3], dtype=np.float32),
        )
        self.assertEqual({item["key"] for item in result}, set(CLASSES))
        self.assertAlmostEqual(sum(item["prob"] for item in result), 1.0, places=3)
        self.assertEqual(result[0]["key"], "HSIL")
        self.assertEqual(result[0]["model_index"], 2)

    def test_grade_contract_rejects_missing_class(self):
        with self.assertRaises(ValueError):
            _grade_probabilities(
                ["NILM", "LSIL", "HSIL", "KOIL"],
                np.asarray([0.2, 0.3, 0.4, 0.1], dtype=np.float32),
            )

    def test_status_exposes_locked_and_external_koil_evidence(self):
        evidence = {
            "locked_test": {"test_koil": {"support_positive": 133, "sensitivity": 0.9624, "specificity": 0.9764, "auroc": 0.9912}},
            "external_challenge": {"dataset": "CCCID v2", "support_positive": 20, "sensitivity": 0.95},
        }
        with patch.dict(predictor._STATE, {"koil_evidence": evidence}):
            status = predictor.status()["koil_evidence"]
        self.assertEqual(status["locked_test_support"], 133)
        self.assertEqual(status["external_positive_support"], 20)
        self.assertEqual(status["external_dataset"], "CCCID v2")


if __name__ == "__main__":
    unittest.main()

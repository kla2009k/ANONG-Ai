import unittest

import numpy as np

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


if __name__ == "__main__":
    unittest.main()

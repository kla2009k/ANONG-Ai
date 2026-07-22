import unittest

import numpy as np

from ml.grade_v4_evaluation import average_member_predictions, promotion_gate


class GradeV4EvaluationTests(unittest.TestCase):
    def test_fold_ensemble_requires_identical_labels_and_groups(self):
        first = {
            "labels": np.asarray([0, 3]),
            "groups": np.asarray(["a", "b"]),
            "probabilities": np.asarray([[0.8, 0.1, 0.1, 0.0], [0.0, 0.0, 0.4, 0.6]]),
            "triage_scores": np.asarray([0.1, 0.9]),
            "high_risk_scores": np.asarray([0.1, 0.9]),
        }
        second = {**first, "probabilities": np.asarray([
            [0.6, 0.2, 0.1, 0.1], [0.0, 0.0, 0.2, 0.8]
        ])}
        result = average_member_predictions([first, second])
        np.testing.assert_allclose(result["probabilities"], (first["probabilities"] + second["probabilities"]) / 2)
        with self.assertRaises(ValueError):
            average_member_predictions([first, {**second, "groups": np.asarray(["a", "c"]) }])

    def test_promotion_gate_does_not_accept_headline_accuracy_alone(self):
        decision = promotion_gate(
            per_class_recall={"NILM": 0.96, "LSIL": 0.91, "HSIL": 0.93, "SCC": 0.70},
            parent_disjoint=True,
            external_lbc_complete=False,
        )
        self.assertFalse(decision["passed"])
        self.assertIn("SCC exact recall", " ".join(decision["failures"]))
        self.assertIn("external LBC", " ".join(decision["failures"]))

    def test_promotion_gate_rejects_completed_but_unsafe_external_evaluation(self):
        decision = promotion_gate(
            per_class_recall={grade: 0.95 for grade in ("NILM", "LSIL", "HSIL", "SCC")},
            parent_disjoint=True,
            external_lbc_complete=True,
            external_per_class_recall={"NILM": 1.0, "LSIL": 0.11, "HSIL": 0.02, "SCC": 0.0},
        )
        self.assertFalse(decision["passed"])
        self.assertIn("external SCC", " ".join(decision["failures"]))


if __name__ == "__main__":
    unittest.main()

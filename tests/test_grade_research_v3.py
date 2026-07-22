import unittest
from pathlib import Path

import numpy as np
import torch

from ml.grade_research_v3 import (
    GradeResearchNet,
    MultiScaleGradeResearchNet,
    combined_five_outputs,
    ordinal_targets,
    safety_selection_score,
    selective_metrics,
    update_hard_example_weights,
)


class GradeResearchV3Tests(unittest.TestCase):
    def test_research_module_has_no_untracked_script_dependency(self):
        source = (Path(__file__).resolve().parents[1] / "ml" / "grade_research_v3.py").read_text(encoding="utf-8")
        self.assertNotIn("from scripts.augmentations", source)

    def test_five_display_outputs_keep_koil_independent(self):
        outputs = combined_five_outputs(
            np.asarray([0.1, 0.2, 0.6, 0.1]), koil_probability=0.8
        )
        self.assertEqual([row["key"] for row in outputs], ["NILM", "LSIL", "HSIL", "SCC", "KOIL"])
        self.assertAlmostEqual(sum(row["probability"] for row in outputs[:4]), 1.0)
        self.assertEqual(outputs[-1]["probability"], 0.8)
        self.assertEqual(outputs[-1]["relationship"], "independent_morphology_endpoint")

    def test_ordinal_targets(self):
        labels = torch.tensor([0, 1, 2, 3])
        expected = torch.tensor([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 1.0],
        ])
        torch.testing.assert_close(ordinal_targets(labels), expected)

    def test_model_exposes_multitask_heads(self):
        model = GradeResearchNet("efficientnet_b0", pretrained=False, mask_classes=5)
        result = model(torch.randn(2, 3, 128, 128))
        self.assertEqual(result["grade_logits"].shape, (2, 4))
        self.assertEqual(result["triage_logit"].shape, (2,))
        self.assertEqual(result["high_risk_logit"].shape, (2,))
        self.assertEqual(result["ordinal_logits"].shape, (2, 3))
        self.assertEqual(result["segmentation_logits"].shape[:2], (2, 5))

    def test_multiscale_model_fuses_cell_and_context_without_changing_contract(self):
        model = MultiScaleGradeResearchNet("efficientnet_b0", pretrained=False, mask_classes=5)
        cell = torch.randn(2, 3, 96, 96)
        context = torch.randn(2, 3, 96, 96)
        result = model(cell, context)
        self.assertEqual(result["grade_logits"].shape, (2, 4))
        self.assertEqual(result["triage_logit"].shape, (2,))
        self.assertEqual(result["high_risk_logit"].shape, (2,))
        self.assertEqual(result["ordinal_logits"].shape, (2, 3))
        self.assertEqual(result["segmentation_logits"].shape[:2], (2, 5))
        self.assertEqual(result["cell_embedding"].shape, result["context_embedding"].shape)

    def test_hard_example_weights_increase_for_harder_samples(self):
        base = np.ones(4)
        result = update_hard_example_weights(base, np.asarray([0.1, 0.2, 0.5, 2.0]), strength=2.0)
        self.assertGreater(result[-1], result[0])
        self.assertAlmostEqual(float(result.mean()), 1.0, places=6)

    def test_selective_metrics_report_coverage(self):
        probabilities = np.asarray([
            [0.9, 0.05, 0.03, 0.02],
            [0.1, 0.6, 0.2, 0.1],
            [0.2, 0.2, 0.5, 0.1],
            [0.3, 0.3, 0.2, 0.2],
        ])
        result = selective_metrics(np.asarray([0, 1, 2, 3]), probabilities, thresholds=[0.5, 0.8])
        self.assertEqual(result[0]["coverage"], 0.75)
        self.assertEqual(result[1]["coverage"], 0.25)
        self.assertEqual(result[1]["selective_accuracy"], 1.0)

    def test_checkpoint_selection_prioritizes_safety_recall(self):
        accurate_but_less_safe = safety_selection_score(
            macro_f1=0.90, high_risk_recall=0.80, triage_recall=0.95, balanced_accuracy=0.90
        )
        slightly_less_accurate_but_safer = safety_selection_score(
            macro_f1=0.86, high_risk_recall=0.92, triage_recall=1.00, balanced_accuracy=0.86
        )
        self.assertGreater(slightly_less_accurate_but_safer, accurate_but_less_safe)


if __name__ == "__main__":
    unittest.main()

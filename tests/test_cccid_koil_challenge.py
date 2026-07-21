import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "models" / "koil_sipakmed" / "evaluation" / "cccid_koil_20_case_challenge.json"
PUBLIC_RESULTS = ROOT / "web-react" / "public" / "evidence" / "cccid_koil_20_case_challenge.json"


class CccidKoilChallengeTests(unittest.TestCase):
    def test_positive_only_external_challenge_is_reported_without_overclaiming(self):
        payload = json.loads(RESULTS.read_text(encoding="utf-8"))

        self.assertEqual(payload["evaluation_type"], "deterministic_external_positive_only_challenge")
        self.assertTrue(payload["selection_locked_before_inference"])
        self.assertEqual(payload["support_positive"], 20)
        self.assertEqual(payload["true_positive"] + payload["false_negative"], 20)
        self.assertEqual(payload["true_positive"], 19)
        self.assertEqual(payload["false_negative"], 1)
        self.assertAlmostEqual(payload["sensitivity"], 0.95)
        self.assertAlmostEqual(payload["sensitivity_wilson_95_ci"]["lower"], 0.763868806553258)
        self.assertAlmostEqual(payload["sensitivity_wilson_95_ci"]["upper"], 0.9911185511992047)
        self.assertIsNone(payload["specificity"])
        self.assertIsNone(payload["auroc"])
        self.assertFalse(payload["hpv_test"])
        self.assertIn("not estimable", payload["limitation"])
        self.assertEqual(len(payload["rows"]), 20)
        self.assertEqual(sum(row["positive"] for row in payload["rows"]), 19)
        self.assertEqual(RESULTS.read_bytes(), PUBLIC_RESULTS.read_bytes())


if __name__ == "__main__":
    unittest.main()

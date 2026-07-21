import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "web-react" / "public" / "evidence" / "dataset_registry.json"


class DatasetRegistryTests(unittest.TestCase):
    def test_registry_keeps_candidates_out_of_current_model_total(self):
        payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
        records = payload["records"]
        current = [r for r in records if r["status"] == "current_model_development"]
        candidates = [r for r in records if r["status"].startswith("candidate_")]

        self.assertEqual(sum(r["current_use_count"] for r in current), payload["current_model_development_images"])
        self.assertTrue(candidates)
        self.assertTrue(all(r["current_use_count"] == 0 for r in candidates))
        self.assertEqual(len(records), payload["catalogued_sources"])

    def test_registry_exposes_the_unresolved_paired_hpv_gap(self):
        payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
        current = [r for r in payload["records"] if r["current_use_count"] > 0]

        self.assertTrue(current)
        self.assertTrue(all(r["paired_hpv"] != "yes" for r in current))
        self.assertIn("must not be added", payload["warning"])


if __name__ == "__main__":
    unittest.main()

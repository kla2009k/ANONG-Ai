import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FrontendEvidenceContractTests(unittest.TestCase):
    def test_report_preview_uses_grade_classes_and_separates_koil(self):
        source = (ROOT / "web-react" / "src" / "pages" / "ReportPreview.tsx").read_text(encoding="utf-8")

        self.assertIn("GRADE_CLASS_KEYS.map", source)
        self.assertIn("Independent KOIL morphology endpoint", source)
        self.assertNotIn("{CLASS_KEYS.map", source)

    def test_public_demo_reports_match_their_manifest_hashes(self):
        report_root = ROOT / "web-react" / "public"
        manifest = json.loads((report_root / "reports" / "manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["generation_mode"], "real_local_dual_model_inference")
        self.assertFalse(manifest["contains_patient_identifiers"])
        self.assertGreaterEqual(len(manifest["reports"]), 5)
        self.assertTrue(any(report["review_status"] == "edited" for report in manifest["reports"]))
        for report in manifest["reports"]:
            path = report_root / report["file"]
            body = path.read_bytes()
            self.assertTrue(body.startswith(b"%PDF-"))
            self.assertEqual(hashlib.sha256(body).hexdigest(), report["sha256"])
            self.assertEqual(len(body), report["bytes"])

    def test_pages_workflow_generates_real_route_entry_points(self):
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")

        self.assertIn("mkdir -p \"web-dist/$route\"", workflow)
        for route in ("analyze", "koil", "hpv", "datasets", "gallery", "reports"):
            self.assertIn(route, workflow)


if __name__ == "__main__":
    unittest.main()

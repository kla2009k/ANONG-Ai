import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FrontendEvidenceContractTests(unittest.TestCase):
    def test_overview_hides_requested_readiness_rows(self):
        source = (ROOT / "web-react" / "src" / "pages" / "Landing.tsx").read_text(encoding="utf-8")
        self.assertNotIn('["Thai ThinPrep", "Missing"', source)
        self.assertNotIn('["Clinical use", "Not ready"', source)

    def test_model_examples_live_in_case_gallery(self):
        analyze = (ROOT / "web-react" / "src" / "pages" / "Analyze.tsx").read_text(encoding="utf-8")
        gallery = (ROOT / "web-react" / "src" / "pages" / "CaseGallery.tsx").read_text(encoding="utf-8")
        self.assertNotIn("Real examples with model outputs", analyze)
        self.assertIn('href="/gallery"', analyze)
        self.assertIn("Real Herlev cases with class-specific Grad-CAM", gallery)
        self.assertIn("Original image", gallery)
        self.assertIn("Grad-CAM · {sample.top}", gallery)

    def test_public_copy_defines_hpv_risk_without_claiming_infection_detection(self):
        landing = (ROOT / "web-react" / "src" / "pages" / "Landing.tsx").read_text(encoding="utf-8")
        analyze = (ROOT / "web-react" / "src" / "pages" / "Analyze.tsx").read_text(encoding="utf-8")
        report = (ROOT / "web-react" / "src" / "pages" / "ReportPreview.tsx").read_text(encoding="utf-8")

        for source in (landing, analyze, report):
            self.assertIn("HPV-associated cytomorphology", source)
        self.assertIn("does not detect or confirm HPV infection", landing)
        self.assertIn("does not detect HPV DNA/RNA", analyze)
        self.assertIn("does not confirm HPV infection", report)

    def test_research_grade_result_is_shown_with_coverage_and_not_deployed(self):
        source = (ROOT / "web-react" / "src" / "pages" / "Performance.tsx").read_text(encoding="utf-8")

        self.assertIn("Research candidate — not deployed", source)
        self.assertIn("78.8%", source)
        self.assertIn("97.3%", source)
        self.assertIn("53.3% coverage", source)
        self.assertIn("HSIL recall fell", source)

    def test_cric_ninety_percent_claim_is_selective_and_auditable(self):
        source = (ROOT / "web-react" / "src" / "pages" / "Performance.tsx").read_text(encoding="utf-8")
        evidence = json.loads((ROOT / "web-react" / "public" / "evidence" / "cric_grade_5fold_summary.json").read_text(encoding="utf-8"))
        self.assertIn("91.7% selective four-grade accuracy at 94.1% coverage", source)
        self.assertIn("Full-cohort accuracy was 88.8%", source)
        self.assertIn("SCC recall remained only 50.3%", source)
        self.assertAlmostEqual(evidence["selective_accuracy"], 0.9165869726915312)
        self.assertAlmostEqual(evidence["selective_coverage"], 0.940817754673598)
        self.assertLess(evidence["pooled_accuracy"], 0.90)

    def test_dataset_registry_separates_public_images_from_paired_hpv_cohorts(self):
        registry = json.loads((ROOT / "web-react" / "public" / "evidence" / "dataset_registry.json").read_text(encoding="utf-8"))
        records = {record["id"]: record for record in registry["records"]}

        self.assertEqual(registry["current_model_development_images"], 14969)
        self.assertEqual(records["cric"]["current_use_count"], 10003)
        self.assertEqual(records["bmt-thinprep"]["paired_hpv"], "not_exposed_per_image")
        self.assertEqual(records["nci-pap-cohort"]["current_use_count"], 0)
        self.assertEqual(records["nci-pap-cohort"]["paired_hpv"], "yes_restricted_cohort_no_public_images")
        self.assertEqual(records["hycervix-hyperspectral"]["status"], "candidate_different_modality")
        self.assertFalse(any(record["paired_hpv"] == "yes_public_image_assay_pairs" for record in records.values()))

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
        for route in ("analyze", "datasets", "gallery", "reports", "performance"):
            self.assertIn(route, workflow)
        for removed_route in ("clinical-evidence", "koil", "hpv", "workflow", "research-report"):
            self.assertNotIn(f" {removed_route} ", workflow)


if __name__ == "__main__":
    unittest.main()

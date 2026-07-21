import base64
import io
import unittest

from PIL import Image
from pypdf import PdfReader

from server.app import ReportExportReq, ReportReq, report, report_export_pdf


def analysis_payload(**overrides):
    payload = {
        "mode": "model",
        "top": {"key": "NILM", "prob": 0.82},
        "koilocyte": False,
        "quality": {"status": "pass", "ok": True},
        "uncertainty_viz": {"level": "low", "flag": False},
        "advanced_xai": {"ok": True, "primary_method": "gradcam"},
        "heatmap": "data:image/png;base64,AAAA",
    }
    payload.update(overrides)
    return payload


def tiny_png_data_url() -> str:
    stream = io.BytesIO()
    Image.new("RGB", (32, 32), (180, 90, 130)).save(stream, format="PNG")
    return "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode("ascii")


class ReportReleaseGateTests(unittest.TestCase):
    def test_patient_layer_is_locked_without_clinician_review(self):
        result = report(ReportReq(analysis=analysis_payload()))

        self.assertTrue(result["layer_patient"]["locked"])
        self.assertIn("clinician_signoff_incomplete", result["release_gates"])

    def test_high_uncertainty_remains_locked_after_confirmation(self):
        analysis = analysis_payload(uncertainty_viz={"level": "high", "flag": True})
        result = report(ReportReq(analysis=analysis, review={"status": "confirmed"}))

        self.assertTrue(result["layer_patient"]["locked"])
        self.assertIn("high_uncertainty", result["release_gates"])

    def test_quality_failure_and_xai_failure_are_release_blockers(self):
        analysis = analysis_payload(
            quality={"status": "fail", "ok": False},
            advanced_xai={"ok": False, "failure_reason": "flat_activation"},
            heatmap=None,
        )
        result = report(ReportReq(analysis=analysis, review={"status": "confirmed"}))

        self.assertTrue(result["layer_patient"]["locked"])
        self.assertIn("image_quality_failed", result["release_gates"])
        self.assertIn("xai_unavailable", result["release_gates"])

    def test_safe_confirmed_case_unlocks_patient_layer(self):
        result = report(ReportReq(
            analysis=analysis_payload(),
            review={"status": "confirmed"},
        ))

        self.assertFalse(result["layer_patient"]["locked"])
        self.assertEqual(result["release_gates"], [])

    def test_positive_koil_requires_valid_koil_xai(self):
        analysis = analysis_payload(
            koilocyte=True,
            koil_assessment={"mode": "model", "status": "positive", "probability": 0.91, "threshold": 0.34},
            koil_xai={"ok": False, "failure_reason": "flat_activation"},
        )
        result = report(ReportReq(analysis=analysis, review={"status": "confirmed"}))

        self.assertTrue(result["layer_patient"]["locked"])
        self.assertIn("koil_xai_unavailable", result["release_gates"])

    def test_active_koil_model_and_xai_can_pass_the_koil_gates(self):
        evidence = {
            "locked_test": {"sensitivity": 0.9624, "specificity": 0.9764, "auroc": 0.9912},
            "external_positive_challenge": {"true_positive": 19, "support_positive": 20, "sensitivity": 0.95, "specificity": None},
        }
        analysis = analysis_payload(
            koilocyte=True,
            koil_assessment={"mode": "model", "status": "positive", "probability": 0.91, "threshold": 0.34, "evidence": evidence},
            koil_xai={"ok": True, "method": "gradcam"},
        )
        result = report(ReportReq(analysis=analysis, review={"status": "confirmed"}))

        self.assertFalse(result["layer_patient"]["locked"])
        self.assertEqual(result["layer_clinical"]["koil_xai_method"], "gradcam")
        self.assertEqual(result["layer_clinical"]["risk_level"], "MODERATE")
        self.assertIn("KOIL morphology", result["layer_clinical"]["triage"])
        self.assertIn("KOIL morphology", result["layer_patient"]["result"])
        self.assertEqual(result["layer_clinical"]["koil_evidence"], evidence)

    def test_uncertainty_is_forwarded_to_clinical_triage(self):
        analysis = analysis_payload(uncertainty_viz={"level": "high", "flag": True})

        result = report(ReportReq(analysis=analysis, review={"status": "confirmed"}))

        self.assertIn("Do not release automatically", result["layer_clinical"]["triage"])

    def test_clinician_override_changes_reviewed_category_not_model_suggestion(self):
        result = report(ReportReq(
            analysis=analysis_payload(),
            review={"status": "edited", "final_label": "LSIL"},
        ))

        self.assertEqual(result["layer_clinical"]["bethesda"], "LSIL")
        self.assertIn("model suggested NILM", result["detailed_explanation_llm"]["summary"])
        self.assertIn("reviewed category is LSIL", result["detailed_explanation_llm"]["summary"])

    def test_symptoms_lock_patient_release_until_clinician_acknowledges_them(self):
        context = {
            "age_years": 46,
            "symptoms": ["postcoital_bleeding"],
            "specimen_type": "thinprep_lbc",
        }

        locked = report(ReportReq(
            analysis=analysis_payload(),
            clinical_context=context,
            review={"status": "confirmed"},
        ))
        released = report(ReportReq(
            analysis=analysis_payload(),
            clinical_context=context,
            review={"status": "confirmed", "symptoms_acknowledged": True},
        ))

        self.assertIn("symptomatic_context_requires_acknowledgement", locked["release_gates"])
        self.assertTrue(locked["layer_patient"]["locked"])
        self.assertNotIn("symptomatic_context_requires_acknowledgement", released["release_gates"])
        self.assertEqual(released["clinical_context"]["age_years"], 46)
        self.assertEqual(released["layer_clinical"]["bethesda"], "NILM")
        self.assertIn("symptoms still require", released["layer_patient"]["simple"])
        self.assertIn("do not use this result for reassurance", released["layer_patient"]["action"])

    def test_pdf_export_returns_a_real_gated_pdf(self):
        analysis = analysis_payload()
        generated_report = report(ReportReq(
            analysis=analysis,
            clinical_context={"age_years": 46, "symptoms": []},
            review={"status": "confirmed"},
        ))

        response = report_export_pdf(ReportExportReq(
            case_id="CC-TEST-001",
            analysis=analysis,
            report=generated_report,
            clinical_context={"age_years": 46, "symptoms": []},
        ))

        self.assertEqual(response.media_type, "application/pdf")
        self.assertTrue(response.body.startswith(b"%PDF-"))
        self.assertGreater(len(response.body), 1500)
        self.assertIn("attachment", response.headers.get("content-disposition", ""))

    def test_pdf_includes_koil_evidence_and_specific_xai(self):
        image = tiny_png_data_url()
        evidence = {
            "locked_test": {"sensitivity": 0.9624, "specificity": 0.9764, "auroc": 0.9912},
            "external_positive_challenge": {"true_positive": 19, "support_positive": 20, "sensitivity": 0.95},
        }
        analysis = analysis_payload(
            image=image,
            heatmap=image,
            koilocyte=True,
            koil_assessment={"mode": "model", "status": "positive", "probability": 0.91, "threshold": 0.3367, "evidence": evidence},
            koil_xai={"ok": True, "method": "gradcam", "heatmap": image},
        )
        generated_report = report(ReportReq(analysis=analysis, review={"status": "confirmed"}))
        response = report_export_pdf(ReportExportReq(
            case_id="CC-KOIL-XAI",
            analysis=analysis,
            report=generated_report,
            review={"status": "confirmed"},
        ))
        text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(response.body)).pages)

        self.assertIn("KOIL locked-test evidence", text)
        self.assertIn("CCCID positive challenge", text)
        self.assertIn("KOIL-specific Grad-CAM", text)


if __name__ == "__main__":
    unittest.main()

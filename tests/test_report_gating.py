import unittest

from server.app import ReportReq, report


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


if __name__ == "__main__":
    unittest.main()

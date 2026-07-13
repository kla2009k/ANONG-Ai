import json
import unittest
from unittest.mock import MagicMock, patch

from server.app import ready


def audit_connection():
    connection = MagicMock()
    connection.execute.return_value.fetchone.return_value = (0,)
    return connection


class ReadinessTests(unittest.TestCase):
    @patch("server.app._audit_connect", side_effect=audit_connection)
    @patch("server.app.predictor.status")
    def test_ready_requires_both_real_models(self, model_status, _audit):
        model_status.return_value = {
            "grade_mode": "model",
            "koil_mode": "unavailable",
        }

        response = ready()
        payload = json.loads(response.body)

        self.assertEqual(response.status_code, 503)
        self.assertFalse(payload["ok"])

    @patch("server.app._audit_connect", side_effect=audit_connection)
    @patch("server.app.predictor.status")
    def test_ready_accepts_dual_model_endpoint(self, model_status, _audit):
        model_status.return_value = {
            "grade_mode": "model",
            "koil_mode": "model",
        }

        response = ready()
        payload = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["ok"])


if __name__ == "__main__":
    unittest.main()

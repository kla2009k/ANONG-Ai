import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DeploymentContractTests(unittest.TestCase):
    def test_docker_context_includes_both_required_checkpoints(self):
        dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

        required = (
            "models/best_cervical.pt",
            "models/koil_sipakmed/best_koil_model.pt",
            "models/koil_sipakmed/test_metrics.json",
            "models/koil_sipakmed/evaluation/cccid_koil_20_case_challenge.json",
        )
        for checkpoint in required:
            self.assertTrue((ROOT / checkpoint).is_file(), checkpoint)
            self.assertIn(f"!{checkpoint}", dockerignore)
            self.assertIn(f"COPY {checkpoint} {checkpoint}", dockerfile)

    def test_render_blueprint_uses_model_capable_instance_and_readiness(self):
        blueprint = (ROOT / "render.yaml").read_text(encoding="utf-8")

        self.assertIn("runtime: docker", blueprint)
        self.assertIn("plan: standard", blueprint)
        self.assertIn("region: singapore", blueprint)
        self.assertIn("healthCheckPath: /api/ready", blueprint)
        self.assertIn("autoDeployTrigger: checksPass", blueprint)


if __name__ == "__main__":
    unittest.main()

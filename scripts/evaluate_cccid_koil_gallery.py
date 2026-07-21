"""Run the locked KOIL model on the deterministic CCCID reference challenge."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from server import predictor


MANIFEST = ROOT / "web-react" / "public" / "koil-gallery" / "index.json"
CHECKPOINT = ROOT / "models" / "koil_sipakmed" / "best_koil_model.pt"
OUTPUT = ROOT / "models" / "koil_sipakmed" / "evaluation" / "cccid_koil_20_case_challenge.json"
PUBLIC_OUTPUT = ROOT / "web-react" / "public" / "evidence" / "cccid_koil_20_case_challenge.json"


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return center - margin, center + margin


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    state = predictor.load_model()
    evidence_status = predictor.status()["koil_evidence"]
    if state["koil_mode"] != "model" or evidence_status["locked_test_support"] is None:
        raise SystemExit("The trained KOIL checkpoint is not active")

    rows = []
    for item in manifest["items"]:
        image_path = ROOT / "web-react" / "public" / item["image"]
        bgr = predictor._to_bgr(image_path.read_bytes())
        assessment = predictor._model_koil_assessment(bgr)
        rows.append({
            "id": item["id"],
            "subtype": item["subtype"],
            "positive": assessment["positive"],
            "koil_probability": assessment["probability"],
            "locked_threshold": assessment["threshold"],
        })

    positives = sum(row["positive"] for row in rows)
    lower, upper = wilson_interval(positives, len(rows))
    payload = {
        "dataset": "CCCID v2",
        "dataset_doi": manifest["dataset_doi"],
        "license": manifest["license"],
        "evaluation_type": "deterministic_external_positive_only_challenge",
        "selection_locked_before_inference": True,
        "selection": manifest["selection"],
        "model_training_domain": "SIPaKMeD conventional Pap-smear single-cell crops",
        "challenge_domain": "CCCID BD SurePath liquid-based cytology center-focus images",
        "checkpoint_sha256": hashlib.sha256(CHECKPOINT.read_bytes()).hexdigest(),
        "support_positive": len(rows),
        "true_positive": positives,
        "false_negative": len(rows) - positives,
        "sensitivity": positives / len(rows),
        "sensitivity_wilson_95_ci": {"lower": lower, "upper": upper},
        "specificity": None,
        "auroc": None,
        "limitation": "Positive-only 20-image challenge; specificity, AUROC, calibration, and clinical accuracy are not estimable.",
        "hpv_test": False,
        "rows": rows,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2) + "\n"
    OUTPUT.write_text(serialized, encoding="utf-8")
    PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_OUTPUT.write_text(serialized, encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("support_positive", "true_positive", "false_negative", "sensitivity", "sensitivity_wilson_95_ci")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

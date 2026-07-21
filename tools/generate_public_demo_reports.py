"""Generate de-identified public demo PDFs from real local inference runs."""

from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "web-react" / "public"
OUTPUT = PUBLIC / "reports"
API = "http://127.0.0.1:8003"
CASES = [
    ("ANONG-DEMO-NILM", "samples/s00_NILM.jpg", "NILM"),
    ("ANONG-DEMO-LSIL", "samples/s02_LSIL.jpg", "LSIL"),
    ("ANONG-DEMO-HSIL", "samples/s04_HSIL.jpg", "HSIL"),
    ("ANONG-DEMO-SCC", "samples/s06_SCC.jpg", "SCC"),
    ("ANONG-DEMO-KOIL", "koil-gallery/koil-superficial-01.jpg", None),
]


def request_json(path: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        API + path,
        data=body,
        headers={"Content-Type": "application/json"} if body else {},
        method="POST" if body else "GET",
    )
    try:
        with urlopen(request, timeout=180) as response:
            return json.loads(response.read())
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"{path} failed: {exc}") from exc


def request_pdf(path: str, payload: dict) -> bytes:
    request = Request(
        API + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=180) as response:
            data = response.read()
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"{path} failed: {exc}") from exc
    if not data.startswith(b"%PDF-"):
        raise RuntimeError(f"{path} did not return a PDF")
    return data


def image_data_url(relative_path: str) -> str:
    path = PUBLIC / relative_path
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def main() -> None:
    ready = request_json("/api/ready")
    if not ready.get("ok") or ready.get("model_status", {}).get("grade_mode") != "model":
        raise RuntimeError("Local trained models are not ready")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    reports = []
    context = {
        "age_years": None,
        "symptoms": [],
        "other_symptoms": "",
        "specimen_type": "unknown",
        "last_screening": "unknown",
        "hpv_test": "not_performed",
        "hpv_genotype": "",
        "prior_abnormal_result": False,
        "immunocompromised": False,
        "pregnant": False,
    }
    for case_id, source_image, reference_grade in CASES:
        image = image_data_url(source_image)
        analysis = request_json("/api/analyze", {"image": image})
        analysis["image"] = image
        top = analysis.get("top") or {}
        model_grade = top.get("key", "Unavailable")
        reviewed_grade = reference_grade or model_grade
        review_status = "edited" if reference_grade and model_grade != reference_grade else "confirmed"
        review = {"status": review_status, "symptoms_acknowledged": False}
        if review_status == "edited":
            review["final_label"] = reviewed_grade
        report = request_json("/api/report", {
            "case_id": case_id,
            "analysis": analysis,
            "review": review,
            "clinical_context": context,
        })
        pdf = request_pdf("/api/report/export/pdf", {
            "case_id": case_id,
            "analysis": analysis,
            "report": report,
            "review": review,
            "clinical_context": context,
        })
        filename = f"{case_id.lower()}.pdf"
        (OUTPUT / filename).write_bytes(pdf)
        koil = analysis.get("koil_assessment") or {}
        reports.append({
            "case_id": case_id,
            "file": f"reports/{filename}",
            "grade": reviewed_grade,
            "model_grade": model_grade,
            "reference_grade": reference_grade,
            "prediction_correct": reference_grade is None or model_grade == reference_grade,
            "koil_status": koil.get("status", "Unavailable"),
            "koil_probability": koil.get("probability"),
            "review_status": review_status,
            "source_image": source_image,
            "model_mode": analysis.get("mode"),
            "sha256": hashlib.sha256(pdf).hexdigest(),
            "bytes": len(pdf),
        })

    manifest = {
        "generated_by": "tools/generate_public_demo_reports.py",
        "generation_mode": "real_local_dual_model_inference",
        "contains_patient_identifiers": False,
        "regulated_medical_report": False,
        "reports": reports,
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
CervicalAI — FastAPI backend (Phase 1.5 Web/Stress/Report+).

Endpoints:
  GET  /              -> web demo (index.html)
  GET  /api/health    -> status
  POST /api/analyze   -> {image: dataURL} -> 4-class grade + independent KOIL morphology + validated CAM/abstention + uncertainty
  POST /api/batch_analyze -> [{image}, ...] -> array of results (for batch sim)
  POST /api/stress    -> {n, fake_size?} -> run N prediction loops, return stats (load test)
  POST /api/generate_fake -> {count} -> generate synthetic cytology-like images (base64)
  POST /api/report    -> 2-layer report template + prototype LLM-style text + XAI embed support
  POST /api/contours/edit -> apply fake contour edits (prototype demo only)
  POST /api/report/export -> return structured report for client-side PDF/print (with XAI)
  POST /api/report/export/pdf -> formal unsigned research pre-screen PDF
  POST /api/contour_edit -> SAM-like stub (prototype demo only)

Run:
  cd server && python -m uvicorn app:app --port 8003 --reload
"""
import base64
import hashlib
import html
import io
import json
import pathlib
import re
import sqlite3
import time
import os
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from PIL import Image, UnidentifiedImageError

try:
    from . import predictor
except ImportError:
    import predictor

ROOT = pathlib.Path(__file__).parent.parent
WEB = pathlib.Path(os.getenv("ANONG_WEB_DIR", str(ROOT / "web-dist")))
if not WEB.exists() and (ROOT / "web").exists():
    WEB = ROOT / "web"
AUDIT_LOG = ROOT / "artifacts" / "web_demo_audit.jsonl"
AUDIT_DB = ROOT / "artifacts" / "web_demo_audit.sqlite3"
MAX_BYTES = 12 * 1024 * 1024
SERVER_COUNTERS = {"analyze": 0, "audit_writes": 0, "report_exports": 0, "errors": 0}


def _now_iso() -> str:
    return __import__("datetime").datetime.utcnow().isoformat() + "Z"


def _model_dump(model: BaseModel) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _audit_connect() -> sqlite3.Connection:
    AUDIT_DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(AUDIT_DB)
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            client_ts TEXT NOT NULL,
            server_ts TEXT NOT NULL,
            status TEXT NOT NULL,
            ai_top TEXT NOT NULL,
            final_label TEXT NOT NULL,
            confidence REAL NOT NULL,
            uncertainty TEXT NOT NULL,
            hpv_risk TEXT NOT NULL,
            source TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            prev_hash TEXT NOT NULL,
            entry_hash TEXT NOT NULL UNIQUE
        )
        """
    )
    con.commit()
    return con


def _audit_last_hash(con: sqlite3.Connection) -> str:
    row = con.execute("SELECT entry_hash FROM audit_entries ORDER BY id DESC LIMIT 1").fetchone()
    return row[0] if row else "GENESIS"


def _audit_hash(payload: dict, prev_hash: str) -> str:
    body = json.dumps({"prev_hash": prev_hash, "payload": payload}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _audit_insert(entry: dict) -> dict:
    con = _audit_connect()
    try:
        payload = dict(entry)
        payload["server_ts"] = _now_iso()
        payload["regulated"] = False
        payload["storage"] = "sqlite-hash-chain-demo"
        prev_hash = _audit_last_hash(con)
        entry_hash = _audit_hash(payload, prev_hash)
        con.execute(
            """
            INSERT INTO audit_entries
            (case_id, client_ts, server_ts, status, ai_top, final_label, confidence,
             uncertainty, hpv_risk, source, payload_json, prev_hash, entry_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["caseId"],
                payload["ts"],
                payload["server_ts"],
                payload["status"],
                payload["aiTop"],
                payload["finalLabel"],
                float(payload["confidence"]),
                payload["uncertainty"],
                payload["hpvRisk"],
                payload["source"],
                json.dumps(payload, ensure_ascii=False, sort_keys=True),
                prev_hash,
                entry_hash,
            ),
        )
        con.commit()
        payload["prev_hash"] = prev_hash
        payload["entry_hash"] = entry_hash
        return payload
    finally:
        con.close()


def _audit_read(limit: int = 100) -> list[dict]:
    if not AUDIT_DB.exists():
        return []
    con = _audit_connect()
    try:
        rows = con.execute(
            """
            SELECT payload_json, prev_hash, entry_hash FROM audit_entries
            ORDER BY id DESC LIMIT ?
            """,
            (max(1, min(limit, 500)),),
        ).fetchall()
        out = []
        for payload_json, prev_hash, entry_hash in rows:
            item = json.loads(payload_json)
            item["prev_hash"] = prev_hash
            item["entry_hash"] = entry_hash
            out.append(item)
        return out
    finally:
        con.close()


def _decode_image(image: str) -> bytes:
    value = image or ""
    m = re.fullmatch(r"data:(image/[^;]+);base64,(.+)", value, re.DOTALL | re.IGNORECASE)
    if value.startswith("data:") and not m:
        raise HTTPException(status_code=400, detail="invalid image data URL")
    mime = m.group(1).lower() if m else None
    if mime and mime not in {"image/jpeg", "image/png", "image/bmp", "image/x-ms-bmp"}:
        raise HTTPException(status_code=400, detail="unsupported image type")
    raw = m.group(2) if m else value
    try:
        data = base64.b64decode(re.sub(r"\s+", "", raw), validate=True)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid image data")
    if not data:
        raise HTTPException(status_code=400, detail="empty image")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="image too large")
    try:
        with Image.open(io.BytesIO(data)) as decoded:
            decoded.verify()
        with Image.open(io.BytesIO(data)) as decoded:
            if decoded.format not in {"JPEG", "PNG", "BMP"}:
                raise HTTPException(status_code=400, detail="unsupported decoded image format")
            width, height = decoded.size
            if width < 32 or height < 32:
                raise HTTPException(status_code=400, detail="image dimensions are too small")
            if width > 12000 or height > 12000 or width * height > 50_000_000:
                raise HTTPException(status_code=413, detail="image dimensions are too large")
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(status_code=400, detail="decoded payload is not a valid image")
    return data


@asynccontextmanager
async def lifespan(app: FastAPI):
    predictor.load_model()
    yield


app = FastAPI(title="Anong / CerviCo-Pilot", version="0.2", lifespan=lifespan)
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ANONG_ALLOWED_ORIGINS",
        "http://localhost:8003,http://localhost:4174,http://localhost:5173,http://127.0.0.1:4174,http://127.0.0.1:5173,https://kla2009k.github.io",
    ).split(",")
    if origin.strip()
]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


class AnalyzeReq(BaseModel):
    image: str  # data URL


class BatchAnalyzeReq(BaseModel):
    images: list[str]  # list of data URLs


class StressReq(BaseModel):
    n: int = 20
    fake_size: int = 160


class GenerateFakeReq(BaseModel):
    count: int = 4
    size: int = 224


class AuditEntryReq(BaseModel):
    caseId: str
    ts: str
    status: str
    aiTop: str
    finalLabel: str
    confidence: float
    uncertainty: str
    hpvRisk: str
    source: str


@app.get("/api/health")
def health():
    model_status = predictor.status()
    return {
        "ok": True,
        "mode": predictor.mode(),
        "classes": predictor.CLASSES,
        "model_status": model_status,
        "phase": "1.6",
        "features": ["four_class_grade", "independent_koil_morphology", "batch", "stress", "validated_cam_or_abstain", "report_release_gates", "report_only_clinical_context", "formal_research_pdf", "xai_embed"],
        "evaluated_scope": "Herlev grade/triage evidence plus independent SIPaKMeD KOIL morphology evidence; no Thai ThinPrep validation",
        "xai_scope": "Post-hoc engineering visualization with degeneracy checks; not clinically validated localization",
        "prototype_only": ["generated_fake_images", "contour_edit", "SAM-like refinement", "zstack", "WSI simulation"],
    }


@app.get("/api/ready")
def ready():
    """Readiness endpoint for demo deployment checks."""
    try:
        con = _audit_connect()
        last_hash = _audit_last_hash(con)
        count = con.execute("SELECT COUNT(*) FROM audit_entries").fetchone()[0]
        con.close()
        audit_ok = True
    except Exception:
        SERVER_COUNTERS["errors"] += 1
        last_hash = None
        count = 0
        audit_ok = False
    model_status = predictor.status()
    models_ok = model_status["grade_mode"] == "model" and model_status["koil_mode"] == "model"
    ready_ok = models_ok and audit_ok
    payload = {
        "ok": ready_ok,
        "model_loaded": predictor.mode(),
        "model_status": model_status,
        "audit_store_ok": audit_ok,
        "audit_entries": count,
        "audit_last_hash": last_hash,
        "regulated": False,
        "note": "Demo readiness only; not a regulated hospital deployment check.",
    }
    return JSONResponse(status_code=200 if ready_ok else 503, content=payload)


@app.get("/api/metrics")
def metrics():
    """Minimal demo observability counters."""
    return {
        "ok": True,
        "uptime_hint": "process-local counters reset on restart",
        "counters": SERVER_COUNTERS,
        "regulated": False,
    }


@app.post("/api/analyze")
def analyze(req: AnalyzeReq):
    data = _decode_image(req.image)
    try:
        SERVER_COUNTERS["analyze"] += 1
        return predictor.analyze(data, want_heatmap=True)
    except Exception as e:
        SERVER_COUNTERS["errors"] += 1
        raise HTTPException(status_code=500, detail=f"analyze failed: {e}")


@app.get("/api/audit")
def audit_list():
    """Demo-only append-only audit log. Not a regulated clinical audit trail."""
    return {
        "entries": _audit_read(limit=100),
        "source": "sqlite-hash-chain-demo",
        "regulated": False,
        "note": "Hash-chain demo for traceability; not a certified immutable clinical audit log.",
    }


@app.post("/api/audit")
def audit_save(req: AuditEntryReq):
    """Demo-only append-only audit log. Uses no patient identifiers."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = _model_dump(req)
    stored = _audit_insert(entry)
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(stored, ensure_ascii=False) + "\n")
    SERVER_COUNTERS["audit_writes"] += 1
    return {
        "ok": True,
        "stored": True,
        "source": "sqlite-hash-chain-demo",
        "entry_hash": stored["entry_hash"],
        "prev_hash": stored["prev_hash"],
        "regulated": False,
    }


@app.post("/api/batch_analyze")
def batch_analyze(req: BatchAnalyzeReq):
    """Batch prediction for stress / multi-upload sim."""
    results = []
    for i, img in enumerate(req.images or []):
        try:
            data = _decode_image(img)
            res = predictor.analyze(data, want_heatmap=True)
            results.append({"index": i, "ok": True, "result": res})
        except Exception as e:
            results.append({"index": i, "ok": False, "error": str(e)})
    return {"count": len(results), "ok_count": sum(1 for r in results if r["ok"]), "results": results}


@app.post("/api/stress")
def stress(req: StressReq):
    """Run N prediction loops with synthetic data. Returns timing + error stats."""
    import time, io, base64
    from PIL import Image
    import numpy as np

    n = max(1, min(req.n, 500))
    size = max(64, min(req.fake_size, 512))
    times = []
    ok = 0
    fails = 0
    start = time.time()
    for i in range(n):
        # generate tiny synthetic cytology-ish PNG
        arr = np.random.randint(180, 250, (size, size, 3), dtype=np.uint8)
        # add dark blobs
        for _ in range(8):
            cx, cy = np.random.randint(10, size-10), np.random.randint(10, size-10)
            r = np.random.randint(2, 9)
            y, x = np.ogrid[:size, :size]
            mask = (x - cx)**2 + (y - cy)**2 <= r*r
            arr[mask] = np.clip(arr[mask].astype(int) - 70, 0, 255).astype(np.uint8)
        buf = io.BytesIO()
        Image.fromarray(arr).save(buf, format="PNG")
        b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
        t0 = time.time()
        try:
            data = _decode_image(b64)
            _ = predictor.analyze(data, want_heatmap=False)
            ok += 1
        except Exception:
            fails += 1
        times.append((time.time() - t0) * 1000.0)
    total_ms = (time.time() - start) * 1000.0
    return {
        "n": n,
        "ok": ok,
        "fail": fails,
        "total_ms": round(total_ms, 1),
        "avg_ms": round(sum(times)/len(times), 2) if times else 0,
        "p95_ms": round(sorted(times)[int(0.95*len(times))] if times else 0, 2),
        "mode": predictor.mode(),
    }


@app.post("/api/generate_fake")
def generate_fake(req: GenerateFakeReq):
    """Return count synthetic cytology-like images (dataURL)."""
    import io, base64
    from PIL import Image
    import numpy as np

    out = []
    for i in range(max(1, min(req.count, 32))):
        size = req.size
        arr = np.random.randint(170, 255, (size, size, 3), dtype=np.uint8)
        # nuclei-like dark spots + texture
        rng = np.random.default_rng(i + 42)
        for _ in range(rng.integers(6, 18)):
            cx = rng.integers(8, size-8)
            cy = rng.integers(8, size-8)
            r = rng.integers(2, 11)
            y, x = np.ogrid[:size, :size]
            mask = (x - cx)**2 + (y - cy)**2 <= r*r
            shade = rng.integers(40, 90)
            arr[mask] = np.clip(arr[mask].astype(int) - shade, 0, 255).astype(np.uint8)
        buf = io.BytesIO()
        Image.fromarray(arr).save(buf, format="PNG")
        b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
        out.append(b64)
    return {"count": len(out), "images": out}


class ClinicalContext(BaseModel):
    """Optional context for reporting and triage; never used as model input."""
    age_years: int | None = Field(default=None, ge=10, le=120)
    symptoms: List[str] = Field(default_factory=list, max_length=12)
    other_symptoms: str | None = Field(default=None, max_length=500)
    specimen_type: str = Field(default="unknown", max_length=40)
    last_screening: str = Field(default="unknown", max_length=40)
    hpv_test: str = Field(default="not_performed", max_length=40)
    hpv_genotype: str | None = Field(default=None, max_length=80)
    prior_abnormal_result: bool = False
    immunocompromised: bool = False
    pregnant: bool = False


class ReportReq(BaseModel):
    image: str | None = None
    analysis: dict
    review: dict | None = None
    clinical_context: ClinicalContext | None = None


class ContourEdit(BaseModel):
    id: str
    class_: str | None = None  # "class" is reserved
    points: List[List[int]] | None = None


class ContourEditReq(BaseModel):
    image: str | None = None
    edits: List[Dict[str, Any]]


class ReportExportReq(BaseModel):
    case_id: str | None = Field(default=None, max_length=80)
    analysis: dict
    report: dict | None = None
    patient_hint: str | None = None
    clinical_context: ClinicalContext | None = None


def _clinical_context_payload(context: ClinicalContext | None) -> dict:
    if context is None:
        return {}
    return _model_dump(context)


def _has_reported_symptoms(context: dict) -> bool:
    symptoms = [str(value).strip() for value in context.get("symptoms") or []]
    return bool(symptoms or str(context.get("other_symptoms") or "").strip())


@app.post("/api/report")
def report(req: ReportReq):
    """Build a controlled two-layer research report with server-side release gates."""
    a = req.analysis or {}
    review = req.review or {}
    top = a.get("top", {})
    koil = a.get("koilocyte", False)
    koil_assessment = a.get("koil_assessment") or {}
    koil_xai = a.get("koil_xai") or {}
    unc = a.get("uncertainty") or a.get("uncertainty_viz") or {}
    heatmap = a.get("heatmap")
    quality = a.get("quality") or {}
    xai = a.get("advanced_xai") or {}
    clinical_context = _clinical_context_payload(req.clinical_context)
    symptomatic = _has_reported_symptoms(clinical_context)

    model_suggestion = top.get("key", "UNKNOWN")
    reviewed_label = review.get("final_label")
    bethesda = reviewed_label if reviewed_label in {"NILM", "LSIL", "HSIL", "SCC"} else model_suggestion
    prob = float(top.get("prob", 0.0))

    release_gates = []
    if review.get("status") not in {"confirmed", "edited"}:
        release_gates.append("clinician_signoff_incomplete")
    if bool(unc.get("flag")) or unc.get("level") == "high":
        release_gates.append("high_uncertainty")
    if quality.get("status") == "fail" or quality.get("ok") is False:
        release_gates.append("image_quality_failed")
    if xai.get("ok") is not True or not heatmap:
        release_gates.append("xai_unavailable")
    if a.get("mode") != "model":
        release_gates.append("trained_model_not_active")
    if koil_assessment and koil_assessment.get("mode") != "model":
        release_gates.append("koil_model_not_active")
    if koil and koil_xai.get("ok") is not True:
        release_gates.append("koil_xai_unavailable")
    if symptomatic and review.get("symptoms_acknowledged") is not True:
        release_gates.append("symptomatic_context_requires_acknowledgement")

    clinical = {
        "bethesda": bethesda,
        "confidence": round(prob, 3),
        "koilocyte": bool(koil),
        "koil_assessment": koil_assessment,
        "koil_evidence": koil_assessment.get("evidence") if koil_assessment else None,
        "koil_xai_method": koil_xai.get("method") if koil_xai.get("ok") is True else None,
        "uncertainty_flag": bool(unc.get("flag", False)),
        "triage": _triage_rule(bethesda, prob, bool(koil), bool(unc.get("flag", False))),
        "risk_level": "HIGH" if bethesda in ("HSIL", "SCC") else ("MODERATE" if bethesda == "LSIL" or koil else "LOW"),
        "recommended_action": _clinical_action(bethesda, bool(koil), bool(unc.get("flag", False))),
        "quality_status": quality.get("status", "unknown"),
        "xai_method": xai.get("primary_method"),
        "review_status": review.get("status", "pending"),
        "symptoms_present": symptomatic,
        "context_note": (
            "Symptoms require separate clinical evaluation; a cytology AI result must not be used to rule out disease."
            if symptomatic else
            "No symptoms were entered. Absence of entered symptoms is not a clinical finding."
        ),
        "release_gates": release_gates,
        "note": "Research pre-screen only. Qualified clinician review is required before any patient-facing release.",
        "xai_embed_present": bool(heatmap) and xai.get("ok") is True,
    }

    if release_gates:
        lay = {
            "locked": True,
            "release_status": "blocked",
            "blockers": release_gates,
            "result": None,
            "action": "Resolve all release gates and complete qualified clinical review.",
        }
    else:
        lay = {
            "locked": False,
            "release_status": "reviewed_demo",
            **_patient_layer(bethesda, prob, bool(koil), False),
        }
        if symptomatic:
            lay["symptom_safety_note"] = (
                "Reported symptoms require clinician-led evaluation independent of this image result."
            )
            lay["result"] = "The image category was reviewed, but reported symptoms require separate clinical evaluation."
            lay["action"] = "Follow the responsible clinician's symptom-led evaluation plan; do not use this result for reassurance."
            lay["why"] = "A cytology image pre-screen cannot rule out the causes of reported symptoms."
            lay["simple"] = "Reported symptoms still require clinical evaluation regardless of this image result."

    controlled_explanation = {
        "summary": f"The model suggested {model_suggestion} with probability {prob:.3f}; the reviewed category is {bethesda}.",
        "scope": "Grade evidence is from Herlev; KOIL locked-test evidence is from SIPaKMeD and the positive-only external challenge is from CCCID liquid-based cytology.",
        "explanation": f"{xai.get('primary_method') or 'No valid class-activation map'}; post-hoc visualization, not causal proof.",
        "limitations": [
            "Not a final diagnosis.",
            "Not validated on Thai ThinPrep clinical data.",
            "HPV-related morphology wording does not detect HPV DNA or RNA.",
            "The KOIL endpoint has locked SIPaKMeD evidence and a limited positive-only CCCID liquid-based challenge, but no negative-inclusive external ThinPrep or Thai clinical validation.",
        ],
    }

    out = {
        "layer_clinical": clinical,
        "layer_patient": lay,
        "clinical_context": clinical_context,
        "release_gates": release_gates,
        "detailed_explanation_llm": controlled_explanation,
        "source": "deterministic controlled template; no generative clinical text",
        "disclaimer": "Research decision support only. Clinician confirmation is required; this is not a diagnosis.",
        "citations": [
            "The Bethesda System for Reporting Cervical Cytology, 3rd edition",
        ]
    }
    if heatmap and xai.get("ok") is True:
        out["xai_embed"] = heatmap
    return out


def _generate_detailed_llm_explanation(bethesda: str, prob: float, koilocyte: bool, unc: dict) -> dict:
    """Long, detailed medical explanation (simulates high-quality LLM output).
    In production: call real LLM with the prompt templates at bottom of this file.
    """
    prob_pct = f"{prob*100:.1f}%"
    risk = "HIGH" if bethesda in ("HSIL", "SCC") else "MODERATE" if bethesda in ("LSIL", "KOIL") else "LOW"
    entropy = unc.get("entropy", "N/A")
    flagged = unc.get("flag", False)

    base = f"""ผลการคัดกรองโดย AI (CervicalAI – EfficientNet-B0 บนข้อมูลจริง Herlev 917 ภาพ)
พบ **{bethesda}** ด้วยความมั่นใจ {prob_pct} (risk: {risk}).

**ความหมายทางคลินิกตาม Bethesda System 2014:**
"""
    if bethesda == "NILM":
        detail = base + """เซลล์ squamous และ glandular อยู่ในเกณฑ์ปกติ ไม่พบรอยโรค intraepithelial lesion หรือ malignancy. 
นิวเคลียสมีขนาดและรูปร่างปกติ, chromatin กระจายสม่ำเสมอ, ไม่มี hyperchromasia หรือ irregular nuclear membrane. 
Cytoplasm ใส ไม่มี halo หรือ cluster ผิดปกติ.

**เหตุผลที่โมเดลตัดสินใจ (XAI + Uncertainty):**
Grad-CAM แสดงจุดสนใจที่กระจายทั่วไป ไม่มี hotspot ที่ชัดเจนของ atypia. Entropy ต่ำ ({entropy}) แสดงถึงความมั่นใจสูงของโมเดล. ไม่มี flag จาก uncertainty.

**ความเสี่ยงและการจัดการ (อ้างอิง WHO & Thai guidelines):**
ความเสี่ยงต่ำ. อย่างไรก็ตาม การคัดกรองปากมดลูกควรทำซ้ำทุก 3-5 ปีตามอายุและปัจจัยเสี่ยง (HPV 52/58 พบบ่อยในไทย). 
ถ้าผล HPV positive ควรร่วมพิจารณา.

**อ้างอิง:**
- Bethesda System for Reporting Cervical Cytology, 3rd ed. (Nayar & Wilbur, 2014)
- WHO Cervical Cancer Elimination Initiative 90-70-90 (2020-2030)
- Thai National Cancer Institute screening guidelines"""
    elif bethesda == "LSIL":
        detail = base + f"""พบรอยโรค intraepithelial ระดับต่ำ (Low-grade Squamous Intraepithelial Lesion). 
ลักษณะเด่น: การขยายตัวของนิวเคลียสเล็กน้อย (mild nuclear enlargement), perinuclear halo (ถ้าพบ koilocyte) และการเปลี่ยนแปลงของ chromatin ที่ไม่รุนแรง.

{f"พบลักษณะ koilocytic morphology จาก endpoint แยกต่างหาก ซึ่งสัมพันธ์กับ HPV-related cellular change แต่ไม่ยืนยันการติดเชื้อ HPV." if koilocyte else ""}

**เหตุผลจาก AI (XAI + Uncertainty):**
Heatmap เน้นที่โซน halo และ nuclear atypia เล็กน้อย. Entropy ปานกลาง ({entropy}) สะท้อนความไม่แน่นอนระดับต่ำ-ปานกลาง. {"Uncertainty flag ถูกตั้งค่าเนื่องจาก borderline features." if flagged else ""}

**ความเสี่ยงและการจัดการ:**
LSIL ส่วนใหญ่ (60-80%) หายได้เองภายใน 1-2 ปี โดยเฉพาะในผู้ติดเชื้อ HPV transient. 
อย่างไรก็ตาม ควรติดตามเพื่อป้องกัน progression เป็น HSIL (ประมาณ 10-20% ใน 2 ปี).

**คำแนะนำตามแนวทาง:**
- ทำซ้ำ Pap smear ใน 6-12 เดือน หรือ HPV DNA test ร่วม (co-test)
- ถ้า HPV 16/18 positive → colposcopy
- ในไทย: เน้น HPV 52/58 ซึ่งพบบ่อยกว่า 16/18

**อ้างอิง:**
- Bethesda 2014
- Plissiti et al. ICIP 2018 (official SIPaKMeD morphology dataset)
- Nature Comm 2025 LMIC study (compact AI AUC 0.85-0.89)"""
    elif bethesda == "HSIL":
        detail = base + f"""พบรอยโรค intraepithelial ระดับสูง (High-grade Squamous Intraepithelial Lesion) – มีโอกาสสูงที่จะพัฒนาเป็นมะเร็งปากมดลูกหากไม่รักษา.

ลักษณะทางสัณฐาน: นิวเคลียสขยายใหญ่ชัด (high N/C ratio), hyperchromasia, irregular nuclear contour, และ cluster ของเซลล์ผิดปกติ.

{f"พบ koilocytic morphology ร่วมด้วย แต่ภาพเซลล์เพียงอย่างเดียวไม่สามารถยืนยันชนิดหรือสถานะการติดเชื้อ HPV." if koilocyte else ""}

**เหตุผลจาก AI:**
Multi-CAM (Grad + Eigen) เน้นที่โซน nuclear atypia และ chromatin coarse อย่างชัดเจน. Entropy สูงขึ้น ({entropy}) บ่งชี้ความซับซ้อนของภาพ. {"Uncertainty flag เปิด – ควรให้แพทย์ review ใกล้ชิด" if flagged else ""}

**ความเสี่ยงและการจัดการ:**
HSIL มีโอกาส progression เป็น invasive cancer สูง (ประมาณ 20-30% ใน 5 ปี ถ้าไม่รักษา). 
ต้องรีบตรวจยืนยันด้วย colposcopy + biopsy ทันที.

**คำแนะนำ:**
- ส่งต่อ specialist ทันที (LEEP / conization อาจจำเป็น)
- ร่วมตรวจ HPV typing (16/18/52/58)

**อ้างอิง:**
- UniCAS (Jiang et al., Cell Reports Medicine 2026): foundation model บน 48k WSI ลด overhead 70% AUC 0.92
- Nature Comm 2025 LMIC compact AI
- Thai LTFU RCT: AI triage ลด loss-to-follow-up จาก 38% เป็น 22%"""
    elif bethesda == "SCC":
        detail = base + f"""พบ Squamous Cell Carcinoma – มะเร็งปากมดลูกชนิด squamous.

ลักษณะ: นิวเคลียสขนาดใหญ่ผิดปกติมาก, prominent nucleoli, coarse chromatin, necrosis และเซลล์กระจายตัวแบบ invasive.

**เหตุผลจาก AI:**
XAI แสดง hotspot ที่ nuclear atypia รุนแรงและโครงสร้าง tissue ผิดปกติ. 

**ความเสี่ยง:**
สูงมาก – ต้องการ staging และการรักษาแบบมะเร็ง (surgery, radiotherapy, chemotherapy ตาม FIGO staging).

**คำแนะนำ:**
- ส่งต่อศูนย์มะเร็งทันที
- ร่วมตรวจ imaging และ biopsy ยืนยัน

**อ้างอิง:**
- UniCAS 2026 (large-scale WSI foundation model)
- WHO guidelines for invasive cervical cancer management"""
    else:
        detail = base + "พบ koilocytic morphology ซึ่งต้องให้ผู้เชี่ยวชาญทบทวน และไม่สามารถใช้แทน HPV DNA/RNA testing."

    return {
        "summary": f"{bethesda} ({prob_pct})",
        "detailed_text": detail,
        "length": "long (LLM-style 300-500+ words equivalent)",
        "citations_included": True
    }


# ──────────────────────────────────────────────────────────────────────────────
# Interactive contour edit stub (SAM-like for Phase 2)
# ──────────────────────────────────────────────────────────────────────────────
class ContourEditReq(BaseModel):
    points: list[list[int]] | None = None  # [[x,y], ...] user clicks
    image_size: list[int] | None = None  # [w, h]
    mask_hint: str | None = None  # optional base64 rough mask


@app.post("/api/contour_edit")
def contour_edit(req: ContourEditReq):
    """SAM-like interactive contour stub.
    Input: seed points (or rough mask)
    Output: 'refined' polygon + area stats (mock; real = SAM2 fine-tune on cyto nuclei)
    """
    pts = req.points or [[50, 50], [120, 40], [130, 110], [60, 115]]
    w, h = (req.image_size or [224, 224])

    # naive "refine": convex hull-ish + jitter for demo
    import numpy as np
    arr = np.array(pts, dtype=np.float32)
    cx, cy = arr.mean(0)
    refined = []
    for p in arr:
        dx = (p[0] - cx) * 0.9 + cx + np.random.uniform(-3, 3)
        dy = (p[1] - cy) * 0.9 + cy + np.random.uniform(-3, 3)
        refined.append([int(max(0, min(w-1, dx))), int(max(0, min(h-1, dy)))])
    # close polygon
    if len(refined) > 2:
        refined.append(refined[0])

    # compute mock area
    area = 0.0
    for i in range(len(refined)-1):
        x1,y1 = refined[i]; x2,y2 = refined[i+1]
        area += x1*y2 - x2*y1
    area = abs(area) / 2.0

    return {
        "input_points": pts,
        "refined_contour": refined,
        "area_px": round(area, 1),
        "centroid": [round(float(cx),1), round(float(cy),1)],
        "note": "PROTOTYPE STUB: SAM-like refinement only. Not validated; Phase 2 would require real SAM2/cytology segmentation data.",
        "editable": True,
    }


@app.post("/api/contours/edit")
def contours_edit(req: ContourEditReq):
    """Apply user edits to fake contours (demo only)."""
    try:
        data = _decode_image(req.image) if req.image else b""
        edits = req.edits or []
        return predictor.apply_contour_edits(data, edits)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"contour edit failed: {e}")


@app.post("/api/report/export")
def report_export(req: ReportExportReq):
    """Return a clean export payload suitable for client-side PDF/print.
    Includes XAI embed if present, 2-layer report, and text summary.
    """
    a = req.analysis or {}
    r = req.report or {}
    top = a.get("top", {})
    unc = a.get("uncertainty") or a.get("uncertainty_viz") or {}
    clinical = r.get("layer_clinical") or {}
    patient = r.get("layer_patient") or {}
    xai_state = a.get("advanced_xai") or {}
    xai = (r.get("xai_embed") or a.get("heatmap") or a.get("xai_embed")) if xai_state.get("ok") is True else None
    context = _clinical_context_payload(req.clinical_context) or r.get("clinical_context") or {}

    # Build a compact text block
    lines = []
    lines.append("Anong | CerviCo-Pilot reviewed research pre-screen")
    lines.append("=" * 56)
    lines.append(f"Top: {top.get('key','?')}  {(top.get('prob',0)*100):.1f}%")
    koil_assessment = a.get("koil_assessment") or {}
    if koil_assessment:
        koil_probability = float(koil_assessment.get("probability", 0)) * 100
        koil_threshold = koil_assessment.get("threshold")
        threshold_text = f"{float(koil_threshold) * 100:.1f}%" if koil_threshold is not None else "unavailable"
        lines.append(
            "KOIL morphology: "
            f"{koil_assessment.get('status', '?')}  "
            f"probability={koil_probability:.1f}%  "
            f"threshold={threshold_text}"
        )
        lines.append("KOIL domain: trained on SIPaKMeD conventional Pap-smear crops; limited CCCID liquid-based positive challenge only, without external specificity.")
    else:
        lines.append("KOIL morphology: not assessed")
    lines.append(f"Uncertainty: {unc.get('level','?')}  entropy={unc.get('entropy','?')} flag={unc.get('flag')}")
    if clinical:
        lines.append(f"Clinical: {clinical.get('bethesda')} | triage={clinical.get('triage','')}")
        lines.append(f"Risk: {clinical.get('risk_level')} | Action: {clinical.get('recommended_action','')}")
    if context:
        lines.append(f"Context: age={context.get('age_years') or 'not entered'}; specimen={context.get('specimen_type', 'unknown')}")
        symptoms = context.get("symptoms") or []
        lines.append(f"Reported symptoms: {', '.join(symptoms) if symptoms else 'none entered'}")
        lines.append("Context fields are report-only and were not used by the image model.")
    if patient:
        lines.append(f"Patient release: {patient.get('release_status', 'unknown')}")
        if patient.get("locked"):
            lines.append(f"Release blockers: {', '.join(patient.get('blockers') or [])}")
        else:
            lines.append(f"Patient: {patient.get('result','')} — {patient.get('action','')}")
    if xai:
        lines.append("XAI: heatmap embedded (base64)")
    lines.append("")
    lines.append("Limitations: research decision support only; not a diagnosis or regulated clinical report.")
    text_block = "\n".join(lines)

    return {
        "ok": True,
        "top": top,
        "analysis": a,
        "report": r,
        "clinical_context": context,
        "text": text_block,
        "xai_embed": xai,
        "export_version": "2.0-research-gated",
        "exported_at": __import__("datetime").datetime.now().isoformat(),
    }


def _pdf_safe(value: Any) -> str:
    return html.escape(str(value if value not in (None, "") else "Not entered"))


def _pdf_image(data_url: Any, width: float, max_height: float):
    """Return a ReportLab image for a bounded data URL, or None."""
    if not isinstance(data_url, str) or not data_url.startswith("data:image/") or "," not in data_url:
        return None
    try:
        from reportlab.platypus import Image as RLImage
        raw = base64.b64decode(data_url.split(",", 1)[1], validate=True)
        if len(raw) > MAX_BYTES:
            return None
        with Image.open(io.BytesIO(raw)) as source:
            source.verify()
        flowable = RLImage(io.BytesIO(raw))
        scale = min(width / flowable.imageWidth, max_height / flowable.imageHeight)
        flowable.drawWidth = flowable.imageWidth * scale
        flowable.drawHeight = flowable.imageHeight * scale
        return flowable
    except Exception:
        return None


@app.post("/api/report/export/pdf")
def report_export_pdf(req: ReportExportReq):
    """Generate a formal, unsigned research pre-screen PDF with explicit release state."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    payload = report_export(req)
    analysis = payload.get("analysis") or {}
    report_data = payload.get("report") or {}
    clinical = report_data.get("layer_clinical") or {}
    patient = report_data.get("layer_patient") or {}
    context = payload.get("clinical_context") or {}
    top = payload.get("top") or {}
    case_id = re.sub(r"[^A-Za-z0-9_.-]", "-", req.case_id or "ANONG-UNASSIGNED")[:80]
    generated = payload.get("exported_at", "")

    stream = io.BytesIO()
    document = SimpleDocTemplate(
        stream, pagesize=A4, rightMargin=17 * mm, leftMargin=17 * mm,
        topMargin=20 * mm, bottomMargin=19 * mm,
        title=f"{case_id} Anong reviewed research pre-screen",
        author="Anong | CerviCo-Pilot",
    )
    styles = getSampleStyleSheet()
    ink = colors.HexColor("#4A3340")
    rose = colors.HexColor("#A84064")
    line = colors.HexColor("#EAD4D3")
    cream = colors.HexColor("#FFF8E9")
    warn = colors.HexColor("#FFF1F3")
    body = ParagraphStyle("AnongBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13, textColor=ink)
    small = ParagraphStyle("AnongSmall", parent=body, fontSize=7.8, leading=10.5, textColor=colors.HexColor("#735E69"))
    title = ParagraphStyle("AnongTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=rose, spaceAfter=5)
    heading = ParagraphStyle("AnongHeading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=rose, spaceBefore=10, spaceAfter=6)
    center_small = ParagraphStyle("AnongCenter", parent=small, alignment=TA_CENTER)

    def p(value: Any, style=body):
        return Paragraph(_pdf_safe(value), style)

    def section_table(rows):
        formatted = [[p(label, small), p(value)] for label, value in rows]
        table = Table(formatted, colWidths=[43 * mm, 116 * mm], hAlign="LEFT")
        table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (0, -1), cream),
            ("GRID", (0, 0), (-1, -1), 0.45, line),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        return table

    def page_frame(canvas: Canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(line)
        canvas.line(17 * mm, 15 * mm, 193 * mm, 15 * mm)
        canvas.setFillColor(colors.HexColor("#735E69"))
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(17 * mm, 10 * mm, "ANONG | RESEARCH PRE-SCREEN | NOT A FINAL DIAGNOSIS")
        canvas.drawRightString(193 * mm, 10 * mm, f"Page {doc.page}")
        canvas.setFillColor(colors.Color(0.66, 0.25, 0.39, alpha=0.07))
        canvas.setFont("Helvetica-Bold", 28)
        canvas.translate(105 * mm, 145 * mm)
        canvas.rotate(35)
        canvas.drawCentredString(0, 0, "RESEARCH USE ONLY")
        canvas.restoreState()

    probability = top.get("prob", clinical.get("confidence", 0))
    try:
        probability_text = f"{float(probability) * 100:.1f}%"
    except (TypeError, ValueError):
        probability_text = str(probability)
    symptom_labels = {
        "intermenstrual_bleeding": "Bleeding between periods",
        "postcoital_bleeding": "Bleeding after sex",
        "postmenopausal_bleeding": "Bleeding after menopause",
        "unusual_discharge": "Unusual or foul-smelling discharge",
        "persistent_pelvic_back_leg_pain": "Persistent pelvic, back, or leg pain",
        "weight_loss_fatigue_appetite_loss": "Unexplained weight loss, fatigue, or appetite loss",
    }
    specimen_labels = {"thinprep_lbc": "ThinPrep / liquid-based cytology", "conventional_pap": "Conventional Pap smear", "unknown": "Unknown"}
    screening_labels = {"never": "Never screened", "within_3_years": "Within 3 years", "3_to_5_years": "3-5 years ago", "over_5_years": "Over 5 years ago", "unknown": "Unknown"}
    symptoms = [symptom_labels.get(item, str(item).replace("_", " ")) for item in context.get("symptoms") or []]
    blockers = patient.get("blockers") or report_data.get("release_gates") or []
    koil = analysis.get("koil_assessment") or {}
    koil_xai = analysis.get("koil_xai") or {}
    koil_evidence = koil.get("evidence") or {}
    koil_locked = koil_evidence.get("locked_test") or {}
    koil_external = koil_evidence.get("external_positive_challenge") or {}

    story = [
        Paragraph("ANONG | CerviCo-Pilot", small),
        Paragraph("Reviewed Cervical Cytology Research Pre-screen", title),
        p(f"Case {case_id} | Generated {generated}", small),
        Spacer(1, 5 * mm),
        Table([[p("DECISION-SUPPORT OUTPUT ONLY. Not a final diagnosis, not an HPV DNA/RNA test, and not a regulated clinical report.")]], colWidths=[159 * mm], style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), warn), ("BOX", (0, 0), (-1, -1), 0.8, rose),
            ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ])),
        Paragraph("Case and clinical context", heading),
        section_table([
            ("Case identifier", case_id),
            ("Age", f"{context.get('age_years')} years" if context.get("age_years") else "Not entered"),
            ("Specimen", specimen_labels.get(context.get("specimen_type"), context.get("specimen_type", "Unknown"))),
            ("Reported symptoms", "; ".join(symptoms + ([context.get("other_symptoms")] if context.get("other_symptoms") else [])) if (symptoms or context.get("other_symptoms")) else "None entered"),
            ("Last screening", screening_labels.get(context.get("last_screening"), context.get("last_screening", "Unknown"))),
            ("HPV laboratory test", f"{context.get('hpv_test', 'not performed')}{'; genotype ' + str(context.get('hpv_genotype')) if context.get('hpv_genotype') else ''}"),
            ("Other risk context", ", ".join(name for name, present in [
                ("prior abnormal result", context.get("prior_abnormal_result")),
                ("immunocompromised", context.get("immunocompromised")),
                ("pregnant", context.get("pregnant")),
            ] if present) or "None entered"),
        ]),
        p("Clinical context is report-only. It was not used to alter the image model prediction.", small),
        Paragraph("AI pre-screen and reviewed interpretation", heading),
        section_table([
            ("AI suggestion", f"{top.get('key', clinical.get('bethesda', 'UNKNOWN'))} ({probability_text})"),
            ("Reviewed category", clinical.get("bethesda", top.get("key", "UNKNOWN"))),
            ("Uncertainty", (analysis.get("uncertainty") or analysis.get("uncertainty_viz") or {}).get("level", "unknown")),
            ("Image quality", clinical.get("quality_status", "unknown")),
            ("Grade XAI", clinical.get("xai_method", "unavailable")),
            ("KOIL morphology", f"{koil.get('status', 'not assessed')} ({float(koil.get('probability', 0)) * 100:.1f}%)" if koil else "Not assessed"),
            ("KOIL locked-test evidence", f"Sensitivity {float(koil_locked.get('sensitivity', 0)) * 100:.1f}%; specificity {float(koil_locked.get('specificity', 0)) * 100:.1f}%; AUROC {float(koil_locked.get('auroc', 0)):.3f}" if koil_locked else "Unavailable"),
            ("CCCID positive challenge", f"{koil_external.get('true_positive', 0)}/{koil_external.get('support_positive', 0)} detected; specificity not estimable" if koil_external else "Unavailable"),
            ("Triage", clinical.get("triage", "Not generated")),
            ("Recommended action", clinical.get("recommended_action", "Not generated")),
        ]),
        Paragraph("Safety and release status", heading),
        section_table([
            ("Clinician review", clinical.get("review_status", "pending")),
            ("Patient-facing release", patient.get("release_status", "blocked")),
            ("Release blockers", ", ".join(blockers) if blockers else "None"),
            ("Symptom safety", clinical.get("context_note", "No context note")),
        ]),
        Paragraph("Image evidence and limitations", title),
    ]

    original_image = _pdf_image(analysis.get("image"), 75 * mm, 68 * mm)
    heatmap_image = _pdf_image(analysis.get("heatmap") or report_data.get("xai_embed"), 75 * mm, 68 * mm)
    koil_heatmap_image = _pdf_image(koil_xai.get("heatmap"), 75 * mm, 68 * mm) if koil_xai.get("ok") is True else None
    if original_image or heatmap_image or koil_heatmap_image:
        cells = []
        if original_image:
            cells.append([original_image, p("Original image", center_small)])
        if heatmap_image:
            cells.append([heatmap_image, p("Class-activation map (post-hoc; not segmentation)", center_small)])
        if koil_heatmap_image:
            cells.append([koil_heatmap_image, p("KOIL-specific Grad-CAM (not HPV proof)", center_small)])
        image_rows = []
        for start in range(0, len(cells), 2):
            pair = cells[start:start + 2]
            if len(pair) == 1:
                pair.append(["", ""])
            image_rows.extend([[cell[0] for cell in pair], [cell[1] for cell in pair]])
        image_table = Table(image_rows, colWidths=[78 * mm, 78 * mm])
        image_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("BOX", (0, 0), (-1, -1), 0.45, line)]))
        story.append(image_table)
    else:
        story.append(p("No embeddable image evidence was supplied to the PDF renderer.", small))
    story.extend([
        Paragraph("Interpretive boundaries", heading),
        p("The grade model estimates cervical cytology morphology. The independent KOIL endpoint was trained on SIPaKMeD conventional Pap-smear crops and challenged on 20 expert-labelled CCCID liquid-based koilocyte images. No endpoint in this system is an HPV DNA/RNA assay or establishes viral genotype, persistence, or infection status."),
        Spacer(1, 3 * mm),
        p("A class-activation map shows image regions that contributed to a model score. It is a post-hoc explanation and must not be presented as a validated nucleus/cell segmentation or causal proof."),
        Spacer(1, 3 * mm),
        p("The system has not completed external clinical validation on Thai ThinPrep cohorts and must not be used for autonomous diagnosis, treatment selection, or reassurance of a symptomatic patient."),
        Paragraph("Workflow record", heading),
        section_table([
            ("Model mode", analysis.get("mode", "unknown")),
            ("Export version", payload.get("export_version", "unknown")),
            ("Generated at", generated),
            ("Report source", report_data.get("source", "controlled template")),
        ]),
        Spacer(1, 6 * mm),
        p("Reviewer name: ____________________________________    License/role: __________________________"),
        Spacer(1, 4 * mm),
        p("Signature: _________________________________________    Date/time: ______________________________"),
        Spacer(1, 6 * mm),
        p("This unsigned export documents a research workflow demonstration. A clinical pilot requires governance, identity and access controls, de-identification, validated signatures, retention policy, and applicable ethics/PDPA approval.", small),
    ])
    document.build(story, onFirstPage=page_frame, onLaterPages=page_frame)
    SERVER_COUNTERS["report_exports"] += 1
    filename = f"{case_id}-anong-research-prescreen.pdf"
    return Response(
        content=stream.getvalue(), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/report/export/html", response_class=HTMLResponse)
def report_export_html(req: ReportExportReq):
    """Server-side demo HTML export suitable for browser print/PDF.

    This is still a prototype report renderer. It is not a signed clinical
    document generator and must not be used to release patient results without
    clinician sign-off and validation.
    """
    payload = report_export(req)
    SERVER_COUNTERS["report_exports"] += 1
    top = payload.get("top") or {}
    report_data = payload.get("report") or {}
    clinical = report_data.get("layer_clinical") or {}
    patient = report_data.get("layer_patient") or {}
    text = payload.get("text", "")
    label = html.escape(str(top.get("key") or clinical.get("bethesda") or "UNKNOWN"))
    prob = top.get("prob", clinical.get("confidence", 0))
    try:
        prob_txt = f"{float(prob) * 100:.1f}%"
    except Exception:
        prob_txt = html.escape(str(prob))
    rows = [
        ("AI suggestion", f"{label} ({prob_txt})"),
        ("Clinical triage", html.escape(str(clinical.get("triage", "-")))),
        ("Recommended action", html.escape(str(clinical.get("recommended_action", "-")))),
        ("Patient release", html.escape(str(patient.get("release_status", "not generated")))),
        ("Release blockers", html.escape(", ".join(patient.get("blockers") or [])) or "None"),
        ("Patient layer", html.escape(str(patient.get("result") or "Not released"))),
        ("Patient action", html.escape(str(patient.get("action", "-")))),
        ("Export version", html.escape(str(payload.get("export_version", "-")))),
        ("Exported at", html.escape(str(payload.get("exported_at", "-")))),
    ]
    row_html = "\n".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)
    body = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CerviCo-Pilot Demo Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 820px; margin: 36px auto; color: #111; line-height: 1.55; }}
    h1 {{ color: #0e7490; margin-bottom: 4px; }}
    .muted {{ color: #666; font-size: 12px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
    th, td {{ border: 1px solid #ddd; padding: 10px; vertical-align: top; text-align: left; }}
    th {{ width: 190px; background: #f2f6f7; }}
    pre {{ white-space: pre-wrap; border: 1px solid #ddd; padding: 14px; border-radius: 8px; background: #fafafa; }}
    .warn {{ border: 1px solid #c0492f; color: #8b2d1d; padding: 12px; border-radius: 8px; background: #fff7f4; }}
  </style>
</head>
<body>
  <h1>CerviCo-Pilot Clinical Pre-screen</h1>
  <p class="muted">Server-side HTML export for demo print/PDF. Decision-support only.</p>
  <div class="warn">This is not a final diagnosis, not an HPV DNA/RNA test, and not a regulated clinical report. Clinician sign-off is required.</div>
  <table>{row_html}</table>
  <h2>Export text</h2>
  <pre>{html.escape(text)}</pre>
</body>
</html>"""
    return HTMLResponse(body)


@app.post("/api/demo_script")
def demo_script():
    """Return text scripts for demo video / host simulation docs."""
    return {
        "title": "CervicalAI Demo Script (2-3 min + 5-7 min)",
        "short": [
            "1. แนะนำปัญหา: มะเร็งปากมดลูกพบมากในไทย, loss-to-follow-up สูงเพราะรายงานเข้าใจยาก",
            "2. โชว์ภาพตัวอย่าง → วิเคราะห์ → แสดง 4-class grade + independent KOIL morphology + uncertainty + heatmap",
            "3. สลับ heatmap modes (Original/Heat/Blend/Side) + ปรับ live alpha/colormap",
            "4. คลิก contour เปลี่ยนคลาส → ส่ง edit ไปเซิร์ฟเวอร์ (human-in-loop demo)",
            "5. กดสร้างรายงาน → แสดง clinical + patient layer + แก้ไขใน editor",
            "6. Export JSON / Copy / Print → เน้น embed XAI",
            "7. Stress: กดปุ่ม 50 loops → แสดง avg latency + p95",
        ],
        "full": [
            "OPEN: เปิดเว็บ http://localhost:8003 (หรือ host)",
            "UPLOAD: ใช้ภาพตัวอย่าง หรือ drag ภาพ ThinPrep จริง",
            "ANALYZE: กดวิเคราะห์ → ดู 4-class grade probabilities + independent KOIL morphology score",
            "UNCERTAINTY: อธิบาย gauge สี + entropy + flag (แดง=ไม่มั่นใจ)",
            "XAI: สลับโหมด heatmap, ปรับ alpha slider, เปลี่ยน colormap → กด Apply Live",
            "CONTOUR: คลิก contour แต่ละอันเพื่อสลับคลาส (แดง=ผิดปกติ), กดส่งแก้ไข",
            "REPORT: กดสร้างรายงาน → แก้ไขชั้น clinical/patient ใน textarea → Apply",
            "EXPORT: Export JSON (มี xai_embed), Copy ข้อความ, Print/PDF",
            "BATCH: สร้างชุดภาพจำลอง 8 ภาพ → วิเคราะห์ batch พร้อมกัน",
            "STRESS: กด Stress 50/100 loops → แสดง timing stats (avg/p95)",
            "CLOSE: เน้น 'AI คัดกรองเบื้องต้น ต้องแพทย์ยืนยัน' + guardrails",
        ],
        "host_notes": "ใช้ภาพจริงจาก models/xai_heatmaps ถ้ามี / หรือ synthetic จากปุ่ม GenFake. อย่าลืมบอกกรรมการว่า contour เป็นจำลอง",
    }


def _triage_rule(bethesda: str, prob: float, koil: bool, uncertain: bool = False) -> str:
    """Conservative research-workflow triage without patient-specific instructions."""
    if uncertain:
        return "Do not release automatically; obtain independent review and consider recapture."
    if bethesda in ("HSIL", "SCC"):
        return "Prioritize confirmatory specialist assessment under applicable clinical guidance."
    if bethesda == "LSIL":
        return "Arrange guideline-directed follow-up; HPV testing remains a separate test."
    if koil:
        return "Review the independent KOIL morphology finding; HPV DNA/RNA testing remains separate and may be considered under applicable guidance."
    return "Continue screening according to the applicable program and individual clinical context."


def _clinical_action(bethesda: str, koil: bool, uncertain: bool) -> str:
    if uncertain:
        return "Independent expert review; consider repeat slide preparation or image capture."
    if bethesda == "SCC":
        return "Urgent specialist assessment and confirmatory diagnostic work-up."
    if bethesda == "HSIL":
        return "Prompt specialist referral for confirmatory assessment."
    if bethesda == "LSIL":
        return "Guideline-directed follow-up; consider separate HPV testing when indicated."
    if koil:
        return "Expert review of the KOIL morphology finding; separate HPV testing when clinically indicated."
    return "Continue guideline-based routine screening."


def _patient_layer(bethesda: str, prob: float, koil: bool, uncertain: bool) -> dict:
    if uncertain:
        return {
            "result": "The screening image requires additional review.",
            "action": "Wait for confirmation from the responsible clinical service.",
            "why": "The model did not produce a sufficiently certain result.",
            "simple": "Additional professional review is required.",
        }
    if bethesda in ("HSIL", "SCC"):
        return {
            "result": "The reviewed screening category indicates high-grade abnormality.",
            "action": "Follow the responsible clinician's confirmatory referral plan.",
            "why": "Cytology screening alone does not establish a final diagnosis.",
            "simple": "Prompt confirmatory assessment is recommended.",
        }
    if bethesda == "LSIL":
        return {
            "result": "The reviewed screening category indicates low-grade cellular change.",
            "action": "Follow the clinician's guideline-directed follow-up plan.",
            "why": "HPV status cannot be determined from this image analysis.",
            "simple": "Clinical follow-up is recommended.",
        }
    if koil:
        return {
            "result": "The reviewed grade is not high-grade, with a separate KOIL morphology finding.",
            "action": "Obtain expert review and separate testing when clinically indicated.",
            "why": "Koilocytic morphology can be associated with HPV-related cellular change but does not confirm HPV infection.",
            "simple": "Additional review is required.",
        }
    return {
        "result": "The reviewed preliminary screening category is NILM.",
        "action": "Continue screening according to the applicable program and clinician advice.",
        "why": "This reviewed pre-screen does not replace routine clinical screening processes.",
        "simple": "Continue guideline-based screening.",
    }


@app.get("/")
def index():
    idx = WEB / "index.html"
    if idx.exists():
        return FileResponse(str(idx))
    raise HTTPException(status_code=404, detail="web demo not found")


@app.exception_handler(404)
async def spa_fallback(request: Request, exc):
    if request.url.path.startswith("/api"):
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    idx = WEB / "index.html"
    if idx.exists():
        return FileResponse(str(idx))
    return JSONResponse({"detail": "Not Found"}, status_code=404)


if WEB.exists():
    app.mount("/", StaticFiles(directory=str(WEB), html=True), name="web")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

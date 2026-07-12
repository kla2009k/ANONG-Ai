#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CervicalAI — Generate 50+ Sample Outputs (inference + XAI + reports)

Creates a large corpus of synthetic demo outputs for:
- FULL_DEMO_GUIDE.md consumption
- Video script references
- Stress test artifacts
- Bulk gallery / comparison

Generates:
  artifacts/samples/analyze_000.json ... analyze_049.json (or more)
  artifacts/samples/report_000.json ...
  artifacts/samples/gallery_index.json
  artifacts/samples/summary_stats.json

Also optionally POSTs to live server if --live.
"""
from __future__ import annotations
import argparse
import base64
import io
import json
import pathlib
import time
from datetime import datetime
from typing import List, Dict, Any

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).parent.parent
ART = ROOT / "artifacts"
SAMPLES = ART / "samples"
SAMPLES.mkdir(parents=True, exist_ok=True)

CLASSES = ["NILM", "LSIL", "HSIL", "SCC", "KOIL"]


def make_varied_image(idx: int, size: int = 192) -> str:
    rng = np.random.default_rng(424242 + idx)
    h = int(size * (0.6 + rng.random() * 0.35))
    w = size
    # base tone varies to simulate stain variation
    base = rng.integers(160, 245)
    arr = np.full((h, w, 3), base, dtype=np.uint8)
    # random stain tint
    tint = rng.integers(-18, 18, 3)
    arr = np.clip(arr.astype(int) + tint, 0, 255).astype(np.uint8)
    # nuclei / dark features
    n = rng.integers(4, 20)
    for _ in range(n):
        cx = rng.integers(6, w-6)
        cy = rng.integers(6, h-6)
        r = rng.integers(2, 10)
        y, x = np.ogrid[:h, :w]
        mask = (x - cx)**2 + (y - cy)**2 <= r*r
        shade = rng.integers(30, 100)
        arr[mask] = np.clip(arr[mask].astype(int) - shade, 0, 255).astype(np.uint8)
    # chromatin texture
    for _ in range(rng.integers(30, 160)):
        x = rng.integers(0, w)
        y = rng.integers(0, h)
        arr[y, x] = np.clip(arr[y, x].astype(int) - rng.integers(8, 28), 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def heuristic_demo_analyze(b64: str, idx: int) -> Dict[str, Any]:
    """Pure client-side heuristic (matches server demo mode) for offline generation.
    Biased per idx to produce varied class distribution for demo richness.
    """
    raw = base64.b64decode(b64.split(",")[1])
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    arr = np.array(img)
    gray = np.mean(arr, axis=2)
    inv = 255 - gray
    area = float((inv > 128).sum()) / inv.size
    gx = np.abs(np.diff(gray, axis=1)).mean() if gray.shape[1] > 1 else 0.0
    gy = np.abs(np.diff(gray, axis=0)).mean() if gray.shape[0] > 1 else 0.0
    tex = float(gx + gy)
    seed = (idx * 7919) % 1000 / 1000.0

    # base scores
    s = np.array([0.55, 0.48, 0.28, 0.18, 0.38], dtype=np.float32)

    # drive class variety by idx bands
    band = (idx // 8) % 6
    if band == 0:
        s[0] += 0.9  # NILM heavy
    elif band == 1:
        s[1] += 1.1  # LSIL
    elif band == 2:
        s[2] += 1.3; s[4] += 0.6  # HSIL + KOIL
    elif band == 3:
        s[3] += 1.4  # SCC
    elif band == 4:
        s[4] += 1.35; s[1] += 0.5  # KOIL + LSIL
    else:
        s[2] += 0.9; s[1] += 0.4  # HSIL mix

    # feature nudges
    s[0] += 0.7 * (1 - min(area * 2.8, 1))
    s[1] += 0.85 * min(area * 1.9, 1)
    s[2] += 1.0 * min(tex / 55, 1) * min(area * 1.8, 1)
    s[3] += 0.75 * min(tex / 75, 1)
    s[4] += 0.65 * (0.55 if area > 0.11 else 0.0)

    # seeded jitter
    for i in range(5):
        s[i] += 0.18 * ((seed * (i + 1)) % 1.0)

    p = np.exp(s) / np.exp(s).sum()
    cls = [{"key": k, "prob": round(float(pp), 4)} for k, pp in zip(CLASSES, p)]
    cls.sort(key=lambda d: -d["prob"])
    top = cls[0]
    low = top["prob"] < 0.35
    koil = any((d["key"] == "KOIL" and d["prob"] > 0.20) for d in cls[:2])
    ent = round(float(-sum(x["prob"] * np.log(x["prob"] + 1e-8) for x in cls)), 4)
    unc = {"entropy": ent, "top_std": round(0.07 + (0.13 if low else 0.0), 4), "flag": bool(low), "level": "high" if low else ("med" if ent > 1.02 else "low")}

    # fake heatmap (spotlight)
    g = (gray - gray.min()) / (gray.max() - gray.min() + 1e-6)
    spot = ((1.0 - g) ** 1.4 * 255).astype(np.uint8)
    heat = np.zeros_like(arr)
    # simple jet-ish
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            v = spot[i, j] / 255.0
            r = int(128 + 127 * np.sin((v-0.5)*3.14*1.5))
            g_ = int(128 + 127 * np.sin((v-0.5)*3.14*2.2))
            b = int(200 - 150 * v)
            heat[i, j] = [max(0, min(255, r)), max(0, min(255, g_)), max(0, min(255, b))]
    # overlay
    overlay = (0.55 * arr + 0.45 * heat).astype(np.uint8)
    hbuf = io.BytesIO()
    Image.fromarray(overlay).save(hbuf, "PNG")
    heatmap = "data:image/png;base64," + base64.b64encode(hbuf.getvalue()).decode("ascii")

    # fake contours
    contours = []
    rng = np.random.default_rng(12345 + idx)
    for ci in range(5):
        cx = int(arr.shape[1] * (0.25 + 0.5 * rng.random()))
        cy = int(arr.shape[0] * (0.25 + 0.5 * rng.random()))
        r = int(min(arr.shape[1], arr.shape[0]) * (0.03 + 0.04 * rng.random()))
        pts = [[cx + int(r*np.cos(a)), cy + int(r*np.sin(a))] for a in np.linspace(0, 2*np.pi, 10, endpoint=False)]
        cidx = int(np.clip(["NILM","LSIL","HSIL","SCC","KOIL"].index(top["key"]) + rng.integers(-1, 2), 0, 4))
        contours.append({"id": f"c{ci}", "points": pts, "class": CLASSES[cidx], "confidence": round(0.6 + rng.random()*0.3, 3), "editable": True})

    return {
        "mode": "demo",
        "classification_mode": "demo",
        "quality": {"ok": True, "issues": [], "blur": round(float(np.var(np.gradient(gray.astype(np.float32)))), 1), "brightness": round(float(gray.mean()), 1)},
        "low_confidence": low,
        "conf_threshold": 0.35,
        "classification": cls,
        "top": top,
        "koilocyte": bool(koil),
        "uncertainty": unc,
        "uncertainty_viz": unc,
        "heatmap": heatmap,
        "contours": contours,
        "disclaimer": "เครื่องมือคัดกรองเบื้องต้นด้วย AI — ต้องให้แพทย์ยืนยัน ไม่ใช่การวินิจฉัย",
    }


def make_report(analysis: Dict[str, Any]) -> Dict[str, Any]:
    top = analysis.get("top", {})
    bethesda = top.get("key", "NILM")
    prob = float(top.get("prob", 0.0))
    koil = bool(analysis.get("koilocyte"))
    uncf = bool((analysis.get("uncertainty_viz") or analysis.get("uncertainty") or {}).get("flag"))
    clinical = {
        "bethesda": bethesda,
        "confidence": round(prob, 3),
        "koilocyte": koil,
        "uncertainty_flag": uncf,
        "triage": "ส่ง Colposcopy ด่วน + แนะนำ HPV co-test (16/18/52/58) + ตรวจชิ้นเนื้อ" if bethesda in ("HSIL","SCC") else ("พบลักษณะ koilocyte (HPV) — ส่ง HPV genotyping + ติดตาม 6 เดือน" if (bethesda=="LSIL" and koil) else ("ติดตามตาม guideline (6-12 เดือน)" if bethesda=="LSIL" else ("พบลักษณะ koilocyte เฉพาะ — ส่ง HPV test" if bethesda=="KOIL" else "ผลปกติ — ตรวจตามโปรแกรม (3-5 ปี)"))),
        "risk_level": "HIGH" if bethesda in ("HSIL","SCC") else ("MODERATE" if bethesda in ("LSIL","KOIL") else "LOW"),
        "recommended_action": "Urgent colposcopy+biopsy" if bethesda=="SCC" else ("Colposcopy + directed biopsy 4-6wk" if bethesda=="HSIL" else ("HPV test + repeat 6-12mo" if bethesda=="LSIL" else ("HPV test" if bethesda=="KOIL" else "Routine screening"))),
        "note": "AI pre-screen (demo) — ต้องแพทย์ลงนามก่อนปล่อยผลผู้ป่วย",
    }
    patient = {
        "result": "พบเซลล์ผิดปกติระดับสูง" if bethesda in ("HSIL","SCC") else ("พบเซลล์ผิดปกติระดับต่ำ" if bethesda=="LSIL" else ("เห็นเซลล์ที่ถูกไวรัส HPV ทำ" if bethesda=="KOIL" else "ผลปกติ")),
        "action": "ควรพบแพทย์โดยเร็ว (ภายใน 1-2 สัปดาห์)" if bethesda in ("HSIL","SCC") else ("ส่งตรวจ HPV + มาตรวจซ้ำตามนัด (6-12 เดือน)" if bethesda in ("LSIL","KOIL") else "ตรวจคัดกรองต่อเนื่องทุก 3-5 ปี"),
        "why": "เซลล์มีรูปร่างผิดปกติชัด อาจเป็นระยะก่อนมะเร็งหรือมะเร็งระยะต้น" if bethesda in ("HSIL","SCC") else ("ส่วนใหญ่หายได้เอง แต่บางส่วนอาจพัฒนาได้ ต้องเฝ้าดู" if bethesda=="LSIL" else ("HPV บางสายพันธุ์ (โดยเฉพาะ 52/58 ในไทย) เกี่ยวข้องกับมะเร็ง" if bethesda=="KOIL" else "ไม่พบลักษณะผิดปกติชัดเจนในภาพนี้")),
        "simple": "พบเซลล์ไม่ปกติแบบรุนแรง ต้องรีบไปหาหมอตรวจต่อ" if bethesda in ("HSIL","SCC") else ("มีเซลล์ผิดปกติเล็กน้อย ต้องตรวจและติดตาม" if bethesda=="LSIL" else ("พบร่องรอยการติดเชื้อ HPV ในเซลล์ ต้องตรวจเพิ่ม" if bethesda=="KOIL" else "ปกติดีค่ะ มาตรวจตามโปรแกรมปกติ")),
    }
    return {"layer_clinical": clinical, "layer_patient": patient, "source": "demo-template", "disclaimer": "รายงานนี้เป็นผลจาก AI คัดกรองเบื้องต้น ต้องให้แพทย์ยืนยัน ไม่ใช่การวินิจฉัย"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=60, help="Number of samples to generate (aim >50)")
    ap.add_argument("--live", action="store_true", help="Also POST to running server at --url")
    ap.add_argument("--url", default="http://127.0.0.1:8003")
    ap.add_argument("--with-xai", action="store_true", default=True)
    args = ap.parse_args()

    print(f"[gen50] generating {args.count} samples (live={args.live})")
    items: List[Dict[str, Any]] = []
    t0 = time.time()
    for i in range(args.count):
        b64 = make_varied_image(i)
        if args.live:
            import requests
            try:
                r = requests.post(f"{args.url}/api/analyze", json={"image": b64}, timeout=30)
                aj = r.json() if r.ok else {"error": r.text[:200]}
            except Exception as e:
                aj = {"error": str(e)}
            try:
                rr = requests.post(f"{args.url}/api/report", json={"image": b64, "analysis": aj}, timeout=20)
                rj = rr.json() if rr.ok else {"error": rr.text[:200]}
            except Exception as e:
                rj = {"error": str(e)}
        else:
            aj = heuristic_demo_analyze(b64, i)
            rj = make_report(aj)
        rec = {
            "idx": i,
            "image_b64": b64,
            "analysis": aj,
            "report": rj,
            "ts": datetime.now().isoformat(timespec="seconds"),
        }
        # write individual
        (SAMPLES / f"analyze_{i:03d}.json").write_text(json.dumps({"analysis": aj}, indent=2, ensure_ascii=False), encoding="utf-8")
        (SAMPLES / f"report_{i:03d}.json").write_text(json.dumps({"report": rj}, indent=2, ensure_ascii=False), encoding="utf-8")
        items.append(rec)
        if (i+1) % 10 == 0:
            print(f"  ... {i+1}/{args.count}")

    # index + stats
    index = {"count": len(items), "generated_at": datetime.now().isoformat(), "items": [{"idx": it["idx"], "top": it["analysis"].get("top"), "koil": it["analysis"].get("koilocyte"), "unc_flag": (it["analysis"].get("uncertainty_viz") or it["analysis"].get("uncertainty") or {}).get("flag")} for it in items]}
    (SAMPLES / "gallery_index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    # summary stats
    tops = [it["analysis"].get("top", {}).get("key") for it in items]
    flags = sum(1 for it in items if (it["analysis"].get("uncertainty_viz") or it["analysis"].get("uncertainty") or {}).get("flag"))
    koils = sum(1 for it in items if it["analysis"].get("koilocyte"))
    stats = {
        "count": len(items),
        "class_dist": {c: tops.count(c) for c in CLASSES},
        "uncertainty_flags": flags,
        "koilocyte_flags": koils,
        "elapsed_sec": round(time.time() - t0, 2),
    }
    (SAMPLES / "summary_stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")

    # big bundle
    (ART / "samples_50plus_bundle.json").write_text(json.dumps({"count": len(items), "items": items}, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[gen50] DONE {len(items)} samples")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    print(f"[gen50] bundle: {ART / 'samples_50plus_bundle.json'}")


if __name__ == "__main__":
    main()

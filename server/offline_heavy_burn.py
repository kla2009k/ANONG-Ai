#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CervicalAI — OFFLINE HEAVY BURN (100+ inference + XAI + reports) — NO TORCH REQUIRED

Simulates the exact same output schema as the live /api/analyze + /api/report.
Generates artifacts for:
  - stress test report
  - FULL_DEMO_GUIDE.md references
  - 50+ bulk sample gallery

Run:
  python offline_heavy_burn.py --n 150 --with-xai --with-reports

Outputs (under artifacts/):
  offline_burn_*.json (full run log + samples)
  offline_reports_*.json (bulk 2-layer reports)
  offline_summary.json
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
ART.mkdir(parents=True, exist_ok=True)

CLASSES = ["NILM", "LSIL", "HSIL", "SCC", "KOIL"]


def synth_image(idx: int, size: int = 176) -> str:
    rng = np.random.default_rng(202600 + idx)
    h = int(size * (0.62 + rng.random()*0.28))
    w = size
    base = rng.integers(158, 248)
    arr = np.full((h, w, 3), base, dtype=np.uint8)
    tint = rng.integers(-22, 22, 3)
    arr = np.clip(arr.astype(int) + tint, 0, 255).astype(np.uint8)
    n = rng.integers(5, 19)
    for _ in range(n):
        cx, cy = rng.integers(6, w-6), rng.integers(6, h-6)
        r = rng.integers(2, 10)
        y, x = np.ogrid[:h, :w]
        mask = (x - cx)**2 + (y - cy)**2 <= r*r
        shade = rng.integers(32, 98)
        arr[mask] = np.clip(arr[mask].astype(int) - shade, 0, 255).astype(np.uint8)
    for _ in range(rng.integers(35, 150)):
        x, y = rng.integers(0, w), rng.integers(0, h)
        arr[y, x] = np.clip(arr[y, x].astype(int) - rng.integers(7, 30), 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def offline_analyze(b64: str, idx: int, want_heatmap: bool = True) -> Dict[str, Any]:
    raw = base64.b64decode(b64.split(",")[1])
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    arr = np.array(img)
    gray = np.mean(arr, axis=2).astype(np.float32)
    inv = 255 - gray
    area = float((inv > 130).sum()) / inv.size
    gx = float(np.abs(np.diff(gray, axis=1)).mean()) if gray.shape[1] > 1 else 0.0
    gy = float(np.abs(np.diff(gray, axis=0)).mean()) if gray.shape[0] > 1 else 0.0
    tex = gx + gy
    seed = ((idx * 9137) ^ int(gray.mean()*17)) % 1000000 / 1000000.0

    band = (idx // 7) % 6
    s = np.array([0.52, 0.46, 0.27, 0.17, 0.36], dtype=np.float32)
    if band == 0: s[0] += 0.95
    elif band == 1: s[1] += 1.15
    elif band == 2: s[2] += 1.35; s[4] += 0.55
    elif band == 3: s[3] += 1.45
    elif band == 4: s[4] += 1.40; s[1] += 0.45
    else: s[2] += 0.95; s[1] += 0.35

    s[0] += 0.75 * (1 - min(area * 2.7, 1))
    s[1] += 0.90 * min(area * 1.85, 1)
    s[2] += 1.05 * min(tex / 52, 1) * min(area * 1.7, 1)
    s[3] += 0.78 * min(tex / 72, 1)
    s[4] += 0.68 * (0.52 if area > 0.105 else 0.0)
    for i in range(5):
        s[i] += 0.16 * ((seed * (i+1)) % 1.0)

    p = np.exp(s) / np.exp(s).sum()
    cls = [{"key": k, "prob": round(float(pp), 4)} for k, pp in zip(CLASSES, p)]
    cls.sort(key=lambda d: -d["prob"])
    top = cls[0]
    low = top["prob"] < 0.35
    koil = any((d["key"]=="KOIL" and d["prob"]>0.19) for d in cls[:2])
    ent = round(float(-sum(x["prob"]*np.log(x["prob"]+1e-8) for x in cls)), 4)
    unc = {"entropy": ent, "top_std": round(0.065 + (0.135 if low else 0.0), 4), "flag": bool(low),
           "level": "high" if low else ("med" if ent > 1.0 else "low")}

    heatmap = None
    if want_heatmap:
        g = (gray - gray.min()) / (gray.max() - gray.min() + 1e-6)
        spot = ((1.0 - g) ** 1.35 * 255).astype(np.uint8)
        heat = np.zeros_like(arr)
        for i in range(heat.shape[0]):
            for j in range(heat.shape[1]):
                v = spot[i, j] / 255.0
                r = int(125 + 130 * np.sin((v-0.5)*3.14*1.55))
                gg = int(125 + 130 * np.sin((v-0.5)*3.14*2.15))
                b = int(205 - 155 * v)
                heat[i, j] = [max(0,min(255,r)), max(0,min(255,gg)), max(0,min(255,b))]
        overlay = (0.52 * arr + 0.48 * heat).astype(np.uint8)
        hbuf = io.BytesIO(); Image.fromarray(overlay).save(hbuf, "PNG")
        heatmap = "data:image/png;base64," + base64.b64encode(hbuf.getvalue()).decode("ascii")

    # contours
    contours = []
    rng = np.random.default_rng(7713 + idx)
    for ci in range(6):
        cx = int(arr.shape[1] * (0.22 + 0.56 * rng.random()))
        cy = int(arr.shape[0] * (0.22 + 0.56 * rng.random()))
        r = int(min(arr.shape[1], arr.shape[0]) * (0.028 + 0.042 * rng.random()))
        pts = [[cx + int(r*np.cos(a)), cy + int(r*np.sin(a))] for a in np.linspace(0, 2*np.pi, 9, endpoint=False)]
        cidx = int(np.clip(CLASSES.index(top["key"]) + rng.integers(-1, 2), 0, 4))
        contours.append({"id": f"c{ci}", "points": pts, "class": CLASSES[cidx],
                         "confidence": round(0.58 + rng.random()*0.32, 3), "editable": True})

    quality = {"ok": True, "issues": [], "blur": round(float(np.var(np.gradient(gray))), 1),
               "brightness": round(float(gray.mean()), 1)}

    return {
        "mode": "demo",
        "classification_mode": "demo",
        "quality": quality,
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


def offline_report(analysis: Dict[str, Any]) -> Dict[str, Any]:
    top = analysis.get("top", {})
    bethesda = top.get("key", "NILM")
    prob = float(top.get("prob", 0.0))
    koil = bool(analysis.get("koilocyte"))
    uncf = bool((analysis.get("uncertainty_viz") or analysis.get("uncertainty") or {}).get("flag"))
    clinical = {
        "bethesda": bethesda, "confidence": round(prob, 3), "koilocyte": koil, "uncertainty_flag": uncf,
        "triage": ("ส่ง Colposcopy ด่วน + แนะนำ HPV co-test (16/18/52/58)" if bethesda in ("HSIL","SCC")
                   else ("พบลักษณะ koilocyte (HPV) — ส่ง HPV genotyping + ติดตาม 6 เดือน" if (bethesda=="LSIL" and koil)
                   else ("ติดตามตาม guideline (6-12 เดือน)" if bethesda=="LSIL"
                   else ("พบลักษณะ koilocyte เฉพาะ — ส่ง HPV test" if bethesda=="KOIL"
                   else "ผลปกติ — ตรวจตามโปรแกรม (3-5 ปี)")))),
        "risk_level": "HIGH" if bethesda in ("HSIL","SCC") else ("MODERATE" if bethesda in ("LSIL","KOIL") else "LOW"),
        "recommended_action": ("Urgent colposcopy+biopsy" if bethesda=="SCC" else
                               ("Colposcopy + directed biopsy 4-6wk" if bethesda=="HSIL" else
                                ("HPV test + repeat 6-12mo" if bethesda=="LSIL" else
                                 ("HPV test" if bethesda=="KOIL" else "Routine screening")))),
        "note": "AI pre-screen (offline burn) — ต้องแพทย์ลงนามก่อนปล่อยผลผู้ป่วย",
    }
    patient = {
        "result": ("พบเซลล์ผิดปกติระดับสูง" if bethesda in ("HSIL","SCC") else
                   ("พบเซลล์ผิดปกติระดับต่ำ" if bethesda=="LSIL" else
                    ("เห็นเซลล์ที่ถูกไวรัส HPV ทำ" if bethesda=="KOIL" else "ผลปกติ"))),
        "action": ("ควรพบแพทย์โดยเร็ว (ภายใน 1-2 สัปดาห์)" if bethesda in ("HSIL","SCC") else
                   ("ส่งตรวจ HPV + มาตรวจซ้ำตามนัด (6-12 เดือน)" if bethesda in ("LSIL","KOIL") else
                    "ตรวจคัดกรองต่อเนื่องทุก 3-5 ปี")),
        "why": ("เซลล์มีรูปร่างผิดปกติชัด อาจเป็นระยะก่อนมะเร็งหรือมะเร็งระยะต้น" if bethesda in ("HSIL","SCC") else
                ("ส่วนใหญ่หายได้เอง แต่บางส่วนอาจพัฒนาได้ ต้องเฝ้าดู" if bethesda=="LSIL" else
                 ("HPV บางสายพันธุ์ (โดยเฉพาะ 52/58 ในไทย) เกี่ยวข้องกับมะเร็ง" if bethesda=="KOIL" else
                  "ไม่พบลักษณะผิดปกติชัดเจนในภาพนี้"))),
        "simple": ("พบเซลล์ไม่ปกติแบบรุนแรง ต้องรีบไปหาหมอตรวจต่อ" if bethesda in ("HSIL","SCC") else
                   ("มีเซลล์ผิดปกติเล็กน้อย ต้องตรวจและติดตาม" if bethesda=="LSIL" else
                    ("พบร่องรอยการติดเชื้อ HPV ในเซลล์ ต้องตรวจเพิ่ม" if bethesda=="KOIL" else
                     "ปกติดีค่ะ มาตรวจตามโปรแกรมปกติ"))),
    }
    return {"layer_clinical": clinical, "layer_patient": patient, "source": "offline-burn-template",
            "disclaimer": "รายงานนี้เป็นผลจาก AI คัดกรองเบื้องต้น ต้องให้แพทย์ยืนยัน ไม่ใช่การวินิจฉัย"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=130, help="Number of inference loops")
    ap.add_argument("--with-xai", action="store_true", default=True)
    ap.add_argument("--with-reports", action="store_true", default=True)
    args = ap.parse_args()

    print(f"[offline_burn] n={args.n} xai={args.with_xai} reports={args.with_reports}")
    t0 = time.time()
    records = []
    reports = []
    latencies = []
    for i in range(args.n):
        b64 = synth_image(i)
        t1 = time.time()
        a = offline_analyze(b64, i, want_heatmap=args.with_xai)
        lat = (time.time() - t1) * 1000
        latencies.append(lat)
        rec = {"idx": i, "analysis": a, "lat_ms": round(lat, 2)}
        if args.with_reports:
            r = offline_report(a)
            rec["report"] = r
            reports.append(r)
        records.append(rec)
        if (i+1) % 25 == 0:
            print(f"  ... {i+1}/{args.n}  avg={(sum(latencies)/len(latencies)):.1f}ms")

    total_ms = (time.time() - t0) * 1000
    l = sorted(latencies)
    def pct(p):
        if not l: return 0
        return l[max(0, min(len(l)-1, int(p*(len(l)-1))))]
    summary = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "n": args.n,
        "ok": args.n,
        "fail": 0,
        "total_ms": round(total_ms, 1),
        "latencies": {
            "avg_ms": round(sum(latencies)/len(latencies), 2),
            "p50_ms": round(pct(0.50), 2),
            "p95_ms": round(pct(0.95), 2),
            "p99_ms": round(pct(0.99), 2),
            "max_ms": round(max(latencies), 2),
        },
        "with_xai": args.with_xai,
        "with_reports": args.with_reports,
        "class_dist": {c: sum(1 for r in records if r["analysis"]["top"]["key"]==c) for c in CLASSES},
        "uncertainty_flags": sum(1 for r in records if r["analysis"]["uncertainty_viz"]["flag"]),
        "koilocyte_flags": sum(1 for r in records if r["analysis"]["koilocyte"]),
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = ART / f"offline_burn_{ts}.json"
    out.write_text(json.dumps({"summary": summary, "records": records}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[offline_burn] wrote {out}")

    if reports:
        rj = ART / f"offline_reports_{ts}.json"
        rj.write_text(json.dumps({"count": len(reports), "items": reports}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[offline_burn] wrote {rj} ({len(reports)} reports)")

    (ART / "offline_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== OFFLINE HEAVY BURN SUMMARY ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"elapsed_total={summary['total_ms']}ms")


if __name__ == "__main__":
    main()

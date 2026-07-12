#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CervicalAI — HEAVY STRESS + XAI BURN (100+ inference + XAI + reports)

Max token burn end-to-end demo stress test.
Runs 100-200+ analyze calls with heatmap, uncertainty, then bulk reports.

Usage:
  python heavy_stress_burn.py --n 150 --with-xai --with-reports --url http://127.0.0.1:8003
  python heavy_stress_burn.py --n 100 --burst --concurrency 8

Outputs:
  - artifacts/stress_burn_*.json (full results + latencies)
  - artifacts/bulk_reports_*.json (50+ full 2-layer reports)
  - Console summary with p50/p95/p99
"""
from __future__ import annotations
import argparse
import asyncio
import base64
import io
import json
import pathlib
import statistics
import time
from datetime import datetime
from typing import List, Dict, Any

import aiohttp
from PIL import Image
import numpy as np

ROOT = pathlib.Path(__file__).parent.parent
ART = ROOT / "artifacts"
ART.mkdir(parents=True, exist_ok=True)

CLASSES = ["NILM", "LSIL", "HSIL", "SCC", "KOIL"]


def make_cytology_like(size: int = 180, seed: int | None = None) -> str:
    """Generate varied synthetic cytology-like PNG (data URL)."""
    rng = np.random.default_rng(seed)
    h = int(size * (0.65 + rng.random() * 0.2))
    w = size
    arr = rng.integers(165, 255, (h, w, 3), dtype=np.uint8)
    # nuclei-like dark blobs with variable count/size
    n_blobs = rng.integers(5, 18)
    for _ in range(n_blobs):
        cx = rng.integers(8, w-8)
        cy = rng.integers(8, h-8)
        r = rng.integers(2, 11)
        y, x = np.ogrid[:h, :w]
        mask = (x - cx)**2 + (y - cy)**2 <= r*r
        shade = rng.integers(35, 95)
        arr[mask] = np.clip(arr[mask].astype(int) - shade, 0, 255).astype(np.uint8)
    # texture speckles
    for _ in range(rng.integers(40, 140)):
        x = rng.integers(0, w)
        y = rng.integers(0, h)
        arr[y, x] = np.clip(arr[y, x].astype(int) - rng.integers(10, 35), 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return "data:image/png;base64," + b64


async def one_analyze(session: aiohttp.ClientSession, base_url: str, img: str, want_heat: bool) -> Dict[str, Any]:
    t0 = time.time()
    try:
        async with session.post(f"{base_url}/api/analyze",
                                json={"image": img},
                                timeout=aiohttp.ClientTimeout(total=45)) as resp:
            j = await resp.json()
            ms = (time.time() - t0) * 1000
            return {"ok": resp.status == 200, "ms": ms, "result": j if resp.status == 200 else None, "status": resp.status}
    except Exception as e:
        ms = (time.time() - t0) * 1000
        return {"ok": False, "ms": ms, "error": str(e)}


async def one_report(session: aiohttp.ClientSession, base_url: str, img: str, analysis: dict) -> Dict[str, Any]:
    t0 = time.time()
    try:
        async with session.post(f"{base_url}/api/report",
                                json={"image": img, "analysis": analysis},
                                timeout=aiohttp.ClientTimeout(total=30)) as resp:
            j = await resp.json()
            ms = (time.time() - t0) * 1000
            return {"ok": resp.status == 200, "ms": ms, "report": j if resp.status == 200 else None}
    except Exception as e:
        return {"ok": False, "ms": (time.time() - t0) * 1000, "error": str(e)}


async def run_heavy_burn(n: int, base_url: str, with_xai: bool, with_reports: bool, concurrency: int = 6) -> Dict[str, Any]:
    sem = asyncio.Semaphore(concurrency)
    latencies: List[float] = []
    xai_latencies: List[float] = []
    report_latencies: List[float] = []
    ok = fail = 0
    results: List[Dict[str, Any]] = []
    reports: List[Dict[str, Any]] = []

    async with aiohttp.ClientSession() as session:
        async def worker(i: int):
            nonlocal ok, fail
            async with sem:
                img = make_cytology_like(160 + (i % 5) * 12, seed=2026 + i)
                r = await one_analyze(session, base_url, img, with_xai)
                latencies.append(r["ms"])
                if r["ok"]:
                    ok += 1
                    res = r["result"]
                    results.append(res)
                    if with_xai and res.get("heatmap"):
                        xai_latencies.append(r["ms"])
                    if with_reports:
                        rp = await one_report(session, base_url, img, res)
                        report_latencies.append(rp["ms"])
                        if rp["ok"]:
                            reports.append(rp["report"])
                else:
                    fail += 1

        t0 = time.time()
        tasks = [asyncio.create_task(worker(i)) for i in range(n)]
        await asyncio.gather(*tasks)
        total_ms = (time.time() - t0) * 1000

    def pct(l: List[float], p: float) -> float:
        if not l: return 0.0
        s = sorted(l)
        idx = max(0, min(len(s)-1, int(p * (len(s)-1))))
        return s[idx]

    summary = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "n": n,
        "ok": ok,
        "fail": fail,
        "total_ms": round(total_ms, 1),
        "latencies": {
            "avg_ms": round(statistics.mean(latencies), 2) if latencies else 0,
            "p50_ms": round(pct(latencies, 0.50), 2),
            "p95_ms": round(pct(latencies, 0.95), 2),
            "p99_ms": round(pct(latencies, 0.99), 2),
            "max_ms": round(max(latencies), 2) if latencies else 0,
        },
        "xai_calls": len(xai_latencies),
        "xai_avg_ms": round(statistics.mean(xai_latencies), 2) if xai_latencies else 0,
        "report_calls": len(report_latencies),
        "report_avg_ms": round(statistics.mean(report_latencies), 2) if report_latencies else 0,
        "concurrency": concurrency,
        "with_xai": with_xai,
        "with_reports": with_reports,
    }
    return summary, results, reports


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8003")
    ap.add_argument("--n", type=int, default=120, help="Number of inference loops")
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--with-xai", action="store_true", help="Expect/measure heatmap paths")
    ap.add_argument("--with-reports", action="store_true", help="Also call /api/report for each")
    ap.add_argument("--burst", action="store_true", help="High concurrency burst")
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()

    n = args.n
    conc = max(8, args.concurrency) if args.burst else args.concurrency

    print(f"[heavy_burn] target={args.url} n={n} conc={conc} xai={args.with_xai} reports={args.with_reports}")
    summary, results, reports = asyncio.run(
        run_heavy_burn(n, args.url, args.with_xai, args.with_reports, conc)
    )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_json = ART / f"stress_burn_{ts}.json"
    out_json.write_text(json.dumps({"summary": summary, "sample_results": results[:5]}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[heavy_burn] wrote {out_json}")

    if reports:
        rep_json = ART / f"bulk_reports_{ts}.json"
        rep_json.write_text(json.dumps({"count": len(reports), "items": reports}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[heavy_burn] wrote {rep_json} ({len(reports)} reports)")

    print("\n=== HEAVY STRESS SUMMARY ===")
    print(f"ok={summary['ok']} fail={summary['fail']} total={summary['total_ms']}ms")
    print(f"latencies avg={summary['latencies']['avg_ms']} p50={summary['latencies']['p50_ms']} p95={summary['latencies']['p95_ms']} p99={summary['latencies']['p99_ms']} max={summary['latencies']['max_ms']}")
    if args.with_xai:
        print(f"xai_calls={summary['xai_calls']} xai_avg_ms={summary['xai_avg_ms']}")
    if args.with_reports:
        print(f"report_calls={summary['report_calls']} report_avg_ms={summary['report_avg_ms']}")

    # pass/fail gates
    if summary["fail"] > summary["n"] * 0.05:
        print("WARNING: >5% failures")
    if summary["latencies"]["p95_ms"] > 3000:
        print("WARNING: p95 > 3s")


if __name__ == "__main__":
    main()

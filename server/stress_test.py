#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CervicalAI — Dedicated Server Stress + Load Test Script (Phase 1.5)

Usage (after server running on 8003):
  python stress_test.py --n 100 --concurrency 4 --fake-size 160
  python stress_test.py --burst 200 --report stress_report.json

Generates:
  - Multiple synthetic cytology-like images (no external data needed)
  - Concurrent / sequential prediction loops
  - Latency stats (avg, p50, p95, p99, max)
  - Error count + mode detection
  - Optional JSON report

This is for DEMO + STRESS only. Does NOT train or modify models.
"""
from __future__ import annotations
import argparse
import asyncio
import base64
import io
import json
import statistics
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any

import aiohttp
from PIL import Image
import numpy as np


@dataclass
class StressResult:
    n: int
    ok: int
    fail: int
    total_ms: float
    latencies_ms: List[float]
    avg_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    max_ms: float
    mode: str
    concurrency: int
    fake_size: int
    timestamp: str


def make_fake_image(size: int = 160) -> str:
    """Generate a tiny synthetic cytology-like PNG (data URL)."""
    arr = np.random.randint(175, 252, (size, size, 3), dtype=np.uint8)
    rng = np.random.default_rng()
    for _ in range(rng.integers(5, 14)):
        cx = rng.integers(6, size-6)
        cy = rng.integers(6, size-6)
        r = rng.integers(2, 10)
        y, x = np.ogrid[:size, :size]
        mask = (x - cx)**2 + (y - cy)**2 <= r*r
        shade = rng.integers(35, 85)
        arr[mask] = np.clip(arr[mask].astype(int) - shade, 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return "data:image/png;base64," + b64


async def one_predict(session: aiohttp.ClientSession, base_url: str, img: str, want_heat: bool = False) -> Dict[str, Any]:
    t0 = time.time()
    try:
        async with session.post(f"{base_url}/api/analyze",
                                json={"image": img},
                                timeout=aiohttp.ClientTimeout(total=30)) as resp:
            j = await resp.json()
            ms = (time.time() - t0) * 1000
            return {"ok": resp.status == 200, "ms": ms, "result": j if resp.status == 200 else None, "status": resp.status}
    except Exception as e:
        ms = (time.time() - t0) * 1000
        return {"ok": False, "ms": ms, "error": str(e)}


async def run_concurrent(n: int, concurrency: int, base_url: str, size: int, want_heat: bool = False) -> StressResult:
    sem = asyncio.Semaphore(concurrency)
    latencies: List[float] = []
    ok = 0
    fail = 0

    async with aiohttp.ClientSession() as session:
        async def worker(i: int):
            nonlocal ok, fail
            async with sem:
                img = make_fake_image(size)
                r = await one_predict(session, base_url, img, want_heat)
                latencies.append(r["ms"])
                if r["ok"]:
                    ok += 1
                else:
                    fail += 1

        t0 = time.time()
        tasks = [asyncio.create_task(worker(i)) for i in range(n)]
        await asyncio.gather(*tasks)
        total_ms = (time.time() - t0) * 1000

    l = sorted(latencies)
    def pct(p: float) -> float:
        if not l: return 0.0
        idx = max(0, min(len(l)-1, int(p * len(l))))
        return l[idx]

    mode = "unknown"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{base_url}/api/health", timeout=aiohttp.ClientTimeout(total=5)) as r:
                hj = await r.json()
                mode = hj.get("mode", "unknown")
    except Exception:
        pass

    return StressResult(
        n=n,
        ok=ok,
        fail=fail,
        total_ms=round(total_ms, 1),
        latencies_ms=[round(x, 2) for x in latencies],
        avg_ms=round(statistics.mean(latencies), 2) if latencies else 0.0,
        p50_ms=round(pct(0.50), 2),
        p95_ms=round(pct(0.95), 2),
        p99_ms=round(pct(0.99), 2),
        max_ms=round(max(latencies), 2) if latencies else 0.0,
        mode=mode,
        concurrency=concurrency,
        fake_size=size,
        timestamp=datetime.now().isoformat(timespec="seconds"),
    )


def run_sequential(n: int, base_url: str, size: int) -> StressResult:
    """Simple blocking loop (no async) for baseline."""
    import requests
    latencies = []
    ok = fail = 0
    t0 = time.time()
    for i in range(n):
        img = make_fake_image(size)
        try:
            r = requests.post(f"{base_url}/api/analyze", json={"image": img}, timeout=25)
            ms = (time.time() - t0) * 1000  # rough cumulative; use per-call
            # better per call timing
            t1 = time.time()
            r = requests.post(f"{base_url}/api/analyze", json={"image": img}, timeout=25)
            ms = (time.time() - t1) * 1000
            latencies.append(ms)
            if r.ok:
                ok += 1
            else:
                fail += 1
        except Exception:
            fail += 1
            latencies.append(9999)
    total = (time.time() - t0) * 1000
    l = sorted(latencies)
    def pct(p):
        if not l: return 0
        return l[max(0, min(len(l)-1, int(p*len(l))))]
    mode = "unknown"
    try:
        h = requests.get(f"{base_url}/api/health", timeout=5).json()
        mode = h.get("mode", "unknown")
    except Exception:
        pass
    return StressResult(
        n=n, ok=ok, fail=fail, total_ms=round(total,1),
        latencies_ms=[round(x,2) for x in latencies],
        avg_ms=round(statistics.mean(latencies),2) if latencies else 0,
        p50_ms=round(pct(0.5),2), p95_ms=round(pct(0.95),2), p99_ms=round(pct(0.99),2),
        max_ms=round(max(latencies),2) if latencies else 0,
        mode=mode, concurrency=1, fake_size=size,
        timestamp=datetime.now().isoformat(timespec="seconds"),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8003", help="Server base URL (start with: python -m uvicorn app:app --port 8003)")
    ap.add_argument("--n", type=int, default=50, help="Number of prediction loops")
    ap.add_argument("--concurrency", type=int, default=4, help="Concurrent workers (async)")
    ap.add_argument("--fake-size", type=int, default=160, help="Synthetic image size")
    ap.add_argument("--sequential", action="store_true", help="Force sequential (requests)")
    ap.add_argument("--burst", type=int, default=0, help="If >0, run a quick burst of N with high concurrency")
    ap.add_argument("--report", default="", help="Write full JSON result to this file")
    ap.add_argument("--print-latencies", action="store_true", help="Print all latencies (long)")
    args = ap.parse_args()

    print(f"[stress] target={args.url} n={args.n} conc={args.concurrency} size={args.fake_size}")

    if args.burst > 0:
        res = asyncio.run(run_concurrent(args.burst, max(8, args.concurrency), args.url, args.fake_size))
    elif args.sequential:
        res = run_sequential(args.n, args.url, args.fake_size)
    else:
        res = asyncio.run(run_concurrent(args.n, args.concurrency, args.url, args.fake_size))

    print("\n=== STRESS RESULT ===")
    print(f"mode={res.mode} ok={res.ok} fail={res.fail}")
    print(f"total={res.total_ms}ms  avg={res.avg_ms}ms  p50={res.p50_ms}  p95={res.p95_ms}  p99={res.p99_ms}  max={res.max_ms}")
    print(f"concurrency={res.concurrency}  fake_size={res.fake_size}")

    if args.print_latencies:
        print("latencies_ms:", res.latencies_ms)

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(asdict(res), f, ensure_ascii=False, indent=2)
        print(f"[stress] wrote {args.report}")

    # quick pass/fail gate for demo
    if res.fail > res.n * 0.05:
        print("WARNING: >5% failures during stress")
    if res.p95_ms > 2000:
        print("WARNING: p95 latency > 2s — may feel slow on demo")


if __name__ == "__main__":
    main()
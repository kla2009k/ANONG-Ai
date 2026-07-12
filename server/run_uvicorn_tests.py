#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CervicalAI — Uvicorn Live Test Runner (Prolific)

Starts uvicorn on a free port, runs:
  - health
  - analyze (single)
  - batch
  - stress
  - generate_fake
  - report (with XAI embed check)
  - report/export
  - demo_script
  - contour_edit

Then prints summary and exits.

Usage:
  python run_uvicorn_tests.py --port 8011 --stress-loops 30
"""
import argparse
import base64
import io
import json
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import requests
from PIL import Image
import numpy as np


def make_fake(size=128):
    arr = np.random.randint(175, 252, (size, size, 3), dtype=np.uint8)
    for _ in range(7):
        cx = np.random.randint(6, size-6)
        cy = np.random.randint(6, size-6)
        r = np.random.randint(2, 8)
        y, x = np.ogrid[:size, :size]
        mask = (x - cx)**2 + (y - cy)**2 <= r*r
        arr[mask] = np.clip(arr[mask].astype(int) - np.random.randint(30, 70), 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


@contextmanager
def uvicorn_server(port: int, cwd: Path):
    cmd = [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"]
    proc = subprocess.Popen(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    base = f"http://127.0.0.1:{port}"
    # wait for ready
    for _ in range(40):
        try:
            r = requests.get(base + "/api/health", timeout=1.5)
            if r.ok:
                break
        except Exception:
            time.sleep(0.25)
    else:
        proc.terminate()
        raise RuntimeError("Server did not start in time")
    try:
        yield base
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8012)
    ap.add_argument("--stress-loops", type=int, default=20)
    args = ap.parse_args()

    server_dir = Path(__file__).parent
    results = {}

    with uvicorn_server(args.port, server_dir) as base:
        print(f"[test] server up at {base}")

        # 1. health
        h = requests.get(base + "/api/health", timeout=5).json()
        results["health"] = h
        print("HEALTH mode:", h.get("mode"), "phase:", h.get("phase"))

        img = make_fake(160)

        # 2. analyze
        a = requests.post(base + "/api/analyze", json={"image": img}, timeout=15).json()
        results["analyze"] = {"top": a.get("top"), "has_heatmap": bool(a.get("heatmap")), "contours": len(a.get("contours", []))}
        print("ANALYZE top:", a.get("top"), "heatmap:", bool(a.get("heatmap")))

        # 3. batch
        b = requests.post(base + "/api/batch_analyze", json={"images": [img, img, img]}, timeout=20).json()
        results["batch"] = {"count": b.get("count"), "ok": b.get("ok_count")}
        print("BATCH:", b.get("ok_count"), "/", b.get("count"))

        # 4. stress
        s = requests.post(base + "/api/stress", json={"n": args.stress_loops, "fake_size": 96}, timeout=40).json()
        results["stress"] = {"n": s.get("n"), "ok": s.get("ok"), "p95": s.get("p95_ms"), "avg": s.get("avg_ms")}
        print("STRESS p95:", s.get("p95_ms"), "avg:", s.get("avg_ms"))

        # 5. generate_fake
        f = requests.post(base + "/api/generate_fake", json={"count": 5, "size": 128}, timeout=10).json()
        results["generate_fake"] = f.get("count")
        print("FAKE count:", f.get("count"))

        # 6. report + xai
        r = requests.post(base + "/api/report", json={"analysis": a}, timeout=10).json()
        results["report"] = {"clinical": bool(r.get("layer_clinical")), "patient": bool(r.get("layer_patient")), "xai": bool(r.get("xai_embed"))}
        print("REPORT xai_embed:", bool(r.get("xai_embed")))

        # 7. export
        e = requests.post(base + "/api/report/export", json={"analysis": a, "report": r}, timeout=10).json()
        results["export"] = {"ok": e.get("ok"), "version": e.get("export_version"), "has_xai": bool(e.get("xai_embed"))}
        print("EXPORT version:", e.get("export_version"))

        # 8. demo_script
        ds = requests.get(base + "/api/demo_script", timeout=5).json()
        results["demo_script"] = ds.get("title")
        print("DEMO_SCRIPT:", ds.get("title"))

        # 9. contour_edit (SAM stub)
        ce = requests.post(base + "/api/contour_edit", json={"points": [[40,40],[90,35],[95,85],[45,90]]}, timeout=8).json()
        results["contour_edit"] = {"refined": len(ce.get("refined_contour", [])), "area": ce.get("area_px")}
        print("CONTOUR_EDIT area:", ce.get("area_px"))

    print("\n=== TEST SUMMARY ===")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print("\nALL LIVE UVICORN TESTS COMPLETED")


if __name__ == "__main__":
    main()
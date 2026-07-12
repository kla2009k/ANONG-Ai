#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CervicalAI — Batch Upload Simulator (for web demo + load)

Sends a batch of fake images to /api/batch_analyze and prints summary.
Useful to test the new batch endpoint from CLI before/after UI batch.

Run (server must be up):
  python batch_sim.py --count 12 --size 180
"""
import argparse
import base64
import io
import json
import time

import requests
from PIL import Image
import numpy as np


def make_fake(size: int) -> str:
    arr = np.random.randint(170, 255, (size, size, 3), dtype=np.uint8)
    rng = np.random.default_rng()
    for _ in range(rng.integers(7, 16)):
        cx, cy = rng.integers(5, size-5), rng.integers(5, size-5)
        r = rng.integers(2, 9)
        y, x = np.ogrid[:size, :size]
        mask = (x - cx)**2 + (y - cy)**2 <= r*r
        arr[mask] = np.clip(arr[mask].astype(int) - rng.integers(30, 80), 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8003")
    ap.add_argument("--count", type=int, default=8)
    ap.add_argument("--size", type=int, default=160)
    args = ap.parse_args()

    imgs = [make_fake(args.size) for _ in range(args.count)]
    t0 = time.time()
    r = requests.post(f"{args.url}/api/batch_analyze", json={"images": imgs}, timeout=60)
    dt = (time.time() - t0) * 1000
    print(f"HTTP {r.status_code} in {dt:.1f}ms")
    try:
        j = r.json()
        print(json.dumps(j, indent=2, ensure_ascii=False)[:2000])
        print("...")
        print(f"ok_count={j.get('ok_count')}/{j.get('count')}")
    except Exception as e:
        print("raw:", r.text[:500])


if __name__ == "__main__":
    main()
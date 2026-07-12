#!/usr/bin/env python3
"""Quick live API smoke against running server."""
import requests, time, json, base64, io
from PIL import Image
import numpy as np

base = "http://127.0.0.1:8003"
print("=== LIVE SERVER SMOKE (REAL MODEL) ===")

h = requests.get(base+"/api/health", timeout=5).json()
print("Health:", h.get("mode"), h.get("phase"))

lats = []
for i in range(8):
    arr = np.random.randint(150,255,(160,160,3),dtype=np.uint8)
    buf = io.BytesIO(); Image.fromarray(arr).save(buf,"PNG")
    b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    t0 = time.time()
    r = requests.post(base+"/api/analyze", json={"image":b64}, timeout=90)
    ms = (time.time()-t0)*1000
    lats.append(ms)
    if r.ok:
        j = r.json()
        top = j.get("top", {})
        unc = (j.get("uncertainty_viz") or j.get("uncertainty") or {})
        print(f"  [{i}] {top.get('key')} {top.get('prob',0):.2f} unc={unc.get('flag')} {ms:.0f}ms")
    else:
        print(f"  [{i}] FAIL {r.status_code}")

print("Lats:", [round(x) for x in lats])
print("Avg:", round(sum(lats)/len(lats)), "ms")

# batch 4
imgs = []
for _ in range(4):
    arr = np.random.randint(150,255,(128,128,3),dtype=np.uint8)
    buf=io.BytesIO(); Image.fromarray(arr).save(buf,"PNG")
    imgs.append("data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode())
t0=time.time()
rb=requests.post(base+"/api/batch_analyze", json={"images":imgs}, timeout=120)
print("Batch4:", rb.status_code, "in", round((time.time()-t0)*1000), "ms", "ok=", rb.json().get("ok_count") if rb.ok else "?")

print("=== SMOKE DONE ===")

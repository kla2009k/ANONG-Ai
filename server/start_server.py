#!/usr/bin/env python3
"""Start CervicalAI server in background for demo/stress."""
import subprocess
import sys
import time
import pathlib

here = pathlib.Path(__file__).parent
log_out = here / "srv_out.log"
log_err = here / "srv_err.log"

cmd = [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]
print(f"[start] launching: {' '.join(cmd)}")
with open(log_out, "w", encoding="utf-8") as fo, open(log_err, "w", encoding="utf-8") as fe:
    proc = subprocess.Popen(cmd, stdout=fo, stderr=fe, cwd=str(here))
print(f"[start] pid={proc.pid}")
time.sleep(3)
print("[start] done (check srv_out.log / srv_err.log)")

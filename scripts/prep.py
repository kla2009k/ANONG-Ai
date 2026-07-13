#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CervicalAI — Data preparation, Bethesda mapping, stratified split, class weights, aug spec.

RESPONSIBILITIES:
  - Scan data/raw/ (SIPaKMeD, RepoMedUNM, Mendeley LBC, synthetic_demo)
  - Map source labels → Bethesda (NILM/LSIL/HSIL/SCC) + binary koilocyte flag
  - Build unified index.csv with 5-class label encoding
  - Stratified train/val/test split (default 70/15/15) by (label, source)
  - Compute inverse-frequency class weights
  - Export albumentations spec + cytology-tuned aug config (see scripts/augmentations.py)
  - Generate DETAILED class balance reports + per-source breakdown
  - Support --synthetic to include generated demo data

BETESDA 5-CLASS ENCODING (for classifier head):
  0: NILM
  1: LSIL   (includes koilocyte-positive LSIL)
  2: HSIL
  3: SCC
  4: KOIL   (pure koilocyte flag without other label; treated as LSIL+koil triage view)

KOILOCYTE FLAG:
  - Separate binary column (0/1) for multi-task or triage routing
  - Source classes that set flag=1: SIPaKMeD koilocytotic, RepoMedUNM koilocyte, synthetic KOIL

AUTHORITATIVE MAPPING:
  See _build_bethesda_mapping() in download_data.py and the mappers below.
  This file is the IMPLEMENTATION. Keep in sync with docs.

RUNS:
  python scripts/prep.py                     # normal
  python scripts/prep.py --val 0.2 --test 0.1 --seed 123
  python scripts/prep.py --demo              # mark config as demo
  python scripts/prep.py --synthetic         # include data/raw/synthetic_demo
  python scripts/prep.py --synthetic-only    # ONLY synthetic (for smoke tests)

OUTPUTS (data/processed/):
  index.csv                 # all images + labels
  split_train.csv
  split_val.csv
  split_test.csv
  class_weights.json        # inverse freq + counts per source
  prep_config.json          # img_size, mean/std, albumentations spec, metadata
  class_balance_report.json # detailed breakdown
  per_source_stats.json
  prep_run_log.json         # reproducibility (command, seed, timestamp, git hash if avail)
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import pathlib
import random
import subprocess
import sys
import time
from collections import defaultdict, Counter
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import numpy as np

ROOT = pathlib.Path(__file__).parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# SOURCE MAPPERS (keep in sync with download_data.py _build_bethesda_mapping)
# ──────────────────────────────────────────────────────────────────────────────

def map_sipakmed(path: pathlib.Path) -> Tuple[str, int]:
    """SIPaKMeD: 5 folders → Bethesda + koil flag."""
    # Class directories are above CROPPED/, so inspect the full path rather
    # than only the immediate parent directory.
    full = str(path).lower().replace("\\", "/")
    stem = path.stem.lower()

    if "koilocyt" in full:
        return ("LSIL", 1)
    if "dyskerat" in full:
        return ("HSIL", 0)
    if any(k in full for k in ["superficial", "intermediate", "parabasal", "metaplast"]):
        return ("NILM", 0)
    if "koilo" in stem:
        return ("LSIL", 1)
    if "dysker" in stem:
        return ("HSIL", 0)
    return ("NILM", 0)


def map_repomedunm(path: pathlib.Path) -> Tuple[str, int]:
    """RepoMedUNM ThinPrep: normal/koilocyte/LSIL/HSIL."""
    p = str(path).lower()
    if "koilocyte" in p:
        return ("LSIL", 1)
    if "lsil" in p:
        return ("LSIL", 0)
    if "hsil" in p:
        return ("HSIL", 0)
    if "normal" in p or "nilm" in p:
        return ("NILM", 0)
    return ("NILM", 0)


def map_mendeley_lbc(path: pathlib.Path) -> Tuple[str, int]:
    """Mendeley LBC: NILM/LSIL/HSIL/SCC (no koil label)."""
    p = str(path).lower()
    parent = path.parent.name.lower()
    for key in ["scc", "hsil", "lsil", "nilm", "normal"]:
        if key in p or key in parent:
            if key == "scc":
                return ("SCC", 0)
            if key == "hsil":
                return ("HSIL", 0)
            if key == "lsil":
                return ("LSIL", 0)
            return ("NILM", 0)
    return ("NILM", 0)


def map_synthetic(path: pathlib.Path) -> Tuple[str, int]:
    """Synthetic data: folders NILM/LSIL/HSIL/SCC/KOIL."""
    p = str(path).lower()
    parent = path.parent.name.lower()
    if "koil" in parent or "koil" in p:
        return ("LSIL", 1)  # KOIL folder treated as LSIL + flag
    if "scc" in parent:
        return ("SCC", 0)
    if "hsil" in parent:
        return ("HSIL", 0)
    if "lsil" in parent:
        return ("LSIL", 0)
    if "nilm" in parent:
        return ("NILM", 0)
    return ("NILM", 0)


MAPPERS = {
    "sipakmed": map_sipakmed,
    "repomedunm": map_repomedunm,
    "mendeley_lbc": map_mendeley_lbc,
    "synthetic_demo": map_synthetic,
    "synthetic": map_synthetic,
    "herlev_organized": map_synthetic,  # mapped to NILM etc
}

BETHESDA_CLASSES = ["NILM", "LSIL", "HSIL", "SCC", "KOIL_FLAG"]

# Final 5-class for single-head classifier:
# NILM=0, LSIL=1, HSIL=2, SCC=3, KOIL=4 (pure koilocyte view)
CLASS_MAP = {"NILM": 0, "LSIL": 1, "HSIL": 2, "SCC": 3, "KOIL": 4}
INV_CLASS = {v: k for k, v in CLASS_MAP.items()}


def bethesda_to_5class(bethesda: str, koil: int) -> int:
    # Koilocytosis is an explicit legacy fifth-class endpoint. It must be
    # checked before LSIL because SIPaKMeD represents KOIL as LSIL-like
    # morphology plus koilocyte=1. New research uses a separate koil head.
    if koil:
        return 4
    if bethesda == "NILM":
        return 0
    if bethesda == "LSIL":
        return 1
    if bethesda == "HSIL":
        return 2
    if bethesda == "SCC":
        return 3
    # fallback conservative
    return 1


# ──────────────────────────────────────────────────────────────────────────────
# Scanning + indexing
# ──────────────────────────────────────────────────────────────────────────────

def scan_raw(include_synthetic: bool = False) -> List[Dict]:
    rows: List[Dict] = []
    sources_to_scan = list(MAPPERS.keys())
    if not include_synthetic:
        sources_to_scan = [s for s in sources_to_scan if "synthetic" not in s]

    # Dynamic discovery for factory explosion runs (synth_*, factory_*, synthetic_* under raw)
    if include_synthetic:
        for cand in list(RAW.glob("synth*")) + list(RAW.glob("factory*")) + list(RAW.glob("synthetic*")):
            if cand.is_dir():
                dname = cand.name
                if dname not in MAPPERS:
                    MAPPERS[dname] = map_synthetic
                if dname not in sources_to_scan:
                    sources_to_scan.append(dname)

    for dset in sources_to_scan:
        mapper = MAPPERS[dset]
        root = RAW / dset
        if not root.exists():
            continue
    # auto include herlev_organized for real data
    if (RAW / "herlev_organized").exists() and "herlev_organized" not in sources_to_scan:
        sources_to_scan.append("herlev_organized")
    for dset in sources_to_scan:
        mapper = MAPPERS[dset]
        root = RAW / dset
        if not root.exists():
            continue
        imgs = [p for p in root.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}]
        # Herlev ships a segmentation-mask copy per cell named "*-d.bmp" — exclude (not a real cell image)
        imgs = [p for p in imgs if not p.stem.lower().endswith("-d")]
        for p in imgs:
            try:
                bethesda, koil = mapper(p)
            except Exception:
                bethesda, koil = "NILM", 0
            rows.append({
                "path": str(p.resolve()),
                "source": dset,
                "bethesda": bethesda,
                "koilocyte": int(koil),
                "label5": bethesda_to_5class(bethesda, koil),
            })
    print(f"[scan] found {len(rows)} images across {len(set(r['source'] for r in rows))} datasets")
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# Stratified split (by label5 + source)
# ──────────────────────────────────────────────────────────────────────────────

def stratified_split(rows: List[Dict], val: float, test: float, seed: int = 42) -> Tuple[List[int], List[int], List[int]]:
    random.seed(seed)
    np.random.seed(seed)

    buckets: Dict[Tuple, List[int]] = defaultdict(list)
    for i, r in enumerate(rows):
        buckets[(r["label5"], r["source"])].append(i)

    train_idx, val_idx, test_idx = [], [], []
    for key, idxs in buckets.items():
        random.shuffle(idxs)
        n = len(idxs)
        n_test = int(round(n * test))
        n_val = int(round(n * val))
        # ensure at least 1 in train if n large enough
        if n - n_val - n_test < 1 and n > 2:
            n_val = max(0, n_val - 1)
            n_test = max(0, n_test - 1)
        n_train = n - n_val - n_test
        test_idx.extend(idxs[:n_test])
        val_idx.extend(idxs[n_test:n_test + n_val])
        train_idx.extend(idxs[n_test + n_val:])

    random.shuffle(train_idx)
    random.shuffle(val_idx)
    random.shuffle(test_idx)
    return train_idx, val_idx, test_idx


def compute_weights(labels: List[int], n_classes: int = 5) -> List[float]:
    counts = np.bincount(labels, minlength=n_classes).astype(float)
    counts = np.maximum(counts, 1.0)
    w = counts.sum() / (n_classes * counts)
    return [float(x) for x in w]


# ──────────────────────────────────────────────────────────────────────────────
# Detailed stats
# ──────────────────────────────────────────────────────────────────────────────

def compute_detailed_stats(rows: List[Dict], tr: List[int], va: List[int], te: List[int]) -> Dict:
    """Produce rich class balance + per-source reports."""
    def _subset(idxs):
        return [rows[i] for i in idxs]

    all_labels = [r["label5"] for r in rows]
    tr_labels = [rows[i]["label5"] for i in tr]
    va_labels = [rows[i]["label5"] for i in va]
    te_labels = [rows[i]["label5"] for i in te]

    def _counts(labels):
        c = Counter(labels)
        return {INV_CLASS[k]: int(v) for k, v in sorted(c.items())}

    def _koil_rate(subset):
        if not subset:
            return 0.0
        k = sum(r["koilocyte"] for r in subset)
        return round(100.0 * k / len(subset), 2)

    report = {
        "total": len(rows),
        "splits": {"train": len(tr), "val": len(va), "test": len(te)},
        "overall_counts": _counts(all_labels),
        "train_counts": _counts(tr_labels),
        "val_counts": _counts(va_labels),
        "test_counts": _counts(te_labels),
        "class_weights": compute_weights(tr_labels),
        "koilocyte_rate_percent": {
            "all": _koil_rate(rows),
            "train": _koil_rate(_subset(tr)),
            "val": _koil_rate(_subset(va)),
            "test": _koil_rate(_subset(te)),
        },
        "per_source": {},
    }

    # per source breakdown
    by_source: Dict[str, List[Dict]] = defaultdict(list)
    for r in rows:
        by_source[r["source"]].append(r)

    for src, lst in by_source.items():
        src_labels = [r["label5"] for r in lst]
        src_koil = sum(r["koilocyte"] for r in lst)
        report["per_source"][src] = {
            "count": len(lst),
            "counts": _counts(src_labels),
            "koilocyte_count": src_koil,
            "koilocyte_rate_percent": round(100.0 * src_koil / len(lst), 2) if lst else 0.0,
        }

    # imbalance ratios
    def _imba(d):
        vals = list(d.values())
        return round(max(vals) / max(1, min(vals)), 3) if vals else 0.0

    report["imbalance_ratio"] = {
        "overall": _imba(report["overall_counts"]),
        "train": _imba(report["train_counts"]),
    }

    return report


# ──────────────────────────────────────────────────────────────────────────────
# Reproducibility log
# ──────────────────────────────────────────────────────────────────────────────

def make_run_log(args: argparse.Namespace, rows: List[Dict]) -> Dict:
    log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": " ".join(sys.argv),
        "args": vars(args),
        "n_images": len(rows),
        "sources": sorted(set(r["source"] for r in rows)),
        "python": sys.version.split()[0],
        "platform": sys.platform,
    }
    # best-effort git hash
    try:
        h = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL).decode().strip()
        log["git"] = h
    except Exception:
        log["git"] = None
    return log


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(PROC))
    ap.add_argument("--val", type=float, default=0.15)
    ap.add_argument("--test", type=float, default=0.15)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--synthetic", action="store_true", help="include synthetic_demo if present")
    ap.add_argument("--synthetic-only", action="store_true", help="use ONLY synthetic data")
    ap.add_argument("--real-data", action="store_true", help="use real data from data/raw/herlev_organized etc if present")
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    t0 = time.time()

    include_synth = args.synthetic or args.synthetic_only
    rows = scan_raw(include_synthetic=include_synth)

    if not rows:
        print("[error] no images found. Run download_data.py or generate_synthetic_data.py first.")
        # write empty artifacts so downstream doesn't explode
        header = "path,source,bethesda,koilocyte,label5,split\n"
        for name in ["index.csv", "split_train.csv", "split_val.csv", "split_test.csv"]:
            (out / name).write_text(header, encoding="utf-8")
        (out / "class_weights.json").write_text(json.dumps({"weights": [1.0]*5, "demo": True}, indent=2), encoding="utf-8")
        cfg = {
            "img_size": 224,
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225],
            "albumentations": {"train": ["RandomResizedCrop", "HorizontalFlip", "ColorJitter"], "val": ["Resize", "CenterCrop"]},
            "demo": True,
            "synthetic": include_synth,
        }
        (out / "prep_config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
        (out / "class_balance_report.json").write_text(json.dumps({"note": "empty run"}, indent=2), encoding="utf-8")
        (out / "per_source_stats.json").write_text(json.dumps({}, indent=2), encoding="utf-8")
        (out / "prep_run_log.json").write_text(json.dumps(make_run_log(args, rows), indent=2), encoding="utf-8")
        print("[demo] wrote empty artifacts.")
        return

    tr, va, te = stratified_split(rows, args.val, args.test, args.seed)

    # write index
    with open(out / "index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "source", "bethesda", "koilocyte", "label5"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    def write_split(name, idxs):
        with open(out / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["path", "source", "bethesda", "koilocyte", "label5", "split"])
            w.writeheader()
            for i in idxs:
                r = rows[i].copy()
                r["split"] = name.replace("split_", "").replace(".csv", "")
                w.writerow(r)

    write_split("split_train.csv", tr)
    write_split("split_val.csv", va)
    write_split("split_test.csv", te)

    # detailed stats
    stats = compute_detailed_stats(rows, tr, va, te)
    (out / "class_balance_report.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    (out / "per_source_stats.json").write_text(json.dumps(stats["per_source"], indent=2), encoding="utf-8")

    # class weights
    (out / "class_weights.json").write_text(json.dumps({
        "weights": stats["class_weights"],
        "classes": INV_CLASS,
        "counts": stats["train_counts"],
        "note": "inverse-frequency for weighted CE / focal",
    }, indent=2), encoding="utf-8")

    # albumentations config + cytology aug reference
    try:
        from scripts import augmentations as aug
        aug_cfg = aug.export_pipeline_json(img_size=224, stain_norm=False)
    except Exception:
        aug_cfg = {
            "train": [
                {"name": "RandomResizedCrop", "size": [224, 224], "scale": [0.72, 1.0]},
                {"name": "HorizontalFlip", "p": 0.5},
                {"name": "VerticalFlip", "p": 0.35},
                {"name": "ColorJitter", "brightness": 0.10, "contrast": 0.10, "saturation": 0.08, "hue": 0.03, "p": 0.9},
                {"name": "Normalize", "mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]},
            ],
            "val": [
                {"name": "Resize", "height": 256, "width": 256},
                {"name": "CenterCrop", "height": 224, "width": 224},
                {"name": "Normalize", "mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]},
            ],
        }

    cfg = {
        "img_size": 224,
        "mean": [0.485, 0.456, 0.406],
        "std": [0.229, 0.224, 0.225],
        "albumentations": aug_cfg,
        "bethesda_classes": BETHESDA_CLASSES,
        "class_map": CLASS_MAP,
        "demo": bool(args.demo),
        "synthetic": bool(include_synth),
        "seed": args.seed,
        "split": {"val": args.val, "test": args.test},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    (out / "prep_config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    # run log
    (out / "prep_run_log.json").write_text(json.dumps(make_run_log(args, rows), indent=2), encoding="utf-8")

    print(f"\n[done] prepared in {time.time()-t0:.1f}s -> {out}")
    print(f"  train={len(tr)} val={len(va)} test={len(te)}")
    print(f"  train_dist={stats['train_counts']}")
    print(f"  imbalance_ratio(train)={stats['imbalance_ratio']['train']}")
    print(f"  koil_rate(train)={stats['koilocyte_rate_percent']['train']}%")
    print("  See class_balance_report.json and per_source_stats.json for full breakdown.")


if __name__ == "__main__":
    main()

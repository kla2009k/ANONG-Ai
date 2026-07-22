#!/usr/bin/env python3
"""Download official CRIC parent images and build leakage-resistant folds."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.cric_grade_data import CRIC_LABEL_MAP, crop_around_nucleus, grouped_folds, supported_rows, write_manifest


RAW = ROOT / "data" / "raw" / "cric_official"
ANNOTATIONS = RAW / "classifications.csv"
IMAGE_DIR = RAW / "images"
ARTICLE_API = "https://api.figshare.com/v2/articles/{article_id}"


def request_bytes(url: str, attempts: int = 8) -> bytes:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Anong-CerviCo-Pilot/1.0"})
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code not in {403, 408, 429, 500, 502, 503, 504}:
                raise
            retry_after = error.headers.get("Retry-After")
            delay = float(retry_after) if retry_after and retry_after.isdigit() else min(45.0, 2.0 ** attempt)
        except (TimeoutError, urllib.error.URLError) as error:
            last_error = error
            delay = min(45.0, 2.0 ** attempt)
        time.sleep(delay + random.uniform(0.0, 1.0))
    raise RuntimeError(f"download failed after {attempts} attempts: {url}") from last_error


def article_id(doi: str) -> str:
    return doi.split("figshare.", 1)[1].split(".", 1)[0]


def download_parent(row: dict[str, str]) -> Path:
    destination = IMAGE_DIR / row["image_filename"]
    if destination.exists():
        with Image.open(destination) as image:
            image.verify()
        return destination
    metadata = json.loads(request_bytes(ARTICLE_API.format(article_id=article_id(row["image_doi"]))))
    source = next((item for item in metadata.get("files", []) if item.get("name") == row["image_filename"]), None)
    if source is None:
        raise RuntimeError(f"missing Figshare image for {row['image_doi']}")
    payload = request_bytes(source["download_url"])
    expected_md5 = source.get("supplied_md5")
    if expected_md5 and hashlib.md5(payload).hexdigest() != expected_md5:
        raise RuntimeError(f"checksum mismatch for {row['image_filename']}")
    temporary = destination.with_suffix(destination.suffix + ".part")
    temporary.write_bytes(payload)
    with Image.open(temporary) as image:
        image.verify()
    temporary.replace(destination)
    return destination


def parent_rows() -> list[dict[str, str]]:
    with ANNOTATIONS.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["bethesda_system"] in CRIC_LABEL_MAP]
    return list({row["image_id"]: row for row in rows}.values())


def split_summary(split: dict[str, list[dict[str, str]]]) -> dict:
    return {
        name: {
            "cells": len(rows),
            "parent_images": len({row["group_id"] for row in rows}),
            "classes": dict(Counter(row["bethesda"] for row in rows)),
        }
        for name, rows in split.items()
    }


def build_crop_cache(rows: list[dict[str, str]], cache_dir: Path, crop_size: int,
                     path_field: str = "crop_path", suffix: str = "") -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    by_parent: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_parent.setdefault(row["path"], []).append(row)
    for parent_index, (parent_path, cells) in enumerate(by_parent.items(), start=1):
        with Image.open(parent_path) as opened:
            parent = opened.convert("RGB")
        for row in cells:
            tag = f"-{suffix}" if suffix else ""
            filename = f"{row['group_id']}-{row['cell_id']}{tag}.jpg"
            destination = cache_dir / filename
            if not destination.exists():
                crop = crop_around_nucleus(parent, int(row["nucleus_x"]), int(row["nucleus_y"]), crop_size)
                crop.save(destination, format="JPEG", quality=88, optimize=True)
            row[path_field] = str(destination.resolve())
        if parent_index % 40 == 0 or parent_index == len(by_parent):
            print(f"cached crops from {parent_index}/{len(by_parent)} parent images", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "processed" / "cric_grade_grouped")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260725)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--crop-size", type=int, default=320)
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "data" / "cache" / "cric_grade_320")
    parser.add_argument("--context-crop-size", type=int, default=640)
    parser.add_argument("--context-cache-dir", type=Path, default=ROOT / "data" / "cache" / "cric_context_640")
    parser.add_argument("--skip-download", action="store_true")
    args = parser.parse_args()

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    parents = parent_rows()
    if not args.skip_download:
        with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 8))) as executor:
            futures = {executor.submit(download_parent, row): row["image_id"] for row in parents}
            for count, future in enumerate(as_completed(futures), start=1):
                future.result()
                if count % 20 == 0 or count == len(futures):
                    print(f"verified {count}/{len(futures)} parent images", flush=True)

    rows = supported_rows(ANNOTATIONS, IMAGE_DIR)
    missing = sorted({row["path"] for row in rows if not Path(row["path"]).exists()})
    if missing:
        raise RuntimeError(f"{len(missing)} parent images are missing; rerun without --skip-download")
    build_crop_cache(rows, args.cache_dir, args.crop_size, "crop_path")
    build_crop_cache(rows, args.context_cache_dir, args.context_crop_size, "context_path", "context")
    folds = grouped_folds(rows, folds=args.folds, seed=args.seed)
    summaries = []
    for index, split in enumerate(folds, start=1):
        fold_dir = args.output / f"fold_{index}"
        for name, split_rows in split.items():
            write_manifest(fold_dir / f"{name}.csv", split_rows)
        summaries.append({"fold": index, **split_summary(split)})
    metadata = {
        "dataset": "CRIC Cervix Cell Classification",
        "doi": "10.6084/m9.figshare.c.4960286.v2",
        "license": "CC BY 4.0",
        "supported_cells": len(rows),
        "parent_images": len({row["group_id"] for row in rows}),
        "excluded_labels": ["ASC-US", "ASC-H"],
        "split_unit": "parent microscope image",
        "crop_cache": str(args.cache_dir.resolve()),
        "crop_size": args.crop_size,
        "context_cache": str(args.context_cache_dir.resolve()),
        "context_crop_size": args.context_crop_size,
        "seed": args.seed,
        "folds": summaries,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

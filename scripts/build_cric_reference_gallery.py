"""Build a license-safe CRIC Cervix reference atlas for the web gallery.

The generated crops are external morphology references, not model predictions or
validation evidence. Source images and annotations come from the official
Figshare collection under CC BY 4.0.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "cric_official"
ANNOTATIONS = RAW / "classifications.csv"
SOURCE_IMAGES = RAW / "images"
OUT = ROOT / "web-react" / "public" / "cric-gallery"
ANNOTATION_URL = "https://ndownloader.figshare.com/files/22494383"
ARTICLE_API = "https://api.figshare.com/v2/articles/{article_id}"
DATASET_URL = "https://figshare.com/collections/CRIC_Cervix_Cell_Classification/4960286"
DATASET_DOI = "10.6084/m9.figshare.c.4960286.v2"
CLASS_MAP = {
    "Negative for intraepithelial lesion": "NILM",
    "LSIL": "LSIL",
    "HSIL": "HSIL",
    "SCC": "SCC",
}


def request_bytes(url: str, attempts: int = 4) -> bytes:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Anong-CerviCo-Pilot/1.0"})
            with urllib.request.urlopen(request, timeout=90) as response:
                return response.read()
        except Exception as error:
            last_error = error
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"download failed after {attempts} attempts: {url}") from last_error


def ensure_annotations() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    if not ANNOTATIONS.exists():
        ANNOTATIONS.write_bytes(request_bytes(ANNOTATION_URL))


def load_selected(per_class: int) -> list[dict[str, str]]:
    with ANNOTATIONS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    selected: list[dict[str, str]] = []
    for source_label, display_class in CLASS_MAP.items():
        candidates = sorted(
            (row for row in rows if row["bethesda_system"] == source_label),
            key=lambda row: (int(row["image_id"]), int(row["cell_id"])),
        )
        seen_sources: set[str] = set()
        for row in candidates:
            if row["image_id"] in seen_sources:
                continue
            seen_sources.add(row["image_id"])
            selected.append({**row, "class": display_class})
            if len(seen_sources) == per_class:
                break
        if len(seen_sources) != per_class:
            raise RuntimeError(f"{display_class}: requested {per_class} unique images, found {len(seen_sources)}")
    return selected


def article_id(row: dict[str, str]) -> str:
    return row["image_doi"].split("figshare.", 1)[1].split(".", 1)[0]


def download_source(row: dict[str, str]) -> Path:
    SOURCE_IMAGES.mkdir(parents=True, exist_ok=True)
    destination = SOURCE_IMAGES / row["image_filename"]
    if destination.exists():
        return destination
    metadata = json.loads(request_bytes(ARTICLE_API.format(article_id=article_id(row))))
    files = metadata.get("files") or []
    match = next((item for item in files if item.get("name") == row["image_filename"]), None)
    if match is None:
        raise RuntimeError(f"source image missing from Figshare article {article_id(row)}")
    payload = request_bytes(match["download_url"])
    temporary = destination.with_suffix(destination.suffix + ".part")
    temporary.write_bytes(payload)
    with Image.open(temporary) as image:
        image.verify()
    temporary.replace(destination)
    return destination


def crop_cell(source: Path, x: int, y: int, crop_size: int = 320) -> Image.Image:
    with Image.open(source) as opened:
        image = opened.convert("RGB")
    half = crop_size // 2
    left, top, right, bottom = x - half, y - half, x + half, y + half
    padding = (max(0, -left), max(0, -top), max(0, right - image.width), max(0, bottom - image.height))
    if any(padding):
        image = ImageOps.expand(image, border=padding, fill=(248, 241, 244))
        left += padding[0]
        right += padding[0]
        top += padding[1]
        bottom += padding[1]
    return image.crop((left, top, right, bottom)).resize((256, 256), Image.Resampling.LANCZOS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-class", type=int, default=20)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    if not 1 <= args.per_class <= 20:
        raise SystemExit("--per-class must be between 1 and 20; SCC has 21 unique source images")

    ensure_annotations()
    selected = load_selected(args.per_class)
    representative_by_image = {row["image_id"]: row for row in selected}
    sources: dict[str, Path] = {}
    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 8))) as executor:
        future_to_id = {executor.submit(download_source, row): image_id for image_id, row in representative_by_image.items()}
        for completed, future in enumerate(as_completed(future_to_id), start=1):
            image_id = future_to_id[future]
            sources[image_id] = future.result()
            print(f"downloaded {completed}/{len(future_to_id)} source images", flush=True)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    counters = {key: 0 for key in CLASS_MAP.values()}
    items = []
    for row in sorted(selected, key=lambda item: (item["class"], int(item["image_id"]))):
        label = row["class"]
        counters[label] += 1
        filename = f"{label.lower()}-{counters[label]:02d}-image-{row['image_id']}-cell-{row['cell_id']}.jpg"
        crop = crop_cell(sources[row["image_id"]], int(row["nucleus_x"]), int(row["nucleus_y"]))
        crop.save(OUT / filename, format="JPEG", quality=88, optimize=True)
        items.append({
            "id": f"CRIC-{label}-{counters[label]:02d}",
            "image": f"cric-gallery/{filename}",
            "class": label,
            "source_label": row["bethesda_system"],
            "source_image_id": int(row["image_id"]),
            "source_cell_id": int(row["cell_id"]),
            "source_doi": row["image_doi"],
            "license": "CC BY 4.0",
            "domain": "conventional Pap-smear annotated cell crop",
        })

    manifest = {
        "dataset": "CRIC Cervix Cell Classification",
        "dataset_doi": DATASET_DOI,
        "dataset_url": DATASET_URL,
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "attribution": "Rezende et al., CRIC Cervix Cell Classification (2020)",
        "selection": f"one annotated cell from each of {args.per_class} unique source images per displayed class",
        "intended_use": "external_reference_atlas_not_model_evaluation",
        "model_predictions_included": False,
        "count": len(items),
        "counts": counters,
        "items": items,
    }
    (OUT / "index.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("*.jpg"))}
    (OUT / "sha256.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"items": len(items), "sources": len(sources), "counts": counters}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

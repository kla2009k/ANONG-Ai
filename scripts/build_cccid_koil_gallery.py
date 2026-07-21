"""Extract a deterministic, licensed CCCID koilocyte reference gallery."""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data" / "raw" / "cccid_official" / "CCCID_V2_LSIL.zip"
OUT = ROOT / "web-react" / "public" / "koil-gallery"
DOI = "10.5281/zenodo.20807462"
DATASET_URL = "https://zenodo.org/records/20807462"
ARCHIVE_MD5 = "6e2f6bf468addd80b698318d87c16123"
SUBTYPES = {
    "12. Superficial-type_Koilocytic_Cells": "Superficial-type koilocyte",
    "13. Intermediate-type_Koilocytic_Cells": "Intermediate-type koilocyte",
}


def center_focus_members(archive: zipfile.ZipFile, folder: str) -> list[str]:
    prefix = f"CCCID_V2_LSIL/{folder}/"
    return sorted(
        member for member in archive.namelist()
        if member.startswith(prefix) and re.search(r",5\)\.jpeg$", member)
    )


def main() -> int:
    if not ARCHIVE.exists():
        raise SystemExit(f"Missing official archive: {ARCHIVE}")
    archive_md5 = hashlib.md5(ARCHIVE.read_bytes()).hexdigest()
    if archive_md5 != ARCHIVE_MD5:
        raise SystemExit(f"CCCID archive MD5 mismatch: expected {ARCHIVE_MD5}, got {archive_md5}")
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.jpg"):
        old.unlink()

    items = []
    with zipfile.ZipFile(ARCHIVE) as archive:
        for folder, subtype in SUBTYPES.items():
            selected = center_focus_members(archive, folder)[:10]
            if len(selected) != 10:
                raise RuntimeError(f"{folder}: expected at least 10 center-focus images")
            for index, member in enumerate(selected, start=1):
                slug = "superficial" if subtype.startswith("Superficial") else "intermediate"
                filename = f"koil-{slug}-{index:02d}.jpg"
                with archive.open(member) as source, Image.open(source) as opened:
                    image = opened.convert("RGB")
                    if image.size != (384, 384):
                        raise RuntimeError(f"Unexpected CCCID image size {image.size}: {member}")
                    image.save(OUT / filename, "JPEG", quality=92, optimize=True)
                items.append({
                    "id": f"CCCID-KOIL-{slug.upper()}-{index:02d}",
                    "image": f"koil-gallery/{filename}",
                    "class": "KOIL",
                    "subtype": subtype,
                    "focus_plane": 5,
                    "source_member": member,
                    "source_doi": DOI,
                    "license": "CC BY-NC 4.0",
                    "domain": "BD SurePath liquid-based cervical cytology, Pap stain, center-focus plane",
                })

    # Alternate both subtypes in the default gallery viewport.
    items.sort(key=lambda item: (int(item["id"].rsplit("-", 1)[1]), item["subtype"]))
    manifest = {
        "dataset": "CCCID v2",
        "dataset_title": "Cervical Cancer Cell Image Database: Multi-focus Cytology Dataset",
        "dataset_doi": DOI,
        "dataset_url": DATASET_URL,
        "license": "CC BY-NC 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc/4.0/",
        "attribution": "Ohno et al., Cervical Cancer Cell Image Database v2 (2026)",
        "selection": "first 10 center-focus images from each of two expert-labelled koilocyte subtypes; no model-based selection",
        "archive_file": ARCHIVE.name,
        "archive_md5": archive_md5,
        "intended_use": "external_koil_reference_and_preselected_positive_challenge",
        "model_predictions_included": False,
        "count": len(items),
        "counts": {"KOIL": len(items)},
        "items": items,
    }
    (OUT / "index.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("*.jpg"))}
    (OUT / "sha256.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"count": len(items), "subtypes": list(SUBTYPES.values())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

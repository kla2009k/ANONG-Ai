#!/usr/bin/env python3
"""Download SIPaKMeD class archives from the dataset authors' website."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import html.parser
import json
import pathlib
import shutil
import threading
import time
import urllib.request
from datetime import datetime, timezone

import py7zr
import requests
from requests.adapters import HTTPAdapter


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "sipakmed_official"
BASE = "https://www.cs.uoi.gr/~marina/SIPAKMED"
ARCHIVES = {
    "Superficial-Intermediate": "im_Superficial-Intermediate.7z",
    "Parabasal": "im_Parabasal.7z",
    "Koilocytotic": "im_Koilocytotic.7z",
    "Dyskeratotic": "im_Dyskeratotic.7z",
    "Metaplastic": "im_Metaplastic.7z",
}
IMAGE_SUFFIXES = {".bmp", ".jpg", ".jpeg", ".png", ".tif", ".tiff"}
USER_AGENT = "ANONG-Ai research downloader/1.1"
_THREAD_LOCAL = threading.local()


class LinkParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.links.append(href)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def session() -> requests.Session:
    current = getattr(_THREAD_LOCAL, "session", None)
    if current is None:
        current = requests.Session()
        current.headers.update({"User-Agent": USER_AGENT})
        current.mount("https://", HTTPAdapter(pool_connections=1, pool_maxsize=1, max_retries=0))
        _THREAD_LOCAL.session = current
    return current


def valid_existing_file(path: pathlib.Path) -> bool:
    if not path.exists() or path.stat().st_size <= 1024:
        return False
    if path.suffix.lower() == ".bmp":
        with path.open("rb") as handle:
            return handle.read(2) == b"BM"
    return True


def unlink_with_retry(path: pathlib.Path) -> None:
    for attempt in range(5):
        try:
            path.unlink(missing_ok=True)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.2 * (attempt + 1))


def download(url: str, destination: pathlib.Path, force: bool, quiet: bool = False) -> None:
    if valid_existing_file(destination) and not force:
        if not quiet:
            print(f"[skip] {destination.name} ({destination.stat().st_size / 1e6:.1f} MB)")
        return
    partial = destination.with_suffix(destination.suffix + ".part")
    partial.unlink(missing_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "ANONG-Ai research downloader/1.0"})
    if not quiet:
        print(f"[download] {url}")
    with urllib.request.urlopen(request, timeout=600) as response, partial.open("wb") as handle:
        total = int(response.headers.get("Content-Length", "0"))
        received = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
            received += len(chunk)
            if total:
                if not quiet:
                    print(f"\r  {received / 1e6:.1f}/{total / 1e6:.1f} MB", end="")
    if not quiet:
        print()
    partial.replace(destination)


def download_persistent(url: str, destination: pathlib.Path, force: bool) -> None:
    if valid_existing_file(destination) and not force:
        return
    partial = destination.with_suffix(destination.suffix + ".part")
    unlink_with_retry(partial)
    with session().get(url, stream=True, timeout=(30, 120)) as response:
        response.raise_for_status()
        expected = int(response.headers.get("Content-Length", "0"))
        received = 0
        with partial.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=256 * 1024):
                if chunk:
                    handle.write(chunk)
                    received += len(chunk)
    if expected and received != expected:
        unlink_with_retry(partial)
        raise OSError(f"truncated response: expected {expected} bytes, received {received}")
    partial.replace(destination)
    if not valid_existing_file(destination):
        unlink_with_retry(destination)
        raise OSError("downloaded file failed basic format validation")


def directory_files(url: str, suffixes: tuple[str, ...]) -> list[str]:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=(30, 120))
    response.raise_for_status()
    listing = response.text
    parser = LinkParser()
    parser.feed(listing)
    return sorted({link for link in parser.links if link.lower().endswith(suffixes) and "/" not in link})


def download_direct_cropped(force: bool, workers: int, include_contours: bool) -> dict:
    classes_dir = OUT / "classes"
    classes_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for class_name in ARCHIVES:
        source_dir = f"{BASE}/im_{class_name}/CROPPED/"
        suffixes = (".bmp", ".dat") if include_contours else (".bmp",)
        names = directory_files(source_dir, suffixes)
        target_dir = classes_dir / class_name / "CROPPED"
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"[index] {class_name}: {len(names)} files")

        def fetch(name: str) -> dict:
            destination = target_dir / name
            last_error = None
            for attempt in range(20):
                try:
                    download_persistent(source_dir + name, destination, force)
                    return {
                        "name": name,
                        "bytes": destination.stat().st_size,
                        "sha256": sha256(destination),
                    }
                except Exception as error:  # network retries are recorded by final failure
                    last_error = error
                    unlink_with_retry(destination.with_suffix(destination.suffix + ".part"))
                    time.sleep(min(30, 2 + attempt * 2))
            raise RuntimeError(f"failed to download {source_dir + name}: {last_error}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            files = list(executor.map(fetch, names))
        image_files = [file for file in files if file["name"].lower().endswith(".bmp")]
        records.append({
            "class": class_name,
            "directory_url": source_dir,
            "image_count": len(image_files),
            "total_image_bytes": sum(file["bytes"] for file in image_files),
            "files": files,
        })
    return {
        "dataset": "SIPaKMeD",
        "official_page": "https://www.cs.uoi.gr/~marina/sipakmed.html",
        "paper": "https://www.cs.uoi.gr/~sfikas/sipakmed2018.pdf",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "method": "direct official CROPPED directory download",
        "use_note": "Publicly available for experimental purposes; cite Plissiti et al., ICIP 2018.",
        "classes": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--keep-archives", action="store_true")
    parser.add_argument("--archives", action="store_true", help="Download large class archives instead of cropped cells")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--include-contours", action="store_true")
    args = parser.parse_args()

    if not args.archives:
        manifest = download_direct_cropped(args.force, args.workers, args.include_contours)
        (OUT / "provenance_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(json.dumps({
            "dataset": manifest["dataset"],
            "retrieved_utc": manifest["retrieved_utc"],
            "counts": {record["class"]: record["image_count"] for record in manifest["classes"]},
        }, indent=2))
        return

    archive_dir = OUT / "archives"
    extracted_dir = OUT / "classes"
    archive_dir.mkdir(parents=True, exist_ok=True)
    extracted_dir.mkdir(parents=True, exist_ok=True)
    records = []

    for class_name, filename in ARCHIVES.items():
        url = f"{BASE}/{filename}"
        archive = archive_dir / filename
        target = extracted_dir / class_name
        download(url, archive, args.force)
        checksum = sha256(archive)
        if args.force and target.exists():
            shutil.rmtree(target)
        if not target.exists() or not any(target.rglob("*")):
            target.mkdir(parents=True, exist_ok=True)
            print(f"[extract] {filename} -> {target}")
            with py7zr.SevenZipFile(archive, mode="r") as package:
                package.extractall(path=target)
        images = [p for p in target.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES]
        records.append({
            "class": class_name,
            "url": url,
            "archive": str(archive.relative_to(ROOT)),
            "archive_bytes": archive.stat().st_size,
            "sha256": checksum,
            "image_count_including_masks": len(images),
        })

    manifest = {
        "dataset": "SIPaKMeD",
        "official_page": "https://www.cs.uoi.gr/~marina/sipakmed.html",
        "paper": "https://www.cs.uoi.gr/~sfikas/sipakmed2018.pdf",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "use_note": "Publicly available for experimental purposes; cite Plissiti et al., ICIP 2018.",
        "archives": records,
    }
    (OUT / "provenance_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if not args.keep_archives:
        for record in records:
            (ROOT / record["archive"]).unlink(missing_ok=True)
        try:
            archive_dir.rmdir()
        except OSError:
            pass
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

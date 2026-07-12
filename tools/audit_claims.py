from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_TARGETS = [
    "README.md",
    "CLAUDE.md",
    "HONEST_STATUS.md",
    "FINAL_SUBMISSION_PACKAGE.md",
    "docs/PROJECT_HARDENING_STATUS.md",
    "docs/CLAIMS_LEDGER.md",
    "docs/DATASET_MODEL_CARD.md",
    "docs/VALIDATION_ROADMAP.md",
    "docs/RISK_REGISTER.md",
    "docs/THINPREP_HPV_FRAMING.md",
    "docs/THAI_THINPREP_DATA_PROTOCOL.md",
    "docs/UNCERTAINTY_AND_ABSTENTION_POLICY.md",
    "docs/PATIENT_REPORT_SAFETY_SPEC.md",
    "docs/READER_STUDY_PROTOCOL.md",
    "docs/ERROR_ANALYSIS_PLAN.md",
    "docs/CLAUDE_HANDOFF_SOLVE_WSEEC_2026.md",
    "web-react/src",
]

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    "web-dist",
    "models",
    "logs",
    "_archive",
    "data/raw",
}

PATTERNS = [
    ("HPV infection detection", re.compile(r"\b(detects?|detected|detecting)\s+HPV\b", re.I)),
    ("Thai HPV direct detection", re.compile(r"ตรวจพบเชื้อ\s*HPV|ตรวจหาเชื้อ\s*HPV(?!\s*DNA/RNA\s*โดยตรง)", re.I)),
    ("Clinical readiness", re.compile(r"ready\s+for\s+clinical\s+use|พร้อมใช้(?:งาน)?ทางคลินิก", re.I)),
    ("Thai validation overclaim", re.compile(r"validated\s+in\s+Thailand|ผ่านการตรวจสอบในไทย", re.I)),
    ("Full calibration overclaim", re.compile(r"fully\s+calibrated|well[- ]calibrated|calibration\s+สมบูรณ์", re.I)),
    ("99 percent accuracy", re.compile(r"\b99(?:\.\d+)?%\s+(?:accurate|accuracy|แม่นยำ)|แม่นยำ\s*99", re.I)),
    ("KOIL validated overclaim", re.compile(r"KOIL\s+detection\s+works|ตรวจ\s*KOIL\s*ได้", re.I)),
    ("Diagnosis overclaim", re.compile(r"\bdiagnoses?\s+(?:cervical\s+)?cancer\b|วินิจฉัย(?:โรค)?มะเร็ง", re.I)),
]

ALLOW_CONTEXT = [
    "do not",
    "does not",
    "ห้าม",
    "อย่า",
    "not ",
    "not_",
    "not:",
    "**not**",
    "not intended",
    "not yet",
    "without",
    "ไม่ใช่",
    "ไม่ได้",
    "forbidden",
    "unsafe",
    "red flags",
    "stop and review",
    "claims to avoid",
    "do not claim",
    "must not claim",
    "no claim",
    "requiring",
    "asked",
    "โดยไม่ระบุ",
    "public benchmarks",
    "controlled",
    "benchmark",
]


def iter_files(all_files: bool) -> list[Path]:
    if all_files:
        files: list[Path] = []
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            if any(rel == d or rel.startswith(d + "/") for d in EXCLUDE_DIRS):
                continue
            if rel == "tools/audit_claims.py":
                continue
            if path.suffix.lower() in {".md", ".txt", ".py", ".ts", ".tsx", ".json"}:
                files.append(path)
        return sorted(files)

    files = []
    for item in DEFAULT_TARGETS:
        path = ROOT / item
        if path.is_dir():
            files.extend(
                p
                for p in path.rglob("*")
                if p.is_file() and p.suffix.lower() in {".ts", ".tsx", ".md"}
            )
        elif path.exists():
            files.append(path)
    return sorted(set(files))


def is_allowed_context(line: str, previous: list[str] | None = None) -> bool:
    context = line.lower()
    if previous:
        context = "\n".join(previous[-10:]).lower() + "\n" + context
    return any(token in context for token in ALLOW_CONTEXT)


def audit(files: list[Path]) -> int:
    findings = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            findings.append((rel, 0, "READ_ERROR", str(exc)))
            continue

        previous_lines: list[str] = []
        for lineno, line in enumerate(text.splitlines(), start=1):
            for label, pattern in PATTERNS:
                if pattern.search(line) and not is_allowed_context(line, previous_lines):
                    findings.append((rel, lineno, label, line.strip()))
            previous_lines.append(line)

    if not findings:
        print("claim audit passed: no risky unqualified claims found")
        return 0

    print(f"claim audit found {len(findings)} risky line(s):")
    for rel, lineno, label, line in findings:
        print(f"{rel}:{lineno}: {label}: {line}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit CerviCo-Pilot claims for risky wording.")
    parser.add_argument("--all", action="store_true", help="scan the whole repository, excluding generated/heavy dirs")
    args = parser.parse_args()
    return audit(iter_files(args.all))


if __name__ == "__main__":
    raise SystemExit(main())

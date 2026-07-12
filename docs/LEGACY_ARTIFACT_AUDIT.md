# Legacy Artifact Audit

Last updated: 2026-07-06

## Purpose

The repository contains many generated reports, proposal variants, pitch drafts,
and burn artifacts from earlier sessions. Some are useful historical material,
but they are not all current source-of-truth.

This audit defines what can be trusted now and what must be regenerated before
public use.

## Current Source Of Truth

Use these before any generated artifact:

- `README.md`
- `CLAUDE.md`
- `HONEST_STATUS.md`
- `docs/PROJECT_HARDENING_STATUS.md`
- `docs/CLAIMS_LEDGER.md`
- `docs/DATASET_MODEL_CARD.md`
- `docs/VALIDATION_ROADMAP.md`
- `docs/RISK_REGISTER.md`
- `docs/THINPREP_HPV_FRAMING.md`
- `docs/CALIBRATION_EXPERIMENT_REPORT.md`
- `docs/ERROR_ANALYSIS_REPORT_HERLEV.md`

Metrics source:

- `models/test_metrics.json`
- `models/triage_metrics.json`
- `models/cv_results.json`
- `models/calibration_temperature.json`

## Legacy Artifact Classes

| Artifact class | Status | Rule |
| --- | --- | --- |
| `report/*.json`, `report/*.txt`, old batch reports | Legacy outputs | Regenerate before use |
| `proposal/*.md/html/docx` | Drafts | Audit against `CLAIMS_LEDGER.md` before use |
| older pitch decks/scripts | Drafts | Update title, metrics, HPV wording before use |
| synthetic/burn reports | Historical only | Do not use as evidence |
| docs with SOTA 99% references | Context only | Must say external benchmark context, not our result |

## Generator Patch

`report/make_full_report.py` was updated to avoid hard HPV language:

- old: "HPV-related cell changes detected"
- new: "HPV-related morphology risk noted"
- old: "Recommend HPV DNA test to identify virus type"
- new: "Consider HPV DNA/RNA testing if clinically appropriate"

Generated report files created before this change may still contain older text.
Treat them as stale unless regenerated.

## Audit Commands

Run:

```powershell
python tools\audit_claims.py
python tools\audit_claims.py --all
```

Passing audit does not prove the artifact is up to date; it only catches risky
unqualified wording. Always compare metrics to canonical JSON.

## Remaining Legacy Risk

The repo still contains historical generated files that mention:

- HPV DNA testing recommendations in old KOIL examples;
- external >99% benchmark papers;
- old competition-specific framing;
- synthetic/burn-era volume claims.

These are acceptable as archived context but should not be copied into new
submission/report text without rewriting.

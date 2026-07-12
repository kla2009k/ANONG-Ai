# Project Hardening Status

Date: 2026-07-07  
Scope: strengthen CerviCo-Pilot as a credible medical-AI prototype before any
competition-specific packaging.

## Current Product Definition

CerviCo-Pilot is a **clinician-in-the-loop cervical cytology screening co-pilot**.
It accepts ThinPrep/Pap-style cytology images, provides a Bethesda-style
5-class abnormality grade, estimates HPV-related morphology risk, shows
explainability, flags uncertainty, and requires clinician sign-off.

The system is **not**:

- a final diagnostic device;
- a replacement for cytotechnologists/pathologists;
- an HPV DNA/RNA test;
- clinically validated in Thailand;
- ready for unsupervised clinical deployment.

## Core Framing

Use this hierarchy everywhere:

| Layer | Role | How to Describe |
| --- | --- | --- |
| 5-class Bethesda-style output | Product identity | Structured cytology screening support |
| HPV-related morphology risk | Clinical explanation layer | Visual risk signals associated with HPV-related cytologic change |
| Binary normal/abnormal triage | Safety layer | High-sensitivity triage to reduce missed abnormal/high-risk cases |
| Grad-CAM | Explainability | Shows regions the model used; physician can challenge it |
| MC Dropout uncertainty | Safety/abstention | Flags low-confidence cases for human review |
| Clinician sign-off | Governance | Prevents automatic diagnosis or patient release |

## Canonical Evidence

Metrics must be copied from:

- `models/test_metrics.json`
- `models/triage_metrics.json`
- `models/cv_results.json`
- `docs/CURVES_CALIBRATION.md`

Current honest checkpoint:

- `models/best_cervical.pt`
- architecture: EfficientNet-B0
- dataset: Herlev real images only, masks excluded
- no synthetic/combined-run metric may be used as public evidence

## Current Metrics Snapshot

Held-out 5-class:

- accuracy: **0.6934**
- macro F1: **0.5545**
- macro AUROC: **0.7311**
- QWK: **0.687**
- HSIL recall: **0.8667**
- SCC recall: **0.5909**
- KOIL recall: **0.0** because Herlev has no KOIL examples

Held-out binary safety layer:

- sensitivity: **1.0**
- specificity: **0.7222**
- AUROC: **0.964**
- AUPRC: **0.9856**
- MCC: **0.8107**
- confusion: **TP 101 / TN 26 / FP 10 / FN 0**
- high-risk catch HSIL+SCC: **1.0**

5-fold CV:

- 5-class accuracy: **0.6904 +/- 0.0618**
- QWK: **0.6981 +/- 0.0866**
- binary sensitivity: **0.9867 +/- 0.0086**
- binary AUROC: **0.9435 +/- 0.0448**

## Hardening Completed

- Hardened Analyze after a reported 0% activation-map defect: added CAM
  degeneracy checks, class-aware fallback with provenance, XAI abstention,
  equal uncropped comparison views, domain-calibrated crop quality checks,
  strict upload validation, backend patient-release gates, deterministic report
  text, and 21 regression tests. Added Docker/Render/GitHub Pages deployment
  configuration and corrected KOIL recall from misleading `0.0000` to `N/A`
  when support is zero. See `docs/ANALYZE_HARDENING_AND_DEPLOYMENT_2026.md`.
- Fixed the live-server import path so advanced quality checks, MC Dropout, and
  multi-method XAI load when Uvicorn starts from `server/`. Added explicit
  `heatmap_source` provenance and reviewed-report HTML/PDF actions to Analyze.
  Verified a real Herlev upload through model inference, advanced Grad-CAM,
  uncertainty gating, clinician confirmation, and a 156 KB downloaded report.
  See `docs/MODEL_XAI_REPORT_E2E_2026.md`.
- Simplified the Anong information architecture from 15 primary navigation
  links to seven core destinations. Removed duplicated homepage quick-action
  and six-step sections, consolidated six supporting tools under Evidence,
  linked report preview from Clinical Workflow, and retained every existing
  route. Production build, claims audit, desktop/mobile route checks, console
  checks, and overflow checks passed. See
  `docs/ANONG_INFORMATION_ARCHITECTURE_2026.md`.
- Rebranded the user-facing web product as **Anong** while retaining
  **CerviCo-Pilot** as the technical/research identity; implemented a
  rose/butter/cream pastel-clinical system, unified Lucide navigation icons,
  updated PWA/export metadata, strengthened contrast, and verified desktop and
  mobile routes. See `docs/ANONG_WEB_REBRAND_2026.md`.
- Migrated the complete product UI to English across all 15 routes, dynamic
  analysis/sign-off/report states, browser metadata, PWA metadata, and exported
  demo HTML. Thai Unicode scans, production build, claim audit, and responsive
  Chromium QA all pass. See `docs/ANONG_ENGLISH_UI_MIGRATION_2026.md`.
- Recovered the honest EfficientNet-B0 checkpoint framing.
- Added ROC/reliability curve generation from canonical evaluation path.
- Added `docs/THINPREP_HPV_FRAMING.md`.
- Added `docs/SFT_WSEEC_STRATEGY.md` while keeping it optional for competition
  packaging.
- Updated web About/Analyze pages to say HPV-related morphology risk, not HPV
  detection.
- Updated API health/predictor notes to mark prototype-only explanation paths.
- Added this project-hardening layer to reduce ambiguity for future agents.
- Added Thai ThinPrep data protocol, uncertainty/abstention policy,
  patient-report safety spec, reader-study protocol, and error-analysis plan.
- Added `tools/audit_claims.py` for lightweight risky-claim checks.
- Added post-hoc temperature-scaling experiment and report.
- Added Herlev error-analysis report and project readiness scorecard.
- Added engineering Herlev error-case gallery from existing sample artifacts.
- Added legacy artifact audit and patched `report/make_full_report.py` HPV wording.
- Updated web Analyze result card with a separate HPV-related morphology risk
  panel and stricter high-uncertainty patient-report gate.
- Added localStorage demo audit trail for clinician confirm/edit/reject actions.
- Added browser/accessibility verification checklist and Thai data intake checklist.
- Added DentScanAI-inspired web hardening: History page, project Q&A assistant,
  homepage workflow cards, sample class filters, and shared local audit utility.
- Added 1-8 web/docs expansion: sidebar app shell, dashboard, case gallery,
  clinical workflow page, report preview, judge Q&A bank, submission master, and
  failure-mode/human-factors analysis.
- Verified the 1-8 expansion with production build, claim audit, and runtime
  browser smoke checks.
- Added submission-readiness layer: intended-use statement, web demo runbook,
  1/3/5-minute pitch scripts, WSEEC poster content, SFT/WSEEC package map, and
  server-side audit roadmap.
- Added complete DOCX report booklet with tables, charts, cytology images,
  Grad-CAM examples, appendices, and build notes.
- Added formal Thai research-report DOCX for serious submission packaging,
  with cover/approval pages, Thai/English abstracts, Chapters 1-5,
  references, appendices, 21 tables, 7 figures, and build notes.
- Polished the formal research report with sharper Thai/English abstracts,
  stronger Chapter 1 research framing, research questions, formal bibliography,
  and a Word/PDF final-polish checklist.
- Hardened the web app for competition demo: renamed package metadata to
  CerviCo-Pilot, added evidence/report downloads, judge demo mode, report
  export/copy controls, mock server-side audit endpoints, and deploy QA docs.
- Added a production-hardening demo layer: SQLite hash-chain audit storage,
  backend readiness/metrics endpoints, server-side HTML report export, and a
  `/deployment` page that separates demo readiness from hospital-pilot gaps.
- Added the official-format WSEEC 2026 English full paper in Word and PDF,
  constrained to 12 main pages plus references, with format audit and final
  submission checklist.
- Added a refined WSEEC polished version with matched Word/PDF pagination,
  exactly 12 pages, improved cover, headers/page numbers, table hierarchy,
  six figures, and full render edge QA.

## Remaining Weak Spots

1. **Thai ThinPrep data missing**
   - Current model is not Thai-domain validated.
   - Need de-identified Thai ThinPrep/LBC images with expert labels.

2. **HPV endpoint missing**
   - Current HPV story is morphology-based.
   - Need paired HPV DNA/RNA status to evaluate true HPV-positive risk
     prediction.

3. **KOIL not validated**
   - Herlev has no KOIL examples.
   - KOIL must remain a Phase 2 target.

4. **Calibration remains Phase 1 only**
   - Temperature scaling has been run on Herlev validation/test splits and
     improved held-out ECE/Brier in `docs/CALIBRATION_EXPERIMENT_REPORT.md`.
   - It is still not external Thai ThinPrep calibration.
   - Do not claim "fully calibrated" or "clinically calibrated."

5. **No reader study**
   - Need cytotechnologist/pathologist comparison with and without AI.

6. **No prospective clinical workflow trial**
   - Current evidence is retrospective/public-dataset only.

## Next Best Work

The next work should be project strengthening, not more pitch polish:

1. Build a Thai ThinPrep data dictionary and annotation protocol.
2. Add a patient/report safety spec: what can be shown before clinician sign-off.
3. Add an uncertainty threshold policy: when to abstain and escalate.
4. Add calibration experiment script and report.
5. Add a reader-study protocol.
6. Add a small claim-audit script or checklist before generating any proposal.

Status of this list after 2026-07-07 hardening:

- Thai ThinPrep protocol: `docs/THAI_THINPREP_DATA_PROTOCOL.md`
- Patient report safety: `docs/PATIENT_REPORT_SAFETY_SPEC.md`
- Uncertainty/abstention: `docs/UNCERTAINTY_AND_ABSTENTION_POLICY.md`
- Reader study: `docs/READER_STUDY_PROTOCOL.md`
- Error analysis: `docs/ERROR_ANALYSIS_PLAN.md`
- Claim audit: `tools/audit_claims.py`
- Calibration experiment: `ml/scripts/calibrate_temperature.py` and
  `docs/CALIBRATION_EXPERIMENT_REPORT.md`
- Error analysis: `docs/ERROR_ANALYSIS_REPORT_HERLEV.md`
- Error-case gallery: `docs/HERLEV_ERROR_CASE_GALLERY.md`
- Readiness: `docs/PROJECT_READINESS_SCORECARD.md`
- Legacy generated artifacts: `docs/LEGACY_ARTIFACT_AUDIT.md`
- Browser/accessibility verification: `docs/BROWSER_ACCESSIBILITY_VERIFICATION.md`
- Thai data intake: `docs/THAI_DATA_INTAKE_CHECKLIST.md`
- Web hardening after DentScanAI comparison: `/history` and `/ask` now exist;
  `/analyze` sample filtering and audit-trail reuse are verified.
- Additional web completion: `/gallery`, `/workflow`, and `/reports` now exist.
- Submission docs: `docs/JUDGE_QA_BANK.md`, `docs/SUBMISSION_MASTER.md`,
  `docs/FAILURE_MODE_AND_HUMAN_FACTORS.md`.
- Demo/submission docs: `docs/INTENDED_USE_STATEMENT.md`,
  `docs/WEB_DEMO_RUNBOOK.md`, `docs/PITCH_SCRIPT_1_3_5MIN.md`,
  `docs/POSTER_CONTENT_WSEEC.md`, `docs/SFT_WSEEC_SUBMISSION_PACKAGE.md`,
  `docs/SERVER_SIDE_AUDIT_ROADMAP.md`.
- Complete report booklet: `docs/CerviCo_Pilot_Complete_Report_2026.docx`,
  `docs/BOOKLET_BUILD_NOTES.md`, generated by `tools/build_full_booklet.py`.
- Still missing: manual reviewed image-level error gallery and real Thai data
- External evidence review: `docs/EXTERNAL_EVIDENCE_REVIEW_2026.md`
- Source citation ledger: `docs/SOURCE_CITATION_LEDGER.md`

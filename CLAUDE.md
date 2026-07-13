# Project_CervicalAI — Anong · CerviCo-Pilot

> **Critical KOIL update (2026-07-13):** Read
> `docs/KOIL_REAL_DATA_VALIDATION_2026.md` before changing model claims, paper
> metrics, inference, reports, or the web. KOIL is now an independent SIPaKMeD
> morphology endpoint with real locked-test evidence. It is not a fifth
> Bethesda grade and not an HPV infection test. Historical KOIL placeholder
> text later in this file must not override the new canonical report.

Clinician-in-the-loop cervical cytology screening co-pilot. It reads
ThinPrep/Pap-style images, gives a four-class Bethesda-style abnormality grade,
adds an independent KOIL morphology endpoint and binary safety-triage view, estimates HPV-related
morphology risk, and flags cases for expert review. Every output is advisory
and a clinician signs off.

## Session start
1. Read `PRODUCT.md` and `docs/ANONG_WEB_REBRAND_2026.md` before any web/brand change.
2. Read workspace `data/hot-cache.md` for current context.
3. Task list: `docs/TOMORROW_FABLE_PLAN.md`.
4. Read current hardening docs before making claims:
   - `docs/PROJECT_HARDENING_STATUS.md`
   - `docs/CLAIMS_LEDGER.md`
   - `docs/VALIDATION_ROADMAP.md`
   - `docs/RISK_REGISTER.md`
   - `docs/DATASET_MODEL_CARD.md`
   - `docs/THAI_THINPREP_DATA_PROTOCOL.md`
   - `docs/UNCERTAINTY_AND_ABSTENTION_POLICY.md`
   - `docs/PATIENT_REPORT_SAFETY_SPEC.md`
   - `docs/READER_STUDY_PROTOCOL.md`
   - `docs/ERROR_ANALYSIS_PLAN.md`
   - `docs/CALIBRATION_EXPERIMENT_REPORT.md`
   - `docs/ERROR_ANALYSIS_REPORT_HERLEV.md`
   - `docs/HERLEV_ERROR_CASE_GALLERY.md`
   - `docs/PROJECT_READINESS_SCORECARD.md`
   - `docs/LEGACY_ARTIFACT_AUDIT.md`
   - `docs/BROWSER_ACCESSIBILITY_VERIFICATION.md`
   - `docs/THAI_DATA_INTAKE_CHECKLIST.md`
   - `docs/EXTERNAL_EVIDENCE_REVIEW_2026.md`
   - `docs/SOURCE_CITATION_LEDGER.md`
   - `docs/JUDGE_QA_BANK.md`
   - `docs/SUBMISSION_MASTER.md`
   - `docs/FAILURE_MODE_AND_HUMAN_FACTORS.md`
   - `docs/INTENDED_USE_STATEMENT.md`
   - `docs/WEB_DEMO_RUNBOOK.md`
   - `docs/PITCH_SCRIPT_1_3_5MIN.md`
   - `docs/POSTER_CONTENT_WSEEC.md`
   - `docs/SFT_WSEEC_SUBMISSION_PACKAGE.md`
   - `docs/SERVER_SIDE_AUDIT_ROADMAP.md`
   - `docs/BOOKLET_BUILD_NOTES.md`
   - `docs/FORMAL_REPORT_BUILD_NOTES.md`
   - `docs/FORMAL_REFERENCES_BIBLIOGRAPHY.md`
   - `docs/FORMAL_REPORT_FINAL_POLISH_CHECKLIST.md`
   - `docs/WEB_DEPLOY_READY_CHECKLIST.md`
   - `docs/WEB_QA_REPORT_2026_07_07.md`
   - `docs/WEB_PRODUCTION_HARDENING_REPORT.md`
   - `docs/wseec_2026/WSEEC_2026_FORMAT_AUDIT.md`
   - `docs/wseec_2026/WSEEC_2026_SUBMISSION_CHECKLIST.md`
5. Metrics are canonical in JSON — never hardcode/invent. Pull from
   `models/test_metrics.json`, `models/triage_metrics.json`, `models/cv_results.json`.

## Hard rules
- Never fabricate metrics. Read the JSON files.
- Cleanup = move to `_archive/`, never delete.
- Web changes: `cd web-react && npm run build` must pass before saying done.
- Web display brand = **Anong**. Technical/research identity = **CerviCo-Pilot**.
  Do not globally replace either name; use `Anong · CerviCo-Pilot` when both
  contexts must be visible.
- Product UI language = **English only**. Before saying a web change is done,
  scan `src`, `index.html`, and non-document `public/` files for Thai Unicode.
  Downloadable research documents may retain their original submission language.
- Numbers must match across web (`web-react/src/lib/data.ts` METRICS) = docx = docs/*.md.
- Four-class Bethesda-style grade output (NILM/LSIL/HSIL/SCC) = primary grade endpoint.
- KOIL is an independent morphology endpoint trained and locked-tested on SIPaKMeD.
- Binary normal/abnormal triage = safety layer, not the whole product.
- HPV wording must be "HPV-related morphology risk"; never say the model detects
  HPV infection or replaces HPV DNA/RNA testing.
- KOIL evidence is internal SIPaKMeD conventional Pap-smear validation only; Thai ThinPrep and paired HPV validation remain future work.
- When unsure, ask before guessing.
- Before publishing or generating new claims, run:
  `python tools/audit_claims.py`
- Legacy generated reports/proposals are not source-of-truth. Check
  `docs/LEGACY_ARTIFACT_AUDIT.md` and regenerate before public use.
- The web demo has a localStorage audit trail for demo sign-off only. It is not a
  server-side regulated audit log. For pilot planning, read
  `docs/SERVER_SIDE_AUDIT_ROADMAP.md`.
- Live upload requires FastAPI on port 8003. `server/predictor.py` must add the
  project root to `sys.path` before importing `ml.*`; otherwise advanced XAI and
  MC Dropout silently degrade. Every live response now exposes
  `heatmap_source`; only `advanced_gradcam` or `legacy_gradcam` may be described
  as Grad-CAM. Read `docs/MODEL_XAI_REPORT_E2E_2026.md`.
- Analyze shows Original, Grad-CAM, and thresholded Activation Regions together.
  Activation Regions are derived from the strongest Grad-CAM response and must
  always be described as attention boundaries, never cell/lesion segmentation.
- Reviewed report downloads are research/demo pre-screen reports, not signed or
  regulated medical reports. Analyze unlocks reviewed HTML and Print/Save PDF
  after clinician confirm/edit; high uncertainty keeps the patient section locked.
- Analyze XAI must validate CAM maps before display. Flat, non-finite, or missing
  maps abstain; Grad-CAM may fall back only to a valid class-aware method with
  honest provenance. Never show heuristic spotlight output in model mode. The
  quality gate uses `single_cell_crop_herlev_v1`, not slide-level cellularity.
  Read `docs/ANALYZE_HARDENING_AND_DEPLOYMENT_2026.md`.
- When class support is zero, report recall as `N/A (not estimable)`, not `0.0`.
  This rule applies to the historical Herlev grade checkpoint. Report KOIL only
  from the independent SIPaKMeD endpoint and its locked-test metrics.
- External sources support public-health/governance framing only. They do not
  create model-performance claims. Read `docs/SOURCE_CITATION_LEDGER.md` before
  using WHO/CDC/FDA/CONSORT-AI/DECIDE-AI claims.

## Build / run
- Web: `web-react/` (Vite + React) → build to `web-dist/`
- API: `server/` (FastAPI, uvicorn :8003) — predictor.analyze
- Static serve `web-dist/` on :8090
- Web app pages now include `/`, `/analyze`, `/gallery`, `/workflow`,
  `/reports`, `/research-report`, `/demo`, `/deployment`, `/history`, `/performance`,
  `/knowledge`, `/ask`, `/model`, `/about`, and `/settings`.
- Primary navigation is intentionally limited to seven routes: Overview,
  Analyze, Case Gallery, Clinical Workflow, Performance, Evidence, and About.
  Keep secondary routes out of the primary navigation unless the information
  architecture is deliberately revised. `/reports` is linked from Workflow;
  `/demo`, `/deployment`, `/knowledge`, `/ask`, and `/model` are consolidated
  under Evidence; `/history` is linked from Analyze; theme control replaces a
  primary Settings link. See `docs/ANONG_INFORMATION_ARCHITECTURE_2026.md`.
- Before a live demo, read `docs/WEB_DEMO_RUNBOOK.md`.
- Complete report booklet: `docs/CerviCo_Pilot_Complete_Report_2026.docx`
  generated by `tools/build_full_booklet.py`. Read
  `docs/BOOKLET_BUILD_NOTES.md` before editing/regenerating it.
- Formal Thai research report: `docs/CerviCo_Pilot_Formal_Research_Report_2026_Polished.docx`
  generated by `tools/build_formal_research_report.py`. This is the more
  serious 30+ page submission-style report; read
  `docs/FORMAL_REPORT_BUILD_NOTES.md` before editing/regenerating it.
- Preferred WSEEC 2026 English full paper:
  `docs/wseec_2026/CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.docx`
  and matching PDF, generated by `tools/build_wseec_full_paper_polished.py`
  and exported through Word. It follows the official guidebook/template and is
  exactly 12 pages in both Word and PDF.
- Public GitHub Pages demo: `https://kla2009k.github.io/ANONG-Ai/` (verified
  2026-07-13, commit `43692a8`). The public static build supports precomputed
  Herlev cases and evidence downloads. Live uploads still require FastAPI on
  `:8003` or a provisioned backend configured through `VITE_API_URL`.

## Web UI design (อ่านก่อนแตะ UI / ทำเว็บ)
- **`PRODUCT.md`** = users/purpose/personality/anti-references สำหรับ product UI
- **`docs/ANONG_WEB_REBRAND_2026.md`** = naming, palette, contrast, QA และ guardrails ล่าสุด
- **`IMPECCABLE_BRIEF.md`** (โฟลเดอร์นี้) = brand/สี/tone/screens สำหรับหน้าเว็บ
- **`../_SHARED_GRADCAM_UI.md`** = spec heatmap/explainability overlay (ใช้ร่วมทุกโปรเจกต์ med-AI)
- สไตล์: **Anong pastel clinical** — ชมพูกุหลาบ + เหลืองเนย + ครีม, English-only, สุขุม อ่านง่าย และไม่เป็นเว็บความงาม
- จุดขาย = **explainability** (Phase 1 LOCKED) → cell gallery + dual-layer "Where/Why"
- เริ่มงาน UI: อ่าน context ทั้ง 3 ไฟล์ → build → browser smoke desktop/mobile → claim audit
- Reference: Hologic Genius ใช้เฉพาะ information hierarchy/workflow ไม่ใช่ชุดสี

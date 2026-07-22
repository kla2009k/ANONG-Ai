# Claude Handoff: CerviCo-Pilot for Samsung Solve for Tomorrow 2026 + WSEEC

## Whole-site CRIC evidence consistency audit — 2026-07-22

- Updated Overview, About, Model Card, Demo Mode, Settings, Navbar, and Case
  Gallery so they distinguish the deployed Herlev upload baseline from the
  separate CRIC four-grade research candidate.
- The repeated public CRIC wording retains all required qualifiers: `91.7%`
  selective accuracy, `94.1%` coverage, `88.8%` full-cohort accuracy, and
  research/not-deployed status.
- The Model Card additionally exposes SCC recall `50.3%` and the selective
  accuracy CI `89.54-93.46%`.
- The Analyze route intentionally continues to describe the Herlev upload
  checkpoint. The CRIC checkpoint has not replaced live uploaded-image
  inference.
- Updated the public dataset/model card, claims ledger, and deployment
  checklist mirrors. Added a regression test covering cross-route CRIC wording.

## Genuine 90%+ selective CRIC result — 2026-07-22

- Downloaded and verified all 395 CRIC parent microscope images containing a
  directly supported NILM/LSIL/HSIL/SCC label.
- Built 10,003 nucleus-centered cell records. ASC-US and ASC-H were excluded,
  not remapped into the four-grade endpoint.
- Completed five-fold parent-image-disjoint training and out-of-fold testing.
- Pooled full-cohort accuracy is `88.83%`, not above 90%.
- At prespecified confidence threshold `0.60`, selective accuracy is `91.66%`
  at `94.08%` coverage; 592/10,003 cells are abstained for human review.
- Parent-image bootstrap 95% CI is `89.54-93.46%` for selective accuracy and
  `92.76-95.28%` for coverage.
- Pooled macro F1 is `74.10%`; SCC recall is only `50.31%`. The model is a
  research candidate and must not replace the deployed screening workflow.
- Required headline: `91.7% selective four-grade accuracy at 94.1% coverage on
  CRIC conventional Pap-smear cells; full-cohort accuracy 88.8%.`
- Do not shorten this to `91.7% model accuracy`, ThinPrep accuracy, clinical
  accuracy, or HPV detection accuracy.
- Full report: `docs/CRIC_GRADE_5FOLD_REPORT_2026_07_22.md`.
- Public artifact: `web-react/public/evidence/cric_grade_5fold_summary.json`.

## UI and grade-model update — 2026-07-22

- Removed the `Thai ThinPrep / Missing` and `Clinical use / Not ready` cards
  from the Overview readiness scorecard at the team's request. The underlying
  scientific limitations remain documented elsewhere and were not converted
  into positive claims.
- Removed the precomputed Herlev sample selector from Analyze. Analyze is now
  focused on uploaded-image workflow and links to Case Gallery for evidence.
- Added a default `Model outputs` view to Case Gallery. Each held-out example
  shows the original image and class-specific Grad-CAM side by side, plus true
  label, prediction, correctness, confidence, and uncertainty.
- Performance now distinguishes the deployed baseline (`0.690 +/- 0.062`
  five-fold CV accuracy), research v3 full-cohort locked-test accuracy (`78.8%`),
  and selective accuracy (`94.0%` at `60.6%` coverage). Selective accuracy must
  never be presented without its coverage and abstention rate.
- A new lower-regularization run reached only `67.2%` full-cohort accuracy and
  `36.7%` HSIL recall. It was rejected. The artifact is
  `models/grade_research_v3/b0_320_balanced_20260724.json`.
- Do not edit the site to claim 90-95% full-cohort four-grade accuracy. No
  current artifact supports that claim. Reaching that range credibly requires
  more patient/slide-disjoint expert-labelled data, a pre-registered external
  test, and repeated source-disjoint validation rather than more test-set
  tuning.

> **Slide visual asset update 2026-07-22:** A reproducible 17-image,
> presentation-ready evidence set now exists under
> `presentation/slide_assets_2026/`. Every PNG is 1920x1080, uses canonical
> metrics and carries dataset/claim boundaries. The complete local archive is
> `presentation/slide_assets_2026.zip`. Rebuild with
> `python tools/build_slide_visuals.py`.

The same generator also creates
`presentation/slide_assets_2026/ANONG_Evidence_Visuals_2026.pptx`, a 16:9
PowerPoint containing the 17 PNGs as full-slide images. It is a visual asset
deck for selection/reordering, not the final competition narrative deck.

## Slide-ready evidence visuals (2026-07-22)

The generator `tools/build_slide_visuals.py` reads canonical JSON and produces:

1. system evidence map;
2. dataset provenance and missing-evidence statement;
3. Herlev binary triage evidence;
4. recall comparison with explicit Herlev/SIPaKMeD separation;
5. four-class Herlev grade confusion matrix;
6. independent binary KOIL confusion matrix;
7. SIPaKMeD five-morphology matrix;
8. KOIL ROC and precision-recall curves reconstructed from 641 locked-test
   predictions;
9. KOIL calibration plot;
10. four-category Herlev Grad-CAM examples;
11. KOIL Grad-CAM audit with TP, near-threshold, FN and FP;
12. every KOIL FN plus the five highest-scoring FPs;
13. CCCID v2 19/20 positive-only LBC challenge;
14. HPV image/laboratory/context claim boundary;
15. clinician-in-the-loop report release workflow;
16. validation roadmap;
17. closing evidence summary.

`00_contact_sheet.jpg` is for asset selection only. `manifest.json` stores
dimensions, byte size, SHA-256, canonical sources and non-negotiable claim
boundaries. `README.md` separates recommended main-deck visuals from appendix
visuals. Do not remove dataset names, sample sizes or limitation captions when
cropping these images.

Canonical quantitative inputs:

- `models/triage_metrics.json`
- `models/cv_results.json`
- `models/koil_sipakmed/test_metrics.json`
- `models/koil_sipakmed/locked_test_predictions.json`
- `models/koil_sipakmed/evaluation/error_analysis.json`
- `models/koil_sipakmed/evaluation/cccid_koil_20_case_challenge.json`

Visual QA was performed on the contact sheet and full-resolution Grad-CAM,
error-analysis, CCCID and HPV-boundary slides. The CCCID layout was regenerated
after detecting and removing an overlap between the 20-case glyphs and summary
metrics.

> **Performance visualization update 2026-07-22:** `/performance` now exposes
> KOIL in its tables and charts without inserting it as a fifth Herlev grade.
> The top endpoint map identifies each output, dataset, test support and metric;
> the recall chart has an explicit Herlev/SIPaKMeD boundary; and the KOIL
> section includes a labelled 2x2 matrix plus ROC/PR and calibration evidence.
> HPV infection remains visibly `Not developed` with zero paired assay cases.

## Performance visualization update (2026-07-22)

`web-react/src/pages/Performance.tsx` now provides the requested cross-endpoint
view while preserving valid evaluation boundaries:

- Endpoint map: four-class grade, binary safety triage, KOIL morphology, CCCID
  positive-only KOIL challenge, and future molecular HPV endpoint.
- Cross-endpoint recall chart: NILM/LSIL/HSIL/SCC use the Herlev held-out set;
  KOIL uses the independent SIPaKMeD locked test. A visual separator and test
  support labels prevent the bars from implying a shared five-class model.
- KOIL 2x2 matrix: TN=496, FP=12, FN=5, TP=128; positive support 133,
  negative support 508, locked threshold 0.3367, test n=641.
- KOIL metric cards: sensitivity 0.9624, specificity 0.9764, AUROC 0.9912,
  AUPRC 0.9810, F1 0.9377, and ECE 0.0134.
- Existing canonical figures `evidence/koil_test_performance.png` and
  `evidence/koil_calibration.png` are now visible directly on Performance.
- HPV is included in the endpoint table only as a missing paired molecular
  endpoint. It has zero paired test cases and no performance claim.

Do not replace the two valid confusion matrices with a single matrix containing
NILM/LSIL/HSIL/SCC/KOIL. KOIL can coexist with a grade, and the current grade
and KOIL evidence comes from different test datasets.

> **Frontend consolidation update 2026-07-22:** The public navigation now
> centers on six core destinations. KOIL Evidence, HPV Context, and Clinical
> Workflow are combined at `/clinical-evidence`; legacy routes still render the
> same page. The Overview reports 4,049 SIPaKMeD KOIL-task cells and 917 Herlev
> grade-task images as separate evidence pools. A local demo reviewer profile
> was added at `/login`. Full implementation and claim notes are below.

## Frontend consolidation update (2026-07-22)

### Team brief implemented

The sidebar now exposes Overview, Analyze, Clinical Evidence, Case Gallery,
Performance, and Evidence. `web-react/src/pages/ClinicalEvidence.tsx` brings
four previously fragmented topics into one evidence-first page:

1. KOIL development and locked-test evidence, including 4,049 SIPaKMeD cells,
   966 source clusters, confidence intervals, and the 19/20 positive-only CCCID
   challenge limitation.
2. The strict boundary between image morphology, a separately performed
   laboratory HPV assay, and clinician-entered context.
3. A Bethesda-aligned future co-finding architecture for Candida,
   Trichomonas, bacterial-vaginosis pattern, Actinomyces, HSV/CMV-associated
   changes, and reactive/reparative changes.
4. The controlled path from image quality through separate grade and KOIL
   endpoints, XAI/uncertainty review, clinician sign-off, report, and audit.

The Bethesda co-findings are explicitly marked **Not trained**. They must be a
multi-label auxiliary endpoint because a non-neoplastic finding can coexist
with NILM or an epithelial abnormality. They must not become mutually exclusive
cancer-grade classes. Real expert labels, slide/patient grouping, mimic-focused
error analysis, and external ThinPrep validation are required before claims.

### Dataset count shown on Overview

The Overview headlines `4,049 real KOIL-task cells` and separately displays
`917 real grade-task images`. These belong to different datasets, units, and
endpoints. Do not change this to “4,966 training images” or “4,000+ ThinPrep
images”: SIPaKMeD is conventional Pap-smear cropped-cell data. Augmentation
must never be represented as additional real cases.

### Local reviewer profile

`web-react/src/pages/Login.tsx` and `web-react/src/lib/session.ts` store display
name, professional role, optional organization, and creation time in browser
localStorage after acknowledgement. No password is requested. The page includes
a delete control, and navbar state updates immediately.

This is labelled `Local demo workspace`, not secure authentication. GitHub
Pages cannot provide trustworthy clinical authorization. A pilot still needs
an identity provider, server-side sessions, encryption, RBAC, expiry and
revocation, privacy controls, and an immutable audit log. Patient identifiers
must not be entered in this profile.

### Routing and verification

- Canonical combined route: `/clinical-evidence`
- Backward-compatible routes: `/koil`, `/hpv`, `/workflow`
- Reviewer route: `/login`
- GitHub Pages SPA fallbacks include the new routes.
- Evidence version in the public footer: `2026-07-22`.
- `npm.cmd run build`: passed.
- Chromium audit at 1440x1000 and 390x844: no page overflow, console errors,
  broken reference images, overlap, or clipping.
- Local reviewer profile create/delete flow: passed.

### Non-negotiable claims

- `4,049` means SIPaKMeD cells for the independent KOIL morphology task.
- `917` means Herlev images for the separate grade/triage task.
- KOIL morphology is not a Bethesda grade and not an HPV infection test.
- The grade display is a four-class supported subset, not the complete Bethesda
  reporting vocabulary.
- Organism/reactive co-findings are future work with no trained model or metric.
- The reviewer profile is a static demonstration, not production login.

> **Static evidence hardening update 2026-07-21:** The public frontend now
> distinguishes static evidence from live API mode before upload; static mode
> never maps a canned prediction to a new upload. `ReportPreview` uses only
> `GRADE_CLASS_KEYS` for Bethesda-style grade and carries KOIL separately. Five
> de-identified PDFs in `web-react/public/reports/` were generated from real
> local dual-model runs by `tools/generate_public_demo_reports.py`; their
> manifest stores SHA-256 hashes and exposes two clinician-edited grade cases.
> KOIL has a filterable all-20 external challenge explorer, and HPV has a
> deterministic educational state explorer. XAI now supports compare, overlay,
> opacity, zoom, boundary, and download views for separate grade and KOIL
> endpoints. Gallery references have a keyboard/lightbox viewer. GitHub Pages
> generates per-route `index.html` files so deep links return HTTP 200.
>
> Dataset reporting policy: `web-react/public/evidence/dataset_registry.json`
> catalogues ten sources but counts only Herlev + SIPaKMeD (4,966 images) as
> current model-development data. CCCID is a 20-positive external challenge;
> CRIC is a reference atlas; all other records are unused candidates. Never add
> candidate/repository counts to the model training total. No current source
> supplies paired molecular HPV ground truth for a validated HPV endpoint.

> **Web KOIL/HPV information architecture update 2026-07-21:** The English
> Anong frontend now has two first-class routes: `/koil` and `/hpv`. `/koil`
> reads the existing locked SIPaKMeD metrics and CCCID positive-challenge JSON,
> joins challenge probabilities to prespecified reference cases by ID, shows
> KOIL-specific evidence figures, and states the negative-inclusive external
> validation gap. `/hpv` explicitly separates image morphology, a manually
> entered external laboratory HPV result, and report-only clinical context. It
> also explains that age/symptoms do not alter image probabilities. The primary
> navigation intentionally increased from seven to nine items because the team
> requested dedicated KOIL and HPV pages. Overview links to both pages. Build,
> all 43 unit tests, and `python tools/audit_claims.py --all` passed. Browser
> screenshot inspection was not available in this Codex session, so visual QA
> still needs a real-browser desktop/mobile pass before claiming it complete.

> **Critical KOIL/HPV update 2026-07-21:** Read
> `docs/KOIL_REAL_DATA_VALIDATION_2026.md` and
> `web-react/public/docs/WEB_DEPLOY_READY_CHECKLIST.md` first. The Case Gallery
> now contains 80 CRIC grade references plus 20 expert-labelled CCCID v2
> liquid-based KOIL references. The unchanged SIPaKMeD-trained KOIL endpoint
> detected 19/20 of the deterministic preselected CCCID positives (sensitivity
> 0.9500; Wilson 95% CI 0.7639-0.9911). This is a positive-only challenge, so
> external specificity, AUROC, calibration, and clinical accuracy are not
> estimable. It is not an HPV DNA/RNA endpoint and is not Thai ThinPrep
> validation. The live analyze/report/PDF path now carries this evidence and a
> separate KOIL-specific Grad-CAM. Full regression status: 43/43 tests and the
> production frontend build passed on 2026-07-21.

> **Critical update 2026-07-21:** Read
> `docs/CLINICAL_CONTEXT_PDF_GALLERY_UPDATE_2026-07-21.md` before continuing.
> Analyze now has report-only age/symptom/HPV-lab context, a symptom
> acknowledgement release gate, a real two-page server PDF, backend readiness
> state, and a SIPaKMeD evidence gallery. The legitimate 97% metric is the
> SIPaKMeD five-morphology locked-test accuracy (0.9750), not Herlev grade
> accuracy, Thai ThinPrep accuracy, clinical diagnostic accuracy, or HPV
> detection accuracy.

> **Critical update 2026-07-13:** Statements below that call KOIL a zero-support
> placeholder are historical. Read `docs/KOIL_REAL_DATA_VALIDATION_2026.md`
> first. The live architecture separates four-class grade from an independent
> SIPaKMeD KOIL morphology endpoint (locked-test sensitivity 0.9624,
> specificity 0.9764, AUROC 0.9912). This is conventional Pap-smear morphology
> evidence, not ThinPrep validation and not an HPV DNA/RNA endpoint.

วันที่เขียน: 2026-07-07  
ผู้ใช้ต้องการ: ให้ Claude รับงานต่อจาก Codex โดยเข้าใจ framing ล่าสุดของ CervicalAI / CerviCo-Pilot แบบละเอียด โดยเฉพาะการส่ง **Samsung Solve for Tomorrow 2026** และ **WSEEC**  
สถานะเอกสารนี้: ใช้เป็นไฟล์เริ่มอ่านก่อนทำงานต่อ

## 0A. Web brand update (2026-07-11)

เว็บใช้ชื่อหน้าบ้านภาษาอังกฤษ **Anong** แล้ว โดยยังเก็บ **CerviCo-Pilot** เป็นชื่อเทคนิค/งานวิจัย ห้าม replace ชื่อ CerviCo-Pilot ทั้ง repository เพราะ model card, metrics, full paper และหลักฐานเดิมต้องอ้างชื่อเดียวกัน เมื่อต้องเชื่อมสองบริบทให้เขียน **Anong · CerviCo-Pilot**

ทิศทางสีล่าสุดคือ pastel clinical: ชมพูกุหลาบ + เหลืองเนย + ครีม ไม่ใช่ navy/plum brief เดิม ก่อนแก้ UI ให้อ่าน:

- `PRODUCT.md`
- `IMPECCABLE_BRIEF.md`
- `docs/ANONG_WEB_REBRAND_2026.md`
- `docs/ANONG_ENGLISH_UI_MIGRATION_2026.md`

รอบนี้แก้ navbar/mobile menu ให้ใช้ Lucide icons ชุดเดียว อัปเดต home/About/Ask/footer/browser/PWA/export report branding เพิ่ม contrast ของ semantic colors และตรวจ Chromium ทั้ง desktop/mobile แล้ว การเปลี่ยนแปลงนี้เป็น visual/naming rebrand เท่านั้น ไม่เพิ่ม clinical evidence หรือ validation claim ใหม่

Update รอบถัดมาในวันที่ 2026-07-11: product UI ถูกย้ายเป็น **English-only** ครบทุก 15 routes รวม dynamic states, metadata, PWA, report export และ accessibility labels แล้ว เอกสารดาวน์โหลดภาษาไทยยังคงภาษาต้นฉบับและไม่ถือเป็น UI

Update วันที่ 2026-07-12: ปรับ information architecture ให้กระชับขึ้น โดย primary navigation เหลือ 7 รายการเท่านั้น: Overview, Analyze, Case Gallery, Clinical Workflow, Performance, Evidence และ About ส่วนหน้ารองยังอยู่ครบแต่เข้าผ่านบริบทที่เหมาะสม: Reports จาก Workflow, History จาก Analyze และ Demo/Deployment/Knowledge/Ask/Model Card จาก Evidence ห้ามนำทั้ง 15 routes กลับไปใส่ navbar โดยไม่มีเหตุผลด้าน workflow ชัดเจน อ่านรายละเอียดและผล QA ที่ `docs/ANONG_INFORMATION_ARCHITECTURE_2026.md`

Update เพิ่มเติมวันที่ 2026-07-12: แก้ `server/predictor.py` ให้เพิ่ม project root ใน `sys.path` ก่อน import `ml.*` เพราะเดิม Uvicorn ที่เริ่มจากโฟลเดอร์ `server/` โหลด model ได้ แต่ advanced XAI/MC Dropout หล่นไป fallback แบบเงียบ ๆ ตอนนี้ response มี `heatmap_source` และทดสอบจริงแล้วว่าได้ `advanced_gradcam`, Score-CAM, Eigen-CAM, Layer-CAM, uncertainty overlay, top-k patches และ `advanced_mc` หน้า Analyze เพิ่ม Download reviewed HTML กับ Print/Save PDF หลัง confirm/edit แล้ว แต่ไฟล์ยังเป็น research prototype report ไม่ใช่ regulated medical report อ่าน `docs/MODEL_XAI_REPORT_E2E_2026.md` ก่อนแก้ inference/report ต่อ

Update รอบ hardening ล่าสุดวันที่ 2026-07-12: แก้บัค activation 0.0% แบบครบ pipeline แล้ว CAM ที่ flat/NaN/non-finite จะไม่ถูกแสดงเป็น XAI, model mode ห้ามใช้ heuristic spotlight fallback, Grad-CAM ที่เสียเลือก Grad-CAM++/Layer-CAM/Score-CAM ได้เฉพาะ map ที่ผ่าน diagnostics และต้องรายงาน provenance ตรงวิธี หน้า Analyze แสดงภาพแบบ uncropped ขนาดเท่ากัน มี XAI abstention, quality pass/warning/fail แบบ `single_cell_crop_herlev_v1`, file validation และ release gates ฝั่ง backend รายงานเปลี่ยนเป็น deterministic template นอกจากนี้ paper เปลี่ยน KOIL recall จาก 0.0000 เป็น N/A เพราะ support=0 และเตรียม GitHub Pages/Docker/Render deployment แล้ว อ่าน `docs/ANALYZE_HARDENING_AND_DEPLOYMENT_2026.md`

## 0. Update ล่าสุดจาก Codex (2026-07-07)

ผู้ใช้สั่งให้ "ทำให้โปรเจกต์ดูแข็งแรงขึ้นก่อน" และยังไม่ต้องทำเอกสารของเวทีใดเวทีหนึ่ง
ดังนั้น Codex เพิ่ม project-hardening layer แล้ว โดยต้องอ่านไฟล์เหล่านี้ก่อนเริ่มทำงานต่อ:

- `docs/PROJECT_HARDENING_STATUS.md`
- `docs/CLAIMS_LEDGER.md`
- `docs/VALIDATION_ROADMAP.md`
- `docs/RISK_REGISTER.md`
- `docs/DATASET_MODEL_CARD.md`
- `docs/THINPREP_HPV_FRAMING.md`
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

การเปลี่ยนแปลงหลัก:

- README ถูกอัปเดตให้มี `Current Truth (2026-07-06)` อยู่ด้านบน
- `CLAUDE.md` ถูกอัปเดตให้บังคับอ่าน hardening docs และใช้ wording ใหม่
- `HONEST_STATUS.md` ถูกเพิ่ม section ล่าสุดเรื่อง 5-class + safety triage + HPV morphology risk
- `web-react/src/lib/data.ts` ลด wording เสี่ยง เช่น "พบลักษณะเซลล์มะเร็งชัดเจน" และ "สัญญาณ HPV"
- เพิ่ม `tools/audit_claims.py` สำหรับตรวจคำเคลมเสี่ยงก่อน publish/generate เอกสารใหม่
- เพิ่ม protocol docs ชุดใหม่สำหรับ Thai ThinPrep data, uncertainty/abstention, patient report safety, reader study, และ error analysis
- เพิ่ม calibration experiment จริง (`ml/scripts/calibrate_temperature.py`) และรายงาน `docs/CALIBRATION_EXPERIMENT_REPORT.md`
- เพิ่ม `docs/ERROR_ANALYSIS_REPORT_HERLEV.md` จาก confusion matrix จริง
- เพิ่ม `docs/HERLEV_ERROR_CASE_GALLERY.md` และ `web-react/public/samples/error_cases.json` จาก sample artifacts เพื่อเป็น engineering review gallery ไม่ใช่ pathologist review
- เพิ่ม `docs/PROJECT_READINESS_SCORECARD.md` เพื่อดู readiness แบบ done/partial/missing
- เพิ่ม `docs/LEGACY_ARTIFACT_AUDIT.md` และ patch `report/make_full_report.py` ให้ wording HPV ปลอดภัยขึ้น
- อัปเดตหน้า Analyze ให้มี HPV-related morphology risk panel แยก และ block patient report เมื่อ uncertainty สูง
- เพิ่ม localStorage audit trail ในหน้า Analyze สำหรับ confirm/edit/reject พร้อม export JSON
- เพิ่ม `docs/BROWSER_ACCESSIBILITY_VERIFICATION.md` และ `docs/THAI_DATA_INTAKE_CHECKLIST.md`
- เพิ่ม `docs/EXTERNAL_EVIDENCE_REVIEW_2026.md` และ `docs/SOURCE_CITATION_LEDGER.md`
  เพื่อผูก framing กับ WHO/CDC/FDA/CONSORT-AI/DECIDE-AI และกันการใช้ตัวเลขไทยที่ยังไม่ได้ pin primary source
- อัปเดตเว็บตามไอเดียจาก DentScanAI: เพิ่ม `/history`, `/ask`, workflow cards
  บนหน้าแรก, sample filter ใน `/analyze`, และแยก audit trail เป็น shared util
- ทำชุด 1-8 ต่อ: sidebar app shell, dashboard หน้าแรก, `/gallery`,
  `/workflow`, `/reports`, `docs/JUDGE_QA_BANK.md`, `docs/SUBMISSION_MASTER.md`,
  และ `docs/FAILURE_MODE_AND_HUMAN_FACTORS.md`
- รอบ 2026-07-07 เป็น web/docs completion + verification ไม่ใช่ clinical claim
  ใหม่ ยังต้องถือว่าเป็น Phase 1 Herlev-only research prototype
- เพิ่ม submission-readiness layer: intended use, demo runbook, pitch scripts,
  WSEEC poster content, SFT/WSEEC package map, และ server-side audit roadmap
- เพิ่มรูปเล่ม DOCX ฉบับสมบูรณ์ `docs/CerviCo_Pilot_Complete_Report_2026.docx`
  พร้อมตาราง กราฟ รูป cytology/Grad-CAM และภาคผนวก โดย build จาก
  `tools/build_full_booklet.py`
- เพิ่มรูปเล่มรายงานวิจัยไทยฉบับทางการ
  `docs/CerviCo_Pilot_Formal_Research_Report_2026_Polished.docx` โดย build จาก
  `tools/build_formal_research_report.py` โครงสร้างเป็นปก, หน้าอนุมัติ,
  บทคัดย่อไทย/อังกฤษ, บทที่ 1-5, เอกสารอ้างอิง และภาคผนวก เหมาะกว่าเล่ม
  booklet สำหรับการส่งงานจริงจัง/รูปเล่มวิจัย
- รอบ polish ล่าสุดปรับบทคัดย่อไทย/อังกฤษ, บทนำ/ปัญหาวิจัย/คำถามวิจัย,
  เพิ่ม bibliography จริงใน `docs/FORMAL_REFERENCES_BIBLIOGRAPHY.md` และเพิ่ม
  checklist ตรวจ Word/PDF ก่อนส่งใน `docs/FORMAL_REPORT_FINAL_POLISH_CHECKLIST.md`
- รอบ web hardening ล่าสุดเปลี่ยน package metadata เป็น `cervico-pilot-web`,
  เพิ่ม `/research-report` สำหรับ evidence/download package, เพิ่ม `/demo`
  สำหรับสคริปต์เดโมกรรมการ, เพิ่ม mock server audit API (`/api/audit`),
  เพิ่ม report export/copy controls และเพิ่ม deploy/QA docs
- รอบ production-hardening demo ล่าสุดเพิ่ม SQLite hash-chain audit
  (`artifacts/web_demo_audit.sqlite3`), `/api/ready`, `/api/metrics`,
  `/api/report/export/html`, และหน้า `/deployment` สำหรับอธิบาย readiness
  กับ production gaps อย่างซื่อสัตย์
- เพิ่ม WSEEC 2026 full paper ภาษาอังกฤษตาม Guidebook และ FORMAT FULL PAPER
  จริง: `docs/wseec_2026/CerviCo_Pilot_WSEEC_2026_Full_Paper.docx` และ `.pdf`
  โดยคุม 12 หน้าหลัก + references, Arial 12, single spacing, A4,
  margins 4/3/3/3 cm และมี format audit/checklist แยก
- ฉบับที่ควรใช้ส่งล่าสุดคือ
  `docs/wseec_2026/CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.docx`
  และ `.pdf`; Word/PDF ตรงกัน 12 หน้า ปรับ cover, running header/page number,
  chapter hierarchy, ตาราง, figure panels และ render QA แล้ว

Claude ควรถือว่าเอกสาร hardening เหล่านี้เป็น source of truth ระดับเดียวกับ canonical JSON metrics
และควรอัปเดต handoff นี้ทุกครั้งถ้ามีการเปลี่ยน core framing, metrics, validation status หรือ claim policy

คำสั่งตรวจ claim:

```powershell
python tools\audit_claims.py
```

Calibration result ล่าสุด:

- fitted temperature: **0.7941**
- held-out multiclass ECE: **0.0669 -> 0.0387**
- held-out binary ECE: **0.0907 -> 0.0738**
- held-out binary Brier: **0.0710 -> 0.0670**
- threshold 0.5 confusion after scaling remains **TP 101 / TN 26 / FP 10 / FN 0**

ห้ามแปลผลว่า "fully calibrated"; ให้พูดว่า post-hoc temperature scaling improved calibration on held-out Herlev, external Thai validation still required.

---

---

## 1. สรุปสั้นที่สุดก่อนเริ่ม

โปรเจกต์นี้ไม่ควรถูกขายเป็นแค่ "AI classifier" หรือ "normal/abnormal triage"
แต่ควรถูกวางเป็น:

> **ระบบปัญญาประดิษฐ์เพื่อคัดกรองความผิดปกติของเซลล์ปากมดลูก และการประเมินความเสี่ยงเชื้อ HPV จากภาพถ่าย ThinPrep**

English:

> **Development of an AI System for Cervical Cell Abnormality Screening and HPV Risk Assessment from ThinPrep Images**

ชื่อสำรอง/ชื่อเวทีสั้น:

> **An Explainable Deep Learning System for Cervical Cytology Screening with Uncertainty-Aware, Clinician-in-the-Loop Triage**

แกนความคิดล่าสุดของผู้ใช้:

- ต้องการส่ง Solve for Tomorrow 2026 และ WSEEC
- เชื่อว่า **5-class output ดีแล้ว** และไม่ควรถูกลดเหลือ binary classifier
- จุดมุ่งหมายใหญ่คือ "Almost no one should die of cervical cancer"
- AI ต้องช่วยคัดกรองเร็วขึ้น อธิบายได้ และช่วยลดคนไข้หลุด follow-up
- ต้องพูดเรื่อง ThinPrep และ HPV ให้ละเอียด แต่ห้ามเคลมเกินว่า "AI ตรวจพบเชื้อ HPV"

ประโยคสำคัญ:

> **5-class Bethesda-style grading คือ product output หลัก ส่วน binary normal/abnormal triage คือ safety layer**

---

## 2. ตำแหน่งของโปรเจกต์ตอนนี้

โปรเจกต์อยู่ที่:

`C:\Users\LENOVO LEGION5\Desktop\claude work space\Projects\Project_CervicalAI`

ไฟล์ที่ควรอ่านก่อนทำต่อ:

1. `CLAUDE.md`
2. `HONEST_STATUS.md`
3. `REPRODUCIBILITY_REAL.md`
4. `BENCHMARKS.md`
5. `FINAL_SUBMISSION_PACKAGE.md`
6. `docs/SFT_WSEEC_STRATEGY.md`
7. `docs/THINPREP_HPV_FRAMING.md`
8. `docs/SIRIRAJ_MIT_STRATEGY.md`
9. `docs/CURVES_CALIBRATION.md`
10. `models/test_metrics.json`
11. `models/triage_metrics.json`
12. `models/cv_results.json`
13. `docs/EXTERNAL_EVIDENCE_REVIEW_2026.md`
14. `docs/SOURCE_CITATION_LEDGER.md`
15. `docs/INTENDED_USE_STATEMENT.md`
16. `docs/WEB_DEMO_RUNBOOK.md`
17. `docs/PITCH_SCRIPT_1_3_5MIN.md`
18. `docs/POSTER_CONTENT_WSEEC.md`
19. `docs/SFT_WSEEC_SUBMISSION_PACKAGE.md`
20. `docs/SERVER_SIDE_AUDIT_ROADMAP.md`
21. `docs/BOOKLET_BUILD_NOTES.md`
22. `docs/CerviCo_Pilot_Complete_Report_2026.docx`

ห้าม fabricate metrics เอง ให้ใช้ JSON canonical เท่านั้น

---

## 3. Framing ที่ถูกต้องสำหรับเวที

### 3.1 Samsung Solve for Tomorrow 2026

Solve for Tomorrow ควรขายเป็น social-impact + design-thinking + responsible-AI project

แกนเรื่อง:

1. ปัญหาไม่ใช่แค่ "ตรวจพบหรือไม่พบ"
2. ปัญหาคือ screening coverage ลดลง และคนที่ได้ผลผิดปกติจำนวนมากไม่กลับมาติดตาม
3. CerviCo-Pilot ช่วยเปลี่ยนภาพ cytology ให้เป็นผลคัดกรองที่เข้าใจง่าย อธิบายได้ และส่งต่อได้เร็ว
4. ระบบ offline ได้ เหมาะกับคลินิก/โรงพยาบาลชุมชน/พื้นที่ทรัพยากรจำกัด
5. มี human-in-the-loop: AI ไม่ปล่อยผลเอง ต้องมีแพทย์/บุคลากรยืนยัน

Samsung SFT ควรเน้น:

- Empathize: ผู้หญิงจำนวนมากไม่กลับมาติดตามหลังผลผิดปกติ
- Define: ช่องว่างคือ follow-up gap ไม่ใช่แค่ model accuracy
- Ideate: AI + Grad-CAM + uncertainty + report ที่คนไข้เข้าใจได้
- Prototype: เว็บ offline ที่ upload ภาพแล้วเห็น Bethesda grade, heatmap, uncertainty, report
- Test/Next step: Thai ThinPrep retrospective data + reader study + calibration

ประโยค pitch:

> CerviCo-Pilot is not trying to replace cytologists. It is trying to make sure abnormal slides are noticed, explained, and followed up before a preventable cancer becomes a late diagnosis.

### 3.2 WSEEC

WSEEC ควรขายเป็น science/engineering project ที่ซื่อสัตย์กับหลักฐาน

แกนเรื่อง:

1. Problem: cervical cancer screening and follow-up gap
2. Dataset: real Herlev images, mapped to Bethesda-style 5-class
3. Method: EfficientNet-B0 transfer learning
4. Explainability: Grad-CAM
5. Uncertainty: Monte Carlo Dropout
6. Evaluation: held-out test, bootstrap CI, 5-fold CV, ROC, reliability/ECE
7. Result: 5-class performance ยัง moderate แต่ binary safety triage แข็งแรง
8. Limitation: no Thai data yet, no clinical validation, KOIL not learned in Phase 1

WSEEC ต้องไม่หลบข้อจำกัด เพราะความซื่อสัตย์เป็นจุดแข็ง:

> The five-class model is not yet a final diagnosis model. It is an early Bethesda grading assistant. For safety, the system also collapses predictions into a triage layer, where sensitivity is prioritized over specificity.

---

## 4. ทำไม 5-class ถึงควรเก็บไว้

ผู้ใช้ย้ำว่าการแยก 5 class เป็นสิ่งที่ดี และควรรักษา framing นี้ไว้

เหตุผล:

1. **ตรงกับชื่อโครงงาน**
   - ชื่อคือการคัดกรองความผิดปกติของเซลล์ปากมดลูก
   - ถ้าเหลือแค่ normal/abnormal จะดูเป็น classifier ตื้น ๆ
   - Bethesda-style 5-class ทำให้ระบบดูเหมือน workflow ทาง cytology มากกว่า

2. **เชื่อมกับ HPV risk ได้ดีกว่า**
   - HPV risk จากภาพไม่ได้มาจาก "ตรวจเชื้อ" แต่มาจาก morphology
   - LSIL / KOIL / abnormal cytology เป็นช่องทางอธิบาย HPV-related visual risk
   - ถ้าเหลือ binary จะอธิบายเรื่อง HPV ได้ยากกว่า

3. **กรรมการเห็น technical depth**
   - 5-class classification ยากกว่า binary
   - มี per-class recall, QWK, confusion, limitation ให้พูดเชิงวิทยาศาสตร์
   - เหมาะกับ WSEEC มากกว่า binary-only pitch

4. **binary triage ยังใช้ได้ แต่เป็น safety layer**
   - ใช้เพื่อพูดเรื่องไม่พลาดเคสผิดปกติ
   - ไม่ควรกลายเป็น identity หลักของโปรเจกต์

สรุป:

> 5-class = clinical detail / product identity  
> binary triage = safety argument / screening safeguard

---

## 5. ThinPrep + HPV: ต้องพูดอย่างไร

ชื่อผู้ใช้ต้องการคือ:

> การพัฒนาระบบปัญญาประดิษฐ์เพื่อคัดกรองความผิดปกติของเซลล์ปากมดลูก และการประเมินความเสี่ยงเชื้อ HPV จากภาพถ่าย ThinPrep

สิ่งที่ต้องระวังมาก:

> AI จากภาพ cytology **ไม่ใช่ HPV DNA/RNA test**

ดังนั้นห้ามพูดว่า:

- AI detects HPV
- AI diagnoses HPV infection
- AI replaces HPV DNA test
- AI confirms HPV status

ให้พูดว่า:

- HPV-related morphology risk assessment
- image-based HPV risk assessment
- visual risk patterns associated with HPV-related cell changes
- ประเมินความเสี่ยงที่สัมพันธ์กับ HPV จากลักษณะทางเซลล์วิทยา
- ไม่ใช่การตรวจหาเชื้อ HPV DNA/RNA โดยตรง

คำตอบกรรมการ:

> ระบบนี้ไม่ได้ตรวจหาเชื้อ HPV โดยตรง เพราะการยืนยัน HPV ต้องใช้ HPV DNA/RNA test แต่ภาพ ThinPrep สามารถแสดงความผิดปกติของเซลล์ที่สัมพันธ์กับ HPV ได้ เช่น koilocytic atypia หรือ low-grade squamous lesion ดังนั้นระบบจึงประเมินความเสี่ยงที่สัมพันธ์กับ HPV จาก morphology ของเซลล์ และส่งต่อให้แพทย์ยืนยันเสมอ

ทำไม ThinPrep สำคัญ:

- เป็น liquid-based cytology workflow
- ให้ภาพ/ชั้นเซลล์ที่ standardized กว่า conventional smear หลายกรณี
- เชื่อมกับ lab workflow ได้จริง
- เป็น input ที่สมเหตุสมผลสำหรับ AI มากกว่าภาพมือถือทั่วไป
- เหมาะกับ narrative เรื่อง screening workflow

---

## 6. Metrics จริงที่ใช้ได้

ใช้ตัวเลขจาก canonical JSON เท่านั้น:

- `models/test_metrics.json`
- `models/triage_metrics.json`
- `models/cv_results.json`

### 6.1 Model ปัจจุบัน

จาก `tools/inspect_checkpoints.py`:

- Checkpoint: `best_cervical.pt`
- Architecture: EfficientNet-B0
- Current real checkpoint ไม่ใช่ polluted EfficientNet-B3 0.99
- 5-class model, Herlev-based

### 6.2 Held-out 5-class metrics

จาก `models/test_metrics.json`:

- Accuracy: **0.6934**
- Macro F1: **0.5545**
- Macro recall: **0.5584**
- recall_hsil_scc: **0.75**
- Macro AUROC: **0.7311**
- ECE ในไฟล์นี้เป็น **0.0** แต่ห้ามเคลมว่า calibrated เพราะตัวนี้ไม่ใช่ calibration proof

Per-class recall:

- NILM: **0.7222**
- LSIL: **0.6122**
- HSIL: **0.8667**
- SCC: **0.5909**
- KOIL: **0.0**

Per-class F1:

- NILM: **0.8125**
- LSIL: **0.75**
- HSIL: **0.5909**
- SCC: **0.6190**
- KOIL: **0.0**

### 6.3 Held-out binary triage metrics

จาก `models/triage_metrics.json`:

- Test n: **137**
- Sensitivity: **1.0**
- Specificity: **0.7222**
- PPV: **0.9099**
- NPV: **1.0**
- Accuracy: **0.927**
- Balanced accuracy: **0.8611**
- F1: **0.9528**
- AUROC: **0.964**
- AUPRC: **0.9856**
- MCC: **0.8107**
- Confusion: **TP 101 / TN 26 / FP 10 / FN 0**
- High-risk catch HSIL+SCC: **1.0**

### 6.4 5-fold CV metrics

จาก `models/cv_results.json`:

- 5-fold n: **917**
- 5-class accuracy: **0.6904 +/- 0.0618**
- 5-class recall_hsil_scc: **0.6859 +/- 0.0553**
- 5-class macro F1: **0.5482 +/- 0.0475**
- 5-class macro AUROC: **0.7271 +/- 0.0249**
- QWK: **0.6981 +/- 0.0866**
- Binary triage sensitivity: **0.9867 +/- 0.0086**
- Binary triage specificity: **0.6910 +/- 0.1151**
- Binary triage AUROC: **0.9435 +/- 0.0448**
- Binary triage AUPRC: **0.9756 +/- 0.0217**

### 6.5 Headline order ที่ควรใช้

เวลาทำ pitch หรือ paper ให้เรียงแบบนี้:

1. Product output: Bethesda-style 5-class screening
2. Safety layer: 5-fold binary sensitivity **0.987 +/- 0.009**
3. Held-out discrimination: binary AUROC **0.964**
4. Held-out safety: high-risk catch **1.0**
5. Confusion: **TP 101 / TN 26 / FP 10 / FN 0**
6. Honest 5-class performance: accuracy **0.6934**
7. QWK: **0.687 held-out**, **0.698 +/- 0.087 CV**
8. HSIL recall: **0.8667**
9. SCC recall: **0.5909**

---

## 7. Claims ที่พูดได้ / ห้ามพูด

### พูดได้

- Screening assistance
- Bethesda grading support
- HPV-related morphology risk assessment
- Explainable AI
- Grad-CAM heatmap
- Uncertainty-aware triage
- Clinician-in-the-loop
- Offline prototype
- Phase 1 evidence on public real images
- Thai ThinPrep validation is the next step

### ห้ามพูด

- AI diagnoses cervical cancer
- AI detects HPV infection
- AI replaces HPV DNA/RNA testing
- Ready for clinical use
- Validated in Thailand
- KOIL detection works
- No one will die because of this system
- Fully calibrated model
- 99% 5-class accuracy

เหตุผล:

- โปรเจกต์ยังเป็น Phase 1 POC
- Dataset ยังไม่ใช่ Thai ThinPrep clinical validation
- KOIL class ยังไม่ learned ใน Phase 1 เพราะ Herlev ไม่มี true KOIL samples
- มีผล binary triage ดี แต่ 5-class accuracy ยัง moderate

---

## 8. Abstract เวอร์ชันที่ควรใช้

### English

Almost no one should die of cervical cancer. Caught early on a Pap or ThinPrep
slide, abnormal cells are nearly always stopped in time. Yet Thailand is moving
in the wrong direction: screening coverage has fallen from 77.5% to 53.9%, and
roughly 41% of women with abnormal results never return for care.

CerviCo-Pilot was built to close that follow-up gap. A user uploads a ThinPrep
or Pap cytology image; the system grades cervical cell abnormality on a
Bethesda-style scale, estimates HPV-related visual risk from cytologic
morphology, overlays a Grad-CAM heatmap over the regions it examined, and
estimates uncertainty with Monte Carlo Dropout. When the model is unsure, it
hands the case back to a clinician instead of forcing a prediction. It supports
the clinician; it never pretends to be one.

We trained EfficientNet-B0 on 917 real Herlev images and evaluated it using
held-out testing, bootstrap confidence intervals, and 5-fold cross-validation.
Binary screening sensitivity reached 0.987 +/- 0.009 across 5 folds, and
held-out binary AUROC reached 0.964 with no high-risk case missed in the
held-out triage test. The system runs offline, making it suitable for
low-resource screening workflows.

### Thai

มะเร็งปากมดลูกเป็นโรคที่ป้องกันการเสียชีวิตได้มาก หากตรวจพบความผิดปกติของเซลล์ตั้งแต่ระยะเริ่มต้นจากภาพ Pap smear หรือ ThinPrep แต่ประเทศไทยกำลังเผชิญปัญหาสำคัญสองด้าน คืออัตราการเข้ารับการคัดกรองลดลงจาก 77.5% เหลือ 53.9% และผู้หญิงที่ได้รับผลผิดปกติประมาณ 41% ไม่กลับมาติดตามผลต่อ

CerviCo-Pilot ถูกออกแบบมาเพื่อช่วยลดช่องว่างหลังการคัดกรอง ระบบรับภาพ ThinPrep หรือ Pap cytology แล้วจำแนกระดับความผิดปกติของเซลล์ตาม Bethesda scale พร้อมประเมินความเสี่ยงที่สัมพันธ์กับ HPV จากลักษณะทางเซลล์วิทยา ไม่ใช่การตรวจหาเชื้อ HPV DNA/RNA โดยตรง ระบบแสดง Grad-CAM heatmap เพื่อบอกว่าปัญญาประดิษฐ์พิจารณาบริเวณใดของภาพ เมื่อโมเดลไม่มั่นใจ ระบบจะ flag ให้แพทย์ตรวจทานแทนการปล่อยผลอัตโนมัติ และรายงานสำหรับผู้ป่วยจะออกได้หลังการยืนยันโดยบุคลากรทางการแพทย์เท่านั้น

เราใช้ EfficientNet-B0 ฝึกบนภาพจริงจากชุดข้อมูล Herlev จำนวน 917 ภาพ และประเมินด้วย held-out test, bootstrap confidence intervals และ 5-fold cross-validation ผลการคัดกรองแบบปกติ/ผิดปกติให้ sensitivity เฉลี่ย 0.987 +/- 0.009 และ AUROC 0.964 บน held-out test โดยไม่พลาดเคสเสี่ยงสูงในการทดสอบ triage ระบบสามารถทำงานแบบ offline จึงเหมาะกับการสาธิต workflow สำหรับโรงพยาบาลชุมชนหรือพื้นที่ทรัพยากรจำกัด

---

## 9. สิ่งที่ Codex แก้ไปแล้ว

### 9.1 เอกสารหลัก

แก้/เพิ่มแล้ว:

- `REPRODUCIBILITY_REAL.md`
- `HONEST_STATUS.md`
- `BENCHMARKS.md`
- `FINAL_SUBMISSION_PACKAGE.md`
- `docs/SIRIRAJ_MIT_STRATEGY.md`
- `docs/SFT_WSEEC_STRATEGY.md`
- `docs/THINPREP_HPV_FRAMING.md`
- `docs/CURVES_CALIBRATION.md`

สาระที่แก้:

- เลิกใช้ framing แบบโมเดล 0.99 ที่ไม่น่าเชื่อถือ
- ยืนยัน checkpoint ปัจจุบันเป็น EfficientNet-B0
- วาง 5-class เป็น product output
- วาง binary triage เป็น safety layer
- เพิ่ม ThinPrep + HPV morphology risk wording
- เพิ่มคำเตือนว่าไม่ใช่ HPV DNA/RNA test
- เพิ่มเอกสารสำหรับ SFT/WSEEC โดยเฉพาะ

### 9.2 โค้ด/เว็บ

แก้/เพิ่มแล้ว:

- `ml/scripts/gen_curves.py`
- `web-react/public/samples/curves.json`
- `web-react/src/pages/Performance.tsx`
- `web-react/src/lib/data.ts`
- `web-react/src/pages/About.tsx`
- `web-react/src/pages/Analyze.tsx`
- `server/app.py`
- `server/predictor.py`
- `tools/inspect_checkpoints.py`

สาระที่แก้:

- สร้าง ROC/reliability curve จาก canonical eval path
- หน้า Performance แสดง AUROC/ECE/Brier และ calibration note
- หน้า About/Analyze ปรับเป็น ThinPrep/Pap + 5-class + HPV morphology risk
- API health เพิ่ม scope ว่า prototype/validated scope
- predictor ระบุว่า LLM-style explanation/SAM/contour เป็น prototype ไม่ใช่ clinical validation
- inspect checkpoint แสดง expected honest target ไม่ใช่ตัวเลขเกินจริง

### 9.3 Verification ที่รันแล้ว

ผ่านแล้ว:

```powershell
python ml\scripts\gen_curves.py
python -m py_compile ml\scripts\gen_curves.py server\app.py server\predictor.py tools\inspect_checkpoints.py
python tools\inspect_checkpoints.py
npm.cmd run build
```

ผล `gen_curves.py`:

- n = 137
- roc_auc = 0.963971
- ece = 0.090679
- brier = 0.071015
- confusion = TP 101 / TN 26 / FP 10 / FN 0

ผล `npm.cmd run build` ล่าสุด:

- ผ่าน
- build ไปที่ `web-dist`
- JS ประมาณ 288.60 kB

---

## 10. สิ่งที่ควรให้ Claude ทำต่อ

### งาน A: ทำ submission package สำหรับ Samsung SFT

ควรสร้าง:

1. One-page Thai proposal
2. 3-minute Thai pitch script
3. 1-minute elevator pitch
4. Problem-solution-impact diagram
5. Thai patient journey storyboard
6. Demo script
7. Q&A defense sheet

โทน:

- Human-centered
- ไม่ technical จนเกินไป
- เน้นผู้หญิงที่ผลผิดปกติแล้วหายจากระบบ
- เน้น offline + human-in-the-loop + report ภาษาไทย

### งาน B: ทำ WSEEC paper / presentation

ควรสร้าง:

1. English abstract
2. Introduction
3. Methodology
4. Dataset and preprocessing
5. Evaluation protocol
6. Results
7. Discussion
8. Limitations
9. Future work
10. References

โทน:

- Scientific honesty
- ใช้ metrics จริงเท่านั้น
- ไม่ซ่อน 5-class accuracy moderate
- อธิบายว่าทำไม screening safety layer จึงสำคัญ

### งาน C: ปรับ pitch deck

ควรตรวจไฟล์:

- `PITCH_DECK.md`
- `PITCH_SCRIPT.md`
- `pitch/make_pitch_pptx.py`

เป้าหมาย:

- เปลี่ยน title เป็น ThinPrep + HPV risk title
- ใส่ 5-class as main output
- ใส่ binary triage as safety layer
- ใส่ "not HPV DNA/RNA test"
- ใส่ Grad-CAM + uncertainty + clinician sign-off

### งาน D: ปรับ report generator

ควรตรวจไฟล์:

- `report/make_wseec_paper.py`
- `report/make_cervical_doc.py`
- `report/make_report.py`

เป้าหมาย:

- sync wording ล่าสุด
- sync metrics จริง
- เพิ่ม ThinPrep/HPV caveat
- ห้ามให้ docx พูดว่า HPV detected

### งาน E: เพิ่ม UX mock/flow ในเว็บ

ถ้าจะทำต่อใน frontend:

- เพิ่ม "HPV-related morphology risk" panel
- แยก "Bethesda grade" กับ "HPV risk note"
- เพิ่ม disclaimer ใกล้ผล HPV risk
- แสดงว่า report ปล่อยได้หลัง clinician sign-off เท่านั้น

สำคัญ:

- ถ้าทำ frontend ต้องรัน `npm.cmd run build` หลังแก้

### งาน F: เตรียม Q&A

คำถามกรรมการที่ต้องเตรียม:

1. ทำไมไม่ใช้ ChatGPT/Claude/Gemini?
2. AI จากภาพตรวจ HPV ได้อย่างไร?
3. ถ้า 5-class accuracy แค่ 0.69 ทำไมยังน่าเชื่อถือ?
4. ทำไมไม่ใช้ binary classifier อย่างเดียว?
5. ใช้จริงในโรงพยาบาลได้หรือยัง?
6. ถ้า Grad-CAM ชี้ผิดจะทำอย่างไร?
7. ถ้า model ไม่มั่นใจจะเกิดอะไรขึ้น?
8. ข้อมูลไทยอยู่ไหน?
9. มี bias/domain shift ไหม?
10. ทำไม offline สำคัญ?

คำตอบแกน:

- ไม่ใช้ general chatbot เพราะงานนี้ต้องอ่านภาพ cytology ด้วย model ที่ train/evaluate เฉพาะ task, มี deterministic evaluation, heatmap, uncertainty, audit trail และ offline deployment
- HPV risk คือ morphology risk ไม่ใช่ DNA/RNA detection
- 5-class ยังเป็น grading assistant; safety layer sensitivity สูงใช้ป้องกัน miss
- ยังไม่ clinical use; Phase 2 ต้อง Thai ThinPrep + reader study + calibration

---

## 11. คำตอบเรื่อง "ทำไมไม่ใช้ ChatGPT/Claude/Gemini"

ควรตอบประมาณนี้:

> ChatGPT, Claude, หรือ Gemini เป็น general-purpose assistants ที่ช่วยอธิบายหรือเขียนรายงานได้ แต่ไม่ใช่ระบบคัดกรอง cytology ที่ถูก train และประเมินด้วย protocol เฉพาะงานนี้ CerviCo-Pilot ต่างออกไปเพราะมีโมเดล vision เฉพาะ cervical cytology, มีการวัด sensitivity/AUROC/QWK บน held-out และ 5-fold CV, มี Grad-CAM เพื่อให้แพทย์ตรวจสอบจุดที่โมเดลดู, มี Monte Carlo Dropout เพื่อ flag ความไม่แน่นอน, ทำงาน offline ได้ และบังคับ clinician sign-off ก่อนออกผลผู้ป่วย ดังนั้นมันไม่ใช่ chatbot มาตอบแทนแพทย์ แต่เป็น workflow tool สำหรับคัดกรองและติดตามผล

เวอร์ชันสั้น:

> General chatbots answer questions; CerviCo-Pilot is an evaluated, offline, image-based screening workflow with explainability, uncertainty, and clinician sign-off.

---

## 12. ความเสี่ยงของ project และวิธีพูด

### Risk 1: 5-class accuracy moderate

พูดตรง ๆ:

> 5-class grading is still an early assistant, not a final diagnostic model. The safety layer is designed to reduce missed abnormal/high-risk cases.

### Risk 2: No Thai validation yet

พูดตรง ๆ:

> Current evidence is Phase 1 on public real cytology images. Thai ThinPrep validation and reader study are the next step.

### Risk 3: HPV claim อาจถูกตีว่าเกินจริง

พูดตรง ๆ:

> It is HPV-related morphology risk assessment, not HPV infection detection.

### Risk 4: KOIL evidence may be conflated with the Herlev grade table

พูดตรง ๆ:

> KOIL recall is not estimable in the Herlev grade table because Herlev has no
> true KOIL support. KOIL is evaluated separately: locked SIPaKMeD sensitivity
> 0.9624 and specificity 0.9764, plus a 19/20 positive-only CCCID liquid-based
> challenge. The CCCID result cannot estimate external specificity and neither
> dataset establishes HPV infection status.

### Risk 5: Specificity around 0.69-0.72

พูดตรง ๆ:

> In screening, some over-referral is acceptable if the priority is not missing abnormal cases. Clinician sign-off prevents unsafe automation.

---

## 13. Suggested file names Claude may create next

ถ้าทำเอกสารต่อ แนะนำสร้าง:

- `docs/SAMSUNG_SFT_2026_SUBMISSION_DRAFT.md`
- `docs/SAMSUNG_SFT_2026_PITCH_SCRIPT_TH.md`
- `docs/WSEEC_2026_FULL_PAPER_DRAFT.md`
- `docs/WSEEC_2026_PRESENTATION_SCRIPT.md`
- `docs/HPV_THINPREP_EXPLAINER_FOR_JUDGES.md`

ทำแล้ว ไม่ต้องสร้างซ้ำ:

- `docs/JUDGE_QA_BANK.md`
- `docs/SUBMISSION_MASTER.md`
- `docs/FAILURE_MODE_AND_HUMAN_FACTORS.md`

ถ้าทำ slide/deck:

- `pitch/SFT_2026_DECK.md`
- `pitch/WSEEC_2026_DECK.md`

---

## 14. Commands ที่ใช้ได้

จาก project root:

```powershell
cd "C:\Users\LENOVO LEGION5\Desktop\claude work space\Projects\Project_CervicalAI"
python tools\inspect_checkpoints.py
python ml\scripts\gen_curves.py
python -m py_compile ml\scripts\gen_curves.py server\app.py server\predictor.py tools\inspect_checkpoints.py
```

Frontend:

```powershell
cd "C:\Users\LENOVO LEGION5\Desktop\claude work space\Projects\Project_CervicalAI\web-react"
npm.cmd run build
```

อย่าใช้ `npm run build` ใน PowerShell ถ้าติด execution policy ให้ใช้ `npm.cmd run build`

---

## 15. Final guidance for Claude

อย่าทำให้ project ดูเกินจริง จุดแข็งของ CerviCo-Pilot คือมันจริงใจและรับผิดชอบ:

- มี 4-class grade output (NILM/LSIL/HSIL/SCC) และ independent KOIL morphology endpoint
- มี safety triage layer ที่เน้นไม่พลาด abnormal/high-risk cases
- มี Grad-CAM ให้แพทย์ท้าทาย reasoning ได้
- มี MC Dropout เพื่อยอมรับความไม่แน่นอน
- มี clinician sign-off เพื่อไม่ปล่อยผลอัตโนมัติ
- มี offline deployment story
- มี limitation ชัดเจนและ plan สำหรับ Thai ThinPrep validation

ข้อความสุดท้ายที่ควรยึด:

> CerviCo-Pilot is not a diagnosis machine. It is a cervical screening co-pilot: it suggests a cytology morphology grade, separately estimates koilocytotic morphology, explains where the model responded, flags uncertainty, and keeps the clinician in control. It does not detect HPV DNA/RNA, and Thai ThinPrep clinical validation remains future work.
# 2026-07-21 deployment and gallery update

- The public Case Gallery now includes a reproducible 100-cell atlas: 20 each
  for NILM, LSIL, HSIL, SCC, and KOIL. The first four categories use CRIC
  Cervix under CC BY 4.0; KOIL uses 20 CCCID v2 center-focus liquid-based
  cytology crops under CC BY-NC 4.0.
- Treat the CRIC atlas only as external morphology reference material. It is
  not model evaluation, external validation, ThinPrep evidence, or HPV testing.
- KOIL remains a separate morphology endpoint. SIPaKMeD supplies training and
  locked testing; CCCID supplies only the limited 20-positive external
  challenge and public reference images. Do not bulk republish SIPaKMeD images
  until explicit redistribution terms are documented.
- `scripts/build_cric_reference_gallery.py` regenerates the atlas and records
  per-image DOI provenance plus SHA-256 hashes.
- Docker now includes both `models/best_cervical.pt` and
  `models/koil_sipakmed/best_koil_model.pt`; a deployment contract test guards
  this packaging requirement.
- Render `starter` is too small. The loaded local backend measured about 804 MiB
  RSS, so `render.yaml` now uses `standard` in Singapore with `/api/ready`.
- Read `web-react/public/docs/WEB_DEPLOY_READY_CHECKLIST.md` before deployment.
  GitHub Pages needs repository variable `VITE_API_URL` set to the final Render
  origin before uploads and server-generated PDF reports work there.

## 2026-07-22 standalone chart and heatmap library

For manual slide authoring, use `presentation/standalone_visual_assets_2026/`
rather than cropping the full-slide PNG files. The package contains 27
individual visual elements with no slide header or footer:

- grade recall and precision/recall/F1 charts;
- binary-triage five-fold trends and mean ± SD summary;
- binary triage, four-grade, KOIL binary and five-morphology confusion matrices;
- separate KOIL ROC, precision-recall and calibration curves;
- KOIL probability distribution at the locked threshold;
- KOIL outcome and false-positive source charts;
- individual NILM, LSIL, HSIL and SCC Grad-CAM pairs;
- KOIL Grad-CAM audit, all five false negatives and five highest-scoring false positives;
- CCCID positive-only challenge graphic;
- system evidence, HPV/KOIL boundary, clinician workflow, validation roadmap and evidence summary diagrams.

Files:

- Contact sheet: `presentation/standalone_visual_assets_2026/00_contact_sheet.jpg`
- Usage and claim boundaries: `presentation/standalone_visual_assets_2026/README.md`
- Integrity metadata: `presentation/standalone_visual_assets_2026/manifest.json`
- Archive: `presentation/standalone_visual_assets_2026.zip`
- Rebuild command: `python tools/build_standalone_visual_assets.py`

Do not combine Herlev and SIPaKMeD counts into one cohort, place KOIL inside
the Bethesda grade confusion matrix, describe Grad-CAM as segmentation, or
describe KOIL morphology as molecular HPV confirmation.

## 2026-07-22 HPV paired-data and grade-v3 continuation

This section supersedes earlier route and HPV wording in this handoff.

- The public `/clinical-evidence`, `/koil`, `/hpv`, `/workflow`, and
  `/research-report` routes were removed. The focused public navigation is
  Overview, Analyze, Case Gallery, and Performance. Dataset audit remains at
  `/datasets` and is linked from Performance.
- Read `docs/HPV_PAIRED_DATA_AND_BETHESDA_FEASIBILITY_2026.md` before changing
  any HPV, KOIL, Bethesda, organism, or dataset claim.
- The repository contains zero same-patient microscopy-image + molecular-assay
  pairs. This is not a claim that HPV cohorts do not exist. NCI PaP and the
  Swedish screening cohort are relevant governed resources; BMT is a strong
  public ThinPrep image candidate but does not expose HPV status per image.
- The defensible report structure is grade + independent KOIL + independent
  organism findings + externally reported molecular HPV field + uncertainty.
  Do not force these into one mutually exclusive five-class softmax.
- A future Bethesda grade expansion may use NILM / ASC-US / ASC-H / LSIL / HSIL
  / SCC after data review. An interim ASC merge loses a clinically relevant
  distinction and must be disclosed. Glandular abnormalities require their own
  support and must not be silently mapped to squamous classes.
- `web-react/public/evidence/dataset_registry.json` now catalogues 15 sources
  while keeping the current model-development count fixed at 4,966.
- `ml/grade_research_v3.py` and
  `ml/scripts/train_grade_research_v3.py` implement a valid four-grade research
  model with mask, hierarchy, ordinal, hard-example, stain, and selective
  prediction support.
- Read `docs/GRADE_RESEARCH_V3_EXPERIMENTS_2026_07_22.md` before promoting any
  research checkpoint. Experiment A reached 0.7883 locked-test accuracy but
  reduced HSIL recall and triage sensitivity. Experiment B recovered 1.0000
  triage recall but had only 0.4667 HSIL recall. Neither is deployment-approved;
  `models/best_cervical.pt` remains canonical.
- The production web build and full project suite passed on 2026-07-22:
  `55 passed`; `npm.cmd run build` completed successfully; `git diff --check`
  was clean; and the local static preview returned HTTP 200 at
  `http://127.0.0.1:4174/`. The only test warning was Albumentations being
  unable to perform its optional online version check in the restricted
  environment.
- The two grade-v3 checkpoints are experiment artefacts only. They have not
  been wired into `server/predictor.py`, copied over `models/best_cervical.pt`,
  committed, pushed, or deployed.

## 2026-07-22 latest CRIC Performance and Case Gallery release

This section supersedes the old Performance-page and Case-Gallery grade-model
descriptions above.

- `/performance` now presents only the two principal measured endpoints: the
  latest CRIC four-grade research candidate and the independent SIPaKMeD KOIL
  morphology model. The old Herlev grade charts, research-v3 comparison panels,
  and the explanatory "What each table and graph measures" block were removed.
- The latest CRIC candidate was evaluated on 10,003 cells from 395 parent
  microscope images with five parent-image-disjoint out-of-fold splits. Its
  full-cohort four-grade accuracy is 88.8% (95% CI 0.8619-0.9110).
- At the pre-reported confidence threshold of 0.60, 9,411 cells are accepted
  and 592 are abstained for human review: selective accuracy is 91.7% at 94.1%
  coverage (95% CI 0.8960-0.9349). Never shorten this to "the model is 91.7%
  accurate" without stating both selective evaluation and coverage.
- CRIC per-class recall is NILM 94.5%, LSIL 70.4%, HSIL 84.7%, and SCC 50.3%.
  The weak SCC result, with 161 cells from only 21 parent images, remains
  visible and prevents an autonomous or clinical-readiness claim.
- All five grade figures are regenerated from the latest OOF records:
  confusion matrix, precision/recall/F1, fold accuracy, accuracy-coverage
  trade-off, and recall by endpoint. The final chart includes KOIL sensitivity
  for comparison but explicitly marks the separate dataset and ontology.
- `/gallery` defaults to 20 latest-model CRIC cases: five per true grade, each
  containing three accepted correct predictions, one accepted error, and one
  abstained prediction from different parent images. Every probability is the
  recorded OOF TTA output from the fold where that parent image was held out.
- Every displayed heatmap is a newly generated predicted-class Grad-CAM from
  that case's fold-specific EfficientNet-B0 checkpoint. The heatmap is a
  single-view post-hoc explanation, not segmentation or causal proof. SHA-256
  integrity hashes for every original and Grad-CAM file are in
  `web-react/public/cric-model-gallery/index.json`.
- Rebuild the figures and gallery with
  `python scripts/build_cric_latest_web_evidence.py`. Machine-readable figure
  metrics are in `web-react/public/evidence/cric-latest/index.json`.
- The live `/analyze` upload workflow still uses the historical Herlev grade
  checkpoint. The CRIC candidate is research evidence and has not replaced the
  deployed upload model. CRIC is conventional Pap-smear evidence, not Thai
  ThinPrep clinical validation.
- KOIL remains a separate SIPaKMeD morphology endpoint with sensitivity 96.2%,
  specificity 97.6%, and AUROC 0.991 on its locked source-cluster-disjoint test.
  Neither KOIL nor CRIC confirms HPV DNA/RNA, genotype, persistence, or
  molecular infection status.
- Verification for this release: 66 unit/contract tests passed, the production
  frontend build completed, claim audit passed, and responsive browser checks
  showed no horizontal overflow at 390 px on Performance or Case Gallery.

## 2026-07-22 SCC interpretation and clean Performance UI

- The SCC exact-label recall remains 50.3%: 81 of 161 true SCC cells were
  labelled SCC. This metric was not changed or hidden.
- The confusion matrix shows that 74 additional SCC cells were labelled HSIL.
  Therefore, 155 of 161 SCC cells (96.3%) were still captured in the combined
  HSIL-or-SCC high-grade group. Across all true HSIL and SCC cells, high-grade
  capture is 1,688 of 1,864 (90.6%).
- Always distinguish these endpoints: 50.3% measures exact SCC subtyping;
  96.3% measures whether SCC entered the high-grade review queue. The latter
  does not justify autonomous grading or a claim that SCC classification is
  96.3% accurate.
- A post-hoc global SCC logit-bias sweep was explored locally and rejected. It
  raised SCC recall only by sharply reducing SCC precision and macro F1, and it
  was not validation-selected. No model checkpoint or headline result changed.
- `/performance` uses a clean evidence hierarchy. Four screening-level cards,
  an SCC exact-versus-high-grade explanation, and a compact recall view appear
  first. All five latest-model research charts are visible directly below that
  summary so users do not mistake them for removed content. Exact tabular
  precision/recall/F1, endpoint provenance, and the KOIL confusion matrix remain
  available in expandable sections.
- `ml/scripts/aggregate_cric_grade_cv.py` and
  `scripts/build_cric_latest_web_evidence.py` now write auditable grouped
  endpoints. The recall chart displays SCC exact recall and SCC high-grade
  capture separately.
- Improving exact SCC grading requires more independent SCC parent images,
  validation-selected cost-sensitive training, and external ThinPrep
  evaluation. UI wording cannot repair this endpoint.

## 2026-07-22 grade v4 and APCData external-domain audit

- Read `docs/GRADE_V4_1_TO_8_EXECUTION_2026_07_22.md` before changing grade
  metrics, ThinPrep/LBC claims, or the production checkpoint.
- Official APCData (`10.17632/ytd568rh3p.1`, CC BY 4.0) was downloaded and CRC
  verified. A locked external manifest contains 3,065 supported cells: NILM
  2,076, LSIL 444, HSIL 419, and SCC 126. ASC-US/ASC-H remain excluded.
- The existing CRIC five-checkpoint ensemble failed external LBC transfer:
  accuracy 0.6966, balanced accuracy 0.2835, LSIL recall 0.1126, HSIL recall
  0.0215, and SCC recall 0.0000. It predicted 2,960/3,065 cells as NILM.
- This result blocks any claim that the CRIC candidate is ThinPrep-ready. It is
  visible on `/performance`; do not remove or replace it with raw accuracy.
- `ml/grade_research_v3.py` now includes `MultiScaleGradeResearchNet` with a
  cell backbone, lightweight context branch, and hierarchical/ordinal heads.
- CRIC manifests now contain cached 640-pixel context crops. The v4 trainer
  uses parent-balanced sampling and validation-selected checkpoints.
- `ml/grade_v4_evaluation.py` and
  `ml/scripts/aggregate_cric_grade_v4.py` enforce fold-safe ensemble alignment
  and an explicit production-promotion gate.
- `review/grade_boundary_review_2026/queue.csv` contains 120 unreviewed cases
  from unique parent images. Never call them expert-adjudicated until the
  reviewer fields are completed by a qualified reviewer.
- End-to-end v4 smoke training passed. Its artifacts are labelled
  `smoke_test_only` and must never be used as evidence or website metrics.
- A full ten-run experiment (five folds x two members) was not completed in
  this session because 224-pixel dual-input training was preprocessing-bound.
  The canonical CRIC metrics and deployed upload checkpoint therefore remain
  unchanged.

## 2026-07-23 endpoint-specific web metric audit

- Overview and Model Card metrics are now grouped into three explicitly
  separate result sets. Do not collapse them into one model score:
  1. Herlev deployed upload baseline: 917 conventional Pap cell images;
     binary-triage CV sensitivity 98.7% +/- 0.9%, specificity 69.1% +/- 11.5%,
     and four-grade CV accuracy 69.0% +/- 6.2%.
  2. CRIC research candidate, not deployed: 10,003 cells from 395 parent
     images; 88.8% all-cell OOF accuracy, or 91.7% accepted-case accuracy at
     94.1% coverage. Exact SCC recall remains 50.3%; SCC high-grade capture is
     a different endpoint at 96.3%.
  3. SIPaKMeD KOIL morphology: locked n=641; sensitivity 96.2%, specificity
     97.6%, AUROC 0.991. This is not a fifth grade or a molecular HPV test.
- `METRICS.fiveClass`, generic `METRICS.dataset`, and other unused historical
  arrays were removed from `web-react/src/lib/data.ts`. Use
  `METRICS.herlevBaseline`, `METRICS.cricGrade`, and `METRICS.koil` so dataset
  and endpoint provenance remain visible in code.
- CCCID's 20 positives are external challenge evidence, not training data.
  The Model Card now labels the row as Evidence datasets and states this role.
- Percent-valued Herlev metrics are displayed as percentages throughout the
  public UI; AUROC remains on its 0-1 scale. Mobile Model Card metrics use
  stacked endpoint cards instead of a horizontally clipped table.
- The 14,969 current development items are a registry sum across separate
  datasets and endpoints, not one cohort, not independent patients, and not
  all ThinPrep images.
- Verification on 2026-07-23: the TypeScript and Vite production build passed;
  desktop and 390 px browser checks showed no horizontal page overflow.
- `/performance` is now a compact presentation route. The SCC explanation,
  APCData panel, exact-class table, endpoint-comparison disclosure, and
  recall-by-endpoint figure were removed from that route. Four CRIC figures
  remain. A scope note states that headline results are endpoint-specific and
  links to the full Model Card.
- The measured limitations were not altered: exact SCC recall 50.3% and
  APCData balanced accuracy 28.4% remain in the Model Card, repository reports,
  and machine-readable evidence. Never replace them with invented values or
  describe the 91.7% selective result as accuracy for every grade.

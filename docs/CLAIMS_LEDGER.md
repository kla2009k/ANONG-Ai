# Claims Ledger

Purpose: one source of truth for what CerviCo-Pilot can and cannot claim.

Last updated: 2026-07-22

> **Current endpoint contract:** the deployed research workflow has a
> four-class grade output (NILM, LSIL, HSIL, SCC) and a separate KOIL
> morphology endpoint. KOIL is not a fifth mutually exclusive Bethesda grade.
> The public evidence inventory contains 917 Herlev grade-task images and 4,049
> SIPaKMeD KOIL-task cells; these counts must remain separate.

Read with:

- `docs/EXTERNAL_EVIDENCE_REVIEW_2026.md`
- `docs/SOURCE_CITATION_LEDGER.md`

## Rule

If a claim is not supported by `models/*.json`, a named document, or a verified
workflow, write it as future work or limitation.

External sources can support public-health and clinical-workflow framing, but
they cannot create new model-performance claims.

## Approved Core Claims

| Claim | Status | Evidence | Safe Wording |
| --- | --- | --- | --- |
| The system is a cervical cytology screening assistant | Supported | Web/API demo + model card | "screening assistance" |
| It outputs a four-class Bethesda-style supported subset | Supported with limitations | `models/test_metrics.json`, endpoint contract | "four-class grading support: NILM, LSIL, HSIL, SCC" |
| It outputs an independent KOIL morphology assessment | Supported with domain limitations | `docs/KOIL_REAL_DATA_VALIDATION_2026.md` | "independent koilocytotic-morphology endpoint; not an HPV test" |
| It has strong binary normal/abnormal triage sensitivity on Herlev held-out/CV | Supported | `models/triage_metrics.json`, `models/cv_results.json` | "safety triage layer" |
| It can show model attention using Grad-CAM | Supported as XAI demo | web/server XAI path | "Grad-CAM heatmap shows regions the model emphasized" |
| It estimates uncertainty | Supported as prototype | MC Dropout flow | "uncertainty-aware; flags cases for review" |
| It runs offline as a prototype | Supported | local FastAPI/React build | "offline-capable prototype" |
| It uses real public Herlev images | Supported | canonical metrics + prep | "Phase 1 evidence on public real images" |

## Claims Requiring Careful Qualification

| Claim | Required Qualification |
| --- | --- |
| "HPV risk assessment" | Must say "HPV-related morphology risk from cytology images", not infection detection |
| "ThinPrep images" | Current workflow is ThinPrep/Pap-style; current Herlev evidence is public cytology, not Thai ThinPrep validation |
| "No high-risk cases missed" | Only in the held-out binary triage test, n=137, with TP 101/TN 26/FP 10/FN 0 |
| "Clinically useful" | Say "workflow-relevant prototype"; clinical utility needs reader study |
| "Explainable" | Grad-CAM is an explanation aid, not proof of causal reasoning |
| "Calibrated uncertainty" | Current uncertainty is prototype; calibration tuning is not complete |

## External Evidence Claims

| Claim | Status | Evidence | Safe Wording |
| --- | --- | --- | --- |
| Cervical cancer prevention depends on vaccination, screening, and follow-up/treatment | Supported externally | WHO cervical cancer fact sheet / elimination strategy | "aligns with cervical-cancer prevention and early-detection workflows" |
| Pap/ThinPrep cytology and HPV testing are different test types | Supported externally | CDC cervical cancer screening page | "cytology looks for cell changes; HPV testing looks for the virus" |
| HPV-related morphology risk is not HPV infection detection | Supported externally + project policy | CDC distinction + `docs/THINPREP_HPV_FRAMING.md` | "HPV-related morphology risk from visible cytologic changes" |
| Reader study/prospective evaluation is needed before clinical-utility claims | Supported externally | CONSORT-AI, DECIDE-AI | "clinical utility remains future work" |
| Medical-AI lifecycle governance matters | Supported externally | FDA/IMDRF GMLP | "prototype follows intended-use, limitation, monitoring, and claim-control principles" |

Thailand-specific numeric claims, including screening coverage decline and
loss-to-follow-up percentages, require primary-source verification before final
publication. Until then, use them only as background motivation or mark them as
"source pending."

## Forbidden Claims

Do not write these in public-facing materials:

- "AI diagnoses cervical cancer."
- "AI detects HPV infection."
- "AI replaces HPV DNA/RNA testing."
- "AI replaces cytotechnologists/pathologists."
- "Validated in Thailand."
- "Ready for clinical use."
- "KOIL detection works."
- "Fully calibrated."
- "99% accurate" without context.
- "No patient will die because of this system."

## Metrics Claims

Approved metrics:

| Metric | Value | Source | Wording |
| --- | --- | --- | --- |
| Held-out supported-grade accuracy | 0.6934 | `models/test_metrics.json` | "moderate four-class supported-grade accuracy" |
| Held-out supported-grade QWK | 0.687 | `models/triage_metrics.json` | "ordinal agreement signal" |
| Held-out HSIL recall | 0.8667 | `models/triage_metrics.json` | "HSIL recall was strong" |
| Held-out SCC recall | 0.5909 | `models/triage_metrics.json` | "SCC recall remains imperfect" |
| Held-out binary sensitivity | 1.0 | `models/triage_metrics.json` | "no false negatives in this held-out triage test" |
| Held-out binary AUROC | 0.964 | `models/triage_metrics.json` | "strong binary discrimination" |
| 5-fold binary sensitivity | 0.9867 +/- 0.0086 | `models/cv_results.json` | "high screening sensitivity across folds" |
| 5-fold binary AUROC | 0.9435 +/- 0.0448 | `models/cv_results.json` | "robust triage AUROC across folds" |

Do not headline:

- `ece=0.0` from `models/test_metrics.json`
- old synthetic/combined data results
- old B3 polluted checkpoint numbers

## HPV Wording

Safe:

> The system estimates HPV-related morphology risk from visible cytologic
> changes. It does not detect viral DNA/RNA.

Unsafe:

> The system detects HPV.

Safe Thai:

> ระบบประเมินความเสี่ยงที่สัมพันธ์กับ HPV จากลักษณะทางเซลล์วิทยา ไม่ใช่การ
> ตรวจหาเชื้อ HPV DNA/RNA โดยตรง

## Grade, KOIL, and Binary Wording

Safe:

> The four-class grade display is the primary cytology output. KOIL is an
> independent morphology endpoint. The binary normal/abnormal view is a safety
> layer used to reduce missed abnormal cases.

Unsafe:

> The project is just a binary triage classifier.

Unsafe:

> The four-class grade model or KOIL endpoint is ready for diagnosis.

## Dataset Count Wording

Safe:

> Current public evidence uses 917 Herlev images for grade/triage and 4,049
> SIPaKMeD cropped cells for the separate KOIL morphology endpoint.

Unsafe:

> The model was trained on 4,966 ThinPrep images.

Unsafe:

> Data augmentation increased the number of real clinical cases.

## Bethesda Co-finding Wording

Safe:

> Organism-related and reactive/reparative co-findings are a proposed future
> multi-label endpoint. No current model or performance result supports them.

Unsafe:

> Anong currently detects Candida, Trichomonas, bacterial vaginosis,
> Actinomyces, HSV, CMV, or reactive change.

## Claim Review Checklist

Before generating any proposal, deck, report, webpage, or abstract:

- [ ] Does every metric match canonical JSON?
- [ ] Does HPV wording avoid "detect infection"?
- [ ] Does the document say clinician sign-off is required?
- [ ] Does it avoid clinical-use readiness?
- [ ] Does it disclose no Thai validation yet?
- [ ] Does it disclose that Herlev has no KOIL support and the separate KOIL endpoint uses SIPaKMeD?
- [ ] Does it describe binary triage as a safety layer, not the whole product?
- [ ] Does it avoid old synthetic/B3 polluted metrics?
- [ ] Did `python tools/audit_claims.py` pass for current source-of-truth files?

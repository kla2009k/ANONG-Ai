# Clinical Context, Formal PDF, KOIL Gallery, and Metric Policy Update

**Date:** 2026-07-21  
**Status:** implemented and locally verified  
**Scope:** product hardening; this update does not add Thai clinical validation

## 1. Executive summary

The Analyze workflow now accepts optional age, specimen, screening history,
reported symptoms, prior abnormal-result status, pregnancy,
immunocompromised status, and a separately obtained laboratory HPV result.
These fields are **report-only clinical context**. They are not passed into the
image model and cannot alter its class probabilities.

The system now has a server-generated two-page PDF research pre-screen report,
in addition to the existing HTML print fallback. The PDF includes the release
state, reviewer signature fields, clinical context, image-model result,
original image, class-activation map, and explicit limitations. It is watermarked
`RESEARCH USE ONLY` and must not be described as a regulated medical record.

The Case Gallery now includes four real SIPaKMeD-derived evaluation figures:
locked-test performance, calibration, error analysis, and KOIL Grad-CAM audit.
The gallery exposes errors rather than showing only favorable examples.

## 2. Safety behavior

Symptoms are not used to make an image prediction. When one or more symptoms
are entered, the patient-facing report remains locked until the reviewer checks
the symptom acknowledgement. Even after acknowledgement, the report states
that a cytology AI result cannot rule out disease or replace symptom-led
clinical evaluation.

Other existing release gates remain independent and cannot be bypassed by the
symptom acknowledgement:

- clinician sign-off incomplete;
- high model uncertainty;
- failed image-quality gate;
- unavailable/invalid class-specific XAI;
- trained model not active;
- independent KOIL model or KOIL XAI unavailable when required.

No direct patient identifiers should be entered. The current demo uses a
pseudonymous case ID and has no production patient database.

## 3. WHO-aligned symptom context

The form includes unusual bleeding between periods, after sex, or after
menopause; unusual/foul-smelling discharge; persistent pelvic/back/leg pain;
and unexplained weight loss, fatigue, or appetite loss. WHO states that women
with cervical-cancer symptoms should seek medical care promptly and that
symptomatic women require evaluation rather than reassurance from routine
screening alone.

Primary sources:

- WHO cervical cancer fact sheet (updated 3 July 2026):
  <https://www.who.int/news-room/fact-sheets/detail/cervical-cancer>
- WHO screening and treatment recommendations:
  <https://www.who.int/publications/i/item/9789240030824>

## 4. KOIL data and the HPV claim boundary

SIPaKMeD contains 4,049 cropped cells from 966 source clusters, including 825
koilocytotic cells from 238 clusters. It is appropriate evidence for a
**koilocytotic-morphology** endpoint. The dataset publication does not provide
paired image-level HPV DNA/RNA assay results, infection status, persistence, or
viral genotype labels. Therefore:

- supported: `koilocytotic morphology detected/estimated`;
- supported: `morphology can be associated with HPV-related cellular change`;
- unsupported: `HPV positive`, `HPV detected`, `HPV genotype predicted`, or
  `HPV infection confirmed from the image`.

Primary dataset paper:

- Plissiti et al., SIPaKMeD, ICIP 2018:
  <https://www.cs.uoi.gr/~sfikas/sipakmed2018.pdf>

To create a true HPV-risk endpoint, the next dataset must link de-identified
ThinPrep/LBC images to a reference laboratory HPV test at the patient/specimen
level. Required fields include assay platform, positive/negative status,
genotype where available, collection timestamps, cytology/histology follow-up,
site/scanner metadata, and exclusion criteria. Train/validation/test splits must
be patient-disjoint and preferably site-disjoint. Ethics approval, consent or
waiver, PDPA governance, de-identification, and a locked external test protocol
are mandatory. Cell crops from one slide must never cross splits.

## 5. Training-size and 97% policy

Do not inflate the reported sample size with augmentation, repeated crops, or
synthetic images. Report all three units where relevant: patients/slides,
source clusters, and cell crops. The strongest response to “the dataset is
small” is leakage-resistant evaluation, confidence intervals, learning curves,
external validation, and transparent failure cases, not a cosmetically larger
number.

The project already has a legitimate metric above 97%:

- SIPaKMeD five-morphology locked-test accuracy: **0.9750**;
- SIPaKMeD five-morphology macro F1: **0.9753**;
- independent KOIL specificity: **0.9764**;
- independent KOIL AUROC: **0.9912**.

These metrics apply only to SIPaKMeD conventional Pap-smear morphology. They
must not be presented as Herlev Bethesda-grade accuracy, Thai ThinPrep
performance, clinical diagnostic accuracy, or HPV detection accuracy. The
historical Herlev supported-grade accuracy remains about 0.69 across folds;
binary screening sensitivity is the stronger result for the intended triage
framing. Do not tune on the test set, select a checkpoint by test accuracy, or
change the primary endpoint merely to display a prettier number.

## 6. Files changed

- `server/app.py`: clinical-context schema, symptom release gate, formal PDF
  endpoint, and removal of an unsafe unused patient-text helper.
- `requirements.txt`: pinned ReportLab dependency.
- `web-react/src/components/ClinicalContextPanel.tsx`: accessible context form.
- `web-react/src/pages/Analyze.tsx`: context, backend readiness, symptom
  acknowledgement, PDF download, and report integration.
- `web-react/src/lib/api.ts`: backend configuration/status and report/PDF API.
- `web-react/src/pages/CaseGallery.tsx`: real KOIL evidence gallery.
- `web-react/src/pages/Performance.tsx`: task-qualified 97% metric explanation.
- `web-react/src/pages/Deployment.tsx` and `Settings.tsx`: dynamic endpoint state.
- `web-react/public/sw.js`: navigation network-first cache update to prevent a
  stale cached index from causing an old/blank deployment after a new release.

## 7. Verification record

- Python suite: 35 tests passed.
- New report tests cover symptom acknowledgement and binary PDF output.
- TypeScript and Vite production build passed.
- Claims audit passed.
- Local end-to-end HTTP flow passed: `/api/analyze`, `/api/report`, and
  `/api/report/export/pdf` all returned successful model-backed responses.
- Generated PDF was rendered to images and inspected: two A4 pages, no clipping
  or overlap, original image and XAI present, page numbers and research watermark
  present.

## 8. Remaining boundary

GitHub Pages is a static deployment. Uploaded-image inference and direct PDF
generation require a separately deployed API configured through
`VITE_API_URL`. Without it, the website now states `static evidence mode`,
disables upload analysis, and retains precomputed evidence cases plus the HTML
print fallback. This is intentional; the interface must not pretend that a
model backend exists when it does not.

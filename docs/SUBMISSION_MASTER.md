# Submission Master

Last updated: 2026-07-07

Purpose: one source file for turning CerviCo-Pilot into competition packages
without drifting from the current evidence.

## Project Title

Thai:

> การพัฒนาระบบปัญญาประดิษฐ์เพื่อคัดกรองความผิดปกติของเซลล์ปากมดลูก และการ
> ประเมินความเสี่ยงเชื้อ HPV จากภาพถ่าย ThinPrep

English:

> Development of an AI System for Cervical Cell Abnormality Screening and HPV
> Risk Assessment from ThinPrep Images

Short competition name:

> CerviCo-Pilot

Technical subtitle:

> An Explainable Deep Learning System for Cervical Cytology Screening with
> Uncertainty-Aware, Clinician-in-the-Loop Triage

## One-Liner

CerviCo-Pilot is a clinician-in-the-loop cervical cytology screening co-pilot
that reads Pap/ThinPrep-style images, gives a Bethesda-style 5-class grade,
shows Grad-CAM, flags uncertainty, and blocks patient reports until clinician
sign-off.

## Problem

Cervical cancer prevention depends on screening and follow-up. In real
workflows, delays and unclear communication can cause abnormal screening
results to be missed, misunderstood, or not followed up. Community hospitals
and resource-limited settings need faster triage and clearer communication
without pretending that AI can replace cytology experts.

Use Thailand-specific numeric claims only when primary sources are attached.

## Solution

CerviCo-Pilot turns a cytology image into a structured, reviewable workflow:

1. Upload Pap/ThinPrep-style cytology image.
2. Model outputs Bethesda-style 5-class grade.
3. Binary normal/abnormal safety layer prioritizes sensitivity.
4. HPV-related morphology risk note explains visual HPV-associated patterns.
5. Grad-CAM shows the region emphasized by the model.
6. Uncertainty gate flags cases for human review.
7. Clinician confirms, edits, or rejects the result.
8. Patient-facing report unlocks only after sign-off and acceptable uncertainty.

## Current Evidence

Canonical evidence source: `models/test_metrics.json`,
`models/triage_metrics.json`, `models/cv_results.json`.

Current honest checkpoint:

- EfficientNet-B0.
- Real Herlev public images only.
- Masks excluded.
- No Thai clinical validation yet.

Headline metrics:

- Held-out 5-class accuracy: 0.6934.
- Held-out macro AUROC: 0.7311.
- Held-out HSIL recall: 0.8667.
- Held-out SCC recall: 0.5909.
- Held-out binary triage sensitivity: 1.0.
- Held-out binary AUROC: 0.964.
- Held-out binary confusion: TP 101 / TN 26 / FP 10 / FN 0.
- 5-fold binary sensitivity: 0.9867 +/- 0.0086.
- 5-fold binary AUROC: 0.9435 +/- 0.0448.

## Innovation

The project is not just a classifier:

- 5-class cytology output for structured clinical detail.
- Binary safety layer for high-sensitivity screening.
- HPV-related morphology framing that avoids false HPV infection claims.
- Grad-CAM for visual review.
- MC Dropout uncertainty and abstention behavior.
- Clinician sign-off before patient report release.
- Local audit trail for demo governance.
- Case gallery includes failures, not only good examples.

## Web Demo Pages

- `/`: dashboard with current truth and readiness.
- `/analyze`: upload/sample analysis with Grad-CAM, HPV morphology note,
  sign-off, and audit trail.
- `/gallery`: case gallery with correct and incorrect Herlev examples.
- `/workflow`: clinical pathway and safety gates.
- `/reports`: clinician/patient report preview and lock state.
- `/history`: local audit trail viewer.
- `/ask`: bounded project Q&A assistant.
- `/performance`: metrics and curves.
- `/model`: model card and do-not-use boundaries.

Current web status:

- Sidebar app shell is implemented for desktop, with mobile menu on small
  screens.
- Dashboard, case gallery, workflow, report preview, local history, and bounded
  Q&A pages are included.
- The web app is still a competition/research demo, not a clinical deployment.

## Limitations

- No Thai ThinPrep/LBC validation yet.
- No paired HPV DNA/RNA endpoint yet.
- KOIL is not learned in Phase 1 because Herlev has no true KOIL examples.
- 5-class performance is moderate; binary triage is stronger.
- Grad-CAM is an explanation aid, not proof of causal reasoning.
- LocalStorage audit trail is only for demo; a clinical pilot needs server-side
  signed audit logging.
- Not ready for unsupervised clinical use.

## Samsung Solve for Tomorrow Framing

Emphasize:

- social impact and follow-up gap;
- community-hospital fit;
- understandable patient communication;
- offline-capable prototype;
- human-in-the-loop safety.

Recommended message:

> CerviCo-Pilot helps make abnormal cytology noticed, explained, and followed up
> earlier, without replacing clinicians.

## WSEEC Framing

Emphasize:

- scientific method;
- real public dataset;
- model architecture;
- metrics;
- calibration;
- uncertainty;
- honest limitations;
- validation roadmap.

Recommended message:

> The current model is a Phase 1 screening research prototype: strong on binary
> triage sensitivity, moderate on 5-class grading, and not yet externally Thai
> validated.

## Required Attachments

- `docs/INTENDED_USE_STATEMENT.md`
- `docs/CLAIMS_LEDGER.md`
- `docs/SOURCE_CITATION_LEDGER.md`
- `docs/EXTERNAL_EVIDENCE_REVIEW_2026.md`
- `docs/DATASET_MODEL_CARD.md`
- `docs/VALIDATION_ROADMAP.md`
- `docs/PROJECT_READINESS_SCORECARD.md`
- `docs/JUDGE_QA_BANK.md`
- `docs/FAILURE_MODE_AND_HUMAN_FACTORS.md`
- `docs/WEB_DEMO_RUNBOOK.md`
- `docs/PITCH_SCRIPT_1_3_5MIN.md`
- `docs/POSTER_CONTENT_WSEEC.md`
- `docs/SFT_WSEEC_SUBMISSION_PACKAGE.md`
- `docs/SERVER_SIDE_AUDIT_ROADMAP.md`

## Submission Build Order

1. Read `docs/SUBMISSION_MASTER.md`.
2. Pick competition track from `docs/SFT_WSEEC_SUBMISSION_PACKAGE.md`.
3. Use `docs/PITCH_SCRIPT_1_3_5MIN.md` for spoken script.
4. Use `docs/POSTER_CONTENT_WSEEC.md` for WSEEC poster.
5. Use `docs/WEB_DEMO_RUNBOOK.md` for live demo flow.
6. Use `docs/JUDGE_QA_BANK.md` for defense questions.
7. Run claim audit and web build.

## Final Claim Checklist

- Metrics copied from canonical JSON.
- HPV wording says morphology risk only.
- No Thai validation claim.
- Clinician sign-off stated.
- KOIL limitation stated.
- Reader study listed as future work.
- `python tools\audit_claims.py --all` passes.

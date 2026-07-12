# Intended Use Statement

Last updated: 2026-07-07

Purpose: define exactly what CerviCo-Pilot is intended to do, who it is for,
what inputs it accepts, and what claims are outside scope.

## Intended Use

CerviCo-Pilot is a **clinician-in-the-loop cervical cytology screening support
prototype**. It is intended to assist trained medical personnel in reviewing
Pap/ThinPrep-style cervical cytology images by producing:

1. a Bethesda-style 5-class abnormality suggestion;
2. a binary normal/abnormal safety-triage view;
3. an HPV-related morphology risk note from visible cytologic patterns;
4. Grad-CAM visual explanation;
5. uncertainty/abstention signal;
6. a clinician sign-off workflow before any patient-facing report is released.

## Intended Users

Primary users:

- cytotechnologists;
- pathologists;
- trained clinicians in cervical screening workflows;
- supervised research/demo evaluators.

Not intended users:

- patients using the tool alone;
- untrained lay users making medical decisions;
- autonomous clinical deployment without institutional governance.

## Intended Patient / Image Population

Current evidence supports only:

- public Herlev cervical cytology images;
- Phase 1 retrospective research evaluation;
- Pap/ThinPrep-style field images used for demo and workflow prototyping.

Not yet supported:

- Thai ThinPrep/LBC clinical deployment;
- prospective patient workflow;
- whole-slide routine screening;
- HPV-positive prediction validated against DNA/RNA testing;
- KOIL detection as a validated Phase 1 capability.

## Inputs

Accepted demo input:

- `.jpg`, `.png`, or `.bmp` cytology field image;
- Herlev sample images bundled with the web demo;
- uploaded image sent to local FastAPI server when available.

Required future clinical input:

- de-identified slide/image ID;
- preparation type: ThinPrep, other LBC, or conventional Pap;
- scanner/camera/magnification;
- staining and site metadata when available;
- expert reference label;
- optional paired HPV DNA/RNA result;
- optional histology outcome.

## Outputs

The system may output:

- AI-suggested class: NILM, LSIL, HSIL, SCC, KOIL placeholder;
- probability bars for each class;
- binary normal/abnormal triage state;
- HPV-related morphology risk note;
- Grad-CAM heatmap;
- uncertainty level;
- clinician report draft;
- locked patient report draft after sign-off.

## Explicit Do-Not-Use Boundaries

Do not use CerviCo-Pilot to:

- make a final diagnosis without clinician review;
- replace cytotechnologists, pathologists, or clinicians;
- detect HPV infection directly;
- replace HPV DNA/RNA testing;
- claim Thai clinical validation;
- release patient results when uncertainty is high;
- use KOIL as a validated Phase 1 performance claim;
- deploy in real patient workflow without ethics, governance, and external
  validation.

## Decision Point

CerviCo-Pilot belongs **before confirmatory clinical decisions**, as a screening
support and prioritization tool. The correct decision point is:

> after image capture and before final clinician-confirmed result release.

It should support:

- prioritizing suspicious cytology cases;
- showing why the model focused on a region;
- routing uncertain cases back to human review;
- creating clearer report drafts after clinician approval.

It should not independently decide:

- treatment;
- cancer diagnosis;
- HPV infection status;
- discharge from follow-up.

## Competition Wording

Safe short wording:

> CerviCo-Pilot is a Phase 1 clinician-in-the-loop cytology screening support
> prototype. It grades cervical cytology images, shows model attention, flags
> uncertainty, and requires clinician sign-off before any patient-facing report.

Unsafe wording:

> The system diagnoses cervical cancer or detects HPV infection.

## Evidence Boundary

Current performance evidence comes from:

- `models/test_metrics.json`;
- `models/triage_metrics.json`;
- `models/cv_results.json`;
- `docs/CALIBRATION_EXPERIMENT_REPORT.md`.

External clinical/public-health sources support the problem framing only. They
do not create new model-performance claims.


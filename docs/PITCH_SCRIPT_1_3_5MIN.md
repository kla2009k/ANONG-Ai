# Pitch Scripts: 1, 3, and 5 Minutes

Last updated: 2026-07-07

Purpose: give safe scripts for different judging formats. These scripts must be
kept aligned with `docs/CLAIMS_LEDGER.md` and `docs/SUBMISSION_MASTER.md`.

## 1-Minute Pitch

CerviCo-Pilot is a clinician-in-the-loop AI co-pilot for cervical cytology
screening. The goal is simple: abnormal cervical cells should be noticed,
explained, and followed up early, before a preventable cancer becomes a late
diagnosis.

The system reads Pap/ThinPrep-style cytology images and outputs a
Bethesda-style 5-class grade. It also shows a binary safety-triage view,
Grad-CAM heatmap, uncertainty level, and HPV-related morphology risk. That HPV
part is important: the system does not detect HPV infection or replace HPV
DNA/RNA testing. It only flags visible cell patterns that may be HPV-related.

We trained and evaluated the current Phase 1 model on real public Herlev
images. The 5-class model is moderate, but the binary safety layer is strong:
held-out binary sensitivity is 1.0, and 5-fold sensitivity is 0.9867 +/- 0.0086.
Every patient-facing report is locked until a clinician confirms the result.

This is not a replacement for clinicians. It is a workflow prototype for safer,
faster screening support in resource-limited settings.

## 3-Minute Pitch

### Opening

Cervical cancer is one of the clearest examples of a cancer that should often be
prevented through screening and follow-up. The problem is not only detecting
abnormal cells. The problem is the workflow after screening: delays,
communication gaps, limited expert availability, and patients who may not return
for follow-up.

CerviCo-Pilot was built for that second gap. It is a clinician-in-the-loop AI
co-pilot for cervical cytology screening.

### What It Does

The user uploads a Pap or ThinPrep-style cytology image. The system returns a
Bethesda-style 5-class grade: NILM, LSIL, HSIL, SCC, or KOIL placeholder. It also
adds a binary normal/abnormal safety-triage view because screening should
prioritize not missing abnormal cases.

Then it shows three safety layers:

1. Grad-CAM heatmap, so the clinician can see what region the model emphasized.
2. Uncertainty, so the system can abstain instead of forcing a confident answer.
3. Clinician sign-off, so patient-facing reports stay locked until a human
   confirms or edits the result.

The web demo also includes a case gallery with wrong predictions. That is
intentional. In medical AI, hiding errors makes a prototype less trustworthy.

### HPV Framing

The title mentions HPV risk, so we are careful with the wording. CerviCo-Pilot
does not detect HPV infection and does not replace HPV DNA/RNA testing. It
estimates HPV-related morphology risk from visible cytologic patterns, such as
low-grade changes or possible koilocytic features. Paired HPV DNA/RNA labels are
a future validation endpoint.

### Evidence

The current model is an EfficientNet-B0 trained and evaluated on real public
Herlev images. It is Phase 1 evidence, not Thai clinical validation.

The held-out 5-class accuracy is 0.6934, with macro AUROC 0.7311. That is
moderate, and we state that openly. The safety triage layer is stronger:
held-out binary sensitivity is 1.0, held-out binary AUROC is 0.964, and 5-fold
binary sensitivity is 0.9867 +/- 0.0086.

### Closing

CerviCo-Pilot is not trying to replace cytotechnologists or pathologists. It is
trying to make abnormal cytology easier to catch, easier to explain, and easier
to follow up safely.

## 5-Minute Pitch

### 0:00-0:45 Problem

Cervical cancer prevention depends on three things working together: screening,
clear interpretation, and timely follow-up. In resource-limited settings, the
weak point is often not a single algorithmic decision. It is the workflow: images
wait to be read, abnormal findings may not be explained clearly, and some
patients do not return in time.

Our project, CerviCo-Pilot, focuses on that workflow gap.

### 0:45-1:45 Product

CerviCo-Pilot is a clinician-in-the-loop cervical cytology screening support
prototype. It accepts a Pap or ThinPrep-style cytology image and returns:

- a Bethesda-style 5-class abnormality suggestion;
- a binary safety-triage view;
- an HPV-related morphology risk note;
- a Grad-CAM heatmap;
- an uncertainty flag;
- a clinician sign-off workflow;
- a locked patient-friendly report.

This design matters because a raw classifier is not enough for healthcare.
Clinicians need to see what the model looked at, when not to trust it, and how
to override it.

### 1:45-2:35 HPV and Safety Boundary

The HPV wording is deliberately careful. HPV DNA/RNA testing is the test for
infection status. An image model cannot replace that. CerviCo-Pilot only
estimates HPV-related morphology risk from visible cell changes. If paired HPV
DNA/RNA labels are available in a future Thai ThinPrep dataset, HPV status can
be evaluated as a separate endpoint.

Safety boundaries are built into the interface:

- high uncertainty blocks patient report release;
- clinicians can confirm, edit, or reject results;
- the model card states do-not-use cases;
- local audit trail records demo sign-off actions;
- the gallery includes failure cases.

### 2:35-3:35 Evidence

The current evidence is honest Phase 1 evidence on real public Herlev images.
The checkpoint is EfficientNet-B0. Masks are excluded. Old synthetic-heavy
metrics are not used as public evidence.

Current metrics:

- held-out 5-class accuracy: 0.6934;
- held-out macro AUROC: 0.7311;
- held-out HSIL recall: 0.8667;
- held-out SCC recall: 0.5909;
- held-out binary sensitivity: 1.0;
- held-out binary AUROC: 0.964;
- 5-fold binary sensitivity: 0.9867 +/- 0.0086;
- 5-fold binary AUROC: 0.9435 +/- 0.0448.

The interpretation is: 5-class grading is promising but not complete; binary
triage is stronger and useful as a safety layer.

### 3:35-4:25 Web Demo

The web demo shows the full workflow:

- dashboard for current truth;
- analysis page with samples and upload mode;
- case gallery with correct and incorrect examples;
- workflow page for safety gates;
- report preview with patient-report lock;
- history page with local audit;
- Q&A page for explaining the project;
- model card and performance pages.

The point is to show a governed workflow, not just an isolated neural network.

### 4:25-5:00 Next Steps

The next scientific steps are clear:

1. Thai ThinPrep/LBC retrospective validation.
2. Paired HPV DNA/RNA endpoint study.
3. Pathologist-reviewed error gallery.
4. Reader study with and without AI.
5. Server-side signed audit log.
6. Prospective workflow study only after ethics approval.

CerviCo-Pilot is not a final clinical device. It is a credible, transparent
Phase 1 prototype designed to make cervical cytology screening safer, faster,
and more explainable.


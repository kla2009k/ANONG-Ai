# Failure Mode and Human Factors Analysis

Last updated: 2026-07-07

Purpose: identify how CerviCo-Pilot can fail and how the prototype mitigates
those failures before any clinical pilot.

## Intended Use Boundary

CerviCo-Pilot is a decision-support prototype for cervical cytology screening
research. It is not a diagnostic device, not an HPV DNA/RNA test, not a
replacement for cytotechnologists/pathologists, and not validated for Thai
clinical deployment.

## Human Factors Risks

| Risk | Why It Matters | Current Mitigation | Remaining Gap |
| --- | --- | --- | --- |
| Automation bias | Clinician may trust AI despite wrong prediction | UI shows uncertainty, probabilities, Grad-CAM, and sign-off controls | Reader study needed to measure overreliance |
| Patient misunderstanding | Patient may think AI result is final diagnosis | Patient report locked until clinician sign-off; disclaimers near result | Need health-literacy testing in Thai |
| Grad-CAM overtrust | Heatmap can look convincing even when wrong | Case gallery includes wrong predictions and states Grad-CAM is review aid | Pathologist-reviewed heatmap failure gallery needed |
| HPV wording confusion | Image model may be mistaken for HPV infection test | UI and docs say HPV-related morphology risk only | Paired HPV DNA/RNA endpoint still missing |
| Alert fatigue | False positives can increase referrals | Binary triage presented as safety layer with specificity limitation | Threshold tuning and workflow study needed |
| Local audit overclaim | Demo audit may be mistaken for regulated audit log | Docs state localStorage is demo-only | Server-side signed audit log needed for pilot |

## Technical Failure Modes

| Failure Mode | Detection | Current Response | Future Control |
| --- | --- | --- | --- |
| Blurry/low-cellularity image | User/clinician review; low confidence may appear | Reject slide action | Add image-quality classifier |
| Out-of-domain Thai stain/scanner | Not reliably detected in Phase 1 | Disclose no Thai validation | Thai locked external validation |
| HSIL/SCC boundary confusion | Confusion matrix and case gallery | Human review and high-risk referral | More data + expert error review |
| SCC undercall as HSIL | Error-case gallery shows this risk | Still abnormal/high-risk triage | Clinically chosen referral rules |
| KOIL not learned | Per-class recall and dataset card | Mark KOIL as Phase 2 | Collect koilocytosis annotations |
| High uncertainty | MC Dropout/uncertainty level | Block patient report | Tune abstention threshold externally |
| Misleading confidence | Calibration report | Temperature scaling on Herlev only | External calibration and selective classification |

## Safety Requirements Before Pilot

1. Ethics/IRB review for patient data.
2. De-identification at source.
3. Locked Thai ThinPrep/LBC test set.
4. Patient/slide-level split to prevent leakage.
5. Reader study with unaided vs AI-assisted arms.
6. Server-side signed audit log.
7. Explicit intended-use training for users.
8. Procedure for handling uncertainty, poor-quality images, and disagreement.

## UI Controls Already Implemented

- Intended-use banner on Analyze page.
- HPV-related morphology risk panel with DNA/RNA caveat.
- High-uncertainty alert.
- Patient report lock until sign-off.
- Confirm/edit/reject controls.
- Local audit trail and export.
- History page for local demo audit review.
- Case gallery that includes wrong predictions.
- Ask page bounded to project Q&A, not patient medical advice.
- Sidebar app shell and dashboard make the decision-support boundary visible
  across the demo.
- Report preview page demonstrates patient-report lock/unlock behavior without
  needing a live clinical backend.

## Pilot Readiness Verdict

Current status:

> Strong for competition demo and Phase 1 research prototype.

Not ready for:

> Unsupervised clinical deployment or patient-facing autonomous diagnosis.

Highest priority next controls:

1. Thai ThinPrep validation.
2. Pathologist-reviewed error gallery.
3. Reader study.
4. Server-side audit logging.
5. Health-literacy testing for patient report wording.

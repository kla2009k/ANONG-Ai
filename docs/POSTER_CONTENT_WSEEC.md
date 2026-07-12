# WSEEC Poster Content

Last updated: 2026-07-07

Purpose: poster-ready content for a science/engineering fair. Keep the poster
honest: Phase 1 Herlev-only, not Thai clinical validation.

## Poster Title

**CerviCo-Pilot: An Explainable Deep Learning System for Cervical Cytology
Screening with Uncertainty-Aware, Clinician-in-the-Loop Triage**

Thai subtitle:

**ระบบปัญญาประดิษฐ์เพื่อคัดกรองความผิดปกติของเซลล์ปากมดลูกและประเมิน
HPV-related morphology risk จากภาพ Pap/ThinPrep-style**

## Section 1: Problem

Cervical cancer is largely preventable when screening and follow-up pathways
work. In practice, cervical screening can be slowed by limited expert
availability, unclear communication, and delayed follow-up. A useful AI system
therefore must support the workflow, not simply output a class.

Do not include Thailand-specific exact numbers unless the final poster attaches
the primary source.

## Section 2: Objective

Develop a Phase 1 AI screening-support prototype that:

- grades cervical cytology images with a Bethesda-style 5-class output;
- adds a high-sensitivity binary triage safety layer;
- shows Grad-CAM model attention;
- flags uncertainty;
- gives HPV-related morphology risk without claiming HPV infection detection;
- requires clinician sign-off before patient-facing report release.

## Section 3: Dataset

Current dataset:

- Herlev public cervical cytology images;
- 917 real images;
- segmentation masks excluded;
- no Thai ThinPrep data yet;
- KOIL not validated because Herlev has no true KOIL examples.

Poster visual:

- dataset card;
- class distribution if available;
- note: "Phase 1 public-dataset prototype."

## Section 4: Method

Pipeline:

1. Image input.
2. Preprocessing.
3. EfficientNet-B0 classifier.
4. Bethesda-style 5-class prediction.
5. Binary normal/abnormal safety layer.
6. Grad-CAM heatmap.
7. MC Dropout uncertainty.
8. Clinician sign-off and report gate.

Poster visual:

- flowchart from `/workflow`;
- one sample original image and Grad-CAM.

## Section 5: Results

Use exact values from canonical sources:

| Metric | Value | Interpretation |
| --- | ---: | --- |
| Held-out 5-class accuracy | 0.6934 | moderate 5-class grading |
| Held-out macro AUROC | 0.7311 | moderate multiclass discrimination |
| Held-out HSIL recall | 0.8667 | strong HSIL recall |
| Held-out SCC recall | 0.5909 | SCC remains imperfect |
| Held-out binary sensitivity | 1.0 | no false negatives in this held-out triage test |
| Held-out binary AUROC | 0.964 | strong binary discrimination |
| 5-fold binary sensitivity | 0.9867 +/- 0.0086 | robust high sensitivity |
| 5-fold binary AUROC | 0.9435 +/- 0.0448 | robust triage AUROC |

Poster visual:

- ROC curve;
- reliability/calibration figure;
- confusion matrix;
- case gallery thumbnails.

## Section 6: Explainability and Safety

Safety layers:

- Grad-CAM: shows emphasized image regions.
- Uncertainty: high uncertainty blocks patient report.
- Clinician sign-off: confirm/edit/reject before release.
- Audit trail: local demo log for case ID, AI label, final label, timestamp.
- Model card: do-not-use boundaries.

Important caveat:

> Grad-CAM is a review aid, not proof of causal reasoning.

## Section 7: HPV Framing

Safe poster wording:

> CerviCo-Pilot estimates HPV-related morphology risk from visible cytologic
> patterns. It does not detect HPV infection and does not replace HPV DNA/RNA
> testing.

Future endpoint:

- collect paired HPV DNA/RNA status where available;
- evaluate HPV-positive risk prediction separately;
- compare morphology signal against molecular result.

## Section 8: Limitations

- No Thai ThinPrep/LBC validation yet.
- No paired HPV DNA/RNA endpoint yet.
- No reader study yet.
- No prospective workflow study yet.
- KOIL not validated in Phase 1.
- Specificity is moderate, so over-referral is possible.
- LocalStorage audit is demo-only.

## Section 9: Next Steps

1. Thai ThinPrep/LBC retrospective validation.
2. Paired HPV endpoint study.
3. Pathologist-reviewed error gallery.
4. Reader study: unaided vs AI-assisted.
5. Server-side audit log for pilot readiness.
6. Prospective workflow study after ethics approval.

## QR / Demo Box

Add a QR code or local URL pointing to the web demo.

Recommended demo order:

1. `/` dashboard;
2. `/analyze`;
3. `/gallery`;
4. `/reports`;
5. `/model`.

## One-Sentence Poster Conclusion

CerviCo-Pilot shows that cervical cytology AI can be framed as a transparent,
uncertainty-aware, clinician-controlled screening workflow rather than a black
box replacement for clinicians.


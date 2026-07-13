# Dataset and Model Card

> **KOIL endpoint update (2026-07-13):** The historical Herlev checkpoint has
> zero true KOIL support, so KOIL is excluded from the deployed grade output.
> A separate EfficientNet-B0 KOIL morphology model is internally validated on
> 4,049 official SIPaKMeD conventional Pap-smear cells using source-cluster-
> disjoint splits. Locked-test sensitivity is 0.9624, specificity 0.9764, and
> AUROC 0.9912. See `KOIL_REAL_DATA_VALIDATION_2026.md`. This is not ThinPrep
> validation and not HPV DNA/RNA detection.

Last updated: 2026-07-06

## Model

Name: CerviCo-Pilot Phase 1 Screening Model  
Architecture: EfficientNet-B0  
Task: cervical cytology image screening  
Outputs:

- Bethesda-style four-class grade: NILM / LSIL / HSIL / SCC
- independent KOIL morphology assessment from the SIPaKMeD endpoint
- binary safety triage: normal vs abnormal
- HPV-related morphology risk note
- Grad-CAM heatmap
- MC Dropout uncertainty flag

## Intended Use

Assist clinicians, cytotechnologists, or supervised medical staff in preliminary
screening of cervical cytology images. The model can help prioritize abnormal
cases, explain where it looked, and support follow-up workflow.

The model must be used as decision-support only. A qualified clinician must
review and sign off before any patient-facing result is released.

## Not Intended For

- final diagnosis;
- unsupervised clinical use;
- replacement of cytotechnologists/pathologists;
- HPV DNA/RNA detection;
- self-diagnosis by patients;
- deployment on Thai ThinPrep images without validation;
- deployment on images with severe blur, wrong magnification, or poor staining
  without a quality gate.

## Current Dataset

Primary Phase 1 evidence uses public Herlev cytology images.

Current facts:

- 917 unique real images;
- segmentation masks excluded;
- mapped to Bethesda-style classes;
- no true KOIL support in current Phase 1 data;
- no Thai hospital images;
- no paired HPV DNA/RNA endpoint;
- no histology outcome endpoint.

## Label Schema

| Class | Meaning | Current Status |
| --- | --- | --- |
| NILM | Negative for intraepithelial lesion/malignancy | Supported |
| LSIL | Low-grade squamous intraepithelial lesion | Supported |
| HSIL | High-grade squamous intraepithelial lesion | Supported |
| SCC | Squamous cell carcinoma | Supported but recall imperfect |
| KOIL | Koilocyte / HPV-effect morphology | Separate SIPaKMeD endpoint; not a Bethesda grade |

Binary safety triage:

- negative: NILM
- positive/abnormal: LSIL, HSIL, SCC, KOIL

## Performance

Held-out test:

- supported-grade four-class accuracy: 0.6934
- supported-grade four-class QWK: 0.687
- HSIL recall: 0.8667
- SCC recall: 0.5909
- historical Herlev KOIL recall: N/A (not estimable because support is 0)
- binary sensitivity: 1.0
- binary specificity: 0.7222
- binary AUROC: 0.964
- binary confusion: TP 101 / TN 26 / FP 10 / FN 0

5-fold CV:

- supported-grade four-class accuracy: 0.6904 +/- 0.0618
- QWK: 0.6981 +/- 0.0866
- binary sensitivity: 0.9867 +/- 0.0086
- binary AUROC: 0.9435 +/- 0.0448

## Known Limitations

- Small public dataset.
- No Thai ThinPrep validation.
- No paired HPV endpoint.
- KOIL is internally validated on SIPaKMeD conventional Pap-smear crops, but not externally validated on ThinPrep or paired to HPV assays.
- SCC recall remains imperfect.
- Calibration tuning incomplete.
- Grad-CAM is an explanation aid, not proof of correct reasoning.
- Current model should not be treated as regulatory-grade SaMD.

## Ethical and Clinical Safeguards

- clinician sign-off required;
- uncertainty flag must trigger review;
- patient report must use plain-language caution;
- no automatic diagnosis;
- no HPV infection confirmation;
- no unsupervised deployment.

## Recommended Next Data Collection

To strengthen the model:

- de-identified Thai ThinPrep/LBC images;
- expert Bethesda labels;
- paired HPV DNA/RNA results where available;
- quality labels;
- site/scanner/stain metadata;
- slide/patient grouping for leakage-safe splits;
- optional histology outcome for CIN2+ endpoint.

# Error Analysis Plan

Last updated: 2026-07-06

## Purpose

Make failures visible. A credible medical-AI project should explain not only
where it works, but where it fails and how those failures will be reduced.

## Current Known Error Pattern

From the honest held-out Herlev evaluation:

- 5-class accuracy is moderate: 0.6934.
- HSIL recall is strong: 0.8667.
- SCC recall is imperfect: 0.5909.
- KOIL recall is 0.0 because KOIL support is 0.
- Binary triage has no false negatives in the held-out Herlev test, but this
  must not be generalized beyond that test.

## Required Error Buckets

Every misclassification should be categorized into at least one bucket:

1. Class boundary ambiguity: NILM vs LSIL, LSIL vs HSIL, HSIL vs SCC.
2. Poor image quality: blur, staining, low cellularity, artifact.
3. Morphology limitation: rare pattern not learned.
4. Domain shift: scanner/stain/preparation different from training.
5. Localization issue: Grad-CAM focuses on non-diagnostic region.
6. Calibration issue: high confidence but wrong.
7. Uncertainty success: wrong/ambiguous case correctly flagged.
8. Label uncertainty: reference label may be debatable.

## Analysis Tables

For each evaluation run, produce:

- confusion matrix;
- per-class recall/precision/F1;
- top false-negative cases for abnormal/high-risk;
- top false-positive NILM cases;
- high-confidence wrong cases;
- low-confidence correct cases;
- high-uncertainty abstained cases;
- Grad-CAM quality review sample.

## Case Review Template

Use this template for each important error:

```text
case_id:
image_id:
true_label:
predicted_label:
binary_triage_result:
confidence:
uncertainty_level:
Grad-CAM acceptable? yes/no/unclear
image_quality:
likely_error_bucket:
clinical_risk:
what should change:
```

## High-Priority Failures

Prioritize review in this order:

1. HSIL/SCC predicted as NILM.
2. SCC predicted as LSIL/NILM.
3. High-confidence wrong predictions.
4. Low-quality images not rejected.
5. KOIL/HPV-effect claims without data support.
6. Grad-CAM focused on background/artifact.

## Deliverables

Near-term:

- `docs/ERROR_ANALYSIS_REPORT_HERLEV.md`
- sample reviewed error cases;
- threshold recommendation for uncertainty;
- list of needed Thai data examples.

Future:

- Thai ThinPrep domain-shift error report;
- HPV endpoint error report;
- reader-study disagreement report.


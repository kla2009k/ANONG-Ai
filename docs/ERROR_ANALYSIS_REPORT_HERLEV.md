# Error Analysis Report: Herlev Phase 1

Last updated: 2026-07-06  
Source metrics: `models/triage_metrics.json`, `models/test_metrics.json`,
`models/cv_results.json`

## Scope

This report analyzes known error patterns from the current honest Phase 1 model:

- checkpoint: `models/best_cervical.pt`
- architecture: EfficientNet-B0
- data: public Herlev cytology images, masks excluded
- test size: n=137
- classes: NILM / LSIL / HSIL / SCC / KOIL placeholder

This is not a clinical validation report. It is an engineering error-analysis
summary to guide next data collection, calibration, and UI safety work.

## Headline Results

Held-out 5-class:

- accuracy: **0.6934**
- QWK: **0.687**
- macro F1: **0.5545**
- HSIL recall: **0.8667**
- SCC recall: **0.5909**
- KOIL recall: **N/A (not estimable)** because KOIL support is 0

Binary normal/abnormal safety layer:

- sensitivity: **1.0**
- specificity: **0.7222**
- AUROC: **0.964**
- confusion: **TP 101 / TN 26 / FP 10 / FN 0**

## 5-Class Confusion Matrix

Rows are true labels. Columns are predictions.

| True \ Pred | NILM | LSIL | HSIL | SCC | KOIL |
| --- | ---: | ---: | ---: | ---: | ---: |
| NILM | 26 | 1 | 7 | 2 | 0 |
| LSIL | 1 | 30 | 16 | 2 | 0 |
| HSIL | 1 | 0 | 26 | 3 | 0 |
| SCC | 0 | 0 | 9 | 13 | 0 |
| KOIL | 0 | 0 | 0 | 0 | 0 |

## Error Buckets

### 1. NILM over-called as abnormal

Observed:

- 10 NILM cases are over-called as abnormal in binary triage.
- Most are predicted as HSIL (7) or SCC (2), with 1 as LSIL.

Clinical implication:

- This creates over-referral and extra review workload.
- In screening, this is safer than false reassurance, but still matters for
  workflow burden.

Next action:

- Review NILM false positives for staining, nucleus artifacts, inflammation, or
  field quality.
- Add quality labels and site/scanner metadata in Thai data.

### 2. LSIL vs HSIL boundary

Observed:

- 16 LSIL cases are predicted as HSIL.

Clinical implication:

- This is a severity over-call.
- It may increase referral urgency but is less dangerous than under-calling HSIL
  as NILM.

Next action:

- Add ordinal loss/error analysis.
- In UI, show this as "screening support" and require clinician confirmation.

### 3. HSIL mostly caught, but some severity confusion remains

Observed:

- HSIL recall is 0.8667.
- 26/30 HSIL cases are predicted as HSIL.
- 3 HSIL cases are predicted as SCC.
- 1 HSIL case is predicted as NILM.

Clinical implication:

- The single HSIL-to-NILM 5-class error is important.
- However, the binary triage view reports FN=0, meaning the abnormal safety
  layer still flagged the case as abnormal at threshold 0.5.

Next action:

- Inspect this case manually.
- Check probability distribution and uncertainty.
- If it is high uncertainty, the abstention policy is doing its job.

### 4. SCC recall remains imperfect

Observed:

- SCC recall is 0.5909.
- 13/22 SCC cases are predicted as SCC.
- 9/22 SCC cases are predicted as HSIL.

Clinical implication:

- Most SCC errors remain high-risk abnormal rather than normal.
- For triage, HSIL and SCC both require urgent expert review, so binary safety is
  preserved.
- For final grading, this is not sufficient for diagnostic use.

Next action:

- Do not present SCC grading as validated diagnosis.
- Add more SCC examples in Thai/Phase 2 data.
- Report HSIL/SCC together for high-risk catch when appropriate.

### 5. KOIL is not learned

Observed:

- KOIL support is 0 in Herlev.
- KOIL recall is not estimable because there are no true KOIL examples.

Clinical implication:

- Current KOIL/HPV-effect output is not validated.
- HPV claim must stay at morphology-risk framing, not detection.

Next action:

- Add true koilocytosis/HPV-effect annotations in Thai ThinPrep protocol.
- Add paired HPV DNA/RNA endpoint if available.

## High-Priority Case Review Queue

Review cases in this order:

1. HSIL predicted as NILM in 5-class view.
2. NILM predicted as SCC.
3. NILM predicted as HSIL.
4. SCC predicted as HSIL.
5. Any high-confidence wrong case.
6. Any wrong case with low uncertainty.
7. Any Grad-CAM focused on background/artifact.

## Safety Interpretation

The current system is best described as:

> a screening co-pilot that keeps a detailed 5-class output but relies on a
> binary safety layer to reduce missed abnormal/high-risk cases.

Do not describe it as:

> a final 5-class diagnostic model.

## Recommended Fixes

Short-term:

- Add explicit HPV risk panel and disclaimer in UI.
- Block patient report export for high uncertainty.
- Use uncertainty and quality flags to route ambiguous cases to manual review.
- Keep claim audit passing.

Medium-term:

- Collect Thai ThinPrep/LBC data with quality labels.
- Add reviewed error-case gallery.
- Fit and report temperature scaling, but do not overclaim calibration.
- Run reader study.

Long-term:

- Validate on held-out Thai site.
- Add paired HPV DNA/RNA endpoint.
- Evaluate workflow outcomes such as follow-up completion.

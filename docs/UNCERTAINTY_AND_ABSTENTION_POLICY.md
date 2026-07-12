# Uncertainty and Abstention Policy

Last updated: 2026-07-06

## Purpose

Uncertainty is a safety mechanism. It should prevent overconfident automation,
not decorate the UI.

Current implementation uses MC Dropout-style uncertainty as a prototype. It is
not yet fully calibrated, so all thresholds below are policy targets to validate,
not final clinical thresholds.

## Output Levels

The UI/report should express uncertainty in three levels:

| Level | Meaning | Action |
| --- | --- | --- |
| Low | Model output is internally stable | Clinician still reviews and signs off |
| Medium | Model has noticeable ambiguity | Show caution; require explicit clinician note |
| High | Model should not be trusted alone | Abstain: no patient-facing report until clinician review |

## Abstention Rules

The system should abstain if any of these are true:

- top-class probability is below the configured threshold;
- entropy is above the configured threshold;
- MC Dropout top-class standard deviation is above the configured threshold;
- top-2 class margin is too small;
- image quality gate fails;
- predicted class is KOIL in Phase 1;
- Grad-CAM focuses mostly on background/artifact;
- input appears outside cytology domain.

## Current Policy For Phase 1

Because calibration is not complete:

1. Never say "the model is certain."
2. Use "low/medium/high uncertainty" instead of absolute certainty claims.
3. If uncertainty is high, show:  
   **"ระบบไม่มั่นใจในผลนี้ ต้องให้แพทย์อ่านสไลด์และยืนยันเอง"**
4. Block automatic patient-report export for high-uncertainty cases.
5. Require clinician sign-off for all cases, including low uncertainty.

## Suggested Metrics

Future calibration/abstention experiments should report:

- ECE and adaptive ECE;
- Brier score;
- reliability diagrams;
- coverage vs accuracy;
- coverage vs binary sensitivity;
- error rate among high-uncertainty cases;
- proportion of cases abstained;
- class-specific abstention rate;
- site/scanner-specific abstention rate.

## Threshold Selection Protocol

Thresholds should be selected on validation data only, then locked before test.

Recommended objective:

1. Maintain high binary sensitivity for abnormal/high-risk cases.
2. Reduce false reassurance on HSIL/SCC.
3. Keep abstention workload feasible.
4. Preserve transparency: the user sees why the case was abstained.

Do not tune thresholds on the final test set.

## UI Language

Safe:

> AI confidence is not a diagnosis. This case still requires clinician review.

Safe Thai:

> ความมั่นใจของ AI ไม่ใช่ผลวินิจฉัย ต้องให้บุคลากรทางการแพทย์ตรวจทานและยืนยัน

High-uncertainty Thai:

> ระบบไม่มั่นใจในผลนี้ จึงไม่ควรออกผลให้ผู้ป่วยโดยอัตโนมัติ กรุณาให้แพทย์หรือผู้เชี่ยวชาญตรวจสไลด์โดยตรง

## Report Policy

For high uncertainty:

- hide confident class wording in the patient layer;
- show "ต้องตรวจทานเพิ่มเติม";
- include no cancer/HPV conclusion;
- require clinician note before export.

For medium uncertainty:

- show class suggestion but with caution;
- require clinician note;
- include follow-up language but avoid definitive phrasing.

For low uncertainty:

- show class suggestion, triage, heatmap, and disclaimer;
- still require clinician sign-off.


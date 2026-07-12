# Calibration Experiment Plan

Last updated: 2026-07-06

## Purpose

Discrimination metrics such as AUROC do not prove that the model's probabilities
are trustworthy. CerviCo-Pilot needs a calibration workflow so uncertainty can
be used safely for abstention and clinician review.

## Current Status

Before this plan, the project reported:

- binary triage ROC/reliability in `docs/CURVES_CALIBRATION.md`;
- ECE/Brier from `ml/scripts/gen_curves.py`;
- no post-hoc temperature scaling.

Do not claim "fully calibrated." The current goal is to measure calibration and
test a simple post-hoc correction.

## Experiment

Use post-hoc temperature scaling:

1. Load `models/best_cervical.pt`.
2. Compute logits on `data/processed/split_val.csv`.
3. Fit one scalar temperature on validation logits by minimizing multiclass
   cross-entropy.
4. Apply the same temperature to `data/processed/split_test.csv`.
5. Compare before/after on held-out test:
   - multiclass NLL;
   - multiclass ECE;
   - binary abnormal-vs-normal ECE;
   - binary Brier;
   - binary AUROC;
   - threshold 0.5 confusion.

## Acceptance Criteria

The experiment is useful if:

- it runs reproducibly from the shipped checkpoint;
- it writes a report to `docs/CALIBRATION_EXPERIMENT_REPORT.md`;
- it does not change discrimination claims without evidence;
- it states whether calibration improved or not;
- it keeps the same safety disclaimers.

## Command

```powershell
python ml\scripts\calibrate_temperature.py
```

## Interpretation Rules

- If ECE improves: say "post-hoc temperature scaling improved calibration on
  held-out Herlev, but external validation is still needed."
- If ECE worsens: keep uncalibrated probabilities and use uncertainty as a
  review signal only.
- If binary threshold behavior changes: document it; do not silently change
  deployment threshold.
- In all cases: clinician sign-off remains mandatory.


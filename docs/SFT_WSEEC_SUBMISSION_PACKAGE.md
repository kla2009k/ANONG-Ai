# Samsung SFT + WSEEC Submission Package

Last updated: 2026-07-07

Purpose: organize what to submit for Samsung Solve for Tomorrow and WSEEC while
keeping both packages aligned with the same evidence.

## Shared Core

Use the same project truth for both competitions:

- Phase 1 Herlev-only research prototype;
- EfficientNet-B0 checkpoint;
- 5-class Bethesda-style output as product identity;
- binary normal/abnormal triage as safety layer;
- HPV-related morphology risk, not HPV infection detection;
- Grad-CAM, uncertainty, sign-off, and report gating;
- no Thai clinical validation yet.

## Package A: Samsung Solve for Tomorrow

### Main Story

Samsung SFT should focus on social impact and human-centered workflow:

> CerviCo-Pilot helps community screening workflows notice, explain, and follow
> up abnormal cytology earlier, while keeping clinicians in control.

### Deliverables

1. 1-page executive summary.
2. 3-minute pitch script.
3. Web demo video.
4. Problem-solution-impact slide deck.
5. Prototype screenshots.
6. Roadmap and partnership ask.
7. Claim-safe FAQ.

### Slide Outline

1. Problem: preventable cancer, follow-up workflow gap.
2. User: community hospital screening team and patient.
3. Insight: interpretation alone is not enough; follow-up must be clearer.
4. Solution: AI cytology co-pilot with explanation, uncertainty, and sign-off.
5. Demo: upload/sample, Grad-CAM, sign-off, patient report lock.
6. Impact: faster triage, clearer communication, offline-capable prototype.
7. Safety: no autonomous diagnosis, no HPV DNA/RNA detection, no Thai validation
   claim.
8. Next steps: Thai ThinPrep data, reader study, pilot governance.

### What To Emphasize

- empathy and workflow;
- patient-friendly report only after clinician sign-off;
- offline demo and local resource fit;
- honest limits as responsible AI.

### What Not To Lead With

- raw architecture details;
- dense confusion matrix;
- unsupported Thailand numeric claims;
- "AI replaces experts" framing.

## Package B: WSEEC

### Main Story

WSEEC should focus on scientific method and validation discipline:

> CerviCo-Pilot is an explainable, uncertainty-aware cervical cytology screening
> prototype evaluated on real public Herlev images, with honest performance
> reporting and a defined clinical validation roadmap.

### Deliverables

1. Research abstract.
2. Poster.
3. Methods/results report.
4. Web demo.
5. Model card.
6. Error-case gallery.
7. Validation roadmap.
8. Source/citation ledger.

### Poster / Paper Outline

1. Background.
2. Objective.
3. Dataset.
4. Model and training.
5. Explainability and uncertainty.
6. Evaluation metrics.
7. Results.
8. Error analysis.
9. Limitations.
10. Future validation.

### What To Emphasize

- real public dataset;
- held-out and 5-fold evaluation;
- binary vs 5-class distinction;
- calibration report;
- error gallery;
- limitations and next steps.

### What Not To Lead With

- social-impact story without metrics;
- claims of clinical readiness;
- HPV infection detection;
- KOIL capability claim.

## Required Files To Read Before Packaging

- `docs/SUBMISSION_MASTER.md`
- `docs/JUDGE_QA_BANK.md`
- `docs/PITCH_SCRIPT_1_3_5MIN.md`
- `docs/POSTER_CONTENT_WSEEC.md`
- `docs/INTENDED_USE_STATEMENT.md`
- `docs/WEB_DEMO_RUNBOOK.md`
- `docs/CLAIMS_LEDGER.md`
- `docs/SOURCE_CITATION_LEDGER.md`
- `docs/VALIDATION_ROADMAP.md`
- `docs/FAILURE_MODE_AND_HUMAN_FACTORS.md`

## Final Pre-Submission Gate

Before exporting any package:

```powershell
python tools\audit_claims.py --all
npm.cmd run build
```

Manual checks:

- open `/`;
- open `/analyze`, click a sample, confirm sign-off;
- open `/history`;
- open `/gallery`;
- open `/reports`;
- open `/model`;
- verify no public text claims Thai validation or HPV infection detection.

## Short Distinction Between The Two Competitions

Samsung SFT:

> Why this matters for people and community workflows.

WSEEC:

> How the model was built, evaluated, limited, and planned for validation.


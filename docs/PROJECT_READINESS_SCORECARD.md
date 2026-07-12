# Project Readiness Scorecard

Last updated: 2026-07-06

Read with `docs/EXTERNAL_EVIDENCE_REVIEW_2026.md` and
`docs/SOURCE_CITATION_LEDGER.md` for external source backing.

## Summary

CerviCo-Pilot is strong as a Phase 1 medical-AI prototype. It is not clinically
validated yet. The project is now strongest in transparency, safety framing, and
workflow design; weakest in external Thai validation, HPV endpoint evidence, and
reader-study evidence.

## Scorecard

| Area | Status | Evidence | Next Step |
| --- | --- | --- | --- |
| Core model checkpoint | Done | EfficientNet-B0 `best_cervical.pt` inspected | Keep synthetic metrics out of claims |
| 5-class Bethesda-style output | Partial | Held-out acc 0.6934, QWK 0.687 | Thai ThinPrep validation + error analysis |
| Binary safety triage | Strong Phase 1 | sensitivity 1.0 held-out, 0.9867 +/- 0.0086 CV | Validate externally |
| HPV risk framing | Partial | morphology-risk wording and protocol | Add paired HPV DNA/RNA endpoint |
| Explainability | Partial | Grad-CAM available, error-analysis plan + engineering gallery written | Add pathologist-reviewed Grad-CAM failure gallery |
| Uncertainty | Partial | MC Dropout prototype, abstention policy written, high-uncertainty UI gate tightened | Tune threshold on validation/external data |
| Calibration | Improved Phase 1 | temperature scaling report: multiclass ECE 0.0669 -> 0.0387; binary ECE 0.0907 -> 0.0738 | Validate on external Thai ThinPrep |
| Patient report safety | Strong prototype | safety spec written; UI gate requires sign-off and blocks high uncertainty | Add server-side audit trail if moving beyond local demo |
| Thai data readiness | In progress | data protocol + template + intake checklist | Obtain IRB/MOU and collect pilot set |
| Reader study readiness | In progress | protocol written | Recruit readers and lock case set |
| Claim governance | Strong | claims ledger + audit script + legacy artifact audit | Run audit before publishing |
| Web demo | Strong prototype | React build works; HPV panel, model-card governance, local audit trail; Playwright runtime check console errors 0 | Keep visual QA after future UI edits |
| Regulatory posture | Early | risk register, model card | Add SaMD lifecycle docs if clinical pilot begins |
| External citation hygiene | In progress | WHO/CDC/FDA/CONSORT-AI/DECIDE-AI evidence review and citation ledger added | Pin primary Thai sources before publishing Thailand-specific numbers |
| Submission readiness | Strong draft | submission master, pitch scripts, poster content, demo runbook, Q&A bank | Convert into final deck/poster/PDF for the chosen competition |
| Audit governance | Demo only | localStorage audit + server-side audit roadmap | Implement server-side signed audit before any real pilot |

## Current Readiness Level

Recommended public framing:

> Phase 1 explainable screening co-pilot prototype with honest public-dataset
> evaluation and a defined validation path.

Not ready to claim:

> clinically validated diagnostic system.

## Highest-Impact Remaining Work

1. Add pathologist-reviewed Herlev/Thai error-case gallery with image-level notes.
2. Add Thai ThinPrep pilot data using the protocol/template.
3. Move audit trail from localStorage to a server-side signed audit log if the demo becomes a pilot.
4. Repeat browser visual/accessibility verification after future UI edits.
5. Regenerate legacy report/proposal artifacts from updated generators before public use.
6. Keep claim audit passing before every public package.
7. Attach primary Thai sources before using exact Thailand coverage,
   loss-to-follow-up, genotype, or regulatory numbers in final submissions.

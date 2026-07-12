# Risk Register

Last updated: 2026-07-06

## Summary

CerviCo-Pilot is credible as a Phase 1 screening-assist prototype, but it touches
medical decision-making. The strongest version of the project is explicit about
risk and routes unsafe uncertainty back to humans.

## Risk Table

| Risk | Severity | Current Mitigation | Next Action |
| --- | --- | --- | --- |
| Model misses abnormal/high-risk case | High | Binary safety layer sensitivity high on Herlev; clinician sign-off | Validate on Thai ThinPrep; tune abstention threshold |
| False positives overload clinicians | Medium | Specificity is reported honestly; over-referral is framed as screening trade-off | Add workload analysis and threshold options |
| HPV claim misunderstood as infection detection | High | Wording updated to HPV-related morphology risk | Keep disclaimer near every HPV output |
| Domain shift from Herlev to Thai ThinPrep | High | Limitation documented | Collect Thai retrospective set |
| KOIL output looks validated when it is not | High | KOIL recall/support disclosed | Disable/label KOIL as Phase 2 unless true KOIL data exists |
| Grad-CAM creates false trust | Medium | Described as explanation aid, not proof | Add "AI focused here; clinician must verify" language |
| Uncertainty not calibrated | Medium | MC Dropout used as prototype | Add temperature scaling/reliability study |
| Patient misunderstands report as diagnosis | High | Clinician sign-off and disclaimers | Gate patient report behind sign-off; plain Thai caution |
| Dataset leakage or polluted metrics recur | High | Canonical JSON and inspect script | Keep claim audit checklist; never use synthetic metrics as evidence |
| Privacy/PDPA risk for Thai data | High | No Thai patient data in Phase 1 | De-identification protocol + ethics approval before collection |

## Safety Requirements

Minimum requirements for any demo:

- show "decision-support only";
- show "not diagnosis";
- show "not HPV DNA/RNA test";
- show clinician sign-off requirement;
- show uncertainty/abstention if model is unsure;
- do not hide limitations.

Minimum requirements for any patient-facing report:

- must be generated only after clinician sign-off;
- must avoid saying "you have cancer";
- must avoid saying "you have HPV";
- must say what follow-up is recommended;
- must say who to contact next.

## Risk-Based UI Policy

For any result:

1. Display the 5-class Bethesda-style grade.
2. Display normal/abnormal safety triage.
3. Display HPV-related morphology risk as a note, not diagnosis.
4. Display Grad-CAM with explanation caveat.
5. Display uncertainty.
6. If uncertainty is high, hide confident wording and show "requires review."
7. Require clinician sign-off before export/send.

## Red Flags In Future Work

Stop and review if future generated text contains:

- "detects HPV";
- "diagnoses cancer";
- "ready for hospital use";
- "validated in Thailand";
- "99% accurate";
- "fully calibrated";
- "no false negatives" without saying "in held-out Herlev triage test."


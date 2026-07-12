# Siriraj x MIT Hacking Medicine 2026 Strategy

## Recommendation
Use **CerviCo-Pilot** for Siriraj x MIT Hacking Medicine, framed as an
**explainable cervical cytology screening workflow** for community hospitals.
The product output remains 5-class Bethesda grading; binary triage is the
safety layer used to prioritize abnormal/high-risk cases.

Do not pitch it as a finished diagnostic AI. The winning framing is:

> CerviCo-Pilot helps community-hospital staff grade cervical cytology images on
> the Bethesda scale, flag abnormal/high-risk cases early, show where the AI
> looked, require clinician sign-off, and produce a patient-friendly follow-up
> explanation to reduce loss-to-follow-up.

## Why This Fits Siriraj x MIT Better Than DuckCheck

Siriraj/MIT-style health hackathons reward a real clinical workflow, not only a
model. CerviCo-Pilot has the right ingredients:

- **Clinical problem depth**: cervical cancer screening, delayed follow-up,
  community hospitals, cytology/pathology bottlenecks.
- **Stakeholders are clear**: patient, cytotechnologist, pathologist,
  gynecologist, community hospital, referral center.
- **Workflow is demoable**: upload cytology field -> abnormal triage ->
  Grad-CAM -> uncertainty -> clinician sign-off -> patient report.
- **Harder to dismiss than a chatbot**: it is computer vision + clinical
  decision support, not a thin wrapper around ChatGPT/Gemini.
- **Honest evidence exists**: real Herlev test metrics, bootstrap CI, 5-fold CV,
  and clear limitations.

DuckCheck remains good for a medication-safety workflow, but it must constantly
defend "why not just use ChatGPT?" CerviCo-Pilot instead gets judged on the
right medical-AI questions: data, sensitivity, workflow, validation, and safety.

## Evidence To Lead With

Canonical metrics are in:

- `models/test_metrics.json`
- `models/triage_metrics.json`
- `models/cv_results.json`
- `docs/TRIAGE_RESULTS.md`
- `docs/CV_RESULTS.md`

Use these numbers:

| View | Metric | Value |
|---|---:|---:|
| Binary triage, held-out | Sensitivity | 1.0 |
| Binary triage, held-out | AUROC | 0.964 |
| Binary triage, held-out | Specificity | 0.7222 |
| Binary triage, held-out | Confusion | TP 101 / TN 26 / FP 10 / FN 0 |
| Binary triage, 5-fold CV | Sensitivity | 0.9867 +/- 0.0086 |
| Binary triage, 5-fold CV | AUROC | 0.9435 +/- 0.0448 |
| 5-class Bethesda, held-out | Accuracy | 0.6934 |
| 5-class Bethesda, held-out | HSIL recall | 0.8667 |
| 5-class Bethesda, held-out | SCC recall | 0.5909 |
| 5-class Bethesda, held-out | KOIL recall | 0.0 |

Interpretation:

- The model is **not** a final 5-class diagnostic device, but 5-class Bethesda
  output is still worth showing because it maps to real clinical follow-up
  categories.
- It is credible as a **screening-assist prototype**: it grades the image,
  explains where it looked, and uses a safety triage layer that catches abnormal
  cases aggressively while accepting some over-referral.
- FN=0 in the held-out binary triage test is the strongest result, but state it
  as Phase 1 evidence on a small public dataset, not a clinical guarantee.

## Demo Flow For Judges

1. **Problem**: community hospitals need faster abnormal-case triage and clearer
   patient follow-up.
2. **Upload or select a real Herlev sample**.
3. **Show triage result first**: normal vs abnormal, not only 5-class label.
4. **Show Grad-CAM**: "where the AI focused."
5. **Show uncertainty/abstain**: if confidence is weak, the system asks for
   clinician review instead of forcing a result.
6. **Show physician sign-off**: confirmed / edited / rejected slide.
7. **Show patient report**: simple Thai explanation after clinician sign-off.
8. **Close with Phase 2**: Thai data, reader study, calibration, and integration
   into cytology worklists.

## Claims To Avoid

Do not say:

- "AI diagnoses cervical cancer."
- "Ready for real clinical deployment."
- "Well-calibrated."
- "Detects HPV DNA."
- "KOIL detection works."
- "Validated on Thai patients."
- "Contours/SAM/z-stack/WSI are real validated features."

Say instead:

- "AI-assisted pre-screening / triage."
- "Doctor-in-the-loop decision support."
- "Real Herlev Phase 1 evidence; Thai validation is Phase 2."
- "KOIL is a known limitation because Herlev has no KOIL samples."
- "Interactive contours, SAM-like editing, z-stack and WSI are prototype stubs
  demonstrating the intended future workflow."

## Likely Judge Questions And Answers

**Q: Accuracy is only around 69%. Why is this useful?**

A: We are not positioning the Phase 1 model as a final 5-class diagnostic
system. The clinically useful first step is triage: normal vs abnormal. In that
view, the held-out test has sensitivity 1.0 and AUROC 0.964, with FN=0/101. The
trade-off is moderate specificity, meaning over-referral, which is acceptable
for a screening-assist prototype because missing abnormal cases is worse.

**Q: Is this clinically validated?**

A: No. It is a Phase 1 prototype trained and evaluated on a public Herlev
dataset. Clinical validation requires Thai data, IRB/MOU, reader study, external
validation, and calibration. The current system demonstrates workflow and
technical feasibility, not regulatory readiness.

**Q: Why not just use existing Hologic/BD systems?**

A: Those systems are strong but expensive and designed for well-resourced
settings. Our angle is a low-cost, explainable, doctor-in-the-loop workflow for
community hospitals and LMIC contexts, with plain-language patient follow-up.

**Q: Why does KOIL fail?**

A: Herlev has no KOIL samples, so KOIL recall is 0.0 by design in Phase 1. We
keep it visible as a limitation and Phase 2 target using SIPaKMeD/RepoMedUNM or
Thai annotated data.

**Q: What is the safest next step?**

A: Add Thai retrospective cytology images under IRB, compute calibration/ECE,
run reader study with cytotechnologists/pathologists, and evaluate whether
triage reduces time-to-follow-up without increasing unsafe automation bias.

## Immediate Work Before Submission

- Sync all visible numbers with JSON metrics.
- Add ROC/reliability evidence to the performance page.
- Hide or label prototype-only features in the live demo.
- Prepare a 3-minute Siriraj flow: problem -> triage demo -> physician sign-off
  -> patient follow-up -> validation roadmap.
- Prepare a one-page model card handout.

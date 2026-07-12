# Judge Q&A Bank

Last updated: 2026-07-07

Purpose: prepare safe, precise answers for judges across Samsung Solve for
Tomorrow, WSEEC, and medical/AI review settings.

## Core Answer Rules

- Say "screening support" or "triage assistant", not diagnosis.
- Say "HPV-related morphology risk", not HPV infection detection.
- Say current evidence is Herlev public data only, not Thai clinical validation.
- Explain 5-class output as product identity and binary triage as safety layer.
- Do not hide weaknesses: KOIL is not validated; 5-class performance is
  moderate; reader study is not done.

## Short Opening Answer

> CerviCo-Pilot is a clinician-in-the-loop cervical cytology screening co-pilot.
> It reads Pap/ThinPrep-style cytology images, gives a Bethesda-style 5-class
> grade, shows Grad-CAM, flags uncertainty, and blocks patient-facing reports
> until a clinician confirms the result. It does not diagnose cancer or detect
> HPV infection directly.

## Q1. Why not just use ChatGPT, Claude, or Gemini?

Because this is not a text question-answering task. The hard part is controlled
image triage with a fixed medical output schema, reproducible evaluation, and
safety gates.

Safe answer:

> General LLMs can help explain a confirmed result in plain language, but they
> are not the cytology classifier. CerviCo-Pilot has a defined image input,
> fixed Bethesda-style output classes, Herlev evaluation metrics, Grad-CAM,
> uncertainty gating, clinician sign-off, and local audit trail. That is a
> governed screening workflow, not a chat response.

If judges point to the `/ask` page:

> The `/ask` page is only a bounded project Q&A assistant for explaining the
> prototype. It is not the medical classifier and not patient-specific medical
> advice.

## Q2. Why not just use HPV DNA testing?

HPV DNA/RNA testing is the molecular test for infection status. CerviCo-Pilot
does not replace it.

Safe answer:

> HPV testing answers whether high-risk HPV is present. Cytology answers whether
> cells already look abnormal. CerviCo-Pilot supports the cytology side when
> Pap/ThinPrep images exist: it grades abnormal cells, explains the visual
> region, flags uncertainty, and routes cases for clinician follow-up. Paired
> HPV DNA/RNA labels are a future validation endpoint, not a current claim.

## Q3. How can an image assess HPV risk?

Safe answer:

> It cannot detect the virus directly. The system estimates HPV-related
> morphology risk from visible cytologic patterns, such as low-grade changes or
> possible koilocytic morphology. The report states clearly that confirmatory
> HPV testing is separate.

## Q4. Why keep 5 classes if the binary triage metric is stronger?

Safe answer:

> Binary triage is the safety layer. The product identity is the 5-class
> Bethesda-style output because cytology workflows need more detail than
> normal/abnormal. We are honest that 5-class performance is moderate in Phase 1,
> while binary sensitivity is strong on Herlev. That is why the UI shows both:
> clinical detail plus safety triage.

## Q5. Is it clinically validated?

No.

Safe answer:

> It is a Phase 1 retrospective public-dataset prototype. It has real Herlev
> image evidence, held-out evaluation, cross-validation, Grad-CAM, uncertainty,
> and calibration work. It still needs Thai ThinPrep validation, paired HPV
> endpoint testing, reader study, and prospective workflow evaluation before
> clinical utility can be claimed.

## Q6. What happens if the model is uncertain?

Safe answer:

> The system abstains operationally: high uncertainty blocks the patient-facing
> report and routes the case back to clinician review. The clinician can confirm,
> edit, or reject the case. This is why the workflow is safer than a raw
> classifier.

## Q7. What if Grad-CAM highlights the wrong region?

Safe answer:

> Grad-CAM is an explanation aid, not proof of causal reasoning. If the heatmap
> looks suspicious, the clinician should challenge the AI and rely on expert
> review. The project includes an error-case gallery to expose failures instead
> of hiding them.

## Q8. KOIL recall is 0. Why mention HPV?

Safe answer:

> KOIL is not a validated current capability because Herlev does not provide
> true KOIL training examples. HPV remains in the project title because the
> clinical pathway is HPV-driven, and because future Thai ThinPrep data should
> include paired HPV DNA/RNA results and koilocytosis annotations. Current
> wording is limited to HPV-related morphology risk.

## Q9. What is the biggest weakness?

Safe answer:

> External validation. The model has honest Phase 1 evidence on Herlev, but it
> is not yet validated on Thai ThinPrep images, Thai staining/scanner variation,
> or paired HPV results. That is the main next step, and the data protocol is
> already written.

## Q10. What makes this socially useful?

Safe answer:

> Cervical cancer is highly preventable when screening and follow-up work. The
> project targets the workflow gap after a cytology image exists: faster
> preliminary triage, clearer explanation for clinicians, safer uncertainty
> handling, and patient-friendly reporting after sign-off.

## Q11. What makes this scientifically honest?

Safe answer:

> We report both strengths and weaknesses: strong binary triage sensitivity on
> Herlev, moderate 5-class performance, SCC recall still imperfect, KOIL not
> learned, no Thai validation, and no clinical-use claim. The web demo includes
> wrong predictions and uncertainty cases.

## Q12. What would make it ready for pilot?

Minimum next steps:

1. IRB/MOU and de-identified Thai ThinPrep/LBC dataset.
2. Locked Thai test set before tuning.
3. Paired HPV DNA/RNA endpoint where available.
4. Reader study with and without AI.
5. Server-side signed audit log.
6. Prospective workflow study only after ethics approval.

## One-Sentence Closing

> CerviCo-Pilot is not trying to replace clinicians; it is trying to make
> abnormal cervical cytology easier to catch, explain, and follow up safely.

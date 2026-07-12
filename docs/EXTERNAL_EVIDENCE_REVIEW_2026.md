# External Evidence Review 2026

Last updated: 2026-07-06

Purpose: give CerviCo-Pilot a source-backed public-health, clinical-workflow,
and medical-AI governance foundation. This file is not a metric source for the
model. Model performance still comes from `models/*.json`.

## Executive Takeaway

CerviCo-Pilot is strongest when framed as a **clinician-in-the-loop cervical
cytology triage assistant**:

- cervical cancer is largely preventable when HPV vaccination, screening, and
  treatment/follow-up work together;
- cytology and HPV testing answer related but different questions;
- an image model can support visible cytologic abnormality grading and
  HPV-related morphology risk, but it cannot replace molecular HPV testing;
- medical AI needs explicit intended use, input/output handling, human-AI
  interaction design, error analysis, calibration, and lifecycle governance.

This supports the current product hierarchy:

1. 5-class Bethesda-style cytology grade = primary product output.
2. Binary normal/abnormal triage = high-sensitivity safety layer.
3. HPV-related morphology risk = visual risk signal, not infection detection.
4. Grad-CAM + uncertainty = review aids, not proof of diagnosis.
5. Clinician sign-off = mandatory governance layer.

## 1. Public-Health Case

### What the external evidence says

WHO states that cervical cancer is largely preventable through HPV vaccination
and screening, and that it is curable if detected early and managed effectively.
WHO's July 2026 fact sheet reports 604,000 new cases and 280,000 deaths in
2024, and links almost all cases to oncogenic HPV infection. WHO's elimination
strategy uses the 90-70-90 targets: 90% vaccination, 70% screening, and 90%
treatment/management.

Source:
https://www.who.int/news-room/fact-sheets/detail/cervical-cancer

### Implication for CerviCo-Pilot

The project should not pitch "AI beats doctors." The stronger public-health
argument is:

> CerviCo-Pilot supports the screen-and-triage part of cervical cancer
> prevention by making abnormal cytology easier to notice, explain, and route to
> human follow-up.

Safe claims:

- "supports cervical cytology screening workflows";
- "aims to reduce missed or delayed follow-up after abnormal cytology";
- "aligns with prevention and early-detection goals."

Unsafe claims:

- "eliminates cervical cancer by itself";
- "guarantees no deaths";
- "replaces national HPV screening."

## 2. Pap/ThinPrep Cytology vs HPV Testing

### What the external evidence says

CDC separates the two screening tests clearly:

- the HPV test looks for the virus that can cause cell changes on the cervix;
- the Pap test looks for precancers or cell changes that may become cervical
  cancer if not treated appropriately;
- if an HPV test is performed, cells are tested for HPV; if a Pap test is
  performed, cells are checked to see whether they look normal.

CDC also notes that abnormal Pap results usually do not mean cancer, that many
abnormal changes are likely caused by HPV, and that serious changes can become
cancer if not removed.

Sources:
https://www.cdc.gov/cervical-cancer/screening/index.html
https://www.cdc.gov/cervical-cancer/about/index.html

### Implication for CerviCo-Pilot

This is the central answer to judges who ask "Why not just use an HPV test?" or
"How can an image detect HPV?"

Correct answer:

> HPV DNA/RNA testing is the molecular test for infection status. CerviCo-Pilot
> does not replace it. CerviCo-Pilot reads visible cell morphology from
> Pap/ThinPrep-style cytology images, grades cell abnormality, and flags
> morphology that may be HPV-related. It turns image interpretation and follow-up
> routing into a faster, explainable workflow.

This makes the title defensible:

> "HPV risk assessment from ThinPrep images" means HPV-related morphology risk,
> not direct viral detection.

## 3. Human-AI Clinical Evaluation

### What the external evidence says

CONSORT-AI states that AI interventions need rigorous prospective evaluation to
demonstrate health-outcome impact. It recommends clear reporting of the AI
intervention, required user instructions or skills, setting, handling of input
and output data, human-AI interaction, and analysis of error cases.

DECIDE-AI addresses early-stage clinical evaluation of AI decision-support
systems. It notes that many systems show promising in-silico performance but
few have demonstrated real benefit to patient care, and that early small-scale
clinical evaluation should assess actual clinical performance, safety, and
human factors before large trials.

Sources:
https://www.nature.com/articles/s41591-020-1034-x
https://www.nature.com/articles/s41591-022-01772-9

### Implication for CerviCo-Pilot

The project is currently Phase 1 retrospective/public-dataset evidence. That is
acceptable for a student research prototype if stated honestly.

Source-backed next steps:

- locked Thai ThinPrep/LBC retrospective validation;
- paired HPV DNA/RNA endpoint study when labels exist;
- reader study with and without AI;
- error-case analysis, including cases where Grad-CAM may mislead;
- prospective workflow pilot only after ethics and clinical governance review.

These map directly to:

- `docs/VALIDATION_ROADMAP.md`
- `docs/READER_STUDY_PROTOCOL.md`
- `docs/ERROR_ANALYSIS_PLAN.md`
- `docs/THAI_THINPREP_DATA_PROTOCOL.md`

## 4. Medical-AI Lifecycle Governance

### What the external evidence says

FDA describes AI/ML medical devices as having unique considerations because of
complexity and iterative, data-driven development. FDA/IMDRF Good Machine
Learning Practice guidance is intended to promote safe, effective, and
high-quality AI/ML medical devices and emphasizes a total product lifecycle
perspective.

Source:
https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles

### Implication for CerviCo-Pilot

Even as a prototype, CerviCo-Pilot should behave like a responsible medical-AI
project:

- intended use is narrow and explicit;
- data provenance and domain limits are visible;
- metrics come from canonical JSON, not hand-written memory;
- uncertainty can abstain;
- clinician sign-off is required;
- audit trail exists for demo actions;
- claim audit runs before public release;
- Thai clinical validation is listed as missing, not implied.

These map directly to:

- `docs/CLAIMS_LEDGER.md`
- `docs/DATASET_MODEL_CARD.md`
- `docs/RISK_REGISTER.md`
- `docs/UNCERTAINTY_AND_ABSTENTION_POLICY.md`
- `docs/PATIENT_REPORT_SAFETY_SPEC.md`
- `docs/BROWSER_ACCESSIBILITY_VERIFICATION.md`

## 5. Thailand-Specific Claims

Some existing legacy drafts mention Thailand-specific values such as screening
coverage decline and loss-to-follow-up percentages. These are important for the
story, but they must be treated as **competition-narrative claims requiring
source verification** unless a primary source is attached in the final package.

Current safe policy:

- use WHO/CDC/FDA/CONSORT-AI/DECIDE-AI as verified external foundation;
- keep Thailand-specific numerical claims in the claims ledger until primary
  Thai sources are pinned;
- if a pitch needs the 77.5% -> 53.9% or 41% figures, attach the exact Thai
  source, year, population, and definition before publishing.

Safe wording until verified:

> Thailand still needs faster, more reliable follow-up pathways for abnormal
> cervical screening results; CerviCo-Pilot targets this follow-up gap as a
> workflow prototype.

## 6. Judge-Facing Answers

### Why not ChatGPT, Claude, or Gemini?

General LLMs are not trained, validated, or governed as cervical cytology image
triage devices. CerviCo-Pilot is not a chat answer generator. It has a defined
image input, a fixed output schema, Herlev evaluation metrics, Grad-CAM,
uncertainty/abstention behavior, and clinician sign-off. LLMs may help draft
patient-friendly explanations after clinician approval; they are not the
classifier or clinical evidence.

### Why not just HPV DNA testing?

HPV testing is excellent for detecting high-risk HPV infection. CerviCo-Pilot
does not replace it. The system addresses the cytology side: when images exist,
it helps grade abnormal cells, show visual evidence, flag uncertainty, and route
the case for human follow-up. With paired HPV data later, HPV status becomes an
evaluation endpoint, not an unproven claim.

### Why keep 5 classes if binary sensitivity is the strongest metric?

Binary triage is the safety layer. The 5-class output is the product identity
because cytology workflows need more structure than yes/no. The honest message
is that Phase 1 binary triage is strong on Herlev, while 5-class grading is
moderate and needs Thai ThinPrep validation.

## 7. Submission Use

Use this evidence order in public materials:

1. WHO: cervical cancer is preventable; screening/follow-up matters.
2. CDC: Pap/ThinPrep cytology and HPV testing are distinct but connected.
3. Project evidence: real Herlev model metrics from JSON.
4. CONSORT-AI/DECIDE-AI: reader study and clinical evaluation are required next.
5. FDA/GMLP: lifecycle governance, limitations, monitoring, and claim control.

Do not use this file to invent new model performance claims.

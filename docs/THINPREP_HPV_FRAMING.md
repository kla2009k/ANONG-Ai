# ThinPrep + HPV Risk Assessment Framing

## Core Title

**Thai**

การพัฒนาระบบปัญญาประดิษฐ์เพื่อคัดกรองความผิดปกติของเซลล์ปากมดลูก
และการประเมินความเสี่ยงเชื้อ HPV จากภาพถ่าย ThinPrep

**English**

Development of an AI System for Cervical Cell Abnormality Screening and HPV
Risk Assessment from ThinPrep Images

## The Exact Claim

The project can safely claim:

> CerviCo-Pilot screens cervical cytology images, grades abnormality on a
> Bethesda-style scale, and provides an HPV-related morphology risk assessment
> from visible cell changes.

The project must not claim:

> CerviCo-Pilot detects HPV infection.

Reason: a cytology image can show cell changes associated with HPV, such as
koilocytic atypia and low-grade squamous changes, but true HPV infection status
requires molecular HPV DNA/RNA testing or validated clinical testing. The AI is
therefore a visual risk-assessment layer, not a virus test.

External source backing:

- CDC cervical screening guidance separates HPV tests, which look for the virus,
  from Pap tests, which look for precancers or cervical cell changes.
- WHO frames persistent oncogenic HPV infection as the causal pathway behind
  most cervical cancers, which explains why HPV belongs in the clinical story.

See:

- `docs/EXTERNAL_EVIDENCE_REVIEW_2026.md`
- `docs/SOURCE_CITATION_LEDGER.md`

## Why ThinPrep Matters

ThinPrep is a liquid-based cytology workflow. Instead of smearing cells directly
onto a slide, cervical cells are preserved in liquid and processed into a thin,
more standardized cell layer for microscopic reading. That matters for an AI
project because:

- cells are more consistently prepared than many conventional smears;
- the image is closer to what automated slide reading systems use;
- the workflow fits hospital laboratories that already process cervical
  cytology;
- the same clinical pathway can support Pap cytology, HPV testing, and follow-up
  triage.

For the competition story, say:

> We focus on ThinPrep-style cytology because it is a realistic laboratory
> workflow for cervical screening and gives AI a clearer, more standardized
> image input than an uncontrolled phone photo.

## Why HPV Belongs In The Story

HPV is central because persistent high-risk HPV infection causes the large
majority of cervical cancers. Screening systems therefore need to answer two
different but connected questions:

1. **Are the cervical cells already abnormal?**
   This is the Pap/ThinPrep cytology question.
2. **Do the visual changes suggest HPV-related risk?**
   This is the morphology-based risk question.

CerviCo-Pilot is strongest when it combines them:

- **Bethesda 5-class output**: the core cell abnormality grade.
- **HPV morphology risk note**: a visual explanation that HPV-related changes may
  be suspected, especially in LSIL/koilocytic patterns.
- **Binary safety triage**: normal vs abnormal for high-sensitivity screening.
- **Grad-CAM**: where the model looked.
- **Uncertainty flag**: when not to trust the model alone.
- **Clinician sign-off**: no automatic diagnosis or patient release.

## 5-Class Strategy

Keep the 5-class design. It makes the project more clinically meaningful than a
plain "normal/abnormal" classifier.

Recommended product interpretation:

| Layer | Purpose | Competition Message |
| --- | --- | --- |
| 5-class Bethesda-style grade | Clinical detail | "The AI gives a structured cytology grade, not just a yes/no answer." |
| HPV morphology risk | Patient pathway | "The system explains whether visible cell changes may be HPV-related." |
| Binary triage | Safety | "For screening, we optimize not missing abnormal/high-risk cases." |
| Grad-CAM + uncertainty | Trust | "Doctors can challenge the AI, and uncertain cases return to humans." |

## How To Explain HPV Risk To Judges

Use this answer if asked "How can an image detect HPV?"

> It does not directly detect the virus. HPV DNA/RNA testing is molecular. What
> our system does is estimate HPV-related visual risk from cytology morphology.
> HPV can cause characteristic cell changes, especially koilocytic atypia and
> low-grade squamous lesions. CerviCo-Pilot uses those visible patterns as a
> risk signal, then clearly states that confirmatory HPV testing or clinician
> review is still required.

If asked "So why include HPV in the title?"

> Because cervical screening is not only about naming a cell class; it is about
> deciding who needs follow-up. HPV is the causal pathway behind most cervical
> cancers, and ThinPrep cytology often sits beside HPV testing in screening
> workflows. Our contribution is an image-based HPV risk assessment layer, not a
> replacement for lab HPV testing.

## Strong Thai Pitch Paragraph

โครงงานนี้ไม่ได้อ้างว่า AI ตรวจพบเชื้อ HPV โดยตรง เพราะการตรวจเชื้อ HPV ต้องใช้
การตรวจระดับโมเลกุล เช่น HPV DNA/RNA test แต่ภาพ ThinPrep สามารถแสดงความผิดปกติ
ของเซลล์ที่สัมพันธ์กับการติดเชื้อ HPV ได้ เช่น ลักษณะ koilocytosis หรือกลุ่ม
ความผิดปกติระดับ LSIL ดังนั้น CerviCo-Pilot จึงทำหน้าที่เป็นระบบคัดกรองจากภาพ
เซลล์วิทยา ให้ระดับความผิดปกติตาม Bethesda scale พร้อมประเมินความเสี่ยงที่อาจ
สัมพันธ์กับ HPV จาก morphology ของเซลล์ และส่งต่อให้แพทย์ยืนยันก่อนออกผลเสมอ

## Strong English Pitch Paragraph

CerviCo-Pilot does not claim to detect HPV infection directly. HPV confirmation
requires molecular testing, such as HPV DNA or RNA assays. Instead, the system
performs image-based HPV risk assessment by analyzing cytologic morphology:
Bethesda-grade abnormalities, possible koilocytic patterns, model uncertainty,
and the regions highlighted by Grad-CAM. This makes HPV risk visible and
actionable without pretending that an image classifier can replace laboratory
HPV testing.

## Evidence Order For Submission

Use metrics in this order:

1. Product output: 5-class Bethesda-style screening.
2. Safety layer: 5-fold binary sensitivity **0.987 +/- 0.009**.
3. Held-out discrimination: binary AUROC **0.964**.
4. Held-out safety: high-risk catch **1.0**, TP 101 / TN 26 / FP 10 / FN 0.
5. Honest 5-class performance: accuracy **0.6934**, QWK **0.687 held-out**,
   **0.698 +/- 0.087 CV**.
6. Limitation: KOIL is a Phase 2 class because the current Herlev training set
   does not contain true KOIL examples.

## Phase 2 Data Plan

To make the ThinPrep + HPV claim stronger, the next dataset should include:

- de-identified ThinPrep or liquid-based cytology fields;
- Bethesda labels from cytotechnologist/pathologist review;
- HPV DNA/RNA result if available;
- koilocytosis / HPV-effect annotation where possible;
- slide quality score;
- Thai hospital domain labels, because staining and imaging can shift across
  laboratories.

This turns HPV risk from a morphology explanation into a measurable endpoint:

- cytology abnormality prediction;
- HPV-positive risk prediction;
- high-risk lesion triage;
- uncertainty-triggered referral.

Until that paired endpoint exists, do not write "HPV-positive prediction" as a
validated current capability. Write "planned HPV-positive endpoint study" or
"HPV-related morphology risk."

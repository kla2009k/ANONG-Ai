# Samsung Solve for Tomorrow 2026 + WSEEC Strategy

## Recommended Competition Framing

Use CerviCo-Pilot as:

> **Development of an AI System for Cervical Cell Abnormality Screening and
> HPV Risk Assessment from ThinPrep Images**

Thai:

> **การพัฒนาระบบปัญญาประดิษฐ์เพื่อคัดกรองความผิดปกติของเซลล์ปากมดลูก
> และการประเมินความเสี่ยงเชื้อ HPV จากภาพถ่าย ThinPrep**

Shorter stage title:

> **An Explainable Deep Learning System for Cervical Cytology Screening with
> Uncertainty-Aware, Clinician-in-the-Loop Triage**

Thai:

> **ระบบปัญญาประดิษฐ์แบบอธิบายได้สำหรับคัดกรองเซลล์ปากมดลูก พร้อมการประเมินความไม่แน่นอนและการยืนยันโดยแพทย์**

This framing keeps the **5-class Bethesda output** as the core product, while
using binary triage sensitivity as the safety argument. For HPV, use the phrase
**HPV risk assessment from cytologic morphology**, not "HPV detection." The
system estimates visual risk patterns associated with HPV-related cell change;
it does not test viral DNA/RNA.

## Why 5-Class Is Worth Keeping

For Samsung Solve for Tomorrow and WSEEC, the goal is not only "catch abnormal
or not." Judges want to see a meaningful innovation with a clear social problem,
a working prototype, and enough technical depth to be credible.

The 5-class Bethesda scale gives the project that depth:

- **NILM**: likely normal, routine screening
- **LSIL**: low-grade abnormality, follow-up / HPV testing
- **HSIL**: high-grade abnormality, urgent colposcopy pathway
- **SCC**: suspected cancer, urgent referral
- **KOIL**: Phase 2 target; not learned in Phase 1 because Herlev has no KOIL samples

Binary triage is still important, but it should be described as the **safety
layer**:

> The system grades the image on the Bethesda scale, then also collapses the
> result into a normal-vs-abnormal triage decision so high-risk cases are not
> missed.

## Best One-Liner

Almost no one should die of cervical cancer when abnormal cells are caught early.
CerviCo-Pilot helps community hospitals screen ThinPrep/Pap cytology images,
grade cervical cell abnormality on the Bethesda scale, estimate HPV-related
visual risk, highlight the regions the AI examined, flag uncertainty, and
require clinician sign-off before a patient report is released.

## Strong English Abstract / Form Text

Almost no one should die of cervical cancer. Caught early on a Pap or ThinPrep
slide, abnormal cells are nearly always stopped in time. Yet Thailand is moving
in the wrong direction: screening coverage has fallen from 77.5% to 53.9%, and
roughly 41% of women with abnormal results never return for care.

CerviCo-Pilot was built to close that follow-up gap. A user uploads a ThinPrep
or Pap cytology image; the system grades cervical cell abnormality on the
Bethesda scale, estimates HPV-related visual risk from cytologic morphology,
overlays a Grad-CAM heatmap over the regions it examined, and estimates
uncertainty with Monte Carlo Dropout. When the model is unsure, it hands the
case back to a clinician instead of forcing a prediction. It supports the
clinician; it never pretends to be one.

We trained EfficientNet-B0 on 917 real Herlev images and evaluated it using
held-out testing, bootstrap confidence intervals, and 5-fold cross-validation.
Binary screening sensitivity reached 0.987 +/- 0.009 across 5 folds, and
held-out binary AUROC reached 0.964 with no high-risk case missed in the
held-out triage test. The system runs offline, making it suitable for low-resource
screening workflows.

## Thai Abstract / Form Text

มะเร็งปากมดลูกเป็นโรคที่ป้องกันการเสียชีวิตได้มาก หากตรวจพบความผิดปกติของเซลล์ตั้งแต่ระยะเริ่มต้นจากภาพ Pap smear หรือ ThinPrep แต่ประเทศไทยกำลังเผชิญปัญหาสำคัญสองด้าน คืออัตราการเข้ารับการคัดกรองลดลงจาก 77.5% เหลือ 53.9% และผู้หญิงที่ได้รับผลผิดปกติประมาณ 41% ไม่กลับมาติดตามผลต่อ

CerviCo-Pilot ถูกออกแบบมาเพื่อช่วยลดช่องว่างหลังการคัดกรอง ระบบรับภาพ ThinPrep หรือ Pap cytology แล้วจำแนกระดับความผิดปกติของเซลล์ตาม Bethesda scale พร้อมประเมินความเสี่ยงที่สัมพันธ์กับ HPV จากลักษณะทางเซลล์วิทยา ไม่ใช่การตรวจหาเชื้อ HPV DNA/RNA โดยตรง ระบบแสดง Grad-CAM heatmap เพื่อบอกว่าปัญญาประดิษฐ์พิจารณาบริเวณใดของภาพ เมื่อโมเดลไม่มั่นใจ ระบบจะ flag ให้แพทย์ตรวจทานแทนการปล่อยผลอัตโนมัติ และรายงานสำหรับผู้ป่วยจะออกได้หลังการยืนยันโดยบุคลากรทางการแพทย์เท่านั้น

เราใช้ EfficientNet-B0 ฝึกบนภาพจริงจากชุดข้อมูล Herlev จำนวน 917 ภาพ และประเมินด้วย held-out test, bootstrap confidence intervals และ 5-fold cross-validation ผลการคัดกรองแบบปกติ/ผิดปกติให้ sensitivity เฉลี่ย 0.987 +/- 0.009 และ AUROC 0.964 บน held-out test โดยไม่พลาดเคสเสี่ยงสูงในการทดสอบ triage ระบบสามารถทำงานแบบ offline จึงเหมาะกับการสาธิต workflow สำหรับโรงพยาบาลชุมชนหรือพื้นที่ทรัพยากรจำกัด

## Samsung Solve for Tomorrow Angle

Samsung SFT rewards social problem solving, design thinking, AI, feasibility,
and youth-led impact. Lead with the human story:

1. **Empathize**: women receive abnormal results but do not understand, cannot
   travel, or never return for follow-up.
2. **Define**: the gap is not only detecting abnormal cells; it is turning an
   abnormal screening result into a clear, trusted next step.
3. **Ideate**: combine AI cytology screening, Bethesda grading, HPV morphology
   risk assessment, explainability, uncertainty, and a patient-friendly report.
4. **Prototype**: offline web app with ThinPrep/Pap upload, Bethesda grading,
   HPV risk explanation, Grad-CAM, uncertainty flag, clinician sign-off, and
   patient report.
5. **Test / next step**: Thai retrospective data, reader study, calibration, and
   hospital partner validation.

What to emphasize:

- Offline-first: usable in school demos, clinics, and low-resource settings.
- Human-in-the-loop: AI cannot release patient report without clinician sign-off.
- Plain-language report: the intervention targets loss-to-follow-up, not only
  model accuracy.
- Responsible AI: uncertainty/abstain, model card, limitations, no diagnosis claim.

## WSEEC Angle

WSEEC is closer to a science/engineering presentation. Lead with scientific
method and evidence:

- Problem: cervical cancer screening and follow-up gap.
- Method: EfficientNet-B0 transfer learning, real Herlev dataset, 5-class
  Bethesda mapping, ThinPrep/Pap workflow, Grad-CAM, MC Dropout uncertainty,
  and HPV-related morphology risk explanation.
- Evaluation: held-out test, bootstrap CI, 5-fold CV, confusion matrix, ROC,
  reliability/ECE.
- Results: 5-class performance is moderate; screening triage performance is
  strong.
- Engineering: offline React/FastAPI demo, model card, clinician sign-off,
  report export.
- Limitations: no Thai data yet, no clinical validation, KOIL not learned,
  external validation required.

The scientific honesty is a strength. Do not hide the 5-class accuracy. Explain
why it is acceptable for Phase 1:

> The five-class model is not yet a final diagnosis model. It is an early
> Bethesda grading assistant. For safety, the system also collapses predictions
> into a triage layer, where sensitivity is prioritized over specificity.

## Recommended Headline Metrics

Use this order:

1. 5-fold binary screening sensitivity: **0.987 +/- 0.009**
2. Held-out binary AUROC: **0.964**
3. Held-out high-risk catch: **1.0**
4. Held-out binary confusion: **TP 101 / TN 26 / FP 10 / FN 0**
5. 5-class accuracy: **0.6934**
6. QWK: **0.687 held-out**, **0.698 +/- 0.087 CV**
7. HSIL recall: **0.8667**
8. SCC recall: **0.5909**

How to say it:

> Five-class grading is still imperfect, especially SCC and KOIL. But the safety
> layer catches abnormal/high-risk cases aggressively, which is exactly the
> correct trade-off for a screening-assist system.

## Claims To Avoid

- "AI diagnoses cervical cancer."
- "Ready for clinical use."
- "Validated in Thailand."
- "KOIL detection works."
- "Detects HPV infection."
- "Replaces an HPV DNA/RNA test."
- "No one will die because of this system."
- "The model is fully calibrated."

Safer wording:

- "screening assistance"
- "Bethesda grading support"
- "HPV-related morphology risk assessment"
- "clinician-in-the-loop"
- "offline prototype"
- "Phase 1 evidence on public real images"
- "Thai data and reader study are the next validation step"

## 3-Minute Pitch Skeleton

1. **Opening**: Almost no one should die of cervical cancer if abnormal cells
   are found early.
2. **Thailand gap**: coverage is down, and abnormal-result follow-up is weak.
3. **Solution**: upload ThinPrep/Pap cytology image -> Bethesda grade -> HPV
   morphology risk note -> Grad-CAM -> uncertainty -> clinician sign-off ->
   patient report.
4. **Demo**: show one abnormal case and one uncertain/sign-off flow.
5. **Evidence**: real Herlev data, held-out + bootstrap + 5-fold CV; high
   sensitivity/AUROC for screening.
6. **Responsible AI**: not diagnosis, no auto-release, offline, model card,
   limitations visible.
7. **Next step**: Thai retrospective dataset + reader study + calibration.

## Best Positioning Sentence

CerviCo-Pilot is not trying to replace cytologists. It is trying to make sure
abnormal slides are noticed, explained, and followed up before a preventable
cancer becomes a late diagnosis.

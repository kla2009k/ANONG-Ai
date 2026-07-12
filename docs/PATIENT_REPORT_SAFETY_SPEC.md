# Patient Report Safety Spec

Last updated: 2026-07-06

## Purpose

The patient report is one of the strongest social-impact parts of CerviCo-Pilot,
but it is also a safety risk. A patient-facing report must reduce confusion and
loss-to-follow-up without implying that AI has made a final diagnosis.

## Release Rule

No patient-facing report may be exported, sent, printed, or copied until:

1. clinician reviews image/result;
2. clinician accepts, edits, or rejects AI suggestion;
3. clinician writes or confirms next-step recommendation;
4. clinician signs off.

## Report Layers

### Clinical layer

Audience: clinician/cytotechnologist/pathologist.

Can include:

- Bethesda-style class probabilities;
- binary triage;
- HPV-related morphology risk note;
- uncertainty metrics;
- Grad-CAM heatmap;
- quality flags;
- limitations;
- clinician override controls.

### Patient layer

Audience: patient.

Should include:

- plain Thai explanation;
- whether follow-up is needed;
- what the next step is;
- where/when to contact care team;
- clear note that this is not a final diagnosis.

Should not include:

- raw probability table without explanation;
- "you have cancer";
- "you have HPV";
- "AI is certain";
- "no risk";
- alarming wording without clinician context.

## Safe Patient Language

### NILM / likely normal

> จากการตรวจคัดกรองเบื้องต้น ยังไม่พบสัญญาณความผิดปกติที่เด่นชัดจากภาพนี้ กรุณาตรวจตามรอบที่แพทย์แนะนำ ผลนี้ไม่ใช่การวินิจฉัยขั้นสุดท้าย

### LSIL / low-grade abnormality

> ภาพนี้มีลักษณะบางอย่างที่อาจเป็นความผิดปกติระดับต่ำ แพทย์อาจแนะนำให้ติดตามผลหรือตรวจเพิ่มเติม เช่น HPV test ตามความเหมาะสม

### HSIL / high-grade abnormality

> ภาพนี้มีลักษณะที่ควรได้รับการตรวจยืนยันเพิ่มเติมโดยเร็ว แพทย์อาจแนะนำการตรวจเพิ่มเติม เช่น colposcopy หรือการส่งต่อผู้เชี่ยวชาญ

### SCC / urgent referral

> ภาพนี้มีลักษณะที่ต้องให้ผู้เชี่ยวชาญตรวจยืนยันอย่างเร่งด่วน กรุณาติดต่อสถานพยาบาลตามคำแนะนำของแพทย์

### HPV morphology risk note

> ระบบพบลักษณะทางเซลล์วิทยาที่อาจสัมพันธ์กับ HPV แต่ไม่ได้ตรวจหาเชื้อ HPV โดยตรง การยืนยันต้องใช้การตรวจทางห้องปฏิบัติการตามแพทย์เห็นสมควร

### High uncertainty

> ระบบไม่มั่นใจพอที่จะสรุปผลจากภาพนี้ ต้องให้แพทย์หรือผู้เชี่ยวชาญตรวจทานเพิ่มเติมก่อนแจ้งผล

## Required Disclaimers

Thai:

> รายงานนี้เป็นผลช่วยคัดกรองเบื้องต้น ไม่ใช่การวินิจฉัยขั้นสุดท้าย และไม่ใช่การตรวจหาเชื้อ HPV DNA/RNA ผลทุกครั้งต้องผ่านการยืนยันโดยบุคลากรทางการแพทย์

English:

> This report is a screening-support output, not a final diagnosis and not an HPV DNA/RNA test. All results require clinician review and sign-off.

## Unsafe Language

Do not use:

- "คุณเป็นมะเร็ง"
- "คุณติดเชื้อ HPV"
- "ไม่ต้องกังวลแน่นอน"
- "AI ยืนยันแล้ว"
- "ผลถูกต้อง 100%"
- "ไม่ต้องพบแพทย์"

## Audit Trail

Each released report should store:

- image ID;
- model version;
- timestamp;
- raw AI suggestion;
- clinician final decision;
- clinician ID/sign-off;
- whether AI was accepted/edited/rejected;
- uncertainty level;
- report language/version.

No patient-identifying data should be stored in public repo artifacts.


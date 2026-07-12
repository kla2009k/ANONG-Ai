# Rubric & เตรียมตัว — IID 2026 (IYIA) + WSEEC (IYSA) สำหรับ CerviCo-Pilot
> สรุปจาก web (มิ.ย. 2026). ⚠️ % ที่ไม่ confirm = ต้องเช็ค guidebook ทางการก่อนส่ง (อย่าอ้างเป๊ะ)

## งานคืออะไร
- **IID 2026 / IYIA** — Indonesia Inventors Day, จัดโดย **INNOPA** ภายใต้ **IFIA**. รุ่น **IYIA** = นักเรียน <18 ปี. ปีนี้ 3–6 ก.ย./ต.ค. 2026 จาการ์ตา. (เวที**สิ่งประดิษฐ์/นวัตกรรม** ไม่ใช่ ML benchmark)
- **WSEEC** — World Science, Environment & Engineering Competition จัดโดย **IYSA** + Univ. Pancasila. นานาชาติ (2025 มี 370 ทีม 14 ประเทศ)
- ทั้งคู่แนวเดียวกัน: **โปสเตอร์ + บูธ + พรีเซนต์ภาษาอังกฤษ + Q&A** ตัดสินโดยกรรมการ (มี online/Zoom ได้)

## เกณฑ์ตัดสิน (confirmed + typical IYSA/INNOPA)
| หมวด | น้ำหนัก | กรรมการดูอะไร |
|---|---|---|
| **Idea / Originality / Inventiveness / Functionality** | **~40%** (confirmed IYIA) | ใหม่/ต่างแค่ไหน, แก้ปัญหาจริงไหม, ใช้งานได้ไหม |
| **Scientific method / Depth** | ~20% (typical) | ระเบียบวิธี, ข้อมูล, ผลลัพธ์น่าเชื่อ |
| **Benefit / Impact / Applicability** | ~20% (typical) | ประโยชน์ต่อสังคม, นำไปใช้จริง, ความยั่งยืน |
| **Presentation (poster + oral + booth + English)** | ~15-20% (typical) | สื่อสารชัด, โปสเตอร์สวย, ตอบ Q&A ได้ |

## รูปแบบ (WSEEC confirmed)
- พรีเซนต์ **7 นาที + Q&A 8 นาที** = 15 นาที, **ภาษาอังกฤษ** (สไลด์อังกฤษ)
- มี **บูธ/โต๊ะ + โปสเตอร์** (ตกแต่งพอดี ไม่เวอร์) + ต้องโชว์ product
- รองรับ online/Zoom

## CerviCo-Pilot แมตช์ rubric ยังไง (จุดแข็ง)
| หมวด | เราใช้อะไรชน |
|---|---|
| Idea/Originality (40%) | **XAI co-pilot + รายงาน 2 ชั้น แก้ loss-to-follow-up 41%** + เน้น HPV ไทย 52/58 + รพ.ชุมชน → human-centered, ไม่ใช่ classifier เปล่า |
| Scientific (20%) | honest metrics + **bootstrap 95% CI + 5-fold CV + QWK/MCC/AUPRC** (โปร, reproducible) |
| Impact (20%) | WHO 90-70-90, LMIC, ต้นทุนต่ำ, ขยาย CLMV |
| Presentation (20%) | **เว็บ explainer + demo คลิกได้ + heatmap** = โชว์บูธได้จริง; โปสเตอร์ + พรีเซนต์ 7 นาที EN |

## สิ่งที่ต้องเตรียม (checklist)
- [ ] **โปสเตอร์ A0/A1 ภาษาอังกฤษ** (problem→solution→pipeline→results CI→impact) — ยังไม่มี
- [ ] **สไลด์พรีเซนต์ 7 นาที (EN)** + ซ้อม Q&A 8 นาที — มี PITCH_SCRIPT (ไทย) ต้องทำ EN
- [ ] **Demo บูธ**: เว็บ explainer + live model (server) + heatmap — ✅ มีแล้ว (explainer.html + server)
- [ ] **เลขแกร่ง**: triage sens 1.0 (CI 1.0–1.0), AUROC 0.964, QWK 0.687 + CV mean±SD — ✅ (กำลังได้จาก CV)
- [ ] **abstract/บทคัดย่อ EN** — มีในเล่ม docx (ไทย) ต้องทำ EN
- [ ] เช็ค **guidebook ทางการ** ยืนยัน % + deadline + ค่าสมัคร + รูปแบบ submission

## โฟกัสให้ตรงเวที (สำคัญ)
- เวทีนี้ **นวัตกรรม+impact+presentation ชนะ acc ดิบ** → นำด้วยเรื่องเล่า (คนหาย 41%) + demo สด ไม่ใช่ตัวเลข
- เลขชู: **triage sensitivity/AUROC + CI + CV** (honest, ดูโปร) — ไม่เน้น acc 0.69
- **ห้าม fabrication** (เพิ่งเคลียร์มา) — เวที inter ตรวจเข้ม + reproducible สำคัญ

## Sources
- IID/IYIA: https://iid-official.com/iyia/ · IFIA: https://ifia.com/iyia-and-wintex-indonesia-inventors-day/
- WSEEC (IYSA): https://wsec.or.id/ · WSEEC 2024 guidebook (Scribd) · WSEEC 2025 (Univ. Pancasila)

*จัดทำ 2026-06-27 — ยืนยัน % กับ guidebook ทางการก่อนส่งจริง*

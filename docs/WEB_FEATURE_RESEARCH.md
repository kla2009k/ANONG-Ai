# เว็บ CerviCo-Pilot ควรมีอะไรอีก — Deep Research + Gap Analysis + Backlog
> จัดทำ 2026-06-29 · อ้างอิงแนวปฏิบัติ clinical AI / SaMD / accessibility / LMIC · เทียบกับ build ปัจจุบัน

## Executive Summary
เว็บปัจจุบันแข็งแรงด้านแกนหลักแล้ว: 6 หน้า, dark mode, **รูปจริง+Grad-CAM+ผลจริง**, เชื่อม FastAPI วิเคราะห์สด, กราฟ honest (confusion heatmap, per-fold line, per-class bar), รายงาน 2 ชั้น. จากงานวิจัย clinical decision-support สิ่งที่ "ควรมี" เพื่อให้ดูเป็นเครื่องมือแพทย์จริง + ได้แต้มเวที แบ่งเป็น 3 ระดับ:

- **MUST (ความปลอดภัย/ความน่าเชื่อถือ — ทำก่อน):** ปุ่ม "แพทย์ยืนยัน/แก้ไข/ปฏิเสธ" จริง (sign-off), **Model Card** หน้า, intended-use/disclaimer ชัดทุกผล, แสดง **uncertainty + abstain** (เคสไม่มั่นใจส่งคน), บังคับให้แพทย์ใส่ความเห็นก่อน AI (กัน automation bias), accessibility สีไม่พึ่งสีอย่างเดียว + alt text.
- **SHOULD:** export รายงาน PDF, ROC + calibration plot, worklist/triage queue (หลายภาพ), feedback/รายงานข้อผิดพลาด, PWA offline + service worker, version/“how it works” page, EN toggle.
- **NICE:** LINE/SMS mock, audit log, batch upload, multi-CAM compare, QR/print poster mode.

**ข้อค้นพบหลัก:** จุดที่ยกระดับจาก "เดโมสวย" → "เครื่องมือแพทย์น่าเชื่อถือ" คือ **human-in-the-loop sign-off + transparency (model card/disclaimer) + การจัดการความไม่แน่นอน** ซึ่งงานวิจัยชี้ว่าเป็นตัวสร้าง trust ที่ยั่งยืนและลด automation bias [1][3][9].

---

## Introduction
**ขอบเขต:** แนวปฏิบัติเว็บ/UX สำหรับ AI ช่วยคัดกรองทางการแพทย์ (decision-support) 9 ด้าน + เทียบ build ปัจจุบัน → backlog จัดลำดับ. **กลุ่มผู้อ่าน:** ทีมเทคนิคนักเรียน. **สมมุติฐาน:** เป้าหมายคือ POC ที่ดู "ทางการ + น่าเชื่อถือ + ใช้ได้จริง" สำหรับ Samsung SfT / IID / WSEC ไม่ใช่ผลิตภัณฑ์ขอ อย. จริง.

---

## Finding 1 — UX สำหรับ AI decision-support: บทบาทชัด + override
งานวิจัยเน้น **decision-centered design**: ต้องระบุชัดว่า AI เป็น "ที่ปรึกษา" ไม่ใช่ "ผู้สั่ง" — ความกำกวมตรงนี้ทำลาย trust และทำให้เกิดทั้ง over-reliance และ disengagement [1]. ต้องมี **override mechanism** ให้แพทย์ค้านผล AI ได้โดยไม่มีโทษ และแนวคิด "expert critiquing" คือ **ให้แพทย์ใส่ความเห็นก่อน แล้ว AI ค่อยเสริม/ท้วง** ช่วยลด automation bias โดยตรง [1][3].
> **Gap เรา:** มีข้อความ "แพทย์ต้องยืนยัน" แต่ **ยังไม่มีปุ่ม sign-off จริง** (ยืนยัน/แก้ไข/ปฏิเสธ) + ยังไม่มี flow ให้แพทย์ใส่ความเห็นก่อน. → MUST.

## Finding 2 — Trust & Explainability: Model Card + แสดงความมั่นใจคู่ผล
**Model Card** กลายเป็น best practice (Google 2019 → FDA ดัน transparency มิ.ย. 2024) มีหัวข้อ: intended use, training data + bias, performance แยก subgroup, **limitations + "ห้ามใช้ทำอะไร"** และ clinical boundary (ผู้ใช้คือใคร จุดตัดสินใจไหน) [4][5]. การแสดง **confidence ควรมาคู่กับ prediction เสมอ** และต้องบอก "อะไรขับความมั่นใจ" — แต่ raw probability เฉย ๆ ไม่ช่วยปรับ reliance ต้องใช้ **calibrated / Low-Med-High + บริบท** [6][8].
> **Gap เรา:** มี Grad-CAM + bar prob + uncertainty level (ดี) แต่ **ยังไม่มีหน้า Model Card** เป็นเรื่องเป็นราว + ยังไม่บอก "ทำไมมั่นใจ/ไม่มั่นใจ". → MUST (model card), SHOULD (อธิบาย driver).

## Finding 3 — SaMD safety UI: intended-use + version + feedback
FDA/IMDRF GMLP 2025: ต้องสื่อสารชัดว่ามี AI, **intended use + ประชากรที่ออกแบบไว้**, performance, และ **version tracking + การเปลี่ยนแปลง** ผ่าน UI; ต้องเปิดเผย limitation และ monitor ต่อเนื่อง [7][12]. ทุกผลควรติด **disclaimer "ไม่ใช่การวินิจฉัย"** ไม่ใช่แค่ footer.
> **Gap เรา:** disclaimer มีแต่กระจาย; **ไม่มี version/changelog, ไม่มีช่อง feedback/รายงานปัญหา, intended-use ไม่เด่น**. → MUST (disclaimer ติดทุกผล + intended-use), SHOULD (version + feedback).

## Finding 4 — Accessibility (WCAG 2.2 + color-blind + ไทย)
WCAG 2.2 AA: contrast ข้อความ ≥ 4.5:1, องค์ประกอบกราฟ ≥ 3:1; **300 ล้านคนตาบอดสี → ห้ามพึ่งสีอย่างเดียว** ใช้ pattern/ไอคอน/ป้ายข้อความเสริม; กราฟต้องมี **alt text/คำอธิบาย** และ keyboard navigable [13][14][19]. palette แดง-เขียว (NILM เขียว/SCC แดง ของเรา) = เสี่ยงตาบอดสีแดง-เขียว.
> **Gap เรา:** confusion heatmap + kind colors พึ่งสีล้วน, ยังไม่มี alt text/aria, ยังไม่เช็ค contrast (dark mode), ไม่มี keyboard focus styles ชัด. → MUST (เพิ่มป้าย/ไอคอนกำกับสี + alt), SHOULD (audit contrast + focus).

## Finding 5 — Privacy / PDPA in-browser
LMIC offline-first: ประมวลผลฝั่ง client/edge ลดการส่ง PHI; ภาพผู้ป่วยถ้าส่ง server ต้องมี consent + ไม่เก็บถาวร + de-identify [PDPA]. เว็บควรระบุชัดว่า "ภาพถูกส่งไปไหน/เก็บไหม".
> **Gap เรา:** upload ส่งภาพไป :8003 โดยไม่มีข้อความ privacy; ตัวอย่าง offline ดีอยู่แล้ว. → SHOULD (ข้อความ privacy + ตัวเลือก "ไม่เก็บภาพ"), NICE (in-browser inference ONNX).

## Finding 6 — PWA / offline / low-bandwidth (รพ.ชนบท)
แนวปฏิบัติ rural health: **service worker + cache-first สำหรับ static, network-first สำหรับข้อมูล**, IndexedDB, รูป WebP/AVIF + srcset, **skeleton screen** ตอนโหลด, ฟอนต์เบา [LMIC refs]. ทำให้ใช้ได้แม้เน็ตหลุด.
> **Gap เรา:** มี sw.js (จาก DermaTrace) แต่ไม่ได้ register/ปรับ; ภาพ sample เป็น jpg (ควร webp); ยังไม่มี skeleton/offline indicator. → SHOULD (PWA จริง + manifest CerviCo + offline banner), NICE (webp).

## Finding 7 — Reporting: structured + 2-layer + export
Bethesda = structured report มาตรฐาน; ควร export **PDF ทางการ** ได้, รายงานผู้ป่วยต้อง **plain language ระดับ ป.3–ป.5** (everyday words, ประโยคสั้น, active voice) ลด anxiety + เพิ่มการมาตามนัด [Health literacy refs]. ช่องทางส่ง (LINE/SMS) แก้ loss-to-follow-up.
> **Gap เรา:** มีรายงาน 2 ชั้นเป็นข้อความ (ดี) แต่ **ยังไม่มี export PDF, ไม่มีโครง structured เต็ม (case id/วันที่/ผู้ลงนาม), ภาษายังไม่ผ่านเช็ค readability**. → MUST (โครง report + แพทย์ลงนาม), SHOULD (export PDF + readability), NICE (LINE/SMS mock).

## Finding 8 — Performance dashboard: เพิ่ม ROC + calibration
มาตรฐาน 3 กราฟของ AI วินิจฉัย: **confusion matrix + ROC (sens vs 1-spec, AUC) + calibration plot (เทียบเส้น 45°)** [RSNA]; แนะนำรายงาน macro-F1, per-class sens/spec, และ **calibration (ECE/Brier/reliability)** เพราะ discrimination ดีไม่การันตี calibration ดี [eval refs].
> **Gap เรา:** มี confusion + per-fold + per-class (ดีมาก) แต่ **ขาด ROC curve + calibration/reliability plot**. และ ECE ยังคำนวณไม่จริง (ระบุไว้แล้ว). → SHOULD (เพิ่ม ROC + บอกตรงๆ ว่า calibration ยังไม่ทำ).

## Finding 9 — Demo/judging readiness (IID/WSEC)
กรรมการสาย invention: โครงโปสเตอร์ logical (คำถาม→วิธี→ผล→สรุป) scan ได้ใน 1 นาที, **demo สดต้องซ้อม + มี fallback ถ้าพัง**, พูด 2–5 นาทีจากความจำ, แต่งกายทางการ; ถ้าเดโมพังให้พลิกเป็น "สิ่งที่เรียนรู้" [science fair refs].
> **Gap เรา:** เว็บ demo ดีแต่ **พึ่ง server (ถ้าพังหน้างาน = เสี่ยง)** → ตัวอย่าง offline เป็น fallback ที่ดีอยู่แล้ว; ควรมี **"presenter/kiosk mode"** + ปุ่มรีเซ็ตเร็ว + QR ไปเว็บ. → SHOULD (kiosk/demo mode + QR), NICE (โหมดนำเสนอเต็มจอ).

---

## Synthesis & Insights
1. **แกน UX ครบแล้ว — ที่ขาดคือ "ชั้น governance/trust"** (sign-off, model card, disclaimer-per-result, uncertainty handling). นี่คือสิ่งที่แยก "เดโมนักเรียน" ออกจาก "เครื่องมือแพทย์" และเป็นแต้มใหญ่เวที [1][3][4].
2. **Honesty เป็นจุดแข็งอยู่แล้ว** (confusion จริง, per-fold, บอก limitation) — ต่อยอดด้วย ROC + calibration ให้ครบมาตรฐาน [RSNA].
3. **Resilience สำหรับ demo day** สำคัญกว่าฟีเจอร์เพิ่ม — offline fallback + kiosk mode กัน "พังหน้างาน".
4. **Accessibility = ได้ทั้งคะแนน + จริยธรรม** ราคาถูก (เพิ่มป้าย/ไอคอน/alt) แต่หลายทีมมองข้าม.

---

## Prioritized Backlog (ทำตามนี้)

### 🔴 MUST (ก่อน submission/เดโม)
1. **ปุ่ม sign-off จริง** ที่หน้า Analyze: [✔ แพทย์ยืนยัน] [✏ แก้ไขระดับ] [✘ ปฏิเสธสไลด์คุณภาพต่ำ] → เปลี่ยนสถานะผล + ต้องกดก่อน "ส่งรายงานผู้ป่วย"
2. **หน้า Model Card** (/model หรือใน About): intended use, ประชากร (Herlev), data + bias, performance (held/CV), **"ห้ามใช้: วินิจฉัย/แทนแพทย์/ตรวจ HPV DNA"**, limitations, version
3. **Disclaimer ติดทุกผล** (ไม่ใช่แค่ footer) + intended-use banner ในหน้า Analyze
4. **Uncertainty/abstain เด่น**: เคส level=high → แสดงป้าย "ระบบไม่มั่นใจ — ส่งให้แพทย์อ่านเอง" ชัด (มี level แล้ว แค่ทำให้เด่น + กันไม่ให้ออกรายงานผู้ป่วยอัตโนมัติ)
5. **Accessibility ขั้นต่ำ**: เพิ่มไอคอน/ป้ายข้อความกำกับทุกสี (NILM✓/HSIL⚠/SCC⛔), alt/aria-label ทุกกราฟ, focus ring
6. **โครง report ทางการ**: case id (mock), วันที่, ชื่อผู้ลงนาม, Bethesda + คำแนะนำ + disclaimer

### 🟠 SHOULD
7. **Export PDF** รายงาน (jsPDF) — แพทย์ + ผู้ป่วย
8. **ROC curve + reliability/calibration plot** ในหน้า Performance (บอกตรง ๆ ว่า calibration ยังไม่ปรับ)
9. **PWA จริง**: register service worker, manifest CerviCo (ไอคอน/ชื่อ), offline banner + cache-first
10. **Feedback/รายงานปัญหา** (ปุ่ม "รายงานผลที่น่าสงสัย") + version/changelog เล็ก
11. **Privacy note** ที่ upload ("ภาพส่งไปประมวลผลที่เครื่อง/เซิร์ฟเวอร์ ไม่ถูกเก็บถาวร")
12. **EN toggle** (เวที inter พูดอังกฤษ) — อย่างน้อยหน้า About/Model Card
13. **Worklist/triage demo**: อัปหลายภาพ → เรียงตามความเสี่ยง (โชว์ concept คัดกรองจำนวนมาก)
14. **Kiosk/demo mode** + ปุ่มรีเซ็ต + QR code ไปเว็บ (กันพังหน้างาน)

### 🟢 NICE
15. LINE/SMS mock (โชว์ flow แก้ loss-to-follow-up), audit log, batch report, multi-CAM compare (มีใน server แล้ว), WebP samples, in-browser ONNX (privacy), readability score ของรายงานผู้ป่วย

---

## Limitations & Caveats
- รายงานนี้อิง best practice เชิงหลักการ — บาง guideline (FDA/IMDRF) เป็นของผลิตภัณฑ์จริง ไม่ใช่ POC นักเรียน จึงใช้ "ตามสมควร" (โชว์ความ aware พอ)
- ตัวเลข backlog priority เป็นการประเมินตามบริบทเวที ไม่ใช่ requirement บังคับ
- ยังไม่ได้ audit contrast/accessibility ด้วยเครื่องมือจริง (เป็นงานใน MUST-5)

## Bibliography
1. JAMIA 2024 — Recommendations for AI-enabled clinical decision support. https://academic.oup.com/jamia/article/31/11/2730/7776823
2. Frontiers Digital Health 2026 — Operationalizing trustworthy AI in clinical workflows. https://www.frontiersin.org/journals/digital-health/articles/10.3389/fdgth.2026.1779041/full
3. Springer Sci Eng Ethics 2025 — Compliance with guidelines & AI-CDSS: ethics & trust. https://link.springer.com/article/10.1007/s11948-025-00562-z
4. arXiv 2311.12560 — Expanding clinical AI model card (bias/fairness). https://arxiv.org/pdf/2311.12560
5. arXiv 2511.01902 — Transparent & operable design principles for healthcare AI. https://arxiv.org/pdf/2511.01902 · npj Digital Medicine 2025 — transparency in FDA-reviewed AI/ML devices. https://www.nature.com/articles/s41746-025-02052-9
6. arXiv 2401.05612 — Designing for appropriate reliance (uncertainty presentation). https://arxiv.org/pdf/2401.05612
7. FDA — Transparency for ML-enabled medical devices: guiding principles. https://www.fda.gov/medical-devices/software-medical-device-samd/transparency-machine-learning-enabled-medical-devices-guiding-principles
8. MDPI Diagnostics 2025 — Dynamic framework for confidence calibration & transparency / PMC12428550. https://www.mdpi.com/2075-4418/15/17/2204
9. PMC11073764 — AI-driven CDSS: automation bias & trust. https://pmc.ncbi.nlm.nih.gov/articles/PMC11073764/
12. IMDRF/FDA GMLP 2025 + PCCP guidance. https://www.fda.gov/media/151482/download
13. WebAIM — Contrast & color accessibility (WCAG 2). https://webaim.org/articles/contrast/
14. WellAlly — Accessible health data visualizations (WCAG). https://www.wellally.tech/blog/accessible-health-data-visualizations-wcag-guide
19. Accessibility.Works — What's new in WCAG 2.2. https://www.accessibility.works/blog/wcag-2-2-guide/
- RSNA Radiology — Methods for clinical evaluation of AI diagnostic algorithms (ROC/calibration/confusion). https://pubs.rsna.org/doi/full/10.1148/radiol.220182
- ScienceDirect 2025 — Evaluation metrics in medical imaging AI: pitfalls & recommendations. https://www.sciencedirect.com/science/article/pii/S3050577125000283
- SCT 2026 — Low-bandwidth healthcare app UX (rural). https://www.sctinfo.com/blog/building-healthcare-apps-for-low-bandwidth-area/
- CHCS / HRSA — Plain language & health literacy for patient communication. https://www.chcs.org/resource/improving-written-communication-to-promote-health-literacy/
- Science Buddies — Judging tips for top science competitions. https://www.sciencebuddies.org/science-fair-projects/competitions/judging-tips-for-top-science-competitions
- CAP TODAY — AI in cytology (worklist/triage, Bethesda). https://www.captodayonline.com/ai-in-cytology-where-digital-meets-diagnostic/

## Methodology Appendix
- Mode: deep · 10 web searches ครอบคลุม 9 หัวข้อ (CDSS UX, model card, uncertainty display, SaMD UI, accessibility, PWA/LMIC, dashboard charts, plain-language, judging, cytology worklist)
- แหล่ง: peer-reviewed (JAMIA, npj Digital Medicine, RSNA, MDPI, Springer, Frontiers), regulatory (FDA/IMDRF), arXiv (flagged), practitioner guides
- ทุก finding map กับ build ปัจจุบัน + แปลงเป็น backlog ที่ทำได้จริง
*จัดทำ 2026-06-29*

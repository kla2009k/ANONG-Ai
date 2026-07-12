# CervicalAI — User Guide (v1.0 for รพ.ชุมชน)

**สำหรับ:** พยาบาล/เจ้าหน้าที่คัดกรอง + แพทย์เวชปฏิบัติทั่วไป

## การใช้งานพื้นฐาน (Web Demo / Local Server)

1. เปิดเว็บ demo หรือ http://localhost:8003
2. อัปโหลดภาพ ThinPrep / Pap smear (jpg/png, <12MB)
3. ดูผลทันที:
   - Bethesda class (NILM / LSIL / HSIL / SCC / KOIL)
   - ความมั่นใจ + Uncertainty flag (ถ้าสูง → ส่งหมอเช็ค)
   - Heatmap (Grad-CAM) แสดงจุดที่ AI ดู (นิวเคลียส)
   - รายงาน 2 ชั้น (ชั้นแพทย์ + ชั้นผู้ป่วยภาษาไทย)

## Output Interpretation (สรุปเร็ว)

- **NILM + low unc**: ผลปกติ — แจ้งผู้ป่วยปกติ
- **LSIL / KOIL**: ส่ง HPV test + follow 6 เดือน
- **HSIL / SCC**: ส่ง Colposcopy ด่วน + แนะนำ HPV co-test 16/18/52/58
- **Uncertainty flag = Yes**: อย่าใช้ผล AI เดี่ยว — ต้องแพทย์อ่านเพิ่ม

## Guardrails (สำคัญมาก)

- ผล AI **ต้อง** แพทย์ลงนามก่อนปล่อยให้ผู้ป่วย
- อย่าใช้คำว่า "เป็นมะเร็ง" กับผู้ป่วยจาก AI
- ภาพเบลอ/มืด/เล็ก AI จะปฏิเสธ
- สำหรับ Phase 1 ใช้เฉพาะ public data — ยังไม่นำไปใช้จริงจนกว่าจะ validate ไทย

## LINE / Report Export

- จากเว็บ → Export JSON หรือ copy ชั้นผู้ป่วยส่ง LINE
- ใช้ make_full_report.py สำหรับ batch production reports

## Troubleshooting

- ภาพไม่ขึ้น: ใช้ PNG/JPG 224px+
- ผลแปลก: ดู uncertainty + heatmap
- Server ไม่รัน: `cd server && python -m uvicorn app:app --port 8003`

---

*เอกสารนี้เป็นส่วนหนึ่งของ CervicalAI artifact factory burn 2026-06-26*

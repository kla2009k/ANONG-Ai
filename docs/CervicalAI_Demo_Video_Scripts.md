# CervicalAI — Demo Video Scripts & Host Simulation Docs

**Purpose**: Text scripts for recording demo videos or live presentation (no actual video files).

---

## A. 2-3 Minute Demo Script (Pitch / Quick Show)

**Scene 1 — Hook (15s)**
> "สวัสดีครับ วันนี้ผมจะสาธิต CervicalAI — ระบบ AI คัดกรองเซลล์ปากมดลูกแบบ 2 ชั้น
> ปัญหาในไทยคือ loss-to-follow-up สูง เพราะผู้ป่วยไม่เข้าใจจดหมายผล วันนี้เราจะโชว์ว่า AI ช่วยได้ยังไง"

**Scene 2 — Upload & Analyze (30s)**
1. เปิดเว็บ http://localhost:8003
2. กด "ใช้ภาพตัวอย่าง" หรือ "สร้างภาพจำลอง"
3. กด "วิเคราะห์"
4. พูด: "ได้ผล 5-class (NILM/LSIL/HSIL/SCC/KOIL) + ตรวจ koilocyte + uncertainty gauge"

**Scene 3 — Live Heatmap (30s)**
1. สลับปุ่ม Original → Heatmap → Blend → Side-by-side
2. ลาก slider Alpha 0.3 → 0.8
3. เปลี่ยน Colormap เป็น VIRIDIS / HOT
4. กด "Apply Live"
5. พูด: "Heatmap แสดงจุดที่โมเดลสนใจ (demo ใช้ spotlight บริเวณมืด nuclear-like)"

**Scene 4 — Contour Edit (20s)**
1. คลิก contour สีแดง/เขียว บน canvas
2. เปลี่ยนคลาส NILM → HSIL → SCC
3. กด "ส่งการแก้ไขไปยังเซิร์ฟเวอร์"
4. พูด: "นี่คือ human-in-the-loop sim — แพทย์แก้ไขได้ (Phase 2 จะใช้ SAM2 จริง)"

**Scene 5 — Report 2-Layer + Editor (30s)**
1. กด "สร้างรายงาน"
2. แสดง clinical (Bethesda + triage + risk) และ patient (ภาษาง่าย)
3. แก้ไขใน textarea เช่น เปลี่ยน action
4. กด Apply + Export JSON
5. พูด: "รายงาน 2 ชั้น + ฝัง XAI heatmap + แก้ไขได้ก่อนส่งแพทย์"

**Scene 6 — Batch + Stress (20s)**
1. กด "สร้างชุดภาพจำลอง 8 ภาพ"
2. กด "วิเคราะห์ทั้งหมด"
3. กด "Stress Test 50 loops"
4. แสดง log avg/p95
5. พูด: "รองรับ batch และ stress test ได้จริง"

**Close (10s)**
> "ทุกผลต้องให้แพทย์ยืนยัน — AI เป็นเพียงผู้ช่วยคัดกรอง ครับ"

---

## B. 5-7 Minute Full Technical Demo

**0:00-0:45** Problem + Solution Overview
- Loss-to-follow-up 41% จากรายงานเข้าใจยาก
- 2-layer report (clinical EN + patient TH)
- XAI + uncertainty สำหรับแพทย์
- Guardrails ชัดเจน

**0:45-2:00** Full Single Case Walkthrough
- Upload ภาพจริงหรือ synthetic
- วิเคราะห์
- แสดงทุกส่วน: classification, koilocyte, quality, uncertainty, heatmap
- สลับทุกโหมด heatmap + live controls

**2:00-3:00** Interactive Human-in-the-Loop
- Contour canvas + list
- คลิกสลับคลาสหลายตัว
- ส่ง edit ไป server
- แสดง response (suggested_top + edited contours)

**3:00-4:30** Report Editor Deep Dive
- สร้างรายงาน
- แก้ไข clinical layer (เช่น เปลี่ยน triage)
- แก้ไข patient layer (เช่น เปลี่ยน action)
- Regenerate จาก template
- Export JSON (มี xai_embed)
- แสดงตัวอย่าง full_burn_report.json

**4:30-5:30** Batch + Stress
- สร้าง 8-12 ภาพจำลอง
- วิเคราะห์ batch
- Run 50 / 100 loops
- แสดง timing (avg, p95)
- ใช้ CLI stress_test.py แสดง (ถ้าต้องการ)

**5:30-6:30** Export + Integration Points
- Export JSON สำหรับ downstream
- Print/PDF จาก browser
- /api/demo_script สำหรับ host
- เชื่อมกับ make_full_report.py สำหรับ DOCX จริง

**6:30-7:00** Limitations + Guardrails + Q&A
- Demo mode vs Model mode
- Synthetic data
- ต้องแพทย์ลงนาม
- Phase 2: LLM, SAM2, real Thai data, FDA path

---

## C. Host Simulation Notes (สิ่งที่พูดแทรก)

### C.1 ทุกครั้งที่โชว์ heatmap
> "ใน demo นี้ เราใช้ spotlight บริเวณมืดเพื่อจำลอง Grad-CAM ถ้าโหลดโมเดลจริงจะได้ heatmap จาก Grad-CAM + multi-method"

### C.2 ทุกครั้งที่โชว์ contour
> "Contour เหล่านี้เป็น synthetic จาก threshold + jitter ไม่ใช่ segmentation จริง Phase 2 จะใช้ SAM2 fine-tune บน nuclei ปากมดลูก"

### C.3 ทุกครั้งที่โชว์ report
> "รายงานนี้เป็น template ยังไม่มี LLM จริง แต่โครงสร้างพร้อมต่อ LLM ที่ constrained (RAG + schema) ใน Phase 2"

### C.4 ทุกครั้งที่โชว์ stress
> "นี่คือการทดสอบ server ด้วย synthetic data 100% ไม่มีข้อมูลผู้ป่วยจริง ใช้เพื่อวัด latency และ stability"

### C.5 ปิดท้ายทุก demo
> "CervicalAI เป็นเครื่องมือคัดกรองเบื้องต้นด้วย AI — ต้องให้แพทย์ยืนยันและลงนามก่อนปล่อยผล ไม่ใช่การวินิจฉัย"

---

## D. Video Recording Tips (Text)

- ความละเอียดแนะนำ: 1920x1080 หรือ 1280x720
- เสียง: พูดช้า ชัด ใช้ไมค์ดี
- แสดง cursor ชัด
- ซูมที่ gauge / heatmap / report editor เมื่อพูดถึง
- แสดง terminal log เมื่อรัน stress CLI
- ใส่ timestamp overlay ถ้าต้องการ (เช่น 0:00-0:45 Problem)
- Export เป็น MP4 + มีสคริปต์คู่ (ไฟล์นี้)

---

## E. Quick Reference Commands (for Live Host)

```bash
# Start server
cd server
python -m uvicorn app:app --port 8003 --reload

# Quick stress (CLI)
python stress_test.py --n 50 --concurrency 4

# Batch sim
python batch_sim.py --count 8

# Generate fake data only (via API)
curl -X POST http://localhost:8003/api/generate_fake \
  -H "Content-Type: application/json" \
  -d '{"count":4,"size":224}'

# Get demo script
curl http://localhost:8003/api/demo_script | jq .
```

---

**END OF VIDEO SCRIPTS**

*Text-only. No video files generated in this burn.*
# แผนพัฒนาเว็บ CerviCo-Pilot — ละเอียดทุกขั้น (ก่อนลงมือ)
> 2026-06-30 · อิง backlog จาก WEB_FEATURE_RESEARCH.md · เป้า: กันตกหล่น/คลาดเคลื่อน

## 0. สถานะโค้ดปัจจุบัน (baseline)
```
web-react/src/
  App.tsx              # routes: / /analyze /performance /knowledge /about /settings
  main.tsx, index.css  # theme light/dark (CSS vars), reveal/card/kicker
  components/ Layout, Navbar, Reveal, ui/{button,card,badge,tabs}
  lib/ data.ts (CLASSES, METRICS, analyzeReal), theme.ts, utils.ts
  pages/ Landing, Analyze, Performance, Knowledge, About, Settings
public/samples/  # 8 รูปจริง + _cam + samples.json (จาก gen_samples.py)
```
build: `npm run build` → `../web-dist` (base "./"), serve static :8090, API server :8003.

## 0.1 หลักการทำงาน (กันพลาด)
- แก้ทีละ item → `npm run build` ทุกครั้ง → ถ้า error แก้ก่อนไปต่อ (อย่าสะสม)
- ทุก item มี **acceptance check** ชัด
- ไม่ทำลายของเดิม: เพิ่ม component/หน้าใหม่มากกว่ารื้อ
- รูป/asset ที่ต้องใช้โมเดล → gen ด้วย script ก่อน (offline-bundle) เพื่อไม่พึ่ง server ตอนเดโม

---

## จุดที่ต้องตัดสินใจก่อน (DECISIONS) — เลือกก่อนเริ่ม
- **D1 Export PDF:** (ก) `window.print()` + print CSS [แนะนำ — รองรับไทยชัวร์ ไม่มีปัญหาฟอนต์] vs (ข) jsPDF [เสี่ยงฟอนต์ไทยต้อง embed Sarabun base64 ยุ่ง]
- **D2 EN toggle:** (ก) i18n บางส่วน (Model Card + About + disclaimer) [แนะนำ — คุ้ม/เบา] vs (ข) i18n เต็มทุกหน้า [งานเยอะ เสี่ยง] vs (ค) ข้าม
- **D3 ขอบเขตรอบนี้:** ทำ **MUST ทั้งหมด** ก่อน แล้วค่อย SHOULD [แนะนำ] vs ทำ MUST+SHOULD รวด
- **D4 QR (kiosk):** ใช้ไลบรารี `qrcode` (npm) vs รูป QR ที่ gen ไว้ล่วงหน้า [แนะนำ — เบากว่า ไม่เพิ่ม dep]

---

## PHASE 1 — MUST (governance/trust/safety) 🔴

### M1. ปุ่ม Sign-off (แพทย์ยืนยัน/แก้ไข/ปฏิเสธ)
- **ไฟล์:** `pages/Analyze.tsx` (ResultCard)
- **ทำ:** เพิ่ม state `status: "pending"|"confirmed"|"edited"|"rejected"` + `overrideClass`.
  - แถวปุ่ม 3 ปุ่ม: ✔ ยืนยัน / ✏ แก้ไขระดับ (dropdown เลือก Bethesda) / ✘ ปฏิเสธสไลด์
  - ป้ายสถานะบนการ์ด (เช่น "รอแพทย์ยืนยัน" สีเทา → "ยืนยันแล้ว" เขียว)
  - ปุ่ม "ส่งรายงานผู้ป่วย" **disabled จนกว่า status=confirmed/edited**
- **data:** ไม่ต้อง backend (state ใน component); override เปลี่ยน top ที่แสดง
- **Acceptance:** กดยืนยัน → ป้ายเปลี่ยน + ปุ่มส่งรายงาน enable; แก้ไข → ระดับเปลี่ยนตาม; ปฏิเสธ → ซ่อนรายงาน + ขอภาพใหม่
- **Risk:** ต่ำ

### M2. หน้า Model Card
- **ไฟล์ใหม่:** `pages/ModelCard.tsx` · แก้ `App.tsx` (route `/model`), `Navbar.tsx` (ลิงก์), `lib/data.ts` (const `MODEL_CARD`)
- **เนื้อหา (จากข้อมูลจริง):** intended use, ผู้ใช้=บุคลากรแพทย์, ประชากร/ข้อมูล=Herlev 917, training (EfficientNet-B0, focal, TTA), performance (held+CV จาก METRICS), **ห้ามใช้:** วินิจฉัยเอง/แทนแพทย์/ตรวจ HPV DNA/กลุ่มนอก Herlev, limitations (KOIL=0, specificity ปานกลาง, ECE ยังไม่ทำ, domain shift), version "Phase 1 POC", วันที่
- **Acceptance:** /model แสดงครบทุกหัวข้อ ตรงเลขจริง; ลิงก์ใน nav ใช้ได้
- **Risk:** ต่ำ

### M3. Disclaimer ติดทุกผล + Intended-use banner
- **ไฟล์:** `components/Disclaimer.tsx` (ใหม่, reusable) · ใช้ใน `Analyze.tsx` (ใต้ผล + banner บนหน้า)
- **ทำ:** banner เล็กบนหน้า Analyze "เครื่องมือคัดกรองช่วยตัดสินใจ — ไม่ใช่การวินิจฉัย ต้องมีแพทย์ยืนยัน"; แถบ disclaimer ใต้การ์ดผลทุกครั้ง
- **Acceptance:** เห็น disclaimer ทั้งบนหน้าและใต้ผล ทุกครั้งที่มีผล
- **Risk:** ต่ำ

### M4. Uncertainty / Abstain เด่น
- **ไฟล์:** `pages/Analyze.tsx` (ResultCard)
- **ทำ:** ถ้า `uncertainty.level==="high"` → แสดงแบนเนอร์เด่น (สี amber/แดง) "⚠ ระบบไม่มั่นใจในผลนี้ — ควรให้แพทย์อ่านสไลด์เอง" + **บล็อกการออกรายงานผู้ป่วยอัตโนมัติ** (ต้องแพทย์ override)
- **Acceptance:** เลือกตัวอย่างที่ unc=high (เช่น s04/s07) → เห็นแบนเนอร์ + รายงานผู้ป่วยถูกกั้น
- **Risk:** ต่ำ (มี level อยู่แล้วใน samples + server)

### M5. Accessibility ขั้นต่ำ
- **ไฟล์:** `lib/data.ts` (เพิ่ม `icon`+`safe` ต่อ class), `pages/Analyze.tsx`, `pages/Performance.tsx`, `pages/Knowledge.tsx`, `index.css`
- **ทำ:**
  - ทุกป้ายระดับมี **ไอคอน/สัญลักษณ์ + ข้อความ** ไม่พึ่งสีล้วน (NILM ✓ปกติ / LSIL ◐ / HSIL ⚠ / SCC ⛔)
  - SVG กราฟทุกตัว: `role="img"` + `aria-label` สรุป + `<title>` (per-class, confusion, fold line)
  - `:focus-visible` ring ชัดใน index.css; ตรวจ contrast dark mode (mut บนพื้นเข้ม ≥4.5:1)
- **Acceptance:** ดูแล้วแยกระดับได้แม้ภาพขาวดำ; Tab โฟกัสเห็นกรอบ; กราฟมี aria-label
- **Risk:** ปานกลาง (ต้องไล่หลายไฟล์ + เช็ค contrast)

### M6. โครงรายงานทางการ (structured)
- **ไฟล์:** `pages/Analyze.tsx`
- **ทำ:** รายงานแพทย์เพิ่ม: Case ID (gen `CC-yymmdd-xxxx`), วันที่/เวลา, Specimen, Bethesda, คำแนะนำ triage, ช่อง "ผู้ลงนาม: ____" + สถานะ sign-off (M1), disclaimer
- **Acceptance:** รายงานมี id/วันที่/ผู้ลงนาม + จัดวางแบบเอกสาร
- **Risk:** ต่ำ

**จบ PHASE 1 → build + เปิดเทสทุกหน้า**

---

## PHASE 2 — SHOULD 🟠

### S7. Export รายงาน (ตาม D1)
- **แนะนำ window.print():** `index.css` เพิ่ม `@media print` (ซ่อน nav/ปุ่ม, โชว์เฉพาะรายงาน) + ปุ่ม "พิมพ์/บันทึก PDF" เรียก `window.print()`
- **ไฟล์:** Analyze.tsx + index.css
- **Acceptance:** กดพิมพ์ → preview เป็นรายงานสะอาด (ไทยชัด) → Save as PDF ได้
- **Risk:** ต่ำ (ถ้าเลือก print); jsPDF = เสี่ยงฟอนต์

### S8. ROC curve + Calibration plot
- **ต้อง gen data จริงก่อน:** `ml/scripts/gen_curves.py` → รัน best_cervical.pt บน test → ROC points (binary triage: NILM vs abnormal) + reliability bins → save `web-react/public/samples/curves.json`
- **ไฟล์:** gen_curves.py (ใหม่), `lib/data.ts` (โหลด curves), `pages/Performance.tsx` (SVG ROC + calibration)
- **honest:** ถ้า calibration ยังไม่ดี → แสดง reliability diagram จริง + label "calibration ยังต้องปรับ (ECE สูง)" ไม่ปั้น
- **Acceptance:** หน้า Performance มี ROC (มี AUC + เส้น diag) + calibration (เทียบเส้น 45°)
- **Risk:** ปานกลาง (ต้อง gen + วาด SVG 2 กราฟ)

### S9. PWA (offline)
- **ไฟล์:** `public/manifest.webmanifest` (rebrand CerviCo + ไอคอน), `public/sw.js` (cache-first static + network-first api), `index.html` (link manifest), `main.tsx` (register sw)
- **Acceptance:** เปิดครั้งแรกออนไลน์ → ปิดเน็ต → หน้า/ตัวอย่าง offline ยังเปิดได้; ติดตั้งเป็น app ได้
- **Risk:** ปานกลาง (sw scope กับ base "./" + cache busting)

### S10. Feedback + Version
- **ไฟล์:** `pages/Settings.tsx` หรือ component เล็ก + `lib/data.ts` (VERSION/CHANGELOG)
- **ทำ:** ปุ่ม "รายงานผลที่น่าสงสัย" (เก็บ localStorage/แสดง toast mock) + แสดง version + changelog สั้น
- **Acceptance:** ส่ง feedback → ขึ้นยืนยัน; เห็น version
- **Risk:** ต่ำ

### S11. Privacy note (upload)
- **ไฟล์:** Analyze.tsx — ข้อความใต้ dropzone "ภาพถูกส่งไปประมวลผลที่เซิร์ฟเวอร์ในเครื่อง (:8003) ไม่ถูกจัดเก็บถาวร · ตัวอย่างทำงานออฟไลน์"
- **Acceptance:** เห็นข้อความชัด · Risk: ต่ำ

### S12. EN toggle (ตาม D2)
- **แนะนำบางส่วน:** `lib/i18n.ts` (dict th/en + `t()` + lang ใน localStorage) → ใช้กับ ModelCard + About + disclaimer + nav. ปุ่มสลับใน Navbar
- **ไฟล์:** i18n.ts (ใหม่), Navbar, ModelCard, About, Disclaimer
- **Acceptance:** สลับ TH/EN → หน้าเป้าหมายเปลี่ยนภาษา; จำค่าได้
- **Risk:** ปานกลาง-สูง (ขยายขอบเขตง่าย — คุมไว้เฉพาะหน้าที่ระบุ)

### S13. Worklist (คัดกรองหลายภาพ)
- **ไฟล์:** `pages/Worklist.tsx` (ใหม่) + route + nav, ใช้ samples + อัปหลายไฟล์ → ตารางเรียงตามความเสี่ยง (abnormal prob มาก่อน) + ธง uncertain
- **Acceptance:** อัปหลายภาพ/โหลด samples → list เรียง risk + คลิกดูผล
- **Risk:** ปานกลาง

### S14. Kiosk/Demo mode + QR (ตาม D4)
- **ไฟล์:** `App.tsx`/`Layout.tsx` (อ่าน `?kiosk=1` → ซ่อน nav เล็ก/โหมดเต็ม) + ปุ่มรีเซ็ต + รูป QR (gen ล่วงหน้า) ชี้ URL เดโม
- **Acceptance:** เปิด ?kiosk=1 → โหมดนำเสนอ; QR สแกนได้
- **Risk:** ต่ำ

---

## PHASE 3 — NICE 🟢 (ถ้ามีเวลา)
LINE/SMS mock flow · audit log (localStorage) · batch report · multi-CAM compare (server มี advanced_xai แล้ว → แค่แสดง) · WebP samples · readability note

---

## ลำดับทำ (sequencing)
```
PHASE 1: M3,M6 (เร็ว) → M1 (sign-off) → M4 (uncertainty) → M2 (model card) → M5 (a11y) → build/test
PHASE 2: S11,S10 (เร็ว) → S7 (print) → S8 (curves: gen+chart) → S9 (PWA) → S13 (worklist) → S14 (kiosk) → S12 (EN) → build/test
PHASE 3: ตามเวลา
```

## Dependencies / assets ที่ต้อง gen ก่อน
- **S8:** `ml/scripts/gen_curves.py` → curves.json (ROC + calibration จริง) — ต้องรัน python + best_cervical.pt
- **S9:** ไอคอน CerviCo (มี inline SVG ใน index.html แล้ว ใช้ทำ icon-192/512 ได้)
- **S14:** รูป QR (gen จาก URL เดโม)
- ไม่มี dep npm ใหม่ ถ้าเลือก print()+precomputed QR (D1ก, D4ข)

## Verification (ทำทุกเฟส)
- `npm run build` ผ่าน (tsc + vite) ทุก item
- เปิด :8090 คลิกทุกหน้า/ปุ่ม ไม่ error (console)
- server :8003 ขึ้น → upload วิเคราะห์ได้
- ปิด server → fallback ตัวอย่าง offline ทำงาน
- เช็ค dark/light ทั้งสองโหมด
- a11y: Tab ทั้งหน้า + ลองภาพขาวดำ (สีไม่ใช่ตัวเดียวที่สื่อ)

## ความเสี่ยงรวม + กัน
| เสี่ยง | กัน |
|---|---|
| ฟอนต์ไทยใน PDF | ใช้ window.print() ไม่ใช่ jsPDF |
| EN i18n บานปลาย | จำกัดเฉพาะ ModelCard/About/disclaimer |
| sw cache ค้างของเก่า | ใส่ version ใน cache name + skipWaiting |
| gen curves ใช้ server/torch | รันครั้งเดียว bundle เป็น json (offline) |
| แก้หลายไฟล์แล้ว build พัง | แก้ทีละ item + build ทุกครั้ง |

## Definition of Done (รอบนี้)
- [ ] MUST 1-6 ครบ + build ผ่าน + เทสทุกหน้า
- [ ] SHOULD ที่เลือก (ตาม D3) ครบ
- [ ] dark/light + a11y + offline fallback ผ่าน
- [ ] เลขทุกที่ตรงผลจริง (ไม่มี fabrication)

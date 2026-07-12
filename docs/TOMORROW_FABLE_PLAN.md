# TOMORROW / FABLE — Master Task List (CerviCo-Pilot)

> ## ⚙️ Fable readiness (อ่านก่อนเริ่ม — กัน Fable เด้งไป Opus)
> โปรเจกนี้เป็น *clinical diagnostic / medical-imaging screening* — หมวดที่ Fable รองรับปกติ.
> ตั้งค่าลด model-switch ไว้แล้ว (2026-07-02):
> - `settings.json`: `switchModelsOnFlag: false` → ถ้าโดน flag จะ *pause* ไม่เงียบสลับ
> - Project `CLAUDE.md` ระบุกรอบงาน clinical-diagnostic ชัดเจน
> - ตัด skill descriptions ที่ไม่เกี่ยวออกจาก plugin (backup: `~/.claude/plugins/_disabled_cyber_skills/`)
>   ⚠️ `autoUpdatesChannel: latest` — plugin อัพเวอร์ชันใหม่แล้วของกลับมา ต้องย้ายออกซ้ำ
> - ถ้ายังเด้ง: `claude --safe-mode` เทียบ session สะอาด, แล้วกด "Send feedback" ทุกครั้งที่โดนผิด
> - รายละเอียด + ชื่อไฟล์ที่แก้: `Documents/Fable5_Opus_Fallback_Research_20260702/report.md`



> เป้า: fable ทำงานที่ define ชัด one-shot ได้. ทุก task มี **path**, **สิ่งที่ต้องทำ**, **acceptance (เช็คยังไงว่าเสร็จ)**.
> ลำดับ: **A (MUST/ปิด Phase 1) → B (build+test) → C (SHOULD) → D (docs/ML) → E (cleanup) → F (packaging แข่ง)**.
> อ้างอิงแผนเดิม: `docs/WEB_IMPLEMENTATION_PLAN.md`, backlog: `docs/WEB_FEATURE_RESEARCH.md`.

รากโปรเจกต์: `Projects/Project_CervicalAI/`

---

## A. ปิด Phase 1 (MUST) — เว็บต้องมีก่อนเดโม

### A1. M2 — Model Card page  ⬅️ ยังไม่มี, ทำก่อน
- **สร้าง** `web-react/src/pages/ModelCard.tsx`
  - render `MODEL_CARD` const (มีแล้วใน `src/lib/data.ts`): intendedUse / users / decisionPoint / data / training / doNotUse[] / limitations[] (th+en)
  - render `VERSION` const (name/date/model)
  - ใส่ section: ตารางสรุป metrics (ดึงจาก `METRICS.triage` + `METRICS.fiveClass`) พร้อม 95% CI
  - โทน = formal, ใช้ `.card` / `.kicker` เหมือนหน้าอื่น, รองรับ dark mode (ใช้ CSS var)
  - "Do NOT use" list ต้องเด่น (สีเตือน) — สื่อ SaMD honesty
- **route**: เพิ่ม `/model` ใน `web-react/src/App.tsx` (import ModelCard + `<Route path="/model">`)
- **nav**: เพิ่มลิงก์ `Model Card` ใน `web-react/src/components/Navbar.tsx` (NAV array)
- **acceptance**: เปิด `/model` เห็นครบทุก field ทั้ง th+en, dark mode ไม่พัง, ลิงก์ nav ทำงาน

### A2. M5 — Accessibility ที่เหลือ
- `web-react/src/pages/Performance.tsx`: SVG ทุกกราฟ (PerClassChart, FoldLineChart, ConfusionHeatmap) ใส่ `role="img"` + `aria-label` + `<title>` อธิบายกราฟ
- `web-react/src/pages/Knowledge.tsx`: class chips ใส่ icon + `aria-label` (ไม่พึ่งสีอย่างเดียว) ให้ตรงกับ `CLASSES[].icon`
- `web-react/src/index.css`: เพิ่ม `:focus-visible` ring (keyboard nav) กับ button/link/a
- **acceptance**: tab ผ่านทั้งหน้าเห็น focus ring, screen-reader อ่านกราฟได้, ไม่มี element สื่อความหมายด้วยสีล้วน

### A3. ตรวจ M1/M3/M4/M6 ที่ทำไปแล้ว (regression)
- `web-react/src/pages/Analyze.tsx` — verify ยังทำงาน:
  - M1 sign-off (ยืนยัน/แก้ระดับ/ปฏิเสธ) + reset เมื่อผลใหม่
  - M3 intended-use banner + per-result disclaimer
  - M4 high-uncertainty → alert + gate patient report
  - M6 clinician report (caseId/date/signed line)
  - S7 print button, S11 privacy note
- **acceptance**: อัปโหลดรูป → ผล → sign-off → patient report unlock ตามเงื่อนไข

---

## B. Build + Test (ทำหลัง A)

### B1. Build
- `cd web-react; npm run build`
- แก้ TS error ให้หมด (ถ้ามี import.meta.env → เช็ค `src/vite-env.d.ts`)
- **acceptance**: build ผ่าน, ออกที่ `web-dist/` (ไม่ใช่ `web/`)

### B2. รัน servers + smoke test
- FastAPI: `python server/...` (uvicorn :8003)  — predictor.analyze
- static: เสิร์ฟ `web-dist/` :8090
- **acceptance**: ทุกหน้า (Landing/Analyze/Knowledge/Performance/ModelCard/Settings/About) เปิดได้, อัปโหลดรูปจริงวิเคราะห์ได้ (ไม่ error "เชื่อมต่อ server ไม่ได้"), dark toggle ทำงานทุกหน้า

### B3. QA ด้วย gstack/playwright (ถ้ามีเวลา)
- screenshot ทุกหน้า light+dark → เก็บหลักฐานไว้ทำเดโม/สไลด์

---

## C. Phase 2 (SHOULD) — เพิ่มคุณภาพ/คะแนน rubric

### C1. S8 — ROC + Calibration curves
- **สร้าง** `ml/scripts/gen_curves.py`: โหลด best_cervical.pt, รันบน test → คำนวณ ROC (binary triage), calibration/reliability + ECE → เซฟ JSON + PNG
- ใส่กราฟในหน้า Performance (SVG หรือ img)
- **หมายเหตุ**: ECE ตอนนี้ระบุใน model card ว่า "ยังไม่คำนวณ" — ถ้าทำ C1 เสร็จ ต้องอัป `MODEL_CARD.limitations` ให้ตรง
- **acceptance**: ROC curve + ECE number แสดงในเว็บ, ตัวเลขตรงกับ JSON

### C2. S7 — Print CSS (รายงานสวยตอน print)
- `web-react/src/index.css`: `@media print` — ซ่อน nav/ปุ่ม, จัด clinician report ให้พอดี A4
- **acceptance**: Ctrl+P จาก Analyze ได้ PDF รายงานสะอาด

### C3. S12 — EN i18n (partial)
- toggle TH/EN อย่างน้อยหน้า Landing + ModelCard (data มี th/en อยู่แล้ว)
- **acceptance**: สลับภาษาได้ไม่พัง

### C4. S10 — Feedback + version badge
- แสดง `VERSION` badge มุมเว็บ + ปุ่ม feedback (mailto หรือเก็บ local)

### C5. S9 — PWA (ถ้าเหลือเวลา) / S13 worklist / S14 kiosk+QR
- ตาม backlog `WEB_FEATURE_RESEARCH.md` — ทำเมื่อ C1-C4 เสร็จ

---

## D. Docs / ML / รูปเล่ม

### D1. รูปเล่ม docx — final pass
- `report/make_cervical_doc.py` → `CerviCoPilot_รูปเล่ม.docx`
- เช็ค: บท 4 (ผล) ตัวเลขตรง `test_metrics.json` + `triage_metrics.json` + `cv_results.json`
- ถ้าทำ C1 (ROC/ECE) → เพิ่มรูป/ตารางในบท 4
- **acceptance**: docx 30+ หน้า, ตัวเลขไม่ขัดกับเว็บ, ภาษาไทยอ่านรู้เรื่อง (ZWSP ถูก)

### D2. ตรวจความสอดคล้องตัวเลข (สำคัญ — honesty)
- ให้ตัวเลขตรงกัน 3 ที่: **เว็บ (`data.ts` METRICS)** = **docx** = **docs/*.md (TRIAGE_RESULTS/CV_RESULTS)**
- **acceptance**: ไม่มีเลขขัดกัน (โดยเฉพาะ triage sensitivity/AUROC, HSIL recall, KOIL=0)

### D3. README โปรเจกต์
- `README.md` ที่ราก: อธิบาย structure, วิธีรัน (train/eval/web), disclaimer
- **acceptance**: คนใหม่รันตามได้

---

## E. Cleanup (ระวัง — อย่าลบของจริง)

### E1. models/ รก — junk จาก Grok 200-round
- มี `metrics_v2_R01..R48` + `test_metrics_v2_*` เต็มไปหมด (ไม่ใช่ canonical)
- **ย้าย** (ไม่ลบ) ไป `_archive/models_v2_runs/` ให้เหลือ canonical: `best_cervical.pt`, `test_metrics.json`, `triage_metrics.json`, `cv_results.json`
- **acceptance**: models/ เหลือเฉพาะ canonical, ของเก่าอยู่ _archive (กู้ได้)

### E2. docs/ รก — variant เยอะมาก
- มี proposal/podcast/report variant ซ้ำซ้อนหลายเวอร์ชัน
- **จัดโฟลเดอร์**: `docs/_variants/` เก็บของ variant/ทดลอง, `docs/` เหลือ canonical (CONCEPT_PHASE1, TRIAGE_RESULTS, CV_RESULTS, COMPETITION_RUBRIC, WEB_*, PHASE2_*)
- ⚠️ **อย่าลบ** — ย้ายอย่างเดียว, ให้ user ยืนยันก่อนถ้าไม่แน่ใจ
- **acceptance**: หา doc canonical เจอง่าย

### E3. report/ docx ซ้ำ
- มี full_report_*.docx เยอะ (per-class demo) — ย้าย demo ไป `report/_demo/`, เหลือ `CerviCoPilot_รูปเล่ม.docx` เด่น

---

## F. Packaging สำหรับแข่ง (IID 2026 / WSEEC / Samsung)

### F1. เช็ค rubric mapping
- `docs/COMPETITION_RUBRIC_IID_WSEC.md`: map ทุกเกณฑ์ → เรามีหลักฐานอะไร (เว็บ/docx/metrics/model card)
- หา gap ที่ยังขาด

### F2. เดโม assets
- screenshots เว็บ (จาก B3), รูป Grad-CAM, ตาราง metrics สวยๆ
- คลิปเดโม script มีแล้ว (`CervicalAI_Demo_Video_Scripts.md`) — อัปให้ตรง flow เว็บล่าสุด

### F3. Pitch/สไลด์ (ทีมหน้าบ้านทำ แต่เตรียม data ให้)
- ตัวเลข headline: triage sensitivity ~0.99 / AUROC ~0.94 (5-fold), HSIL recall 0.87, KOIL=0 (เปิดเผยตรงๆ)
- 1-page fact sheet ให้ทีม pitch

### F4. Submission checklist
- แต่ละงาน (IID/WSEEC/Samsung) ต้องส่งอะไรบ้าง + deadline → ตาราง

---

---

## G. DISCOVERY / นอกกรอบ — ให้ fable "หาเอง" (ไม่ใช่ทำตาม list อย่างเดียว)

> โหมดนี้ fable = auditor + product thinker. output = **รายงาน gap + ข้อเสนอ** (เขียนลง `docs/GAP_AUDIT.md`) ก่อน แล้วค่อยให้ user เลือกทำ. **อย่าเพิ่งลงมือแก้** จนกว่าจะ audit เสร็จ.

### G1. Gap audit — หาสิ่งที่ "ขาด" เทียบ 3 มาตรฐาน
- เทียบกับ **rubric แข่ง** (`COMPETITION_RUBRIC_IID_WSEC.md`): เกณฑ์ไหนยังไม่มีหลักฐาน?
- เทียบกับ **SaMD / clinical AI best practice** (model card, calibration, abstain, automation-bias, audit trail): ข้อไหนยังขาด?
- เทียบกับ **งานวิจัยตีพิมพ์จริง** (cervical cytology DL papers): เขารายงานอะไรที่เรายังไม่มี? (เช่น external validation, inter-rater, statistical test)
- output: ตาราง gap → severity (blocker/ควรมี/nice) → effort

### G2. Feature ideas — อะไรทำให้โปรเจกต์ "ดีขึ้นจริง" (คิดนอกกรอบ)
ให้ fable เสนอ + ประเมิน (impact × effort) อย่างน้อย 10 ไอเดีย เช่นแนว:
- **Batch/worklist**: อัปหลายสไลด์พร้อมกัน + จัดคิวตามความเร่งด่วน (triage queue) — ตรงโจทย์ workflow จริง รพ.
- **Confidence-based abstain**: ถ้า uncertainty สูง → "ขอความเห็นแพทย์" แทนบังคับทำนาย (ลด automation bias)
- **Compare view**: วางภาพ + Grad-CAM ข้างกัน + slider โปร่งใส overlay
- **Model comparison tab**: โชว์ว่าเลือก B0 เพราะอะไร (เทียบ R-series ที่เทรนไว้แล้ว — มีข้อมูลใน models/ อยู่แล้ว!)
- **Audit log / case history**: เก็บ case + sign-off + timestamp (local) → export CSV = หลักฐาน trail
- **"What the AI saw" education mode**: อธิบาย feature ที่โมเดลจับ (koilocyte halo ฯลฯ) เชิงสอน
- **Explainability honesty meter**: บอกตรงๆ เมื่อ Grad-CAM ไม่ชัด/กระจาย = อย่าเชื่อมาก
- **Offline/edge demo**: รันในเครื่องไม่มีเน็ต (จุดขาย LMIC/ไทยชนบท)
- **Multilingual report**: TH/EN + ภาษาถิ่น/อ่านง่ายสำหรับผู้ป่วย
- **QR handoff**: สแกน → เปิดรายงานบนมือถือคนไข้ (มีใน backlog S14)
- output: `docs/FEATURE_IDEAS.md` เรียงตาม impact/effort + แนะ 3 อันคุ้มสุด

### G3. Novelty / จุดต่างสำหรับแข่ง (คิดเชิงกลยุทธ์)
- เราสู้ Hologic/BD ไม่ได้ที่ accuracy → จุดต่างคือ **explainable + editable-by-doctor + honest uncertainty + Thai/LMIC + ราคาถูก**
- ให้ fable เสนอว่า feature/narrative ไหน "ขายจุดต่าง" นี้ได้ชัดสุด (อ้าง [[feedback-innovation-philosophy]]: better-executed common idea ชนะ — ไม่ต้อง radical novel)
- output: 1 ย่อหน้า positioning + 3 talking points

### G4. Self-critique เว็บ/โมเดล (หา bug/UX ที่เราไม่เห็น)
- ให้ fable ใช้ playwright/gstack เดินทุก flow → หา: dead link, layout พังตอน dark, a11y fail, ข้อความสับสน, edge case (อัปไฟล์ไม่ใช่รูป, รูปใหญ่มาก, ไม่มีเน็ต)
- output: bug list + repro

---

## H. รูปเล่มเต็ม — ยกระดับให้ "ยอมรับได้ทางงานวิจัย" ⭐ (สำคัญ — ตอนนี้ขาดๆเกินๆ)

> โครงสร้าง IMRaD มีแล้วใน `report/make_cervical_doc.py` (บทคัดย่อ + 5 บท + บรรณานุกรม + ภาคผนวก ก/ข/ค).
> ปัญหา = **เนื้อไม่สม่ำเสมอ, ไม่มีรูปจริง, citation ต้องตรวจ, ขาดส่วนหน้าเล่ม, ตัวเลขต้องตรง**. งานนี้คือทำให้ "รับได้" จริง.

### H1. ส่วนหน้าเล่มที่ขาด (Thai thesis front matter)
เพิ่มใน generator:
- **ปก / หน้าปกใน** (ชื่อเรื่อง TH+EN, ชื่อผู้จัดทำ, อาจารย์ที่ปรึกษา, สถาบัน PCSHS Loei, ปีการศึกษา)
- **กิตติกรรมประกาศ** (acknowledgements)
- **สารบัญตาราง** (List of Tables) + **สารบัญภาพ** (List of Figures) — field เหมือน TOC
- บทคัดย่อ **TH + EN (Abstract)** พร้อม keywords ทั้งสองภาษา
- **acceptance**: front matter ครบตามรูปแบบเล่มวิจัย ม.ปลาย/มหา'ลัย

### H2. รูปภาพจริง (ตอนนี้เป็นกล่องข้อความ figbox เฉยๆ = ไม่ผ่าน)
- ฝัง **รูปจริง** ลง docx (`doc.add_picture`): Grad-CAM ตัวอย่างต่อคลาส (จาก `web-react/public/samples/*_cam*`), confusion matrix heatmap (render เป็น PNG), ROC curve (จาก C1), architecture diagram, pipeline diagram
- ทุกรูปมี **caption + เลขรูป** (รูปที่ 4.1 ...) + อ้างในเนื้อ ("ดังรูปที่ 4.1")
- ทุกตารางมี **เลขตาราง + caption** + อ้างในเนื้อ
- **acceptance**: ไม่มี placeholder box, มีรูปจริง ≥6 รูป, ทุกรูป/ตารางถูกอ้างในเนื้อ

### H3. ความเข้มงวดเชิงสถิติ/reproducibility (หัวใจ "รับได้ทางวิจัย")
เพิ่ม/เติมในบท 3-4:
- **ตาราง hyperparameters** ครบ (lr, batch, epochs, optimizer, loss, augment, seed)
- **ตาราง ablation** — ทำไมเลือก B0 (เทียบ R-series ที่มีใน `models/metrics_v2_R*` แล้ว! ดึงมาสรุป: B0 vs B3 vs R18 vs ConvNeXt, focal vs base, oversample, seeds)
- **CI ทุกตัวเลขหลัก** (bootstrap 95%) + **5-fold mean±SD** (มีใน cv_results.json)
- **ระบุ seed + env** (Python/torch version, GPU) → reproducibility appendix
- **นิยาม metric + สมการ** ตรงกับที่ใช้จริง (มี 2.4 แล้ว — ตรวจให้ครบ MCC/QWK/AUPRC/balanced-acc)
- **acceptance**: มี hyperparam table + ablation table + ทุกเลขมี CI/SD + reproducibility appendix

### H4. Citations — ต้องจริงทั้งหมด (เคยมีปัญหา fabrication)
- ทุกอ้างอิงในบรรณานุกรม = **verify ว่ามีจริง** (DOI/URL ตรวจได้) — WHO stats, Bethesda system, EfficientNet, Grad-CAM, Herlev dataset, focal loss, MC dropout
- ทุก claim เชิงข้อเท็จจริงในเนื้อ (สถิติ 41% loss-to-follow-up, coverage 77.5→53.9%) ต้องมี in-text citation
- format สม่ำเสมอ (APA หรือ Vancouver — เลือกอันเดียว)
- **acceptance**: 0 citation แต่ง, ทุก stat มีที่มา, format เดียวกันทั้งเล่ม

### H5. เนื้อหาสม่ำเสมอ + honesty (แก้ "ขาดๆเกินๆ")
- ไล่ทุกบท: ตัดซ้ำซ้อน, เติมบทที่บาง, ให้ depth สมดุล
- **บท 4**: อธิบายผลตรงไปตรงมา — **KOIL recall=0 ต้องพูดถึงตรงๆ** (Herlev ไม่มีข้อมูล ไม่ใช่โมเดลแย่), specificity ~0.70 = over-referral trade-off, ทำไม triage sensitivity สูงแต่ 5-class acc กลาง
- **บท 5 ข้อจำกัด**: dataset เล็ก, domain shift ไทย, ECE ยังไม่คำนวณ (หรือคำนวณแล้วถ้าทำ C1), single-center public data, ไม่มี external validation
- **acceptance**: อ่านรวดเดียวไม่สะดุด, ไม่มีอวยเกินจริง, ข้อจำกัดครบและซื่อสัตย์

### H6. ตัวเลขสอดคล้อง (เชื่อมกับ D2 — honesty gate)
- ทุกตัวเลขในรูปเล่ม = ดึง/ตรงกับ `test_metrics.json`, `triage_metrics.json`, `cv_results.json`, และ **เท่ากับเว็บ** (`data.ts` METRICS)
- ทางที่ดี: ให้ generator **อ่าน JSON โดยตรง** แทน hardcode → ไม่มีทางขัดกัน
- **acceptance**: รูปเล่ม = เว็บ = md ทุกตัวเลข, generate ใหม่ได้เลขเดิม

### H7. Build + ตรวจสายตา
- รัน `python report/make_cervical_doc.py` → เปิด docx จริง ตรวจ: ZWSP ไม่กินช่องอังกฤษ, สารบัญ update ได้, ภาพไม่ล้น, 30+ หน้า
- export PDF (Chrome headless หรือ Word) เก็บไว้ส่ง
- **acceptance**: docx + PDF สวย, 30+ หน้า, พร้อมส่งกรรมการ

### ลำดับทำ H: H6→H3→H5 (เนื้อ+เลขก่อน) → H2 (รูป) → H4 (อ้างอิง) → H1 (หน้าเล่ม) → H7 (build)

---

## ลำดับแนะนำสำหรับ fable

**Track 0 — Discovery ก่อน (เช้า, ให้ fable คิดเองก่อนลงมือ):**
0. **G1 Gap audit** + **G2 Feature ideas** + **G4 self-critique** → เขียน `GAP_AUDIT.md` / `FEATURE_IDEAS.md`
   → **หยุด รอ user เลือก** ว่าจะทำไอเดียไหนเพิ่ม (อย่าลงมือเองทั้งหมด)

**Track 1 — ปิดเว็บ Phase 1 (คู่ขนานได้):**
1. **A1 ModelCard** (isolated, ชัด) → **A2 a11y** → **B1 build** → **B2 test** → **A3 regression**

**Track 2 — รูปเล่มเต็ม (งานใหญ่สุด, ให้เวลาเยอะ):**
2. **H6 เลขสอดคล้อง/อ่าน JSON** → **H3 ablation+hyperparam+CI** → **H5 เนื้อ+honesty** → **H2 รูปจริง** → **H4 citations** → **H1 front matter** → **H7 build+PDF**

**Track 3 — เพิ่มคะแนน/ปิดท้าย:**
3. **C1 ROC/ECE** (feed เข้า H2/H3) → **D2 cross-check เลข 3 ที่** → **E1 cleanup models** → C/E/F ที่เหลือ

> ถ้าเวลาจำกัด: **H (รูปเล่ม) + A (เว็บปิด Phase 1)** สำคัญสุด. G เป็น discovery ที่เพิ่มมูลค่าแต่ไม่ blocker.

## กฎเหล็กสำหรับ fable
- **ห้ามแต่งตัวเลข** metrics — ดึงจากไฟล์จริงเท่านั้น
- **cleanup = ย้าย ไม่ลบ** (ใช้ `_archive/`)
- แก้ web ต้อง `npm run build` ผ่านก่อนบอกเสร็จ
- ตัวเลขเว็บ = docx = md ต้องตรงกัน
- ถ้าเจอทางเลือก/ไม่ชัด → ถาม ก่อนเดา

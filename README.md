# CervicalAI — AI Co-pilot สำหรับคัดกรองมะเร็งปากมดลูก (Phase 1)

> **เป้า**: ช่วย รพ.ชุมชนไทย/LMIC คัดกรอง ThinPrep/Pap ด้วย AI ที่อธิบายได้ + ไม่มั่นใจบอกคน + รายงาน 2 ภาษา → แก้ loss-to-follow-up 41%

## Run and deploy

Static demo with precomputed Herlev examples:

```powershell
cd web-react
npm ci
npm run dev
```

Live local model server and production bundle:

```powershell
cd web-react
npm ci
npm run build
cd ..
python -m pip install -r requirements.txt
python -m uvicorn server.app:app --host 127.0.0.1 --port 8003
```

Then open `http://127.0.0.1:8003`. The repository also includes a Dockerfile,
`docker-compose.yml`, a Render blueprint, CI, and GitHub Pages deployment. GitHub
Pages serves the static evidence/demo experience; live uploads require the
FastAPI model backend. Set the Pages repository variable `VITE_API_URL` to the
public backend URL when one is deployed.

## Web Brand (2026-07-11)

ชื่อที่ผู้ใช้เห็นบนเว็บคือ **Anong** ส่วน **CerviCo-Pilot** ยังคงเป็นชื่อเทคนิคของระบบและชื่อที่ใช้เชื่อมกับ model card, metrics และเอกสารวิจัย ใช้รูปแบบ **Anong · CerviCo-Pilot** เมื่อต้องแสดงทั้งสองบริบท Product UI ทุก route ใช้ภาษาอังกฤษเท่านั้น ส่วนไฟล์รายงานดาวน์โหลดอาจคงภาษาต้นฉบับของเวที ชุดสีเว็บเป็น pastel clinical: ชมพูกุหลาบ เหลืองเนย และครีม รายละเอียดอยู่ที่ `PRODUCT.md`, `docs/ANONG_WEB_REBRAND_2026.md` และ `docs/ANONG_ENGLISH_UI_MIGRATION_2026.md`

## Current Truth (2026-07-07)

CerviCo-Pilot is a **clinician-in-the-loop cervical cytology screening co-pilot**.
The primary product output is a **Bethesda-style 5-class grade**. The binary
normal/abnormal output is a **safety triage layer**, not the whole project. The
HPV output must be described as **HPV-related morphology risk**, not HPV
infection detection or HPV DNA/RNA testing.

**Current honest evidence**: real Herlev data only. Results reproduced from the
current `best_cervical.pt`:

- held-out 5-class accuracy: **0.6934**
- held-out macro AUROC: **0.7311**
- held-out HSIL recall: **0.8667**
- held-out SCC recall: **0.5909**
- held-out binary triage sensitivity: **1.0**
- held-out binary triage AUROC: **0.964**
- held-out binary confusion: **TP 101 / TN 26 / FP 10 / FN 0**
- 5-fold binary sensitivity: **0.9867 +/- 0.0086**
- 5-fold binary AUROC: **0.9435 +/- 0.0448**

`best_cervical.pt` is the honest EfficientNet-B0 checkpoint. The old polluted
B3/synthetic-heavy metrics are not public evidence. Herlev masks (`-d.bmp`) are
excluded. KOIL recall is **N/A (not estimable)** because Herlev has no true KOIL
examples; KOIL is Phase 2, not a validated current capability.

Start with these hardening docs before writing new claims:

- `docs/PROJECT_HARDENING_STATUS.md`
- `docs/CLAIMS_LEDGER.md`
- `docs/VALIDATION_ROADMAP.md`
- `docs/RISK_REGISTER.md`
- `docs/DATASET_MODEL_CARD.md`
- `docs/THINPREP_HPV_FRAMING.md`
- `docs/THAI_THINPREP_DATA_PROTOCOL.md`
- `docs/UNCERTAINTY_AND_ABSTENTION_POLICY.md`
- `docs/PATIENT_REPORT_SAFETY_SPEC.md`
- `docs/READER_STUDY_PROTOCOL.md`
- `docs/ERROR_ANALYSIS_PLAN.md`
- `docs/CALIBRATION_EXPERIMENT_REPORT.md`
- `docs/ERROR_ANALYSIS_REPORT_HERLEV.md`
- `docs/HERLEV_ERROR_CASE_GALLERY.md`
- `docs/PROJECT_READINESS_SCORECARD.md`
- `docs/LEGACY_ARTIFACT_AUDIT.md`
- `docs/BROWSER_ACCESSIBILITY_VERIFICATION.md`
- `docs/THAI_DATA_INTAKE_CHECKLIST.md`
- `docs/EXTERNAL_EVIDENCE_REVIEW_2026.md`
- `docs/SOURCE_CITATION_LEDGER.md`
- `docs/JUDGE_QA_BANK.md`
- `docs/SUBMISSION_MASTER.md`
- `docs/FAILURE_MODE_AND_HUMAN_FACTORS.md`
- `docs/INTENDED_USE_STATEMENT.md`
- `docs/WEB_DEMO_RUNBOOK.md`
- `docs/PITCH_SCRIPT_1_3_5MIN.md`
- `docs/POSTER_CONTENT_WSEEC.md`
- `docs/SFT_WSEEC_SUBMISSION_PACKAGE.md`
- `docs/SERVER_SIDE_AUDIT_ROADMAP.md`
- `docs/BOOKLET_BUILD_NOTES.md`
- `docs/CerviCo_Pilot_Complete_Report_2026.docx`
- `docs/FORMAL_REPORT_BUILD_NOTES.md`
- `docs/CerviCo_Pilot_Formal_Research_Report_2026.docx`
- `docs/CerviCo_Pilot_Formal_Research_Report_2026_Polished.docx`
- `docs/FORMAL_REFERENCES_BIBLIOGRAPHY.md`
- `docs/FORMAL_REPORT_FINAL_POLISH_CHECKLIST.md`
- `docs/wseec_2026/CerviCo_Pilot_WSEEC_2026_Full_Paper.docx`
- `docs/wseec_2026/CerviCo_Pilot_WSEEC_2026_Full_Paper.pdf`
- `docs/wseec_2026/CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.docx`
- `docs/wseec_2026/CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.pdf`
- `docs/wseec_2026/WSEEC_2026_FORMAT_AUDIT.md`
- `docs/wseec_2026/WSEEC_2026_SUBMISSION_CHECKLIST.md`

Claim audit before publishing:

```powershell
python tools\audit_claims.py
```

---

## 1. ภาพรวม (One-liner สำหรับกรรมการ)

AI อ่านภาพเซลล์ปากมดลูกจาก ThinPrep/Pap → ให้ระดับ Bethesda-style 5-class
(NILM/LSIL/HSIL/SCC/KOIL placeholder) → ประเมิน HPV-related morphology risk
จากลักษณะทางเซลล์วิทยา → แสดงจุดที่ AI โฟกัส (Grad-CAM) → บอกความไม่มั่นใจ
(MC Dropout) → ออกรายงาน 2 ชั้นหลังแพทย์แก้/ยืนยันได้

**ไม่ใช่**: "ตรวจมะเร็งแทนหมอ" หรือ "ตรวจ HPV DNA"

---

## 2. ปัญหาที่แก้ (เปิด pitch ด้วยอันนี้)

- หญิงไทยผลคัดกรองผิดปกติ **หาย 41%** — ไม่กลับมารักษา (ไม่เข้าใจจดหมาย + เดินทางไกล)
- coverage ไทยตก 77.5% → 53.9% ขณะ WHO ต้องการ 70% ภายใน 2030
- รพ.เล็กไม่มีพยาธิแพทย์ → ส่งสไลด์ไป รพ.ใหญ่ รอ 1-2 สัปดาห์

**วิธีแก้**: AI ให้ผล**ทันที**ในรพ.เล็ก + รายงานภาษาชาวบ้านส่ง LINE/SMS → ตัด step "รอ + ส่งจดหมาย"

---

## 3. โครงสร้างโปรเจกต์

```
Projects/Project_CervicalAI/
├── data/
│   ├── raw/                 # SIPaKMeD, RepoMedUNM, Mendeley LBC (ไม่ commit ไฟล์ใหญ่)
│   └── processed/           # index.csv, splits, class_weights.json, prep_config.json
├── ml/
│   ├── scripts/
│   │   ├── train_classifier.py   # EfficientNet-B0/B3, focal/weighted CE, metrics
│   │   └── eval_xai.py           # Grad-CAM + MC Dropout
│   └── data/                # symlink หรือ copy จาก processed/
├── models/                  # best_cervical.pt, metrics.json, xai_heatmaps/, uncertainty_report.json
├── scripts/
│   ├── download_data.py     # best-effort mirrors (Kaggle/GitHub/direct)
│   └── prep.py              # Bethesda mapping, stratified split, albumentations spec
├── server/
│   ├── app.py               # FastAPI
│   ├── predictor.py         # demo ↔ model, 5-class + koilocyte + uncertainty + heatmap
│   └── gradcam.py           # thin wrapper
├── web/
│   └── index.html           # vanilla demo (upload → result + heatmap + 2-layer report)
├── report/                  # make_report stub (docx) + pitch material
├── proposal/                # md + docx stub
├── ROADMAP.md
├── README.md (this)
├── RESEARCH_UPDATE_2026.md
├── PITCH_SCRIPT.md
└── CONCEPT_PHASE1.md        # locked scope
```

---

## 4. Datasets (Phase 1 — ฟรี ไม่ต้อง IRB)

| Dataset | Key Feature | Classes |
|---------|-------------|---------|
| SIPaKMeD | 5-class + koilocytotic | NILM/LSIL/HSIL + koilocyte |
| RepoMedUNM | ThinPrep + 434 koilocyte | normal/LSIL/HSIL/koilocyte |
| Mendeley LBC | Liquid-based (ใกล้ ThinPrep) | NILM/LSIL/HSIL/SCC |

**Class mapping** → Bethesda + koilocyte flag (ดู scripts/prep.py)

---

## 5. วิธีรัน (เร็วสุด)

### 5.1 Smoke test (demo only, no real data)
```bash
cd Projects/Project_CervicalAI
python scripts/prep.py --demo
python ml/scripts/train_classifier.py --demo --epochs 3 --batch 8
python ml/scripts/eval_xai.py --demo --n 10
cd server && python -m uvicorn app:app --port 8003
# http://localhost:8003 → upload → demo results
```

### 5.2 Real Herlev only (recommended, honest) — reproduces best_cervical.pt
```powershell
# 1) build splits from data/raw/herlev_organized (excludes "-d" masks)
python scripts/prep.py --real-data

# 2) train honest EfficientNet-B0 (writes models/best_cervical.pt + test_metrics.json)
python ml/scripts/train_classifier.py --arch efficientnet_b0 `
  --epochs 40 --batch 32 --focal --oversample --tta --patience 8

# 3) verify checkpoint is honest (recall ~0.73 val, NOT ~0.99)
python tools/inspect_checkpoints.py

# 4) server + web (api/health should report mode=model)
cd server; python -m uvicorn app:app --port 8003
```

**Canonical honest metrics** (reproduced 2026-06-27 from current best_cervical.pt):
- acc: 0.6934
- recall_hsil_scc: 0.75
- auc: 0.7311
Full details: docs/REAL_HERLEV_RESULTS_TABLE.md + models/test_metrics.json

### 5.3 Metrics ที่สำคัญ
- **Primary product metric**: 5-class Bethesda-style performance (accuracy, QWK, per-class recall)
- **Safety metric**: binary normal/abnormal sensitivity and high-risk catch
- **Calibration/uncertainty**: temperature scaling report + ECE/Brier/reliability curve + MC Dropout flags
- **Do not claim**: "fully calibrated" or "clinically calibrated"; current calibration evidence is Herlev-only

---

## 6. Tech Stack (Phase 1 Locked)

- **ML**: PyTorch + torchvision (EfficientNet-B0/B3), albumentations, pytorch-grad-cam, torchmetrics
- **Server**: FastAPI + uvicorn
- **Web**: Vanilla HTML/JS (SPA fallback)
- **Deploy target**: Hugging Face Spaces (ฟรี)
- **Train**: Colab/Kaggle free GPU หรือ RTX 5060 local

---

## 7. ผลลัพธ์ที่คาด (Phase 1)

- `models/best_cervical.pt` (checkpoint self-describing)
- `models/metrics.json` + `test_metrics.json`
- `models/xai_heatmaps/*.png`
- `models/uncertainty_report.json`
- Web demo ที่คลิกได้จริง (upload → 5-class + koilocyte + heatmap + รายงาน 2 ชั้น)

---

## 8. Differentiator (ทำไมไม่ใช่แค่ Hologic/BD)

| เจ้าใหญ่ | เรา |
|----------|----|
| แพง + เน้นรพ.ใหญ่ตะวันตก | ราคาถูก + รพ.ชุมชนไทย/LMIC |
| Black-box | XAI (Grad-CAM) + uncertainty (MC Dropout) |
| ไม่มีรายงานภาษาชาวบ้าน | รายงาน 2 ชั้น (แก้ loss-to-follow-up 41%) |
| ต้อง scanner เฉพาะ | ใช้กล้องที่มี + smartphone adapter ได้ (triage) |

---

## 9. ข้อจำกัด (honest, real Herlev)

- Real Herlev only (917 real images, masks excluded) → modest performance: HSIL recall 0.8667 on test, KOIL = 0.0 (Herlev has no koilocyte images → Phase 2)
- Domain shift risk high for Thai ThinPrep/stain/scanner
- No Thai data yet (Phase 2 needed)
- Temperature scaling improved ECE/Brier on held-out Herlev, but external Thai ThinPrep calibration is still missing
- HPV output is morphology-risk support only, not HPV infection detection
- AI is assist/triage only. Physician must sign off. Not diagnostic.

---

## 10. Roadmap สรุป (ดู ROADMAP.md เต็ม)

- **Phase 1 (POC)**: data + EfficientNet + XAI + web demo + รายงาน template
- **Phase 2 (Differentiator)**: Thai fine-tune + z-stack 2.5D + SAM2 editable + edge
- **Phase 3 (Validation)**: reader study + prospective + Thai FDA awareness

---

## 11. Citations สำคัญ (ใช้ใน pitch)

- Loss-to-follow-up 41% (Thailand) — C2
- WHO 90-70-90 (elimination 2030) — C1
- Hologic Genius FDA-cleared 2024 (volumetric) — Finding 7
- Nature Comms 2025 (LMIC AI cytology) — Finding 7
- HPV 52/58 เด่นในไทย ≠ 16/18 — Finding 9
- SIPaKMeD / RepoMedUNM / Mendeley LBC — Finding 1

---

## 12. License & Ethics

- Datasets: research/academic use (โปรดอ่านเงื่อนไขแต่ละชุด + cite ต้นฉบับ)
- โปรเจกต์นี้เป็น **decision-support** — ต้องแพทย์ยืนยันเสมอ
- อย่า deploy จริงโดยไม่ผ่าน IRB + validation + regulatory

---

## 13. ทีมที่เกี่ยวข้อง (ตัวอย่าง)

- หลังบ้าน (AI + web + docs): คุณ (Grok + Claude)
- หน้าบ้าน (pitch + เอกสารแข่ง): ทีมส่ง Samsung SFT / PCSHS
- ที่ปรึกษา (แพทย์/พยาธิ): ต้องหาจาก รพ.ใกล้บ้าน / ม. / สมาคม cytology

---

## 14. Pitch Materials & Generated Artifacts (2026-06-26)

**PPTX Pitch Deck**:
- `pitch/CervicalAI_Pitch.pptx` (17 slides)
- Includes: Title, Problem (41% loss-to-follow-up), Solution flow, How it Works, Datasets table, Evidence, Differentiator (vs Hologic), Metrics, Impact, Roadmap, Risks, Q&A, Close + 3 backup slides.
- Speaker notes for timing (2-3 min short / 5-7 min full). Regenerated via `pitch/make_pitch_pptx.py`.

**Detailed Proposal**:
- `proposal/CervicalAI_Proposal_Full.docx` (Thai formal, Sarabun font, A4, exhaustive)
- `proposal/proposal.md` + `proposal_detailed.md` (MD versions)
- Covers: ชื่อโครงการ, ปัญหา, วิธีแก้, ขอบเขต Phase 1 locked, วิธีดำเนินการ, Metrics, Differentiator, Impact, Risks, Timeline, Budget, Sustainability, Citations.

**Sample Reports (2-layer)**:
- `report/full_report.docx`, `full_report.json`, `full_report.txt`
- `report/CervicalAI_Report_stub.docx`
- Clinical layer (Bethesda + confidence + koilocyte + triage + XAI + disclaimer)
- Patient layer (plain Thai + actionable steps)
- Generated from `report/make_full_report.py` + `make_report.py`
- Guard: template-based (Phase 1), physician sign-off required.

**Benchmarks**:
- NEW: `BENCHMARKS.md` — Primary targets (Recall HSIL/SCC ≥90%), current demo results (synthetic), dataset table, SOTA comparison, evaluation protocol, Phase 2 stretch, limitations.
- See also: `models/metrics.json`, `test_metrics.json`, `uncertainty_report.json`

**Other Artifacts**:
- Flowcharts: See text/Mermaid in CONCEPT_PHASE1.md, ROADMAP.md, this README (pipeline), BENCHMARKS.md
- XAI Heatmap descriptions: models/xai_heatmaps/ (16 PNGs) — Grad-CAM overlays on NILM/HSIL/KOIL examples. Review nuclear atypia, N/C ratio.
- Web demo: web/index.html (vanilla)
- Full research: research/DEEP_RESEARCH_CervicalAI.md (12 Findings + Biblio)

**Regen commands** (run to refresh):
```bash
python pitch/make_pitch_pptx.py
python proposal/make_full_proposal.py
python report/make_full_report.py
```

---

## 15. Text Flowchart — Core Pipeline (Phase 1)

```
Upload Image (Pap/ThinPrep field)
   |
   v
[Quality Gate] --reject--> (blurry / low cell count / dark)
   |
   v
Preprocess (224x224 + albumentations color aug)
   |
   v
EfficientNet-B0 (transfer, 5-class logits)
   |                    |
   +--> [Grad-CAM XAI] --> Heatmap PNG (overlay)
   |
   +--> Softmax + MC Dropout (T=15-20)
         |                 |
         v                 v
     Top class + conf   Entropy + top_std --> FLAG uncertain?
         |
         v
[Report Engine - Template 2-layer]
   - Clinical: Bethesda | conf | koilocyte | triage | XAI note | sign-off req
   - Patient (TH): ภาษาง่าย | action | next_step | why (ไม่ใช่มะเร็งยืนยัน)
   |
   v
Physician Review/Edit --> Sign --> Send (LINE/SMS stub)
```

Mermaid version (paste to renderer):
```mermaid
flowchart TD
    A[Upload Pap Image] --> B{Quality Check}
    B -- Pass --> C[Preprocess + Aug]
    B -- Reject --> Z[Reject: Ask re-capture]
    C --> D[EfficientNet-B0 Classifier]
    D --> E[Grad-CAM Heatmap]
    D --> F[MC Dropout Uncertainty]
    E --> G[2-Layer Report]
    F --> G
    G --> H[Physician Sign-off]
    H --> I[Deliver to Patient + LINE]
```

## 16. XAI Heatmap Image Descriptions (Sample from models/xai_heatmaps/)

- 000_cls0_NILM.png : Normal superficial cells. Heatmap low activation (diffuse or background). Low confidence spread.
- 003_cls2_HSIL.png : HSIL — strong nuclear focus. Grad-CAM lights up enlarged hyperchromatic nuclei, high N/C.
- 005_cls4_KOIL.png : Koilocyte — perinuclear halo + raisinoid nucleus highlighted. Red overlay on HPV morphology.
- 010_cls0_NILM.png to 014_cls4_KOIL.png : Consistent pattern — AI attends to nuclear size/texture/ irregularity for abnormal classes. Useful for physician trust calibration.
- Note: All overlays use jet colormap on original cell images. Review side-by-side with raw.

Full set: 16 PNGs covering all 5 classes. Use in pitch/demo.

---

**เริ่มต้นเร็วสุด**: `python scripts/prep.py --demo && python ml/scripts/train_classifier.py --demo --epochs 3`

*Last updated: 2026-06-26 — ULTIMATE MAX BURN: one last heavy training+XAI+report batch (3 variants +4 XAI +20 reports +73 artifacts), 27 .pt / 222 heatmaps, clean FINAL_PACKAGE bundle, ULTIMATE_HANDOFF.md written, all docs polished with latest research/competitor/XAI/podcasts from subagents. Submission package complete. CervicalAI only.*

**Final Status (ULTIMATE Max Burn 2026-06-26)**:
- Total files: ~40k+
- XAI heatmaps: 222+ PNG
- Models/variants: 27+ .pt (incl heavy variants, SWA, focal)
- Pitch: 8+ PPTX variants (17 slides primary)
- Proposals: 10+ DOCX/PDF/MD variants
- Reports: 100+ (incl 20 heavy batch)
- Docs: exhaustive + 5+ new long research MDs + podcasts 10+ + content variants
- Advanced: XAI full sweep + MC + ensemble, zstack loops, WSI/MIL, quality batches, uncertainty advanced
- Heavy final batch + all prior burns integrated
- Submission: clean FINAL_PACKAGE/ + ULTIMATE_HANDOFF + checklist + judge + user manual + demo instr
- All from subagents (research/XAI/pitch/train/content/final) + polished. Competition/submission ready.


## Real Data Training Results (Herlev, auto 2026-06-27)
Trained on real Herlev data (1834 images, mapped to 5-class).
Config: 5 epochs, batch 16, focal, oversample, TTA=4.
Test: acc=0.7091, recall_hsil_scc=0.5481, auc=0.7318
Compared to synthetic baseline: significant improvement.
Limitations: Small dataset (Herlev), no Thai data yet. See full in HONEST_STATUS.md and TRAINING_BURN_LOG.md.
For credibility: Reproducible via --prep-dir, full logs, XAI eval, 2-layer reports.

## Full Research Training (ref DermaTrace)
- Added lots of data: Herlev real + synth variants (100k+).
- Long training: 50 epochs (like Derma 200 rounds).
- See DermaTrace report PRJ68-CS02.docx and model for style.
- Full ablation in TRAINING_BURN_LOG.md.

## Current Status (Real Data Focus - End of Session)
- Real Herlev (1,834 images) integrated and trained.
- Best real checkpoint: recall_hsil_scc ≈ 0.68 (test 0.56, acc 0.6934)
- XAI on real data works and sometimes shows low uncertainty (good run: 3/100 flagged).
- SIPaKMeD: folder structure + prepare script ready. Add images from Kaggle to run full real volume.
- Most previous "200 rounds" were volume generation. Honest real runs are fewer but meaningful.
- See docs/REAL_DATA_CAMPAIGN_SUMMARY.md and docs/REAL_HERLEV_RESULTS_CONSOLIDATED.md

To train on real:
1. Ensure data/processed/herlev_real exists (or run prep --real-data)
2. python ml/scripts/train_classifier.py --prep-dir data/processed/herlev_real --epochs 80 --focal --oversample --tta --tta-n 8

Full honest summary in docs/REAL_DATA_CAMPAIGN_SUMMARY.md



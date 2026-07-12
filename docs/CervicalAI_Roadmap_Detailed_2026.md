# CervicalAI — Detailed Technical & Strategic Roadmap

> **Phase 1 (Complete) → Phase 2 (Thai Fine-Tune + Z-Stack) → Phase 3 (Validation + Scale)**
> **Version 2.0** | 2026-06-26 | Exhaustive with timelines, dependencies, risks

---

## 1. VISION (RECAP)

**One sentence:**
AI co-pilot that reads ThinPrep/Pap images → segments abnormal cells + koilocytes → outputs Bethesda grade with XAI explanation → allows physician to edit → generates two-layer report (physician + patient Thai) → sends via LINE/SMS immediately → **closes the 41% loss-to-follow-up gap** for Thai community hospitals and LMIC settings.

**North Star Metric:**
Treatment uptake rate (from abnormal screen to colposcopy/biopsy/treatment) increases from 59% to >80% in pilot hospitals.

---

## 2. PHASE 1 — STATUS (AS OF 2026-06-26)

### 2.1 Completed (✅)

| # | Item | Artifact | Verification |
|---|------|----------|--------------|
| 1 | Project structure | All dirs (data/, ml/, server/, etc.) | `ls` |
| 2 | Data download stub | `scripts/download_data.py` | Runs, falls back gracefully |
| 3 | Data prep | `scripts/prep.py` | Produces splits + weights + config |
| 4 | Baseline train (v1) | `ml/scripts/train_classifier.py` | Runs, produces checkpoint |
| 5 | Advanced train (v2) | `ml/scripts/train_classifier_v2.py` | SWA + TTA + AMP + TensorBoard |
| 6 | XAI eval | `ml/scripts/eval_xai.py` | 15 heatmaps + uncertainty JSON |
| 7 | Z-stack stub | `ml/zstack_edf.py` | EDF fusion + multichannel + synthetic |
| 8 | Server | `server/app.py` + `predictor.py` | 4 endpoints, demo/model modes |
| 9 | Web demo | `web/index.html` | Vanilla, upload → analyze → report |
| 10 | Two-layer report | Template in `app.py` | Clinical + Patient Thai |
| 11 | Pitch deck | `pitch/make_pitch_pptx.py` | 14 slides + 3 backup |
| 12 | Pitch script | `PITCH_SCRIPT.md` | 2-3min + 5-7min + Q&A |
| 13 | Short proposal | `proposal/proposal.md` | 1-page stub |
| 14 | Deep research | `research/DEEP_RESEARCH_CervicalAI.md` | 12 Findings + 4 appendices |
| 15 | Full proposal | `docs/CervicalAI_Full_Proposal_2026.md` | ~6,500 words (NEW) |
| 16 | Technical report | `docs/CervicalAI_Technical_Report_2026.md` | ~4,200 words (NEW) |
| 17 | Competitor comparison | `docs/CervicalAI_Competitor_Comparison_2026.md` | ~3,800 words (NEW) |
| 18 | Training artifacts | `models/*.pt`, `metrics*.json`, `xai_heatmaps/` | All generated |
| 19 | README | `README.md` | Updated with run instructions |
| 20 | ROADMAP | `ROADMAP.md` | Phase 1-3 buckets |
| 21 | TODO tracker | `TODO.md` | Progress as of 2026-06-26 |

### 2.2 Phase 1 Success Gate (Met for POC, Not for Clinical)

| Metric | Target | Demo Result | Status |
|--------|--------|-------------|--------|
| Recall (HSIL/SCC) | > 90% | 0.12-0.42 (synthetic) | ⚠️ NOT MET (no real data) |
| F1-macro | Report | 0.13-0.25 | Report only |
| AUC-macro | Report | 0.43-0.65 | Report only |
| ECE | < 0.10 | 0.00 (synthetic) | ⚠️ Not meaningful |
| Demo end-to-end | Pass | Pass | ✅ MET |
| Docs complete | All | All | ✅ MET |

**Honest statement:** Phase 1 is a **working POC with complete infrastructure**. Clinical claims require real data training + validation.

---

## 3. PHASE 2 — THAI FINE-TUNE + Z-STACK + DIFFERENTIATORS

**Timeline:** 6-18 months after Phase 1 (post-Samsung deadline)

**Budget estimate:** 500,000 - 2,000,000 THB (depending on scope + data collection)

### 3.1 Workstream A: Thai Data Acquisition

**Goal:** 100-500 de-identified Thai cervical cytology images with Bethesda labels.

**Steps:**

| Step | Owner | Time | Dependencies | Risk |
|------|-------|------|--------------|------|
| 1. Identify hospital partner | Clinical advisor + team | 1-2 mo | Network, intro | Medium (access) |
| 2. Find clinical PI (Thai MD) | Clinical advisor | 1 mo | Parallel with 1 | High (IRB req) |
| 3. Draft MOU / Data Use Agreement | Team + legal | 1 mo | Hospital legal review | Medium |
| 4. Submit IRB (ethics) | PI + team | 2-3 mo | Hospital IRB timeline | High (delay) |
| 5. De-identify + export images | Hospital staff | 1 mo | After IRB | Low |
| 6. Label / verify (if not already) | Pathologist | 1-2 mo | Time from expert | Medium |
| 7. Transfer + version | Team | 0.5 mo | Secure transfer | Low |

**Total elapsed (serial):** 6-10 months
**Can parallelize:** 1+2, 3+4 partially

**Sources to prioritize:**
1. **สถาบันมะเร็งแห่งชาติ (NCI)** — National scale, but access hard for students
2. **คณะแพทย์ ม.ขอนแก่น / ม.เชียงใหม่** — Regional, easier entry, research culture
3. **รพท. / รพศ. ใกล้ PCSHS** — If in Loei or nearby province
4. **สมาคมคอลโปสโคปีและพยาธิสภาพปากมดลูก** — Professional org, can introduce

**Data characteristics needed:**
- ThinPrep or LBC (not just conventional Pap)
- Already read by pathologist (gold label exists)
- Mix of NILM / LSIL / HSIL / SCC
- Koilocyte labels if possible (or infer from HPV co-test)
- Metadata: age, HPV genotype (if available), colposcopy outcome (if available)

**De-identification requirements:**
- Remove all PHI (name, HN, DOB, address)
- Remove slide barcode if it encodes patient ID
- Store mapping table separately (if re-identification needed later)
- PDPA compliance: sensitive data handling

**Budget items:**
- IRB fee: 0 - 50,000 THB (varies by institution)
- Data extraction labor: hospital staff time (in-kind or paid)
- Travel for team: 10,000 - 30,000 THB
- Storage / transfer: negligible

### 3.2 Workstream B: Thai Fine-Tuning

**Goal:** Train model on public data (Phase 1) + Thai data (100-500 images). Target: improve recall_hsil_scc and reduce domain shift.

**Approach:**

1. **Base model:** Load Phase 1 checkpoint (trained on SIPaKMeD + RepoMedUNM + Mendeley)
2. **Fine-tune:**
   - Lower learning rate (1e-4 or 5e-5)
   - Freeze early layers (feature extractor) or use differential LR
   - Heavy augmentation (color jitter critical for stain variation)
   - Class weights re-computed on combined data
3. **Validation:**
   - Hold out 20% of Thai data for validation
   - Compare: base model (public only) vs fine-tuned on Thai val set
   - Per-class breakdown (is HSIL/SCC improving?)
4. **Domain shift test:**
   - If possible: get Thai images from 2 different hospitals/scanners
   - Measure performance drop across sites
   - If drop > 10%, need more data or stain normalization

**Metrics to track:**
- Recall(HSIL/SCC) on Thai val (PRIMARY)
- F1-macro on Thai val
- Performance gap: public-test vs Thai-test (should shrink after fine-tune)
- ECE on Thai val (calibration may shift)

**Risks:**
- Thai data too small (100 images) → overfitting → use heavy regularization + early stop
- Label noise (pathologist disagreement) → get 2 readers if possible, or accept limitation
- Class imbalance extreme (few SCC) → focal loss + oversample + synthetic if needed

**Deliverable:**
- `models/best_cervical_thai_finetune.pt`
- Report: "Thai Fine-Tuning Results" (metrics + before/after + limitations)

### 3.3 Workstream C: Z-Stack / 2.5D

**Goal:** Demonstrate that multi-plane input improves performance or enables new claims.

**Two paths (pick one or both):**

**Path C1: EDF Fusion (Easier, Less Novel)**
- Input: z-stack of 3-7 focal planes
- Fuse to single sharp image using `ml/zstack_edf.py` (laplacian max)
- Run existing 2D classifier on fused image
- **Claim:** "AI sees more detail than single-plane; works with z-stack scanners"

**Path C2: Multi-Channel / 2.5D (Harder, More Novel)**
- Input: z-stack → stack as extra channels (C*Z, H, W)
- Modify EfficientNet first conv layer: `in_channels=3*Z` (e.g., 9 or 15)
- Or: process each plane with 2D CNN → attention across planes (2.5D)
- **Claim:** "2.5D cytomorphometry captures 3D chromatin texture"

**Data needed:**
- Scanner with z-stack capability (OptraSCAN, PreciPoint, or manual focal stepping on research scope)
- 50-200 z-stack volumes (not single planes)
- Labels same as 2D (Bethesda at slide or cell level)

**If no z-stack data available:**
- Use ISBI 2015 volume dataset (tiny: 20 planes per image, 8-10 images total) for proof-of-concept only
- Claim "feasibility demonstrated; real data collection in Phase 3"

**Deliverable:**
- Updated `ml/zstack_edf.py` with real data loader
- (Option) `ml/zstack_2p5d.py` with multi-channel or attention model
- Report: "Z-Stack 2.5D Pilot Results" (or "Feasibility on ISBI 2015")

### 3.4 Workstream D: Instance Segmentation + SAM2 Editable (Stretch)

**Goal:** Show contours around abnormal cells; physician can click to add/remove.

**Steps:**

1. **Dataset:**
   - Cx22 (1,320 images, 14,946 instances, semantic + instance masks)
   - ISBI 2014/2015 (nucleus + cytoplasm masks, some z-stack)
   - If Thai data has masks (unlikely), use it

2. **Baseline model:**
   - Mask R-CNN or Cyto R-CNN (from literature)
   - Or: fine-tune Cellpose / StarDist on Cx22
   - Target: AP50 > 50% on Cx22 val (literature baseline)

3. **SAM2 integration (demo only):**
   - SAM2 (Segment Anything Model 2) is promptable
   - User clicks point or draws box → SAM2 outputs mask
   - Overlay on image
   - User can accept / reject / refine

4. **UI:**
   - In web demo: toggle "Edit Mode"
   - Click (+) on image → prompt SAM2 → add contour
   - Click (-) on existing contour → remove
   - "Accept All" / "Reject All" for batch

5. **Active learning (NOT in Phase 2):**
   - Correction → store as new training example
   - Periodic retrain
   - **BLOCKED by FDA PCCP guidance (2024):** Cannot auto-learn without validation gate
   - Defer to Phase 3 with proper protocol

**Deliverable:**
- `ml/segmentation.py` (baseline model)
- Updated web demo with SAM2 edit (if SAM2 weights downloadable)
- Demo video (30-60s) showing click-to-edit
- **Honest limitation:** "Demo only. Not integrated into active learning loop yet."

### 3.5 Workstream E: Edge Deployment

**Goal:** Run inference on Jetson Nano or Raspberry Pi 4, < 30s per case, offline.

**Steps:**

1. **Export:**
   - `python ml/scripts/train_classifier_v2.py --export-onnx`
   - Produces `best_cervical_v2.onnx`

2. **Quantize:**
   - ONNX Runtime quantization (FP32 → FP16 → INT8)
   - Or: TensorRT (Jetson) FP16
   - Measure accuracy drop on val set

3. **Hardware:**
   - Jetson Nano (or Orin Nano if budget): ~$100-300
   - Raspberry Pi 4 + Coral USB accelerator (optional): ~$100 + $70
   - Benchmark: batch=1, 224x224, end-to-end (preprocess + infer + post)

4. **Runtime:**
   - ONNX Runtime (cross-platform)
   - Or: TensorRT (Jetson only, faster)
   - Simple Python wrapper or C++ for speed

5. **UI (minimal):**
   - Local web server (FastAPI same as Phase 1)
   - Or: CLI tool `cervical-ai infer --image foo.jpg`
   - Output: JSON + optional heatmap PNG

**Target metrics:**
- Latency: < 30s per image (end-to-end) on Jetson Nano
- Accuracy drop after INT8: < 2% on recall_hsil_scc
- Power: runs on 5V/2A (portable)

**Deliverable:**
- ONNX + quantized variants
- `scripts/deploy_edge.py` (benchmark script)
- Report: "Edge Deployment Benchmarks (Jetson Nano / Pi 4)"

### 3.6 Workstream F: Local LLM Patient Report (Optional)

**Goal:** Replace rigid template with natural Thai text, while preserving clinical meaning and privacy.

**Approach:**

1. **Model:**
   - Local LLM: llama.cpp + 7B or 13B model (Thai-capable)
   - Or: smaller instruction-tuned model (e.g., Typhoon, OpenThaiGPT if available)
   - Must run on CPU or single GPU, < 10s per generation

2. **Prompt engineering:**
   ```
   System: You are a medical communication assistant. Rewrite the following structured findings into plain Thai for a patient with primary school education. Do not add diagnosis. Do not change clinical meaning. Use only these approved phrases: [list].
   
   Input: {"bethesda": "HSIL", "koilocyte": true, "confidence": 0.89, "triage": "ส่ง Colposcopy ด่วน"}
   
   Output: (must contain: ผล, การกระทำ, เหตุผล)
   ```

3. **Constraints / Guardrails:**
   - Output must be JSON with keys: `result`, `action`, `why`
   - No words from banned list ("มะเร็ง", "cancer", "เป็น", "diagnose")
   - Max 3 sentences per field
   - If generation fails constraints → fall back to template

4. **RAG (optional):**
   - Pre-approved phrase bank
   - Retrieve similar cases → few-shot examples in prompt

5. **Privacy:**
   - All inference local (no API call to OpenAI/Anthropic)
   - No patient data logged

**Risks:**
- LLM hallucinates clinical meaning
- Thai grammar broken (low-quality model)
- Slow on CPU (user waits 10-30s)

**Deliverable:**
- `server/llm_report.py` (local LLM wrapper)
- Prompt templates + guardrail code
- Fallback to template if LLM fails
- **Honest statement:** "Optional feature. Template is default and safe."

---

## 4. PHASE 3 — VALIDATION + SCALE

**Timeline:** 18-36 months (after Phase 2)

**Budget:** Multi-million THB (grant + hospital + government)

### 4.1 Workstream G: Reader Study

**Goal:** Prove that AI + physician > physician alone (or at least non-inferior).

**Design (standard for medical AI):**

| Arm | Description | N (slides) |
|-----|-------------|------------|
| A | Physician alone (no AI) | 200-500 |
| B | AI alone (no physician) | 200-500 |
| C | AI + physician (physician sees AI output, can override) | 200-500 |

**Metrics:**
- Sensitivity for CIN2+ (or HSIL/SCC as proxy if histology not available)
- Specificity
- Time to interpretation
- Agreement (kappa) between arms

**Blinding:**
- Pathologists randomized to arm
- Same slide set across arms (washout period)
- Ground truth: histology (biopsy) if available, or consensus panel if not

**Sample size calculation:**
- Need statistician
- Depends on expected effect size (literature: AI-assisted +10-15% sens)
- Typical: 300-1000 slides for powered study

**Deliverable:**
- Protocol (IRB-approved)
- Reader study report (sensitivity, specificity, time, kappa)
- Publication (target: Thai journal or international conference)

### 4.2 Workstream H: Prospective Validation

**Goal:** Deploy in real workflow (not retrospective on archived slides).

**Design:**
- Hospital A and B (different sites)
- All women coming for routine screening during study period
- AI runs in parallel with standard of care (not replacing)
- Physician makes final call (AI is second reader)
- Track:
  - AI prediction vs final diagnosis
  - Time from sample to result (standard vs AI-assisted)
  - Loss-to-follow-up rate (standard vs AI-assisted)
  - Physician override rate (how often they disagree with AI)
  - Patient satisfaction (survey on report clarity)

**Duration:** 6-12 months enrollment + 6 months follow-up

**N:** 1,000 - 5,000 women (depending on prevalence and power)

**IRB:** Required (prospective, even if de-identified)

**PDPA:** Consent or waiver (if secondary use of routine care data)

**Deliverable:**
- Prospective validation report
- Real-world metrics (not just retrospective)
- Workflow integration lessons learned

### 4.3 Workstream I: Cost-Effectiveness

**Goal:** Show that AI triage is cost-effective (or cost-saving) vs status quo.

**Model:**
- Decision tree or Markov model
- Inputs:
  - Cost of AI (hardware amortized + software + training)
  - Cost of standard cytology (pathologist time, transport, etc.)
  - Sensitivity/specificity (from reader study)
  - Loss-to-follow-up rates (standard vs AI)
  - Treatment costs for CIN2+, cancer
  - QALY (quality-adjusted life years) from early detection

**Outputs:**
- Cost per woman screened
- Cost per CIN2+ detected
- Cost per QALY gained
- Incremental cost-effectiveness ratio (ICER)

**Threshold (Thailand):**
- WHO: cost-effective if < 3x GDP per capita per QALY
- Thai: similar, or use local threshold

**Deliverable:**
- Health economics report
- "AI cytology is cost-effective for Thai community hospitals" (or not, with caveats)

### 4.4 Workstream J: Thai FDA SaMD Awareness

**Goal:** Understand the pathway. Do NOT submit in Phase 3 unless funded for it.

**Activities:**
- Read Thai FDA SaMD guidance (June + Oct 2024)
- Map our system to risk class (likely II or III)
- Identify required evidence:
  - Training/test dataset disclosure
  - Fairness / bias assessment
  - Cybersecurity
  - Clinical validation (reader study + prospective)
  - Post-market surveillance plan
- Talk to Thai FDA (if possible) or consultant
- Draft "Intended Use" statement
- Draft "Indications for Use"

**Not in scope:**
- Actual submission (costs 1-5M THB + 1-2 years)
- Clinical trial for regulatory (different from research validation)

**Deliverable:**
- Regulatory strategy memo
- "What would be needed for Thai FDA submission" checklist

### 4.5 Workstream K: Pilot Deployment (1-2 Hospitals)

**Goal:** Real-world use, not just research.

**Site selection:**
- 1-2 community hospitals (รพ.ชุมชน)
- Existing cytology program (they already do Pap/ThinPrep)
- Pathologist or cytotechnologist on site or accessible
- IT support (or we provide)
- Hospital director buy-in

**Deployment mode:**
- **Offline-first** (laptop or Jetson, no internet required)
- Images from existing microscope + smartphone adapter
- AI runs locally
- Report printed or sent via LINE (hospital's existing channel)
- Physician signs before patient sees

**Data collection (with consent):**
- All AI predictions logged
- All physician overrides logged
- All patient reports logged (de-identified)
- Quarterly review: performance, issues, feedback

**Support:**
- Training for staff (1-2 days)
- Hotline / chat for troubleshooting
- Monthly visit or call for first 3 months

**Success criteria:**
- > 80% of staff report "AI is helpful" (survey)
- Latency < 30s per case (measured)
- Zero critical bugs in 3 months
- At least 100 cases processed

**Deliverable:**
- Deployment report
- Lessons learned
- Go / No-Go for scale-up

---

## 5. PHASE 4+ (NOT CLAIMED IN PITCH)

### 5.1 WSI + MIL (Whole-Slide Image + Multiple Instance Learning)

**Problem:** Real-world cytology is a full slide with 10,000-100,000 cells. Phase 1 is single-field or single-cell.

**Approach:**
- OpenSlide to read .svs / .ndpi / .tiff WSI
- histolab or custom tissue detection (remove background)
- Patch extraction (256x256 or 512x512, 50% overlap)
- Run cell classifier on each patch
- MIL: attention transformer aggregates top-K suspicious patches
- Output: slide-level grade + attention heatmap (where AI focused)

**Data:** Need WSI-level labels (not cell-level). Harder to get.

**Claim (Phase 4):** "We can screen full slides, not just fields."

### 5.2 Federated Learning + Differential Privacy

**Problem:** Thai data is sensitive. Hospitals won't share raw images.

**Approach:**
- Train locally at each hospital
- Share only model updates (gradients or weights)
- Aggregate at central server (FedAvg)
- Add noise (DP) to updates to prevent reconstruction

**Benefit:** Multi-site training without data leaving premises.

**Challenge:** Domain shift across hospitals (different scanners, stains, populations).

**Claim (Phase 4):** "Privacy-preserving multi-site learning."

### 5.3 Multimodal Fusion

**Input:**
- Cytology image
- HPV genotype (16/18/52/58)
- Age
- Clinical history (if available)

**Model:** Late fusion or cross-attention.

**Output:** Risk score (probability of CIN2+ given all data).

**Claim (Phase 4):** "AI integrates image + molecular + clinical for precision triage."

---

## 6. TIMELINE VISUAL (GANTT-STYLE)

```
2026 Q3   Q4   2027 Q1   Q2   Q3   Q4   2028 Q1   Q2   Q3   Q4
─────────────────────────────────────────────────────────────────
PHASE 1 (DONE)
  POC infrastructure ████
  Docs + pitch ████

PHASE 2
  Thai data MOU+IRB        ████████████
  Thai fine-tune                    ████
  Z-stack 2.5D                   ████
  SAM2 editable (demo)         ████
  Edge deploy                    ████
  LLM report (opt)                  ████

PHASE 3
  Reader study                          ████████████
  Prospective validation                     ████████████████
  Cost-effectiveness                              ████
  Thai FDA awareness                          ████
  Pilot deployment 1-2 รพ.                     ████████████

PHASE 4+ (future)
  WSI + MIL                                              ████
  Federated + DP                                          ████
  Multimodal                                              ████
```

---

## 7. DEPENDENCIES & CRITICAL PATH

**Critical path (longest chain):**
1. Find clinical PI + hospital partner (2-3 mo)
2. IRB approval (2-3 mo, can overlap with MOU drafting)
3. Data collection + de-id (1-2 mo)
4. Thai fine-tuning (1-2 mo)
5. Reader study (6-12 mo)

**Parallelizable:**
- Z-stack hardware search (can start now, independent of Thai data)
- Edge deployment (can use public data + Phase 1 model)
- LLM report (can prototype on public data)

**Blockers:**
- No clinical PI = no IRB = no Thai data = no fine-tuning
- No z-stack scanner access = no 2.5D (use ISBI 2015 as fallback)

---

## 8. RISK REGISTER (UPDATED)

| Risk | Phase | Likelihood | Impact | Mitigation | Owner |
|------|-------|------------|--------|------------|-------|
| Cannot find hospital partner | 2 | Medium | High | Start with academic hospitals (easier entry); use personal network | Clinical advisor |
| IRB rejects or delays > 6 mo | 2 | Medium | High | Secondary data (already collected) is easier than prospective; have backup hospital | PI |
| Thai data < 100 images | 2 | Medium | Medium | Use heavy augmentation + transfer learning; accept limitation | ML lead |
| Z-stack data unavailable | 2 | High | Low | Use ISBI 2015 for feasibility; claim "roadmap validated" | ML lead |
| Reader study underpowered | 3 | Medium | Medium | Get statistician early; publish as "pilot reader study" if N small | Clinical advisor |
| Hospital refuses pilot deployment | 3 | Low | High | Choose hospital that participated in data collection (relationship) | Team |
| Thai FDA pathway unclear | 3 | Medium | Low | Hire consultant if needed; "awareness" not submission | Regulatory |
| Funding gap | All | High | High | Samsung + other grants (NSTDA, NRCT, international); hospital in-kind | Team |
| Key person leaves | All | Medium | Medium | Document everything; pair programming on critical code | Team |

---

## 9. RESOURCE REQUIREMENTS (ESTIMATE)

### 9.1 People (FTE or equivalent)

| Role | Phase 2 | Phase 3 | Source |
|------|---------|---------|--------|
| ML Engineer | 0.5 | 0.3 | Student / volunteer / hire |
| Backend / DevOps | 0.3 | 0.2 | Student / volunteer |
| Clinical advisor (MD) | 0.1 | 0.2 | Consultant / co-PI |
| Hospital liaison | 0.2 | 0.3 | Paid or in-kind |
| Statistician | 0 | 0.2 | Consultant (reader study) |
| Health economist | 0 | 0.1 | Consultant (cost-effectiveness) |

### 9.2 Hardware

| Item | Phase 2 | Phase 3 | Cost |
|------|---------|---------|------|
| GPU (RTX 5060 or Colab Pro) | 1 | 1 | Existing or 10k THB/mo |
| Jetson Nano / Orin | 1-2 | 2-3 | 10-30k THB each |
| Smartphone + adapter (test) | 2-3 | 5 | 5-10k THB |
| Z-stack scanner access | Borrow | Borrow or buy | 500k+ THB (or hospital in-kind) |

### 9.3 Data

| Item | Phase 2 | Phase 3 | Cost |
|------|---------|---------|------|
| Public datasets | ✅ | ✅ | Free |
| Thai images (100-500) | Target | + more | IRB + labor (0-100k THB) |
| Z-stack volumes (50-200) | Target | + more | Hospital access (in-kind) |
| WSI (for Phase 4) | — | — | Expensive (later) |

### 9.4 Money (Rough)

| Category | Phase 2 | Phase 3 | Notes |
|----------|---------|---------|-------|
| Personnel (stipend / consultant) | 200-500k THB | 1-3M THB | Depends on grants |
| Hardware | 50-100k THB | 100-500k THB | Jetson + adapters |
| IRB + legal | 0-50k THB | 50-200k THB | Varies |
| Travel (site visits) | 20-50k THB | 50-100k THB | |
| Publication / conference | 0 | 50-100k THB | |
| **Total** | **300k-700k THB** | **1.5M-4M THB** | |

**Funding sources:**
- Samsung Solve for Tomorrow (if win)
- NSTDA, NRCT, Thai Health
- International (WHO, Gates, etc. — hard for students)
- Hospital in-kind (staff time, scanner access)
- University grant (if affiliated)

---

## 10. SUCCESS METRICS BY PHASE

| Phase | Primary Metric | Target | Secondary |
|-------|----------------|--------|-----------|
| 1 (POC) | Demo works end-to-end | Pass | Code complete, docs complete |
| 2 (Thai + Z) | Recall(HSIL/SCC) on Thai val | > 85% (or +10% over base) | Domain shift gap < 5% |
| 3 (Validation) | Sensitivity (AI+MD vs MD) | Non-inferior or +5-10% | Time reduction 30%, loss-to-f/u drop 20% |
| 4 (Scale) | Hospitals deployed | 5+ | Cost per screen < 100 THB |

---

## 11. GO / NO-GO GATES

**After Phase 2:**
- GO if: Thai data > 100 images, fine-tuned recall > 80% or +5% over base, z-stack demo works
- NO-GO if: No Thai data (stuck at Phase 1), or fine-tuned model worse than base (overfit or label noise)

**After Phase 3:**
- GO if: Reader study shows non-inferior, prospective pilot runs 100+ cases with < 5% critical error
- NO-GO if: AI+MD worse than MD alone, or hospitals refuse to deploy

**Do not proceed to scale without evidence.**

---

**END OF DETAILED ROADMAP**

*Word count: ~4,500*
*Date: 2026-06-26*
*Use for planning, grant writing, partner discussions*

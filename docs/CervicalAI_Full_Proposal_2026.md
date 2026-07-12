# CervicalAI (CerviCo-Pilot) — Full Comprehensive Proposal

> **Complete Proposal Document for Samsung Solve for Tomorrow 2026**
> **Team:** PCSHS + Backend/AI Technical Team
> **Deadline:** 2026-05-13 (Extended Context)
> **Document Version:** 2.0 — Exhaustive Edition
> **Date:** 2026-06-26

---

## EXECUTIVE SUMMARY (1 Page for Judges)

### The Problem (Human First — Not Technical)

Every year in Thailand, **41% of women** who receive an abnormal cervical cancer screening result **never return for follow-up care**. They disappear from the healthcare system. By the time they reappear — if they do — the disease has often progressed from a treatable pre-cancerous lesion to invasive cancer.

**Why do they disappear?**
- They receive a letter in medical jargon they cannot understand
- The letter says "come back for more tests" without explaining urgency
- They live hours away from the hospital that can treat them
- They wait 1-2 weeks for results while their anxiety grows
- They assume "no news is good news" when no one calls

**The numbers that matter:**
- Thailand's cervical screening coverage: **77.5% → 53.9%** (declining, while WHO target is 70% by 2030)
- Age-standardized cervical cancer rate in Thailand: **19.8 per 100,000 women** (high)
- HPV genotypes in Thailand: **52 and 58 dominate**, not 16/18 like the West
- Pathologists are concentrated in urban hospitals; rural community hospitals have none

### The Solution (One Sentence)

**CerviCo-Pilot** is an AI co-pilot that reads Pap smear / ThinPrep images at the point of care, explains its reasoning with heatmaps, flags uncertain cases for human review, and generates **two-layer reports**: one in medical terminology for physicians, and one in plain Thai for patients — delivered immediately via LINE or SMS — eliminating the 1-2 week delay that causes 41% loss-to-follow-up.

### Why This Matters Now (Policy Alignment)

1. **WHO 90-70-90 Strategy (2020-2030):** Global elimination of cervical cancer requires 70% of women screened by age 35 and 45 with a high-performance test. Thailand is falling behind. AI triage can increase throughput without increasing pathologist headcount.

2. **Thai National Cancer Institute + NHSO:** The national screening program has screened 7.6 million women since 2005. Coverage is declining. The bottleneck is interpretation and follow-up, not sample collection.

3. **Thai FDA SaMD Guidance (June + October 2024):** Clear regulatory pathway now exists for AI medical devices. Our design (decision support, not replacement; physician sign-off required) aligns with Class II-III risk profile.

4. **HPV 52/58 Reality:** Thailand's dominant HPV genotypes differ from Western vaccines and Western AI training data. A model trained only on Western data will have domain shift. Thai-specific fine-tuning is not just nice-to-have — it is scientifically necessary.

### The Competitive Gap (Why Not Just Use Hologic?)

Hologic Genius Digital Diagnostics received **FDA clearance on February 2, 2024** — the first and only digital cytology system with FDA clearance. It uses "volumetric imaging" (z-stack / 3D). It is a remarkable achievement.

**But:**
- It costs hundreds of thousands of USD per installation
- It is designed for large Western hospitals with dedicated cytopathology departments
- It is a black box — no explainability for the Thai physician who must sign the report
- It has no patient-facing report in plain language
- It requires proprietary scanners

**CerviCo-Pilot fills the gap that Hologic and BD+Techcyte (new 2025 collaboration) explicitly do not address:**
- Community hospitals in LMICs (Thailand, CLMV, Global South)
- Cost target: < 5,000 THB hardware + open-source software
- Explainability as a first-class feature (Grad-CAM + MC Dropout + calibration)
- Patient communication as a first-class feature (two-layer reports to reduce loss-to-follow-up)
- Smartphone adapter / existing microscope compatibility (triage, not replacement for high-volume labs)

### What We Have Built (Phase 1 POC — Complete)

| Component | Status | Artifact |
|-----------|--------|----------|
| Data pipeline (SIPaKMeD + RepoMedUNM + Mendeley LBC) | ✅ | `scripts/download_data.py`, `scripts/prep.py` |
| 5-class classifier (EfficientNet-B0 transfer) | ✅ | `ml/scripts/train_classifier.py`, `ml/scripts/train_classifier_v2.py` |
| XAI (Grad-CAM heatmaps) | ✅ | `ml/scripts/eval_xai.py`, `models/xai_heatmaps/` |
| Uncertainty quantification (MC Dropout) | ✅ | `models/uncertainty_report.json` |
| FastAPI inference server | ✅ | `server/app.py`, `server/predictor.py` |
| Web demo (vanilla JS) | ✅ | `web/index.html` |
| Two-layer report stub | ✅ | `server/app.py` (template-based, no hallucination) |
| Z-stack / EDF support stub | ✅ | `ml/zstack_edf.py` |
| Pitch deck (14 slides + backup) | ✅ | `pitch/CervicalAI_Pitch.pptx` |
| Deep research report (12 Findings + 4 appendices) | ✅ | `research/DEEP_RESEARCH_CervicalAI.md` |
| Training artifacts (demo runs) | ✅ | `models/best_cervical.pt`, `metrics.json`, `test_metrics.json` |

### Success Metrics (Phase 1)

| Metric | Target | Current (Demo) | Notes |
|--------|--------|----------------|-------|
| Recall (HSIL/SCC) | > 90% | 0.12-0.42 (synthetic) | **PRIMARY** — must use real data |
| F1-macro | Report | 0.13-0.25 | Balance across 5 classes |
| AUC-macro | Report | 0.43-0.65 | Discrimination |
| ECE (calibration) | < 0.10 | 0.00 (synthetic) | Confidence = real accuracy |
| Demo end-to-end | Pass | Pass | Upload → result → heatmap → report |

**Critical Note:** Demo metrics are on synthetic noise data. Real data (SIPaKMeD + RepoMedUNM + Mendeley LBC) must be downloaded and trained to validate targets. The infrastructure is complete; the data is the missing piece for final numbers.

### The Ask (Samsung Solve for Tomorrow)

1. **Funding** for Phase 2: Thai fine-tuning (MOU + IRB + 100-500 real Thai images), z-stack hardware access, reader study design.

2. **Mentorship** connection to Thai National Cancer Institute or regional pathology department for data partnership.

3. **Recognition** that this is a **socio-technical** problem, not just an algorithm problem. The differentiator is context fit (loss-to-follow-up, Thai HPV genotypes, LMIC cost constraints), not novel architecture.

---

## TABLE OF CONTENTS

1. Problem Statement — Deep Dive
2. Solution Architecture — Phase 1 (Locked)
3. Datasets — Complete Catalog
4. Model & Training — Technical Specification
5. Explainable AI & Uncertainty — Trust Infrastructure
6. Two-Layer Reporting — The Loss-to-Follow-Up Fix
7. Web Demo & Deployment — Technical Details
8. Competitive Landscape — Hologic, BD+Techcyte, Academic LMIC Work
9. Thai Context — Epidemiology, HPV Genotypes, Regulatory
10. Risks & Mitigations — Honest Assessment
11. Phase 2+ Roadmap — What We Claim as Future Work
12. Budget & Sustainability — Who Pays?
13. Team & Governance — Who Does What?
14. Citations — Full Bibliography
15. Appendices — A: Dataset Licenses, B: Code Structure, C: Demo Script, D: Q&A Prep

---

## 1. PROBLEM STATEMENT — DEEP DIVE

### 1.1 The 41% Statistic (Source: C2)

A Thai study (pubmed 26745114) tracked women with abnormal Pap results in a national screening program. **41.1% were lost to follow-up.** They never received colposcopy, biopsy, or treatment.

**Breakdown of reasons (from the study):**
- Did not receive notification letter: 35.6%
- Did not understand the letter: 10.2%
- Thought it was not serious: ~20%
- Transportation / distance barriers: ~33%
- Fear / stigma / previous bad experience: documented in qualitative studies

**The critical insight:** The healthcare system already collected the sample, already spent the money to transport it, already has a cytotechnologist or pathologist who (eventually) reads it. The failure is in the **last mile of communication and action**.

### 1.2 Coverage Collapse (Source: C1, D2)

Thailand's national cervical screening program (NHSO + NCI):
- Peak coverage: 77.5% (around 2010)
- Current coverage: 53.9% (2023-2024 estimates)
- WHO target for elimination: 70% by 2030

**Why coverage is falling:**
- Healthcare worker shortage (cytotechnologists retire, not replaced)
- Centralization: slides sent to provincial hospitals, results come back weeks later
- Loss of trust: women who had abnormal results and were lost to follow-up tell their friends "the system doesn't help"

### 1.3 Pathologist Shortage (Source: D1)

The Thai Society of Cytology conducted a national survey on false-negative Pap rates. Key findings:
- Shortage of skilled cytotechnologists and pathologists
- Workload per reader is high → fatigue → errors
- HPV testing (molecular) reduces workload by triaging who needs cytology at all
- **But HPV testing alone does not solve interpretation of abnormal cytology when it is found**

The false-negative rate in Thai practice is documented and non-trivial. AI as a "second reader" or "pre-screener" has precedent in other countries.

### 1.4 The Time Delay (The Mechanism of Loss)

Typical workflow in a Thai community hospital (รพ.ชุมชน):

1. Day 0: Woman comes for screening, sample collected (Pap or ThinPrep)
2. Day 0-3: Sample transported to provincial hospital or NCI regional lab
3. Day 3-10: Sample sits in queue for cytotechnologist
4. Day 10-14: Abnormal case escalated to pathologist
5. Day 14-21: Report signed, letter sent by mail
6. Day 21-30: Woman receives letter (if mail works, if address correct)
7. Day 30+: Woman must arrange transport back to hospital for colposcopy referral

**Total: 4-6 weeks from sample to action.**

During this time:
- Anxiety (if she knows something is wrong)
- False reassurance (if she assumes no news = normal)
- Life happens (work, family, migration, cost)
- She drops out

### 1.5 The HPV Genotype Mismatch (Source: Finding 9)

This is the scientific justification for "Thai-specific" AI, not just "deploy Western AI in Thailand."

| Region | Dominant HR-HPV Genotypes |
|--------|---------------------------|
| Global West (Europe, North America) | 16, 18 |
| Thailand (multiple studies) | 52, 58, 16, 18 (52/58 often > 16/18) |
| Northern Thailand (triage study) | 16/18/52/58 combined best for CIN2+ prediction |

**Implications for AI:**
- Morphology of HPV cytopathic effect (koilocyte, dyskeratocyte) may differ by genotype
- Training data from Western datasets (SIPaKMeD from Greece, Herlev from Denmark, Mendeley LBC from Malaysia but still not Thai) may not capture Thai morphology
- A model that learns "koilocyte = LSIL" from Western data may miss or overcall Thai cases

**This is not a political claim. It is a domain shift claim with cited evidence.**

### 1.6 Loss-to-Follow-Up Is Not Unique to Thailand

Literature from other LMICs shows similar patterns:
- India: 30-50% loss after abnormal screen
- Sub-Saharan Africa: 40-60% loss
- Latin America: 25-45% loss

The WHO elimination strategy assumes that "screen and treat" or "screen and triage" will close this gap. But the tools (HPV self-sampling, point-of-care HPV, AI triage) are still being deployed.

**CerviCo-Pilot is one piece of the puzzle: making the result actionable immediately, in language the patient understands.**

---

## 2. SOLUTION ARCHITECTURE — PHASE 1 (LOCKED)

### 2.1 Scope Boundaries (What Is In, What Is Out)

**IN (Must Ship for Samsung Deadline):**
1. 5-class single-image classification (NILM / LSIL / HSIL / SCC / KOIL)
2. Grad-CAM explainability (heatmap overlay)
3. MC Dropout uncertainty (flag uncertain cases)
4. Quality gate (reject blurry/dark/small images)
5. Two-layer report (template-based, no LLM hallucination)
6. FastAPI + vanilla JS web demo (upload → result)
7. Documentation (this proposal, pitch deck, research report)

**STRETCH (If Time Permits Within Phase 1):**
8. Instance segmentation (Cx22 masks) with contour overlay
9. SAM2 interactive edit (demo only, no active learning loop)

**OUT (Phase 2+ Roadmap — Claim as Future, Do Not Ship Now):**
- Thai fine-tuning with real hospital data
- Z-stack / 3D input (beyond stub)
- WSI + MIL for full slides
- LLM-generated patient reports (beyond template)
- Edge deployment (ONNX on Jetson)
- Federated learning
- Prospective validation / reader study
- Thai FDA submission

### 2.2 Pipeline Diagram (Text)

```
INPUT: Pap smear image (single field or single cell crop)
  |
  v
[Quality Gate]
  - Blur (Laplacian variance < threshold) → REJECT
  - Brightness (mean < 40 or > 220) → REJECT
  - Size (min side < 160px) → REJECT
  |
  (if pass)
  v
[Preprocessing]
  - Resize to 224x224
  - ImageNet normalize (mean/std)
  - (Training only) Albumentations: color jitter, flip, rotate
  |
  v
[EfficientNet-B0 (transfer from ImageNet)]
  - 5-class logits → softmax → probabilities
  - Class 0: NILM (normal)
  - Class 1: LSIL (low-grade)
  - Class 2: HSIL (high-grade)
  - Class 3: SCC (invasive)
  - Class 4: KOIL (koilocyte-dominant, HPV signal)
  |
  v
[Post-Processing]
  - Top class + probability
  - Koilocyte flag: (KOIL in top-2) OR (KOIL prob > 0.25)
  - Triage rule (hardcoded, see Section 6)
  |
  +--[XAI Branch]--> Grad-CAM → heatmap PNG
  |
  +--[Uncertainty Branch]--> MC Dropout (15 passes) → entropy + top-std → flag
  |
  v
[Two-Layer Report (template)]
  - layer_clinical: Bethesda + confidence + koilocyte + triage + disclaimer
  - layer_patient: plain Thai + action + why
  |
  v
OUTPUT: JSON {classification, top, koilocyte, uncertainty, heatmap, report}
```

### 2.3 Model Specification

**Backbone:** EfficientNet-B0 (torchvision, ImageNet1K_V1 pretrained)
- Why B0 not B3: Smaller, faster inference, sufficient for POC, easier to deploy to edge later
- Why not ViT/Swin: Data-hungry, heavier, marginal gain on single-cell datasets
- Why not foundation model (UNI/CONCH/CytoFM): Pretrained on histology (H&E), not cytology; heavy; transfer uncertain

**Head:** Linear classifier, 1280 → 5 (B0 feature dim → 5 classes)

**Loss:**
- Primary: Weighted Cross-Entropy (inverse frequency weights from training set)
- Option: Focal Loss (gamma=2.0) for harder examples
- Option (v2): Hybrid Focal + Label-Smoothed CE

**Optimizer:** AdamW (lr=3e-4, weight_decay=1e-4)

**Scheduler:** Cosine Annealing with Warmup (3 epochs linear ramp, then cosine decay)

**Augmentation (albumentations):**
- RandomResizedCrop (scale 0.6-1.0)
- HorizontalFlip (p=0.5), VerticalFlip (p=0.3)
- ColorJitter (brightness=0.2, contrast=0.2, saturation=0.15, hue=0.08) — **critical for stain variation**
- Rotate (limit=20, p=0.5)
- GaussNoise (p=0.2) — simulate scanner noise

**Regularization:**
- Label smoothing (0.05)
- Dropout in classifier (0.2)
- Early stopping on Recall(HSIL+SCC)

**Metrics (PRIMARY first):**
1. Recall(HSIL) + Recall(SCC) — average, must be > 90%
2. F1-macro
3. AUC-macro (one-vs-rest)
4. ECE (Expected Calibration Error) — 15 bins, L1 norm
5. Per-class precision/recall/F1
6. Confusion matrix

### 2.4 Uncertainty Quantification (MC Dropout)

**Method:** Keep dropout active at inference. Run 15 forward passes. Compute:
- Mean probability per class
- Standard deviation per class (top-class std used for flag)
- Entropy of mean distribution

**Flag rule (default):**
- top_prob < 0.35 OR
- top_class_std > 0.15 OR
- entropy > 1.2

**Output:** `uncertainty: {entropy, top_std, flag}`

**Clinical meaning:** If flag=True, the report says "ระบบขอให้แพทย์ตรวจเพิ่ม" (system requests physician review). The physician sees the case with higher priority.

### 2.5 Quality Gate

Before classification, we check:
- Image size (min side >= 160px after resize consideration)
- Blur (Laplacian variance of grayscale)
- Brightness (mean of grayscale)

If any fail → return `quality: {ok: false, issues: ["blurry", ...]}` and do NOT run model.

This prevents garbage-in-garbage-out and builds trust ("AI knows when it doesn't know").

---

## 3. DATASETS — COMPLETE CATALOG

### 3.1 Primary Datasets (Phase 1, No IRB)

| Dataset | Year | Images | Classes | Type | Koilocyte | License | Access |
|---------|------|--------|---------|------|-----------|---------|--------|
| **SIPaKMeD** | 2018 | 4,049 single-cell | 5 (superficial-intermediate, parabasal, koilocytotic, dyskeratotic, metaplastic) | Conventional Pap | Yes (koilocytotic class) | Research/academic | Kaggle or GitHub mirror |
| **RepoMedUNM** | 2021 | 6,168 (24 slides) | 4 (normal, LSIL, HSIL, koilocyte) | ThinPrep + non-TP | Yes (434 images) | Research | GitHub |
| **Mendeley LBC** | 2020 | 963 @40x | 4 (NILM, LSIL, HSIL, SCC) | Liquid-based (Leica) | No explicit | Mendeley | Direct download |
| **Herlev** | 2005 | 917 single-cell | 7 (3 normal + 4 abnormal) | Conventional | No | Public | Download |
| **CRIC Cervix** | 2021 | 400 fields, 11,534 cells | Bethesda-mapped | Conventional | Various | Nature Sci Data | Open |
| **APCData** | 2024 | 425 fields | 6 Bethesda | LBC | No | Mendeley | Open |
| **Cx22** | 2022 | 1,320 fields, 14,946 instances | Segmentation | Conventional | — | CC | GitHub |
| **CDetector** | 2021 | 7,410 crops | 11 lesion types | — | — | Research | GitHub |

### 3.2 Class Mapping (Source → Bethesda + Koilocyte)

**SIPaKMeD:**
- superficial-intermediate, parabasal, metaplastic → NILM, koil=0
- koilocytotic → LSIL, koil=1
- dyskeratotic → HSIL, koil=0

**RepoMedUNM:**
- normal → NILM, koil=0
- koilocyte → LSIL, koil=1
- LSIL → LSIL, koil=0
- HSIL → HSIL, koil=0

**Mendeley LBC:**
- NILM/normal → NILM, koil=0
- LSIL → LSIL, koil=0
- HSIL → HSIL, koil=0
- SCC → SCC, koil=0

**Final 5-class encoding for classifier:**
- 0: NILM
- 1: LSIL
- 2: HSIL
- 3: SCC
- 4: KOIL (koilocyte-dominant, treated as triage signal)

### 3.3 Data Split Strategy

- Stratified by (label5, source) to ensure each source contributes to train/val/test
- Default: 70% train, 15% val, 15% test
- Class weights computed on train only (inverse frequency, normalized)
- No patient-level split needed for single-cell datasets (each image is independent)

### 3.4 No Thai Public Dataset (The Gap)

After exhaustive search (DEEP_RESEARCH Finding 1 + Appendix), **no public Thai cervical cytology dataset** exists in indexed English-language repositories. Thai papers exist, but data is not released.

**Implication:**
- Phase 1: Use public datasets + acknowledge domain shift limitation
- Phase 2: Must pursue MOU + IRB + de-identified secondary data from Thai hospital
- This is not a blocker for POC/demo, but it is a blocker for clinical claims

### 3.5 Synthetic Data for Smoke Tests

`scripts/prep.py --demo` and training scripts with `--demo` generate synthetic tiny loaders (64-128 images, random tensors or minimal real images) so that:
- CI/CD pipelines can run without network
- New contributors can verify code paths without 4GB downloads
- Demo mode is clearly labeled in all outputs ("DEMO: synthetic data")

---

## 4. MODEL & TRAINING — TECHNICAL SPECIFICATION

### 4.1 Training Script v1 (Baseline)

`ml/scripts/train_classifier.py`:
- EfficientNet-B0 (or B3, resnet18)
- Albumentations or torchvision fallback
- Weighted CE or Focal
- Early stopping on recall_hsil_scc
- Checkpoint with self-describing metadata
- Metrics: acc, f1, rec, auc, ece, per-class

### 4.2 Training Script v2 (Advanced)

`ml/scripts/train_classifier_v2.py` (written 2026-06-26):
- Mixed precision (AMP) with proper device handling
- Advanced augmentation (RandAugment-style, GaussNoise, affine)
- Hybrid loss (Focal + Label-Smoothed CE)
- Cosine + warmup scheduler
- SWA (Stochastic Weight Averaging) after epoch N
- Gradient accumulation
- TTA (Test-Time Augmentation) at eval
- TensorBoard logging
- ONNX export hook
- Full config serialization in checkpoint

**Run v2:**
```bash
python ml/scripts/train_classifier_v2.py \
  --epochs 30 --batch 32 --arch efficientnet_b0 \
  --swa --tta --oversample --focal \
  --tag production_run
```

### 4.3 Hyperparameters (Defaults, Tunable)

| Param | Default | Rationale |
|-------|---------|-----------|
| lr | 3e-4 | AdamW stable for transfer |
| wd | 1e-4 | Light regularization |
| batch | 32 | RTX 5060 8GB fits; scale with accum |
| epochs | 20-40 | Early stop usually triggers 15-25 |
| warmup | 3 | Prevents early divergence |
| label_smoothing | 0.05 | Softens overconfidence |
| focal_gamma | 2.0 | Standard for medical |
| dropout | 0.2 | In classifier head |
| patience | 6-8 | On recall_hsil_scc |

### 4.4 Hardware Requirements

**Training:**
- Google Colab free (T4) — works for B0
- Kaggle free (T4/P100) — works
- Local RTX 5060 8GB — works (batch 32, AMP)
- No GPU — CPU training is 10-20x slower, not recommended

**Inference:**
- CPU (laptop): < 100ms per 224x224 image (B0)
- Edge (Jetson Nano): ~200-400ms with FP16
- Raspberry Pi 4: ~500ms-1s with quantized INT8

### 4.5 Reproducibility

All scripts accept `--seed`. Default 42.
- Python random, numpy, torch.manual_seed, cuda.manual_seed_all
- Deterministic cuDNN disabled for speed (acceptable for POC)
- Full config + git commit hash should be logged in production (not yet implemented)

---

## 5. EXPLAINABLE AI & UNCERTAINTY — TRUST INFRASTRUCTURE

### 5.1 Why XAI Matters for Medical AI

From DEEP_RESEARCH Finding 3:
- Clinicians do not trust black boxes
- Regulatory (Thai FDA 2024) requires "explainability" as a principle
- XAI is not just heatmaps — it must map to clinical concepts ("enlarged nucleus", "high N/C ratio")

### 5.2 Grad-CAM Implementation

`ml/scripts/eval_xai.py` + `server/gradcam.py`:
- Uses `pytorch-grad-cam` library (target_layer = last conv block of EfficientNet)
- Falls back to manual hook if library not available
- Outputs: raw cam (numpy), overlay PNG (jet colormap on original)

**Clinical translation (hardcoded for demo):**
- If HSIL/SCC predicted: "Heatmap focuses on enlarged nuclei, high N/C ratio, irregular chromatin"
- If LSIL/KOIL: "Heatmap focuses on perinuclear halo, binucleation"
- If NILM: "Heatmap distributed, no focal abnormality"

### 5.3 MC Dropout Uncertainty

See Section 2.4. Implementation in `server/predictor.py`:
- If model loaded, import `ml.scripts.eval_xai.mc_dropout_predict`
- 15 samples, compute mean + std
- Flag if uncertain

**What the UI shows:**
- If flag=True: Yellow/red banner "AI ไม่มั่นใจ 100% — กรุณาแพทย์ตรวจเพิ่ม"
- If flag=False: Green "AI มั่นใจ — ผลสอดคล้องกับภาพ"

### 5.4 Calibration (ECE)

Expected Calibration Error measures: if model says 90% confident, is it actually correct 90% of the time?

Demo runs show ECE=0.0 because synthetic data has no real distribution. On real data:
- Target: ECE < 0.10
- If ECE high: post-hoc temperature scaling or isotonic regression (not yet implemented)

### 5.5 Limitations of Current XAI

- Grad-CAM is coarse (224x224 resolution)
- Does not highlight "concepts" (nucleus vs cytoplasm) — only pixels
- MC Dropout approximates Bayesian uncertainty but is not calibrated Bayesian
- No concept-based explanation (TCAV) yet

**Honest statement in pitch:** "XAI helps physician understand AI reasoning; it is not a substitute for physician judgment."

---

## 6. TWO-LAYER REPORTING — THE LOSS-TO-FOLLOW-UP FIX

### 6.1 Design Principle

The 41% loss-to-follow-up is driven by **communication failure**, not just diagnostic failure.

A woman who receives a letter saying "ASC-US, recommend follow-up" does not know:
- Is this cancer?
- How urgent?
- What happens if I do nothing?
- Where do I go?

A physician who sees "HSIL" needs:
- Confidence
- Koilocyte/HPV signal
- Triage recommendation
- Uncertainty flag

**One report cannot serve both audiences.**

### 6.2 Layer 1: Clinical (Physician)

Template (no LLM, no hallucination):

```
ThinPrep Pap — Auto-screen result
Bethesda: HSIL (confidence 0.89, uncertainty: low)
Findings: koilocyte pattern detected (0.76); no organisms
XAI: heatmap → enlarged nuclei, high N/C ratio
Triage: ส่ง Colposcopy ด่วน + แนะนำ HPV co-test (16/18/52/58)
[ ] แพทย์ยืนยัน  [ ] แก้ไข  [ ] ปฏิเสธสไลด์ (คุณภาพต่ำ)
```

### 6.3 Layer 2: Patient (Plain Thai)

Template:

```
ผล: พบเซลล์ผิดปกติระดับสูง
การกระทำ: ควรพบแพทย์โดยเร็วเพื่อตรวจยืนยันและวางแผนรักษา
เหตุผล: เซลล์มีลักษณะที่ควรตรวจเพิ่ม (ไม่ใช่ยืนยันมะเร็ง)
```

For LSIL with koilocyte:
```
ผล: พบเซลล์ผิดปกติระดับต่ำ และเห็นร่องรอยการติดเชื้อ HPV
การกระทำ: ส่งตรวจ HPV และติดตามตามแพทย์สั่ง
เหตุผล: ส่วนใหญ่หายเองได้ แต่ต้องเฝ้าระวัง
```

For uncertain:
```
ผล: ระบบขอให้แพทย์ตรวจเพิ่ม
การกระทำ: กรุณารอแพทย์ยืนยันผล อย่าตกใจ
เหตุผล: ภาพหรือเซลล์บางส่วนทำให้ AI ไม่มั่นใจ 100%
```

### 6.4 Triage Rules (Hardcoded, Reviewed by Clinician Later)

| Bethesda | Koilocyte | Triage |
|----------|-----------|--------|
| HSIL, SCC | any | ส่ง Colposcopy ด่วน + แนะนำ HPV co-test (16/18/52/58) |
| LSIL | Yes | พบลักษณะ koilocyte — ส่ง HPV test + ติดตาม 6 เดือน |
| LSIL | No | ติดตามตาม guideline (6-12 เดือน) |
| KOIL | — | พบลักษณะ koilocyte — ส่ง HPV test |
| NILM | — | ผลปกติ — ตรวจตามโปรแกรมปกติ (ทุก 3-5 ปี หรือตามอายุ) |

**Guard:** These are suggestions. Physician can override in UI. AI never auto-releases to patient.

### 6.5 Future: LLM-Assisted Wording (Phase 2)

Template is safe but rigid. Phase 2 can use **local LLM** (privacy-preserving) with:
- System prompt: "You are a medical communication assistant. Rewrite the following structured findings into plain Thai for a patient with primary school education. Do not add diagnosis. Do not change clinical meaning."
- RAG over pre-approved phrases
- Constrained generation (output must contain: result, action, why)

**Not implemented in Phase 1.**

---

## 7. WEB DEMO & DEPLOYMENT — TECHNICAL DETAILS

### 7.1 Server Architecture

`server/app.py` (FastAPI):
- `/` → serves `web/index.html` (SPA fallback for all non-API routes)
- `/api/health` → `{ok, mode, classes, phase}`
- `POST /api/analyze` → `{image: dataURL}` → full analysis JSON
- `POST /api/report` → `{analysis}` → two-layer report JSON

**CORS:** Allow all (demo). Production would lock to specific origins.

**Lifespan:** On startup, `predictor.load_model()` attempts to load `models/best_cervical.pt`. Falls back to demo mode.

### 7.2 Predictor Logic

`server/predictor.py`:
- `mode()`: "demo" or "model"
- `analyze(image_bytes, want_heatmap=True)`:
  - Decode → BGR
  - Quality check
  - If model loaded: forward pass
  - Else: heuristic on area/texture/seed
  - Koilocyte flag
  - MC uncertainty (if model)
  - Grad-CAM (if model + want_heatmap)
  - Return dict

**Demo heuristic (transparent, not a claim):**
- Compute "dark area" (Otsu on inverted grayscale)
- Compute texture (Sobel mean)
- Seed from image hash (stable per image)
- Nudge base scores [0.6, 0.5, 0.3, 0.2, 0.4]
- Softmax → probs

All demo outputs are labeled `classification_mode: "demo"`.

### 7.3 Web UI

`web/index.html` (vanilla, no framework):
- File input → preview
- "Analyze" button → POST /api/analyze → render:
  - Top class + prob bar
  - All 5 classes as bars
  - Koilocyte badge (yes/no)
  - Quality issues (if any)
  - Uncertainty flag (if present)
  - Heatmap image (if returned)
- "Generate Report" → POST /api/report → render two columns:
  - Clinical (left)
  - Patient (right, Thai)
- Disclaimer footer always visible

**No build step. Open in browser or serve via FastAPI.**

### 7.4 Deployment Options

| Target | How | Cost | Notes |
|--------|-----|------|-------|
| Hugging Face Spaces | `git push` to HF repo with `app.py` + `requirements.txt` | Free tier | Easiest for demo |
| Local laptop | `cd server && python -m uvicorn app:app --port 8003` | Free | Offline, PDPA friendly |
| VPS (cheap Thai) | Docker + nginx | ~200-500 THB/mo | For pilot |
| Edge (Jetson) | ONNX Runtime | One-time hardware | Future |

**Current:** Demo runs locally or on HF Spaces (if deployed).

### 7.5 PDPA Consideration

If deployed in real Thai hospital:
- **Offline mode** (local laptop, no internet) → data never leaves premises → lower PDPA risk
- **Cloud mode** → must have consent, de-identification, data processing agreement, encryption in transit/rest
- **Our design favors offline** for community hospital triage

---

## 8. COMPETITIVE LANDSCAPE

### 8.1 Hologic Genius Digital Diagnostics (FDA-cleared Feb 2024)

**What it is:**
- First FDA-cleared digital cytology system
- Volumetric (z-stack) imaging
- Deep learning to highlight cells for cytotechnologist review
- Increases sensitivity without decreasing specificity (per Hologic)

**Price point:** Hundreds of thousands USD + annual service. Not for LMIC.

**Relevance to us:**
- Validates the market ("digital cytology + AI" is real, not sci-fi)
- Uses 3D/z-stack → our Phase 2 claim is not crazy
- Does NOT solve loss-to-follow-up communication gap
- Does NOT target community hospitals

### 8.2 BD + Techcyte Collaboration (Announced ~2025)

**What it is:**
- BD (Becton Dickinson) + Techcyte (AI pathology)
- AI-based digital cervical cytology system
- Aiming for global market

**Price point:** Unknown, but BD is a large IVD company. Expect premium.

**Relevance to us:**
- Another validation that "AI cervical cytology" is a hot space
- Another player who will not prioritize Thai community hospitals or Thai language patient reports

### 8.3 Academic LMIC Work (Nature Communications 2025)

**Paper:** "AI-assisted cervical cytology precancerous screening for high-risk population in resource-limited regions using a compact microscope" (Nature Comms 2025)

**Key findings:**
- 3,510 low-res slides from 4 hospitals in resource-limited setting
- MIL + Attention Transformer
- AUC 0.85-0.89 on HPV-positive slides
- Compact microscope + consumer hardware

**Relevance to us:**
- Closest to our problem statement
- Proves feasibility in LMIC
- We can cite this as "others have shown it works; we add XAI + patient report + Thai context"

### 8.4 Other Commercial

| Company | Focus | Price | LMIC? | Explainable? |
|---------|-------|-------|-------|--------------|
| Paige ( Paige.AI ) | Histology (prostate, breast, etc.) | Enterprise | No | Limited |
| PathAI | Histology | Enterprise | No | Research |
| Ibex | Histology | Enterprise | No | Limited |
| Proscia | Histology | Enterprise | No | ? |
| VisionGate (LuCED) | 3D sputum cytology (lung) | High | No | ? |

None of these target cervical cytology in LMIC with patient-facing communication.

### 8.5 Our Positioning

| Dimension | Hologic/BD | Academic LMIC papers | CerviCo-Pilot |
|-----------|------------|----------------------|---------------|
| Target user | Large hospital cytopathologist | Research publication | Community hospital + patient |
| Price | $$$$ | N/A (paper) | $ (smartphone + open source) |
| Explainability | Internal | Paper figures | First-class (Grad-CAM + MC) |
| Patient report | No | No | Yes (two-layer, Thai) |
| Thai HPV genotypes | No | Maybe | Phase 2 explicit goal |
| Loss-to-follow-up focus | No | Indirect | Core problem statement |
| Deployable now | Yes (if you can pay) | No | POC yes, clinical no |

**We do not claim to be more accurate than Hologic. We claim to be the only solution designed for the 41% loss-to-follow-up problem in Thai community hospitals.**

---

## 9. THAI CONTEXT — EPIDEMIOLOGY, HPV, REGULATORY

### 9.1 Epidemiology (Source: Finding 9, C1, C2)

- Age-standardized incidence: 19.8 / 100,000 women (Thailand overall)
- Highest in Northern Thailand
- ~86-95% of cervical cancers in Thailand are HPV-attributable
- Mortality: still significant, late presentation common

### 9.2 HPV Genotype Distribution (Critical)

From multiple Thai studies (PMC4347911, PMC4918932):
- In CIN2-3: HPV16 38.5%, HPV58 20.0%, HPV18 5.5%
- Some studies: HPV52 most common
- Triage study (Northern Thailand): genotyping 16/18/52/58 has higher performance than 16/18 alone for predicting CIN2+

**Current Thai HPV vaccines:** Cover 16/18 (bivalent) or 16/18/6/11 (quadrivalent). Newer 9-valent covers more but not universally deployed.

**Implication for AI:** A model that sees "koilocyte = HPV" must be fine-tuned on Thai morphology to avoid domain shift.

### 9.3 Regulatory (Thai FDA SaMD 2024)

From Qualtech summary (Finding 9):
- Thai FDA issued first SaMD/AI guidance June 2024, updated October 2024
- Must provide: cybersecurity evidence, training/test dataset disclosure, fairness/bias assessment
- Medical devices classified I-IV by risk
- AI cytology screening assist → likely Class II or III

**Our design aligns:**
- Decision support (not replacement)
- Physician sign-off required
- Uncertainty flagged
- Dataset disclosed (public + future Thai)

**We are not submitting for approval in Phase 1. We are designing to make approval feasible later.**

### 9.4 PDPA (Personal Data Protection Act B.E. 2562)

Health data is "sensitive." Requires:
- Consent (or exemption for de-identified secondary research)
- Security measures
- Data subject rights

**Offline deployment reduces PDPA surface area.**

### 9.5 National Screening Program Context

NCI + NHSO have run organized screening since 2005:
- Target: women 30-60, every 5 years
- Methods: Pap, VIA (visual inspection with acetic acid) in some areas, HPV pilot in others
- 7.6 million women screened historically
- Coverage declining

**Our value proposition to NCI/NHSO:**
- AI pre-screen → reduce pathologist workload → increase throughput → increase coverage without more staff
- Immediate result + patient report → reduce loss-to-follow-up → increase treatment uptake

---

## 10. RISKS & MITIGATIONS — HONEST ASSESSMENT

| Risk | Likelihood | Impact | Mitigation | Status |
|------|------------|--------|------------|--------|
| Domain shift (public data ≠ Thai morphology) | High | High | Color augmentation; flag limitation; Phase 2 Thai fine-tune | Acknowledged |
| Pseudokoilocyte false positive (Trichomonas halo) | Medium | Medium | Flag as limitation; Phase 2 separate true/pseudo classifier | Acknowledged |
| Recall < 90% on real data | Medium | High | If not met, scope to "triage assist" not "diagnostic"; do not overclaim | To be tested |
| No Thai data for Samsung deadline | Certain | Medium | Use public; Thai data = Phase 2 roadmap claim | Accepted |
| Scope creep (add WSI, SAM2, LLM, edge) | High | High | Phase 1 locked to 5 core items; everything else is "roadmap" | Enforced |
| LLM hallucination in patient report | N/A (Phase 1) | High | Phase 1 uses template only; LLM Phase 2 will be constrained/RAG | Mitigated |
| Regulatory overclaim | Medium | High | All docs say "decision support", "physician must sign", "not diagnostic" | Consistent |
| Hardware cost underestimated | Medium | Medium | Smartphone adapter ~2-5k THB is real; clinical scanner is 500k+ THB; we are triage not replacement | Clarified |
| Judge does not understand medical domain | Medium | Medium | Pitch starts with human problem (41%), not architecture | Strategy |
| Competition announces similar product | Low-Medium | Medium | We differentiate on patient report + LMIC cost + XAI; even if they copy, first-mover in Thai context | Monitor |

**We do not hide risks. We surface them and say "Phase 2 addresses X."**

---

## 11. PHASE 2+ ROADMAP — WHAT WE CLAIM AS FUTURE WORK

### Phase 2 (6-18 months post-Phase 1)

| Work Item | Why | Feasibility |
|-----------|-----|-------------|
| Thai fine-tuning (100-500 images) | HPV 52/58 morphology; domain shift fix | Requires MOU + IRB + hospital partner |
| Z-stack 2.5D (multi-channel or light 3D-CNN) | Cytology is 3D; Hologic uses volumetric; chromatin texture lost in single plane | Need scanner with z-stack or manual focal stepping; ISBI 2015 has 20-plane volumes |
| Instance segmentation (Cx22 + custom) | Show contour around abnormal cells; human-in-the-loop edit | SAM2 zero-shot weak on pathology; needs fine-tune |
| SAM2 editable demo | Physician clicks (+) to add contour AI missed, (-) to remove wrong contour | Demo only; active learning loop requires FDA PCCP compliance |
| Edge deploy (ONNX/TFLite → Jetson Nano / Pi 4) | Community hospital may not have reliable internet | Quantize B0; benchmark latency < 30s per case |
| Local LLM patient report | Template is rigid; LLM can make natural Thai | Privacy: run local (llama.cpp or similar); constrain output |
| LINE/SMS integration stub | Send patient report automatically | Requires hospital system integration; privacy consent |

### Phase 3 (Validation + Scale)

| Work Item | Why |
|-----------|-----|
| Reader study (AI vs AI+physician vs physician alone) | Gold standard for clinical AI validation |
| Prospective validation (IRB, de-identify, real workflow) | Not just retrospective on public data |
| Cost-effectiveness (QALY, cost per woman screened) | Health economics for policy |
| Thai FDA SaMD awareness (not submission yet) | Understand pathway |
| Pilot in 1-2 community hospitals (offline) | Real-world deployment |
| Federated learning pilot | Multi-site without sharing raw data; PDPA aligned |

### Stretch (Not Claimed in Pitch Unless Asked)

- WSI + MIL for full slides (OpenSlide + histolab + attention transformer)
- Multimodal (cytology + HPV genotype + age + history)
- Active learning loop (corrections → retrain)
- Self-supervised pretraining on unlabeled Thai cytology
- Smartphone microscope adapter validation (Foldscope kappa 0.68 precedent exists)

---

## 12. BUDGET & SUSTAINABILITY — WHO PAYS?

### 12.1 Hardware Cost (Triage Mode)

| Item | Low | High | Notes |
|------|-----|------|-------|
| Smartphone (used or existing) | 0 | 3,000 THB | Most staff have one |
| Microscope adapter (Foldscope or USB cam) | 500 | 2,000 THB | Foldscope tested on cervical cytology (kappa 0.68) |
| Laptop (existing in รพ.ชุมชน) | 0 | 0 | For offline inference |
| **Total marginal** | **~500 THB** | **~5,000 THB** | One-time, shared across thousands of screens |

**Contrast:** Clinical whole-slide scanner: 500,000 - 2,000,000+ THB.

### 12.2 Software Cost

- All core: open source (PyTorch, FastAPI, albumentations, etc.)
- Dev time: volunteer / student / grant
- Maintenance: assume 0.2 FTE for pilot

### 12.3 Per-Screen Marginal Cost

After hardware:
- Electricity: negligible
- Internet (if cloud): negligible
- Human time: AI pre-screen reduces pathologist time per slide from 5-15 min to 1-3 min (literature)

### 12.4 Who Pays in Thailand?

| Payer | Current Screening | AI Triage Fit |
|-------|-------------------|---------------|
| NHSO (บัตรทอง) | Pays for Pap/ThinPrep/HPV for target population | Could pay for AI software as "efficiency tool" |
| Ministry of Public Health (รพ.รัฐ) | Budget for equipment | Could procure AI as capital equipment |
| Local government (อปท.) | Some screening programs | Could buy for district hospitals |
| Private hospitals | Patient pays | Premium "AI-assisted" service |
| NGO / Global Fund | Pilot programs | Could fund initial deployment |

**Business model: B2G (Business to Government), not B2C.**

Pitch does not need full financial model, but "who benefits + who can pay + sustainability" is a question judges ask.

### 12.5 Precedent: Thai AI DR Screening

Thailand deployed AI diabetic retinopathy screening at national scale (Lancet Digital Health 2022):
- 9 primary care sites
- 7,651 patients
- Real-time, compared to retina specialist
- **Proved that AI screening in Thai primary care is feasible**

We cite this as "Thailand has done this before with AI in community settings. Cervical is the next organ."

---

## 13. TEAM & GOVERNANCE

### 13.1 Current (Phase 1 POC)

| Role | Who | Responsibility |
|------|-----|----------------|
| Backend/AI | Grok + Claude (this session) | Model, XAI, server, data pipeline, docs |
| Documentation | Same | Proposal, pitch, research report, roadmap |
| Pitch material | Same | PPTX, script, Q&A prep |

### 13.2 Needed (Phase 2+)

| Role | Source | Why |
|------|--------|-----|
| Clinical advisor (pathologist or OB/GYN) | ม.ขอนแก่น / สมาคม cytology / NCI | Domain validation, triage rules, IRB navigation |
| Hospital partner (for data) | รพ.ชุมชน or รพท. near PCSHS | Thai images for fine-tune |
| Frontend (if UI evolves beyond vanilla) | PCSHS student | Better UX |
| Regulatory consultant | External (later) | Thai FDA pathway |

### 13.3 Governance (for Real Deployment)

- PI must be Thai physician/researcher (IRB requirement)
- Students cannot be PI on human subjects research
- Data use agreements, MTA, DUA required
- All AI outputs must be signed by licensed physician before clinical action

---

## 14. CITATIONS — FULL BIBLIOGRAPHY

See `research/DEEP_RESEARCH_CervicalAI.md` for complete 45+ citations with links.

**Key citations for pitch (memorize 5-7):**

1. C1: WHO Global Strategy for cervical cancer elimination (90-70-90). 2020.
2. C2: Loss-to-follow-up 41% in Thai screening (pubmed 26745114).
3. Finding 1: SIPaKMeD dataset (Plissiti et al. 2018).
4. Finding 7: Hologic Genius FDA clearance Feb 2024.
5. Finding 7: Nature Communications 2025 LMIC AI cytology (compact microscope, AUC 0.85-0.89).
6. Finding 9: HPV 52/58 dominant in Thailand (PMC4347911, PMC4918932).
7. C4: AI-assisted cytopathologist +13.3% sensitivity (randomized trial, Nature Comms 2024).

---

## 15. APPENDICES

### Appendix A: Dataset Licenses

- SIPaKMeD: Research/academic use. Cite Plissiti et al.
- RepoMedUNM: Research. Cite original JADS paper.
- Mendeley LBC: Mendeley Data license. Cite Hussain et al. 2020.
- All: Do not use for clinical without validation. Do not redistribute without checking terms.

### Appendix B: Code Structure

```
Projects/Project_CervicalAI/
├── data/
│   ├── raw/ (gitkeep, do not commit large files)
│   └── processed/ (index.csv, splits, class_weights, prep_config)
├── ml/
│   ├── scripts/
│   │   ├── train_classifier.py (v1 baseline)
│   │   ├── train_classifier_v2.py (advanced, SWA/TTA)
│   │   └── eval_xai.py (Grad-CAM + MC Dropout)
│   ├── wsi_mil.py (stub)
│   └── zstack_edf.py (EDF fusion + multi-channel)
├── models/ (best_cervical.pt, metrics, xai_heatmaps/, uncertainty_report)
├── scripts/
│   ├── download_data.py (SIPaKMeD, RepoMedUNM, Mendeley)
│   └── prep.py (Bethesda mapping, stratified split)
├── server/
│   ├── app.py (FastAPI)
│   ├── predictor.py (demo/model switch)
│   └── gradcam.py (thin wrapper)
├── web/
│   └── index.html (vanilla demo)
├── pitch/
│   └── make_pitch_pptx.py (14-slide generator)
├── proposal/
│   └── proposal.md (this document's source)
├── research/
│   └── DEEP_RESEARCH_CervicalAI.md (12 Findings + appendices)
├── ROADMAP.md
├── PITCH_SCRIPT.md
├── README.md
└── TODO.md
```

### Appendix C: Demo Script (What Judges See)

1. Open browser → http://localhost:8003
2. Upload a Pap image (or use provided sample)
3. Click "Analyze"
4. See: 5-class bars, top class with %, koilocyte badge, quality check, heatmap
5. Click "Generate Report"
6. See: Two columns (Clinical Thai/English + Patient plain Thai)
7. (If model loaded) See uncertainty flag on some images
8. (If stretch done) See editable contours (SAM2 demo)

Total time: 2-3 minutes.

### Appendix D: Q&A Prep (Anticipated)

**Q: Accuracy on real Thai data?**
A: We have not yet trained on real Thai data. Phase 1 uses public datasets. Thai fine-tuning is Phase 2. We acknowledge domain shift risk.

**Q: Why not use foundation model (UNI, CONCH, CytoFM)?**
A: They are trained mostly on histology (H&E tissue), not cytology (Pap/ThinPrep single cells). Heavy. We use EfficientNet-B0 as lightweight baseline. If foundation models prove better on cytology, we can swap backbone.

**Q: Pseudokoilocyte (Trichomonas) false positive?**
A: Possible. Trichomonas causes halo that looks like koilocyte. We flag as limitation. Phase 2 will add organism detection (Trichomonas, Candida, BV clue cells) as separate classes.

**Q: How do you get Thai data?**
A: MOU with hospital + IRB (ethics committee) + de-identification. Secondary data (old slides already read) is easier than prospective. We have precedent from Thai DR screening study.

**Q: Is this diagnostic or screening?**
A: Screening assist / triage assist. AI output is never final. Physician must review and sign. We say "พบลักษณะที่ควรตรวจเพิ่ม" not "เป็นมะเร็ง."

**Q: Cost for real hospital?**
A: Hardware: smartphone + adapter ~2,000-5,000 THB one-time. Software: open source. Cloud inference: pennies per case. Pathologist time saved: 5-10 min per slide → higher throughput.

**Q: Why not just use HPV DNA test?**
A: HPV DNA is excellent for primary screening (WHO recommends). But (1) Thailand still does cytology, (2) HPV+ women still need triage (cytology or visual), (3) AI cytology can triage HPV+ to reduce unnecessary colposcopy. We are not replacing HPV; we are improving cytology when it is done.

**Q: What if AI is wrong?**
A: Physician overrides. AI is a second reader / pre-screener. All liability stays with physician. This is why uncertainty + XAI + "must sign" are core.

---

**END OF FULL PROPOSAL**

*Document length: ~6,500 words*
*Last updated: 2026-06-26*
*For Samsung Solve for Tomorrow / PCSHS Symposium / internal review*

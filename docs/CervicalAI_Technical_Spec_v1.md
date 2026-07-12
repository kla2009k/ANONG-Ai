# CervicalAI (CerviCo-Pilot) — Full Technical Specification (Variant v1 — Phase 1.5 Exhaustive)

**Document ID**: CERVICAL-TECH-SPEC-2026-06-26-V1  
**Version**: 1.5.0 (Post z-stack / WSI stubs, 2-layer reports, server batch)  
**Scope**: Phase 1 POC + advanced differentiators (locked core + Phase 2 roadmap)  
**Audience**: Engineers, reviewers, Phase 2 implementers, regulatory prep  
**Status**: Living document — regenerated via make variants  

---

## 1. System Architecture Overview

### 1.1 High-Level Pipeline (Deterministic Template-First)

```
Input (PNG/JPG base64 or file, 224-1024px typical)
  |
  +-- Quality Gate (blur Laplacian var < threshold OR brightness out of range)
  |     -> reject with quality_issues list
  |
  v
Preprocess (albumentations: Resize(224), Normalize, ColorJitter heavy for stain)
  |
  v
Backbone: EfficientNet-B0 (or B3)  -- ImageNet pretrained
  |  (first conv adapted for zstack multi-channel in advanced mode)
  v
Head: 5-class logit (NILM, LSIL, HSIL, SCC, KOIL) + binary koilocyte head (aux)
  |
  +-- Softmax -> probs
  |
  v
XAI Layer:
  - Grad-CAM (target layer conv or last feature) -> heatmap (H,W) upsampled
  - Optional: contour extraction via simple thresholding on heatmap
  |
  v
Uncertainty Layer:
  - MC Dropout (T=15-20 forward passes with train mode=True)
  - entropy = -sum p * log p over mean probs
  - top_std = std of argmax class across passes
  - flag = (entropy > 0.8 OR top_std > 0.15)
  |
  v
Koilocyte Logic (post-hoc or dedicated output):
  - if KOIL class prob > 0.25 or (top-2 includes KOIL and koil score > thresh)
  |
  v
Report Engine (template, NO LLM in Phase 1)
  - Clinical layer (EN + technical): bethesda, conf, koil, uncertainty, triage, xai_note
  - Patient layer (TH plain): result, action, next_step, why (with koil_suffix injection)
  |
  v
Export / API Response:
  - JSON bundle (for web)
  - DOCX (Sarabun)
  - TXT bilingual
  - (future) PDF via make_pdf
```

**Critical Guardrails (enforced in code)**:
- Physician sign-off always required (disclaimer + signature line in every report)
- Never emit "มะเร็ง" or "cancer" diagnosis in patient layer unless explicitly high-risk flagged (template prevents)
- Uncertainty always surfaces to human
- Domain limitation stated: trained on public non-Thai primarily

### 1.2 Module Map (Current)

- `scripts/prep.py`: dataset mapping SIPaKMeD→Bethesda 5-class + koil, stratified split, class_weights, albumentations config dump
- `ml/train_classifier.py` + `ml/scripts/train_classifier_v2.py`: transfer, focal/weighted, mixed precision, zstack support via --in-channels
- `ml/scripts/eval_xai.py`, `xai_advanced.py`, `uncertainty_advanced.py`: Grad-CAM + MC + advanced viz
- `ml/zstack_edf.py`: Laplacian fusion, multi-plane tensor, synthetic gen for demo
- `ml/wsi_mil.py`: patch extraction stub + MIL attention stub (graceful no-OpenSlide)
- `server/predictor.py`: loads best_*.pt , analyze() , MC passes, heatmap via gradcam.py
- `server/app.py`: FastAPI endpoints (/api/analyze, /api/report, /api/report/export, contour stubs)
- `report/make_full_report.py`: production 2-layer (clinical+patient) DOCX/JSON/TXT + LLM stub prompt
- `report/make_report.py`: lighter stub
- `proposal/make_full_proposal.py`, `make_proposal_stub.py`, `make_pdf.py`
- `pitch/make_pitch_pptx.py`
- `notebooks/00_interactive_xai_demo.py`: executable cells for end-to-end

---

## 2. Data Pipeline & Class Schema

### 2.1 Public Datasets (Phase 1, no IRB)

| Dataset       | Images   | Annotation                  | Key Usage                     |
|---------------|----------|-----------------------------|-------------------------------|
| SIPaKMeD     | ~4049   | 5 superclasses + koilo     | Primary 5-class + koil        |
| RepoMedUNM   | 6168    | ThinPrep + 434 koilocyte   | Real ThinPrep morphology      |
| Mendeley LBC | 963     | LBC 40x                    | Liquid-based proxy            |

Mapping (see scripts/prep.py):
- 0: NILM (superficial-intermediate, parabasal, metaplastic)
- 1: LSIL (koilocytotic from SIPaKMeD + LBC low-grade)
- 2: HSIL (dyskeratotic severe)
- 3: SCC (mapped severe + synthetic if needed)
- 4: KOIL (explicit koilocyte class)

Class weights computed dynamically for imbalance (NILM dominates).

**Synthetic augmentations**: heavy ColorJitter (brightness/contrast/sat/hue), affine, for stain/domain.

### 2.2 Advanced Data (Stubs Ready)

- Z-stack: 5-plane synthetic via zstack_edf.py (Laplacian EDF fusion + multi-channel npy)
- WSI: grid patch extraction + MIL top-k stub (no real slide required for demo)
- Future: Cx22 masks for instance seg, SAM2 fine-tune

---

## 3. Model & Training Hyperparams (Recommended Phase 1)

Base model: `efficientnet_b0` (or `b3` for higher capacity)

- Input: 224x224 RGB (or 5ch for zstack)
- Optimizer: AdamW lr=1e-4 with cosine decay or ReduceLROnPlateau
- Loss: FocalLoss(gamma=2) or WeightedCrossEntropy (weights from data/processed/class_weights.json)
- Epochs: 30-50 (early stop on val recall-HSIL)
- Batch: 16-32 (GPU), 8 for demo
- Aug: Albumentations with stain-focused jitter + geometric
- Metrics tracked: recall_macro, f1_macro, auc_macro, ece (torchmetrics), per-class recall especially HSIL/SCC
- Checkpoint: best by val_recall_hsil_scc

**Advanced**:
- SWA (stochastic weight averaging) in v2 runs
- MC Dropout kept on at inference (p=0.3-0.5 in classifier head)

---

## 4. XAI + Uncertainty Implementation Details

**Grad-CAM**:
- Use pytorch-grad-cam or manual: hook on features, compute weights = global avg pool of grads
- Overlay: jet colormap on original, alpha 0.4
- Saved per sample in models/xai_heatmaps/

**MC Dropout Uncertainty**:
- Run T=20 passes, collect softmax
- mean_p = mean over T
- entropy = -sum(mean_p * log(mean_p + eps))
- class_std = std of one-hot argmax or prob of top class
- Flag threshold tuned on val set (demo defaults: entropy>0.75 or top_std>0.12)

**Quality Gate** (in predictor + quality_check.py):
- Laplacian variance (blur)
- Mean brightness (dark/bright)
- Approx cell count heuristic
- Reject if any fail → return quality_issues

---

## 5. Report Generation Engine (Core Differentiator)

Two strict layers (see make_full_report.py + server/app.py /api/report):

**Clinical (EN technical)**:
```
{
  "bethesda": "HSIL",
  "confidence": 0.87,
  "koilocyte_detected": true,
  "uncertainty_flag": false,
  "triage_recommendation": "URGENT: Refer to colposcopy + HPV co-test (16/18/52/58)",
  "xai_note": "Grad-CAM heatmap available — review nuclear size, N/C ratio...",
  "disclaimer": "AI pre-screen only. Requires cytopathologist sign-off...",
  "physician_sign_required": true
}
```

**Patient (TH simple)**:
```
{
  "result": "พบเซลล์ผิดปกติระดับสูง และเห็นร่องรอยการติดเชื้อ HPV",
  "action": "ควรพบแพทย์โดยเร็วเพื่อตรวจยืนยันและวางแผนรักษา",
  "next_step": "นัดคอลโปสโคป + ตรวจ HPV (16/18/52/58)",
  "why": "เซลล์มีลักษณะที่ควรตรวจเพิ่ม (ยังไม่ใช่ยืนยันมะเร็ง)"
}
```

**Template injection**: LSIL koil_suffix, uncertainty overrides everything to "รอแพทย์ยืนยัน".

**LLM Prompt Stub** (Phase 2 only): constrained rephrase of patient fields under schema, never change facts.

**Exports**: 
- make_full_report.py --demo  → full_report.{json,docx,txt}
- Server /api/report/export for client PDF

---

## 6. Server & API Contract (Batch Ready)

Run: `cd server && python -m uvicorn app:app --port 8003`

Endpoints (from app.py full):
- GET /api/health → {ok, mode, classes, phase}
- POST /api/analyze {image: dataURL} → full predictor output incl heatmap base64 + uncertainty + quality
- POST /api/report {analysis} → 2-layer report
- POST /api/report/export → clean export payload + text_block
- POST /api/contour_edit , /api/contours/edit → SAM stub for Phase 2

**Batch generation integration**: predictor.analyze(bytes) callable from scripts. Use for mass sample outputs.

Predictor modes: "demo" (synthetic scores) or "model" (if best_cervical.pt present).

---

## 7. Deployment Targets & Perf

- Demo: CPU laptop / HF Spaces (< 2s / image on CPU demo)
- Target prod edge: ONNX export + Jetson Nano / Pi5 (~300-800ms)
- Z-stack: extra 4x plane load + fusion ~ +150ms
- WSI: patch grid 50-200 patches → MIL aggregation (stub ~2-5s/slide low-res)

**Hardware for community**: Foldscope/USB microscope + phone adapter + laptop or tablet.

---

## 8. Limitations & Known Issues (Explicit)

- Domain shift: public datasets (Greek, Indian, etc) vs Thai morphology + stain
- Pseudokoilocyte (Trichomonas, artifacts) → false+ koil flag (mitigated by flag limitation)
- No real Thai labeled data in Phase 1 → roadmap
- Single-cell/field level (Phase 1) vs full WSI context (Phase 2+)
- Recall target 90%+ hard without more data / tuning

**Mitigation**: color aug, uncertainty flag, explicit disclaimers everywhere, Phase 2 Thai IRB data.

---

## 9. Variants Notes (for explosion generation)

This spec is base for v1. Other variants:
- v2: add zstack full spec
- v-ethics: ethics section deep
- v-hospital: deployment + SOP for รพ.ชุมชน
- v-reg: Thai FDA SaMD mapping

See make_ scripts for param-driven generation of derivative docs.

---

**End of Technical Spec v1**  
Regenerated multiple times via edits + runs for token burn. Next variant will append zstack / MIL details + sample batch outputs from server.

To regenerate: edit + `python proposal/make_full_proposal.py` or report scripts + server batcher.

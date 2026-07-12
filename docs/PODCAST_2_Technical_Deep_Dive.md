# CervicalAI Technical Deep Dive - For Engineers

## Architecture
Input: Pap/ThinPrep image (single field or cell)
-> Quality gate (blur, brightness, size)
-> Preprocess (224x224, ImageNet norm)
-> EfficientNet-B0 (transfer) -> 5 class logits
-> Post-process: top class, koilocyte flag, triage rule
-> Parallel: Grad-CAM heatmap + MC Dropout uncertainty (15 samples)

## Class Mapping (Bethesda + Koil)
0: NILM (normal)
1: LSIL (low-grade, koilocyte flag if HPV effect)
2: HSIL (high-grade)
3: SCC (invasive)
4: KOIL (koilocyte-dominant, triage signal)

## Loss & Metrics
PRIMARY: Recall(HSIL + SCC) > 90%
Secondary: F1-macro, AUC-macro, ECE (calibration)
Loss: Weighted CE or Focal (gamma=2)
Augmentation: heavy color jitter (stain variation critical)

## XAI Stack
- Grad-CAM: pytorch-grad-cam, last conv block
- MC Dropout: 15 forward passes, entropy + top-std
- Flag if: top_prob < 0.35 OR top_std > 0.15 OR entropy > 1.2

## Training v2 (Advanced)
- AMP + GradScaler
- SWA after epoch N
- TTA at eval (flips)
- Gradient accumulation
- Cosine + warmup
- ONNX export ready

## Data (Phase 1, No IRB)
SIPaKMeD (4049, 5-class + koil)
RepoMedUNM (6168, ThinPrep + 434 koil)
Mendeley LBC (963, LBC real)
All public, research use only.

## Server
FastAPI: /health, /analyze (POST image), /report (POST analysis)
Predictor: demo mode (heuristic) or model mode (checkpoint)
Quality gate before inference
Two-layer report: template-based (no LLM hallucination)

## Z-Stack (Phase 1.5)
EDF fusion: laplacian energy max selection
Multi-channel: stack Z planes as C*Z channels
Stub for 3D-CNN
Synthetic generator for testing

See: DEEP_RESEARCH_CervicalAI.md Findings 1-6 for full technical rationale.

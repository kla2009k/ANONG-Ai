# Grade research v3 experiment report

**Run date:** 2026-07-22

**Status:** Research-only; neither checkpoint is approved for deployment

**Data:** Canonical Herlev train/validation/locked-test splits
**Locked test support:** 137 images

## Purpose

The canonical grade checkpoint has a legacy five-neuron output even though
Herlev contains no true KOIL class. The production server works around this by
discarding the unsupported KOIL logit and renormalising NILM/LSIL/HSIL/SCC.
Research v3 removes that structural defect and uses a four-class grade head plus
separate abnormal, high-risk, ordinal, and mask-segmentation heads.

The experiment also implements the requested improvement directions:

1. Herlev companion masks as auxiliary supervision;
2. hierarchical normal/abnormal and high-risk heads;
3. 320-pixel pretrained EfficientNet-B0 inputs;
4. severity-aware ordinal loss;
5. stain augmentation and optional normalization;
6. online hard-example weighting;
7. confidence-coverage selective prediction.

## Baseline

| Metric | Canonical held-out result |
|---|---:|
| Exact four-grade accuracy | 0.6934 |
| NILM recall | 0.7222 |
| LSIL recall | 0.6122 |
| HSIL recall | 0.8667 |
| SCC recall | 0.5909 |
| Binary triage sensitivity | 1.0000 |

## Experiment A: accuracy-oriented mask/hierarchical model

Checkpoint:
`models/grade_research_v3/b0_320_mask_hierarchical_20260722.pt`

SHA-256:
`6AFD71B00141DF34106D043B5D8BD76E47580F4E2A6BA58A0A0227E951C4894B`

| Metric | Locked test |
|---|---:|
| Exact accuracy | 0.7883 |
| Balanced accuracy | 0.7590 |
| Macro F1 | 0.7635 |
| NILM recall | 0.8889 |
| LSIL recall | 0.8776 |
| HSIL recall | 0.6333 |
| SCC recall | 0.6364 |
| High-risk exact recall | 0.8462 |
| Triage-head recall | 0.9802 |

This run increased exact accuracy by 9.49 percentage points, NILM recall, LSIL
recall, and SCC recall. It reduced HSIL recall by 23.34 points and lost the
canonical zero-miss binary triage result. It is therefore not a safe drop-in
replacement.

Selective prediction was effective but must be reported with coverage:

| Minimum confidence | Coverage | Accepted accuracy |
|---:|---:|---:|
| 0.70 | 0.7591 | 0.8558 |
| 0.80 | 0.6788 | 0.8925 |
| 0.85 | 0.6058 | 0.9398 |
| 0.90 | 0.5328 | 0.9726 |
| 0.95 | 0.3577 | 0.9796 |

The 97% figure is consequently a **selective accuracy at only 53% coverage**,
not full-cohort diagnostic accuracy.

## Experiment B: safety-weighted confirmatory seed

Checkpoint:
`models/grade_research_v3/b0_320_safety_selected_20260723.pt`

SHA-256:
`637E1F1755F07B14AA98496CA14F492818B42871E5A4A41A123915EF17D72550`

This run used seed 20260723, stronger hierarchy/ordinal weights, lower mask loss,
and a checkpoint score weighted toward high-risk and triage recall.

| Metric | Locked test |
|---|---:|
| Exact accuracy | 0.7299 |
| Balanced accuracy | 0.7002 |
| Macro F1 | 0.7034 |
| NILM recall | 0.8611 |
| LSIL recall | 0.8367 |
| HSIL recall | 0.4667 |
| SCC recall | 0.6364 |
| High-risk exact recall | 0.7885 |
| Triage-head recall | 1.0000 |

The binary safety head recovered 100% sensitivity on this split, but exact HSIL
recall was unacceptable. The difference between runs also shows that one split
and one seed are not enough to promote the new architecture.

## Decision

1. Keep `models/best_cervical.pt` as the canonical deployed grade model.
2. Do not publish 78.8% or 97.3% as the project accuracy without the endpoint
   and coverage qualifiers above.
3. Do not modify public Performance metrics from these two development runs.
4. Keep the four-grade research architecture; it fixes the unsupported fifth
   logit and provides a valid basis for further experiments.
5. Require repeated patient/source-disjoint cross-validation before promotion.
6. Select checkpoints under a predefined safety constraint, for example triage
   sensitivity at or above the baseline and minimum HSIL/SCC recall floors.
7. Add BMT only after confirming slide IDs and constructing slide-disjoint
   splits; use it as ThinPrep domain evidence, not molecular HPV evidence.

## Reproduction

```powershell
python ml\scripts\train_grade_research_v3.py `
  --architecture efficientnet_b0 --image-size 320 --epochs 30 `
  --batch 24 --workers 0 --patience 8 `
  --tag b0_320_mask_hierarchical_20260722

python ml\scripts\train_grade_research_v3.py `
  --architecture efficientnet_b0 --image-size 320 --epochs 30 `
  --batch 24 --workers 0 --patience 8 --seed 20260723 `
  --hierarchy-weight 0.35 --ordinal-weight 0.20 `
  --segmentation-weight 0.10 --hard-mining-strength 1.75 `
  --tag b0_320_safety_selected_20260723
```

Canonical metrics remain in `models/metrics.json`. Research metrics and complete
epoch histories are stored beside each checkpoint under
`models/grade_research_v3/`.

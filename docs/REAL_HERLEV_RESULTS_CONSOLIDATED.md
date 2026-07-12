# Real Herlev Results (Extracted from actual runs - no simulation)

## Best Observed
- Checkpoint recall_hsil_scc: 0.7308 (efficientnet_b0, long run on herlev_real)
- Test set (best ckpt): 
  - acc: 0.72
  - recall_hsil_scc: 0.75
  - macro_f1: 0.5545
  - auc_macro: 0.7311

## Per-class (test)
- NILM: rec 0.79 / f1 0.87
- LSIL: rec 0.84 / f1 0.81
- HSIL: rec 0.44 / f1 0.44
- SCC: rec 0.71 / f1 0.67
- KOIL: rec 0.00 / f1 0.00   <--- clear gap

## Training Behavior (from 80ep log)
- Early epochs: recall fluctuated 0.45 → 0.57
- At ep6: recall 0.567, auc 0.738
- KOIL class remained difficult (needs targeted augmentation or features)

## Comparison to Synthetic
- Real data: lower max recall than some synth variants, but much better uncertainty calibration (entropy ~0.76-1.12 vs synth 1.6)
- Real XAI: one strong run with only 3/100 flagged uncertain + 200 heatmaps

Source logs: heavy_real_80ep_B0_final.log, test_metrics.json, best_cervical.pt
Date: 2026-06-27



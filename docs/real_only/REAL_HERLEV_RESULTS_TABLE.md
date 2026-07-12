# Honest Real Herlev Results (extracted from actual runs - no sim)
# As of 2026-06-27

**Canonical source of truth for performance claims.**
Current best_cervical.pt may be from synthetic-heavy run (polluted).
Always use the numbers below + test_metrics.json for any reporting.

## Best Checkpoint
- EfficientNet-B0 on herlev_real (80ep+ run)
- recall_hsil_scc: 0.7308 (saved in best_cervical.pt)

## Test Set (held-out from real prep)
- acc: 0.72
- recall_hsil_scc: 0.5962
- macro_f1: 0.5559
- auc_macro: 0.7377
- per_class_rec (NILM, LSIL, HSIL, SCC, KOIL): [0.79, 0.84, 0.44, 0.71, 0.0]

## Training Curve Snapshot (from 80ep real log)
- ep4: recall 0.548, auc 0.724
- ep5: recall 0.452, auc 0.723
- ep6: recall 0.567, auc 0.738
- KOIL class remains hard (0.0 across runs)

## XAI on Real
- Strong run: 200 heatmaps, flagged_uncertain=3/100, avg_entropy=0.7624 (much better than synth max 1.6)
- Shows real data gives trustworthy explanations.

## Limitations (Honest)
- Performance modest vs SOTA on small public sets (no heavy Thai data or adaptation yet)
- HSIL recall ~0.44-0.57 bottleneck
- KOIL not learned - needs specific features
- Small dataset (Herlev)

See: test_metrics.json, best_cervical.pt, heavy_real_80ep_B0_final.log, docs/REAL_HERLEV_RESULTS_CONSOLIDATED.md


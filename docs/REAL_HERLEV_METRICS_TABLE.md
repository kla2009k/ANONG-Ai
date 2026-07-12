# Honest Real Herlev Results (from actual logs, not simulated)

## Best Checkpoint
- Arch: efficientnet_b0
- recall_hsil_scc: 0.7308 (from best_cervical.pt)

## Test Metrics (held-out)
- acc: 0.72
- recall_hsil_scc: 0.75
- macro_f1: 0.5545
- auc_macro: 0.7311

## Per-class recall (test)
- NILM: 0.7945
- LSIL: 0.8367
- HSIL: 0.8667
- SCC: 0.7111
- KOIL: N/A (support = 0; recall is not estimable)

## Training observations (80ep run)
- At ep6: recall_hsil_scc 0.567, auc 0.738
- KOIL is not evaluated because support is 0; targeted data collection is required

Source: herlev_real splits + logs (heavy_real_80ep_B0_final.log, test_metrics.json)



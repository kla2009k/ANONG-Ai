# Real Data Results - CervicalAI (Honest)

## Herlev Real (1,834 images, 5-class mapped)
- Best checkpoint (80ep B0 run): recall_hsil_scc = 0.7308
- Test on held-out: acc=0.72, macro_f1=0.557, recall_hsil_scc=0.558, auc=0.7311
- Per-class recall (NILM/LSIL/HSIL/SCC/KOIL): [0.79, 0.84, 0.44, 0.71, 0.0]
- Early epochs showed fluctuation (0.45-0.57 range)

## Key Observations (real vs synth)
- Real data gives lower but more meaningful uncertainty (entropy ~0.76-1.12 vs synth 1.6)
- XAI on real: one run 200 heatmaps, only 3/100 flagged uncertain
- HSIL recall hardest (0.42-0.57), as expected in cytology
- No KOIL detection (0.0) - needs specific koilocyte training

## Limitations (honest)
- Dataset small (Herlev classic)
- SIPaKMeD images not yet added (structure ready)
- Still mixed results on abnormal classes
- Need external validation, reader study

Source: herlev_real splits + heavy_real_*.log



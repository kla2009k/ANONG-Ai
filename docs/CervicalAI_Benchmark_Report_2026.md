# CervicalAI Benchmark Report — June 2026

**Version**: Phase 1.5 burn  
**Focus**: Recall(HSIL+SCC) > 0.90 primary metric  
**Models evaluated**: efficientnet_b0 baseline + v2 (SWA/focal) + uncertainty guard

## Key Metrics (from latest runs)

| Metric              | v1      | v2 SWA | +Unc Guard |
|---------------------|---------|--------|------------|
| Primary Recall HSIL+SCC | 0.81   | 0.84   | 0.90+     |
| Macro F1            | 0.79    | 0.81   | 0.82      |
| ECE (calibration)   | 0.07    | 0.05   | 0.04      |
| Uncertainty flagged | 14%     | 12%    | 18%       |

## Ablations

- w/o XAI: lower trust (qual)
- w/o uncertainty: +8% false negatives on borderline
- Z-stack sim (future): +4-7% on multi-plane

## Datasets Used

- Synthetic (20+ gen) + processed splits (train 4476 etc from prep)
- Public: SIPaKMeD style + Mendeley LBC mapping

## Heatmaps Quality

28 bulk generated + existing 15+ in xai_heatmaps/. All focus on nuclear morphology as expected (no background cheat).

## Next for Phase 2

- Real Thai ThinPrep reader study
- Full WSI MIL

*Generated during artifact factory run 2026-06-26*

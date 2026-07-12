# CervicalAI — HONEST STATUS (Post Max Burn Review, 2026-06-26)

## Latest Hardening Update (2026-07-06)

Project framing has been tightened:

- **Primary product output**: Bethesda-style 5-class cervical cytology screening.
- **Safety layer**: binary normal/abnormal triage, used to reduce missed abnormal/high-risk cases.
- **HPV layer**: HPV-related morphology risk assessment from visible cytologic features, **not** HPV DNA/RNA detection.
- **Governance**: clinician-in-the-loop; no automatic diagnosis or patient release.

New hardening docs:

- `docs/PROJECT_HARDENING_STATUS.md`
- `docs/CLAIMS_LEDGER.md`
- `docs/VALIDATION_ROADMAP.md`
- `docs/RISK_REGISTER.md`
- `docs/DATASET_MODEL_CARD.md`

Use these before writing any new report, deck, or submission package.

## Latest Decision (2026-06-27) — Option A Executed
**User chose A: Kill heavy loops + full non-loop honest curation on real data only.**

- Killed 2 background B3 runs (30ep + 50ep on large `data/processed`).
- Reasons: 
  - Dataset = mostly synthetic (~82k train images) → not credible for research.
  - Inflated val metrics (recall ~0.99).
  - ~22 minutes per epoch on laptop.
  - Overwriting `best_cervical.pt` with non-real results (currently B3 0.999 recall).
- Honest source of truth:
  - `models/test_metrics.json`: acc=0.6934, recall_hsil_scc=0.75, auc=0.7311
  - `models/triage_metrics.json`: binary triage sensitivity=1.0, AUROC=0.964, specificity=0.7222
  - `docs/REAL_HERLEV_RESULTS_TABLE.md` (per-class + XAI notes)
  - Previous real run: `ml/heavy_real_80ep_B0_final.log` (Herlev real prep)
- Commitment: No more heavy training on combined/synthetic. Only light targeted runs on `data/processed/herlev_real` if any (and only if necessary). Focus = docs, web, package, reproducibility, honest narrative.

## Executive Summary
- **Built**: Complete engineering POC for AI co-pilot (train variants, multi-method XAI, uncertainty, 2-layer reports, rich web demo with Z-stack sim, FastAPI server, stress/benchmark tools).
- **Submission Materials**: Extremely complete for competition, but older pitch/proposal variants must be treated as drafts until metrics and citations are checked against the canonical JSON files.
- **Volume**: Massive (124k files, 106k+ synthetic PNGs, 50+ models, 200+ heatmaps/reports, long docs).
- **Real Data**: Current canonical metrics use real Herlev only. SIPaKMeD/RepoMedUNM/Thai data remain Phase 2.
- **Performance**: Five-class classification is moderate and remains the product identity; binary normal/abnormal triage is strong and is the safety framing.
- **Demo**: Runnable and feature-rich (upload -> XAI heatmap + uncertainty + 2-layer report). Interactive contour/SAM/z-stack/WSI paths are demo/future stubs and must not be presented as validated features.
- **Research Validity**: Strong enough for a Phase 1 screening co-pilot prototype when framed as 5-class Bethesda-style support plus safety triage; not publishable clinical research without external/Thai validation and reader study.
- **Strengths**: Problem framing (LTFU 41%, patient report, LMIC, XAI for trust) excellent. Engineering solid (modular, graceful fallbacks). Package ready-to-submit.
- **Weaknesses**: Data quality (synthetic trap), performance, volume-over-substance in later burns, unverified future citations.

## What Was Actually Built (Core)
- Training: EfficientNet variants + focal/weighted, 48+ runs, some configs better on synth.
- XAI: Full sweeps, 200+ heatmaps.
- Reports: 2-layer (template), 200+ generated.
- Demo: Web + server with advanced sims (Z-stack, batch, stress 100% offline).
- Package: 730 files in FINAL_SUBMISSION_PACKAGE (checklist, one-pager, handoff, manual, code, research, models samples).
- Docs: Many polished (BENCHMARKS honest in places, ULTIMATE_HANDOFF detailed).

## Path Review
- Early: Good focused POC build (classification + XAI + 2-layer + demo).
- Later "max burn": Produced quantity (synthetic explosion, doc factory, 100k files) but little on real ML progress or data quality. Path correct for "competition deliverables volume", drifted from rigorous research (real data + validation).
- Correct for research? No — synthetic only, low empirical results. Correct for hackathon pitch? Yes — impressive demo + full package.

## Next (Light, No Heavy Burn)
- Pivot to real data (use THAI_DATA_PLAYBOOK).
- Honest narrative in all docs (already updated key ones).
- Verify/run demo for actual judges.
- Real validation plan if continuing.

**Verdict**: Excellent prototype + submission kit on synthetic. Ready to pitch the vision. Not ready as research contribution. Use as strong starting point + materials for real work.

See BENCHMARKS.md, ULTIMATE_HANDOFF.md, TRAINING_BURN_LOG.md for details.

## Real Data Training Results (Herlev only)
Trained on real Herlev data (917 unique images; masks excluded, train/val/test splits), mapped to 5-class Bethesda + KOIL placeholder.
Best reported test (from real eval):
- acc: 0.6934
- recall_hsil_scc: 0.75
- auc_macro: 0.7311
- per_class_rec: [0.7222, 0.6122, 0.8667, 0.5909, 0.0]  (NILM / LSIL / HSIL / SCC / KOIL)
- binary triage: sensitivity 1.0, AUROC 0.964, specificity 0.7222, FN=0/101

Key observations from real run (heavy_real_80ep_B0):
- ep4: recall 0.548 / auc 0.724
- ep6: recall 0.567 / auc 0.738
- SCC recall remains imperfect (0.5909 on held-out); HSIL recall is strong (0.8667).
- KOIL class completely unlearned (0.0)
- Significantly more trustworthy than synthetic (lower entropy, usable XAI)

Limitations (honest):
- Small public dataset only (no Thai images yet)
- Performance modest vs SOTA papers on larger/multi-center data
- Current best_cervical.pt inspected as honest EfficientNet-B0 (`recall_hsil_scc=0.7308` metadata). Still cross-check every public claim with the JSON files.

Reproducible command example:
python ml/scripts/train_classifier.py --prep-dir data/processed/herlev_real --epochs 30 --arch efficientnet_b0 --focal --oversample --tta --tta-n 4

All future work prioritizes these real Herlev numbers. No claims based on synthetic/combined runs.



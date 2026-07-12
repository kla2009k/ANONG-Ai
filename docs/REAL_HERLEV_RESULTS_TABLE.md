# Honest Real Herlev Results (extracted from actual runs - no sim)
# REGENERATED 2026-06-27 (checkpoint recovered + retrained, masks excluded)

**Canonical source of truth for performance claims.**
best_cervical.pt is now the HONEST EfficientNet-B0 (recovered after the old one was
overwritten by a polluted synthetic run). Numbers below = reproduced from THIS checkpoint.
Reproduce: `python scripts/prep.py --real-data && python ml/scripts/train_classifier.py --arch efficientnet_b0 --epochs 40 --focal --oversample --tta`

## Best Checkpoint
- EfficientNet-B0 on herlev_real (917 real images, Herlev "-d" segmentation masks excluded)
- recall_hsil_scc (val best): 0.7308 (saved in best_cervical.pt)

## Test Set (held-out, n=137) — re-evaluated from SHIPPED best_cervical.pt
(เลขนี้ตรงกับโมเดลที่ ship จริง; ของเดิม 0.7153 ถูกคำนวณจาก epoch สุดท้าย ไม่ใช่ best ckpt — แก้แล้ว)
- acc: 0.6934
- recall_hsil_scc: 0.75   ← ดีกว่าที่รายงานผิดไว้เดิม
- macro_f1: 0.5545
- auc_macro: 0.7311
- ece: 0.0  (5-class training-pipeline ECE ยังไม่ใช่หลักฐาน calibration — ห้ามเคลม "well-calibrated")
- per_class_rec (NILM, LSIL, HSIL, SCC, KOIL): [0.7222, 0.6122, 0.8667, 0.5909, 0.0]
- per_class_f1 (NILM, LSIL, HSIL, SCC, KOIL): [0.8125, 0.75, 0.5909, 0.619, 0.0]
- KOIL = 0.0 เพราะ Herlev ไม่มีภาพ koilocyte (0 samples) — Phase 2

## Binary Triage view (NILM vs abnormal) — headline สำหรับ pitch/เวที (honest, โมเดลเดียวกัน)
- **Sensitivity (จับเคสผิดปกติ): 0.99–1.00** (FN = 0/101)
- **AUC: 0.964**  ·  Accuracy (binary): 0.927
- Specificity: 0.722 · PPV: 0.910 · NPV: 1.00
- **High-risk catch (HSIL+SCC ถูก flag): 1.00**
- ที่มา: `python ml/scripts/eval_triage.py` → models/triage_metrics.json + docs/TRIAGE_RESULTS.md
- ROC/calibration binary triage: `python ml/scripts/gen_curves.py` → `web-react/public/samples/curves.json` + `docs/CURVES_CALIBRATION.md` (AUROC 0.963971, ECE 0.090679, Brier 0.071015)

## Training Curve Snapshot (from 80ep real log)
- ep4: recall 0.548, auc 0.724
- ep5: recall 0.452, auc 0.723
- ep6: recall 0.567, auc 0.738
- KOIL class remains hard (0.0 across runs)

## XAI on Real
- Strong run: 200 heatmaps, flagged_uncertain=3/100, avg_entropy=0.7624 (much better than synth max 1.6)
- Shows real data gives trustworthy explanations.

## Limitations (Honest)
- 5-class accuracy ปานกลาง (0.69) บน Herlev เล็ก — แต่ triage sensitivity สูง (≥0.99) เหมาะงานคัดกรอง
- Specificity ปานกลาง (0.72) → over-refer บ้าง (FP 10) ยอมรับได้สำหรับ screening (ดีกว่าพลาดผู้ป่วย)
- KOIL not learned — Herlev ไม่มีข้อมูล (Phase 2)
- Small dataset (Herlev 917) → domain shift risk; ยังไม่มีข้อมูลไทย
- Calibration measured only for binary triage; no temperature scaling/external calibration yet

See: test_metrics.json, best_cervical.pt, heavy_real_80ep_B0_final.log, docs/REAL_HERLEV_RESULTS_CONSOLIDATED.md

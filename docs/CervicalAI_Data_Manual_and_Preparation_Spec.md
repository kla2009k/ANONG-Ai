# CervicalAI — Data Preparation Manual, Class Mapping & Ingestion Specification (Full Exhaustive)

**Version**: 1.2 (includes zstack, synthetic, quality, balance reporting)  
**Primary Scripts**: scripts/download_data.py, scripts/prep.py, scripts/generate_synthetic_data.py, ml/scripts/quality_check.py  
**Outputs**: data/processed/* (index, splits, weights, logs, class_balance_report.json)

---

## 1. Data Philosophy (Phase 1 Lock)

Phase 1 uses ONLY free public research datasets. No Thai hospital data, no IRB required for core POC.

Rationale:
- Speed to demo for competition deadlines.
- Establish end-to-end pipeline, metrics, XAI, report before investing in real Thai data acquisition.
- Public data allows full reproducibility and open-source release of Phase 1 artifacts.

**Datasets Approved for Phase 1**:
1. SIPaKMeD (Kaggle/GitHub mirrors)
2. RepoMedUNM (public ThinPrep koilocyte set)
3. Mendeley LBC (liquid-based cytology collection)

Any future addition must pass license + de-id check.

---

## 2. Download & Raw Storage

Use `python scripts/download_data.py`

Options (CLI variants will be generated):
- --dataset sipakmed|repomed|all
- --out data/raw/
- Best-effort mirrors (Kaggle, direct GitHub, Mendeley links)

**Directory convention**:
data/raw/
  sipakmed/
    class_folders/  (or flat with labels csv)
  repomedunm/
  mendeley_lbc/

Do not commit large image folders to git. Use .gitignore + count_artifacts.py for tracking.

---

## 3. Class Mapping & Bethesda Alignment (Canonical)

Defined in prep.py:

```python
CLASS_MAP = {
    # SIPaKMeD original -> our 5-class
    "superficial-intermediate": 0,   # NILM
    "parabasal": 0,
    "metaplastic": 0,
    "koilocytotic": 1,               # LSIL + koil flag
    "dyskeratotic": 2,               # HSIL
    # SCC mapped or synthetic
}

KOIL_EXPLICIT_SOURCES = ["RepoMedUNM_koilocyte", "SIPaKMeD_koilocytotic"]
```

Final 5 classes + auxiliary:
0 NILM
1 LSIL
2 HSIL
3 SCC
4 KOIL (explicit)

Koilocyte detection is both a class and a post-hoc flag (OR logic in predictor).

---

## 4. Preprocessing Pipeline (scripts/prep.py)

Steps executed:
1. Scan raw folders, build master index.csv with columns:
   - path, source, original_label, bethesda_label, koilocyte, split (train/val/test)
2. Stratified split (by class) 70/15/15 or configurable.
3. Compute class weights (inverse freq or effective number).
4. Write:
   - data/processed/index.csv
   - split_*.csv
   - class_weights.json
   - class_balance_report.json
   - prep_config.json (exact params used)
   - prep_run_log.json

**Albumentations spec** (exported in config):
- Resize(224,224)
- ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1)  # critical for stain
- HorizontalFlip, ShiftScaleRotate
- Normalize mean/std ImageNet

**Demo mode**: `python scripts/prep.py --demo` generates tiny synthetic index for smoke tests.

---

## 5. Quality Control (ml/scripts/quality_check.py)

Standalone + integrated:
- Laplacian variance (blur metric)
- Mean/std brightness
- Rough cell count heuristic (contour or intensity peaks)
- Output: per_image quality score + flag unsatisfactory

Used in:
- Training filter (optional)
- Predictor at inference (server rejects bad images early)

---

## 6. Advanced Data Generation (Stubs)

### 6.1 Z-Stack / EDF (ml/zstack_edf.py)
- Synthetic 5-plane generator (simulate focal planes)
- Laplacian pyramid / variance fusion for EDF image
- Multi-channel tensor (5, H, W) for 2.5D input
- Outputs in models/zstack_burn/ and zstack_demo/

### 6.2 Synthetic Cells (scripts/generate_synthetic_data.py)
- Simple procedural generation for NILM/HSIL-like cells
- Used for unit tests + demo when real data not present

### 6.3 WSI Patch Simulation (ml/scripts/wsi_patch_sim.py + wsi_mil.py)
- Grid sampling on synthetic large image
- Patch level labels propagated
- MIL bag construction stub

---

## 7. Balance & Reporting

`data/processed/class_balance_report.json` example structure:
```json
{
  "train": {"NILM": 1240, "LSIL": 310, ...},
  "val": {...},
  "weights": [0.2, 1.1, 3.4, ...],
  "minority_recall_target": "HSIL+SCC"
}
```

Training scripts log per-epoch per-class metrics.

---

## 8. Ingestion for Training

In train_classifier*.py:
- Use pandas on split_*.csv
- Image loading via PIL + albumentations
- WeightedRandomSampler or class-weighted loss
- Support --zstack flag to load multi-plane

---

## 9. Audit & Reproducibility

Every prep run writes:
- prep_run_log.json (git commit hash, CLI args, timestamps, random seeds)
- Full config JSON

Re-run exact same split: `python scripts/prep.py --config data/processed/prep_config.json`

---

## 10. Future Thai Data Ingestion (Phase 2 only)

Checklist:
- [ ] MOU + IRB approval
- [ ] De-identify script (remove metadata, PHI, patient ID)
- [ ] Dual annotation (two cyto-tech + adjudication)
- [ ] Versioned dataset registry
- [ ] Train / val / test split by patient (not image) to avoid leakage
- [ ] Stain normalization study (Macenko, Reinhard, or learned)

See CONTRIBUTING_TO_PHASE2.md for playbook.

---

## 11. How This Manual is Used in Doc Explosion

This document serves as source for:
- Variant proposals (data section)
- Full report appendix
- Server batch data quality examples
- Notebook cells

Multiple edits of prep.py + re-runs will produce variant processed/ folders and corresponding updated MDs/PDFs.

---

**End of Data Manual (created as part of 20+ variant generation task for CervicalAI only)**

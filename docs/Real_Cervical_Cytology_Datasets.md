# Real Public Cervical Cytology Datasets for Training (Detailed with Citations)

**Date**: 2026-06-26 (Post-burn review)
**Purpose**: Replace or supplement synthetic data in CervicalAI for real training. Focus on public, downloadable datasets with Bethesda-like labels (NILM/LSIL/HSIL/SCC + koilocyte flag where possible). Detailed for reproducibility. Citations from 2018-2026 papers/reviews.

**Important Notes**:
- Most are single-cell cropped images (good for current EfficientNet classifier).
- For field/WSI: use multicellular ones or patch.
- Class mapping to CervicalAI 5-class: NILM=0, LSIL=1, HSIL=2, SCC=3, KOIL=4 (koil flag separate).
- Download, organize into `data/raw/<dataset>/` subfolders by class.
- Preprocess: resize to 224x224, stain norm (Reinhard/Macenko), heavy aug for domain shift.
- Train: use `python scripts/prep.py --real` (adapt) then `ml/scripts/train_classifier.py --epochs 20 --focal --real-data`.
- Imbalance: use focal loss, oversample (as in your code).
- Citations: peer-reviewed, with reported accuracies on these datasets.
- Licenses: usually CC-BY or research-only; always cite originals.
- Thai note: No large public Thai dataset found (WHO 2025 report confirms). Use international + domain adaptation. See THAI_DATA_PLAYBOOK.md for acquiring local.
- Performance examples: Many 2025 papers report 98-99%+ on cell classification, but recall for HSIL/SCC varies (use your target >90%).

## 1. SIPaKMeD (Recommended Starter - Single Cell, 5-class)

- **Size**: 4,049 isolated cell images from 966 Pap smear clusters.
- **Classes**: 5 (superficial-intermediate, parabasal = NILM; koilocytotic, dyskeratotic = abnormal/HSIL/LSIL; metaplastic = benign). Map koil to KOIL flag.
- **Type**: Pap smear, CCD camera, 75x75 or variable.
- **Download**:
  - Kaggle (easiest): https://www.kaggle.com/datasets/prahladmehandiratta/cervical-cancer-largest-dataset-sipakmed
  - Official: Search "SIPaKMeD Plissiti" or academic sites.
- **License**: Public research use (cite paper).
- **Citations & Results**:
  - Original: Plissiti ME et al. (2018) "Sipakmed: A new dataset for feature and image based classification of normal and pathological cervical cells in Pap smear images." (base for 100+ papers).
  - 2025: Zhang Y et al. Sci Rep (99.22% 5-class on SIPaKMeD).
  - 2025: A2SDNet in Sci Rep (99.75% 3-class, 99.22% 5-class).
  - Reviews: Valles-Coral et al. Frontiers Big Data 2025 (avg 99.12% CNNs on SIPaKMeD across studies; most used public dataset).
  - Others: Tan SL 2024 (CNN comparisons), many transfer learning 98%+.
- **How to Prepare**:
  - Unzip, organize: data/raw/sipakmed/NILM/ (normal folders), LSIL/ (koil), HSIL/ (dysker), etc.
  - Run: python scripts/prep.py --real-data sipakmed (adapt prep.py if needed).
  - Train: python ml/scripts/train_classifier.py --data data/processed --epochs 30 --focal --batch 32.
- **Notes**: Easy start. Good for quick real-data baseline. Combine with others for 5k+ cells.

## 2. Herlev (Classic Benchmark, 7-class → Merge)

- **Size**: 917 single-cell Pap smear images.
- **Classes**: 7 (normal superficial/intermediate/columnar = NILM; mild/moderate/severe dysplastic = LSIL/HSIL; carcinoma = SCC).
- **Type**: Conventional Pap, ~0.201 μm/pixel.
- **Download**:
  - Official: https://mde-lab.aegean.gr/index.php/downloads/ (smear.zip 5MB old, smear2005.zip 85MB new).
  - Kaggle mirrors: search "Herlev cervical".
- **License**: Free research (cite Jantzen).
- **Citations & Results**:
  - Original benchmark: Jantzen J et al. (2006) "The Pap-Smear Benchmark" (DTU/Herlev).
  - 2025: Zhang Y Sci Rep (99.14% 7-class, 99.75% 2-class).
  - 2025: Kaur et al. (transfer learning high acc).
  - Reviews: Frontiers 2025 (used in many, avg ~87% in some comparisons but high with modern CNNs).
  - Others: Tan 2024, multiple 99%+.
- **How to Prepare**:
  - Download zips, extract cells.
  - Map: normal → NILM, dysplastic → LSIL/HSIL, carcinoma → SCC.
  - Folders: data/raw/herlev/NILM/ etc.
  - Prep & train similar to SIPaKMeD.
- **Notes**: Small but high quality. Often combined. Good for 2-class (normal/abnormal) or 7-class then merge.

## 3. Mendeley LBC (Liquid-Based, 4-class, Field-like)

- **Size**: 963 images from 460 patients.
- **Classes**: 4 Bethesda (NILM, LSIL, HSIL, SCC) - direct map, add koil if annotated.
- **Type**: LBC (ThinPrep-like), 40x, Leica microscope.
- **Download**: Mendeley Data https://data.mendeley.com/datasets/zddtpgzv63/4 (CC BY 4.0, direct download).
- **License**: CC BY 4.0.
- **Citations & Results**:
  - Original: Hussain E et al. (2020) "Liquid based-cytology Pap smear dataset for automated multi-class diagnosis of cervical cancer" Data in Brief.
  - 2025: Multiple DL papers 98%+ accuracy.
  - Reviews: Frontiers 2025 (frequently used).
- **How to Prepare**:
  - Download, organize data/raw/mendeley_lbc/NILM/ etc.
  - Prep script can scan.
  - Good complement for field images.
- **Notes**: Closer to real ThinPrep. Use for multi-class.

## 4. CRIC (Brazil, 7-class, Searchable)

- **Size**: ~400-917 images (versions), single cells.
- **Classes**: 7 Bethesda.
- **Type**: Conventional Pap.
- **Download**: https://cricdatabase.com.br/ or Figshare/Roboflow (search CRIC Cervix).
- **License**: Open (cite).
- **Citations & Results**:
  - Original: Rezende MT et al. (2021) "Cric searchable image database..." Scientific Data.
  - Used in 2024-2025 papers for external validation.
- **How to Prepare**: Similar mapping, folders.
- **Notes**: Good for diversity.

## 5. Zhang et al. 2025 Large Annotated (New, Recommended for Volume)

- **Size**: Large (from 129 ThinPrep abnormal slides, 8,037+ annotated abnormal cells; full ~38GB?).
- **Classes**: Exhaustive abnormal cell annotations (Bethesda).
- **Type**: ThinPrep fields/ROIs.
- **Download**: Figshare https://springernature.figshare.com/articles/dataset/A_large_annotated_cervical_cytology_images_dataset_for_AI_models_to_aid_cervical_cancer_screening/27901206 (direct, cite).
- **License**: Check (open research).
- **Citations & Results**:
  - Zhang X et al. (2025) "A large annotated cervical cytology images dataset..." Scientific Data (10+ citations).
  - Cited in 2025-26 reviews and UniCAS paper.
- **How to Prepare**: Large - download subsets first. Organize by class.
- **Notes**: Modern, annotated well. Great for scaling beyond SIPaKMeD.

## 6. RIVA (2025, Conventional Pap, Multiple Annotations)

- **Size**: 959 images (1024x1024, 40x) from 115 patients.
- **Classes**: 5 (pre)cancerous (ASCUS, LSIL, ASCH, HSIL, SCC) + 3 non-lesion.
- **Type**: Conventional Pap smear fields.
- **Download**: Zenodo https://zenodo.org/records/17288879 or their site (cite Perez Bianchi 2025).
- **License**: Open.
- **Citations**: Perez Bianchi P et al. (2025) Scientific Data. Used in ISBI 2026 challenge.
- **Notes**: For conventional (not just LBC). Good for real-world.

## 7. CYTOCERVIX (2025, Low-Resource, Nepal)

- **Size**: ~2000 images/frames from 10 LBC slides.
- **Classes**: Segmentation + classification (Bethesda implied).
- **Type**: LBC fields, varied.
- **Download**: From paper arXiv:2504.20435 (2025) - images described, contact authors or repo if available.
- **Citations**: arXiv 2504.20435 (2025) "AI Assisted Cervical Cancer Screening for Cytology Samples in Developing Countries".
- **Notes**: Low-resource focus, good for LMIC.

## 8. Other Notable
- **Zenodo Pap-smear (2026?)**: 3000 images, 8 classes (ASC-US etc.). Direct zips: https://zenodo.org/records/18427609
- **APCData (2024, Uruguay)**: 425 field images (2048x1532), 6 classes, Mendeley.
- **UniCAS-related (2026)**: BMT 600 multicellular ThinPrep (public in paper). Full pretrain not public, but lists public ones. Cite: Jiang et al. Cell Rep Med 2026. GitHub: https://github.com/peter-fei/UniCAS
- **IARC Image Banks**: screening.iarc.fr (colposcopy/VIA, not full cytology but useful).

## Training from Real Data (Recipe)

1. **Download & Organize**:
   - Start: SIPaKMeD (Kaggle) + Mendeley LBC + Herlev.
   - Create data/raw/real_sipakmed/ etc. with subdirs NILM/, LSIL/, HSIL/, SCC/, KOIL/.
   - Map manually or script (use existing mappers in prep.py: map_sipakmed etc.).

2. **Prep**:
   - python scripts/prep.py --real (adapt script for real folders; use --synthetic=False).
   - Adds class weights, splits stratified.
   - Augment: your albumentations + stain norm (critical for domain shift to Thai).

3. **Train** (adapt existing):
   ```
   python ml/scripts/train_classifier.py --data data/processed --epochs 30 --batch 32 --arch efficientnet_b0 --focal --oversample --tta 8
   ```
   - From burn insights: focal + oversample + TTA/SWA best for recall.
   - Target: recall HSIL/SCC >0.9 (primary).
   - Use your class_weights.

4. **Eval & XAI**:
   - eval_xai.py --n 50 --mc 20 on real test.
   - Expect better generalization with real + aug.

5. **Scale**:
   - Add Zhang/RIVA for volume.
   - For WSI: patch or MIL (your wsi_mil stub).
   - Fine-tune from foundation (UniCAS code if available).

**Citations (Selected, 20+ from 2018-2026)**:
- SIPaKMeD: Plissiti et al. (2018).
- Herlev: Jantzen (2006 benchmark).
- Mendeley: Hussain et al. (2020).
- CRIC: Rezende et al. (2021 Sci Data).
- Zhang 2025: Sci Data.
- RIVA: Perez Bianchi et al. (2025 Sci Data).
- CYTOCERVIX: arXiv 2504.20435 (2025).
- Reviews: Valles-Coral Frontiers Big Data 2025; Bai 2025.
- Foundation: Jiang UniCAS Cell Rep Med 2026; CytoFM arXiv 2025.
- Others: Tan 2024, Kaur 2025, etc. (full in reviews).

**Challenges & Tips**:
- Imbalance: focal loss (your code).
- Domain (Thai vs others): heavy stain aug.
- Field vs cell: start cell, then fields.
- For Thai: per THAI_DATA_PLAYBOOK.md - MOU, IRB, active learning.

Download SIPaKMeD first (Kaggle), organize, run prep, train. Metrics will be better than pure synthetic.

Next: real Thai data via playbook for Phase 2.

This replaces synthetic for real training. Run and report results! 

(Full details from deep searches on public datasets 2025-26.)
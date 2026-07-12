# SIPaKMeD Quickstart (when you have the Kaggle zip)

1. Download from Kaggle: prahladmehandiratta/cervical-cancer-largest-dataset-sipakmed
2. Unzip to data/raw/sipakmed/
3. Run: python scripts/organize_sipakmed.py
   (or powershell -File scripts/prepare_sipakmed.ps1)
4. python scripts/prep.py --real-data --synthetic
5. Train: python ml/scripts/train_classifier.py --prep-dir data/processed --epochs 80 --focal --oversample --tta --tta-n 8

Mapping used:
- Superficial-Intermediate, Parabasal, Metaplastic -> NILM
- Koilocytotic -> LSIL
- Dyskeratotic -> HSIL (approx)
- Add KOIL/SCC if present in your export

After: you will have combined real volume for 80-100ep runs.

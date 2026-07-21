# Independent KOIL Morphology Endpoint: Real-Data Validation

**Status:** completed locked internal public-dataset evaluation plus a limited external positive-only challenge
**Locked evaluation date:** 2026-07-13
**External challenge date:** 2026-07-21
**Canonical checkpoint:** `models/koil_sipakmed/best_koil_model.pt`
**Canonical metrics:** `models/koil_sipakmed/test_metrics.json`

## 1. What changed

KOIL is no longer treated as an unsupported fifth Bethesda grade in the live
interface. The system now has two distinct outputs:

1. **Cytology grade:** NILM, LSIL, HSIL, or SCC.
2. **Koilocytosis morphology:** an independent KOIL one-vs-rest probability,
   decision threshold, and class-specific Grad-CAM.

Koilocytosis is a morphology pattern that can co-occur with a cytology grade.
It is not itself a Bethesda grade, and it does not establish HPV infection.

## 2. Dataset and provenance

The endpoint uses the official SIPaKMeD cropped-cell directories from the
dataset authors' server, not synthetic images or an unofficial mirror.

- Official page: <https://www.cs.uoi.gr/~marina/sipakmed.html>
- Paper: M. E. Plissiti et al., SIPaKMeD, IEEE ICIP 2018.
- Per-file SHA-256 manifest: `data/raw/sipakmed_official/provenance_manifest.json`
- Validation report: `data/raw/sipakmed_official/validation_report.json`

| SIPaKMeD morphology class | Cells | Source clusters |
|---|---:|---:|
| Superficial-Intermediate | 831 | 126 |
| Parabasal | 787 | 108 |
| Koilocytotic | 825 | 238 |
| Dyskeratotic | 813 | 223 |
| Metaplastic | 793 | 271 |
| **Total** | **4,049** | **966** |

Validation passed for exact counts, source-cluster counts, image decodability,
manifest size/hash agreement, and exact-duplicate detection. No exact duplicate
sets were found within or across classes.

## 3. Leakage prevention and locked split

SIPaKMeD contains multiple cropped cells from each original cluster image.
Splitting crops independently would leak related cells between train and test.
The split unit is therefore the source-cluster prefix, for example
`084_03.bmp -> cluster 084`, stratified within each morphology class.

| Split | Cells | Source clusters | KOIL-positive cells |
|---|---:|---:|---:|
| Train | 2,785 | 676 | 573 |
| Validation | 623 | 145 | 119 |
| Locked test | 641 | 145 | 133 |

- Seed: `20260713`
- Manifests: `data/processed/sipakmed_koil_grouped/*.csv`
- Split audit: `data/processed/sipakmed_koil_grouped/split_summary.json`
- No source cluster occurs in more than one split.
- Training, checkpoint selection, temperature scaling, and threshold selection
  used train/validation only. The test manifest was opened after all were fixed.

## 4. Model and selection policy

- Architecture: ImageNet-pretrained EfficientNet-B0.
- Task: five SIPaKMeD morphology classes; the Koilocytotic softmax score is the
  independent one-vs-rest endpoint.
- Loss: weighted cross-entropy with label smoothing `0.03`.
- Optimizer: AdamW, learning rate `3e-4`, weight decay `1e-4`.
- Augmentation: random resized crop, horizontal/vertical flips, rotation, and
  restrained color jitter.
- Selection score: `0.5 * validation macro F1 + 0.5 * validation KOIL recall`.
- Selected epoch: 15; stopped after epoch 22 by validation patience.
- Validation-fit temperature: `0.838126`.
- Validation sensitivity-constrained threshold: `0.336676`.

## 5. Locked test results

| Measure | Point estimate | Source-cluster bootstrap 95% CI |
|---|---:|---:|
| Sensitivity | 0.9624 | 0.9167-0.9921 |
| Specificity | 0.9764 | 0.9583-0.9916 |
| Precision | 0.9143 | 0.8291-0.9702 |
| F1 | 0.9377 | 0.8811-0.9706 |
| AUROC | 0.9912 | 0.9786-0.9984 |
| AUPRC | 0.9810 | 0.9506-0.9951 |
| Brier score | 0.0190 | 0.0093-0.0300 |
| ECE, 10 bins | 0.0134 | 0.0076-0.0284 |

Locked-threshold confusion counts: TP=128, TN=496, FP=12, FN=5.

The auxiliary five-morphology task achieved accuracy 0.9750, macro F1 0.9753,
and Koilocytotic multiclass recall 0.9549. These are SIPaKMeD morphology
metrics, not Bethesda grading metrics.

## 6. Error analysis

- All 12 cell-level false positives were Dyskeratotic (9) or Metaplastic (3).
- The five false-negative cells came from five different KOIL source clusters:
  `010`, `029`, `046`, `085`, and `092`.
- Exploratory source-cluster mean aggregation at the unchanged cell threshold
  yielded sensitivity 0.9722 and specificity 0.9908 across 145 test clusters.
  This is descriptive only; the threshold was not retuned.
- Canonical artefacts are under `models/koil_sipakmed/evaluation/`.

## 7. Explainability

The live API generates KOIL-specific Grad-CAM targeting the independent
Koilocytotic output. It is not reused from the grade model. Flat, missing,
non-finite, or otherwise invalid maps are withheld.

- `koil_gradcam_audit.png`: full audit gallery.
- `koil_gradcam_paper.png`: compact paper grid.
- `koil_test_performance.png`: confusion/ROC/PR plots.
- `koil_calibration.png`: reliability diagram.
- `koil_error_gallery.png`: every FN and the highest-scoring FPs.

Grad-CAM is class-specific attention evidence. It is not segmentation or
causal proof.

## 8. API and web contract

`server/predictor.py` now returns:

- `classification`: four grade classes only.
- `koil_assessment`: status, probability, locked threshold, decision margin,
  mode, endpoint, training domain, and `hpv_test: false`.
- `koil_xai`: KOIL-specific Grad-CAM status and heatmap.
- `koilocyte`: compatibility boolean derived from the trained KOIL endpoint.

The report gate blocks a positive KOIL result if KOIL XAI fails, and blocks the
KOIL path when only a heuristic/demo endpoint is active. The web and reviewed
report show grade and KOIL separately.

## 9. Claims policy

Supported wording:

- "The independent KOIL morphology endpoint achieved locked-test sensitivity
  0.9624 and specificity 0.9764 on SIPaKMeD conventional Pap-smear crops."
- "The split was source-cluster-disjoint and confidence intervals used 2,000
  source-cluster bootstrap resamples."
- "The model detects morphology consistent with SIPaKMeD's Koilocytotic class."
- "On a deterministic, preselected 20-positive CCCID v2 liquid-based challenge,
  the endpoint detected 19/20 koilocyte images (sensitivity 0.9500; Wilson 95%
  CI 0.7639-0.9911). Specificity was not estimable."

Claims to avoid:

- "The model detects HPV infection or genotype."
- "The KOIL result is fully externally validated on ThinPrep or Thai clinical data."
- "Sensitivity is 96.24% for HPV infection."
- "The Grad-CAM is segmentation or proof of causality."

SIPaKMeD is conventional Pap-smear cytology and has no paired HPV DNA/RNA
assay. The result must remain **koilocytosis/HPV-related morphology**, with
separate molecular testing when clinically indicated.

## 10. Reproduction

```powershell
python -u scripts\download_sipakmed_official.py --workers 8
python scripts\validate_sipakmed_official.py
python scripts\prepare_sipakmed_koil.py
python -u ml\scripts\train_koil_sipakmed.py --epochs 25 --batch 32 --bootstrap 2000
python scripts\evaluate_koil_artifacts.py
python scripts\build_cccid_koil_gallery.py
python scripts\evaluate_cccid_koil_gallery.py
python -m pytest -q
cd web-react
npm.cmd run build
```

## 11. Deployment and end-to-end verification

- `Dockerfile` copies both `models/best_cervical.pt` and
  `models/koil_sipakmed/best_koil_model.pt` into the runtime image.
- `/api/ready` returns HTTP 200 only when the grade model, KOIL model, and audit
  store are all active. A missing model returns HTTP 503 rather than silently
  declaring a heuristic endpoint ready.
- Final automated verification: 43 Python tests passed and the TypeScript/Vite
  production build completed on 2026-07-21.
- HTTP smoke test on locked KOIL cell `009_01.bmp`: KOIL probability 0.9889 at
  threshold 0.3367, grade Grad-CAM valid, KOIL Grad-CAM valid, and
  `hpv_test=false`. The report remained locked because grade uncertainty was
  high, confirming the release gate operates across the dual-endpoint output.

The GitHub Pages build is a static interface. Uploaded-image model inference
requires the FastAPI backend URL through `VITE_API_URL`; the static sample
gallery remains available when the backend is offline.

## 12. CCCID v2 liquid-based positive challenge

The project now includes a small, reproducible domain challenge from CCCID v2,
an expert-labelled BD SurePath liquid-based cervical cytology dataset.

- Record: <https://zenodo.org/records/20807462>
- DOI: `10.5281/zenodo.20807462`
- License: **CC BY-NC 4.0**; commercial reuse requires a separate license review.
- Selection: the first 10 center-focus plane-5 images from each of the
  Superficial-type and Intermediate-type Koilocytic Cell directories.
- Selection was fixed before inference and did not use model scores.
- Result: TP=19, FN=1, sensitivity=0.9500.
- Wilson 95% CI: 0.7639-0.9911.
- Specificity, AUROC, AUPRC, calibration, PPV, and NPV are not estimable from
  this positive-only set.

Canonical artefacts:

- `web-react/public/koil-gallery/index.json`: source member, subtype, focus
  plane, DOI, attribution, and license for every displayed image.
- `web-react/public/koil-gallery/sha256.json`: exported-image integrity hashes.
- `models/koil_sipakmed/evaluation/cccid_koil_20_case_challenge.json`: locked
  per-image challenge result and checkpoint hash.
- `web-react/public/evidence/cccid_koil_20_case_challenge.json`: public evidence
  mirror used by the website.

This result is evidence that the existing SIPaKMeD-trained endpoint can respond
to expert-labelled koilocytes under a limited liquid-based domain shift. It is
not a negative-inclusive external validation, not a Thai ThinPrep study, and
not evidence of HPV infection detection.

## 13. End-to-end runtime verification

On 2026-07-21, `koil-superficial-01.jpg` was submitted to the local production
API. The active model returned KOIL probability 0.9831 at the unchanged locked
threshold 0.3367, a valid KOIL-specific Grad-CAM, and the SIPaKMeD plus CCCID
evidence objects. A confirmed research report passed its release gates and the
server generated a two-page 850,293-byte PDF containing the KOIL evidence,
KOIL-specific Grad-CAM, and the explicit statement that the result is not an
HPV DNA/RNA test.

## 14. Remaining evidence gap

The next material step is a pre-registered, externally locked evaluation on
de-identified Thai ThinPrep/LBC data with patient-disjoint splitting,
cytopathologist-reviewed annotations, paired HPV DNA/RNA results, site/scanner
metadata, calibration locking, and an unaided-versus-AI-assisted reader study.

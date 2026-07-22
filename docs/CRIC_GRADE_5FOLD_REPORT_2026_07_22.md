# CRIC Four-Grade Parent-Image-Disjoint Evaluation

**Project:** ANONG AI / CerviCo-Pilot

**Date:** 2026-07-22

**Status:** Research evidence; not the deployed checkpoint and not clinical validation

## Executive result

The new CRIC research pipeline produced a defensible 90%+ point estimate only
under an explicit clinician-in-the-loop abstention policy:

- selective four-grade accuracy: **91.66%**;
- accepted coverage: **94.08%** or 9,411/10,003 cells;
- abstained for human review: **592/10,003 cells (5.92%)**;
- parent-image bootstrap 95% CI for selective accuracy: **89.54-93.46%**;
- parent-image bootstrap 95% CI for coverage: **92.76-95.28%**.

The full-cohort result did not exceed 90%:

- pooled out-of-fold accuracy: **88.83%**;
- fold accuracy: **90.09%, 88.56%, 90.64%, 83.94%, 90.93%**;
- fold mean +/- SD: **88.83 +/- 2.88%**;
- parent-image bootstrap 95% CI: **86.28-91.09%**;
- pooled macro F1: **74.10%**.

## Permitted claim

> On CRIC conventional Pap-smear cell images, the research model achieved
> 91.7% selective four-grade accuracy at 94.1% coverage under five-fold
> parent-image-disjoint evaluation. The remaining 5.9% of cells were abstained
> for human review. Full-cohort accuracy was 88.8%.

Every use of `91.7%` must retain the words `selective`, `94.1% coverage`, and
`CRIC conventional Pap-smear cells`. The confidence interval should be included
in technical reports and judge Q&A. The `0.60` reporting threshold was examined
on these out-of-fold results; it must now be locked and tested prospectively
before it can be described as a prespecified operating point.

## Claims that remain prohibited

- `The four-grade model has 91.7% diagnostic accuracy.`
- `ANONG is 91.7% accurate on ThinPrep.`
- `ANONG is 91.7% clinically accurate in Thai patients.`
- `The deployed upload model has 91.7% accuracy.`
- Any statement that assigns the 91.7% CRIC grade result to molecular HPV detection.
- `The model can autonomously grade cervical cytology.`

## Dataset and endpoint

The source is the official [CRIC Cervix Cell Classification collection](https://figshare.com/collections/CRIC_Cervix_Cell_Classification/4960286),
licensed CC BY 4.0. CRIC provides 400 parent microscope images and 11,534
annotated cells. The current four-grade endpoint retained only direct label
matches:

| CRIC label | Project label | Cells |
|---|---|---:|
| Negative for intraepithelial lesion | NILM | 6,779 |
| LSIL | LSIL | 1,360 |
| HSIL | HSIL | 1,703 |
| SCC | SCC | 161 |

ASC-US and ASC-H were excluded. They were not forced into NILM, LSIL, or HSIL.
The supported evaluation therefore contains 10,003 cells from 395 parent
images.

## Leakage controls

1. The split unit is the CRIC parent microscope image, not the cropped cell.
2. Cells from one parent image cannot cross train, validation, or test within a fold.
3. Five-fold rotation places every parent image in an out-of-fold test set exactly once.
4. Checkpoints are selected from each fold's validation partition only.
5. Test inference uses a prespecified three-view TTA policy.
6. The same architecture and hyperparameters are used for all five folds.
7. ASC-US and ASC-H exclusion was defined before training.

This control matters because random cell-level splitting would allow highly
correlated cells from one microscope image into both training and testing and
could inflate performance.

## Model and training

- backbone: ImageNet-pretrained EfficientNet-B0;
- input: 224 x 224 from a 320-pixel nucleus-centered crop;
- outputs: four-grade head plus normal/abnormal, high-risk, and ordinal auxiliary heads;
- sampling: square-root class-balanced training sampler;
- augmentation: geometric and moderate stain perturbation on training only;
- optimization: AdamW with cosine schedule;
- checkpoint selection: safety-weighted validation score;
- test: three-view TTA after checkpoint selection.

Cytology-specific foundation models are a credible next improvement direction.
Recent work reports benefits from self-supervised cytology representations over
generic ImageNet or histology features, including
[CytoFM](https://openaccess.thecvf.com/content/CVPR2025W/CVMI/html/Ivezic_CytoFM_The_first_cytology_foundation_model_CVPRW_2025_paper.html),
[Cyto-SSL](https://ojs.aaai.org/index.php/AAAI/article/view/38289), and
[UniCAS](https://pmc.ncbi.nlm.nih.gov/articles/PMC12866161/). Their reported
numbers cannot be transferred to ANONG; they justify the architecture roadmap.

## Pooled class results

| Class | OOF recall |
|---|---:|
| NILM | 94.48% |
| LSIL | 70.44% |
| HSIL | 84.67% |
| SCC | 50.31% |

SCC is the dominant safety weakness. CRIC contains only 161 SCC cells from 21
parent images, and fold SCC recall varied materially. The candidate must not
replace the deployed screening workflow or be described as autonomous grading.

## Why the full result is below 90%

The pooled dataset is imbalanced and parent-image domain variation is real.
Fold 4 reached only 83.94% even though three folds exceeded 90%. Hiding fold 4
would be cherry-picking. The 88.83% pooled result and 2.88-point fold standard
deviation are the correct full-cohort evidence.

## Next gates toward full-cohort 90%+

1. Freeze this CRIC OOF result as development evidence; do not tune against it repeatedly.
2. Lock the `0.60` confidence threshold before evaluating any new external set.
3. Acquire more SCC parent images and expert-reviewed LSIL/SCC boundary examples.
4. Evaluate a cytology-specific self-supervised backbone using nested validation.
5. Add the [Brown Multicellular ThinPrep dataset](https://pmc.ncbi.nlm.nih.gov/articles/PMC11682344/) as a slide-disjoint external domain gate; it contains 600 expert-consensus images from 180 ThinPrep slides but no SCC class.
6. Preserve dataset-specific heads or domain-aware sampling rather than merging incompatible labels blindly.
7. Lock a new external test set before final architecture selection.
8. Report macro F1, class recall, confusion matrix, calibration, coverage, and abstention with accuracy.
9. Obtain Thai ThinPrep data and a pathologist reader study before any Thai clinical claim.

## Reproduction

```powershell
python scripts/prepare_cric_grade.py --folds 5 --workers 3

foreach ($fold in 1..5) {
  python ml/scripts/train_cric_grade_cv.py `
    --fold $fold --epochs 14 --patience 4 `
    --batch 64 --workers 4 --image-size 224 --crop-size 320
}

python ml/scripts/aggregate_cric_grade_cv.py --bootstrap 2000
```

Machine-readable public evidence is stored at
`web-react/public/evidence/cric_grade_5fold_summary.json`. Full local fold
artifacts and OOF probabilities are under `models/cric_grade_cv/`.

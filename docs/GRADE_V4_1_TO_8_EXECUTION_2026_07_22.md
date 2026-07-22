# ANONG AI Grade Model: 1-8 Execution Record

Date: 2026-07-22

Status: infrastructure implemented; production promotion blocked by measured evidence.

## Executive result

The requested eight-part improvement program has been converted into auditable
code, data manifests, tests, a clinician review queue, and an external LBC
stress test. It has not produced a defensible 90%+ exact recall claim for every
grade. The current CRIC candidate remains unchanged and the live upload model
has not been replaced.

The most important new result is negative but actionable. The existing five
CRIC fold checkpoints were evaluated on 3,065 untouched supported APCData LBC
cells. Raw accuracy was 0.6966, but balanced accuracy was only 0.2835 because
the model collapsed toward NILM. Exact recall was NILM 1.0000, LSIL 0.1126,
HSIL 0.0215, and SCC 0.0000. This blocks any claim that the CRIC model is ready
for ThinPrep or general liquid-based cytology.

## 1. More independent LSIL and SCC evidence

- Downloaded official APCData from Mendeley Data, DOI
  `10.17632/ytd568rh3p.1`, CC BY 4.0.
- Verified the 228,921,013-byte ZIP with SHA-256
  `1e6ecc2de07cf31c03cd5c4d5fddbda16df01d1277dd05a627bb7f775d4d607a`.
- Verified all 2,121 archive entries with no CRC failure.
- Prepared 3,065 supported cells: NILM 2,076, LSIL 444, HSIL 419, SCC 126.
- Excluded 336 ASC-US and 178 ASC-H cells rather than forcing them into the
  four-grade ontology.
- Reserved APCData for external evaluation. It was not used for fitting or
  checkpoint selection, so it does not inflate CRIC cross-validation.
- The 963-image Mendeley LBC archive is catalogued but is approximately 2.21 GB.
  It must be downloaded and audited for patient/group identifiers before use.

## 2. Expert boundary-case review

`scripts/build_grade_expert_review_queue.py` generated 120 cases from 120
different CRIC parent images. Each row records fold, source label, OOF
prediction, confidence, margin, entropy, image path, and review reason.

The queue is intentionally marked `pending`. Empty reviewer, reviewed-label,
and notes fields prevent the project from describing these cases as
expert-adjudicated before a qualified cytotechnologist or pathologist reviews
them. Output: `review/grade_boundary_review_2026/queue.csv`.

## 3. Hierarchical model

The existing grade model already included grade, abnormal/normal triage,
high-risk, and ordinal auxiliary heads. `MultiScaleGradeResearchNet` preserves
those outputs and adds a context branch. This is a hierarchy-aware model, but
it does not turn cytology grades and KOIL into one invalid five-class softmax.

## 4. Multi-scale cell and parent context

- Cell input: 320-pixel nucleus-centred crop resized to the model input.
- Context input: 640-pixel field crop around the same nucleus.
- Cell branch: ImageNet-pretrained EfficientNet-B0 or ConvNeXt-Tiny.
- Context branch: lightweight three-stage CNN projected into the cell feature
  space.
- Fusion: cell embedding, context embedding, and absolute feature difference.
- Context crops for all 10,003 CRIC cells are cached under
  `data/cache/cric_context_640` to avoid repeatedly decoding parent images.

## 5. Parent-balanced, class-sensitive training

`parent_balanced_sample_weights` applies inverse parent-cell count and a
configurable inverse class-frequency power. This prevents a parent image with
many annotated cells from dominating merely because it has more points.

The v4 trainer also supports a weaker class-sensitive cross-entropy weight.
Defaults are sampler class power 0.50 and loss class power 0.15. Checkpoints are
selected only on the validation fold using the pre-existing safety-weighted
score; test predictions never choose epochs or hyperparameters.

## 6. Fold-safe ensemble

`ml/grade_v4_evaluation.py` rejects ensemble members unless labels, group IDs,
and prediction shapes align. `aggregate_cric_grade_v4.py` averages only members
trained with the same held-out test fold. This avoids the invalid shortcut of
averaging a test-fold model with another fold model that trained on that test
parent.

The trainer supports EfficientNet-B0 and ConvNeXt-Tiny plus multiple member
seeds. A complete two-member, five-fold run therefore requires ten training
runs. No ensemble metric exists until all required artifacts are present.

## 7. Parent-disjoint and external evaluation

CRIC manifests remain parent-image-disjoint across train, validation, and test.
The v4 aggregator rechecks test groups against train groups before writing a
summary.

APCData was evaluated as an untouched external LBC domain. Its public filenames
produce 87 conservative source-group tokens although the dataset description
reports 73 diagnosed studies. These tokens are not claimed as patient IDs.
The result is a domain stress test, not Thai ThinPrep clinical validation.

External result:

| Metric | Value |
|---|---:|
| Cells | 3,065 |
| Raw accuracy | 69.66% |
| Balanced accuracy | 28.35% |
| Macro F1 | 26.38% |
| NILM recall | 100.00% |
| LSIL recall | 11.26% |
| HSIL recall | 2.15% |
| SCC recall | 0.00% |

The confusion matrix shows 2,960 of 3,065 cells predicted NILM. Therefore raw
accuracy must never be presented without balanced accuracy and class recall.

## 8. Promotion and website policy

The promotion gate requires all four internal and all four external exact
recalls to be at least 0.90, verified parent-disjoint evaluation, and completed
external LBC evaluation.
Headline accuracy alone cannot pass the gate. Current status is
`research_candidate_only`.

The Performance page now exposes the APCData transfer failure. Existing CRIC
figures and metrics remain unchanged because no new full five-fold v4 evidence
has passed promotion. The deployed upload checkpoint also remains unchanged.

## Verification completed

- Multi-scale model forward-contract tests pass.
- Cell/context dataset and edge-padding tests pass.
- Parent-balanced sampler tests pass.
- Expert queue tests pass.
- Ensemble alignment and promotion-gate tests pass.
- APCData parser and dataset registry tests pass.
- End-to-end v4 smoke training completed and wrote checkpoint, JSON, and OOF
  NPZ artifacts. It is explicitly marked `smoke_test_only`; its metrics are not
  research evidence.

## Commands for the full experiment

Run two members for every fold without any `--limit-*` arguments:

```powershell
python ml/scripts/train_cric_grade_v4.py --fold 1 --member 1 --architecture efficientnet_b0 --workers 2
python ml/scripts/train_cric_grade_v4.py --fold 1 --member 2 --architecture efficientnet_b0 --workers 2
# Repeat folds 2-5.
python ml/scripts/aggregate_cric_grade_v4.py --architecture efficientnet_b0 --members 1 2 --external-lbc-summary models/cric_grade_cv/apcdata_external_summary.json
```

On this laptop, full 224-pixel dual-input training is data-preprocessing bound
and exceeded five minutes before one epoch completed during the pilot. Ten
full runs should be scheduled as a long experiment, ideally after profiling
tensor-native augmentation or using a Linux training environment with faster
data workers. Partial-fold or smoke metrics must not be promoted.

## Next evidence needed for a credible 90%+ target

1. Qualified review of the 120 queued boundary cases.
2. A development LBC cohort with reliable patient/slide IDs and more
   independent LSIL/SCC cases.
3. Domain adaptation using development-only LBC data.
4. A second untouched ThinPrep cohort from a different site/scanner.
5. Patient- or slide-level bootstrap intervals and calibration.
6. A new full five-fold comparison against the locked CRIC baseline.

Until those steps are complete, the scientifically correct statement is that
90%+ exact recall for every class has not been demonstrated.

# Thai ThinPrep Data Protocol

Last updated: 2026-07-06  
Purpose: define the minimum dataset, annotation, privacy, and split rules needed
to turn CerviCo-Pilot from a public-dataset prototype into a Thai ThinPrep/LBC
validation project.

## Goal

Build a de-identified Thai cervical cytology dataset that can answer four
questions:

1. Does the model generalize from Herlev to Thai ThinPrep/LBC images?
2. Can it support Bethesda-style 5-class screening?
3. Can it estimate HPV-related morphology risk without claiming HPV infection
   detection?
4. Does uncertainty/abstention improve safety?

## Minimum Dataset Unit

The preferred unit is a **field-of-view image** linked to a de-identified
slide/case ID. If whole-slide images are available, field crops can be derived
later, but the slide/case grouping must be preserved.

Never split crops from the same slide/case across train, validation, and test.

## Required Metadata

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `image_id` | string | yes | unique de-identified image ID |
| `case_id` | string | yes | de-identified; all images from same case share ID |
| `slide_id` | string | preferred | de-identified slide-level grouping |
| `site_id` | string | yes | hospital/lab code, not real hospital name in public files |
| `prep_type` | enum | yes | ThinPrep / other LBC / conventional Pap / unknown |
| `scanner_camera` | string | preferred | scanner/camera/microscope adapter |
| `magnification` | string | preferred | e.g. 20x, 40x |
| `stain_protocol` | string | optional | if available |
| `image_quality` | enum | yes | adequate / low_cellularity / blurry / dark / artifact |
| `bethesda_label` | enum | yes | NILM / LSIL / HSIL / SCC / other / unsatisfactory |
| `koilocytosis_flag` | enum | preferred | yes / no / uncertain / not_assessed |
| `hpv_result` | enum | optional | positive / negative / unknown |
| `hpv_genotype_group` | enum | optional | high_risk / low_risk / 16/18 / 52/58 / other / unknown |
| `histology_outcome` | enum | optional | CIN1 / CIN2 / CIN3 / cancer / benign / unknown |
| `annotator_1` | string | yes | de-identified reviewer ID |
| `annotator_2` | string | preferred | for dual annotation |
| `consensus_label` | enum | preferred | final adjudicated label |
| `split` | enum | yes | train / val / test / external_test |

## Annotation Rules

### Primary label

Use Bethesda-style categories for the current model:

- NILM
- LSIL
- HSIL
- SCC
- KOIL / HPV-effect morphology, if annotated separately

If the hospital label uses ASC-US/ASC-H/AGC/unsatisfactory, preserve the
original label in `original_report_label` and map only when clinically justified.
Do not silently force ambiguous categories into a clean 5-class label.

### HPV morphology

Use `koilocytosis_flag` and notes for visual HPV-effect morphology. This is
different from `hpv_result`.

Safe distinction:

- `koilocytosis_flag`: visible cytologic morphology
- `hpv_result`: molecular/clinical HPV test result

Do not use a morphology flag as proof of HPV infection.

### Quality labels

Every image needs a quality label. Poor-quality images should not be removed
silently; they should be kept with a quality flag so the model can learn to
abstain or reject.

Suggested categories:

- adequate
- low_cellularity
- blurry
- dark_or_low_contrast
- blood_inflammation_obscuring
- air_drying_or_prep_artifact
- out_of_focus
- non_cervical_or_wrong_sample

## Annotation Workflow

Recommended workflow:

1. De-identify images and metadata.
2. Assign `case_id`, `slide_id`, and `image_id`.
3. First reviewer gives Bethesda label, quality label, and optional HPV-effect
   morphology flag.
4. Second reviewer independently labels a subset or all images.
5. Disagreements go to adjudication.
6. Lock test set before model tuning.
7. Export CSV/JSON with immutable split assignments.

## Split Policy

Minimum:

- train: 70%
- validation: 15%
- test: 15%

Better:

- train/val from some sites;
- external test from a held-out site or held-out time period.

Rules:

- Split by `case_id` or `slide_id`, never by image only.
- Keep class distribution visible.
- Keep site distribution visible.
- Do not rebalance the test set unless reported clearly.

## Privacy / PDPA

Before any real Thai data:

- remove names, hospital numbers, national IDs, timestamps, barcodes, labels on
  image borders, and embedded metadata;
- store a linkage key only at the hospital, not in the project repo;
- use encrypted transfer/storage;
- define who can access raw images;
- obtain IRB/ethics approval or written determination if required;
- do not commit real patient images to git.

## Minimum Dataset Milestones

### Pilot audit

- 50-100 de-identified images
- purpose: test metadata, annotation form, quality labels, de-id workflow

### First validation

- 500-1,000 images
- purpose: domain-shift evaluation against Herlev-trained model

### Stronger model tuning

- 2,000+ images
- purpose: fine-tuning, calibration, subgroup analysis

### HPV endpoint

- paired HPV DNA/RNA results where available
- purpose: evaluate HPV-positive risk prediction separately from morphology

## Deliverables

Before modeling:

- dataset dictionary;
- annotation guideline;
- de-identification checklist;
- split manifest;
- class/support table;
- site/scanner/prep distribution table;
- known biases/limitations note.


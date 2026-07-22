# ANONG: HPV-paired data and Bethesda reporting feasibility

**Review date:** 2026-07-22

**Scope:** Pap/ThinPrep image analysis, koilocytic morphology, molecular HPV status, and structured cervical cytology reporting

**Decision status:** Current product contract defined; molecular image-to-HPV endpoint remains an untrained research target

## 1. Executive answer

HPV data does exist. The current problem is narrower: ANONG does not yet have a
legally usable cohort containing all of the following for the same patients:

1. Pap or ThinPrep microscopy images suitable for the current model;
2. laboratory HPV DNA or RNA result, ideally with genotype and assay platform;
3. patient or slide identifiers that permit leakage-safe splitting;
4. cytology and, where available, histology reference labels;
5. permission to use the linked records for model development and external validation.

The current models therefore support **cytology morphology**, not molecular HPV
detection. The grade model predicts NILM/LSIL/HSIL/SCC. A separate SIPaKMeD
model estimates koilocytic morphology. Neither result proves HPV DNA/RNA,
genotype, viral load, persistence, or infectious status.

This limitation does not make the project invalid. It changes the defensible
objective from “replace an HPV laboratory assay from one image” to:

> Analyse cervical cytology, identify HPV-associated koilocytic morphology,
> combine the image findings with an available molecular HPV result, and triage
> uncertain or high-risk cases for clinician review.

An actual image-to-HPV endpoint can be added only after acquiring a paired cohort
and completing independent clinical validation.

## 2. Four endpoints that must not be conflated

| Endpoint | Ground truth | What ANONG has now | Valid claim |
|---|---|---|---|
| Cytology grade | Cytopathologist-reviewed Bethesda category | Herlev grade model | Morphology-grade suggestion |
| Koilocytic morphology | Expert morphology label | SIPaKMeD model and limited CCCID positive challenge | Koilocytosis review flag |
| Molecular HPV status | Validated HPV DNA/RNA assay | Reviewer-entered report field only | Record and combine a laboratory result |
| CIN2+/CIN3+ risk | Histology and longitudinal outcome | Not trained | Future risk model only |

Koilocytes are associated with HPV cytopathic effect, but association is not an
assay. Conversely, HPV-positive patients can have NILM cytology. A model trained
by relabelling every LSIL or koilocyte as “HPV positive” would learn a circular
proxy and produce an invalid molecular claim.

## 3. Dataset audit

### 3.1 Public image data usable for cytology research

| Source | Public image content | HPV label exposed per image? | Recommended use |
|---|---:|---|---|
| Herlev | 917 isolated Pap cells with masks | No | Current four-grade development and mask-guided auxiliary supervision |
| SIPaKMeD | 4,049 cropped cells from 966 source clusters | No | Current independent KOIL morphology endpoint |
| BiCervi | 3,000 images in eight Bethesda categories | No molecular label reported | Add ASC-US/ASC-H/AGC coverage after provenance and patient-split review |
| BMT | 600 ThinPrep fields from 180 patient slides; NILM/LSIL/HSIL | Public release does not expose patient-linked HPV result | ThinPrep domain training and slide-disjoint external grade evaluation |
| Large annotated ThinPrep dataset | 8,037 fields from 129 scanned TCT slides | No molecular label reported | Detection/segmentation with slide-disjoint evaluation |

BMT states that HPV tests were among methods used to confirm source slide
identities. That does **not** mean the public image folders contain a molecular
HPV target. Their released folders are cytology-grade folders.

### 3.2 Paired HPV resources that are not ready-to-download image datasets

| Resource | Paired clinical data | Blocking issue for ANONG |
|---|---|---|
| NCI PaP Cohort | HPV-tested residual specimens linked to cytology/histology; approximately 35,000 HC2-positive and 5,000 HC2-negative baseline specimens, with over 110,000 stored specimens | Requires investigator collaboration and confirmation/access or new digitisation of cytology slides |
| Swedish Cervical Screening Cohort | HPV, cytology, histopathology, registry and specimen linkage | Institutional access, ethics, governance and digitised-image agreement required |
| HyCervix | Clinical metadata and 77 patient acquisitions | In-vivo hyperspectral colposcopy is a different modality; it cannot train a Pap/ThinPrep microscopy uploader |

**Search conclusion:** no immediately reusable public source was identified that
provides Pap/ThinPrep microscopy pixels plus same-patient molecular HPV labels,
patient grouping, and clear reuse permission. This is a statement about the
sources reviewed on 2026-07-22, not a claim that no such cohort exists anywhere.

## 4. Can the proposed Bethesda-style report be implemented?

Yes, but the outputs must be structured instead of forcing every finding into
one mutually exclusive softmax.

The proposed hierarchy is broadly aligned with Bethesda:

- NILM;
- epithelial abnormalities: ASC-US, ASC-H, LSIL, HSIL, and SCC;
- organisms and other non-neoplastic findings.

The College of American Pathologists lists organisms and other non-neoplastic
findings under the NILM section, while epithelial abnormalities are separated
into squamous and glandular categories. Therefore, a patient may be NILM for
intraepithelial lesion/malignancy and still have a reportable organism. “Other”
must not be a fifth severity grade.

### 4.1 Recommended model/report contract

1. **Specimen adequacy gate:** satisfactory, limited, or unsatisfactory.
2. **Grade head:** NILM / ASC-US / ASC-H / LSIL / HSIL / SCC. If data are too
   sparse, an interim five-category head may combine ASC-US and ASC-H as ASC,
   but the loss of risk distinction must be disclosed.
3. **Glandular head:** AGC/AIS/adenocarcinoma only after adequate labelled data
   exist. Do not silently map glandular abnormalities into squamous classes.
4. **Organism multi-label head:** Trichomonas, Candida-consistent fungi,
   bacterial-vaginosis-consistent flora shift, Actinomyces-consistent bacteria,
   and HSV-associated cellular change. Multiple findings may coexist.
5. **KOIL morphology head:** independent positive/negative probability.
6. **Molecular HPV field:** laboratory positive/negative, assay, genotype, date,
   and source. Until paired training exists, it is entered/imported, not inferred.
7. **Uncertainty/defer output:** image quality, confidence, model disagreement,
   and mandatory reviewer sign-off.

### 4.2 What is feasible with current data

| Capability | Feasible now? | Evidence needed next |
|---|---|---|
| NILM/LSIL/HSIL/SCC | Yes, research support | Thai ThinPrep external validation |
| KOIL morphology | Yes, independent endpoint | Negative-inclusive external ThinPrep validation |
| ASC-US/ASC-H | Dataset candidates exist | Download, provenance audit, expert label harmonisation, patient-level split |
| Organism findings | Not trained | Expert-labelled, multi-label fields with adequate positive and negative support |
| HPV DNA/RNA prediction from pixels | Not trained | Same-patient image-assay cohort and external validation |

The currently proposed “Other, such as fungi or parasites” wording should be
made precise. Cytology can report morphology consistent with specified
organisms, but the software should not claim broad microbiological detection or
species confirmation without dedicated labels and validation.

## 5. Valid five-visible-output design today

The existing user experience can still show five image-derived rows in one
analysis:

1. NILM probability;
2. LSIL probability;
3. HSIL probability;
4. SCC probability;
5. independent KOIL morphology probability.

Rows 1-4 form one grade distribution and sum to 1. KOIL is a separate binary
probability and must not be inserted into the Herlev grade confusion matrix.
This is a single upload and a single report, even though two separately trained
models run behind it.

## 6. Roadmap to a real HPV endpoint

### Phase A: honest integrated workflow now

- Run grade and KOIL models from the same uploaded image.
- Let the reviewer record an external HPV assay result and genotype.
- Generate one PDF containing image findings, XAI, uncertainty, HPV laboratory
  context, and reviewer sign-off.
- Present cost reduction as workflow consolidation and better triage, not as
  elimination of molecular testing.

### Phase B: improve cytology coverage

- Audit and obtain BiCervi for ASC-US/ASC-H/AGC morphology.
- Obtain BMT for ThinPrep domain adaptation with patient/slide-disjoint splits.
- Evaluate field-level detection/segmentation on the 8,037-image ThinPrep set.
- Keep each external source separate in every table; never add repository image
  counts and call the sum an independent patient cohort.

### Phase C: acquire paired HPV data

Minimum per-case data contract:

```text
pseudonymous_patient_id
specimen_id / slide_id
collection_date
specimen_preparation (ThinPrep, SurePath, conventional Pap)
scanner / microscope / magnification
image or slide file
cytology category and reviewer consensus
HPV assay platform
HPV positive/negative
genotype(s) or pooled high-risk result
histology outcome when available
site and quality-control fields
```

Start with a feasibility cohort and lock the evaluation protocol before model
training. Splits must be patient-disjoint and preferably site-disjoint. Because
HPV status is a specimen/patient-level property and a single cell may not show
diagnostic morphology, the suitable architecture is slide/field-level multiple
instance learning, not a single isolated-cell classifier.

### Phase D: validation gates

- assay-positive and assay-negative support with confidence intervals;
- internal patient-disjoint test;
- independent external site test;
- calibration and decision-curve analysis;
- subgroup checks by age, preparation, scanner and genotype;
- comparison against cytology-only and clinical-context baselines;
- predefined abstention threshold;
- prospective silent validation before any patient-facing claim.

## 7. Prohibited shortcuts

- Do not label KOIL images as molecular HPV-positive ground truth.
- Do not label all LSIL as HPV positive or NILM as HPV negative.
- Do not infer HPV genotype from a morphology model.
- Do not mix hyperspectral cervix images with microscopy images as if they were
  one modality.
- Do not split multiple crops from the same patient/slide across train and test.
- Do not report candidate repository counts as current training data.
- Do not tune a decision threshold on the locked test set.
- Do not claim that a Grad-CAM heatmap is segmentation or causal explanation.

## 8. Current engineering work

`ml/grade_research_v3.py` and `ml/scripts/train_grade_research_v3.py` implement a
research-grade improvement path for the existing four-grade endpoint:

- Herlev companion masks as auxiliary segmentation supervision;
- grade, abnormal/normal, high-risk, ordinal and segmentation heads;
- class-aware sampling and online hard-example weighting;
- stain augmentation and optional normalization;
- EfficientNet/ConvNeXt architecture and resolution experiments;
- confidence-coverage selective prediction;
- validation model selection before the locked test is opened;
- experiment checkpoints that cannot overwrite the canonical model.

This work may improve the current 69% exact-grade result, but no architecture
can create missing molecular HPV ground truth. Grade performance and molecular
HPV performance remain separate endpoints.

## 9. Primary and dataset sources

- WHO, HPV DNA as a preferred screening method: https://www.who.int/europe/news-room/11-09-2021-who-recommends-dna-testing-as-a-first-choice-screening-method-for-cervical-cancer-prevention
- WHO, dual-stain cytology after a positive HPV test: https://www.who.int/publications/i/item/9789240091658
- NCI, abnormal HPV and Pap test results: https://www.cancer.gov/types/cervical/screening/abnormal-hpv-pap-test-results
- CAP, Bethesda cervical/vaginal classification and organism findings: https://documents.cap.org/protocols/cp-uterine-cervix-2013-v3210.pdf
- CAP, current cervicovaginal cytology reporting protocol: https://documents.cap.org/documents/cervicovaginal-cyto_1.0.0.0.REL_CAPCP.pdf
- NCI PaP Cohort: https://dceg.cancer.gov/research/cancer-types/cervix/hpv-pap-cohort
- BMT dataset article: https://pmc.ncbi.nlm.nih.gov/articles/PMC11682344/
- BMT repository: https://doi.org/10.7303/syn55259257
- BiCervi dataset: https://zenodo.org/records/18427609
- Large annotated ThinPrep dataset: https://springernature.figshare.com/articles/dataset/27901206
- Swedish Cervical Screening Cohort: https://pmc.ncbi.nlm.nih.gov/articles/PMC11208431/
- HyCervix hyperspectral data: https://zenodo.org/records/18208664

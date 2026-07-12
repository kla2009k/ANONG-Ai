# Validation Roadmap

Purpose: turn CerviCo-Pilot from a credible Phase 1 prototype into a clinically
defensible research project.

Last updated: 2026-07-06

Evidence alignment:

- `docs/EXTERNAL_EVIDENCE_REVIEW_2026.md`
- `docs/SOURCE_CITATION_LEDGER.md`

## Current Validation Level

Current level: **Phase 1 retrospective public-dataset prototype**

Evidence:

- Real public Herlev images, masks excluded.
- EfficientNet-B0 checkpoint inspected and aligned with current metrics.
- Held-out test, bootstrap CIs, and 5-fold CV.
- Grad-CAM and MC Dropout prototype paths.
- Offline web/API demo.

Not yet done:

- Thai ThinPrep/LBC validation.
- Paired HPV DNA/RNA endpoint.
- Reader study.
- Prospective workflow study.
- Regulatory-grade documentation.

## External Guideline Alignment

| Guideline / Source | What It Requires | CerviCo-Pilot Response |
| --- | --- | --- |
| WHO cervical cancer elimination | Screening and treatment/follow-up pathways matter for prevention | Frame the project as cytology triage and follow-up support, not standalone diagnosis |
| CDC cervical screening guidance | HPV testing and Pap/cytology answer different questions | Keep HPV wording to morphology risk; collect paired HPV DNA/RNA labels for future endpoint study |
| FDA/IMDRF GMLP | Safe, effective, high-quality AI/ML needs lifecycle thinking | Maintain model card, risk register, intended use, audit trail, versioned metrics, and claim audit |
| CONSORT-AI | AI clinical trials should report intervention, users, setting, input/output handling, human-AI interaction, and errors | Reader-study and prospective-study protocols must explicitly describe human-AI workflow and error analysis |
| DECIDE-AI | Early AI decision-support studies should evaluate clinical performance, safety, and human factors at small scale | Stage 4 reader study comes before any clinical-utility claim |

## Validation Stages

### Stage 0: Evidence Hygiene

Goal: make all current claims consistent and reproducible.

Acceptance criteria:

- All public docs cite the same JSON metrics.
- Old synthetic/polluted metrics are marked legacy and not used as evidence.
- README, model card, web pages, reports, and generated docs use the same claims.
- `python tools/inspect_checkpoints.py` confirms EfficientNet-B0.
- `npm.cmd run build` passes after web edits.

Current status: mostly complete; keep auditing old generated proposal files.

### Stage 1: Thai ThinPrep Retrospective Dataset

Goal: evaluate domain shift and make the ThinPrep claim real.

Minimum dataset fields:

- de-identified image ID;
- hospital/lab/site code;
- preparation type: ThinPrep/LBC/Pap;
- scanner/camera/magnification;
- staining protocol if available;
- Bethesda label;
- expert annotator ID or consensus label;
- quality flag;
- optional HPV DNA/RNA result;
- optional histology outcome;
- split assignment.

Suggested minimum:

- 500-1,000 de-identified fields/images for a first domain-shift audit.
- 2,000+ images for more stable model tuning.
- Preserve patient-level or slide-level grouping to avoid leakage.

Acceptance criteria:

- Thai test set is locked before model tuning.
- Per-class support is reported.
- No patient/slide leakage across train/val/test.
- Domain-shift performance is compared against Herlev baseline.

### Stage 2: HPV Endpoint Study

Goal: turn "HPV-related morphology risk" from narrative into measured endpoint.

Required labels:

- HPV DNA/RNA result if available;
- genotype group if available: high-risk positive / negative, optional genotype;
- cytology label;
- optional koilocytosis/HPV-effect annotation.

Model outputs to evaluate:

- Bethesda 5-class abnormality grade;
- binary abnormal triage;
- HPV morphology risk score;
- uncertainty/abstention flag.

Metrics:

- AUROC/AUPRC for HPV-positive risk;
- sensitivity/specificity at clinically chosen thresholds;
- calibration curve/Brier score;
- subgroup checks by site, stain/scanner, age band if available.

Safety wording until done:

> HPV risk is morphology-based and requires confirmatory HPV testing.

### Stage 3: Calibration and Abstention

Goal: make uncertainty actionable.

Experiments:

- temperature scaling on validation set;
- expected calibration error and adaptive calibration error;
- Brier score;
- reliability diagrams;
- threshold sweep for abstention;
- selective classification curves: coverage vs accuracy/sensitivity.

Acceptance criteria:

- chosen threshold documented;
- uncertainty policy written in the UI and model card;
- "uncertain" cases are routed to clinician review;
- no claim of "well-calibrated" unless calibration experiment supports it.

### Stage 4: Reader Study

Goal: test whether the tool helps humans.

Study design:

- Participants: cytotechnologists, pathologists, or trained clinicians.
- Cases: locked retrospective image set with expert reference labels.
- Arms:
  - unaided reading;
  - AI-assisted reading with grade + heatmap + uncertainty;
  - optional AI-assisted report generation.
- Outcomes:
  - sensitivity for abnormal/high-risk cases;
  - specificity;
  - time per case;
  - inter-reader agreement;
  - rate of appropriate follow-up recommendation;
  - trust/overreliance questionnaire.

Acceptance criteria:

- AI assistance improves or preserves sensitivity without unsafe overreliance.
- Cases where AI misleads humans are analyzed.

### Stage 5: Workflow Pilot

Goal: evaluate whether the system reduces follow-up delays.

Outcomes:

- time from image capture to preliminary triage;
- time from abnormal result to patient notification;
- follow-up completion rate;
- clinician workload;
- false-positive referral burden;
- patient understanding of the report.

Important:

- Requires IRB/ethics review if real patient workflow is involved.
- Must remain decision-support until regulatory pathway is clear.

## Model Improvement Roadmap

Near-term model work:

1. Re-run only targeted experiments on real Herlev/Thai data.
2. Avoid synthetic-heavy training as public evidence.
3. Add calibration script.
4. Add abstention threshold tuning.
5. Add external validation split.
6. Add error analysis by class.

Medium-term model work:

- MIL/WSI support for slide-level workflow.
- Quality gate before classification.
- Segmentation-assisted cell crop pipeline.
- HPV endpoint head once paired HPV labels exist.

## Documentation Roadmap

Required before any serious submission:

- `docs/CLAIMS_LEDGER.md`
- `docs/DATASET_MODEL_CARD.md`
- `docs/RISK_REGISTER.md`
- `docs/VALIDATION_ROADMAP.md`
- `docs/THAI_THINPREP_DATA_PROTOCOL.md`
- `docs/UNCERTAINTY_AND_ABSTENTION_POLICY.md`
- `docs/PATIENT_REPORT_SAFETY_SPEC.md`
- `docs/READER_STUDY_PROTOCOL.md`
- `docs/ERROR_ANALYSIS_PLAN.md`
- `docs/CALIBRATION_EXPERIMENT_REPORT.md`
- `docs/ERROR_ANALYSIS_REPORT_HERLEV.md`
- `docs/HERLEV_ERROR_CASE_GALLERY.md`
- `docs/PROJECT_READINESS_SCORECARD.md`
- `docs/LEGACY_ARTIFACT_AUDIT.md`
- `docs/BROWSER_ACCESSIBILITY_VERIFICATION.md`
- `docs/THAI_DATA_INTAKE_CHECKLIST.md`
- updated `README.md`
- updated `CLAUDE_HANDOFF_SOLVE_WSEEC_2026.md`

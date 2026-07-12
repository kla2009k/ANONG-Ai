# Thai Data Intake Checklist

Last updated: 2026-07-06

## Purpose

Prepare CerviCo-Pilot for real Thai ThinPrep/LBC data without fabricating
evidence or storing identifiable patient information in the project repository.

## Before Receiving Any Data

- [ ] Confirm IRB/ethics status or written exemption/determination.
- [ ] Confirm data owner and permitted use.
- [ ] Confirm whether images are ThinPrep, other LBC, or conventional Pap.
- [ ] Confirm whether paired HPV DNA/RNA result exists.
- [ ] Confirm whether histology follow-up exists.
- [ ] Confirm de-identification workflow.
- [ ] Confirm storage location outside public git.
- [ ] Confirm who can access raw images.

## De-Identification Gate

Before any file enters the workspace:

- [ ] Remove names.
- [ ] Remove hospital numbers.
- [ ] Remove national IDs.
- [ ] Remove phone/address.
- [ ] Remove dates of birth.
- [ ] Remove barcode/slide-label overlays.
- [ ] Remove embedded metadata if present.
- [ ] Replace real site names with site codes.

## Required Files For A Pilot Drop

- [ ] image folder outside git or in ignored secure storage;
- [ ] annotation CSV matching `data/templates/thai_thinprep_annotation_template.csv`;
- [ ] data dictionary confirmation;
- [ ] class/support table;
- [ ] split manifest by `case_id` or `slide_id`;
- [ ] known limitations note.

## First 50-Image Pilot

Use the first 50 images only to test process, not to claim performance.

Goals:

- verify file paths;
- verify metadata completeness;
- verify labels;
- verify quality labels;
- test de-identification;
- run model inference for smoke testing;
- identify domain-shift issues.

No public metric claim should be made from this pilot.

## First Validation Set

Minimum target:

- 500-1,000 images;
- locked split;
- no case leakage;
- class/support table;
- site/prep/scanner table;
- expert label source documented.

Outputs:

- Thai domain-shift report;
- per-class metrics;
- binary safety metrics;
- calibration/reliability;
- abstention/uncertainty performance;
- limitations.

## Do Not Do

- Do not copy identifiable patient data into git.
- Do not tune on the locked Thai test set.
- Do not merge crops from one case across train/test.
- Do not call HPV morphology risk a positive HPV infection result.
- Do not use Thai pilot smoke-test results as clinical validation.


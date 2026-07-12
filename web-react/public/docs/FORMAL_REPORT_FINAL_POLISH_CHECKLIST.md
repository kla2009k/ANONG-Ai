# Formal Report Final Polish Checklist

Last updated: 2026-07-07

Use this checklist after opening
`docs/CerviCo_Pilot_Formal_Research_Report_2026_Polished.docx` in Microsoft
Word or LibreOffice.

## Identity Fields

- [ ] Replace `ผู้จัดทำ 1/2/3` placeholders with real names.
- [ ] Add school/institution name.
- [ ] Add advisor name.
- [ ] Add committee names if required.
- [ ] Confirm academic year and competition year.

## Word Layout

- [ ] Update manual table-of-contents page numbers.
- [ ] Confirm Thai font renders as TH Sarabun New.
- [ ] Check every table for page overflow.
- [ ] Check figure captions remain near figures.
- [ ] Confirm title, approval page, abstracts, and chapter starts begin on clean pages.
- [ ] Export to PDF and inspect the PDF before submission.

## Research Tone

- [ ] Abstract states current evidence and limitations.
- [ ] Chapter 1 frames the problem as screening + follow-up workflow, not just a classifier.
- [ ] Chapter 1 separates Pap/ThinPrep cytology from HPV molecular testing.
- [ ] Objectives include technical, safety, and workflow goals.
- [ ] Research questions are clear and measurable.
- [ ] Limitations state Herlev-only evidence and no Thai ThinPrep validation.

## Claim Safety

- [ ] Run `python tools\audit_claims.py --all`.
- [ ] No claim that the system replaces clinicians.
- [ ] No claim that the system is ready for unsupervised clinical deployment.
- [ ] No claim that the system detects HPV infection.
- [ ] No claim that the system replaces HPV DNA/RNA testing.
- [ ] No claim that KOIL is validated in the current model.
- [ ] No claim that Thai-domain validation has already been completed.

## References

- [ ] Keep `docs/FORMAL_REFERENCES_BIBLIOGRAPHY.md` synchronized with the DOCX.
- [ ] Use WHO/CDC only for public-health and screening framing.
- [ ] Use EfficientNet, Grad-CAM, and MC Dropout sources only for method framing.
- [ ] Use GMLP/CONSORT-AI/DECIDE-AI only for governance and reporting framing.
- [ ] Use canonical `models/*.json` files for performance numbers.

## Deliverables

- [ ] Final DOCX: `docs/CerviCo_Pilot_Formal_Research_Report_2026_Polished.docx`
- [ ] Final PDF exported from Word/LibreOffice.
- [ ] Optional anonymous version if the competition requires blinded review.

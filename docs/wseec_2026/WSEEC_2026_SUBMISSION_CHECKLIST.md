# WSEEC 2026 Full Paper Submission Checklist

Use this checklist with:

- `CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.docx`
- `CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.pdf`

These polished files are the preferred submission versions. The earlier files
are retained only for comparison and reproducibility.

## Identity and Cover

- [ ] Replace all six author placeholders; remove unused author lines.
- [ ] Insert the official institution/school logo.
- [ ] Replace the institution-name placeholder.
- [ ] Confirm the category is `Technology` in the WSEEC registration.
- [ ] Confirm the project title matches the registration form exactly.
- [ ] Confirm the supervisor name is included if the registration/template
  requires it.

## Format

- [ ] A4 paper size.
- [ ] Arial 12 pt body text.
- [ ] Single line spacing.
- [ ] Justified body text.
- [ ] Margins: 4 cm left; 3 cm right/top/bottom.
- [ ] Main paper remains no more than 12 pages.
- [ ] Final Word and PDF remain exactly 12 pages after identity edits.
- [ ] References remain on page 12 in the polished version.
- [ ] Abstract remains below 350 words.
- [ ] Keywords remain between 4 and 6.
- [ ] Reference citations remain numerical: `[1]`, `[1-3]`, or `[1,2,5]`.

## Scientific Content

- [ ] Metrics still match `models/test_metrics.json`.
- [ ] Binary metrics still match `models/triage_metrics.json`.
- [ ] Cross-validation values still match `models/cv_results.json`.
- [ ] Calibration values still match `models/calibration_temperature.json`.
- [ ] No claim of Thai ThinPrep validation.
- [ ] No claim that the system replaces molecular HPV testing.
- [ ] KOIL remains identified as unsupported in current Herlev evidence.
- [ ] The paper states that clinician sign-off is required.

## Final Files

- [ ] Open the DOCX in Microsoft Word and visually inspect all 13 pages.
- [ ] Confirm tables and figures do not move after replacing identity fields.
- [ ] Export a fresh PDF from the final edited DOCX.
- [ ] Compare the exported PDF against the supplied PDF page by page.
- [ ] Use `tools\export_wseec_polished_pdf.ps1` to regenerate the final PDF
  from Word after replacing authors/logo/institution.
- [ ] Run `python tools\audit_claims.py --all`.
- [ ] Use short ASCII filenames if the submission portal rejects long names.
- [ ] Upload both the final PDF and Microsoft Word file.

## Presentation Alignment

The guidebook also requires a seven-minute English presentation and an
eight-minute Q&A. Ensure the slide deck uses the same title, metrics, evidence
boundaries, and category as this full paper.

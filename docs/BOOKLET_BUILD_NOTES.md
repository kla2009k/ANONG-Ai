# Complete Booklet Build Notes

Last updated: 2026-07-07

## Deliverable

Final DOCX:

- `docs/CerviCo_Pilot_Complete_Report_2026.docx`

Builder:

- `tools/build_full_booklet.py`

Generated visual assets:

- `docs/booklet_assets/headline_metrics.png`
- `docs/booklet_assets/cv_folds.png`
- `docs/booklet_assets/confusion_matrix.png`
- `docs/booklet_assets/roc_curve.png`
- `docs/booklet_assets/calibration_before_after.png`
- `docs/booklet_assets/workflow_diagram.png`
- `docs/booklet_assets/sample_gradcam_grid.jpg`

## Contents

The booklet includes:

- cover page;
- Thai abstract;
- English abstract;
- manual table of contents;
- list of figures;
- Chapter 1: introduction, objectives, scope;
- Chapter 2: external evidence and clinical framing;
- Chapter 3: methodology and system architecture;
- Chapter 4: results, tables, charts, calibration, Grad-CAM examples;
- Chapter 5: demo use, competition framing, roadmap;
- appendices for intended use, judge Q&A, failure modes, and source ledger.

## Structural QA

Latest structural check:

- DOCX opens with `python-docx`.
- Paragraphs: 123.
- Tables: 16.
- Inline shapes: 8.
- Embedded media files: 7.
- Heading paragraphs: 29.
- Claim audit: passed with `python tools\audit_claims.py --all`.

## Render QA Limitation

The packaged DOCX renderer could not run because `pdf2image` is missing in this
environment. Manual fallback render was also unavailable because `soffice`,
`libreoffice`, `pdftoppm`, and `magick` were not found on PATH.

Therefore, this build has structural QA but not full PNG visual QA in the
current environment. Open the DOCX in Microsoft Word or LibreOffice for final
visual inspection before public printing/submission.

## Rebuild Command

```powershell
python tools\build_full_booklet.py
python tools\audit_claims.py --all
```


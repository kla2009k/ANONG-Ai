# WSEEC 2026 Full Paper Format Audit

Last updated: 2026-07-10

## Official Inputs Reviewed

- `references/Guidebook_WSEEC_2026.pdf`
- `references/FORMAT_FULL_PAPER.pdf`

The source PDFs were copied from the user's Downloads folder so future agents
can verify the format without depending on an external session.

## Official Requirements Applied

| Requirement | Applied value |
| --- | --- |
| Language | English |
| Paper size | A4 |
| Body font | Arial, 12 pt |
| Line spacing | Single |
| Alignment | Justified |
| Margins | Left 4 cm; right 3 cm; top 3 cm; bottom 3 cm |
| Abstract | English, maximum 350 words |
| Keywords | 4-6 terms |
| Main-paper limit | Maximum 12 pages |
| References | Excluded from the 12-page limit |
| Required structure | Abstract; Chapters 1-5; References |
| Submission files | PDF and Microsoft Word |

The guidebook margin specification was treated as authoritative. The visual
template places some example text closer to the left edge, but the guidebook
explicitly states `4,3,3,3 (left, right, top, bottom)`.

## Deliverables

- `CerviCo_Pilot_WSEEC_2026_Full_Paper.docx`
- `CerviCo_Pilot_WSEEC_2026_Full_Paper.pdf`
- Preferred polished submission:
  `CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.docx`
- Preferred polished submission PDF:
  `CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.pdf`
- `WSEEC_2026_FULL_PAPER_AUDIT.json`
- Builder: `../../tools/build_wseec_full_paper.py`
- Polished builder: `../../tools/build_wseec_full_paper_polished.py`
- Word-matched PDF exporter: `../../tools/export_wseec_polished_pdf.ps1`

## Page Map

| Page | Content | Counted in 12-page limit |
| --- | --- | --- |
| 1 | Cover | Yes |
| 2 | Table of Contents | Yes |
| 3 | Abstract and keywords | Yes |
| 4 | Chapter 1: Introduction | Yes |
| 5 | Chapter 2: Literature Review | Yes |
| 6-8 | Chapter 3: Research Method | Yes |
| 9-11 | Chapter 4: Results and Discussion | Yes |
| 12 | Chapter 5: Conclusion | Yes |
| 13 | References | No |

## Polished 12-Page Version

The preferred polished version was rebuilt and exported directly through
Microsoft Word so the DOCX and PDF pagination match exactly.

| Page | Content |
| --- | --- |
| 1 | Refined cover |
| 2 | Table of Contents |
| 3 | Abstract and keywords |
| 4 | Chapter 1: Introduction |
| 5 | Chapter 2: Literature Review |
| 6-7 | Chapter 3: Research Method |
| 8-10 | Chapter 4: Results and Discussion |
| 11 | Chapter 5: Conclusion |
| 12 | References |

The polished file is exactly 12 pages in Microsoft Word and exactly 12 pages
in the exported PDF. This remains within the official maximum because the main
paper does not exceed 12 pages and references are permitted outside the limit.

Polish improvements include:

- restrained WSEEC/CerviCo-Pilot teal and navy hierarchy;
- refined cover and institution-logo placeholder;
- consistent running header and page numbering;
- chapter bands and improved section hierarchy;
- alternating table rows and stronger column alignment;
- side-by-side metric/figure panels;
- six embedded figures;
- compact but readable references;
- Word-generated PDF for identical pagination.

## Structural QA

- PDF pages: 13 total.
- Main paper: 12 pages.
- References begin on page 13.
- Abstract: 215 words.
- Keywords: 6.
- DOCX paragraphs: 137.
- DOCX tables: 16, including layout and data tables.
- DOCX figures: 5.
- PDF figures: 5.
- PDF has no blank pages.
- All 13 PDF pages were rendered to `qa_renders/page-01.png` through
  `qa_renders/page-13.png`.
- Raster edge audit found no content touching the page edge and no clipping
  risk on any rendered page.
- PDF page size: A4.
- DOCX margins: 4.0005 / 3.0004 / 3.0004 / 3.0004 cm.
- DOCX Normal style: Arial 12 pt, single spacing.
- Claim audit: must pass before submission.
- Latest claim audit: passed.
- Polished Word page count: 12.
- Polished PDF page count: 12.
- Polished PDF pages rendered to `qa_renders_polished/page-01.png` through
  `qa_renders_polished/page-12.png`.
- Polished raster edge audit: no clipping risk on any page.

## Evidence Boundaries Preserved

- Current performance evidence is Herlev-only.
- The model is a research prototype and decision-support workflow.
- HPV output is described as HPV-related morphology risk, not molecular HPV
  status.
- KOIL is a placeholder/future target because Herlev has no true KOIL support.
- Thai ThinPrep validation, paired HPV endpoints, reader studies, and
  prospective evaluation remain future work.

## Format Placeholders

The official template requires identity information that was not available in
the project files. Replace these before submission:

- `AUTHOR 1` through `AUTHOR 6`;
- institution logo;
- institution name.

The paper currently uses `CATEGORY: TECHNOLOGY`. Confirm this category with the
registration record before final submission. The project could also be argued
as Life Science, but Technology is the stronger fit for an AI system submission.

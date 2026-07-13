# Analyze Hardening, Paper Correction, and Deployment (2026-07-12)

## Trigger

A browser screenshot showed a nearly uniform blue Grad-CAM and an Activation
Regions panel reporting 0.0% while still displaying an original-looking image.
This was misleading: a degenerate explanation had no explicit validity gate.

## XAI correctness changes

- Added finite-value, shape, dynamic-range, standard-deviation, and positive-area
  diagnostics for every CAM.
- Added deterministic class-aware selection order: Grad-CAM, Grad-CAM++,
  Layer-CAM, then Score-CAM.
- A failed non-Grad-CAM method can no longer silently become manual Grad-CAM
  while retaining the wrong method label.
- If every class-aware map fails, the API returns XAI abstention and the UI shows
  `No stable activation map`; no heuristic image is presented as XAI.
- Heuristic spotlight fallback is restricted to explicit demo mode.
- Model mode no longer returns synthetic editable contours.
- Activation boundaries are created only from a valid selected CAM and are
  explicitly not cell or lesion segmentation.

Repeated live API inference across all eight public Herlev examples produced
valid maps. Six selected Grad-CAM; two safely selected Grad-CAM++ after the live
pipeline rejected a degraded Grad-CAM. Activation coverage ranged from 1.46% to
13.48%; no case returned 0.0% as a successful explanation.

## Analyze UI changes

- Original, heatmap, and activation boundary use the same uncropped field of view.
- All explanation images use equal square containers and `object-contain`.
- Added explanation method, standard deviation, dynamic range, and threshold
  diagnostics.
- Added validated/precomputed/unavailable status labels and a visible legend.
- Added file type and 12 MB size validation, a multi-stage loading message, and
  actionable API error messages.
- New result keys remount review state and generate a new case ID for each case.
- Edited categories now write the final category's HPV morphology-risk wording
  to the audit trail rather than the previous category's wording.

## Quality profile

The original slide-level rule rejected images with fewer than 30 estimated cells,
but Herlev contains single-cell crops with only 1-17 detected objects. A new
`single_cell_crop_herlev_v1` profile separates pass, warning, and hard failure.
Reference cut points were measured on all 917 Herlev images at 224 px model input:

- focus Laplacian p01: 8.448; median: 20.456;
- contrast p01: 14.691;
- brightness p01-p99: 85.078-208.592.

Cellularity is diagnostic only for this profile. Severe size, focus, contrast, or
brightness failures block patient release; reference deviations produce warnings.
These are engineering checks, not Bethesda specimen-adequacy criteria.

## Report safety

Patient release gates now run on the backend as well as the UI. A patient layer
remains locked unless review status is confirmed/edited, uncertainty is not high,
quality does not fail, XAI is valid, and the trained model is active. Report text
is a deterministic controlled template. It is not generative clinical language
and remains a non-regulated research pre-screen report.

## Upload security

The API now validates data URL structure, MIME type, strict base64, decoded image
format, byte limit, pixel dimensions, and actual image readability before model
inference. CORS origins are configured through `ANONG_ALLOWED_ORIGINS` instead of
being open to every origin.

## Paper correction

Herlev contains zero true KOIL examples. Recall is therefore mathematically not
estimable, not a measured 0.0000 failure rate. The WSEEC chart now shades the true
KOIL row and labels it `N/A - no true KOIL samples`; Table 5 reports Recall `N/A`.
The five-column predicted output space remains visible to disclose the product
placeholder while avoiding a false performance interpretation.

Final corrected files:

- `docs/wseec_2026/CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.docx`
- `docs/wseec_2026/CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.pdf`

Word confirmed exactly 12 pages. All pages were rendered for visual QA; page 9
was inspected at full resolution after the final chart change.

## Deployment

- Public static site: `https://kla2009k.github.io/ANONG-Ai/`.
- Deployment was verified on 2026-07-13 at commit `43692a8`: the Anong HTML,
  hashed JS/CSS, sample JSON, manifest, and polished WSEEC PDF all returned 200.
- The repository is currently configured for legacy `main`-root Pages and also
  has an artifact workflow. A checked-in root bundle and `.nojekyll` make both
  paths serve the same app instead of GitHub rendering the repository README.
- Direct nested URLs use the checked-in `404.html` SPA fallback. GitHub may send
  HTTP 404 for the initial nested request while the browser still renders the
  correct client route; normal navigation from the app remains the preferred path.
- GitHub Actions CI runs Python tests, frontend build, and claim audit.
- GitHub Pages builds with `/ANONG-Ai/` router and asset base paths.
- Pages includes SPA fallback and supports the precomputed evidence/demo flow.
- Live upload requires a FastAPI backend URL configured as `VITE_API_URL`.
- GitHub Pages cannot execute the PyTorch/FastAPI backend. Until a Render service
  is provisioned and `VITE_API_URL` is set, public users can inspect the eight
  precomputed Herlev examples; live upload remains available at the local server.
- Dockerfile, Compose, and Render blueprint package the model server and web app.
- Raw data, experiment artifacts, archives, node_modules, and generated QA output
  are excluded from Git.

## Verification

- 21 Python regression tests passed.
- Production and `/ANONG-Ai/` project-site builds passed.
- Simulated Pages navigation, sample JSON, paper PDF, and nested routes returned 200.
- Desktop 1440 px, reported-bug viewport 919 px dark mode, and mobile 390 px had
  no horizontal overflow or browser console errors.
- At 919 px, all three live XAI images measured 396 x 396 px.
- Claim audit passed with no risky unqualified claims.

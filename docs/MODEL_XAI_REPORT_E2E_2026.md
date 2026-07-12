# Model, XAI, and Reviewed Report E2E Verification (2026-07-12)

## Scope

This verification answers whether the current Anong web application can accept
an uploaded image, run the trained model, produce explainability and uncertainty
outputs, enforce clinician review, and download a result report.

## Defect found and fixed

Uvicorn is normally started with `server/` as its working directory. Python could
therefore import local `predictor.py` and load `models/best_cervical.pt`, but the
repository root was not on `sys.path` when `predictor.py` attempted to import
`ml.scripts.*`. The model ran in `mode=model`, while advanced quality, advanced
XAI, and advanced uncertainty imports failed and silently degraded.

`server/predictor.py` now resolves and inserts the repository root before the
optional `ml.*` imports. It also returns `heatmap_source` with one of these values:

- `advanced_gradcam` - advanced Grad-CAM produced successfully.
- `legacy_gradcam` - legacy manual/library Grad-CAM produced successfully.
- `demo_spotlight` - heuristic heatmap in explicit demo mode.
- `fallback_spotlight` - emergency visualization fallback; must not be claimed as Grad-CAM.

## Live API verification

Backend: `http://127.0.0.1:8003`

Test image: `web-react/public/samples/s04_HSIL.jpg`, a real Herlev example.

Observed result after the fix:

| Check | Result |
|---|---|
| Backend mode | `model` |
| Model output | SCC, probability 0.473 |
| True sample label | HSIL; therefore this is an error case, not a success example |
| Quality gate | Failed: blurry, low cellularity, low contrast |
| Uncertainty | High, entropy 1.3209, `advanced_mc` |
| Primary heatmap | Present, `advanced_gradcam` |
| Additional XAI | Score-CAM, Eigen-CAM, Layer-CAM |
| XAI adjuncts | Uncertainty overlay and top-k patches present |
| API report | Clinician and patient report structures generated |
| API export | Successful HTML/structured export |

This case correctly demonstrates why model output cannot be equated with a final
diagnosis: the prediction differs from the sample label, image quality is poor,
and uncertainty is high.

## Browser workflow verification

The production web bundle was opened at `/analyze` and the same file was uploaded
through the file input. Browser automation verified:

1. The upload reached the local FastAPI server.
2. The page rendered the five class probabilities and SCC suggestion.
3. The page displayed Original Image, Grad-CAM Heatmap, Activation Regions, and
   `Explanation source: advanced_gradcam` together.
4. The high-uncertainty warning appeared.
5. Clinician confirmation created a local demo audit entry.
6. The patient report remained locked because uncertainty was high.
7. `Download reviewed HTML` produced a standalone 156 KB report containing the
   case information, original image, Grad-CAM, reviewed category, uncertainty,
   HPV wording boundary, and patient-release lock.
8. No browser console or page errors occurred.

The follow-up visual QA replaced the subtle heatmap toggle with an always-visible
comparison panel containing Original Image, Grad-CAM Heatmap, and Activation
Regions. The activation view thresholds the strongest Grad-CAM response, tints
the selected area, draws a yellow boundary, and reports image coverage. On the
test case the activation area covered 13.5% of the image. It is explicitly labeled
as an attention boundary, not cell or lesion segmentation.

Test artifacts:

- `artifacts/e2e_medical_report_test.html` - server-side export smoke artifact.
- `artifacts/ui-reviewed-report-test.html` - browser-downloaded reviewed report.
- `docs/anong-model-xai-report-e2e.png` - full-page browser QA capture.
- `docs/anong-visible-xai-comparison.png` - final three-view XAI comparison.

## What is usable now

- Upload `.jpg`, `.png`, or `.bmp` images through Analyze while FastAPI is running.
- Run the trained EfficientNet-B0 checkpoint in local `model` mode.
- Display five-class probabilities, advanced Grad-CAM, MC Dropout uncertainty,
  image-quality warnings, and HPV-related morphology wording.
- Confirm, edit, or reject a result in the clinician-in-the-loop demo.
- Download a reviewed standalone HTML report after confirm/edit.
- Use Print / Save PDF on the reviewed report.
- Keep patient-facing output locked when uncertainty is high.

## What is not clinically ready

- The output is not a diagnosis and the report is not a regulated medical record.
- The sign-off is a demo action; it is not a verified electronic signature.
- The tested model is Herlev-domain only and lacks Thai ThinPrep external validation.
- The five-class result can be wrong, as the tested HSIL-to-SCC case demonstrates.
- HPV output is morphology-risk wording only, not HPV DNA/RNA detection.
- Hospital identifiers, patient identity, LIS/HIS integration, signed PDF/A,
  access control, retention policy, and regulatory validation are not implemented.

## Run commands

```powershell
cd server
python -m uvicorn app:app --host 127.0.0.1 --port 8003

cd ..\web-react
npm.cmd run preview -- --host 127.0.0.1 --port 4174
```

Open `http://127.0.0.1:4174/analyze` and verify `/api/health` reports
`"mode":"model"` before demonstrating a live upload.

# Web Deploy-Ready Checklist

Last updated: 2026-07-07

## Build

- [ ] `cd web-react`
- [ ] `npm.cmd run build`
- [ ] Confirm output exists in `web-dist/`.
- [ ] Confirm package name in build log is `cervico-pilot-web`.

## Static Assets

The static web package includes downloadable submission files under:

- `web-react/public/docs/CerviCo_Pilot_Formal_Research_Report_2026_Polished.docx`
- `web-react/public/docs/FORMAL_REFERENCES_BIBLIOGRAPHY.md`
- `web-react/public/docs/FORMAL_REPORT_FINAL_POLISH_CHECKLIST.md`
- `web-react/public/docs/DATASET_MODEL_CARD.md`
- `web-react/public/docs/VALIDATION_ROADMAP.md`
- `web-react/public/docs/CLAIMS_LEDGER.md`

If any source document changes, copy it into `web-react/public/docs/` again
before rebuilding.

## Demo Routes

Smoke-test these routes:

- `/`
- `/demo`
- `/analyze`
- `/gallery`
- `/workflow`
- `/reports`
- `/research-report`
- `/history`
- `/performance`
- `/model`

## Backend Optional

For upload analysis and mock server audit:

```powershell
cd server
python -m uvicorn app:app --port 8003 --reload
```

Backend endpoints used by the web app:

- `POST /api/analyze`
- `GET /api/audit`
- `POST /api/audit`
- `GET /api/ready`
- `GET /api/metrics`
- `POST /api/report/export/html`

If the backend is not running, bundled Herlev samples and localStorage audit
still work for static demo.

## Claim Boundaries

- Web must say HPV-related morphology risk, not HPV infection detection.
- Web must say decision-support/prototype, not clinical deployment.
- Patient report must remain gated by clinician sign-off and uncertainty.
- Audit must be labeled demo/mock, not regulated clinical audit.

## Final Browser QA

- [ ] No console errors.
- [ ] No failed network requests for static assets.
- [ ] `/research-report` download links return 200 in static build.
- [ ] `/demo` links navigate correctly.
- [ ] `/analyze` sample flow works without backend.
- [ ] `/analyze` upload flow shows server-offline error if backend is not running.
- [ ] `/history` does not auto-call backend; `Sync mock server` is manual.
- [ ] `/deployment` loads without backend and shows production boundaries.
- [ ] `/deployment` backend buttons work after FastAPI is started.
- [ ] `/reports` print/save PDF button opens print dialog.
- [ ] Mobile sidebar opens and closes.
- [ ] Text does not overflow at 375px width.

# Anong Full-Stack Deployment Runbook

Last updated: 2026-07-21

This runbook deploys the complete competition demo: React interface, four-grade
classifier, independent KOIL morphology model, XAI, uncertainty, mock audit,
and unsigned research PDF export. It does not make the system suitable for
clinical use.

## Recommended architecture

| Layer | Host | Purpose |
|---|---|---|
| Complete application | Render Docker web service | React, FastAPI, both model checkpoints, XAI, and PDF |
| Public evidence mirror | GitHub Pages | Static pages, documents, and the CRIC reference atlas |
| Model API for Pages | The same Render service | Enables upload and server PDF actions from Pages |

The simplest judging URL is the Render URL because frontend and API share one
origin. GitHub Pages is useful as a stable static mirror, but it cannot run
PyTorch by itself.

## Resource requirement

The loaded local backend measured about 804 MiB resident memory and 1.78 GiB
private memory. Render Starter provides only 512 MB, so `render.yaml` uses
Standard (2 GB RAM, 1 CPU). Treat Standard as the single-user demo minimum.
Use Pro (4 GB RAM, 2 CPU) for several concurrent judges or if Render records an
out-of-memory restart. Keep one Uvicorn worker because each worker loads its own
copy of both models.

Official references:

- Render instance types: https://render.com/docs/compute-plans
- Render web services: https://render.com/docs/web-services
- Render Blueprint fields: https://render.com/docs/blueprint-spec
- Render health checks: https://render.com/docs/health-checks

## One-time Render deployment

1. Push the latest `main` branch to `https://github.com/kla2009k/ANONG-Ai`.
2. Sign in to Render and choose **New > Blueprint**.
3. Connect the `kla2009k/ANONG-Ai` repository.
4. Confirm Render detects the root `render.yaml` and service `anong-ai`.
5. Confirm region **Singapore**, runtime **Docker**, plan **Standard**, and
   health check `/api/ready`.
6. Apply the Blueprint. The first Docker build is large because it installs the
   CPU PyTorch stack and copies two checkpoints.
7. Wait until `/api/ready` is HTTP 200. A healthy response must show both
   `grade_mode: model` and `koil_mode: model`.
8. Open the assigned `https://<service>.onrender.com` URL and test one upload,
   XAI display, clinical-context fields, and PDF download.

No secret is required for the competition demo. Do not put patient identifiers,
tokens, or credentials in `render.yaml`.

## Connect GitHub Pages to the model API

1. Copy the final Render origin, without a trailing slash.
2. Open GitHub repository **Settings > Secrets and variables > Actions > Variables**.
3. Create or update repository variable `VITE_API_URL` with
   `https://<service>.onrender.com`.
4. Open **Actions > Deploy static demo to GitHub Pages > Run workflow**.
5. After deployment, open `https://kla2009k.github.io/ANONG-Ai/analyze`.
6. The status line must report that the trained grade and KOIL models are active.

The allowed Pages origin is already set as `https://kla2009k.github.io` in
`render.yaml`. If the public frontend domain changes, add its exact origin to
`ANONG_ALLOWED_ORIGINS`, separated by commas, and redeploy.

## Release smoke test

Run these checks in order:

```text
GET  /api/health  -> 200, grade_mode=model, koil_mode=model
GET  /api/ready   -> 200, ok=true, audit_store_ok=true
GET  /api/metrics -> 200
GET  /             -> React application
GET  /gallery      -> 80 CRIC references plus model-audit tabs
POST /api/analyze  -> predictions, uncertainty, and valid XAI or explicit abstention
POST /api/report/export/pdf -> application/pdf
```

Also verify desktop and mobile layouts, a deliberately invalid upload, a valid
de-identified image, Grad-CAM labels, report release gating, and PDF filename.

## Gallery provenance

The gallery contains 80 real annotated CRIC Cervix cell crops: 20 NILM, 20
LSIL, 20 HSIL, and 20 SCC examples. Within each displayed category, all 20
come from different source images. CRIC is explicitly CC BY 4.0 and each card
links to its Figshare DOI. These images are external morphology references,
not model predictions, not external validation, and not HPV-test evidence.

KOIL remains a separate evidence tab. The model was evaluated with a locked
SIPaKMeD test split, but the project does not republish a bulk SIPaKMeD gallery
without explicit redistribution terms.

## Storage and privacy

Render's filesystem is ephemeral by default. The demo SQLite hash-chain audit
can reset after a deploy or restart. That is acceptable for a live competition
demo only. A hospital pilot requires a durable database or attached disk,
backups, access control, retention rules, encryption, and a verified audit
design.

Only upload public or fully de-identified research images. The application has
no clinician authentication, patient consent workflow, DICOM/LIS integration,
or regulated security controls.

## Failure diagnosis

| Symptom | Likely cause | Action |
|---|---|---|
| Docker build says KOIL checkpoint is missing | stale commit or broken Docker context | confirm `.dockerignore` explicitly includes both checkpoints |
| `/api/ready` returns 503 | one model failed to load or SQLite is not writable | inspect Render logs and `model_status` |
| Service restarts during inference | memory limit | confirm Standard; move to Pro if memory crosses the limit |
| Pages says static evidence mode | `VITE_API_URL` was absent at build time | set the repository variable and rerun Pages workflow |
| Browser reports CORS failure | Pages/custom origin is not allowed | update `ANONG_ALLOWED_ORIGINS` and redeploy |
| Render root works but Pages uploads fail | wrong API URL, failed workflow, or stale browser cache | inspect Pages build log and hard refresh |
| Audit history disappears | ephemeral service filesystem | expected for demo; attach durable storage before any pilot |

## Rollback

If the new release fails, redeploy the last healthy Render deploy from the
Render dashboard or revert the release commit and push `main`. Recheck
`/api/ready`, one real upload, XAI, and PDF export before sharing the URL again.

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

## Local full-stack verification

For upload analysis and mock server audit:

```powershell
python -m uvicorn server.app:app --host 127.0.0.1 --port 8003
```

Backend endpoints used by the web app:

- `POST /api/analyze`
- `GET /api/audit`
- `POST /api/audit`
- `GET /api/ready`
- `GET /api/metrics`
- `POST /api/report/export/html`

Open `http://127.0.0.1:8003`. If the backend is not running, bundled evidence
still works in a separate Vite static build, but uploads and server PDF export do not.

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

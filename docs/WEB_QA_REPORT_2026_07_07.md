# Web QA Report

Date: 2026-07-07

## Scope

This QA pass covers the web hardening requested after the formal report work:

- package metadata cleanup;
- evidence/report download page;
- judge demo mode;
- mock server-side audit endpoint;
- report export/copy controls;
- deploy-ready checklist;
- production build verification.

## Changes Under Test

- `web-react/package.json`
- `web-react/package-lock.json`
- `web-react/public/sw.js`
- `web-react/src/App.tsx`
- `web-react/src/components/Navbar.tsx`
- `web-react/src/pages/Landing.tsx`
- `web-react/src/pages/ResearchReport.tsx`
- `web-react/src/pages/DemoMode.tsx`
- `web-react/src/pages/ReportPreview.tsx`
- `web-react/src/pages/Analyze.tsx`
- `web-react/src/pages/History.tsx`
- `web-react/src/lib/audit.ts`
- `server/app.py`
- `web-react/public/docs/*`
- `web-react/src/pages/Deployment.tsx`

## Verified

- Production build passes with `npm.cmd run build`.
- Package name in build log is now `cervico-pilot-web`.
- New routes are wired:
  - `/research-report`
  - `/demo`
- Static docs were copied to `web-react/public/docs/` for download.
- Mock audit endpoints were added:
  - `GET /api/audit`
  - `POST /api/audit`
- Backend readiness/observability endpoints were added:
  - `GET /api/ready`
  - `GET /api/metrics`
- Backend HTML report export was added:
  - `POST /api/report/export/html`
- Backend TestClient smoke passed:
  - `/api/health` HTTP 200
  - `/api/ready` HTTP 200
  - `/api/metrics` HTTP 200
  - `/api/audit` HTTP 200
  - `POST /api/audit` HTTP 200 with `entry_hash`
  - `POST /api/report/export/html` HTTP 200 with `text/html`
- Audit flow uses localStorage by default and offers a manual `Sync mock server`
  action when the FastAPI backend is running.
- Report preview now supports:
  - print/save PDF through browser print;
  - HTML export;
  - copy text.
- Static HTTP smoke check passed on built `web-dist/`:
  - `/`
  - `/demo`
  - `/research-report`
  - `/analyze`
  - `/reports`
  - `/history`
  - `/deployment`
  - `/docs/CerviCo_Pilot_Formal_Research_Report_2026_Polished.docx`
- Browser runtime smoke check passed with Playwright:
  - dashboard, demo, research-report, deployment, analyze, reports, and history loaded;
  - mobile menu visible at 390 px viewport;
  - console errors: 0;
  - page errors: 0.

## Remaining Manual QA

Final human visual inspection should still be done before a live submission
demo, especially for projector readability and PDF downloads. Confirm:

- no clipping/overlap at desktop and mobile widths;
- download links work in the final deployed host;
- service worker cache is cleared if old DermaTrace assets were previously
  installed in the browser.

## Production Gaps

The web app is suitable for competition demo and project review. It is not yet
production/pilot hospital software because it still lacks:

- real authentication and clinician identity;
- regulated server-side immutable audit;
- database-backed case management;
- PDPA/IRB clinical data workflow;
- clinician-grade DOCX/PDF report generation from backend;
- deployment hardening and monitoring.

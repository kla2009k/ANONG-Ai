# Web Production-Hardening Report

Last updated: 2026-07-07

## What Was Added

This pass added a stronger backend/web layer while preserving the honest
prototype boundary.

## Backend

New or hardened endpoints:

- `GET /api/ready`
- `GET /api/metrics`
- `GET /api/audit`
- `POST /api/audit`
- `POST /api/report/export/html`

Audit storage:

- primary demo store: `artifacts/web_demo_audit.sqlite3`
- compatibility log: `artifacts/web_demo_audit.jsonl`

The SQLite audit store uses a simple hash chain:

- each row stores `prev_hash`;
- each row stores `entry_hash`;
- `entry_hash = sha256({prev_hash, payload})`;
- this demonstrates tamper-evident thinking, but is not a certified regulated
  immutable audit trail.

Observability:

- `/api/metrics` exposes process-local demo counters:
  - analyze calls;
  - audit writes;
  - report exports;
  - errors.

Report export:

- `/api/report/export/html` returns a printable HTML report.
- The report is explicitly labeled as decision-support demo output.
- It is not a signed clinical report generator.

## Frontend

New route:

- `/deployment`

The page shows:

- demo/pilot readiness matrix;
- backend health/ready/metrics/audit buttons;
- production boundary warning;
- link to deploy checklist.

Existing routes preserved:

- `/research-report`
- `/demo`
- `/analyze`
- `/reports`
- `/history`

## Current Readiness

Ready for:

- competition demo;
- judging walkthrough;
- static evidence package;
- local FastAPI demo;
- showing audit-traceability concept;
- showing report export concept.

Not ready for:

- hospital pilot with real patient data;
- regulated audit requirements;
- clinician identity and access control;
- PDPA/IRB clinical data handling inside the app;
- production monitoring and incident response;
- clinical report release.

## Verification Commands

```powershell
python -m py_compile server\app.py
cd web-react
npm.cmd run build
cd ..
python tools\audit_claims.py --all
```

Latest verification completed:

- `python -m py_compile server\app.py`: passed.
- `npm.cmd run build`: passed.
- `python tools\audit_claims.py --all`: passed.
- FastAPI TestClient smoke for health/ready/metrics/audit/report HTML export:
  passed.
- Playwright smoke for dashboard, demo, research-report, deployment, and
  history: passed with console errors 0 and page errors 0.

## Next Hardening After This

1. Add real authentication and role-based access control.
2. Replace demo audit with an immutable append-only service or signed event log.
3. Add a real case database with de-identified patient/case IDs.
4. Add backend-generated DOCX/PDF reports with signer identity.
5. Add deployment config, TLS, environment variables, and secrets handling.
6. Add monitoring, structured logs, backups, and incident-response docs.
7. Add IRB/PDPA user flows before handling real clinical data.

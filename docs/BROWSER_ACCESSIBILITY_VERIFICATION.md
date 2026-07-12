# Browser and Accessibility Verification

Last updated: 2026-07-07

## Scope

Pages affected by the latest hardening work:

- `/`
- `/analyze`
- `/gallery`
- `/workflow`
- `/reports`
- `/history`
- `/ask`
- `/model`
- `/performance`

## Static Verification Completed

Commands:

```powershell
npm.cmd run build
python tools\audit_claims.py
python tools\audit_claims.py --all
```

Status:

- TypeScript/Vite production build passes.
- Claim audit passes for current source-of-truth files.
- Claim audit passes for repository scan after excluding generated/heavy dirs.

Additional DentScanAI-inspired web hardening checks:

```powershell
npm.cmd run build
python tools\audit_claims.py --all
```

Status:

- TypeScript/Vite production build passes.
- Claim audit still passes after adding `/history` and `/ask`.
- Sidebar/dashboard hardening adds `/gallery`, `/workflow`, and `/reports`.

## Runtime Browser Verification Completed

Tool: Playwright Chromium headless against static `web-dist` server on
`http://127.0.0.1:4177`.

Verified on 2026-07-06:

- `/analyze` renders.
- 8 sample cards render.
- Selecting a Herlev sample displays the result card.
- HPV-related morphology risk panel appears.
- Patient report is locked before clinician sign-off.
- Clicking `ยืนยัน` writes one localStorage audit entry.
- Audit saved message appears.
- Export JSON button appears.
- `/model` renders governance and do-not-use sections.
- `/performance` renders ROC and calibration sections.
- Browser console errors: **0**.
- Failed network/resource requests: **0**.

Verified again after DentScanAI-inspired web hardening on 2026-07-06:

- Static `web-dist` served on `http://127.0.0.1:4181`.
- `/`, `/analyze`, `/history`, `/ask`, and `/performance` render with expected
  page titles.
- `/analyze` shows 8 Herlev sample cards.
- Selecting a sample and clicking clinician confirm writes one
  `cervico_audit_trail_v1` localStorage entry.
- `/history` reads the same localStorage audit trail and displays the case ID.
- `/ask` accepts a typed project question and returns a safe, bounded response.
- Browser console errors: **0**.
- Failed network/resource requests: **0**.

Verified after completing the 1-8 web expansion on 2026-07-07:

- Static `web-dist` served on `http://127.0.0.1:4182`.
- Desktop pages rendered: `/`, `/analyze`, `/gallery`, `/workflow`,
  `/reports`, `/history`, `/ask`, `/performance`, `/model`.
- `/gallery` displays 8 cases and Grad-CAM toggle switches to original/heatmap.
- `/reports` keeps the patient report locked before sign-off and unlocks after
  clinician sign-off when uncertainty is not high.
- `/analyze` still displays 8 sample cards; clinician confirm writes one
  localStorage audit entry.
- `/history` displays the generated case ID from localStorage.
- Mobile 390px check: hamburger menu is visible and can navigate to
  `/gallery`.
- Browser console errors: **0**.
- Failed network/resource requests after waiting for Grad-CAM load: **0**.

Final rerun on 2026-07-07:

- Static `web-dist` served on `http://127.0.0.1:4184`.
- Desktop routes checked: `/`, `/analyze`, `/gallery`, `/workflow`,
  `/reports`, `/history`, `/ask`, `/performance`, `/model`.
- `/analyze` sample cards: **8**.
- Clinician confirm creates localStorage audit entry: **yes**.
- `/history` displays generated case ID: **yes**.
- `/reports` lock behavior: locked before sign-off, unlocked after sign-off
  when high uncertainty is off.
- Browser console errors: **0**.
- Failed network/resource requests: **0**.

Important note:

- The audit trail is localStorage-only for demo governance. It is not a
  server-side regulated audit log.

## UI Behavior To Verify In Browser

### Analyze page

1. Open `/analyze`.
2. Select a Herlev sample.
3. Confirm that result card shows:
   - Bethesda-style class;
   - HPV-related morphology risk panel;
   - probability bars;
   - uncertainty;
   - clinician sign-off controls;
   - patient report locked before sign-off.
4. Click `ยืนยัน`.
5. Confirm that:
   - audit trail entry appears;
   - localStorage key `cervico_audit_trail_v1` is written;
   - patient report unlocks only if uncertainty is not high.
6. Select/edit result through dropdown.
7. Confirm audit trail records `edited`.
8. Click `Export JSON`.
9. Confirm JSON download contains case ID, AI label, final label, uncertainty,
   HPV risk note, source, and timestamp.

### History page

Open `/history`.

Expected:

- empty state appears when no local audit entries exist;
- summary cards show total entries, signed entries, edited/high-uncertainty
  counts;
- class filter chips work;
- `Export JSON` downloads the local audit trail;
- clear history removes local demo entries.

### Case Gallery page

Open `/gallery`.

Expected:

- correct and incorrect Herlev examples appear;
- Grad-CAM toggle works for each case;
- class and error-bucket filters work;
- page states the gallery is engineering review, not pathologist-reviewed.

### Workflow page

Open `/workflow`.

Expected:

- image intake to follow-up pathway is visible;
- safety gates include high uncertainty, HSIL/SCC, KOIL, and poor/OOD image;
- HPV caveat and clinician sign-off boundary remain visible.

### Report Preview page

Open `/reports`.

Expected:

- clinician report is always visible as decision-support;
- patient report remains locked until sign-off and non-high uncertainty;
- label selector changes report text;
- print button is available.

### Ask page

Open `/ask`.

Expected:

- quick prompts are available;
- typed project questions produce bounded, claim-safe responses;
- the page states it is a project knowledge assistant, not a patient medical
  chatbot;
- HPV answers preserve "morphology risk, not HPV DNA/RNA testing" wording.

### High-uncertainty policy

Use a high-uncertainty sample or injected test result.

Expected:

- red/alert uncertainty banner appears;
- patient report remains locked even after sign-off;
- clinical report remains visible;
- audit trail can still record clinician action.

### Model Card page

Open `/model`.

Expected:

- Do-not-use block is prominent;
- governance section states:
  - 5-class output is product identity;
  - binary triage is safety layer;
  - HPV risk is not DNA/RNA test;
  - high uncertainty blocks automatic patient report.

### Performance page

Open `/performance`.

Expected:

- ROC and reliability charts load from `samples/curves.json`;
- calibration copy says raw reliability is shown and post-hoc scaling has a
  separate report;
- calibration wording remains qualified and points to the separate report.

## Accessibility Checklist

- All result actions use native `<button>` or `<select>`.
- File input has `aria-label`.
- Sample cards have `aria-label`.
- Grad-CAM image has descriptive `alt`.
- Probability bars have aggregate `role="img"` + aria label.
- High-uncertainty warning uses `role="alert"`.
- Color is not the only state indicator; labels/icons accompany states.

## Remaining Runtime Verification

Still recommended before public demo:

- keyboard tab-through on `/analyze`, `/model`, `/performance`;
- mobile widths: 320px, 768px;
- desktop widths: 1024px, 1440px;
- localStorage audit export file-content manual check after download;
- print/PDF check for patient report.

## Notes

This document records the verification plan and static checks. Full runtime
browser verification should be repeated after any UI change.

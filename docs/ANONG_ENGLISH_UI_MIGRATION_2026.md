# Anong English-Only UI Migration 2026

Updated: 2026-07-11  
Scope: `web-react/`, generated `web-dist/`, browser/PWA metadata, and demo report export  
Status: implemented and verified

## 1. Decision

The complete product interface is English-only. The visible brand is **Anong** and the technical/research identity remains **CerviCo-Pilot**. Use **Anong · CerviCo-Pilot** when both contexts need to appear together.

The original Thai name **อนงค์** is retained only as brand origin in project documentation. It is not rendered in the current website. Downloadable research artifacts may retain their original submission language; those files are documents, not product UI.

## 2. Translation scope

The migration covers:

- browser title, description, Open Graph title, and `<html lang="en">`;
- PWA name, short name, and description;
- desktop sidebar, mobile menu, theme control, status panels, and footer;
- all static headings, descriptions, buttons, form labels, placeholders, empty states, and error states;
- clinical category names, interpretations, recommended actions, model-card fields, and limitations;
- uploaded-image errors, uncertainty alerts, HPV morphology notes, clinician sign-off, patient-report lock, and local audit trail;
- chart titles, SVG accessibility labels, confusion-matrix annotations, and metric explanations;
- rule-based Ask Anong prompts and answers;
- generated HTML report title, headings, and report text.

## 3. Route coverage

| Route | English page title / purpose |
|---|---|
| `/` | Anong overview and current evidence |
| `/analyze` | Image analysis, examples, sign-off, reports, audit |
| `/gallery` | Real-case gallery and error analysis |
| `/workflow` | Clinical care pathway and safety gates |
| `/reports` | Clinician and patient report preview |
| `/research-report` | Research reports and submission evidence |
| `/demo` | Six-step judge demonstration script |
| `/deployment` | Demo status and pilot readiness |
| `/history` | Analysis and sign-off history |
| `/performance` | Evaluation metrics and charts |
| `/knowledge` | Clinical context, Bethesda categories, and metric glossary |
| `/ask` | Rule-based project knowledge assistant |
| `/model` | English-only model card |
| `/about` | Product definition, workflow, and roadmap |
| `/settings` | Theme, model connection, and system information |

## 4. Canonical terminology

| Concept | Required wording |
|---|---|
| Product brand | `Anong` |
| Technical system | `CerviCo-Pilot` |
| Primary output | `Bethesda-style 5-class output` |
| Binary output | `binary safety triage` or `binary screening view` |
| HPV output | `HPV-related morphology risk` |
| Human control | `clinician sign-off` / `human review` |
| Diagnostic boundary | `not a final diagnosis` |
| HPV boundary | `not HPV DNA/RNA detection` / `not an HPV DNA/RNA test` |
| KOIL boundary | `Phase 2 target; not validated in Phase 1` |
| Audit boundary | `local demo audit trail; not a regulated audit log` |

Do not use an unqualified phrase such as `detect HPV`. The safe user question is `Does this replace HPV DNA/RNA testing?`, followed by an explicit negative answer.

## 5. Data-model cleanup

`src/lib/data.ts` no longer stores duplicate Thai and English UI fields. `ClassInfo.th` was removed; `ClassInfo.en`, `desc`, and `triage` now provide the canonical English strings. `MODEL_CARD` was simplified from bilingual objects to English strings and arrays. This prevents future components from accidentally selecting a Thai field.

Legacy local audit entries may contain wording saved by an older UI. New entries are English. UI code should render canonical English labels from current category/status values instead of trusting legacy presentation text where possible.

## 6. Verification

### Source Unicode scan

```powershell
cd web-react
rg -n -P '[\x{0E00}-\x{0E7F}]' src index.html public -g '!public/docs/**'
```

Expected result: no matches.

### Built-output Unicode scan

```powershell
cd ..\web-dist
rg -n -P '[\x{0E00}-\x{0E7F}]' . -g '!docs/**'
```

Expected result: no matches.

### Build and claims

```powershell
cd ..\web-react
npm.cmd run build

cd ..
python tools\audit_claims.py --all
```

Verified results:

- TypeScript/Vite production build passed;
- claim audit passed with no risky unqualified claims;
- source and built-output Thai Unicode scans returned no matches.

## 7. Browser QA

Headless Chromium verified every route in Section 3:

- English H1 and active navigation label present;
- no Thai characters in `document.body.innerText`;
- no horizontal overflow;
- no console errors or warnings.

Dynamic states verified in English:

- Ask Anong HPV boundary answer;
- patient report unlock and high-uncertainty relock;
- analysis sample selection, clinician confirmation, and slide rejection;
- backend readiness failure/status message;
- empty audit-history state.

Responsive checks passed at 320, 390, 768, 1024, and 1440 pixels. Mobile navigation scrolls independently at narrow heights. Desktop navigation and the fixed HPV-boundary panel do not overlap.

Final visual captures:

- `docs/anong-english-home-desktop.png`
- `docs/anong-english-mobile-menu.png`

The English release uses service-worker cache key `anong-en-v2` so clients do not retain the earlier Thai app shell.

## 8. Future guardrails

1. Product UI strings must remain English-only.
2. Run both Unicode scans after every UI change.
3. Do not translate canonical medical terms into informal substitutes.
4. Keep downloadable reports in the language required by their competition/template; do not confuse document language with UI language.
5. Re-run build, claim audit, all-route browser smoke test, and mobile overflow checks before release.

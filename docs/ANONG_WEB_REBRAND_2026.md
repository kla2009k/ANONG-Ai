# Anong Web Rebrand 2026

Updated: 2026-07-11  
Scope: `web-react/` and generated `web-dist/`  
Status: implemented, built, and browser-smoke-tested

## 1. Naming architecture

| Layer | Name | Use |
|---|---|---|
| User-facing English brand | **Anong** | Navbar, home hero, About, Q&A, browser title, PWA name, footer |
| Thai source name | **อนงค์** | Brand origin only; not displayed in the current English-only product UI |
| Technical/research system | **CerviCo-Pilot** | Model card, evidence documents, metrics, research reports, technical subtitle |
| Research title | Existing formal Thai/English titles | Papers, proposals, WSEEC/SFT material; unchanged by this visual rebrand |

Do not globally replace `CerviCo-Pilot`. The public brand and technical identity coexist: **Anong · CerviCo-Pilot**.

## 2. Design intent

The interface should feel gentle, respectful, and approachable for a women's-health context while remaining credible as a clinician-in-the-loop research tool. Pink is used as the identity color, not as a stereotype or decoration on every element. Butter yellow highlights evidence, caveats, and selected supporting information. Cream reduces glare and provides a calm base.

The redesign deliberately avoids neon AI gradients, decorative blobs, excessive shadows, and rounded-card overload. Medical risk states retain separate semantic colors and text labels.

## 3. Canonical palette

| Token | Value | Role |
|---|---:|---|
| `--paper` | `#fff8e9` | Cream page background |
| `--surface` | `#fffdf7` | High-readability cards and controls |
| `--ink` | `#4a3340` | Main warm-plum text |
| `--mut` | `#735e69` | Secondary text |
| `--line` | `#ead4d3` | Quiet non-interactive separators |
| `--control-line` | `#c37089` | Accessible boundary for interactive controls |
| `--teal` | `#b64e70` | Legacy internal token name; canonical Anong rose |
| `--teal-d` | `#923955` | Hover/pressed rose |
| `--blush-soft` | `#fcebef` | Branded information band |
| `--butter` | `#efc764` | Supporting yellow accent |
| `--butter-soft` | `#fff0b8` | Evidence/caveat panel |

The internal `--teal`/`text-teal` aliases are retained to avoid a high-risk mechanical rewrite. They now resolve to the Anong rose palette and must not be interpreted as actual teal.

## 4. Contrast checks

| Pair | Ratio | Result |
|---|---:|---|
| Ink on cream | 10.80:1 | AAA |
| Secondary text on cream | 5.62:1 | AA |
| Rose on cream | 4.60:1 | AA |
| White on rose | 4.87:1 | AA |
| HSIL ochre on butter | 4.65:1 | AA |
| NILM green on surface | 4.81:1 | AA after adjustment |
| LSIL blue-gray on surface | 4.67:1 | AA after adjustment |

Borders for passive cards may remain subtle. Inputs, selects, textareas, and outlined buttons use `--control-line` so the interactive boundary is not lost against cream.

## 5. Implemented surfaces

- Navbar and mobile menu use one Lucide icon family, English labels, `aria-current`, and a visible theme control.
- Home hero presents **Anong** as the primary name and explains the CerviCo-Pilot relationship.
- Ask page is branded **Ask Anong**, has an accessible live conversation log, and retains claim-safe rule-based answers.
- About, footer, browser metadata, PWA manifest, service-worker cache, and SVG app icons use the new identity.
- Exported demo HTML report uses the Anong palette and `anong-cervico-pilot-demo-report.html` filename.
- Performance limitations use a butter evidence panel; Bethesda semantic colors remain distinct from brand pink.
- Default theme is light pastel. A warm-plum dark theme remains optional for low-light use.

## 6. Responsive and browser QA

Verified with headless Chromium at 1440x1000 and 390x844:

- no horizontal overflow on home, Analyze, Performance, Reports, Ask, or About;
- mobile menu fits the viewport and scrolls independently;
- active route is exposed through `aria-current="page"`;
- all inspected routes load without console errors or warnings;
- page title and H1 resolve to the Anong brand where expected.

Visual QA captures:

- `docs/anong-home-desktop.png`
- `docs/anong-mobile-menu.png`
- `docs/anong-performance.png`
- `docs/anong-ask.png`

## 7. Verification commands

```powershell
cd web-react
npm.cmd run build

cd ..
python tools\audit_claims.py --all
```

Static preview target: `http://127.0.0.1:8090/` from `web-dist/`.

## 8. Guardrails for future edits

1. Keep **Anong** as the dominant visible brand; keep **CerviCo-Pilot** in technical/evidence contexts.
2. Do not return to the superseded navy/plum identity in the old brief.
3. Do not use yellow for small body text on cream; use it as a background/accent with dark text.
4. Do not recolor NILM/LSIL/HSIL/SCC/KOIL to match the brand. Their colors encode clinical categories.
5. Do not claim HPV infection detection. Continue using **HPV-related morphology risk**.
6. Re-run build, claim audit, desktop smoke test, and 390px mobile smoke test after UI changes.
7. Keep the product UI English-only and run the Unicode scan documented in `docs/ANONG_ENGLISH_UI_MIGRATION_2026.md`.

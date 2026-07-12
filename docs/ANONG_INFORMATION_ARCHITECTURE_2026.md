# Anong Information Architecture Simplification (2026-07-12)

## Objective

Reduce visual and cognitive load without deleting working features. The website
must lead a reviewer through the core product story first, while keeping detailed
project tools discoverable in the page where they are relevant.

## Primary navigation

The sidebar and mobile menu contain seven destinations:

1. **Overview** (`/`) - product identity, current evidence, three core steps,
   and readiness boundaries.
2. **Analyze** (`/analyze`) - main image-analysis and clinician sign-off task.
3. **Case Gallery** (`/gallery`) - real Herlev examples and error review.
4. **Clinical Workflow** (`/workflow`) - end-to-end human-in-the-loop pathway.
5. **Performance** (`/performance`) - model evaluation and limitations.
6. **Evidence** (`/research-report`) - research package, evidence snapshot,
   downloads, and supporting project tools.
7. **About** (`/about`) - product scope and identity.

Do not treat every route as a primary destination. Navigation priority reflects
the reviewer journey: understand the system, try it, inspect examples, verify the
workflow, examine performance, inspect evidence, then review project context.

## Contextual secondary routes

No route was removed. Secondary destinations are now reached from the page that
best explains why a user would open them:

| Route | Entry point | Reason |
|---|---|---|
| `/reports` | Clinical Workflow | Reports are an output of sign-off, not a top-level task. |
| `/history` | Analyze | Audit history follows analysis and review activity. |
| `/demo` | Evidence | The judge script supports project presentation. |
| `/deployment` | Evidence | Readiness is supporting evidence, not routine use. |
| `/knowledge` | Evidence | Terminology supports interpretation and review. |
| `/ask` | Evidence | Project Q&A is an exploration aid. |
| `/model` | Evidence | The model card is part of the controlled evidence package. |
| `/settings` | Existing route only | Theme is already controlled directly in navigation. |

## Overview changes

The previous Overview repeated navigation and workflow content in three places.
It has been reduced to four focused elements:

- Hero with two actions: **Analyze an image** and **View research evidence**.
- Current-evidence panel with Herlev metrics and the HPV wording boundary.
- Three core workflow cards: analysis, clinician sign-off, audit/follow-up.
- Readiness scorecard showing both completed and missing evidence.

The seven-card quick-action grid and the separate six-step "How it works" section
were removed. The complete path remains available through one contextual link to
Clinical Workflow.

## Sidebar changes

- Removed the separate prototype-status panel above the navigation.
- Merged prototype scope and HPV limitation into one compact footer notice.
- Kept theme control visible but separate from primary routes.
- Added fixed-content grid alignment so seven desktop links remain compact rather
  than stretching vertically through the sidebar.

## Evidence hub

Evidence now contains a simple divided list for six supporting tools: Report
Preview, Model Card, Knowledge Guide, Judge Demo, Deployment Readiness, and Ask
Anong. This list intentionally avoids another dashboard of large cards.

## Verification

Completed after implementation:

- `npm.cmd run build` - passed; Vite production bundle generated in `web-dist/`.
- `python tools\audit_claims.py --all` - passed with no risky unqualified claims.
- Chromium desktop checks at 1440 x 1000 - all seven primary routes rendered,
  no horizontal overflow, no console errors.
- Chromium mobile checks at 390 x 844 - exactly seven visible navigation links,
  theme control visible, no horizontal overflow.
- Evidence hub - all six secondary links present.
- Clinical Workflow - Report Preview link present.

Visual QA captures:

- `docs/anong-simplified-home-desktop.png`
- `docs/anong-simplified-mobile-menu.png`

## Guardrail for future work

Add a primary navigation item only when it represents a frequent, distinct user
task that cannot be reached naturally from an existing core page. New evidence,
submission, configuration, and presentation views should normally be added to
Evidence or linked contextually rather than expanding the primary menu.

# Source Citation Ledger

Last updated: 2026-07-06

Purpose: map public claims to source categories so proposals, reports, decks,
and Claude/Codex follow-up work do not drift into unsupported medical claims.

## Source Priority

1. Project metrics: `models/test_metrics.json`, `models/triage_metrics.json`,
   `models/cv_results.json`, and reports generated from them.
2. Project governance docs: claims ledger, roadmap, model card, risk register,
   safety specs.
3. Official/primary external sources: WHO, CDC, FDA/IMDRF, peer-reviewed
   reporting guidelines.
4. Legacy generated proposals: background only, not source of truth.

## External Source Map

| Source | URL | What It Supports | How To Use |
| --- | --- | --- | --- |
| WHO cervical cancer fact sheet, 2026 | https://www.who.int/news-room/fact-sheets/detail/cervical-cancer | Cervical cancer preventability, HPV causal pathway, screening/treatment importance, 90-70-90 strategy | Use for public-health problem framing, not model performance |
| WHO cervical cancer elimination initiative | https://www.who.int/initiatives/cervical-cancer-elimination-initiative | Elimination strategy context | Use when explaining policy alignment |
| CDC cervical cancer screening | https://www.cdc.gov/cervical-cancer/screening/index.html | Difference between HPV test and Pap test; abnormal Pap follow-up | Use to defend "HPV morphology risk, not HPV infection detection" |
| CDC cervical cancer basics | https://www.cdc.gov/cervical-cancer/about/index.html | Long-lasting HPV infection as main cause; early detection is highly treatable | Use for simple judge-facing health explanation |
| FDA/IMDRF GMLP principles | https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles | AI/ML medical-device lifecycle, safe/effective/high-quality development | Use for governance, model card, monitoring, and claim-control language |
| CONSORT-AI | https://www.nature.com/articles/s41591-020-1034-x | Reporting AI clinical trials, human-AI interaction, input/output handling, error analysis | Use for reader-study/prospective-study roadmap |
| DECIDE-AI | https://www.nature.com/articles/s41591-022-01772-9 | Early-stage clinical evaluation of AI decision-support systems | Use to justify small-scale clinical evaluation before clinical claims |

## Claim-To-Source Map

| Claim | Source Category | Required Evidence | Safe Public Wording |
| --- | --- | --- | --- |
| Cervical cancer prevention depends on vaccination, screening, and treatment/follow-up | External | WHO fact sheet / elimination initiative | "Cervical cancer is largely preventable when HPV vaccination, screening, and treatment pathways work." |
| HPV is central to cervical cancer | External | WHO / CDC | "Persistent high-risk HPV infection is the main causal pathway behind most cervical cancers." |
| Pap/ThinPrep cytology is different from HPV DNA/RNA testing | External | CDC screening page | "Pap/ThinPrep cytology looks for abnormal cell changes; HPV testing looks for the virus." |
| CerviCo-Pilot estimates HPV-related risk from images | Project + external | Project output schema + CDC distinction | "HPV-related morphology risk from cytology images, not direct HPV infection detection." |
| CerviCo-Pilot has real public-dataset evidence | Project | `models/*.json`, `docs/DATASET_MODEL_CARD.md` | "Phase 1 evidence on real public Herlev images." |
| 5-class model is moderate, not diagnostic | Project | `models/test_metrics.json`, `models/triage_metrics.json` | "Bethesda-style grading support; not a final diagnosis." |
| Binary triage is high-sensitivity on Herlev | Project | `models/triage_metrics.json`, `models/cv_results.json` | "High-sensitivity safety triage in Phase 1 Herlev evaluation." |
| Grad-CAM helps review model emphasis | Project + CONSORT-AI definitions | web/API path + XAI docs | "Grad-CAM shows regions the model emphasized; clinicians can challenge it." |
| Uncertainty should trigger human review | Project + FDA/DECIDE-AI | uncertainty policy + lifecycle governance | "Uncertain cases are routed to clinician review." |
| Reader study is required before clinical-utility claims | External + project | CONSORT-AI / DECIDE-AI + reader-study protocol | "Clinical utility remains future work pending reader study and workflow validation." |
| Thai ThinPrep validation is missing | Project | roadmap + data protocol | "External Thai ThinPrep validation is required before Thai clinical claims." |

## Claims That Need Thai Primary Sources

Do not publish these as final numbers unless the exact primary source is pinned
in the submission bibliography:

- Thailand screening coverage changed from 77.5% to 53.9%.
- Roughly 41% of women with abnormal results never return for care.
- Thai HPV 52/58 dominance in the exact target population.
- Thai FDA SaMD/AI classification for this exact deployment.

Safe interim wording:

> Thailand-specific screening, follow-up, genotype, and regulatory claims should
> be cited from Thai/WHO/IARC/public-health primary sources in the final
> competition package. Until then, use them as hypotheses or background
> motivation, not verified project evidence.

## Required Citation Behavior

Before writing any public-facing package:

- copy model metrics only from canonical JSON or generated metric reports;
- cite WHO/CDC for clinical/public-health framing;
- cite FDA/IMDRF for lifecycle and governance framing;
- cite CONSORT-AI/DECIDE-AI for reader-study and clinical-evaluation roadmap;
- mark Thailand-specific statistics as unverified unless the primary source is
  attached;
- run `python tools\audit_claims.py --all`.

## Short Citation Paragraph For Proposals

CerviCo-Pilot is framed around established cervical-cancer prevention logic:
WHO describes cervical cancer as largely preventable through HPV vaccination,
screening, and treatment/follow-up pathways, while CDC distinguishes HPV tests
that detect virus from Pap tests that detect cervical cell changes. Therefore,
this project does not claim direct HPV infection detection. It provides
Bethesda-style cytology grading, HPV-related morphology risk, Grad-CAM,
uncertainty flags, and clinician sign-off. Its next validation steps follow
medical-AI reporting principles from FDA/IMDRF GMLP, CONSORT-AI, and DECIDE-AI.

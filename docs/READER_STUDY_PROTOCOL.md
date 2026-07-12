# Reader Study Protocol

Last updated: 2026-07-06

## Purpose

Test whether CerviCo-Pilot helps human readers make safer and faster cervical
cytology screening decisions. Model metrics alone are not enough; the key
question is whether AI assistance improves the workflow without causing unsafe
automation bias.

## Study Type

Retrospective reader study using de-identified cytology images with locked
reference labels.

## Participants

Possible reader groups:

- cytotechnologists;
- pathologists;
- gynecologists with cytology workflow experience;
- trained medical staff for triage workflow testing.

Record:

- role;
- years of experience;
- prior AI tool exposure;
- site type if relevant.

## Case Set

The case set should include:

- NILM;
- LSIL;
- HSIL;
- SCC;
- low-quality/uncertain cases;
- Thai ThinPrep/LBC cases if available;
- Herlev/public cases only for early pilot.

Avoid leakage:

- no reader should see the same case in multiple arms too close together;
- randomize order;
- separate sessions if doing crossover.

## Study Arms

### Arm A: Unaided

Reader sees image only and records:

- Bethesda-style label;
- normal/abnormal triage;
- follow-up recommendation;
- confidence;
- time.

### Arm B: AI-assisted

Reader sees:

- image;
- AI Bethesda-style suggestion;
- binary triage;
- HPV-related morphology note;
- Grad-CAM;
- uncertainty level.

Reader records:

- final label;
- whether AI was accepted/edited/rejected;
- follow-up recommendation;
- confidence;
- time;
- whether heatmap was useful or misleading.

## Primary Outcomes

Recommended primary endpoint:

- sensitivity for abnormal/high-risk cases with AI vs unaided.

Secondary endpoints:

- specificity;
- HSIL/SCC recall;
- time per case;
- inter-reader agreement;
- rate of correct follow-up recommendation;
- override rate;
- automation-bias events;
- reader trust rating.

## Automation Bias Monitoring

Flag cases where:

- AI is wrong and reader follows AI;
- Grad-CAM is misleading and reader cites it;
- reader confidence increases despite incorrect final answer;
- uncertainty is high but reader ignores it.

These cases are more useful than average accuracy because they expose safety
failure modes.

## Minimum Analysis

Report:

- per-reader and pooled results;
- confidence intervals;
- confusion matrices;
- time distribution;
- AI accept/edit/reject rates;
- performance by uncertainty level;
- performance by class;
- qualitative feedback.

## Success Criteria

For a strong Phase 2 claim:

- AI assistance improves or preserves abnormal/high-risk sensitivity;
- no dangerous drop in specificity;
- high-uncertainty cases are handled more cautiously;
- readers can explain why they accepted or rejected AI;
- patient follow-up recommendations improve or become clearer.

## What Not To Claim

Do not claim clinical utility until a reader study shows human workflow benefit.

Safe wording before completion:

> A reader study is planned to evaluate whether the system improves clinician performance and follow-up workflow.


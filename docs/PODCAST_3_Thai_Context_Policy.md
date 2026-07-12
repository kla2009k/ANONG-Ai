# CervicalAI Thai Context & Policy Alignment

## Epidemiology
- Age-standardized rate: 19.8 per 100,000 women (high)
- Highest in Northern Thailand
- 86-95% HPV-attributable
- Coverage: 77.5% peak -> 53.9% now (WHO wants 70%)

## HPV Genotype Reality (Critical)
Thailand: HPV 52 and 58 dominate, not 16/18 like West
CIN2-3: HPV16 38.5%, HPV58 20%, HPV18 5.5%
Triage study: 16/18/52/58 better than 16/18 alone

IMPLICATION: Model trained on Western data has domain shift.
Thai fine-tuning is scientifically necessary, not just nice-to-have.

## Loss-to-Follow-Up 41% (The Core Problem)
Thai study (pubmed 26745114):
- 41.1% of abnormal results never return
- 35.6% did not receive letter
- 10.2% did not understand letter
- 33% transportation barriers

Current workflow: sample -> transport -> queue 1-2 weeks -> letter -> woman must travel back
AI at point of care + patient report in Thai = cut the delay = people don't disappear.

## Regulatory
Thai FDA SaMD guidance: June + Oct 2024
Must disclose: training data, fairness, cybersecurity
4 risk classes (I-IV)
Our design: decision support, physician sign-off, uncertainty flag -> Class II-III
Aligned with guidance.

## Policy Alignment
WHO 90-70-90: 70% screened by 2030
Thai NCI + NHSO: need to increase coverage and treatment uptake
AI pre-screen: increase throughput without more pathologists
Patient report: increase treatment uptake (fix 41%)

## Precedent
Thailand deployed AI DR screening nationally (Lancet Digital Health 2022)
9 sites, 7651 patients, real-time, compared to specialist
Proved: AI screening in Thai primary care is feasible
Cervical is next organ.

See: DEEP_RESEARCH_CervicalAI.md Findings 9, C1, C2, C18

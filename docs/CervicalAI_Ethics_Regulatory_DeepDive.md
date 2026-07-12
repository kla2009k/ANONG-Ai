# CervicalAI (CerviCo-Pilot) — Ethics, Regulatory & Safety Deep Dive (Thai Context + Global)

**Version**: Exhaustive 2026-06-26 (for Samsung, PCSHS, future IRB/FDA)  
**Purpose**: Preempt questions from judges, hospitals, regulators, ethics committees.  
**Scope**: Phase 1 (template) + Phase 2 (Thai data + LLM + edge)  

---

## 1. Core Ethical Principles (Non-Negotiable)

1. **Human-in-the-Loop Always**  
   - No result is released without physician sign-off.  
   - AI is strictly "pre-screen / triage assist", never "diagnostic replacement".  
   - Every DOCX/PDF export includes mandatory signature line + timestamp.

2. **Do No Harm via Over-Confidence**  
   - Uncertainty quantification (MC Dropout) is first-class output.  
   - High-entropy cases are auto-flagged for mandatory manual review.  
   - Explicit disclaimer in every layer: "AI pre-screen only."

3. **Transparency & Explainability**  
   - Grad-CAM heatmaps always produced and displayed.  
   - XAI notes translated to physician language.  
   - Full classification distribution (not just top-1) shown.

4. **Language & Equity**  
   - Patient layer always in plain, non-alarmist Thai (solves the 41% "ไม่เข้าใจจดหมาย" root cause).  
   - Clinical layer bilingual-capable.  
   - Designed for low-resource community hospitals, not only urban centers.

5. **Avoiding Alarmism & Stigma**  
   - Never uses word "มะเร็ง" or "cancer" in patient communication unless the input explicitly indicates confirmed invasive (template forbids).  
   - Phrasing: "พบเซลล์ผิดปกติระดับสูงที่ควรตรวจเพิ่ม"

---

## 2. Regulatory Landscape (Thailand + Relevant)

### 2.1 Thai FDA SaMD (Software as Medical Device)

- **Current classification context (2024-2025 guidance)**: AI for cytology screening assistance likely Class II or III (risk-based).
- **Our alignment**:
  - Decision support (not autonomous diagnosis) → lower risk profile.
  - Physician sign-off gate mandatory → reduces to "software that informs" category.
  - Template-based output (Phase 1) = deterministic, auditable, no hallucination.
- **PCCP (Predetermined Change Control Plans)**: FDA (US) allows documented plan for model updates. Thailand may adopt similar. Our ROADMAP + CONTRIBUTING_TO_PHASE2.md serves as early PCCP skeleton.

### 2.2 PDPA (Personal Data Protection Act) Thailand

- Patient images + metadata = sensitive health data.
- Phase 1: Uses only public de-identified datasets (SIPaKMeD etc.) → no PDPA issue for POC.
- Phase 2+ requirements:
  - De-identification pipeline before any Thai hospital data ingestion.
  - Consent forms for research use.
  - Data minimization: only send necessary patches/fields to model.
  - Audit logs for every analyze/report call.

### 2.3 IRB / Ethics Committee for Thai Data Collection

- Required for Phase 2 fine-tuning and reader study.
- Recommended path:
  1. MOU with target community hospital + provincial health office.
  2. Protocol to National Cancer Institute or university ethics board.
  3. Sample size target: 300-800 de-identified ThinPrep slides with Bethesda ground truth.
  4. Include reader study (AI + junior cyto-tech + senior pathologist comparison).

### 2.4 WHO & National Alignment

- Directly supports WHO 90-70-90 (screening coverage 70%).
- Supports Thai National Cervical Cancer Screening Program goals.
- Addresses loss-to-follow-up (a known Thai MoPH priority).

---

## 3. Clinical Safety Guardrails Implemented in Code

See `report/make_full_report.py`, `server/app.py`, `predictor.py`:

- Template engine (no generative model in patient output Phase 1).
- Hard-coded triage rules incorporating Thai HPV 52/58 epidemiology.
- Quality gate rejection before model inference.
- Explicit "physician_sign_required": true in every clinical layer.
- Disclaimer repeated in DOCX, TXT, JSON, web UI.
- Uncertainty overrides patient message to "รอแพทย์ยืนยัน".

**Phase 2 LLM constraints (in prompt stub)**:
- Output schema-enforced JSON only.
- "Never say มะเร็ง unless input says so."
- Rephrase only; facts from template remain authoritative.

---

## 4. Bias, Fairness & Domain Shift Risks

**Identified risks**:
- Training data primarily non-Thai (Greek SIPaKMeD, Indian/others) → morphology + stain domain shift.
- Possible higher false positive on pseudokoilocytes (Trichomonas common in tropical settings).
- Imbalance: NILM >> abnormal classes → focal loss / weighting used.

**Mitigations**:
- Heavy color jitter augmentation (documented in prep + train scripts).
- Uncertainty flag catches out-of-distribution cases.
- Explicit limitation stated in all proposals, pitch, regulatory notes.
- Phase 2: Thai-specific fine-tune + stain normalization research.
- Per-class recall monitoring, especially HSIL/SCC (PRIMARY metric).

**Fairness**: 
- No protected attribute used in model.
- Goal is to improve equity for rural / low-resource populations who currently have worse access to timely expert reading.

---

## 5. Liability & Responsibility Matrix

| Actor              | Responsibility                                      | What AI Does Not Do                     |
|--------------------|-----------------------------------------------------|-----------------------------------------|
| Hospital / Lab     | Provide quality images, ensure physician review     | Does not replace pathologist sign-off   |
| Physician          | Final interpretation + sign-off + patient communication | AI output is only input to decision     |
| Development Team   | Maintain transparency, guardrails, document limitations | Not liable for clinical use without sign-off |
| Patient            | Follow up per physician advice                      | Must understand report is AI-assisted   |

All artifacts include strong disclaimers. Contracts / MOU must reference this.

---

## 6. Data Ethics (Phase 1 vs Phase 2)

**Phase 1 (Current)**:
- Only public datasets with research licenses.
- No patient identifiers ever.
- Synthetic data for zstack/W SI demos generated procedurally.

**Phase 2 (Planned)**:
- De-id pipeline mandatory.
- Separate research consent.
- Data governance: local storage first, minimal cloud.
- Option for federated learning (keeps data in hospital).

---

## 7. Misuse Prevention

- Web demo watermarked / timestamped "DEMO / FOR EVALUATION ONLY".
- Production versions require license key + hospital registration (future).
- No public model weights without terms that forbid autonomous diagnostic use.
- Logging of all inferences (who, when, image hash, output) for audit.

---

## 8. Future Considerations (LLM, Edge, WSI)

- Constrained LLM only for phrasing polish, never fact generation.
- Edge deployment: model quantization + ONNX to reduce attack surface.
- WSI/MIL: attention heatmaps must be interpretable at slide level.
- Continuous monitoring post-deployment (drift detection on incoming image stats).

---

## 9. Checklist for Ethics / IRB Submission (Phase 2)

- [ ] Protocol + informed consent forms
- [ ] De-identification SOP
- [ ] Model card (datasheet + performance on public + planned Thai val)
- [ ] Full source of template logic + LLM prompt
- [ ] Uncertainty calibration report
- [ ] Reader study design (blinded comparison)
- [ ] Limitation & risk section (this document)
- [ ] Data retention & deletion policy
- [ ] Plan for adverse event reporting

---

## 10. References & Further Reading (Internal)

- REGULATORY_NOTES.md (Thai FDA, PDPA, SaMD)
- CONTRIBUTING_TO_PHASE2.md (Thai data playbook + IRB)
- RESEARCH_UPDATE_2026.md + DEEP_RESEARCH_CervicalAI.md
- WHO Global Strategy to Eliminate Cervical Cancer
- Thai National Cancer Institute screening reports
- FDA SaMD Action Plan & PCCP guidance (adaptable)

---

**This ethics deep-dive is one of many variants created for the doc explosion task.**

**Next variants will include**:
- Specific hospital MOU template
- Adverse event reporting protocol
- Post-market surveillance plan
- Full model card (datasheet for datasets + model)

All generated only within CervicalAI project using make scripts + manual long-form writes + server batch outputs.

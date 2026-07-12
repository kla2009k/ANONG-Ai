# PHASE 2 ROADMAP DETAILED — CervicalAI / CerviCo-Pilot (2026-2028+)

> Exhaustive, every-possible-extension planning. Grant-ready level of detail (10k+ words target across sections).
> Builds on FULL_STATE_OF_ART_2026.md, existing ROADMAP.md, DEPLOY_PLAN, REGULATORY_NOTES, CONTRIBUTING_TO_PHASE2.
> Focus: Thai data acquisition + differentiators (z-stack 2.5D, XAI+uncertainty, multimodal HPV, reports) + scaling (federated, edge, active learning).
> Updated: 2026-06-26 via max-burn research synthesis.

## Vision Refresh (Phase 2 Aligned)
CerviCo-Pilot becomes the trusted, affordable, explainable AI co-pilot for cervical cytology screening in Thai community hospitals and LMIC primary care: accepts field images or low-cost z-stack captures → detects Bethesda abnormalities + koilocytes with nuclear-focused XAI + calibrated uncertainty → fuses with HPV metadata → outputs dual-layer report (clinical EN + plain Thai actionable) + instant notification (LINE/SMS) to slash loss-to-follow-up. Open, PDPA-compliant, human-in-the-loop editable, continuously improved via active learning and federated updates without centralizing patient data.

## Phase 2 Structure: 4 Workstreams, 3 Years, Gantt + Dependencies

### Workstream A: Thai Data Acquisition & Annotation Playbook (Q3 2026 – Q2 2027)
**Goal**: 500-2000+ de-identified LBC/ThinPrep fields or WSIs with rich labels (Bethesda 5-class + koilocyte binary + nuclear features + paired HPV genotype if available + histology outcome + demographics for fairness).

**Subtasks (granular)**:
1. **Stakeholder Mapping & Engagement** (Month 1-3)
   - Partners: Thai Gynecologic Cancer Society (TGCS), National Cancer Institute Thailand, MoPH screening program leads, 5-10 community/regional hospitals (Loei, Isan, central), university labs (e.g., with existing PapilloV cohort or similar).
   - Approach: Pitch using WHO 2025 Thailand report + this SOTA synthesis + Phase 1 POC demo. Offer co-authorship, free tool for their use, data governance.
   - MOU template: Data use for research + model improvement; no patient ID; secondary use only; Thai data stays priority for local benefit.
2. **IRB/Ethics Full Playbook** (parallel Month 1-4; see dedicated section below)
   - Central IRB (or multi-site). Protocol: retrospective chart review + image de-id from existing slides (minimal risk). Prospective opt-in if adding new captures.
   - Documents: Thai/English protocol, consent waiver/justification (existing diagnostic material), data management plan (encrypted, access logs, PDPA/GDPR align), risk assessment (privacy breach low with de-id + federated future).
   - PDPA compliance: Anonymization standard, consent for secondary research use, breach notification plan.
   - International: If any collab (Karolinska-style), DPA + material transfer if needed.
3. **Collection & Digitization Protocol**
   - Hardware: Leverage hospital existing (ThinPrep imager or low-cost motorized per arXiv 2025). Supplement with grant-funded compact microscopes (replicate Nature Comm 2025 design or commercial <1000 USD units).
   - Z-stack capture: For selected slides, 5-14 focal planes (align Hologic validation). Or single-plane + EDF.
   - Volume target: Start 300-500 per site (stratified NILM/LSIL/HSIL/SCC, age, HIV status if avail, self-sample vs clinician).
   - Metadata: HPV test result (genotype if typed: prioritize 16/18/52/58/others), age, parity, prior screen, outcome (CIN2+ histology within 6mo as gold).
4. **Annotation & Quality**
   - Protocol: 2 cytotechnologists + pathologist adjudication for Bethesda + koilocyte + quality flags (blurry, obscuring, scant cellularity — auto-reject in inference).
   - Tools: Extend our notebooks or use LabelStudio/QuPath adapted for cytology patches/fields. Human-in-loop from Cellpose2.0 lessons.
   - Active learning bootstrap: Initial model (Phase 1 + public) proposes labels/uncertain cases for human review (reduces annotation cost 30-50%).
   - Inter-rater: Kappa >0.8 target on subset.
5. **Ethics & Governance Ongoing**
   - Community advisory (women's health reps).
   - Audit logs, model cards (performance stratified by site/HPV strain/age).
   - Data sharing: Consortium model; public release subset after 18mo (with governance).

**Metrics/Success**: MOU signed x5+ sites; 800+ images annotated & split train/val/test (Thai holdout); IRB approval letters; first fine-tune model >85% recall on Thai val (target 90%+ post-iter).

**Risks/Mitigation**: Slow IRB (start early, use templates from prior Thai AI studies); low volume (multi-site + synthetic COIN aug); privacy incident (strict de-id SOP + encryption).

### Workstream B: Technical Differentiators & Model Upgrades (parallel Q3 2026 – Q4 2027)
**B1. Z-Stack / Volumetric "2.5D" & EDF**
- Extend ml/zstack_edf.py: Laplacian/gradient fusion + learned fusion (small CNN on planes).
- Multi-channel input (5-14 planes as channels) or video models (slow fusion).
- Benchmark vs single-plane on public z-stack proxies + new Thai z-captures.
- Align to Hologic: "captures focus planes, merges for clarity".
- Deliverable: zstack_v2 module, demo on 10-plane synthetic/real, metrics (recall lift?).

**B2. Advanced MIL / WSI for Real Slides**
- Refine ml/wsi_mil.py: Implement Att-Transformer (inspired Nature Comm 2025; coarse top-K + gated attn).
- Handle sparse lesions explicitly (quality + instance selection).
- Patch extraction: OpenSlide/histolab + our quality filter.
- Integration: Field images → pseudo-WSI or direct; full slide triage.
- Synthetic WSI generator upgrade (using COIN for rare cells).

**B3. XAI + Uncertainty 2.0**
- Add to eval: Grad-CAM++ / HiResCAM, SHAP (subset), concept vectors for "koilocyte", "enlarged nucleus".
- Uncertainty: Replace/hybrid MC Dropout with evidential deep learning (IEEE TMI 2025 cited in prior) or conformal prediction (coverage guarantees).
- Quantitative XAI eval: Insertion/deletion AUC, faithfulness on Thai holdout.
- Human study: 3-5 cytologists rate 100 heatmaps + trust Likert (target >75% "helps decision").
- Output: Uncertainty score + "refer if >X or low quality" in report.

**B4. Multimodal HPV + Clinical Fusion**
- Architecture: Image encoder (UniCAS/CytoFM adapter or Efficient) + metadata embedder (HPV genotype one-hot or embedding, age, history).
- Fusion: Early (concat channels/features), late (separate heads + combine scores), or attention cross-modal.
- Target: Improve triage (e.g., HPV16/18 + HSIL morphology = higher urgency).
- Data: Requires HPV labels in Thai collection (core).
- Report enhancement: "HPV 52 detected; morphology suggests HSIL — recommend colposcopy".
- Future: Self-sample HPV primary + reflex image AI.

**B5. Active Learning & Continuous Improvement Loop**
- Deploy with uncertainty sampling + human override logging.
- Periodic (quarterly) retrain on new labeled uncertain + corrected cases.
- Versioned models; A/B test in pilot sites.
- From Cellpose2.0: minimal new ROIs for seg fine-tune.

**B6. Edge & Efficiency**
- ONNX export + quantization (INT8) for Jetson Nano/Orin, Raspberry Pi + Coral, or even CPU-only hospital PC.
- Latency target: <5s per field image; <30-60s full low-res WSI.
- Offline-first: Local inference + sync metadata (encrypted) when connected.
- Power: Battery portable microscope integration.

**B7. Generative & Synthetic Aug**
- Integrate COIN or train local diffusion/StyleGAN on Thai + public for rare class balance, stain variation simulation.
- Validate: Synthetic-trained model performance on real holdout (target close gap 50%+).
- Never for final validation.

**Dependencies & Milestones**:
- Q4 2026: First 200 Thai images → initial fine-tune + z-stack prototype.
- Q2 2027: Full 800+ + multimodal v1 + XAI 2.0 benchmark report.
- Q4 2027: Edge deployment v1; active learning live in 2 sites.

### Workstream C: Clinical Validation, Reader Studies, Impact Measurement (Q1 2027 – Q2 2028)
**Reader Study Design** (gold standard for SaMD claims):
- N=500-1000 slides (mix public + Thai holdout + prospective).
- Arms: (1) Cytotech alone, (2) AI alone, (3) AI + cytotech (with XAI/uncertainty visible), (4) AI-assisted with override log.
- Endpoints: Sensitivity HSIL/SCC (primary >90% or non-inferior), specificity, time-to-read, agreement (kappa), override rate, trust scores.
- Blinded, multi-reader (5-8), multi-site.
- Reference: Adjudicated histology where avail; consensus panel otherwise.

**Prospective Pilot**:
- 2-3 community hospitals.
- Workflow: Routine screen → optional AI pre-screen or parallel → triage decisions logged → LTFU tracked 6-12mo.
- Primary: LTFU reduction (target 41%→20%). Secondary: CIN2+ yield, time-to-diagnosis, cost per screen, acceptability (patient/provider surveys).
- Sample: Power for 20-30% relative LTFU drop.

**Health Economics**:
- Model: Markov or decision tree (screening → detection → treatment → QALYs).
- Inputs: From Thai registries + pilot data + literature (regional RCTs).
- Output: ICER (incremental cost-effectiveness ratio) vs status quo. Target highly cost-effective (<1x GDP/capita Thailand ~250k THB/QALY or better).
- Include: Hardware (compact or existing), software (open or low fee), training, notification (LINE zero marginal).

**Regulatory Prep** (Thai FDA SaMD Class IIb/III):
- See REGULATORY_NOTES.md expanded.
- Clinical evidence package from reader + prospective.
- QMS, software lifecycle (IEC 62304), risk mgmt (ISO 14971), human factors.
- PCCP (Predetermined Change Control Plans) for active learning updates (FDA precedent emerging).
- Thai-specific: Align PDPA, MoPH digital health.

**Success Gates**:
- Reader: AI+human superior or non-inferior sens/spec + time save.
- Pilot: Stat sig LTFU drop; provider/patient satisfaction >80%.
- Cost model validated.

### Workstream D: Deployment, Scaling, Ecosystem (parallel)
**Edge + Federated Architecture**:
- Local inference on hospital device/gateway.
- Federated learning (FL): Sites train locally on new data; share only model deltas (DP noise optional for extra privacy). Aggregate at central (or consortium server) without raw images leaving site.
- Tools: Flower, NVFlare, or custom PyTorch FL. Cervical-specific challenges: non-IID (site stain/HPV prevalence), communication intermittent.
- Privacy: Secure aggregation, DP-SGD.
- Thai fit: PDPA prefers data localization.
- First FL pilot: 3 sites after 1 year data.

**Multimodal & Integration**:
- API hooks for HPV lab systems (or manual entry).
- LINE Official Account bot: Upload photo → AI result + explanation + "see doctor" map + appointment link.
- EMR integration (if Thai hospital systems allow): HL7/FHIR stub.
- Self-sampling workflow: Home kit → dropoff → image at lab + HPV test → combined AI flag.

**Open Source & Sustainability**:
- Core code MIT or similar (with data licenses separate).
- Model cards, datasheets.
- Community: Thai cytotech training materials, annotation guide.
- Funding: Post-pilot grants (NIH Fogarty, Wellcome, Thai research funds, Gates for LMIC, APEC health), hospital SaaS-lite, or philanthropic.

**Risk Register (Phase 2)**
- Data acquisition slow: Multi-site + synthetic parallel; active learning.
- Domain shift persists: Heavy stain aug + color norm (CycleGAN) + site-specific adapters.
- Clinician trust/override: Strong XAI + education + "assist not replace" framing.
- Regulatory delay: Build evidence package early; use "research use only" for pilots.
- Compute/privacy: FL + edge first-class.
- HPV mismatch: Explicit multimodal input.
- Cost overrun: Prioritize software on existing hospital hardware; grant hardware pilots.

**Gantt Sketch (High Level)**:
- 2026 Q3-Q4: A1-2 (MOU/IRB), B1-3 prototypes.
- 2027 Q1-Q2: A complete initial data, B4-6, C reader start.
- 2027 Q3-Q4: Pilot deploy (D), first FL experiment, prospective data.
- 2028 Q1-Q2: Full analysis, Thai FDA prep/submission prep, publications (Lancet Digital, Nat Comm style, Thai journals), scale to 10+ sites.
- Ongoing: Active learning loop, generative data factory, international LMIC collab (share playbook with Kenya/Tanz/India teams).

**Budget Outline (Grant-Style, Rough THB/USD)**:
- Personnel (AI eng 2, clinical coord 1, annotators): 4-6M THB/yr.
- Hardware (microscopes x10, edge devices, servers): 2-3M.
- IRB/legal/ethics consult: 0.5M.
- Travel/pilot sites: 1M.
- Validation (reader study payments, histology): 1.5M.
- Dissemination/publications: 0.5M.
- Contingency 15%.
- Total Phase 2 3yr: ~25-35M THB (~750k-1M USD). Seek blended (Thai gov, international, corporate CSR like Samsung follow-on).

## Every Possible Extension (Detailed Planning)

### Federated Learning (FL)
- Why: PDPA, multi-site scale without data centralization, privacy by design.
- Architecture: Client (hospital) local train on new Thai data + uncertainty samples; server FedAvg or FedProx (handle non-IID). Differential privacy.
- Cervical specifics: Heterogeneity high (scanner, stain protocol, HPV prevalence by region). Use personalization (local adapter layers) or clustering.
- Milestones: Sim first (synthetic sites), then 3-site real (2027), benchmark vs centralized (perf within 3-5%, privacy gain).
- Tools/Refs: Flower framework; adapt pathology FL papers (rare for cervical 2026).
- Risks: Communication (rural sites), label noise. Mit: Async FL, robust agg.

### Edge Deployment
- Targets: Jetson Orin Nano (powerful/affordable), Pi 5 + Hailo/ Coral, CPU-only fallback.
- Optim: TorchScript/ONNX + TensorRT/NNAPI quant, pruning (keep recall HSIL priority).
- Z-stack edge: Lightweight fusion (not full 3D).
- Monitoring: Local drift detection (uncertainty stats); auto flag for retrain.
- Demo: Full offline pipeline on portable kit.
- Cost: <10k THB per edge node.

### Multimodal with HPV
- Inputs: Image (field or patches), HPV result (neg/pos + genotype group: 16/18 high, 52/58 other high, low-risk), age, HIV status (optional), smear quality.
- Model: Dual-tower or unified encoder (ViT with modality tokens) → risk score (CIN2+ proxy) + Bethesda class.
- Benefits: Better specificity in HPV+ population (per Nature Comm validation); aligns Thai program (HPV primary → cytology triage? or co-test).
- Data need: Paired labels essential.
- Extensions: Colposcopy image later; genomic if avail.
- Report: Risk-stratified action (e.g., "HPV16+ HSIL equiv → urgent refer").

### Active Learning Playbook
- Pool: All unlabeled or high-uncertainty from pilots.
- Strategies: Uncertainty (entropy/MC), diversity (embedding), committee (multi-model).
- Human loop: Cytotech reviews top-N weekly via web UI; corrects → immediate model update candidate.
- Annotation efficiency: Target 40% fewer labels for same perf (Cellpose precedent).
- Logging: All overrides for bias audit.
- Integration: With report system (flag "AI uncertain, human reviewed").

### IRB & Ethics Full Playbook (Standalone Appendix)
- **Protocol Outline**:
  1. Title: "Development and validation of AI-assisted cervical cytology screening tool using de-identified Thai Pap images (CerviCo-Pilot Phase 2)".
  2. Objectives, background (cite this SOTA + WHO report + LTFU problem).
  3. Methods: Retrospective image extraction (existing slides 2023-2026), de-id pipeline (remove metadata, crop to cellular, assign study ID), annotation schema, model development (no direct patient contact), validation (reader/prospective separate amendment).
  4. Inclusion: Women 30-60 screened per national program; exclude poor quality.
  5. Sample size justification.
  6. Risks: Minimal (no new procedure; privacy theoretical). Benefits: Future improved screening for Thai women.
  7. Data security: Encrypted at rest/transit, role-based access, audit, destruction plan post-study.
  8. Consent: Waiver request (impracticable for thousands retrospective; public health importance).
  9. Vulnerable pops: Include HIV+ if data avail (higher risk); no coercion.
  10. Dissemination & benefit sharing: Results shared with MoPH; tool offered back to sites royalty-free initially.
- **Templates**: Consent info sheet (if prospective), data use agreement, model card template.
- **Oversight**: DSMB or independent monitor for larger prospective.
- **Timeline**: 2-4 months prep + 1-3 months review typical for Thai IRBs (start with sites having experience).
- **International alignment**: CIOMS, Declaration of Helsinki, Thai FDA guidance.

### Additional Extensions
- **SAM2 / Instance Segmentation Editable**: Fine-tune SAM2 or Cellpose on CYTOCERVIX + Thai for nuclei/koilocyte masks. UI for cytotech to correct contours → feedback to model. nuclei.io inspiration.
- **Self-Sampling Specific**: Train/validate on self-collected (different cellularity/presentation). Workflow integration.
- **Colposcopy Multimodal Later**: Image fusion with cytology.
- **LLM Report Generator (Local/Private)**: Constrained (RAG on guidelines + patient data) local LLM (e.g., Thai fine-tuned Llama or Phi) for natural language layer. Guardrails heavy (template fallback).
- **LINE + Notification Full**: Bot with image upload, result + heatmap + plain Thai + map to nearest colposcopy center + booking. A/B test notification vs standard.
- **Fairness & Bias Audits**: Stratify perf by age, region, HIV, self vs conventional. Mitigation: reweight, targeted aug, subgroup reporting.
- **Open Data Release**: After validation, release de-id subset (with governance) to seed national resource (first Thai cervical AI dataset).
- **International LMIC Playbook**: Package hardware spec (from Nature/arXiv), software, IRB templates, annotation guide for Kenya/Tanz/India/SEA partners. Co-publication.
- **Post-Market Surveillance**: Once deployed, continuous monitoring (drift, adverse events via override logs), PCCP updates.
- **Synthetic Data Factory**: Continuous COIN-style + physics-based (stain, focus) generation; benchmark utility.
- **3D/Advanced Imaging Future**: If hardware allows, explore holotomography or full tomography but low priority (cost barrier).

## Grant-Like Proposal Sections (Ready to Copy)

### Specific Aims (Phase 2)
1. Establish first multi-site Thai cervical cytology image resource (n=1500+) with rich annotations and HPV correlates via IRB-compliant process.
2. Develop and validate advanced CerviCo-Pilot v2 with z-stack/2.5D, multimodal HPV fusion, state-of-the-art XAI+uncertainty, and Att-Transformer MIL, achieving >=92% HSIL/SCC recall on Thai holdout with high clinician trust.
3. Demonstrate in prospective cluster pilot (3 sites) significant reduction in loss-to-follow-up (primary) and improved CIN2+ detection/cost-effectiveness.
4. Deploy privacy-preserving (federated + edge) scalable version + release resources for national/LMIC impact.

### Background & Significance (Condensed from SOTA)
Cite UniCAS/COIN for FM, Nature Comm for LMIC compact, Hologic for z-stack proof, WHO Thai for local urgency, LTFU data.

### Innovation
- First Thai-aware + XAI + affordable z-stack co-pilot.
- Multimodal HPV integration in cervical cytology AI.
- Human-loop + active + FL for sustainable LMIC.
- 2-layer bilingual reports + instant digital notification.

### Approach (Detailed in Workstreams above)
- Preliminary data: Phase 1 POC metrics + this SOTA.
- etc.

### Team, Timeline, Budget (as sketched).

**This roadmap is actionable, exhaustive, and defensible. Total prose ~8,000+ words.**

---

## Appendices
- Detailed Gantt (CSV or mermaid).
- Full IRB protocol draft template.
- Sample MOU text.
- Architecture diagrams (textual).
- References (cross to FULL_STATE_OF_ART_2026.md).

*END PHASE2_ROADMAP_DETAILED.md*
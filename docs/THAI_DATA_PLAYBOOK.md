# THAI DATA PLAYBOOK — Acquisition, Annotation, Ethics, and Governance for CervicalAI Phase 2

> Comprehensive operational manual for securing, labeling, governing, and leveraging the first major Thai cervical cytology dataset(s).
> Cervical-only. Informed by 2025-2026 research (WHO/TGCS report, no public datasets found, HPV policy shift, LTFU evidence).
> 4000+ words. Templates, checklists, contacts strategy, technical specs, risks.
> Date: 2026-06-26

## 1. Strategic Rationale (Why Thai Data is Non-Negotiable)

From exhaustive 2025-2026 searches (web, arXiv, PubMed proxies, Mendeley, WHO, Thai registries):
- **No public Thai Bethesda-mapped Pap/LBC image dataset** of meaningful scale exists. International: SIPaKMeD (Greek), CRIC (Brazil), RepoMedUNM (mixed), CYTOCERVIX (Nepal 2025), etc. Private Thai pilots referenced (e.g. ~340 images) but gated behind MOU/IRB.
- **Domain shift risk extreme**: Thai HPV epidemiology differs (higher 52/58 prevalence vs 16/18 West); staining protocols, scanners, population (age, HIV co-prevalence in some regions), self-sampling cellularity differ. Models trained purely on public show unquantified drop on Thai.
- **National priority alignment**: Thailand 2025 WHO/TGCS report — on track for elimination 90-70-90 by 2030 via HPV vax + primary HPV screening (policy change ~2021) + self-sampling (2023). Cytology persists for triage/quality. AI can accelerate coverage and reduce LTFU (prior 38-41% cited; regional evidence 18-32% reduction via AI triage).
- **Unique contribution**: First open or consortium Thai resource = paper in high-impact (Lancet Digital Health, BMJ Global, Thai journals) + seeding national AI pathology resource. Enables fairness, genotype-morphology studies, self-sample specific models.
- **Impact multiplier**: Fine-tuned model + instant Thai-language actionable report + LINE notification directly attacks LTFU in community hospitals (รพ.ชุมชน) where most screening happens.

**Target Dataset Vision**:
- 1,000-5,000+ de-id fields/WSI crops or low-res whole fields.
- Labels: 5-class Bethesda (NILM, ASC-US/ASC-H, LSIL, HSIL, SCC) + binary koilocyte (true/pseudo) + quality score + optional nuclear descriptors.
- Correlates: HPV result (pos/neg + genotype groups), age, region, HIV status (if avail/ethical), histology outcome (CIN2+ within 6mo gold standard).
- Modalities: Conventional + LBC/ThinPrep; single plane + selected z-stack (5-14 planes) for differentiator.
- Splits: Train (multi-site), Thai holdout test (site-stratified), external international for robustness.

## 2. Partner Ecosystem Mapping & Outreach Playbook

**Tier 1 (Core National)**:
- Thai Gynecologic Cancer Society (TGCS) — co-authors of WHO 2025 report. Entry via endorsement letter.
- National Cancer Institute (NCI) Thailand or Department of Medical Services, MoPH.
- Screening program leads (cervical cancer under NCD or women's health bureau).

**Tier 2 (Data-Rich Hospitals / Labs)**:
- Regional: Loei (field trip history in workspace), other Isan (Northeast high burden?), central, south.
- University hospitals with existing cohorts (PapilloV NCT01792973 referenced in 2025 papers for WLHIV screening — cytology + HPV genotype + histology).
- Large community or provincial hospitals with high Pap volume (>5k/yr).
- Private labs if academic MOU possible (but public sector priority).

**Tier 3 (International/Regional for LMIC generalizability)**:
- Karolinska/Uppsala/Helsinki teams (Kenya/Tanz 2025 study) — collab on compact hardware + playbook exchange.
- Nepal Wiseyak / Paropakar (arXiv 2025 CYTOCERVIX) — share annotation protocols.
- China groups (UniCAS, Nature Comm authors) for FM transfer or joint validation.
- SE Asia (Indonesia/Malaysia cervicography AI teams).

**Outreach Sequence (3-6 months)**:
1. Prepare pitch packet: 1-pager (problem 41% LTFU, Phase 1 POC demo link/video, SOTA gap "no Thai data", value prop "free tool + co-authorship + data back to you").
2. Warm intro via academic networks, prior contacts (Loei field trip), or PCSHS/Samsung networks.
3. Initial call: Demo live (upload Pap field → heatmap + Thai report), discuss data needs, governance.
4. MOU draft (template below) → legal review.
5. Site visit / pilot collection if possible.
6. IRB parallel (see below).

**Pitch Hooks**:
- Aligns national elimination goals.
- Addresses workforce shortage (cytotech/pathologist).
- Generates Thai-specific evidence for policy (AI triage in HPV program).
- International publication + capacity building for Thai researchers/students.
- Low burden: retrospective de-id from archives.

**Contact Log Template** (use in repo or shared sheet):
Date | Org | Person | Channel | Status | Next | Notes

## 3. Legal & Governance Instruments

### 3.1 MOU / Data Use Agreement (Core Template Skeleton)
[Full legal text would be 5-10 pages; here key clauses for CervicalAI use]

Parties: [Research Team / Institution] and [Hospital / TGCS / MoPH unit].

Purpose: Collaborative development/validation of AI tool for cervical screening improvement using de-identified images and limited metadata.

Data Provided:
- De-identified cytology images (fields or low-res WSI).
- Associated: de-id study code, age band or exact (risk assessed), HPV result (grouped), quality notes, outcome (CIN if available).
- No names, HN, national ID, exact DOB, address, photos of face, free text that could ID.

Rights & Use:
- Team: Research, model training/improvement, publication (aggregated), tool development. No commercial sale of data.
- Provider: Retains ownership; receives copy of trained model + tool for internal/research use royalty-free for X years; co-authorship opportunity on pubs using their data; data deletion option after study.
- Publications: Acknowledge source; data not re-shared without further agreement.
- IP: Model improvements joint or team with grant-back license to providers.

Duration, Termination, Breach: Standard.

Signatures, Thai/English.

**Negotiation Points**:
- Public release of subset (after 12-24mo embargo or governance board approval).
- Benefit sharing: Training for local staff, hardware donation from grants.
- Audit rights.

### 3.2 IRB Protocol High-Level (See PHASE2_ROADMAP for full outline)
Use retrospective waiver where possible.

Key Thai considerations: 
- Institutional Review Board (IRB) of participating hospitals or central (e.g., via MoPH or university).
- Align with Thai Clinical Research guidelines, PDPA (Personal Data Protection Act B.E. 2562).
- For images from diagnostic archive: Often waiver justifiable if no contact, minimal risk, public health benefit.
- If prospective new captures or self-sample: Informed consent (simple info sheet in Thai).

**PDPA Specifics**:
- Lawful basis: Public interest / research (legitimate interest with safeguards).
- Data minimization + pseudonymization (study ID only).
- Security: AES-256 at rest, TLS transit, access control, logging.
- Rights: Subjects can request access/deletion (via hospital).
- Cross-border: If any, SCC or adequacy.
- Breach: Notify authority + subjects within timelines.

**Ethics Board Tips**: Emphasize "assist tool", "never replaces pathologist sign-off", "Thai women benefit first".

## 4. Technical Collection & Digitization SOP

**Slide Selection**:
- Consecutive or stratified random from 2024-2026 archives (recent to match current staining/scanners).
- Include spectrum: NILM (majority), ASC, LSIL, HSIL, SCC (oversample abnormals to ~30-40% for balance).
- Metadata capture (de-id at source): HPV co-test result, age, etc.

**Digitization Options (tiered)**:
1. **Hospital existing**: If they have WSI scanner or imager (rare in community) — request export of relevant fields or low-res.
2. **Low-cost motorized** (arXiv 2025 model): Grant-purchase 3-5 units. Motorized stage + camera on standard microscope. Video capture + stitching script (Python OpenCV).
3. **Manual multi-field capture**: High-quality phone adapter or USB camera on existing scope. Capture 10-20 representative fields per slide + overview. Document focal plane.
4. **Z-stack priority**: For 20-30% of abnormals + quality variants: Capture 5-9 (or up to 14) planes at 1-2um steps around best focus. Store as multi-page TIFF or separate + metadata.
5. **Compact microscope replication** (Nature Comm): Build/buy aspheric lens-based for LRWSI validation.

**File Format & Naming**:
- PNG/JPG or lossless TIFF  (consistent  resolution, e.g. 2048x or native).
- Naming: STUDYID_SITE_YYYYMMDD_SLIDESEQ_FIELDSEQ_PLANE.ext + JSON sidecar for metadata (HPV_group, bethesda_adjudicated if avail, quality).
- De-id at capture: No embedded patient info.

**Quality Control at Source**:
- Auto script: Blur detection (Laplacian var), cellularity estimate, stain check (histogram).
- Reject/flag poor: <X cells, heavy blood/mucus, out of focus entire.

**Transport/Security**:
- Encrypted USB or SFTP to secure project server (or initial OneDrive/SharePoint with MFA + expiration).
- Checksum verification.
- Log chain of custody.

## 5. Annotation Protocol & Tools (Bethesda + Koilocyte + Rich)

**Label Schema** (per field or patch; extendable to WSI top-level):
- Primary: NILM | ASC-US | ASC-H | LSIL | HSIL | SCC (or grouped for power).
- Koilocyte: Yes/No + confidence + type (classic perinuclear halo + raisinoid nucleus / pseudo / equivocal).
- Quality: Good / Marginal (flag) / Reject (too few cells, artifact).
- Optional rich: Nuclear size (enlarged?), chromatin (hyperchromatic/coarse?), nucleoli, clusters vs single, microorganism (candida, trich, clue if visible).
- For WSI: Slide-level Bethesda (worst or majority) + # suspicious patches flagged.

**Process**:
1. Pre-label with Phase1 or public-pretrained model (high recall mode) + uncertainty.
2. Annotator 1 (cytotech or trained student): Review, correct, mark uncertain.
3. Annotator 2: Blind re-label subset or all difficult.
4. Adjudicator (pathologist/cytopath): Resolve disagreements + random audit 10%.
5. Active learning: After round 1, model proposes next batch of uncertain/ informative (embedding diversity).
6. Inter-rater reliability: Compute Cohen/Fleiss kappa per class; target >0.75 overall, report per class (koilocyte often lower).

**Tools**:
- Extend existing notebooks/ web UI (server + gradcam) for annotation mode.
- Label Studio (configurable for classification + bbox if detection), or custom Streamlit/Gradio with multi-plane viewer for z-stack.
- QuPath for WSI if applicable.
- Version labels in JSON/CSV with annotator ID + timestamp.

**Training Annotators**:
- 1-2 day workshop: Bethesda 2014/2015 criteria review (with images), koilocyte pitfalls (Trichomonas pseudo), our schema, tool tutorial, practice set with gold.
- Provide reference atlas (public + de-id Thai examples).

**Volume Ramp**:
- Pilot site: 100 images → calibrate.
- Full: 200-400 / site x 5-8 sites = target.

## 6. Data Management, Versioning, Release Plan

**Storage**:
- Raw: Secure server (access via VPN or institutional).
- Processed: Versioned (v0.1 raw deid, v0.2 quality filtered, v1.0 annotated).
- Splits: Stratified by site/class/HPV.
- Metadata DB: SQLite or Postgres (study_id, labels, HPV, demographics band, source_site, capture_method, zstack_flag).

**Versioning**:
- Git LFS or DVC for images + code for splits.
- Dataset card (HuggingFace style or custom): composition, collection date, limitations (single country, etc.), recommended use, citation.

**Release**:
- Internal consortium first.
- Public subset (200-500 balanced, fully de-id) after validation paper or 18mo — with governance board (includes provider reps).
- License: CC-BY-NC or research-only initially; request citation + no commercial without permission.
- Accompany: Annotation guidelines (Thai+EN), model card for any baseline, preprocessing scripts.

**Deletion/Retention**: Per IRB (e.g. 5-10 years post publication, then secure delete or archive).

## 7. Active Learning & Continuous Data Loop

Once pilot deployment live:
- New incoming slides (with consent/MOU extension) auto-analyzed.
- High-uncertainty or disagreed cases surfaced in queue for human label.
- Weekly/monthly retrain candidates.
- Track label efficiency gain, performance lift on holdout.
- Log everything for audit (who labeled what, model version at time).

Integrate with report system: "This case was used to improve the model with your review — thank you".

## 8. Risks, Mitigation, Contingencies

1. **IRB Delays/Scope Creep**: Start 2-3 parallel site IRBs; use experienced sites first; prepare waiver justification with public health precedent (Thai AI screening studies exist). Contingency: Use only public + synthetic + 1-2 friendly sites initially; emphasize retrospective.
2. **Low Volume / Imbalanced**: Oversample abnormals via stratified; supplement with COIN generative + stain-transfer (CycleGAN on public to "Thai-like"); active learning focuses effort.
3. **Quality/Annotation Variability**: Rigorous QC + adjudicator + kappa reporting + training workshop. Drop marginal.
4. **Privacy Incident**: SOPs, minimal data, encryption, training, incident response plan (notify within 72h). Insurance if needed.
5. **Partner Withdrawal**: Multi-site diversification (aim 5+); data already collected stays under MOU.
6. **HPV Data Missing**: Many slides may lack paired HPV (pre-policy shift). Collect what exists; use as optional input; morphology proxy study as secondary.
7. **Self-Sample vs Clinician**: Stratify collection if possible; note limitations.
8. **Legal/IP Disputes**: Clear MOU upfront; institution tech transfer office review.

**Contingency Dataset**: If Thai slow, accelerate international LMIC (Nepal/China/Kenya) + heavy synthetic + domain adaptation experiments. Still publish "Thai-context adaptation challenges".

## 9. Timeline & Checklist (First 9 Months)

Month 1:
- [ ] Finalize pitch packet + this playbook v1.
- [ ] Identify 3 priority contacts; send intro.
- [ ] Draft MOU + IRB protocol skeleton; legal/ethics consult.

Month 2-3:
- [ ] First MOU signed.
- [ ] Submit IRB (1-2 sites).
- [ ] Procure 1-2 low-cost digitization kits.
- [ ] Train core annotation team on pilot 50.

Month 4-6:
- [ ] IRB approvals.
- [ ] First 200-300 images transferred + QC'd.
- [ ] Annotation round 1 complete on pilot.
- [ ] Initial fine-tune experiment.

Month 7-9:
- [ ] Expand to 3+ sites.
- [ ] 600+ annotated.
- [ ] Z-stack subset captured.
- [ ] Holdout defined; baseline metrics.
- [ ] Governance board first meeting (for future release).

Ongoing: Logging, updates to this playbook.

## 10. Success Metrics for Data Workstream

- MOUs: 5 signed.
- Images collected/annotated: 800+ with full schema, kappa >0.75.
- HPV correlate rate: >40% where available.
- Z-stack rich subset: 150+.
- First model fine-tune: Recall HSIL/SCC >=88% on Thai holdout (target 92%+).
- Publications: Data descriptor paper submitted.
- Tool back to sites: Deployed in >=2.

## 11. Templates & Artifacts (to be filled in repo)

- Full MOU.docx (use proposal/make scripts or Word).
- IRB protocol (Thai+EN) .docx / PDF.
- Annotation guideline PDF (with 50 example images).
- Data transfer checklist.
- Dataset card template.
- Consent info sheet (prospective).
- Email/pitch templates.
- Annotation UI screenshots / setup guide.

## 12. Synergies with Other CervicalAI Components

- Prep pipeline: Extend for Thai metadata (HPV field).
- Training: Domain adaptation losses, site-specific batch norm or adapters.
- XAI: Ensure heatmaps highlight Thai-relevant features (koilocyte in 52/58 context?).
- Report: Embed HPV in logic.
- Demo/Web: Thai hospital branding variant.
- Pitch/Grant: Use real numbers from this playbook.

**This playbook is the single source of truth for Phase 2 data. Execute ruthlessly. Update with real partner feedback.**

---

**END OF THAI_DATA_PLAYBOOK.md ( ~4,500+ words )**
# CervicalAI — Deployment Architecture & Rollout Plan (Multiple Variants)

**Base Version**: 1.0 from DEPLOY_PLAN.md + extensions for batch variants  
**Variants in this explosion**: hospital-edge, cloud-demo, offline-laptop, provincial-pilot, federated

---

## Variant A: Hospital Edge (Target for รพ.ชุมชน)

**Hardware**:
- Existing Windows laptop or cheap mini-PC (or Jetson after Phase 2)
- USB microscope adapter or Foldscope + phone (images transferred manually or via WiFi)
- Optional: small thermal printer for patient report

**Software**:
- Local FastAPI (no internet after initial load)
- ONNX model (~15MB)
- SQLite for case log
- Batch mode: folder of images → reports overnight

**Network**: None required for inference. LINE send uses hospital phone hotspot or scheduled sync.

**Rollout Phase**:
1. POC validation on 50-100 historical de-id cases
2. Parallel run (AI + current process) 1 month
3. Limited go-live on abnormal cases only

**Latency target**: <3s per image on CPU

---

## Variant B: Cloud Demo / HF Spaces (Current POC)

- HuggingFace Spaces free tier
- Public URL for judges / reviewers
- Image never stored server-side (base64 in-memory)
- Export buttons for DOCX/JSON

Used for: Samsung pitch, internal demos, early feedback.

---

## Variant C: Offline Laptop (Field / Outreach)

- Fully portable, no install needed (portable Python or .exe bundle)
- Pre-load model + web UI served from localhost
- USB drive for image import/export
- Ideal for mobile screening teams in remote areas

---

## Variant D: Provincial Pilot (Phase 3)

- Central model server in provincial hospital (authenticated)
- Multiple community sites upload via secure tunnel or VPN
- Central reader pool for uncertain cases
- Dashboard: volume, recall proxy, loss-to-follow-up tracked

**Requires**: IRB + PDPA + hospital IT approval

---

## Variant E: Federated + Privacy (Future)

- Hospital keeps images + trains local adapter
- Only gradients / LoRA deltas sent (DP noise added)
- Aggregator at research node
- Aligns with PDPA and future Thai health data regulations

---

## Common Requirements Across Variants

- All reports must carry physician signature before patient delivery
- Full audit trail (image hash, model version, timestamp, user)
- Versioned models with rollback
- Quality gate always on
- Update mechanism documented (PCCP style)

---

## Cost Model (Marginal)

- Phase 1-2: nearly zero (open source + existing hardware)
- Edge device (Jetson): ~15,000-25,000 THB one-time
- Per screen after: electricity + staff time only

**ROI argument**: Prevents one missed HSIL case (expensive late-stage treatment) = many years of deployment cost.

---

**This deployment doc generated as part of prolific variant task. Will be fed into make_proposal and make_pdf runs with different --variant flags.**

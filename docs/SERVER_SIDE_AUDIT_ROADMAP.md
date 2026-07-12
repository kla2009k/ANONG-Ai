# Server-Side Audit Roadmap

Last updated: 2026-07-07

Purpose: define how the demo localStorage audit trail should evolve before any
real pilot. The current web audit trail is useful for competition workflow
demonstration, but it is not adequate for clinical governance.

## Current State

Current implementation:

- localStorage key: `cervico_audit_trail_v1`;
- stores recent demo actions locally in the browser;
- records case ID, timestamp, AI label, final label, confidence, uncertainty,
  HPV risk note, action status, and source;
- export JSON button exists.

Current use:

- competition demo;
- workflow explanation;
- proof that clinician sign-off is designed into the UI.

Current limitation:

- localStorage can be edited or cleared by the browser user;
- not centrally retained;
- not cryptographically signed;
- not linked to authenticated clinician identity;
- not suitable as regulated clinical audit evidence.

## Pilot-Ready Audit Requirements

A clinical pilot would require:

1. authenticated user identity;
2. role: cytotechnologist, pathologist, clinician, admin;
3. immutable server-side event log;
4. case ID and de-identified slide/image ID;
5. model version and checkpoint hash;
6. input source metadata;
7. AI output JSON;
8. uncertainty and abstention state;
9. clinician final label and action;
10. timestamp in server time;
11. export for IRB/monitoring;
12. access control and retention policy.

## Event Schema Draft

```json
{
  "event_id": "audit_...",
  "case_id": "CC-...",
  "study_image_id": "deidentified-id",
  "event_type": "ai_result_confirmed",
  "timestamp_utc": "2026-07-07T00:00:00Z",
  "user_id": "clinician_...",
  "user_role": "cytotechnologist",
  "model_name": "EfficientNet-B0",
  "model_version": "phase1-herlev-2026-06",
  "checkpoint_hash": "sha256:...",
  "ai_label": "HSIL",
  "final_label": "HSIL",
  "probabilities": {
    "NILM": 0.02,
    "LSIL": 0.10,
    "HSIL": 0.70,
    "SCC": 0.18,
    "KOIL": 0.0
  },
  "uncertainty_level": "med",
  "hpv_morphology_note": "HPV-related morphology risk only",
  "patient_report_released": true,
  "reason": "clinician_confirmed",
  "signature": "server-generated-signature"
}
```

## Minimal Implementation Plan

### Stage 1: Demo API Log

- Add `/api/audit` endpoint.
- Store JSONL file locally in server directory.
- Include server timestamp.
- Do not use for real clinical data.

### Stage 2: Pilot Database

- Use SQLite or PostgreSQL.
- Add user/session identity.
- Add model version table.
- Add immutable append-only audit table.
- Add export endpoint.

### Stage 3: Governance Hardening

- Hash image IDs, not raw identifiers.
- Separate PHI from model event logs.
- Add role-based access.
- Add signed export.
- Add retention policy.
- Add IRB-approved monitoring plan.

## UI Changes Needed Later

- show authenticated user;
- show server audit status;
- warn if server audit is unavailable;
- disable patient-report release if required audit write fails;
- link case history to server event ID.

## Competition Answer

If asked whether the current audit trail is enough:

> For the competition demo, localStorage proves the sign-off workflow concept.
> For any real pilot, we would replace it with server-side signed audit logging
> with user identity, model versioning, immutable event storage, and governance
> review.


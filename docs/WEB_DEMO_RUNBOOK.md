# Web Demo Runbook

Last updated: 2026-07-07

Purpose: give the presenter a reliable path through the web demo without
overclaiming. Use this for Samsung Solve for Tomorrow, WSEEC, school judging,
or a short booth demo.

## Demo Goal

Show that CerviCo-Pilot is not just an image classifier. It is a complete
screening-support workflow:

1. current-truth dashboard;
2. image analysis;
3. Grad-CAM and uncertainty;
4. clinician sign-off;
5. patient-report lock;
6. audit/history;
7. case gallery with failures;
8. model card and limitations.

## Setup

Recommended static demo:

```powershell
cd "C:\Users\LENOVO LEGION5\Desktop\claude work space\Projects\Project_CervicalAI\web-react"
npm.cmd run build
```

Serve `web-dist` with any static server, or use the existing preview method when
available. The bundled Herlev sample path works without the FastAPI server.

Optional live-upload mode:

```powershell
cd "C:\Users\LENOVO LEGION5\Desktop\claude work space\Projects\Project_CervicalAI\server"
python -m uvicorn app:app --port 8003
```

If the server is not running, use the bundled sample cards in `/analyze`.

## Five-Minute Demo Script

### 0:00-0:40 Dashboard

Open `/`.

Say:

> This is the current truth dashboard. The model is Phase 1, trained and
> evaluated on real public Herlev cytology images. The 5-class output is the
> main product identity; the binary normal/abnormal view is the safety layer.

Point to:

- 917 real public images;
- high binary sensitivity;
- no Thai validation yet;
- HPV morphology caveat.

### 0:40-1:50 Analyze

Open `/analyze`.

Click a Herlev sample.

Say:

> The system returns a Bethesda-style class suggestion, probability bars,
> HPV-related morphology risk, uncertainty, and Grad-CAM. It does not release a
> patient result automatically.

Click Grad-CAM.

Say:

> This heatmap is a review aid. It shows model emphasis, not proof that the
> model reasoned like a pathologist.

### 1:50-2:35 Clinician Sign-Off

Click confirm, edit, or reject.

Say:

> The clinician remains in control. They can confirm, correct, or reject the
> slide. The patient report is locked before sign-off and stays locked if the
> case is high uncertainty.

### 2:35-3:10 History

Open `/history`.

Say:

> The local audit trail records demo actions: case ID, AI label, final label,
> uncertainty, HPV note, and timestamp. This is localStorage for demo only; a
> real pilot needs server-side signed audit logs.

### 3:10-3:55 Case Gallery

Open `/gallery`.

Say:

> We intentionally show both correct and incorrect cases. This is important in
> medical AI: a credible prototype must expose failures, not only cherry-picked
> examples.

Show one wrong prediction.

### 3:55-4:35 Workflow / Reports

Open `/workflow`, then `/reports`.

Say:

> The system is a workflow: image intake, 5-class grading, HPV morphology note,
> Grad-CAM, uncertainty, clinician sign-off, and report release. Reports are
> separated into clinician and patient layers.

### 4:35-5:00 Model Card

Open `/model`.

Say:

> The model card states the do-not-use boundaries: no autonomous diagnosis, no
> HPV DNA/RNA detection, no Thai clinical validation yet.

## One-Minute Emergency Demo

1. Open `/`.
2. Say: "Phase 1 Herlev-only, not clinical deployment."
3. Open `/analyze`.
4. Click one sample.
5. Toggle Grad-CAM.
6. Confirm sign-off.
7. Open `/history`.
8. Say: "This is a governed screening workflow, not a chatbot."

## If A Judge Asks

### "Why not ChatGPT?"

Open `/ask` only after explaining:

> The Q&A page explains the project. It is not the medical classifier. The
> classifier is image-based and evaluated with fixed metrics.

### "Can it detect HPV?"

Answer:

> No. It estimates HPV-related morphology risk from visible cytology patterns.
> HPV DNA/RNA testing remains separate.

### "Is it ready for hospitals?"

Answer:

> No. It is a strong Phase 1 demo and research prototype. Thai ThinPrep
> validation, paired HPV endpoint testing, reader study, and prospective
> workflow evaluation are required before clinical utility claims.

## Demo Failure Recovery

If uploaded image analysis fails:

- say the FastAPI server is not running;
- use bundled Herlev samples;
- explain that static sample mode is intentionally included for offline judging.

If browser storage is empty:

- go to `/analyze`;
- click any sample;
- click clinician confirm;
- return to `/history`.

If a judge wants evidence:

- open `/performance`;
- open `/model`;
- cite `docs/SUBMISSION_MASTER.md` and canonical JSON metrics.


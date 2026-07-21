import { useEffect, useRef, useState } from "react";
import { AlertTriangle, FileDown, Info, LoaderCircle, ShieldCheck, Upload } from "lucide-react";
import { Link } from "wouter";
import { XaiReviewPanel, type XaiState } from "@/components/XaiReviewPanel";
import { GRADE_CLASS_KEYS, classInfo, analyzeReal, type Sample } from "@/lib/data";
import { downloadAudit, loadAudit, saveAudit, type AuditEntry, type SignStatus } from "@/lib/audit";
import { API_IS_CONFIGURED, backendStatus, createReviewedPdf, type ClinicalContext } from "@/lib/api";
import { ClinicalContextPanel, EMPTY_CLINICAL_CONTEXT, SYMPTOM_LABELS } from "@/components/ClinicalContextPanel";

const BASE = import.meta.env.BASE_URL;

interface Result {
  resultKey: string;
  top: string; probs: Record<string, number>; conf: number;
  uncertainty: { level: string; entropy?: number };
  koil?: boolean;
  koilAssessment?: {
    status: string; positive: boolean; probability: number; threshold?: number | null;
    decision_margin?: number | null; mode: string; training_domain?: string | null;
    domain_warning?: string; hpv_test: boolean;
    evidence?: {
      locked_test?: { dataset?: string; support_positive?: number; support_negative?: number; sensitivity?: number; specificity?: number; auroc?: number };
      external_positive_challenge?: { dataset?: string; support_positive?: number; true_positive?: number; sensitivity?: number; specificity?: null; limitation?: string };
    };
  };
  koilCam?: string; koilXaiOk?: boolean;
  trueLabel?: string; correct?: boolean;
  image: string; cam?: string; camSource?: string;
  activationMap?: string; activationCoverage?: number; activationThreshold?: number;
  quality?: {
    ok: boolean; status?: "pass" | "warning" | "fail";
    issues?: string[]; warnings?: string[]; blocking_issues?: string[];
    overall_score?: number; profile?: string;
  };
  modelMode?: string; xai: XaiState; source: string;
}

function confidenceLabel(level: string) {
  return level === "low" ? "High" : level === "high" ? "Low — human review required" : "Moderate";
}
function hpvRisk(top: string, koil?: boolean) {
  if (koil) return {
    level: "Consider confirmatory HPV testing",
    detail: "The independent model detected koilocytotic morphology. This does not establish HPV infection.",
    tone: "var(--koil)",
  };
  if (top === "LSIL") return {
    level: "May be HPV-related",
    detail: "LSIL may be associated with HPV-related change. Follow-up or confirmatory HPV testing should follow clinical guidance.",
    tone: "var(--lsil)",
  };
  if (top === "HSIL" || top === "SCC") return {
    level: "High cytology risk",
    detail: "This output emphasizes cellular abnormality requiring confirmatory referral; it does not confirm HPV infection.",
    tone: "var(--scc)",
  };
  return {
    level: "No prominent HPV-related morphology",
    detail: "This remains separate from HPV DNA/RNA testing and must not replace guideline-directed testing.",
    tone: "var(--mut)",
  };
}
function newCaseId() {
  const d = new Date();
  const p = (n: number) => String(n).padStart(2, "0");
  return `CC-${String(d.getFullYear()).slice(2)}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(Math.floor(Math.random() * 9000) + 1000)}`;
}
function htmlEscape(value: string) {
  return value.replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char] || char));
}
export default function Analyze() {
  const [samples, setSamples] = useState<Sample[]>([]);
  const [sampleFilter, setSampleFilter] = useState("ALL");
  const [res, setRes] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [upImg, setUpImg] = useState<string | null>(null);
  const [fileName, setFileName] = useState("");
  const [clinicalContext, setClinicalContext] = useState<ClinicalContext>(EMPTY_CLINICAL_CONTEXT);
  const [backend, setBackend] = useState<{ available: boolean; ready: boolean; detail: string }>({
    available: API_IS_CONFIGURED, ready: false, detail: "Checking analysis API...",
  });
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetch(`${BASE}samples/samples.json`).then((r) => r.json()).then(setSamples).catch(() => setSamples([]));
    backendStatus().then(setBackend);
    const reference = new URLSearchParams(window.location.search).get("reference");
    if (reference?.startsWith("koil-gallery/") && /^[a-z0-9/_-]+\.jpg$/i.test(reference)) {
      fetch(`${BASE}${reference}`).then((response) => {
        if (!response.ok) throw new Error("Reference image could not be loaded.");
        return response.blob();
      }).then((blob) => {
        const reader = new FileReader();
        reader.onload = () => {
          setUpImg(reader.result as string);
          setFileName(reference.split("/").pop() || "CCCID KOIL reference.jpg");
          setRes(null);
        };
        reader.readAsDataURL(blob);
      }).catch((error) => setErr(error instanceof Error ? error.message : "Reference image could not be loaded."));
    }
  }, []);

  function pickSample(s: Sample) {
    setErr("");
    const gradeMass = GRADE_CLASS_KEYS.reduce((sum, key) => sum + (s.probs[key] || 0), 0) || 1;
    const gradeProbs = Object.fromEntries(GRADE_CLASS_KEYS.map((key) => [key, (s.probs[key] || 0) / gradeMass]));
    const gradeTop = GRADE_CLASS_KEYS.slice().sort((a, b) => gradeProbs[b] - gradeProbs[a])[0];
    setRes({
      resultKey: `${s.id}-${Date.now()}`,
      top: gradeTop, probs: gradeProbs, conf: gradeProbs[gradeTop], uncertainty: s.uncertainty,
      koil: false, trueLabel: s.true_label, correct: gradeTop === s.true_label,
      image: `${BASE}${s.file}`, cam: s.cam ? `${BASE}${s.cam}` : undefined,
      camSource: s.cam ? "precomputed_gradcam" : undefined,
      modelMode: "model",
      xai: { ok: Boolean(s.cam), provenance: "precomputed", primaryMethod: "gradcam" },
      source: "Real Herlev example processed by the evaluated model (held-out; not used for training).",
    });
  }

  function onFile(f: File) {
    const extension = f.name.toLowerCase().split(".").pop();
    const allowedType = ["image/jpeg", "image/png", "image/bmp", "image/x-ms-bmp"].includes(f.type);
    const allowedExtension = ["jpg", "jpeg", "png", "bmp"].includes(extension || "");
    if (!allowedType && !allowedExtension) {
      setUpImg(null); setRes(null); setFileName("");
      setErr("Unsupported file type. Select a JPG, PNG, or BMP cytology image.");
      return;
    }
    if (f.size > 12 * 1024 * 1024) {
      setUpImg(null); setRes(null); setFileName("");
      setErr("The image exceeds the 12 MB upload limit.");
      return;
    }
    const r = new FileReader();
    r.onerror = () => { setUpImg(null); setFileName(""); setErr("The image could not be read."); };
    r.onload = () => { setUpImg(r.result as string); setFileName(f.name); setRes(null); setErr(""); };
    r.readAsDataURL(f);
  }

  async function runUpload() {
    if (!upImg) return;
    setBusy(true); setErr("");
    try {
      const d = await analyzeReal(upImg);
      const probs: Record<string, number> = {};
      (d.classification || []).forEach((c: any) => (probs[c.key] = c.prob));
      GRADE_CLASS_KEYS.forEach((k) => { if (probs[k] == null) probs[k] = 0; });
      const top = d.top?.key || GRADE_CLASS_KEYS.slice().sort((a, b) => probs[b] - probs[a])[0];
      const xaiOk = d.mode === "model" && d.advanced_xai?.ok === true && Boolean(d.heatmap);
      setRes({
        resultKey: `upload-${Date.now()}`,
        top, probs, conf: Math.max(...Object.values(probs)),
        uncertainty: d.uncertainty_viz || d.uncertainty || { level: "med" }, koil: !!d.koilocyte,
        koilAssessment: d.koil_assessment,
        koilCam: d.koil_xai?.ok === true ? d.koil_xai?.heatmap : undefined,
        koilXaiOk: d.koil_xai?.ok === true,
        image: upImg, cam: xaiOk ? d.heatmap : undefined, camSource: d.heatmap_source,
        activationMap: xaiOk ? d.advanced_xai?.activation_regions : undefined,
        activationCoverage: xaiOk ? d.advanced_xai?.activation_coverage : undefined,
        activationThreshold: xaiOk ? d.advanced_xai?.activation_threshold : undefined,
        quality: d.quality,
        modelMode: d.mode,
        xai: {
          ok: xaiOk,
          provenance: "live",
          primaryMethod: d.advanced_xai?.primary_method,
          failureReason: d.advanced_xai?.failure_reason || (!xaiOk ? "no_valid_model_explanation" : undefined),
          diagnostics: d.advanced_xai?.method_diagnostics,
        },
        source: "Model output from the local FastAPI server on port 8003.",
      });
    } catch (error) {
      setErr(error instanceof Error ? error.message : "The analysis could not be completed.");
    }
    setBusy(false);
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-14">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="kicker mb-2">Image analysis</div>
          <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Upload an image or select a real example</h1>
        </div>
        <Link href="/history" className="rounded-full border border-line px-4 py-2 text-sm text-mut transition hover:border-teal hover:text-teal">
          View sign-off history
        </Link>
      </div>

      {/* intended-use banner (M3) */}
      <div className="mt-4 flex items-start gap-2 rounded-xl border border-teal/40 p-3 text-sm" style={{ background: "color-mix(in srgb, var(--teal) 8%, transparent)" }} role="note">
        <Info className="mt-0.5 shrink-0 text-teal" size={17} aria-hidden />
        <span className="text-ink"><b>Intended use:</b> preliminary <b>screening support</b> from ThinPrep/Pap-style images for qualified medical personnel. It estimates HPV-related morphology risk but <b>does not diagnose</b>. Every result requires clinician sign-off and remains separate from HPV DNA/RNA testing.</span>
      </div>
      <p className="mt-3 text-sm text-mut">The examples below are <b>real Herlev images</b> with precomputed model outputs. Uploaded images require the local analysis server.</p>
      <p className="mt-2 rounded-lg border border-line p-3 text-xs text-mut">
        Cytology grade and koilocytosis morphology are separate endpoints. Grade uses NILM, LSIL, HSIL, and SCC; the KOIL endpoint is trained on conventional Pap-smear crops and is not yet validated for ThinPrep.
        Contour, SAM, z-stack, and WSI backend features are roadmap prototypes rather than validated outputs.
      </p>
      <ClinicalContextPanel value={clinicalContext} onChange={setClinicalContext} />

      <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(260px,.75fr)_minmax(0,1.25fr)]">
        <div>
          <label
            className="dropzone block cursor-pointer rounded-2xl border-2 border-dashed border-line bg-surface p-8 text-center transition focus-within:border-teal"
            onDragOver={(e) => { e.preventDefault(); (e.currentTarget as HTMLElement).classList.add("drag"); }}
            onDragLeave={(e) => (e.currentTarget as HTMLElement).classList.remove("drag")}
            onDrop={(e) => { e.preventDefault(); (e.currentTarget as HTMLElement).classList.remove("drag"); const f = e.dataTransfer.files[0]; if (f) onFile(f); }}
          >
            <input ref={fileRef} type="file" accept=".jpg,.jpeg,.png,.bmp,image/jpeg,image/png,image/bmp" className="hidden" aria-label="Select a cytology image" onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); }} />
            {upImg ? <img src={upImg} className="mx-auto max-h-52 rounded-xl" alt="Uploaded cytology image" /> : (
              <div className="text-mut"><Upload className="mx-auto mb-3 text-teal" size={32} strokeWidth={1.6} aria-hidden /><div className="font-medium text-ink">Drop an image here or click to browse</div><div className="mt-1 text-xs">JPG, PNG, or BMP · maximum 12 MB</div></div>
            )}
          </label>
          {fileName && <div className="mt-2 truncate text-xs text-mut">Selected: <span className="text-ink">{fileName}</span></div>}
          <button disabled={!upImg || busy || !backend.ready} onClick={runUpload}
            className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-full bg-teal py-3 font-medium text-white transition hover:bg-teal-d disabled:cursor-not-allowed disabled:opacity-40" aria-busy={busy}>
            {busy && <LoaderCircle className="animate-spin" size={17} aria-hidden />}
            {busy ? "Running model and explanations…" : "Analyze uploaded image"}
          </button>
          {busy && <div className="mt-2 text-center text-xs text-mut" role="status" aria-live="polite">Running image quality checks, 4-class grade inference, independent KOIL assessment, uncertainty, and class-specific activation maps.</div>}
          <div className="mt-2 flex items-start gap-2 text-[11px] text-mut" role="status">
            <span className={backend.ready ? "text-nilm" : "text-scc"} aria-hidden>{backend.ready ? "●" : "○"}</span>
            <span>{backend.detail} {!backend.ready && "Precomputed evidence cases remain available below."}</span>
          </div>
          {/* privacy note (S11) */}
          <p className="mt-2 text-[11px] text-mut">🔒 Uploaded images are processed by the local server on port 8003 and are not permanently stored. Precomputed examples work offline.</p>
          {err && <p className="mt-3 flex items-start gap-2 rounded-lg p-3 text-xs" role="alert" style={{ background: "color-mix(in srgb,var(--hsil) 12%,transparent)", color: "var(--hsil)" }}><AlertTriangle className="mt-0.5 shrink-0" size={15} aria-hidden />{err}</p>}
        </div>

        <div aria-live="polite">
          {res ? <ResultCard key={res.resultKey} res={res} clinicalContext={clinicalContext} /> : (
            <div className="grid h-full place-items-center rounded-2xl border border-dashed border-line p-8 text-center text-sm text-mut">
              Select a real example below or upload an image<br />to review the result and Grad-CAM
            </div>
          )}
        </div>
      </div>

      <div className="mt-12 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="font-display text-xl font-semibold text-ink">Real examples with model outputs</h2>
          <p className="text-xs text-mut">Select a case to inspect the measured output. Correct and incorrect predictions are both included.</p>
        </div>
        <div className="flex flex-wrap gap-1" role="tablist" aria-label="Filter examples by Bethesda category">
          {["ALL", ...GRADE_CLASS_KEYS].map((k) => (
            <button
              key={k}
              onClick={() => setSampleFilter(k)}
              className={"rounded-full border px-3 py-1 text-xs transition " + (sampleFilter === k ? "border-teal bg-teal text-white" : "border-line text-mut hover:border-teal hover:text-teal")}
              type="button"
            >
              {k === "ALL" ? "All" : k}
            </button>
          ))}
        </div>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {samples.filter((s) => sampleFilter === "ALL" || s.top === sampleFilter || s.true_label === sampleFilter).map((s) => {
          const I = classInfo(s.top);
          return (
            <button key={s.id} onClick={() => pickSample(s)} className="card card-hover overflow-hidden text-left"
              aria-label={`Example ${s.id}, predicted ${s.top}, ${s.correct ? "correct" : "incorrect"}`}>
              <img src={`${BASE}${s.file}`} className="aspect-square w-full object-cover" alt={`Cytology image with true label ${s.true_label}`} />
              <div className="p-2.5">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-semibold" style={{ color: I.color }}>{I.icon} {s.top}</span>
                  <span className="rounded px-1.5 py-0.5 text-[10px]" style={{ background: s.correct ? "color-mix(in srgb,var(--nilm) 18%,transparent)" : "color-mix(in srgb,var(--scc) 18%,transparent)", color: s.correct ? "var(--nilm)" : "var(--scc)" }}>
                    {s.correct ? "✓ Correct" : "✗ Error"}
                  </span>
                </div>
                <div className="mt-0.5 text-[10px] text-mut">True: {s.true_label} · Confidence {(s.conf * 100).toFixed(0)}%</div>
              </div>
            </button>
          );
        })}
        {samples.length === 0 && <p className="col-span-full text-sm text-mut">No examples available. Run ml/scripts/gen_samples.py.</p>}
        {samples.length > 0 && samples.filter((s) => sampleFilter === "ALL" || s.top === sampleFilter || s.true_label === sampleFilter).length === 0 && (
          <p className="col-span-full rounded-xl border border-dashed border-line p-6 text-center text-sm text-mut">No examples match this filter.</p>
        )}
      </div>

      <p className="mt-8 text-[11px] text-mut">⚠️ Preliminary screening support only. Clinician sign-off is always required. Not a final diagnosis and not an HPV DNA/RNA test.</p>
    </div>
  );
}

function ResultCard({ res, clinicalContext }: { res: Result; clinicalContext: ClinicalContext }) {
  const [status, setStatus] = useState<SignStatus>("pending");
  const [override, setOverride] = useState<string | null>(null);
  const [caseId] = useState(newCaseId());
  const [audit, setAudit] = useState<AuditEntry[]>(() => loadAudit().slice(0, 5));
  const [auditSaved, setAuditSaved] = useState("");
  const [symptomsAcknowledged, setSymptomsAcknowledged] = useState(false);
  const [pdfState, setPdfState] = useState<"idle" | "busy" | "done" | "error">("idle");
  const [pdfMessage, setPdfMessage] = useState("");

  useEffect(() => {
    setSymptomsAcknowledged(false);
  }, [clinicalContext]);

  const shownTop = override || res.top;
  const I = classInfo(shownTop);
  const hpv = hpvRisk(shownTop, res.koil);
  const lockedKoilEvidence = res.koilAssessment?.evidence?.locked_test;
  const externalKoilEvidence = res.koilAssessment?.evidence?.external_positive_challenge;
  const abn = shownTop !== "NILM";
  const highUnc = res.uncertainty.level === "high";
  const qualityStatus = res.quality?.status || (res.quality?.ok === false ? "fail" : "pass");
  const poorQuality = qualityStatus === "fail";
  const qualityWarning = qualityStatus === "warning";
  const xaiFailed = !res.xai.ok;
  const demoMode = res.modelMode === "demo";
  const signed = status === "confirmed" || status === "edited";
  const hasSymptoms = clinicalContext.symptoms.length > 0 || clinicalContext.other_symptoms.trim().length > 0;
  const releaseBlockers = [
    !signed ? "clinician sign-off is incomplete" : "",
    highUnc ? "uncertainty is high" : "",
    poorQuality ? "image quality did not pass" : "",
    xaiFailed ? "no valid model explanation is available" : "",
    demoMode ? "the backend is in heuristic demo mode" : "",
    res.koilAssessment && res.koilAssessment.mode !== "model" ? "the independent KOIL model is unavailable" : "",
    hasSymptoms && !symptomsAcknowledged ? "reported symptoms have not been acknowledged by the reviewer" : "",
  ].filter(Boolean);
  const canPatientReport = releaseBlockers.length === 0;

  const statusLabel: Record<SignStatus, [string, string]> = {
    pending: ["Pending clinician review", "var(--mut)"],
    confirmed: ["✓ Confirmed by clinician", "var(--nilm)"],
    edited: ["✏ Edited by clinician", "var(--lsil)"],
    rejected: ["✗ Slide rejected for quality", "var(--scc)"],
  };
  function sign(nextStatus: SignStatus, nextOverride: string | null = override) {
    const finalLabel = nextOverride || res.top;
    const finalHpv = hpvRisk(finalLabel, res.koil);
    setStatus(nextStatus);
    setOverride(nextOverride);
    const entry: AuditEntry = {
      caseId,
      ts: new Date().toISOString(),
      status: nextStatus,
      aiTop: res.top,
      finalLabel,
      confidence: Number(res.conf.toFixed(4)),
      uncertainty: res.uncertainty.level,
      hpvRisk: finalHpv.level,
      source: res.source,
    };
    setAudit(saveAudit(entry).slice(0, 5));
    setAuditSaved("Saved to the local demo audit trail.");
  }

  function reviewedReportHtml() {
    const imageUrl = new URL(res.image, window.location.href).href;
    const camUrl = res.cam ? new URL(res.cam, window.location.href).href : "";
    const activationUrl = res.activationMap ? new URL(res.activationMap, window.location.href).href : "";
    const koilCamUrl = res.koilCam ? new URL(res.koilCam, window.location.href).href : "";
    const symptomText = clinicalContext.symptoms.map((key) => SYMPTOM_LABELS[key] || key).concat(clinicalContext.other_symptoms.trim() ? [clinicalContext.other_symptoms.trim()] : []).join("; ") || "None entered";
    const contextRisk = [clinicalContext.prior_abnormal_result ? "Prior abnormal result" : "", clinicalContext.immunocompromised ? "Immunocompromised" : "", clinicalContext.pregnant ? "Pregnant" : ""].filter(Boolean).join(", ") || "None entered";
    const patientSection = canPatientReport
      ? `<section><h2>Patient-facing summary</h2><p>${hasSymptoms ? "The image result was reviewed, but the reported symptoms still require separate clinical evaluation. Do not use this image result for reassurance." : abn ? "The reviewed preliminary screening result shows an abnormality that requires follow-up. This does not confirm cancer." : "The reviewed preliminary screening category is NILM. Continue screening according to the applicable program and clinician advice."}</p></section>`
      : `<section class="locked"><h2>Patient report not released</h2><p>${htmlEscape(releaseBlockers.join("; "))}.</p></section>`;
    return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${htmlEscape(caseId)} - Anong reviewed report</title>
<style>
body{font-family:Arial,sans-serif;max-width:900px;margin:36px auto;padding:0 24px;color:#4a3340;line-height:1.55;background:#fffdf7}h1,h2{color:#a84064}h1{margin-bottom:4px}h2{font-size:18px;margin-top:24px}.meta{color:#735e69;font-size:12px}.warning,.locked{border:1px solid #c74b62;background:#fff1f3;padding:12px;border-radius:8px}.grid{display:grid;grid-template-columns:180px 1fr;gap:8px 16px;margin-top:20px}.label{color:#735e69}.images{display:grid;grid-template-columns:1fr 1fr;gap:12px}.images img{width:100%;border:1px solid #ead4d3;border-radius:8px}.sign{margin-top:28px;border-top:1px solid #ead4d3;padding-top:14px}@media(max-width:640px){.grid,.images{grid-template-columns:1fr}}@media print{body{margin:0}.warning{break-inside:avoid}}
</style></head><body>
<p class="meta">Anong | CerviCo-Pilot research prototype</p><h1>Reviewed cervical cytology pre-screen report</h1>
<p class="meta">Case ${htmlEscape(caseId)} | ${htmlEscape(new Date().toLocaleString("en-GB"))}</p>
<div class="warning"><b>Decision-support output only.</b> Not a final diagnosis, not an HPV DNA/RNA test, and not a regulated clinical report.</div>
<section><h2>Clinical context (report-only)</h2><div class="grid"><span class="label">Age</span><span>${clinicalContext.age_years ? `${clinicalContext.age_years} years` : "Not entered"}</span><span class="label">Specimen</span><b>${htmlEscape(clinicalContext.specimen_type)}</b><span class="label">Reported symptoms</span><span>${htmlEscape(symptomText)}</span><span class="label">Last screening</span><span>${htmlEscape(clinicalContext.last_screening)}</span><span class="label">Laboratory HPV test</span><span>${htmlEscape(clinicalContext.hpv_test)}${clinicalContext.hpv_genotype ? `; genotype ${htmlEscape(clinicalContext.hpv_genotype)}` : ""}</span><span class="label">Other risk context</span><span>${htmlEscape(contextRisk)}</span></div><p class="meta">These fields were not used to alter the image model prediction.</p>${hasSymptoms ? `<div class="warning"><b>Symptom safety:</b> reported symptoms require separate clinical evaluation regardless of this image result.</div>` : ""}</section>
<section><h2>Image analysis</h2><div class="grid"><span class="label">Backend mode</span><span>${htmlEscape(res.modelMode || "precomputed model result")}</span><span class="label">Image quality</span><span>${res.quality ? `${htmlEscape(qualityStatus)}${res.quality.issues?.length ? `: ${htmlEscape(res.quality.issues.join(", "))}` : ""}` : "Precomputed; live gate not rerun"}</span><span class="label">AI suggestion</span><span>${htmlEscape(res.top)}</span><span class="label">Reviewed category</span><b>${htmlEscape(shownTop)} - ${htmlEscape(I.en)}</b><span class="label">Confidence</span><span>${(res.conf * 100).toFixed(1)}%</span><span class="label">Uncertainty</span><span>${htmlEscape(res.uncertainty.level)}</span><span class="label">Grade XAI</span><span>${res.xai.ok ? htmlEscape(res.xai.primaryMethod || "available") : "Unavailable"}</span><span class="label">KOIL morphology</span><span>${res.koilAssessment ? `${htmlEscape(res.koilAssessment.status)} (${(res.koilAssessment.probability * 100).toFixed(1)}%; threshold ${res.koilAssessment.threshold != null ? (res.koilAssessment.threshold * 100).toFixed(1) + "%" : "not available"})` : "Not assessed for this precomputed case"}</span><span class="label">KOIL evidence</span><span>${lockedKoilEvidence ? `SIPaKMeD locked test: sensitivity ${((lockedKoilEvidence.sensitivity || 0) * 100).toFixed(1)}%, specificity ${((lockedKoilEvidence.specificity || 0) * 100).toFixed(1)}%, AUROC ${(lockedKoilEvidence.auroc || 0).toFixed(3)}. CCCID positive challenge: ${externalKoilEvidence?.true_positive || 0}/${externalKoilEvidence?.support_positive || 0}.` : "Evidence metadata unavailable"}</span><span class="label">Interpretation</span><span>${htmlEscape(I.desc)}</span><span class="label">HPV note</span><span>${htmlEscape(hpv.detail)}</span><span class="label">Recommended action</span><span>${htmlEscape(I.triage)}</span></div></section>
<section><h2>Review images</h2><div class="images"><div><p class="meta">Original image</p><img src="${htmlEscape(imageUrl)}" alt="Reviewed cytology image"></div>${camUrl ? `<div><p class="meta">${htmlEscape(res.xai.primaryMethod || "Class activation")} grade heatmap</p><img src="${htmlEscape(camUrl)}" alt="Grade class-activation heatmap"></div>` : ""}${koilCamUrl ? `<div><p class="meta">KOIL-specific Grad-CAM</p><img src="${htmlEscape(koilCamUrl)}" alt="KOIL morphology class-activation heatmap"></div>` : ""}${activationUrl ? `<div><p class="meta">Activation boundary (not segmentation)</p><img src="${htmlEscape(activationUrl)}" alt="Thresholded class-activation regions"></div>` : ""}</div></section>
${patientSection}<div class="sign"><b>Review status:</b> ${htmlEscape(status)} (research demo sign-off)<br><span class="meta">A qualified clinician remains responsible for diagnosis, documentation, and follow-up.</span></div>
</body></html>`;
  }

  function analysisForReport(): Record<string, unknown> {
    return {
      image: res.image,
      mode: res.modelMode || "model",
      top: { key: res.top, prob: res.conf },
      classification: GRADE_CLASS_KEYS.map((key) => ({ key, prob: res.probs[key] || 0 })),
      koilocyte: Boolean(res.koil), koil_assessment: res.koilAssessment,
      koil_xai: { ok: Boolean(res.koilXaiOk), method: res.koilXaiOk ? "gradcam" : undefined, heatmap: res.koilCam },
      uncertainty: { ...res.uncertainty, flag: highUnc }, quality: res.quality || { ok: true, status: "pass" },
      advanced_xai: { ok: res.xai.ok, primary_method: res.xai.primaryMethod }, heatmap: res.cam,
    };
  }

  async function downloadReviewedPdf() {
    setPdfState("busy"); setPdfMessage("");
    try {
      const blob = await createReviewedPdf({
        case_id: caseId,
        analysis: analysisForReport(),
        review: { status, final_label: shownTop, symptoms_acknowledged: symptomsAcknowledged },
        clinical_context: clinicalContext,
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url; anchor.download = `${caseId}-anong-research-prescreen.pdf`; anchor.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 1_000);
      setPdfState("done"); setPdfMessage("Formal research pre-screen PDF generated.");
    } catch (error) {
      setPdfState("error");
      setPdfMessage(`${error instanceof Error ? error.message : "PDF generation failed"} Use Print / Save PDF as the offline fallback.`);
    }
  }

  function downloadReviewedReport() {
    const blob = new Blob([reviewedReportHtml()], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${caseId}-anong-reviewed-report.html`;
    anchor.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1_000);
  }

  function printReviewedReport() {
    const popup = window.open("", "_blank");
    if (!popup) return;
    popup.opener = null;
    popup.document.write(reviewedReportHtml());
    popup.document.close();
    popup.addEventListener("load", () => popup.print(), { once: true });
  }

  if (status === "rejected") {
    return (
      <div className="card p-6 text-center">
        <div className="text-3xl" aria-hidden>🚫</div>
        <div className="mt-2 font-semibold text-scc">Slide rejected for inadequate quality</div>
        <p className="mt-1 text-sm text-mut">Recollect the specimen or capture a higher-quality image before review.</p>
        <button onClick={() => setStatus("pending")} className="mt-4 rounded-full border border-line px-4 py-2 text-sm hover:border-teal">Return</button>
      </div>
    );
  }

  return (
    <div className="card p-5">
      <XaiReviewPanel
        image={res.image}
        cam={res.cam}
        camSource={res.camSource}
        activationMap={res.activationMap}
        activationCoverage={res.activationCoverage}
        activationThreshold={res.activationThreshold}
        xai={res.xai}
      />

      {res.quality && (
        <div className={"mt-3 flex items-start gap-2 rounded-lg border p-3 text-sm " + (poorQuality ? "border-scc/50 bg-paper text-scc" : qualityWarning ? "border-aqua bg-paper text-ink" : "border-nilm/50 bg-paper text-nilm")} role={poorQuality ? "alert" : "status"}>
          {poorQuality || qualityWarning ? <AlertTriangle className="mt-0.5 shrink-0" size={17} aria-hidden /> : <ShieldCheck className="mt-0.5 shrink-0" size={17} aria-hidden />}
          <div>
            <b>{poorQuality ? "Image quality failed" : qualityWarning ? "Image quality warning" : "Image quality passed"}</b>
            {(poorQuality || qualityWarning) && <p className="mt-1 text-xs leading-5 text-mut">{poorQuality ? "Blocking issues" : "Advisory warnings"}: {res.quality?.issues?.join(", ") || "unspecified quality issue"}. {poorQuality ? "Recollect or recapture before releasing a result." : "Interpret with caution and consider recapture if morphology is not reviewable."}</p>}
            <p className="mt-1 font-mono text-[10px] text-mut">Profile: {res.quality.profile || "unspecified"} · score {res.quality.overall_score?.toFixed(3) ?? "-"}</p>
          </div>
        </div>
      )}

      {/* uncertainty / abstain banner (M4) */}
      {highUnc && (
        <div className="mt-3 flex items-start gap-2 rounded-lg p-3 text-sm" role="alert"
          style={{ background: "color-mix(in srgb,var(--scc) 12%,transparent)", border: "1px solid color-mix(in srgb,var(--scc) 40%,transparent)" }}>
          <span aria-hidden>⚠️</span><span style={{ color: "var(--scc)" }}><b>High uncertainty</b> — independent clinician review is required, and the patient report remains locked.</span>
        </div>
      )}

      {demoMode && (
        <div className="mt-3 flex items-start gap-2 rounded-lg border border-scc/50 bg-paper p-3 text-sm text-scc" role="alert">
          <AlertTriangle className="mt-0.5 shrink-0" size={17} aria-hidden />
          <span><b>Heuristic demo mode</b> — the trained checkpoint is not active. Do not use this output as model evidence.</span>
        </div>
      )}

      <div className="mt-3 flex flex-wrap items-start justify-between gap-2">
        <div className="font-display text-3xl font-semibold" style={{ color: I.color }}><span aria-hidden>{I.icon}</span> {shownTop}</div>
        <span className="rounded-full border px-2 py-1 text-[11px]" style={{ borderColor: highUnc ? "var(--scc)" : "var(--line)", color: highUnc ? "var(--scc)" : "var(--teal)" }}>
          Confidence: {confidenceLabel(res.uncertainty.level)}
        </span>
      </div>
      <div className="text-sm text-mut">{I.en} — {I.desc}</div>
      <div className="mt-3 rounded-lg border border-line p-3 text-sm">
        <div className="flex flex-col items-start gap-3 sm:flex-row sm:justify-between">
          <div>
            <div className="font-semibold text-ink">HPV-related morphology risk</div>
            <div className="mt-1 text-xs text-mut">{hpv.detail}</div>
          </div>
          <span className="shrink-0 rounded-full border px-2 py-1 text-[11px]" style={{ borderColor: hpv.tone, color: hpv.tone }}>
            {hpv.level}
          </span>
        </div>
        <div className="mt-2 text-[10px] text-mut">
          This assessment uses cellular morphology in the image only. It does not detect HPV DNA/RNA.
        </div>
        {res.koilAssessment && (
          <div className="mt-3 grid gap-2 border-t border-line pt-3 sm:grid-cols-3">
            <div><div className="text-[10px] uppercase text-mut">KOIL endpoint</div><b className="text-ink">{res.koilAssessment.status}</b></div>
            <div><div className="text-[10px] uppercase text-mut">Probability</div><b className="font-mono text-ink">{(res.koilAssessment.probability * 100).toFixed(1)}%</b></div>
            <div><div className="text-[10px] uppercase text-mut">Locked threshold</div><b className="font-mono text-ink">{res.koilAssessment.threshold != null ? `${(res.koilAssessment.threshold * 100).toFixed(1)}%` : "Unavailable"}</b></div>
            <p className="sm:col-span-3 text-[10px] text-mut">{res.koilAssessment.domain_warning}</p>
            {res.koilAssessment.evidence?.locked_test && <div className="sm:col-span-3 rounded-lg bg-paper p-3 text-[10px] leading-5 text-mut">
              <b className="text-ink">Locked SIPaKMeD test:</b> sensitivity {((res.koilAssessment.evidence.locked_test.sensitivity || 0) * 100).toFixed(1)}%, specificity {((res.koilAssessment.evidence.locked_test.specificity || 0) * 100).toFixed(1)}%, AUROC {(res.koilAssessment.evidence.locked_test.auroc || 0).toFixed(3)}. {res.koilAssessment.evidence.locked_test.support_positive} positive and {res.koilAssessment.evidence.locked_test.support_negative} negative cells.
            </div>}
            {res.koilAssessment.evidence?.external_positive_challenge && <div className="sm:col-span-3 rounded-lg bg-paper p-3 text-[10px] leading-5 text-mut">
              <b className="text-ink">External CCCID challenge:</b> {res.koilAssessment.evidence.external_positive_challenge.true_positive}/{res.koilAssessment.evidence.external_positive_challenge.support_positive} expert-labelled koilocytes detected ({((res.koilAssessment.evidence.external_positive_challenge.sensitivity || 0) * 100).toFixed(1)}%). Positive-only exploratory evidence; specificity is not estimable.
            </div>}
          </div>
        )}
      </div>
      {res.koilCam && (
        <figure className="mt-3 rounded-lg border border-line p-3">
          <img src={res.koilCam} className="mx-auto max-h-80 rounded-lg object-contain" alt="KOIL-specific Grad-CAM heatmap" />
          <figcaption className="mt-2 text-xs text-mut"><b className="text-ink">KOIL-specific Grad-CAM.</b> This map targets the independent koilocytotic-morphology output. It is attention evidence, not cell segmentation and not proof of HPV infection.</figcaption>
        </figure>
      )}
      {res.trueLabel && (
        <div className="mt-1 text-xs text-mut">True label: <b style={{ color: classInfo(res.trueLabel).color }}>{classInfo(res.trueLabel).icon} {res.trueLabel}</b>
          {res.correct ? <span style={{ color: "var(--nilm)" }}> · Correct prediction</span> : <span style={{ color: "var(--scc)" }}> · Incorrect prediction</span>}</div>
      )}

      <div className="mt-4 space-y-1.5 font-mono text-xs" role="img" aria-label={`Class probabilities; highest prediction ${shownTop}`}>
        {GRADE_CLASS_KEYS.map((k) => {
          const p = Math.round((res.probs[k] || 0) * 100);
          return (
            <div key={k}>
              <div className="flex justify-between"><span>{classInfo(k).icon} {k}</span><span>{p}%</span></div>
              <div className="h-2 rounded-full bg-line"><div className="bar-fill h-2 rounded-full" style={{ width: `${p}%`, background: k === shownTop ? "var(--teal)" : "var(--line)" }} /></div>
            </div>
          );
        })}
      </div>

      {/* sign-off (M1) */}
      <div className="mt-4 rounded-lg border border-line p-3">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-xs text-mut">Review status</span>
          <span className="text-xs font-semibold" style={{ color: statusLabel[status][1] }}>{statusLabel[status][0]}</span>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={() => sign("confirmed", null)} className="rounded-full px-3 py-1.5 text-xs text-white" style={{ background: "var(--nilm)" }}>✔ Confirm</button>
          <select value={override ?? ""} onChange={(e) => sign("edited", e.target.value || null)}
            className="rounded-full border border-line bg-surface px-3 py-1.5 text-xs text-ink" aria-label="Edit Bethesda category">
            <option value="">✏ Edit category…</option>
            {GRADE_CLASS_KEYS.map((k) => <option key={k} value={k}>{k}</option>)}
          </select>
          <button onClick={() => sign("rejected", shownTop)} className="rounded-full border px-3 py-1.5 text-xs" style={{ borderColor: "var(--scc)", color: "var(--scc)" }}>✘ Reject slide</button>
        </div>
        {hasSymptoms && (
          <label className="mt-3 flex items-start gap-2 rounded-lg border border-scc/40 p-3 text-xs leading-5 text-mut">
            <input type="checkbox" checked={symptomsAcknowledged} onChange={(event) => setSymptomsAcknowledged(event.target.checked)} className="mt-1 accent-[var(--teal)]" />
            <span><b className="text-scc">Symptom acknowledgement:</b> I reviewed the reported symptoms and understand that this image result cannot rule out disease or replace symptom-led clinical evaluation.</span>
          </label>
        )}
        {auditSaved && <div className="mt-2 text-[10px] text-mut">{auditSaved} ({caseId})</div>}
      </div>

      {/* structured clinician report (M6) */}
      <div className="mt-4 rounded-lg border border-line p-3 text-sm" id="clinReport">
        <div className="mb-1 flex items-center justify-between font-mono text-xs text-teal"><span>Clinician report</span><span className="text-mut">{caseId}</span></div>
        <div className="text-xs text-mut">Date {new Date().toLocaleString("en-GB")} · Specimen: {clinicalContext.specimen_type} · Age: {clinicalContext.age_years ?? "not entered"}</div>
        <div className="mt-1">Result <b>{shownTop}</b> ({I.en}) · Confidence {(res.conf * 100).toFixed(0)}% · Uncertainty: {res.uncertainty.level}</div>
        <div>Quality: {res.quality ? `${qualityStatus}${res.quality.issues?.length ? ` (${res.quality.issues.join(", ")})` : ""}` : "precomputed"} · XAI: {res.xai.ok ? (res.xai.primaryMethod || "available") : "Unavailable"}</div>
        <div>KOIL morphology: {res.koilAssessment ? `${res.koilAssessment.status} (${(res.koilAssessment.probability * 100).toFixed(1)}%; locked threshold ${res.koilAssessment.threshold != null ? `${(res.koilAssessment.threshold * 100).toFixed(1)}%` : "unavailable"})` : "not assessed"}</div>
        <div>HPV laboratory context: {clinicalContext.hpv_test}{clinicalContext.hpv_genotype ? `; genotype ${clinicalContext.hpv_genotype}` : ""} · separate from image inference</div>
        <div>Recommended action: {I.triage}</div>
        <div>Reported symptoms: {clinicalContext.symptoms.map((key) => SYMPTOM_LABELS[key] || key).concat(clinicalContext.other_symptoms.trim() ? [clinicalContext.other_symptoms.trim()] : []).join("; ") || "none entered"}</div>
        {hasSymptoms && <div className="mt-1 text-scc">Symptoms require separate clinical evaluation regardless of the image result.</div>}
        <div className="mt-2 border-t border-line pt-2 text-xs text-mut">Signatory: {signed ? (status === "edited" ? "✓ Edited and confirmed by clinician (demo)" : "✓ Confirmed by clinician (demo)") : "____________ (signature pending)"}</div>
        <div className="text-[10px] text-mut">AI pre-screen; clinician confirmation is required before release.</div>
        {signed && (
          <div className="mt-3 flex flex-wrap gap-2 print:hidden">
            {API_IS_CONFIGURED && <button onClick={downloadReviewedPdf} disabled={pdfState === "busy"} className="inline-flex items-center gap-1.5 rounded-full bg-teal px-3 py-1.5 text-xs text-white disabled:opacity-50" type="button">
              {pdfState === "busy" ? <LoaderCircle className="animate-spin" size={14} aria-hidden /> : <FileDown size={14} aria-hidden />}
              {pdfState === "busy" ? "Generating PDF..." : "Download formal PDF"}
            </button>}
            <button onClick={downloadReviewedReport} className="rounded-full border border-teal px-3 py-1.5 text-xs text-teal hover:bg-teal hover:text-white" type="button">Download reviewed HTML</button>
            <button onClick={printReviewedReport} className="rounded-full border border-line px-3 py-1.5 text-xs text-mut hover:border-teal hover:text-teal" type="button">Print / Save PDF</button>
          </div>
        )}
        {pdfMessage && <p className={"mt-2 text-xs " + (pdfState === "error" ? "text-scc" : "text-nilm")} role="status">{pdfMessage}</p>}
      </div>

      {/* patient report — gated (M1/M4) */}
      {canPatientReport ? (
        <div className="mt-2 rounded-lg p-3 text-sm" style={{ background: "color-mix(in srgb,var(--teal) 7%,transparent)" }}>
          <div className="font-mono text-xs text-teal">Patient report</div>
          <div className="mt-1">{hasSymptoms ? "The image result was reviewed, but the reported symptoms still require separate clinical evaluation. Do not use this image result for reassurance." : abn ? "The preliminary screening result shows an abnormality that requires follow-up. This does not confirm cancer. Please attend the clinician appointment." : "The reviewed preliminary screening category is NILM. Continue screening according to the applicable program and clinician advice."}</div>
          <button onClick={() => window.print()} className="mt-2 rounded-full border border-line px-3 py-1 text-xs hover:border-teal print:hidden">Print / Save PDF</button>
        </div>
      ) : (
        <div className="mt-2 rounded-lg border border-dashed border-line p-3 text-center text-xs text-mut">
          <b>Patient report locked.</b> Resolve all release gates: {releaseBlockers.join("; ")}.
        </div>
      )}

      {/* disclaimer per result (M3) */}
      <p className="mt-3 text-[10px] text-mut">{res.source}</p>
      <p className="mt-1 text-[10px]" style={{ color: "var(--scc)" }}>⚠️ AI output — not a final diagnosis; clinician confirmation is required.</p>
      <div className="mt-4 rounded-lg border border-line p-3 text-xs">
        <div className="flex items-center justify-between gap-2">
          <b className="text-ink">Recent local demo audit trail</b>
          <button onClick={downloadAudit} className="rounded-full border border-line px-2 py-1 text-[10px] text-mut hover:border-teal">Export JSON</button>
        </div>
        {audit.length ? (
          <ul className="mt-2 space-y-1 text-mut">
            {audit.map((a) => (
              <li key={`${a.caseId}-${a.ts}`} className="truncate">
                {new Date(a.ts).toLocaleString("en-GB")} · {a.caseId} · {a.status} · AI {a.aiTop} → final {a.finalLabel}
              </li>
            ))}
          </ul>
        ) : <div className="mt-2 text-mut">No audit entries yet.</div>}
      </div>
    </div>
  );
}

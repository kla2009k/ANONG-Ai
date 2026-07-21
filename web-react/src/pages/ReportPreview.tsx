import { useEffect, useState } from "react";
import { GRADE_CLASS_KEYS, classInfo } from "@/lib/data";

const BASE = import.meta.env.BASE_URL;

interface ValidatedReport {
  case_id: string;
  file: string;
  grade: string;
  model_grade?: string;
  koil_status: string;
  review_status: string;
  source_image: string;
  sha256: string;
  bytes: number;
}

export default function ReportPreview() {
  const [label, setLabel] = useState("HSIL");
  const [signed, setSigned] = useState(false);
  const [highUnc, setHighUnc] = useState(false);
  const [koilPositive, setKoilPositive] = useState(false);
  const [validatedReports, setValidatedReports] = useState<ValidatedReport[]>([]);
  const info = classInfo(label);
  const patientUnlocked = signed && !highUnc;
  const reportText = [
    "Anong | CerviCo-Pilot clinical pre-screen report",
    `Case: CC-DEMO-260706`,
    `Final label: ${label} (${info.en})`,
    `KOIL morphology: ${koilPositive ? "Positive (independent endpoint)" : "Not prominent / not assessed"}`,
    `Interpretation: ${info.desc}`,
    "HPV note: HPV-related morphology risk only; confirmatory HPV DNA/RNA testing remains separate.",
    `Recommended action: ${info.triage}`,
    `Sign-off: ${signed ? "confirmed by clinician (demo)" : "pending clinician review"}`,
    "Disclaimer: Decision-support output. Not a final diagnosis.",
  ].join("\n");

  useEffect(() => {
    fetch(`${BASE}reports/manifest.json`).then((response) => response.ok ? response.json() : Promise.reject()).then((data) => setValidatedReports(data.reports || [])).catch(() => setValidatedReports([]));
  }, []);

  function downloadHtml() {
    const html = `<!doctype html><html><head><meta charset="utf-8"><title>Anong · CerviCo-Pilot Report</title><style>body{font-family:Arial,sans-serif;max-width:760px;margin:40px auto;line-height:1.55;color:#4a3340;background:#fff8e9}h1{color:#b64e70}.box{border:1px solid #ead4d3;background:#fffdf7;padding:16px;border-radius:8px;margin:12px 0}.muted{color:#735e69;font-size:12px}</style></head><body><h1>Anong · CerviCo-Pilot Clinical Pre-screen</h1><div class="box"><pre>${reportText.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c] || c))}</pre></div><p class="muted">Demo report only. Requires clinician sign-off.</p></body></html>`;
    const blob = new Blob([html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "anong-cervico-pilot-demo-report.html";
    a.click();
    URL.revokeObjectURL(url);
  }

  function copyReport() {
    navigator.clipboard?.writeText(reportText);
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-14">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="kicker mb-2">Report preview</div>
          <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Clinician and patient report preview</h1>
          <p className="mt-2 max-w-3xl text-sm text-mut">
            Demonstrates that AI cannot release a patient result by itself. The patient report unlocks only after clinician sign-off and remains blocked for high uncertainty.
          </p>
        </div>
        <div className="flex flex-wrap gap-2 print:hidden">
          <button onClick={() => window.print()} className="rounded-full border border-line px-4 py-2 text-sm text-mut transition hover:border-teal hover:text-teal" type="button">
            Print / Save PDF
          </button>
          <button onClick={downloadHtml} className="rounded-full border border-line px-4 py-2 text-sm text-mut transition hover:border-teal hover:text-teal" type="button">
            Export HTML
          </button>
          <button onClick={copyReport} className="rounded-full border border-line px-4 py-2 text-sm text-mut transition hover:border-teal hover:text-teal" type="button">
            Copy text
          </button>
        </div>
      </div>

      <div className="mt-6 grid gap-4 rounded-lg border border-line bg-surface p-4 print:hidden md:grid-cols-3">
        <label className="text-sm">
          <span className="mb-1 block text-xs text-mut">Final Bethesda-style label</span>
          <select value={label} onChange={(e) => setLabel(e.target.value)} className="w-full rounded-xl border border-line bg-paper px-3 py-2 text-ink">
            {GRADE_CLASS_KEYS.map((k) => <option key={k} value={k}>{k}</option>)}
          </select>
        </label>
        <label className="flex items-center gap-3 rounded-xl border border-line px-3 py-2 text-sm">
          <input type="checkbox" checked={signed} onChange={(e) => setSigned(e.target.checked)} />
          Clinician signed
        </label>
        <label className="flex items-center gap-3 rounded-xl border border-line px-3 py-2 text-sm">
          <input type="checkbox" checked={highUnc} onChange={(e) => setHighUnc(e.target.checked)} />
          High uncertainty
        </label>
        <label className="flex items-center gap-3 rounded-xl border border-line px-3 py-2 text-sm md:col-span-3">
          <input type="checkbox" checked={koilPositive} onChange={(e) => setKoilPositive(e.target.checked)} />
          Independent KOIL morphology endpoint positive
        </label>
      </div>

      <div className="mt-8 grid gap-5 lg:grid-cols-2">
        <section className="card p-6">
          <div className="flex items-start justify-between gap-4 border-b border-line pb-4">
            <div>
              <div className="font-mono text-xs uppercase tracking-[.2em] text-teal">Clinician report</div>
              <h2 className="mt-1 font-display text-2xl font-semibold text-ink">Anong · Cervical Cytology AI Pre-screen</h2>
            </div>
            <span className="rounded-full border border-line px-3 py-1 text-xs text-mut">CC-DEMO-260706</span>
          </div>
          <dl className="mt-5 grid gap-3 text-sm">
            <div className="grid grid-cols-[140px_1fr] gap-3">
              <dt className="text-mut">Specimen</dt>
              <dd className="text-ink">Pap / ThinPrep-style cytology image</dd>
            </div>
            <div className="grid grid-cols-[140px_1fr] gap-3">
              <dt className="text-mut">AI suggestion</dt>
              <dd className="font-semibold" style={{ color: info.color }}>{info.icon} {label} · {info.en}</dd>
            </div>
            <div className="grid grid-cols-[140px_1fr] gap-3">
              <dt className="text-mut">Interpretation</dt>
              <dd>{info.desc}</dd>
            </div>
            <div className="grid grid-cols-[140px_1fr] gap-3">
              <dt className="text-mut">HPV note</dt>
              <dd>HPV-related morphology risk only; confirmatory HPV DNA/RNA testing remains separate.</dd>
            </div>
            <div className="grid grid-cols-[140px_1fr] gap-3">
              <dt className="text-mut">KOIL morphology</dt>
              <dd>{koilPositive ? "Positive independent morphology endpoint" : "Not prominent / not assessed"}</dd>
            </div>
            <div className="grid grid-cols-[140px_1fr] gap-3">
              <dt className="text-mut">Recommended action</dt>
              <dd>{info.triage}</dd>
            </div>
          </dl>
          <div className="mt-6 rounded-xl border border-dashed border-line p-4 text-sm">
            Sign-off: {signed ? <b className="text-nilm">confirmed by clinician (demo)</b> : <b className="text-scc">pending clinician review</b>}
          </div>
          <p className="mt-4 text-xs text-mut">Decision-support output. Not a final diagnosis.</p>
        </section>

        <section className={"card p-6 " + (!patientUnlocked ? "opacity-80" : "")}>
          <div className="border-b border-line pb-4">
            <div className="font-mono text-xs uppercase tracking-[.2em] text-teal">Patient report</div>
            <h2 className="mt-1 font-display text-2xl font-semibold text-ink">Plain-language screening result</h2>
          </div>
          {patientUnlocked ? (
            <div className="mt-5 text-sm leading-7">
              <p>
                The preliminary screening category is <b style={{ color: info.color }}>{label}</b>. This does not confirm cancer or HPV infection. Follow the clinician's recommended next step.
              </p>
              <p className="mt-3 rounded-xl bg-paper p-4">
                Next step: {info.triage}
              </p>
              <p className="mt-3 text-xs text-mut">
                Contact the screening service or responsible hospital if you have questions about this reviewed result.
              </p>
            </div>
          ) : (
            <div className="mt-5 rounded-2xl border border-dashed border-line p-8 text-center">
              <div className="text-4xl" aria-hidden>🔒</div>
              <h3 className="mt-3 font-display text-xl font-semibold text-ink">Patient report locked</h3>
              <p className="mt-2 text-sm text-mut">
                Clinician sign-off is required, and the case must not be high uncertainty before release.
              </p>
            </div>
          )}
        </section>
      </div>

      <section className="mt-8 rounded-2xl border border-line bg-surface p-5">
        <div className="font-mono text-xs uppercase tracking-[.18em] text-teal">Export-ready text</div>
        <pre className="mt-3 overflow-x-auto whitespace-pre-wrap rounded-xl bg-paper p-4 font-mono text-xs leading-6 text-ink">{reportText}</pre>
      </section>

      <section className="mt-8" aria-labelledby="validated-report-title">
        <div className="kicker mb-2">Generated by the local model pipeline</div>
        <h2 id="validated-report-title" className="font-display text-2xl font-semibold text-ink">Validated demonstration PDFs</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-mut">These reports are frozen research-demo artifacts generated from real model runs. They contain no patient identifiers and are provided so the static site can demonstrate the complete report format without pretending to analyze a new upload.</p>
        {validatedReports.length ? <div className="mt-5 overflow-x-auto rounded-lg border border-line bg-surface"><table className="w-full min-w-[760px] text-left text-sm"><thead className="bg-[var(--blush-soft)]"><tr><th className="p-4">Case</th><th className="p-4">Model → reviewed</th><th className="p-4">KOIL</th><th className="p-4">Review</th><th className="p-4">Artifact</th></tr></thead><tbody className="divide-y divide-line">{validatedReports.map((report) => <tr key={report.case_id}><td className="p-4 font-mono text-xs text-ink">{report.case_id}</td><td className="p-4 font-semibold text-ink">{report.model_grade || report.grade}{report.model_grade && report.model_grade !== report.grade ? ` → ${report.grade}` : ""}</td><td className="p-4 text-mut">{report.koil_status}</td><td className="p-4 text-mut">{report.review_status}</td><td className="p-4"><a href={`${BASE}${report.file}`} className="font-semibold text-teal underline" download>Download PDF</a><div className="mt-1 font-mono text-[9px] text-mut">SHA-256 {report.sha256.slice(0, 12)}… · {Math.round(report.bytes / 1024)} KB</div></td></tr>)}</tbody></table></div> : <div className="mt-5 rounded-lg border border-dashed border-line p-5 text-sm text-mut">Validated PDF artifacts have not been published in this build. Print / Save PDF remains available above.</div>}
      </section>
    </div>
  );
}

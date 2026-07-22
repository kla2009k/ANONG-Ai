import { ChevronDown } from "lucide-react";
import type { ReactNode } from "react";
import { Link } from "wouter";
import { Reveal } from "@/components/Reveal";
import { METRICS, classInfo } from "@/lib/data";

const BASE = import.meta.env.BASE_URL;
const GRADES = ["NILM", "LSIL", "HSIL", "SCC"] as const;

const CRIC_FIGURES = [
  { file: "evidence/cric-latest/cric_oof_confusion.png", title: "Out-of-fold confusion matrix", detail: "All 10,003 cells; parent microscope images remain disjoint between folds." },
  { file: "evidence/cric-latest/cric_class_metrics.png", title: "Precision, recall, and F1", detail: "Exact-grade performance for every class, including the weak SCC subtype endpoint." },
  { file: "evidence/cric-latest/cric_fold_accuracy.png", title: "Accuracy across five folds", detail: "Every fold is retained so source-image variability remains visible." },
  { file: "evidence/cric-latest/cric_selective_tradeoff.png", title: "Accuracy versus coverage", detail: "Higher confidence thresholds improve accepted-case accuracy by sending more cells to review." },
  { file: "evidence/cric-latest/cric_recall_by_endpoint.png", title: "Recall by endpoint", detail: "SCC exact grading and SCC high-grade capture are shown separately; KOIL uses another dataset." },
] as const;

function MetricCard({ label, value, detail, accent = "var(--ink)" }: { label: string; value: string; detail: string; accent?: string }) {
  return <div className="card min-w-0 p-5"><div className="text-xs font-medium text-mut">{label}</div><div className="mt-2 font-mono text-3xl font-semibold" style={{ color: accent }}>{value}</div><p className="mt-2 text-xs leading-5 text-mut">{detail}</p></div>;
}

function RecallRow({ label, value, detail, color }: { label: string; value: number; detail: string; color: string }) {
  return <div className="grid gap-2 sm:grid-cols-[10rem_1fr_4rem] sm:items-center"><div><div className="text-sm font-semibold text-ink">{label}</div><div className="text-[11px] leading-4 text-mut">{detail}</div></div><div className="h-2 overflow-hidden rounded-full bg-line"><div className="h-full rounded-full" style={{ width: `${value * 100}%`, background: color }} /></div><div className="font-mono text-sm font-semibold sm:text-right" style={{ color }}>{(value * 100).toFixed(1)}%</div></div>;
}

function EvidenceFigure({ file, title, detail, wide = false }: { file: string; title: string; detail: string; wide?: boolean }) {
  return <figure className={`card overflow-hidden ${wide ? "md:col-span-2" : ""}`}><a href={`${BASE}${file}`} target="_blank" rel="noreferrer" className="block bg-[var(--paper)] p-2"><img src={`${BASE}${file}`} alt={title} loading="lazy" className="aspect-[16/10] w-full object-contain" /></a><figcaption className="border-t border-line p-4"><h3 className="font-display text-base font-semibold text-ink">{title}</h3><p className="mt-1 text-xs leading-5 text-mut">{detail}</p></figcaption></figure>;
}

function Disclosure({ title, summary, children }: { title: string; summary: string; children: ReactNode }) {
  return <details className="group rounded-lg border border-line bg-surface"><summary className="flex cursor-pointer list-none items-center justify-between gap-4 p-5"><span><span className="block font-display text-lg font-semibold text-ink">{title}</span><span className="mt-1 block text-xs leading-5 text-mut">{summary}</span></span><ChevronDown className="shrink-0 text-teal transition group-open:rotate-180" size={19} aria-hidden /></summary><div className="border-t border-line p-5">{children}</div></details>;
}

function KoilConfusion() {
  const k = METRICS.koil.confusion;
  const cells = [["TN", k.TN, "var(--nilm)"], ["FP", k.FP, "var(--hsil)"], ["FN", k.FN, "var(--scc)"], ["TP", k.TP, "var(--koil)"]] as const;
  return <div className="grid grid-cols-2 gap-2">{cells.map(([label, value, color]) => <div key={label} className="rounded-lg border border-line p-3 text-center"><div className="font-mono text-xl font-semibold" style={{ color }}>{value}</div><div className="text-[10px] text-mut">{label}</div></div>)}</div>;
}

export default function Performance() {
  const cg = METRICS.cricGrade;
  const koil = METRICS.koil;
  return <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 sm:py-14">
    <div className="kicker mb-2">Performance · latest evidence</div>
    <div className="flex flex-wrap items-start justify-between gap-4">
      <div className="max-w-3xl"><h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Model performance, without the clutter</h1><p className="mt-3 text-sm leading-6 text-mut">Start with the screening results below. Exact class metrics and all research charts remain available when you need to inspect them.</p></div>
      <span className="rounded-full border border-hsil px-3 py-1 text-xs font-semibold text-hsil">CRIC research model · not deployed</span>
    </div>

    <Reveal as="section" className="mt-8" aria-labelledby="headline-results">
      <h2 id="headline-results" className="font-display text-2xl font-semibold text-ink">Key results</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Accepted-case accuracy" value="91.7%" detail="At 94.1% coverage; 592 uncertain cells go to human review." accent="var(--teal)" />
        <MetricCard label="All-cell accuracy" value="88.8%" detail="All 10,003 OOF cells, including uncertain predictions." />
        <MetricCard label="High-grade capture" value="90.6%" detail="1,688 of 1,864 HSIL-or-SCC cells stayed in the high-grade group." accent="var(--navy)" />
        <MetricCard label="SCC high-grade capture" value="96.3%" detail="155 of 161 SCC cells were classified as HSIL or SCC." accent="var(--scc)" />
      </div>
      <p className="mt-3 text-xs leading-5 text-mut">The latest CRIC research model achieved 91.7% selective four-grade accuracy at 94.1% coverage, not accuracy on every cell. Full-cohort accuracy was 88.8%.</p>
    </Reveal>

    <Reveal as="section" className="mt-9" aria-labelledby="scc-explained">
      <div className="kicker mb-2">SCC explained</div>
      <h2 id="scc-explained" className="font-display text-2xl font-semibold text-ink">Screening capture is strong; exact subtyping is not</h2>
      <p className="mt-2 max-w-3xl text-sm leading-6 text-mut">These two numbers answer different questions and should always be presented together.</p>
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="card border-scc/40 p-6"><div className="text-xs font-semibold uppercase tracking-wider text-scc">Exact SCC label</div><div className="mt-2 font-mono text-3xl font-semibold text-scc">50.3%</div><p className="mt-3 text-sm leading-6 text-mut">81 of 161 SCC cells received the exact SCC label. Another 74 were called HSIL, so the model is not reliable for final HSIL-versus-SCC subtyping.</p></div>
        <div className="card border-teal/40 p-6"><div className="text-xs font-semibold uppercase tracking-wider text-teal">Captured as high-grade</div><div className="mt-2 font-mono text-3xl font-semibold text-teal">96.3%</div><p className="mt-3 text-sm leading-6 text-mut">155 of 161 SCC cells were still placed in HSIL or SCC. This supports a high-grade review queue, but it does not make the system autonomous.</p></div>
      </div>
      <div className="mt-4 rounded-lg border border-line bg-[var(--blush-soft)] p-4 text-sm leading-6 text-mut"><b className="text-ink">What must improve next:</b> add more independent SCC parent images, use a validation-selected cost-sensitive objective, and evaluate on an external ThinPrep cohort. A display change cannot repair the exact SCC endpoint.</div>
    </Reveal>

    <Reveal as="section" className="mt-9" aria-labelledby="screening-recall">
      <div className="flex flex-wrap items-end justify-between gap-3"><div><div className="kicker mb-2">Screening view</div><h2 id="screening-recall" className="font-display text-2xl font-semibold text-ink">Recall at a glance</h2></div><Link href="/gallery" className="rounded-full border border-teal px-4 py-2 text-sm font-semibold text-teal">Inspect model heatmaps</Link></div>
      <div className="card mt-5 space-y-5 p-5 sm:p-6">
        <RecallRow label="NILM exact" value={cg.classMetrics.NILM.recall} detail="Normal morphology" color="var(--nilm)" />
        <RecallRow label="LSIL exact" value={cg.classMetrics.LSIL.recall} detail="Low-grade morphology" color="var(--lsil)" />
        <RecallRow label="HSIL exact" value={cg.classMetrics.HSIL.recall} detail="High-grade morphology" color="var(--hsil)" />
        <RecallRow label="SCC → high-grade" value={Number(cg.sccHighGradeCapture)} detail="SCC classified as HSIL or SCC" color="var(--scc)" />
      </div>
    </Reveal>

    <Reveal as="section" className="mt-8 space-y-3" aria-label="Technical evidence">
      <Disclosure title="Exact class metrics" summary="Support, precision, recall, and F1 for NILM, LSIL, HSIL, and SCC.">
        <div className="hidden overflow-x-auto rounded-lg border border-line sm:block"><table className="w-full min-w-[620px] text-left text-sm"><thead className="bg-[var(--blush-soft)]"><tr><th className="p-4">Grade</th><th className="p-4">Support</th><th className="p-4">Precision</th><th className="p-4">Recall</th><th className="p-4">F1</th></tr></thead><tbody className="divide-y divide-line">{GRADES.map((grade) => { const metric = cg.classMetrics[grade]; const info = classInfo(grade); return <tr key={grade}><th className="p-4" style={{ color: info.color }}>{info.icon} {grade}</th><td className="p-4 font-mono">{metric.support.toLocaleString()}</td><td className="p-4 font-mono">{(metric.precision * 100).toFixed(1)}%</td><td className="p-4 font-mono">{(metric.recall * 100).toFixed(1)}%</td><td className="p-4 font-mono">{(metric.f1 * 100).toFixed(1)}%</td></tr>; })}</tbody></table></div>
        <div className="grid grid-cols-2 gap-3 sm:hidden">{GRADES.map((grade) => { const metric = cg.classMetrics[grade]; const info = classInfo(grade); return <article key={grade} className="rounded-lg border border-line p-4"><h3 className="font-semibold" style={{ color: info.color }}>{info.icon} {grade}</h3><div className="mt-3 font-mono text-xs leading-6 text-mut"><div>n {metric.support.toLocaleString()}</div><div>P {(metric.precision * 100).toFixed(1)}%</div><div>R {(metric.recall * 100).toFixed(1)}%</div><div>F1 {(metric.f1 * 100).toFixed(1)}%</div></div></article>; })}</div>
        <p className="mt-4 text-xs leading-5 text-mut">SCC recall is 50.3% for the exact label. Support is only 161 cells from 21 parent images, so the estimate remains unstable.</p>
      </Disclosure>
      <Disclosure title="All five research charts" summary="Every grade graph uses the latest parent-image-disjoint OOF model.">
        <div className="grid gap-5 md:grid-cols-2">{CRIC_FIGURES.map((figure, index) => <EvidenceFigure key={figure.file} {...figure} wide={index === CRIC_FIGURES.length - 1} />)}</div>
      </Disclosure>
      <Disclosure title="How the two model endpoints differ" summary="CRIC grades cells; SIPaKMeD estimates koilocytic morphology.">
        <div className="grid gap-4 md:grid-cols-2"><div className="rounded-lg border border-line p-5"><div className="font-semibold text-ink">CRIC four-grade candidate</div><p className="mt-2 text-sm leading-6 text-mut">NILM / LSIL / HSIL / SCC · 10,003 cells · 395 parent images · five-fold OOF. Research only; the live upload still uses the historical Herlev checkpoint.</p></div><div className="rounded-lg border border-line p-5"><div className="font-semibold text-ink">SIPaKMeD KOIL model</div><p className="mt-2 text-sm leading-6 text-mut">Koilocytic morphology positive / negative · locked test n=641. Independent morphology endpoint, not a fifth grade and not an HPV molecular test.</p></div></div>
      </Disclosure>
    </Reveal>

    <Reveal as="section" className="mt-9" aria-labelledby="koil-results">
      <div className="kicker mb-2">Independent KOIL morphology</div><h2 id="koil-results" className="font-display text-2xl font-semibold text-ink">A separate model for a separate question</h2><p className="mt-2 max-w-3xl text-sm leading-6 text-mut">KOIL estimates morphology associated with HPV effects. It cannot confirm HPV DNA/RNA, genotype, persistence, or infection status.</p>
      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><MetricCard label="Sensitivity" value="96.2%" detail={`95% CI ${koil.sensitivityCi}`} accent="var(--teal)" /><MetricCard label="Specificity" value="97.6%" detail={`95% CI ${koil.specificityCi}`} accent="var(--navy)" /><MetricCard label="AUROC" value={String(koil.auroc)} detail={`AUPRC ${koil.auprc}`} /><MetricCard label="External positives" value={koil.externalDetected} detail="CCCID positive-only challenge" accent="var(--koil)" /></div>
      <div className="mt-4"><Disclosure title="KOIL locked-test details" summary={`Confusion matrix at threshold ${koil.threshold}.`}><div className="mx-auto max-w-md"><KoilConfusion /></div></Disclosure></div>
    </Reveal>

    <div className="butter-panel mt-9 rounded-lg border p-5 text-xs leading-5 text-mut"><b className="text-ink">Evidence boundary:</b> CRIC is conventional Pap-smear cell evidence, not Thai ThinPrep clinical validation. Grad-CAM is post-hoc attention evidence, not segmentation or causal proof. All outputs require qualified human review.</div>
  </div>;
}

import { ChevronDown } from "lucide-react";
import type { ReactNode } from "react";
import { Link } from "wouter";
import { Reveal } from "@/components/Reveal";
import { METRICS } from "@/lib/data";

const BASE = import.meta.env.BASE_URL;

const CRIC_FIGURES = [
  { file: "evidence/cric-latest/cric_oof_confusion.png", title: "Out-of-fold confusion matrix", detail: "All 10,003 cells; parent microscope images remain disjoint between folds." },
  { file: "evidence/cric-latest/cric_class_metrics.png", title: "Precision, recall, and F1", detail: "Exact-grade performance for every class, including the weak SCC subtype endpoint." },
  { file: "evidence/cric-latest/cric_fold_accuracy.png", title: "Accuracy across five folds", detail: "Every fold is retained so source-image variability remains visible." },
  { file: "evidence/cric-latest/cric_selective_tradeoff.png", title: "Accuracy versus coverage", detail: "Higher confidence thresholds improve accepted-case accuracy by sending more cells to review." },
] as const;

function MetricCard({ label, value, detail, accent = "var(--ink)" }: { label: string; value: string; detail: string; accent?: string }) {
  return <div className="card min-w-0 p-5"><div className="text-xs font-medium text-mut">{label}</div><div className="mt-2 font-mono text-3xl font-semibold" style={{ color: accent }}>{value}</div><p className="mt-2 text-xs leading-5 text-mut">{detail}</p></div>;
}

function RecallRow({ label, value, detail, color }: { label: string; value: number; detail: string; color: string }) {
  return <div className="grid gap-2 sm:grid-cols-[10rem_1fr_4rem] sm:items-center"><div><div className="text-sm font-semibold text-ink">{label}</div><div className="text-[11px] leading-4 text-mut">{detail}</div></div><div className="h-2 overflow-hidden rounded-full bg-line"><div className="h-full rounded-full" style={{ width: `${value * 100}%`, background: color }} /></div><div className="font-mono text-sm font-semibold sm:text-right" style={{ color }}>{(value * 100).toFixed(1)}%</div></div>;
}

function EvidenceFigure({ file, title, detail }: { file: string; title: string; detail: string }) {
  return <figure className="card overflow-hidden"><a href={`${BASE}${file}`} target="_blank" rel="noreferrer" className="block bg-[var(--paper)] p-2"><img src={`${BASE}${file}`} alt={title} loading="lazy" className="aspect-[16/10] w-full object-contain" /></a><figcaption className="border-t border-line p-4"><h3 className="font-display text-base font-semibold text-ink">{title}</h3><p className="mt-1 text-xs leading-5 text-mut">{detail}</p></figcaption></figure>;
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
      <div className="max-w-3xl"><h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Model performance, without the clutter</h1><p className="mt-3 text-sm leading-6 text-mut">Start with the measured screening results, then inspect the four presentation charts and independent KOIL endpoint.</p></div>
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
      <div className="mt-5 grid gap-4 md:grid-cols-[1.45fr_1fr]">
        <div className="rounded-lg border border-teal/40 bg-surface p-5">
          <div className="text-xs font-semibold uppercase tracking-wider text-teal">Presentation summary · measured results</div>
          <p className="mt-3 text-sm leading-6 text-ink">ANONG AI achieved <b>91.7% selective accuracy at 94.1% coverage</b>, with <b>90.6% high-grade capture</b> and <b>96.3% SCC-to-high-grade capture</b>. The independent KOIL model achieved <b>96.2% sensitivity</b>, <b>97.6% specificity</b>, and <b>0.991 AUROC</b>.</p>
          <p className="mt-2 text-xs leading-5 text-mut">These endpoints describe different evaluated tasks and are not combined into one accuracy claim.</p>
        </div>
        <div className="rounded-lg border border-line bg-[var(--blush-soft)] p-5">
          <div className="text-xs font-semibold uppercase tracking-wider text-hsil">Next validation target · not achieved</div>
          <div className="mt-3 font-mono text-2xl font-semibold text-ink">≥90% recall</div>
          <p className="mt-2 text-xs leading-5 text-mut">Target for every exact grade after LBC/ThinPrep adaptation, expert review, and external validation.</p>
        </div>
      </div>
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

    <Reveal as="section" className="mt-9" aria-labelledby="research-charts">
      <div className="kicker mb-2">Research charts</div>
      <h2 id="research-charts" className="font-display text-2xl font-semibold text-ink">Latest model evidence</h2>
      <p className="mt-2 max-w-3xl text-sm leading-6 text-mut">Four presentation charts are shown here and use the latest parent-image-disjoint CRIC OOF predictions. Select a chart to open its full-resolution image.</p>
      <div className="mt-5 grid gap-5 md:grid-cols-2">{CRIC_FIGURES.map((figure) => <EvidenceFigure key={figure.file} {...figure} />)}</div>
    </Reveal>

    <div className="butter-panel mt-8 flex flex-wrap items-center justify-between gap-3 rounded-lg border p-4 text-xs leading-5 text-mut"><span><b className="text-ink">Research scope:</b> Headline results are endpoint-specific and do not imply equal accuracy for every cytology grade.</span><Link href="/model" className="font-semibold text-teal underline">Read the full Model Card</Link></div>

    <Reveal as="section" className="mt-9" aria-labelledby="koil-results">
      <div className="kicker mb-2">Independent KOIL morphology</div><h2 id="koil-results" className="font-display text-2xl font-semibold text-ink">A separate model for a separate question</h2><p className="mt-2 max-w-3xl text-sm leading-6 text-mut">KOIL estimates morphology associated with HPV effects. It cannot confirm HPV DNA/RNA, genotype, persistence, or infection status.</p>
      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><MetricCard label="Sensitivity" value="96.2%" detail={`95% CI ${koil.sensitivityCi}`} accent="var(--teal)" /><MetricCard label="Specificity" value="97.6%" detail={`95% CI ${koil.specificityCi}`} accent="var(--navy)" /><MetricCard label="AUROC" value={String(koil.auroc)} detail={`AUPRC ${koil.auprc}`} /><MetricCard label="External positives" value={koil.externalDetected} detail="CCCID positive-only challenge" accent="var(--koil)" /></div>
      <div className="mt-4"><Disclosure title="KOIL locked-test details" summary={`Confusion matrix at threshold ${koil.threshold}.`}><div className="mx-auto max-w-md"><KoilConfusion /></div></Disclosure></div>
    </Reveal>

    <div className="butter-panel mt-9 rounded-lg border p-5 text-xs leading-5 text-mut"><b className="text-ink">Evidence boundary:</b> CRIC provides conventional Pap-smear research evidence; KOIL is an independent morphology endpoint, not an HPV molecular test. Grad-CAM is post-hoc attention evidence, not segmentation or causal proof. All outputs require qualified human review.</div>
  </div>;
}

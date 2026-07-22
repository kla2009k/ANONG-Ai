import { Reveal } from "@/components/Reveal";
import { METRICS, classInfo } from "@/lib/data";
import { Link } from "wouter";

const BASE = import.meta.env.BASE_URL;
const GRADES = ["NILM", "LSIL", "HSIL", "SCC"] as const;

const CRIC_FIGURES = [
  { file: "evidence/cric-latest/cric_oof_confusion.png", title: "Pooled out-of-fold confusion matrix", detail: "All 10,003 CRIC cells. Each prediction comes from the fold where its parent microscope image was held out." },
  { file: "evidence/cric-latest/cric_class_metrics.png", title: "Precision, recall, and F1 by grade", detail: "The aggregate score is not allowed to hide the weak SCC endpoint." },
  { file: "evidence/cric-latest/cric_fold_accuracy.png", title: "Accuracy across all five folds", detail: "Every fold is retained; the lower fourth fold exposes source-image variability." },
  { file: "evidence/cric-latest/cric_selective_tradeoff.png", title: "Selective accuracy versus coverage", detail: "Threshold 0.60 produces 91.7% accuracy at 94.1% coverage; the remaining 5.9% are sent for human review." },
  { file: "evidence/cric-latest/cric_recall_by_endpoint.png", title: "Recall by endpoint", detail: "CRIC grade recalls and SIPaKMeD KOIL sensitivity share a visual scale, but not a dataset or label ontology." },
] as const;

const MODEL_ENDPOINTS = [
  {
    endpoint: "CRIC four-grade candidate",
    output: "NILM / LSIL / HSIL / SCC",
    evaluation: "10,003 cells · 395 parents · five-fold OOF",
    result: <>91.7% selective at 94.1% coverage<br />88.8% full cohort</>,
    status: "Research · not deployed",
    statusClass: "text-hsil",
  },
  {
    endpoint: "SIPaKMeD KOIL model",
    output: "Koilocytic morphology positive / negative",
    evaluation: "Locked test n=641 · source-cluster-disjoint",
    result: <>Sensitivity 96.2% · AUROC 0.991</>,
    status: "Independent endpoint",
    statusClass: "text-teal",
  },
] as const;

function Stat({ label, value, sub, color }: { label: string; value: string; sub?: string; color?: string }) {
  return <div className="card min-w-0 p-5"><div className="text-xs text-mut">{label}</div><div className="mt-1 break-words font-mono text-2xl font-semibold sm:text-3xl" style={{ color: color || "var(--ink)" }}>{value}</div>{sub && <div className="mt-1 text-xs leading-5 text-mut">{sub}</div>}</div>;
}

function EvidenceFigure({ file, title, detail, wide = false }: { file: string; title: string; detail: string; wide?: boolean }) {
  return <figure className={`card overflow-hidden ${wide ? "md:col-span-2" : ""}`}><a href={`${BASE}${file}`} target="_blank" rel="noreferrer" className="block bg-[var(--paper)] p-2"><img src={`${BASE}${file}`} alt={title} loading="lazy" className="aspect-[16/10] w-full object-contain" /></a><figcaption className="border-t border-line p-4"><h3 className="font-display text-base font-semibold text-ink">{title}</h3><p className="mt-1 text-xs leading-5 text-mut">{detail}</p></figcaption></figure>;
}

function KoilConfusion() {
  const k = METRICS.koil.confusion;
  const cells = [
    ["TN", k.TN, "var(--nilm)"], ["FP", k.FP, "var(--hsil)"],
    ["FN", k.FN, "var(--scc)"], ["TP", k.TP, "var(--koil)"],
  ] as const;
  return <div className="grid grid-cols-2 gap-2">{cells.map(([label, value, color]) => <div key={label} className="rounded-lg border border-line p-4 text-center" style={{ background: `color-mix(in srgb, ${color} 14%, var(--surface))` }}><div className="font-mono text-2xl font-semibold" style={{ color }}>{value}</div><div className="text-[10px] text-mut">{label}</div></div>)}</div>;
}

export default function Performance() {
  const cg = METRICS.cricGrade;
  const k = METRICS.koil;
  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 sm:py-14">
      <div className="kicker mb-2">Performance · latest measured evidence</div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Latest model evaluation</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-mut">The primary grade evidence below is the latest CRIC EfficientNet-B0 candidate, evaluated with five parent-image-disjoint folds. KOIL remains a separate SIPaKMeD morphology endpoint and is not a fifth grade or molecular HPV test.</p>
        </div>
        <span className="rounded-full border border-hsil px-3 py-1 text-xs font-semibold text-hsil">CRIC research model · not deployed</span>
      </div>

      <Reveal as="section" className="mt-8" aria-labelledby="headline-results">
        <h2 id="headline-results" className="font-display text-2xl font-semibold text-ink">Primary four-grade result</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Stat label="Selective accuracy" value="91.7%" sub={`95% CI ${cg.selectiveAccuracyCi}`} color="var(--teal)" />
          <Stat label="Coverage" value="94.1%" sub={`${cg.accepted.toLocaleString()} accepted · ${cg.abstained} human review`} color="var(--navy)" />
          <Stat label="Full-cohort accuracy" value="88.8%" sub={`95% CI ${cg.accuracyCi}`} />
          <Stat label="Macro F1" value="74.1%" sub="Pooled across four grades" color="var(--hsil)" />
        </div>
        <div className="butter-panel mt-4 rounded-lg border p-5 text-sm leading-6 text-mut"><b className="text-ink">Required wording:</b> The latest CRIC research model achieved <b className="text-teal">91.7% selective four-grade accuracy at 94.1% coverage</b>; 5.9% of cells were abstained for human review. Full-cohort accuracy was 88.8%. The selective-accuracy CI is {cg.selectiveAccuracyCi}, so its lower bound remains below 90%.</div>
      </Reveal>

      <Reveal as="section" className="mt-8" aria-labelledby="main-endpoints">
        <div className="kicker mb-3">Main evaluated models</div>
        <h2 id="main-endpoints" className="font-display text-2xl font-semibold text-ink">Two model endpoints, two evidence domains</h2>
        <div className="mt-4 hidden overflow-x-auto rounded-lg border border-line bg-surface sm:block">
          <table className="w-full min-w-[720px] text-left text-sm"><thead className="bg-[var(--blush-soft)]"><tr><th className="p-4">Model endpoint</th><th className="p-4">Output</th><th className="p-4">Evaluation</th><th className="p-4">Measured result</th><th className="p-4">Status</th></tr></thead><tbody className="divide-y divide-line">
            {MODEL_ENDPOINTS.map((model) => <tr key={model.endpoint}><th className="p-4 text-ink">{model.endpoint}</th><td className="p-4 text-mut">{model.output}</td><td className="p-4 text-mut">{model.evaluation}</td><td className="p-4 text-mut">{model.result}</td><td className={`p-4 font-semibold ${model.statusClass}`}>{model.status}</td></tr>)}
          </tbody></table>
        </div>
        <div className="mt-4 grid gap-3 sm:hidden">{MODEL_ENDPOINTS.map((model) => <article key={model.endpoint} className="card p-4"><h3 className="font-semibold text-ink">{model.endpoint}</h3><dl className="mt-3 grid gap-3 text-xs"><div><dt className="font-semibold text-ink">Output</dt><dd className="mt-1 leading-5 text-mut">{model.output}</dd></div><div><dt className="font-semibold text-ink">Evaluation</dt><dd className="mt-1 leading-5 text-mut">{model.evaluation}</dd></div><div><dt className="font-semibold text-ink">Measured result</dt><dd className="mt-1 leading-5 text-mut">{model.result}</dd></div><div><dt className="font-semibold text-ink">Status</dt><dd className={`mt-1 font-semibold ${model.statusClass}`}>{model.status}</dd></div></dl></article>)}</div>
        <p className="mt-3 text-xs leading-5 text-mut">The live upload workflow still uses the historical Herlev grade checkpoint. This page reports the latest research candidate without pretending that deployment has already changed.</p>
      </Reveal>

      <Reveal as="section" className="mt-8" aria-labelledby="latest-figures">
        <div className="kicker mb-3">Latest CRIC figures</div>
        <div className="flex flex-wrap items-end justify-between gap-3"><div><h2 id="latest-figures" className="font-display text-2xl font-semibold text-ink">Every grade graph now uses the latest OOF model</h2><p className="mt-2 max-w-3xl text-sm leading-6 text-mut">No Herlev grade graph or superseded research-v3 chart is mixed into this section.</p></div><Link href="/gallery" className="rounded-full border border-teal px-4 py-2 text-sm font-semibold text-teal">Inspect latest heatmaps</Link></div>
        <div className="mt-5 grid gap-5 md:grid-cols-2">
          {CRIC_FIGURES.map((figure, index) => <EvidenceFigure key={figure.file} {...figure} wide={index === CRIC_FIGURES.length - 1} />)}
        </div>
      </Reveal>

      <Reveal as="section" className="mt-8" aria-labelledby="class-table">
        <div className="kicker mb-3">Class-specific evidence</div>
        <h2 id="class-table" className="font-display text-2xl font-semibold text-ink">Latest CRIC precision, recall, and F1</h2>
        <div className="mt-4 hidden overflow-x-auto rounded-lg border border-line bg-surface sm:block"><table className="w-full min-w-[620px] text-left text-sm"><thead className="bg-[var(--blush-soft)]"><tr><th className="p-4">Grade</th><th className="p-4">Support</th><th className="p-4">Precision</th><th className="p-4">Recall</th><th className="p-4">F1</th></tr></thead><tbody className="divide-y divide-line">{GRADES.map((grade) => { const metric = cg.classMetrics[grade]; const info = classInfo(grade); return <tr key={grade}><th className="p-4" style={{ color: info.color }}>{info.icon} {grade}</th><td className="p-4 font-mono">{metric.support.toLocaleString()}</td><td className="p-4 font-mono">{(metric.precision * 100).toFixed(1)}%</td><td className="p-4 font-mono">{(metric.recall * 100).toFixed(1)}%</td><td className="p-4 font-mono">{(metric.f1 * 100).toFixed(1)}%</td></tr>; })}</tbody></table></div>
        <div className="mt-4 grid grid-cols-2 gap-3 sm:hidden">{GRADES.map((grade) => { const metric = cg.classMetrics[grade]; const info = classInfo(grade); return <article key={grade} className="card min-w-0 p-4"><h3 className="font-semibold" style={{ color: info.color }}>{info.icon} {grade}</h3><div className="mt-3 font-mono text-xs leading-6 text-mut"><div>n {metric.support.toLocaleString()}</div><div>P {(metric.precision * 100).toFixed(1)}%</div><div>R {(metric.recall * 100).toFixed(1)}%</div><div>F1 {(metric.f1 * 100).toFixed(1)}%</div></div></article>; })}</div>
        <div className="mt-4 rounded-lg border border-scc/40 p-4 text-sm leading-6 text-mut"><b className="text-scc">Safety limitation:</b> SCC recall is 50.3% on only 161 cells from 21 parent images. The model cannot support autonomous grading or clinical replacement even though its selective aggregate accuracy exceeds 90%.</div>
      </Reveal>

      <Reveal as="section" className="mt-8" aria-labelledby="koil-results">
        <div className="kicker mb-3">Independent KOIL morphology</div>
        <h2 id="koil-results" className="font-display text-2xl font-semibold text-ink">Separate model, retained because it answers a different question</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-mut">KOIL is trained and tested on SIPaKMeD rather than CRIC. It estimates koilocytic morphology only and cannot confirm HPV DNA/RNA, genotype, persistence, or infection status.</p>
        <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><Stat label="Sensitivity" value="96.2%" sub={`95% CI ${k.sensitivityCi}`} color="var(--teal)" /><Stat label="Specificity" value="97.6%" sub={`95% CI ${k.specificityCi}`} color="var(--navy)" /><Stat label="AUROC / AUPRC" value={`${k.auroc} / ${k.auprc}`} sub={`F1 ${k.f1}`} /><Stat label="External positives" value={k.externalDetected} sub="CCCID positive-only challenge" color="var(--koil)" /></div>
        <div className="mt-5 grid gap-5 md:grid-cols-2"><div className="card p-6"><h3 className="text-sm font-semibold text-ink">KOIL locked-test confusion matrix</h3><p className="mb-4 mt-1 text-xs text-mut">Test n={k.test}; threshold {k.threshold}</p><KoilConfusion /></div><div className="card p-6 text-sm leading-6 text-mut"><h3 className="font-semibold text-ink">Claim boundary</h3><p className="mt-3">The CRIC 91.7% result belongs only to four-grade selective classification. The KOIL 96.2% sensitivity belongs only to the independent morphology endpoint. Neither number measures molecular HPV infection.</p><Link href="/datasets" className="mt-4 inline-block font-semibold text-teal underline">Review dataset provenance</Link></div></div>
      </Reveal>

      <div className="butter-panel mt-8 rounded-lg border p-5 text-xs leading-5 text-mut"><b className="text-ink">Evidence boundary:</b> CRIC is conventional Pap-smear cell evidence, not Thai ThinPrep clinical validation. Grad-CAM is post-hoc attention evidence, not segmentation or causal proof. All outputs require qualified human review.</div>
    </div>
  );
}

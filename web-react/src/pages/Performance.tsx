import { Reveal } from "@/components/Reveal";
import { METRICS, classInfo } from "@/lib/data";
import { useEffect, useState } from "react";

const CK = ["NILM", "LSIL", "HSIL", "SCC"];
const BASE = import.meta.env.BASE_URL;

function Stat({ label, value, sub, color }: { label: string; value: string; sub?: string; color?: string }) {
  return (
    <div className="card min-w-0 overflow-hidden p-5">
      <div className="text-xs text-mut">{label}</div>
      <div className="mt-1 break-words font-mono text-2xl font-semibold sm:text-3xl" style={{ color: color || "var(--ink)" }}>{value}</div>
      {sub && <div className="text-xs text-mut">{sub}</div>}
    </div>
  );
}

/* Cross-endpoint comparison with explicit dataset separation. */
function EndpointRecallChart() {
  const rows = [
    ...METRICS.perClass.map((p) => ({ key: p.k, value: p.recall, color: classInfo(p.k).color, group: "HERLEV GRADE" })),
    { key: "KOIL", value: Number(METRICS.koil.sensitivity), color: "var(--koil)", group: "SIPAKMED MORPHOLOGY" },
  ];
  return (
    <svg viewBox="0 0 390 218" className="w-full" role="img"
      aria-label="Recall comparison: four Herlev grade categories and the separate SIPaKMeD KOIL morphology endpoint">
      <title>Recall by endpoint with separate evaluation datasets</title>
      <text x="0" y="11" fill="var(--mut)" fontFamily="IBM Plex Mono" fontSize="8">HERLEV GRADE · HELD-OUT n=137</text>
      <line x1="0" y1="154" x2="378" y2="154" stroke="var(--line)" strokeDasharray="4 4" />
      <text x="0" y="171" fill="var(--mut)" fontFamily="IBM Plex Mono" fontSize="8">SIPAKMED KOIL · LOCKED TEST n=641</text>
      {rows.map((p, i) => {
        const y = i < 4 ? 22 + i * 31 : 182;
        const w = p.value * 270;
        return (
          <g key={`${p.group}-${p.key}`} fontFamily="IBM Plex Mono" fontSize="10">
            <text x="0" y={y + 13} fill="var(--mut)">{p.key}</text>
            <rect x="60" y={y} width="270" height="16" rx="4" fill="var(--line)" />
            <rect x="60" y={y} width={w} height="16" rx="4" fill={p.color}>
              <animate attributeName="width" from="0" to={w} dur="1s" fill="freeze" />
            </rect>
            <text x="340" y={y + 13} fill="var(--ink)">{p.value.toFixed(3)}</text>
          </g>
        );
      })}
    </svg>
  );
}

function KoilConfusionHeatmap() {
  const k = METRICS.koil.confusion;
  const cells = [
    { x: 0, y: 0, value: k.TN, label: "TN", color: "var(--nilm)" },
    { x: 1, y: 0, value: k.FP, label: "FP", color: "var(--hsil)" },
    { x: 0, y: 1, value: k.FN, label: "FN", color: "var(--scc)" },
    { x: 1, y: 1, value: k.TP, label: "TP", color: "var(--koil)" },
  ];
  return (
    <div>
      <div className="grid grid-cols-[5rem_repeat(2,minmax(0,1fr))] gap-2 text-center text-xs">
        <div />
        <div className="text-mut">Pred. negative</div><div className="text-mut">Pred. KOIL</div>
        <div className="self-center text-right text-mut">True negative</div>
        {cells.slice(0, 2).map((cell) => <MatrixCell key={cell.label} {...cell} />)}
        <div className="self-center text-right text-mut">True KOIL</div>
        {cells.slice(2).map((cell) => <MatrixCell key={cell.label} {...cell} />)}
      </div>
      <div className="mt-4 grid grid-cols-2 gap-2 text-[10px] text-mut sm:grid-cols-4">
        <span>Positive support: {METRICS.koil.positive}</span><span>Negative support: {METRICS.koil.negative}</span><span>Threshold: {METRICS.koil.threshold}</span><span>Test n={METRICS.koil.test}</span>
      </div>
    </div>
  );
}

function MatrixCell({ value, label, color }: { value: number; label: string; color: string }) {
  return <div className="rounded-lg border border-line p-4" style={{ background: `color-mix(in srgb, ${color} 18%, var(--surface))` }}><div className="font-mono text-2xl font-semibold" style={{ color }}>{value}</div><div className="mt-1 text-[10px] text-mut">{label}</div></div>;
}

function EvidenceImage({ src, title, detail }: { src: string; title: string; detail: string }) {
  return <figure className="card overflow-hidden"><div className="bg-white p-2"><img src={`${BASE}${src}`} alt={title} className="h-auto w-full" loading="lazy" /></div><figcaption className="border-t border-line p-4"><h3 className="text-sm font-semibold text-ink">{title}</h3><p className="mt-1 text-xs leading-5 text-mut">{detail}</p></figcaption></figure>;
}

/* ── line chart: per-fold sensitivity + AUROC + QWK + acc ── */
function FoldLineChart() {
  const W = 380, H = 200, pad = 34;
  const xs = (i: number) => pad + (i * (W - pad - 10)) / 4;
  const ys = (v: number) => H - pad - v * (H - pad - 16); // 0..1
  const series: [string, string, (f: any) => number][] = [
    ["Sensitivity", "var(--teal)", (f) => f.sens],
    ["AUROC", "var(--navy)", (f) => f.auroc],
    ["QWK", "var(--koil)", (f) => f.qwk],
    ["Accuracy", "var(--hsil)", (f) => f.acc],
  ];
  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" fontFamily="IBM Plex Mono" fontSize="9" role="img"
        aria-label="Line chart of sensitivity, AUROC, QWK, and accuracy across five cross-validation folds">
        <title>Metric trends across five cross-validation folds</title>
        {[0, 0.25, 0.5, 0.75, 1].map((g) => (
          <g key={g}>
            <line x1={pad} y1={ys(g)} x2={W - 10} y2={ys(g)} stroke="var(--line)" />
            <text x="4" y={ys(g) + 3} fill="var(--mut)">{g.toFixed(2)}</text>
          </g>
        ))}
        {METRICS.foldNum.map((f, i) => (
          <text key={i} x={xs(i)} y={H - 16} fill="var(--mut)" textAnchor="middle">F{f.fold}</text>
        ))}
        {series.map(([, col, fn]) => {
          const d = METRICS.foldNum.map((f, i) => `${i === 0 ? "M" : "L"}${xs(i)},${ys(fn(f))}`).join(" ");
          return (
            <g key={col as string}>
              <path d={d} fill="none" stroke={col} strokeWidth="2" />
              {METRICS.foldNum.map((f, i) => <circle key={i} cx={xs(i)} cy={ys(fn(f))} r="2.6" fill={col} />)}
            </g>
          );
        })}
      </svg>
      <div className="mt-2 flex flex-wrap gap-3 text-xs text-mut">
        {series.map(([name, col]) => (
          <span key={name} className="flex items-center gap-1"><span className="inline-block h-2 w-3 rounded" style={{ background: col }} />{name}</span>
        ))}
      </div>
    </div>
  );
}

/* Historical Herlev checkpoint, restricted to supported grade classes. */
function ConfusionHeatmap() {
  const cm = METRICS.confusion.slice(0, 4).map((row) => row.slice(0, 4));
  const max = Math.max(...cm.flat());
  const cell = 52, ox = 60, oy = 28;
  return (
    <svg viewBox={`0 0 ${ox + cell * 4 + 10} ${oy + cell * 4 + 40}`} className="w-full max-w-md" fontFamily="IBM Plex Mono" fontSize="11" role="img"
      aria-label="Four-by-four held-out confusion matrix for the supported Herlev grade classes.">
      <title>Held-out supported-grade confusion matrix</title>
      {CK.map((c, j) => <text key={"p" + c} x={ox + j * cell + cell / 2} y={oy - 10} fill="var(--mut)" textAnchor="middle">{c}</text>)}
      <text x={ox + cell * 2} y={oy + cell * 4 + 30} fill="var(--mut)" textAnchor="middle" fontSize="10">Predicted →</text>
      {cm.map((row, i) =>
        row.map((v, j) => {
          const corr = i === j;
          const op = max ? v / max : 0;
          const base = corr ? "20,150,110" : "192,73,47";
          return (
            <g key={`${i}-${j}`}>
              <rect x={ox + j * cell} y={oy + i * cell} width={cell - 3} height={cell - 3} rx="5"
                fill={`rgba(${base},${0.12 + op * 0.8})`} stroke="var(--line)" />
              <text x={ox + j * cell + (cell - 3) / 2} y={oy + i * cell + (cell - 3) / 2 + 4} textAnchor="middle"
                fill={op > 0.45 ? "#fff" : "var(--ink)"} fontWeight={corr ? "600" : "400"}>{v}</text>
            </g>
          );
        })
      )}
      {CK.map((c, i) => <text key={"t" + c} x={ox - 8} y={oy + i * cell + cell / 2 + 4} fill="var(--mut)" textAnchor="end">{c}</text>)}
    </svg>
  );
}

function RocChart({ curves }: { curves: any }) {
  const W = 260, H = 220, pad = 28;
  const x = (v: number) => pad + v * (W - pad - 12);
  const y = (v: number) => H - pad - v * (H - pad - 12);
  const pts = (curves?.roc || []).filter((_: any, i: number) => i % 3 === 0 || i === 0 || i === curves.roc.length - 1);
  const d = pts.map((p: any, i: number) => `${i === 0 ? "M" : "L"}${x(p.fpr)},${y(p.tpr)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-sm" role="img"
      aria-label={`ROC curve binary triage AUROC ${curves.roc_auc}`} fontFamily="IBM Plex Mono" fontSize="10">
      <title>ROC curve binary triage</title>
      <line x1={pad} y1={H - pad} x2={W - 12} y2={12} stroke="var(--line)" strokeDasharray="4 4" />
      <path d={d} fill="none" stroke="var(--teal)" strokeWidth="3" />
      <text x={pad} y={H - 8} fill="var(--mut)">0</text>
      <text x={W - 18} y={H - 8} fill="var(--mut)">FPR</text>
      <text x="2" y="18" fill="var(--mut)">TPR</text>
    </svg>
  );
}

function ReliabilityChart({ curves }: { curves: any }) {
  const W = 260, H = 220, pad = 28;
  const x = (v: number) => pad + v * (W - pad - 12);
  const y = (v: number) => H - pad - v * (H - pad - 12);
  const pts = (curves?.reliability || []).filter((b: any) => b.accuracy !== null);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-sm" role="img"
      aria-label={`Reliability plot ECE ${curves.ece_l1_10bin}`} fontFamily="IBM Plex Mono" fontSize="10">
      <title>Reliability plot binary triage</title>
      <line x1={pad} y1={H - pad} x2={W - 12} y2={12} stroke="var(--line)" strokeDasharray="4 4" />
      <polyline points={pts.map((p: any) => `${x(p.confidence)},${y(p.accuracy)}`).join(" ")}
        fill="none" stroke="var(--hsil)" strokeWidth="2.5" />
      {pts.map((p: any) => (
        <circle key={p.bin} cx={x(p.confidence)} cy={y(p.accuracy)} r={Math.max(2, Math.min(7, p.count / 8))}
          fill="var(--hsil)" opacity="0.85" />
      ))}
      <text x={pad} y={H - 8} fill="var(--mut)">0</text>
      <text x={W - 46} y={H - 8} fill="var(--mut)">confidence</text>
      <text x="2" y="18" fill="var(--mut)">accuracy</text>
    </svg>
  );
}

export default function Performance() {
  const t = METRICS.triage, f = METRICS.fiveClass, bc = METRICS.binaryConfusion, k = METRICS.koil;
  const [curves, setCurves] = useState<any | null>(null);
  useEffect(() => {
    fetch(`${BASE}samples/curves.json`).then((r) => r.json()).then(setCurves).catch(() => setCurves(null));
  }, []);
  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 sm:py-14">
      <div className="kicker mb-2">Performance · measured evidence</div>
      <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Evaluation results</h1>
      <p className="mt-3 max-w-3xl break-words text-sm leading-6 text-mut">Two trained endpoints are evaluated here without mixing their test sets: four-class grade and binary safety use Herlev; KOIL morphology uses SIPaKMeD and a limited CCCID liquid-based positive challenge. HPV infection has no model endpoint or paired molecular test set.</p>

      <Reveal as="section" className="mt-8" aria-labelledby="endpoint-map-title">
        <div className="kicker mb-3">Endpoint map</div>
        <h2 id="endpoint-map-title" className="font-display text-2xl font-semibold text-ink">What each table and graph measures</h2>
        <div className="mt-4 overflow-x-auto rounded-lg border border-line bg-surface">
          <table className="w-full min-w-[820px] border-collapse text-left text-sm">
            <thead className="bg-[var(--blush-soft)]"><tr><th className="p-4 text-ink">Endpoint</th><th className="p-4 text-ink">Output</th><th className="p-4 text-ink">Evaluation data</th><th className="p-4 text-ink">Test support</th><th className="p-4 text-ink">Evidence</th></tr></thead>
            <tbody className="divide-y divide-line">
              <tr><th className="p-4 text-ink">Cytology grade</th><td className="p-4 text-mut">NILM / LSIL / HSIL / SCC</td><td className="p-4 text-mut">Herlev held-out + 5-fold CV</td><td className="p-4 font-mono text-ink">137 held-out</td><td className="p-4 text-mut">CV accuracy {f.acc}</td></tr>
              <tr><th className="p-4 text-ink">Safety triage</th><td className="p-4 text-mut">Normal / abnormal</td><td className="p-4 text-mut">Herlev</td><td className="p-4 font-mono text-ink">137 images</td><td className="p-4 text-mut">Sensitivity {t.held.sensitivity}</td></tr>
              <tr><th className="p-4 text-ink">KOIL morphology</th><td className="p-4 text-mut">Negative / positive</td><td className="p-4 text-mut">SIPaKMeD locked test</td><td className="p-4 font-mono text-ink">641 cells</td><td className="p-4 text-mut">Sensitivity {k.sensitivity}; AUROC {k.auroc}</td></tr>
              <tr><th className="p-4 text-ink">KOIL LBC challenge</th><td className="p-4 text-mut">Positive detection only</td><td className="p-4 text-mut">CCCID v2 BD SurePath</td><td className="p-4 font-mono text-ink">20 positives</td><td className="p-4 text-mut">{k.externalDetected}; specificity not estimable</td></tr>
              <tr><th className="p-4 text-ink">HPV infection</th><td className="p-4 text-mut">Molecular positive / negative</td><td className="p-4 text-mut">Paired assay cohort required</td><td className="p-4 font-mono text-scc">0 paired cases</td><td className="p-4 font-semibold text-scc">Not developed</td></tr>
            </tbody>
          </table>
        </div>
      </Reveal>

      <Reveal as="div" className="kicker mt-8 mb-3">Binary screening view</Reveal>
      <div className="grid gap-4 md:grid-cols-3">
        <Stat label="Sensitivity (5-fold)" value={t.cv.sensitivity} sub={`held-out ${t.held.sensitivity}`} color="var(--teal)" />
        <Stat label="AUROC" value={t.cv.auroc} sub={`held-out ${t.held.auroc} (CI ${t.held.ci_auroc})`} color="var(--navy)" />
        <div className="butter-panel rounded-lg border p-5 text-ink">
          <div className="text-xs text-mut">High-risk cases identified (HSIL+SCC)</div>
          <div className="mt-1 font-mono text-3xl font-semibold text-scc">{t.highRisk}</div>
        </div>
      </div>
      <div className="mt-3 grid gap-3 sm:grid-cols-2 md:grid-cols-4">
        <Stat label="AUPRC" value={t.cv.auprc} /><Stat label="Specificity" value={t.cv.specificity} />
        <Stat label="MCC" value={t.cv.mcc} /><Stat label="Balanced Acc" value={t.cv.bacc} />
      </div>

      {/* charts row */}
      <div className="mt-6 grid gap-5 md:grid-cols-2">
        <Reveal className="card p-6">
          <div className="mb-1 text-sm font-semibold text-ink">Recall by endpoint</div>
          <div className="mb-3 text-xs leading-5 text-mut">Displayed on one scale for comparison, with a visible dataset boundary. KOIL is not a fifth grade class.</div>
          <EndpointRecallChart />
        </Reveal>
        <Reveal className="card p-6">
          <div className="mb-1 text-sm font-semibold text-ink">Trends across five folds</div>
          <div className="mb-3 text-xs text-mut">Sensitivity remains high across the five Herlev folds.</div>
          <FoldLineChart />
        </Reveal>
      </div>

      <Reveal as="div" className="kicker mt-8 mb-3">Historical Herlev grade view</Reveal>
      <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3">
        <Stat label="Accuracy" value={f.acc} /><Stat label="QWK (ordinal)" value={f.qwk} /><Stat label="Recall HSIL+SCC" value={f.recall_hs} />
      </div>

      <div className="mt-6 grid gap-5 md:grid-cols-2">
        <Reveal className="card p-6">
          <div className="mb-1 text-sm font-semibold text-ink">Held-out supported-grade confusion matrix</div>
          <div className="mb-3 text-xs text-mut">Diagonal cells are correct predictions; off-diagonal cells show class confusion.</div>
          <ConfusionHeatmap />
        </Reveal>
        <Reveal className="card p-6">
          <div className="mb-1 text-sm font-semibold text-ink">Binary screening confusion matrix</div>
          <div className="mb-4 text-xs text-mut">FN = 0 in this held-out split. This does not guarantee zero misses in clinical use.</div>
          <div className="grid grid-cols-2 gap-2 text-center">
            {([["TP", bc.TP, "var(--nilm)", "abnormal → abnormal"], ["FN", bc.FN, "var(--scc)", "abnormal → normal (miss)"],
               ["FP", bc.FP, "var(--hsil)", "normal → abnormal (overcall)"], ["TN", bc.TN, "var(--nilm)", "normal → normal"]] as const).map(([k, v, c, d]) => (
              <div key={k} className="rounded-xl p-4" style={{ background: `color-mix(in srgb, ${c} 14%, transparent)` }}>
                <div className="font-mono text-2xl font-semibold" style={{ color: c }}>{v}</div>
                <div className="text-[10px] text-mut">{k} · {d}</div>
              </div>
            ))}
          </div>
        </Reveal>
      </div>

      <Reveal as="div" className="kicker mt-8 mb-3">Independent KOIL morphology endpoint</Reveal>
      <p className="mb-4 text-sm text-mut">{k.dataset}: {k.total} cells from {k.clusters} source clusters. The locked test set contains {k.positive} KOIL-positive and {k.negative} negative cells; splits are source-cluster-disjoint.</p>
      <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-4">
        <Stat label="Sensitivity" value={k.sensitivity} sub={`95% CI ${k.sensitivityCi}`} color="var(--teal)" />
        <Stat label="Specificity" value={k.specificity} sub={`95% CI ${k.specificityCi}`} color="var(--navy)" />
        <Stat label="AUROC / AUPRC" value={`${k.auroc} / ${k.auprc}`} sub={`F1 ${k.f1}`} />
        <Stat label="Calibration ECE" value={k.ece} sub={`locked threshold ${k.threshold}`} />
      </div>
      <div className="blush-panel mt-4 rounded-lg border p-5 text-sm text-mut">
        <b className="text-ink">Where the project legitimately exceeds 97%:</b> the SIPaKMeD five-morphology auxiliary task reached <b className="font-mono text-teal">{k.multiclassAccuracy}</b> locked-test accuracy and <b className="font-mono text-teal">{k.multiclassMacroF1}</b> macro F1. This number belongs only to SIPaKMeD morphology classification. It must not be presented as Herlev Bethesda-grade accuracy, Thai ThinPrep performance, clinical diagnostic accuracy, or HPV detection accuracy.
      </div>
      <div className="mt-5 grid gap-5 md:grid-cols-2">
        <Reveal className="card p-6">
          <div className="mb-1 text-sm font-semibold text-ink">KOIL locked-test confusion matrix</div>
          <div className="mb-5 text-xs leading-5 text-mut">Independent binary morphology endpoint on source-cluster-disjoint SIPaKMeD cells.</div>
          <KoilConfusionHeatmap />
        </Reveal>
        <Reveal className="card p-6">
          <div className="mb-1 text-sm font-semibold text-ink">Why this is separate from the grade matrix</div>
          <div className="mt-4 space-y-4 text-sm leading-6 text-mut">
            <p><b className="text-ink">Different ontology:</b> KOIL morphology can coexist with a reviewed grade such as LSIL; it is not a mutually exclusive fifth grade.</p>
            <p><b className="text-ink">Different test set:</b> Herlev supplies grade labels, while SIPaKMeD supplies the trained KOIL morphology endpoint.</p>
            <p><b className="text-ink">Different clinical claim:</b> a positive KOIL score requests morphology review. It does not establish HPV DNA/RNA, genotype, viral load, or persistence.</p>
          </div>
        </Reveal>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-[1fr_1fr_2fr]">
        <Stat label="External CCCID detected" value={k.externalDetected} sub="Expert-labelled KOIL positives" color="var(--koil)" />
        <Stat label="External sensitivity" value={k.externalSensitivity} sub={`Wilson 95% CI ${k.externalSensitivityCi}`} color="var(--koil)" />
        <div className="card p-5 text-sm leading-6 text-mut"><b className="text-ink">Positive-only domain challenge:</b> {k.externalDataset}. The 20 center-focus images were selected before inference and the SIPaKMeD threshold was not changed. Specificity, AUROC, calibration, and clinical accuracy are not estimable from this positive-only subset.</div>
      </div>
      <div className="mt-6 grid gap-5 md:grid-cols-2">
        <EvidenceImage src="evidence/koil_test_performance.png" title="KOIL ROC, precision-recall, and locked threshold" detail="AUROC 0.9912 and AUPRC 0.9810 on the SIPaKMeD locked test. These are morphology metrics, not HPV-infection metrics." />
        <EvidenceImage src="evidence/koil_calibration.png" title="KOIL calibration" detail="Reliability evidence for the locked internal test. External ThinPrep calibration remains required." />
      </div>

      <Reveal as="div" className="kicker mt-8 mb-3">ROC + Calibration (binary triage)</Reveal>
      <div className="grid gap-5 md:grid-cols-2">
        <Reveal className="card p-6">
          <div className="mb-1 text-sm font-semibold text-ink">ROC curve</div>
          <div className="mb-3 text-xs text-mut">Computed from best_cervical.pt on the canonical held-out split with TTA.</div>
          {curves ? <RocChart curves={curves} /> : <div className="text-sm text-mut">curves.json not found. Run `python ml/scripts/gen_curves.py`.</div>}
          {curves && <div className="mt-2 font-mono text-xs text-mut">AUROC {curves.roc_auc.toFixed(3)} · n={curves.n}</div>}
        </Reveal>
        <Reveal className="card p-6">
          <div className="mb-1 text-sm font-semibold text-ink">Reliability / calibration</div>
          <div className="mb-3 text-xs text-mut">This is the raw reliability plot. A separate post-hoc temperature-scaling report exists, but external calibration is still required.</div>
          {curves ? <ReliabilityChart curves={curves} /> : <div className="text-sm text-mut">curves.json not found.</div>}
          {curves && <div className="mt-2 font-mono text-xs text-mut">ECE {curves.ece_l1_10bin.toFixed(3)} · Brier {curves.brier.toFixed(3)}</div>}
        </Reveal>
      </div>

      <div className="butter-panel mt-6 rounded-lg border p-5 text-sm">
        <b className="text-hsil">Required context:</b> held-out results, confidence intervals, and cross-validation are shown instead of a single optimistic score. Sensitivity is high in the current Herlev evidence,
        while specificity is moderate. KOIL is evaluated separately on SIPaKMeD conventional Pap-smear crops and challenged on a small CCCID liquid-based positive subset; it is not a Bethesda grade and not an HPV DNA/RNA test. A full negative-inclusive external validation and external calibration remain required.
      </div>
    </div>
  );
}

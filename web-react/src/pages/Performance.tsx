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

/* ── horizontal bar chart (per-class recall) ── */
function PerClassChart() {
  return (
    <svg viewBox="0 0 360 138" className="w-full" role="img"
      aria-label="Bar chart of held-out recall by supported grade category: NILM 0.72, LSIL 0.61, HSIL 0.87, SCC 0.59">
      <title>Held-out recall by category</title>
      {METRICS.perClass.filter((p) => p.k !== "KOIL").map((p, i) => {
        const y = 12 + i * 32, w = p.recall * 250, col = classInfo(p.k).color;
        return (
          <g key={p.k} fontFamily="IBM Plex Mono" fontSize="11">
            <text x="0" y={y + 13} fill="var(--mut)">{p.k}</text>
            <rect x="56" y={y} width="250" height="16" rx="4" fill="var(--line)" />
            <rect x="56" y={y} width={w} height="16" rx="4" fill={col}>
              <animate attributeName="width" from="0" to={w} dur="1s" fill="freeze" />
            </rect>
            <text x={314} y={y + 13} fill="var(--ink)">{p.recall.toFixed(2)}</text>
          </g>
        );
      })}
    </svg>
  );
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
      <p className="mt-3 max-w-full break-words text-sm text-mut">{METRICS.dataset.name}, {METRICS.dataset.total} images · held-out n={METRICS.dataset.test} + bootstrap 95% CI + 5-fold CV</p>

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
          <div className="mb-1 text-sm font-semibold text-ink">Held-out recall by category</div>
          <div className="mb-3 text-xs text-mut">Proportion of true cases identified; HSIL recall is 0.87.</div>
          <PerClassChart />
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
      <div className="mt-4 grid gap-3 md:grid-cols-[1fr_1fr_2fr]">
        <Stat label="External CCCID detected" value={k.externalDetected} sub="Expert-labelled KOIL positives" color="var(--koil)" />
        <Stat label="External sensitivity" value={k.externalSensitivity} sub={`Wilson 95% CI ${k.externalSensitivityCi}`} color="var(--koil)" />
        <div className="card p-5 text-sm leading-6 text-mut"><b className="text-ink">Positive-only domain challenge:</b> {k.externalDataset}. The 20 center-focus images were selected before inference and the SIPaKMeD threshold was not changed. Specificity, AUROC, calibration, and clinical accuracy are not estimable from this positive-only subset.</div>
      </div>
      <div className="mt-4 grid grid-cols-4 gap-2 text-center">
        {Object.entries(k.confusion).map(([label, value]) => <div key={label} className="card p-3"><div className="font-mono text-xl font-semibold text-ink">{value}</div><div className="text-[10px] text-mut">{label}</div></div>)}
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

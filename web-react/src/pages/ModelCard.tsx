import { MODEL_CARD, VERSION, METRICS } from "@/lib/data";

// M2 — Model Card (SaMD-style transparency): intended use, data, training,
// DO-NOT-USE (prominent), limitations, honest metrics with CI.

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid gap-1 py-3 md:grid-cols-[10rem_1fr] md:gap-4">
      <div className="text-sm font-semibold text-ink">{label}</div>
      <div className="text-sm text-mut">{value}</div>
    </div>
  );
}

export default function ModelCard() {
  const t = METRICS.triage;
  const f = METRICS.fiveClass;
  const cg = METRICS.cricGrade;
  return (
    <div className="mx-auto max-w-4xl px-6 py-14">
      <div className="kicker mb-2">Model Card</div>
      <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">{MODEL_CARD.name}</h1>
      <p className="mt-3 text-sm text-mut">
        A transparent summary of the model's intended use, evidence, limitations, and safety boundaries,
        structured in the spirit of Software as a Medical Device documentation.
      </p>

      {/* version */}
      <div className="mt-5 flex flex-wrap gap-2 text-xs">
        <span className="rounded-full border border-line px-3 py-1 text-mut">Version: <b className="text-ink">{VERSION.name}</b></span>
        <span className="rounded-full border border-line px-3 py-1 text-mut">Updated: <b className="text-ink">{VERSION.date}</b></span>
        <span className="rounded-full border border-line px-3 py-1 text-mut">Architecture: <b className="text-ink">{VERSION.model}</b></span>
      </div>

      {/* who / what */}
      <div className="card mt-8 divide-y divide-line p-5">
        <Row label="Intended use" value={MODEL_CARD.intendedUse} />
        <Row label="Intended users" value={MODEL_CARD.users} />
        <Row label="Decision point" value={MODEL_CARD.decisionPoint} />
        <Row label="Training data" value={MODEL_CARD.data} />
        <Row label="Training method" value={MODEL_CARD.training} />
      </div>

      {/* DO NOT USE — prominent */}
      <div className="mt-6 rounded-xl border-2 border-scc/60 bg-scc/5 p-5">
        <div className="flex items-center gap-2 font-semibold text-scc">
          <span aria-hidden>⛔</span> Do not use for
        </div>
        <ul className="mt-3 grid gap-2 text-sm text-ink md:grid-cols-2">
          {MODEL_CARD.doNotUse.map((d, i) => (
            <li key={i} className="flex gap-2">
              <span className="text-scc" aria-hidden>✕</span>
              <span>{d}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* limitations */}
      <div className="card mt-6 p-5">
        <div className="mb-3 font-semibold text-ink">Known limitations</div>
        <ul className="grid gap-2 text-sm text-mut md:grid-cols-2">
          {MODEL_CARD.limitations.map((d, i) => (
            <li key={i} className="flex gap-2">
              <span className="text-lsil" aria-hidden>▲</span>
              <span>{d}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="card mt-6 p-5">
        <div className="mb-3 font-semibold text-ink">Governance & safety policy</div>
        <div className="grid gap-3 text-sm text-mut md:grid-cols-2">
          <div>
            <b className="text-ink">Four-class grade output</b>
            <div className="text-xs">NILM, LSIL, HSIL, or SCC screening support from the Herlev checkpoint; not a final diagnosis.</div>
          </div>
          <div>
            <b className="text-ink">Binary triage</b>
            <div className="text-xs">A high-sensitivity safety layer for abnormal/high-risk case triage.</div>
          </div>
          <div>
            <b className="text-ink">Independent KOIL endpoint</b>
            <div className="text-xs">Koilocytic morphology assessed by a separate SIPaKMeD model, not an HPV DNA/RNA test.</div>
          </div>
          <div>
            <b className="text-ink">Uncertainty gate</b>
            <div className="text-xs">High-uncertainty cases require human review and block automatic patient-report release.</div>
          </div>
        </div>
      </div>

      {/* metrics summary with CI */}
      <div className="card mt-6 p-5">
        <div className="mb-1 font-semibold text-ink">Performance summary — {METRICS.dataset.total} real Herlev images</div>
        <p className="mb-4 text-xs text-mut">
          Reports the held-out test (n={METRICS.dataset.test}) and 5-fold cross-validation (mean ± SD), including the available 95% confidence interval.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-line text-left text-mut">
                <th className="py-2 pr-4 font-medium">Metric</th>
                <th className="py-2 pr-4 font-medium">Held-out (n={METRICS.dataset.test})</th>
                <th className="py-2 font-medium">5-fold CV (mean ± SD)</th>
              </tr>
            </thead>
            <tbody className="text-ink">
              <tr className="border-b border-line/60">
                <td className="py-2 pr-4">Triage sensitivity</td>
                <td className="py-2 pr-4 font-mono">{t.held.sensitivity}</td>
                <td className="py-2 font-mono">{t.cv.sensitivity}</td>
              </tr>
              <tr className="border-b border-line/60">
                <td className="py-2 pr-4">Triage AUROC <span className="text-xs text-mut">(95% CI {t.held.ci_auroc})</span></td>
                <td className="py-2 pr-4 font-mono">{t.held.auroc}</td>
                <td className="py-2 font-mono">{t.cv.auroc}</td>
              </tr>
              <tr className="border-b border-line/60">
                <td className="py-2 pr-4">Triage specificity</td>
                <td className="py-2 pr-4 font-mono">{t.held.specificity}</td>
                <td className="py-2 font-mono">{t.cv.specificity}</td>
              </tr>
              <tr className="border-b border-line/60">
                <td className="py-2 pr-4">MCC (triage)</td>
                <td className="py-2 pr-4 font-mono text-mut">—</td>
                <td className="py-2 font-mono">{t.cv.mcc}</td>
              </tr>
              <tr className="border-b border-line/60">
                <td className="py-2 pr-4">Supported-grade accuracy (4-class)</td>
                <td className="py-2 pr-4 font-mono text-mut">—</td>
                <td className="py-2 font-mono">{f.acc}</td>
              </tr>
              <tr className="border-b border-line/60">
                <td className="py-2 pr-4">Supported-grade QWK <span className="text-xs text-mut">(ordinal)</span></td>
                <td className="py-2 pr-4 font-mono text-mut">—</td>
                <td className="py-2 font-mono">{f.qwk}</td>
              </tr>
              <tr>
                <td className="py-2 pr-4">HSIL recall <span className="text-xs text-mut">(high grade)</span></td>
                <td className="py-2 pr-4 font-mono text-mut">—</td>
                <td className="py-2 font-mono">{f.recall_hs}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-xs leading-relaxed text-mut">
          Evidence note: Herlev contains no true KOIL examples, so KOIL is excluded from the grade output. The separate SIPaKMeD morphology endpoint achieved locked-test sensitivity 0.9624 and specificity 0.9764, but is not externally validated for ThinPrep.
          Specificity near 0.70 implies some over-referral, a trade-off of the current high-sensitivity screening configuration.
          See the Performance page for the complete results and boundaries.
        </p>
      </div>

      <div className="card mt-6 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="font-semibold text-ink">Separate CRIC four-grade research candidate</div>
            <p className="mt-1 text-xs leading-5 text-mut">Five-fold parent-image-disjoint evaluation on {cg.cells.toLocaleString()} conventional Pap-smear cells from {cg.parents} parent microscope images. This candidate is not the upload checkpoint.</p>
          </div>
          <span className="rounded-full border border-hsil px-3 py-1 text-xs font-semibold text-hsil">Research · not deployed</span>
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg border border-line p-3"><div className="font-mono text-lg font-semibold text-teal">91.7%</div><div className="text-xs text-mut">Selective accuracy</div></div>
          <div className="rounded-lg border border-line p-3"><div className="font-mono text-lg font-semibold text-navy">94.1%</div><div className="text-xs text-mut">Coverage</div></div>
          <div className="rounded-lg border border-line p-3"><div className="font-mono text-lg font-semibold text-ink">88.8%</div><div className="text-xs text-mut">Full-cohort accuracy</div></div>
          <div className="rounded-lg border border-line p-3"><div className="font-mono text-lg font-semibold text-scc">50.3%</div><div className="text-xs text-mut">SCC recall</div></div>
        </div>
        <p className="mt-3 text-xs leading-5 text-mut">Selective accuracy 95% CI {cg.selectiveAccuracyCi}; the lower bound is below 90%. Threshold {cg.selectiveThreshold} is locked for the next external evaluation. These metrics do not establish Thai ThinPrep performance, clinical accuracy, or HPV infection detection.</p>
      </div>

      <p className="mt-6 text-xs text-mut">
        Disclaimer: Research decision support only. Clinician sign-off is required. Not a final diagnosis and not an HPV DNA/RNA test.
      </p>
    </div>
  );
}

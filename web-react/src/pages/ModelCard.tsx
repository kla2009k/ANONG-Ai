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
  const hb = METRICS.herlevBaseline;
  const cg = METRICS.cricGrade;
  const koil = METRICS.koil;
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
        <Row label="Evidence datasets" value={MODEL_CARD.data} />
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

      <section className="mt-8" aria-labelledby="evidence-by-endpoint">
        <h2 id="evidence-by-endpoint" className="font-display text-2xl font-semibold text-ink">Measured evidence by endpoint</h2>
        <p className="mt-2 text-sm leading-6 text-mut">Each block below belongs to a different dataset, task, and evaluation protocol. The values are not interchangeable and the sample counts must not be combined.</p>

        <div className="card mt-5 p-5">
          <div className="flex flex-wrap items-start justify-between gap-3"><div><div className="font-semibold text-ink">Deployed upload baseline · Herlev</div><p className="mt-1 text-xs text-mut">{hb.images} conventional Pap cell images; held-out n={hb.heldOut} plus five-fold CV.</p></div><span className="rounded-full border border-teal px-3 py-1 text-xs font-semibold text-teal">Used by upload workflow</span></div>
          <div className="mt-4 hidden overflow-x-auto sm:block"><table className="w-full min-w-[580px] border-collapse text-sm"><thead><tr className="border-b border-line text-left text-mut"><th className="py-2 pr-4 font-medium">Endpoint</th><th className="py-2 pr-4 font-medium">Held-out</th><th className="py-2 font-medium">5-fold CV · mean ± SD</th></tr></thead><tbody className="text-ink"><tr className="border-b border-line/60"><td className="py-2 pr-4">Binary triage sensitivity</td><td className="py-2 pr-4 font-mono">{hb.binaryTriage.held.sensitivity}</td><td className="py-2 font-mono">{hb.binaryTriage.cv.sensitivity}</td></tr><tr className="border-b border-line/60"><td className="py-2 pr-4">Binary triage specificity</td><td className="py-2 pr-4 font-mono">{hb.binaryTriage.held.specificity}</td><td className="py-2 font-mono">{hb.binaryTriage.cv.specificity}</td></tr><tr className="border-b border-line/60"><td className="py-2 pr-4">Binary triage AUROC</td><td className="py-2 pr-4 font-mono">{hb.binaryTriage.held.auroc} <span className="text-xs text-mut">(95% CI {hb.binaryTriage.held.aurocCi})</span></td><td className="py-2 font-mono">{hb.binaryTriage.cv.auroc}</td></tr><tr><td className="py-2 pr-4">Four-grade exact accuracy</td><td className="py-2 pr-4 text-mut">Not reported</td><td className="py-2 font-mono">{hb.fourGrade.accuracy}</td></tr></tbody></table></div>
          <div className="mt-4 grid gap-3 sm:hidden">
            {[
              ["Binary triage sensitivity", hb.binaryTriage.held.sensitivity, hb.binaryTriage.cv.sensitivity],
              ["Binary triage specificity", hb.binaryTriage.held.specificity, hb.binaryTriage.cv.specificity],
              ["Binary triage AUROC", `${hb.binaryTriage.held.auroc} (CI ${hb.binaryTriage.held.aurocCi})`, hb.binaryTriage.cv.auroc],
              ["Four-grade exact accuracy", "Not reported", hb.fourGrade.accuracy],
            ].map(([endpoint, held, cv]) => <div key={endpoint} className="rounded-lg border border-line p-3"><div className="text-sm font-semibold text-ink">{endpoint}</div><div className="mt-2 grid grid-cols-2 gap-3 text-xs"><div><div className="text-mut">Held-out</div><div className="mt-1 font-mono text-ink">{held}</div></div><div><div className="text-mut">5-fold CV</div><div className="mt-1 font-mono text-ink">{cv}</div></div></div></div>)}
          </div>
          <p className="mt-3 text-xs leading-5 text-mut">Binary triage and exact four-grade classification are different endpoints. High sensitivity is paired with moderate specificity, so this baseline can over-refer and always requires human review.</p>
        </div>

        <div className="card mt-5 p-5">
          <div className="flex flex-wrap items-start justify-between gap-3"><div><div className="font-semibold text-ink">Research candidate · CRIC · not deployed</div><p className="mt-1 text-xs text-mut">Five-fold parent-image-disjoint OOF evaluation on {cg.cells.toLocaleString()} conventional Pap cells from {cg.parents} parent microscope images.</p></div><span className="rounded-full border border-hsil px-3 py-1 text-xs font-semibold text-hsil">Research only</span></div>
          <p className="mt-4 text-sm leading-6 text-ink"><b>91.7% accepted-case accuracy</b> at <b>94.1% coverage</b>; <b>88.8% all-cell accuracy</b>. The model abstained on {cg.abstained.toLocaleString()} uncertain cells.</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><div className="rounded-lg border border-line p-3"><div className="font-mono text-lg font-semibold text-teal">91.7%</div><div className="text-xs text-mut">accepted-case accuracy</div></div><div className="rounded-lg border border-line p-3"><div className="font-mono text-lg font-semibold text-navy">94.1%</div><div className="text-xs text-mut">coverage</div></div><div className="rounded-lg border border-line p-3"><div className="font-mono text-lg font-semibold text-ink">88.8%</div><div className="text-xs text-mut">all-cell accuracy</div></div><div className="rounded-lg border border-line p-3"><div className="font-mono text-lg font-semibold text-scc">50.3%</div><div className="text-xs text-mut">exact SCC recall</div></div></div>
          <p className="mt-3 text-xs leading-5 text-mut">Accepted-case accuracy 95% CI {cg.selectiveAccuracyCi}; its lower bound is below 90%. Threshold {cg.selectiveThreshold} was fixed for evaluation. SCC high-grade capture was 96.3%, but exact SCC recall was only 50.3%; those are different clinical questions.</p>
        </div>

        <div className="card mt-5 p-5">
          <div className="flex flex-wrap items-start justify-between gap-3"><div><div className="font-semibold text-ink">Independent KOIL endpoint · SIPaKMeD</div><p className="mt-1 text-xs text-mut">KOIL morphology positive/negative; locked test n={koil.test} ({koil.positive} positive, {koil.negative} negative).</p></div><span className="rounded-full border border-navy px-3 py-1 text-xs font-semibold text-navy">Separate model</span></div>
          <div className="mt-4 grid gap-3 sm:grid-cols-3"><div className="rounded-lg border border-line p-3"><div className="font-mono text-lg font-semibold text-teal">96.2%</div><div className="text-xs text-mut">sensitivity</div></div><div className="rounded-lg border border-line p-3"><div className="font-mono text-lg font-semibold text-navy">97.6%</div><div className="text-xs text-mut">specificity</div></div><div className="rounded-lg border border-line p-3"><div className="font-mono text-lg font-semibold text-ink">0.991</div><div className="text-xs text-mut">AUROC</div></div></div>
          <p className="mt-3 text-xs leading-5 text-mut">This endpoint estimates koilocytic morphology. It is not a fifth cytology grade and does not detect HPV infection, DNA/RNA, genotype, viral load, or persistence.</p>
        </div>
      </section>

      <p className="mt-6 text-xs text-mut">
        Disclaimer: Research decision support only. Clinician sign-off is required. Not a final diagnosis and not an HPV DNA/RNA test.
      </p>
    </div>
  );
}

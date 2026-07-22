import { Link } from "wouter";
import { Reveal } from "@/components/Reveal";
import { METRICS } from "@/lib/data";

const READINESS = [
  ["Upload models", "Done", "Separate Herlev grade and SIPaKMeD KOIL endpoints"],
  ["Binary safety", "Strong P1", `${METRICS.triage.cv.sensitivity} sensitivity`],
  ["Deployed 4-class grade", "Baseline", `${METRICS.fiveClass.acc} accuracy on Herlev 5-fold CV`],
  ["CRIC 4-class research", "Candidate", "91.7% selective at 94.1% coverage; 88.8% full cohort"],
  ["KOIL morphology", "Internally validated", `${METRICS.koil.sensitivity} sensitivity on SIPaKMeD`],
  ["Calibration", "P1 improved", "Temperature scaling on Herlev only"],
];

export default function Landing() {
  return (
    <div>
      <header className="brand-band relative overflow-hidden px-6 pt-14 pb-16">
        <div className="mx-auto max-w-6xl">
          <div className="grid gap-8 lg:grid-cols-[1.15fr_.85fr]">
            <div>
              <Reveal as="div" className="kicker mb-5">Women's health · Explainable decision-support</Reveal>
              <Reveal as="h1" className="font-display max-w-4xl text-5xl font-bold leading-[1.12] text-ink md:text-7xl">
                Anong
              </Reveal>
              <Reveal as="p" className="mt-3 max-w-2xl font-display text-2xl font-semibold text-teal md:text-3xl">
                Cervical cytology screening and HPV-associated cytomorphology risk assessment
              </Reveal>
              <Reveal as="p" className="mt-5 max-w-2xl text-lg leading-8 text-mut">
                Anong is the user-facing identity of the CerviCo-Pilot research system. It suggests a
                Bethesda-style grade from Pap/ThinPrep-style images, shows Grad-CAM and uncertainty,
                and keeps the clinician responsible for review and sign-off.
              </Reveal>
              <Reveal as="div" className="butter-panel mt-6 max-w-2xl rounded-lg border p-4 text-sm leading-6 text-mut">
                <b className="text-ink">What “HPV risk” means here:</b> Anong assesses HPV-associated cytomorphology, including independent koilocytic-morphology evidence. It <b className="text-scc">does not detect or confirm HPV infection</b>, HPV DNA/RNA, genotype, viral load, or persistence. Molecular confirmation remains a separate laboratory test.
              </Reveal>
              <Reveal as="div" className="mt-8 flex flex-wrap gap-3">
                <Link href="/analyze" className="rounded-full bg-teal px-6 py-3 text-sm font-medium text-white transition hover:bg-teal-d">Analyze an image</Link>
                <Link href="/performance" className="rounded-full border border-teal px-6 py-3 text-sm font-medium text-teal transition hover:bg-teal hover:text-white">View model performance</Link>
              </Reveal>
            </div>
            <Reveal as="div" className="card butter-panel p-5">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-mono text-xs uppercase tracking-[.2em] text-teal">Current evidence</div>
                  <h2 className="mt-1 font-display text-2xl font-semibold text-ink">Multi-dataset research prototype</h2>
                </div>
                <span className="rounded-full border border-teal px-3 py-1 text-xs text-teal">Herlev + SIPaKMeD + CRIC</span>
              </div>
              <div className="mt-5 grid grid-cols-2 gap-3">
                <div className="rounded-lg border border-line p-3">
                  <div className="whitespace-nowrap font-mono text-lg font-semibold text-teal sm:text-xl">{METRICS.koil.total.toLocaleString()}</div>
                  <div className="text-xs text-mut">real KOIL-task cells</div>
                </div>
                <div className="rounded-lg border border-line p-3">
                  <div className="whitespace-nowrap font-mono text-lg font-semibold text-navy sm:text-xl">{METRICS.dataset.total}</div>
                  <div className="text-xs text-mut">real grade-task images</div>
                </div>
                <div className="rounded-lg border border-line p-3">
                  <div className="whitespace-nowrap font-mono text-lg font-semibold text-hsil sm:text-xl">{METRICS.koil.auroc}</div>
                  <div className="text-xs text-mut">KOIL locked AUROC</div>
                </div>
                <div className="rounded-lg border border-line p-3">
                  <div className="whitespace-nowrap font-mono text-lg font-semibold text-scc sm:text-xl">91.7%</div>
                  <div className="text-xs text-mut">CRIC selective accuracy</div>
                </div>
              </div>
              <div className="mt-4 rounded-lg border border-dashed border-line p-3 text-xs leading-5 text-mut">
                The 917 Herlev images, 4,049 SIPaKMeD cells, and 10,003 CRIC cells belong to separate development datasets and are not one patient cohort. The CRIC result is 91.7% selective accuracy at 94.1% coverage; full-cohort accuracy is 88.8%. It is not the deployed upload checkpoint or an HPV DNA/RNA result.
              </div>
            </Reveal>
          </div>
          <Reveal as="div" className="mt-8 grid gap-3 md:grid-cols-3">
            {[
              ["1", "Run analysis", "Upload an image or select a Herlev example to review the four-class grade, independent KOIL morphology score, Grad-CAM, and uncertainty."],
              ["2", "Clinician sign-off", "A clinician can confirm, edit, or reject the result before any patient report is released."],
              ["3", "Audit and follow-up", "Store a local demo history, export JSON, and demonstrate the controlled workflow."],
            ].map(([n, title, body]) => (
              <div key={title} className="card p-4">
                <div className="font-mono text-xs text-teal">STEP {n}</div>
                <div className="mt-1 font-display font-semibold text-ink">{title}</div>
                <p className="mt-1 text-xs leading-5 text-mut">{body}</p>
              </div>
            ))}
          </Reveal>
        </div>
      </header>

      <section className="border-t border-line bg-surface px-6 py-16">
        <div className="mx-auto max-w-6xl">
          <Reveal as="div" className="kicker mb-3">Readiness scorecard</Reveal>
          <Reveal as="h2" className="font-display max-w-3xl text-3xl font-semibold text-ink md:text-4xl">A clear view of what is ready and what must not be claimed</Reveal>
          <div className="mt-8 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {READINESS.map(([area, status, note]) => (
              <Reveal key={area} className="card p-5">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="font-display font-semibold text-ink">{area}</h3>
                  <span className={"rounded-full border px-2 py-1 text-[10px] " + (status.includes("Missing") || status.includes("Not") ? "border-scc text-scc" : "border-teal text-teal")}>{status}</span>
                </div>
                <p className="mt-2 text-xs leading-5 text-mut">{note}</p>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

    </div>
  );
}

import { Link } from "wouter";
import { Reveal } from "@/components/Reveal";
import { METRICS } from "@/lib/data";

const READINESS = [
  ["Models", "Done", "Separate EfficientNet-B0 grade and KOIL endpoints"],
  ["Binary safety", "Strong P1", `${METRICS.triage.cv.sensitivity} sensitivity`],
  ["4-class grading", "Partial", `${METRICS.fiveClass.acc} accuracy on Herlev`],
  ["KOIL morphology", "Internally validated", `${METRICS.koil.sensitivity} sensitivity on SIPaKMeD`],
  ["Calibration", "P1 improved", "Temperature scaling on Herlev only"],
  ["Thai ThinPrep", "Missing", "Protocol exists; data not collected"],
  ["Clinical use", "Not ready", "Reader study and validation required"],
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
                AI-assisted cervical cytology screening
              </Reveal>
              <Reveal as="p" className="mt-5 max-w-2xl text-lg leading-8 text-mut">
                Anong is the user-facing identity of the CerviCo-Pilot research system. It suggests a
                Bethesda-style grade from Pap/ThinPrep-style images, shows Grad-CAM and uncertainty,
                and keeps the clinician responsible for review and sign-off.
              </Reveal>
              <Reveal as="div" className="mt-8 flex flex-wrap gap-3">
                <Link href="/analyze" className="rounded-full bg-teal px-6 py-3 text-sm font-medium text-white transition hover:bg-teal-d">Analyze an image</Link>
                <Link href="/research-report" className="rounded-full border border-teal px-6 py-3 text-sm font-medium text-teal transition hover:bg-teal hover:text-white">View research evidence</Link>
              </Reveal>
            </div>
            <Reveal as="div" className="card butter-panel p-5">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-mono text-xs uppercase tracking-[.2em] text-teal">Current evidence</div>
                  <h2 className="mt-1 font-display text-2xl font-semibold text-ink">Dual-endpoint research prototype</h2>
                </div>
                <span className="rounded-full border border-teal px-3 py-1 text-xs text-teal">Herlev + SIPaKMeD</span>
              </div>
              <div className="mt-5 grid grid-cols-[repeat(auto-fit,minmax(150px,1fr))] gap-3">
                <div className="rounded-lg border border-line p-3">
                  <div className="whitespace-nowrap font-mono text-lg font-semibold text-teal sm:text-xl">{METRICS.dataset.total}</div>
                  <div className="text-xs text-mut">real public images</div>
                </div>
                <div className="rounded-lg border border-line p-3">
                  <div className="whitespace-nowrap font-mono text-lg font-semibold text-navy sm:text-xl">{METRICS.triage.cv.auroc}</div>
                  <div className="text-xs text-mut">binary AUROC CV</div>
                </div>
                <div className="rounded-lg border border-line p-3">
                  <div className="whitespace-nowrap font-mono text-lg font-semibold text-hsil sm:text-xl">{METRICS.fiveClass.qwk}</div>
                  <div className="text-xs text-mut">4-class grade QWK CV</div>
                </div>
                <div className="rounded-lg border border-line p-3">
                  <div className="whitespace-nowrap font-mono text-lg font-semibold text-scc sm:text-xl">0</div>
                  <div className="text-xs text-mut">Thai validation datasets</div>
                </div>
              </div>
              <div className="mt-4 rounded-lg border border-dashed border-line p-3 text-xs leading-5 text-mut">
                HPV panel means morphology risk from cytology images. It is not HPV DNA/RNA detection.
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
          <Reveal as="div" className="mt-5 text-right">
            <Link href="/workflow" className="text-sm font-medium text-teal hover:text-teal-d">View the complete clinical workflow →</Link>
          </Reveal>

          <Reveal as="section" className="mt-10 border-t border-line pt-8" aria-labelledby="endpoint-guides-title">
            <div className="kicker mb-2">Understand the two endpoints</div>
            <h2 id="endpoint-guides-title" className="font-display text-2xl font-semibold text-ink">Inspect the evidence before interpreting a result</h2>
            <div className="mt-5 grid gap-3 md:grid-cols-2">
              <Link href="/koil" className="group rounded-lg border border-line bg-surface p-5 transition hover:border-teal">
                <div className="font-mono text-[10px] uppercase tracking-[.16em] text-teal">Independent model</div>
                <h3 className="mt-2 font-display text-xl font-semibold text-ink">KOIL morphology evidence</h3>
                <p className="mt-2 text-sm leading-6 text-mut">Review the training domain, locked internal test, liquid-based positive challenge, visual examples, Grad-CAM and limitations.</p>
                <div className="mt-4 text-sm font-semibold text-teal">Open KOIL evidence <span aria-hidden>→</span></div>
              </Link>
              <Link href="/hpv" className="group rounded-lg border border-line bg-surface p-5 transition hover:border-teal">
                <div className="font-mono text-[10px] uppercase tracking-[.16em] text-teal">Clinical boundary</div>
                <h3 className="mt-2 font-display text-xl font-semibold text-ink">HPV context, not HPV detection</h3>
                <p className="mt-2 text-sm leading-6 text-mut">See how image morphology, a separate laboratory HPV result and clinician-entered context remain distinct in analysis and reporting.</p>
                <div className="mt-4 text-sm font-semibold text-teal">Open HPV context <span aria-hidden>→</span></div>
              </Link>
            </div>
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

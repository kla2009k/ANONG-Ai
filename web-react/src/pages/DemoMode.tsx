import { useState } from "react";
import { Link } from "wouter";

const STEPS = [
  {
    n: "1",
    title: "Start with current truth",
    path: "/",
    action: "Open the dashboard and separate the Herlev upload baseline, SIPaKMeD KOIL endpoint, and CRIC four-grade research candidate.",
    proof: "State the complete CRIC claim: 91.7% selective accuracy at 94.1% coverage, 88.8% full-cohort accuracy, and no molecular HPV endpoint.",
  },
  {
    n: "2",
    title: "Run an analysis",
    path: "/analyze",
    action: "Select a Herlev example and open the Grad-CAM view.",
    proof: "Show the four-class grade, independent KOIL morphology score, endpoint-specific heatmaps, and uncertainty.",
  },
  {
    n: "3",
    title: "Show clinician sign-off",
    path: "/analyze",
    action: "Use confirm, edit, and reject to demonstrate the human-in-the-loop controls.",
    proof: "Show that the patient report remains locked until sign-off and cannot open for high uncertainty.",
  },
  {
    n: "4",
    title: "Separate KOIL evidence",
    path: "/performance",
    action: "Show the locked SIPaKMeD test, the 20-positive CCCID challenge, threshold, and the visible false negative.",
    proof: "KOIL is an independent morphology endpoint with explicit domain and external-evidence limitations.",
  },
  {
    n: "5",
    title: "Explain the HPV boundary",
    path: "/analyze",
    action: "Enter a separately reported laboratory HPV result as clinical context and contrast it with the image morphology result.",
    proof: "No image endpoint claims viral DNA/RNA, genotype, persistence, or infection status.",
  },
  {
    n: "6",
    title: "Prove it is not cherry-picked",
    path: "/gallery",
    action: "Open the case gallery and show correct, incorrect, and high-uncertainty cases.",
    proof: "Reviewers can inspect real errors and explicit limitations.",
  },
  {
    n: "7",
    title: "Download a reviewed report",
    path: "/reports",
    action: "Open a frozen PDF generated from a real local model run and point out clinician edits and the KOIL section.",
    proof: "Static evidence includes reproducible PDF artifacts; live generation remains available through the local backend.",
  },
  {
    n: "8",
    title: "Review measured performance",
    path: "/performance",
    action: "Show endpoint-specific metrics, CRIC confidence intervals, class recall, error analysis, and current HPV handling.",
    proof: "The page separates the deployed baseline from CRIC research and capabilities that still require paired clinical data.",
  },
];

export default function DemoMode() {
  const [step, setStep] = useState(0);
  const active = STEPS[step];
  return (
    <div className="mx-auto max-w-6xl px-6 py-14">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="kicker mb-2">Judge demo mode</div>
          <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Eight-step demonstration script for reviewers</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-mut">
            Use this page as a teleprompter for a live demonstration, moving from current evidence to analysis,
            clinician sign-off, the honest gallery, workflow controls, and the evidence package.
          </p>
        </div>
        <Link href="/analyze" className="rounded-full bg-teal px-5 py-2.5 text-sm font-medium text-white transition hover:bg-teal-d">
          Start demo
        </Link>
      </div>

      <section className="butter-panel mt-8 rounded-lg border p-6" aria-live="polite">
        <div className="flex flex-wrap items-center justify-between gap-3"><div className="font-mono text-xs uppercase tracking-[.16em] text-teal">Presentation mode · {step + 1} of {STEPS.length}</div><div className="flex gap-2"><button type="button" disabled={step === 0} onClick={() => setStep((value) => value - 1)} className="rounded-lg border border-line bg-surface px-3 py-1.5 text-xs font-semibold text-mut disabled:opacity-40">Previous</button><button type="button" disabled={step === STEPS.length - 1} onClick={() => setStep((value) => value + 1)} className="rounded-lg border border-line bg-surface px-3 py-1.5 text-xs font-semibold text-mut disabled:opacity-40">Next</button></div></div>
        <h2 className="mt-4 font-display text-3xl font-semibold text-ink">{active.n}. {active.title}</h2><p className="mt-3 text-base leading-7 text-ink">{active.action}</p><p className="mt-2 text-sm leading-6 text-mut"><b className="text-ink">Evidence to point out:</b> {active.proof}</p><Link href={active.path} className="mt-5 inline-block rounded-lg bg-teal px-4 py-2.5 text-sm font-semibold text-white">Open this step</Link>
      </section>

      <div className="mt-8 grid gap-4">
        {STEPS.map((s) => (
          <section key={s.n} className={"card p-5 " + (s.n === active.n ? "border-teal" : "")}>
            <div className="grid gap-4 md:grid-cols-[72px_1fr_auto] md:items-center">
                <button type="button" onClick={() => setStep(Number(s.n) - 1)} aria-label={`Select demo step ${s.n}`} className="grid h-14 w-14 place-items-center rounded-lg bg-teal font-mono text-xl font-semibold text-white">
                  {s.n}
                </button>
              <div>
                <h2 className="font-display text-xl font-semibold text-ink">{s.title}</h2>
                <p className="mt-1 text-sm text-ink">{s.action}</p>
                <p className="mt-1 text-xs leading-5 text-mut">Evidence to point out: {s.proof}</p>
              </div>
              <Link href={s.path} className="rounded-full border border-line px-4 py-2 text-sm text-mut transition hover:border-teal hover:text-teal">
                Open page
              </Link>
            </div>
          </section>
        ))}
      </div>

      <section className="mt-8 rounded-2xl border border-dashed border-line p-5">
        <h2 className="font-display text-xl font-semibold text-ink">Opening line</h2>
        <p className="mt-2 text-sm leading-6 text-mut">
          CerviCo-Pilot is neither a chatbot nor an autonomous diagnostic system. It is a cervical cytology screening-support workflow:
          one vision endpoint provides a four-class grade and another assesses KOIL morphology; the interface shows endpoint-specific Grad-CAM and uncertainty, a clinician signs off,
          and the patient report remains locked until the workflow permits communication.
        </p>
      </section>
    </div>
  );
}

import { Link } from "wouter";

const STEPS = [
  {
    n: "1",
    title: "Start with current truth",
    path: "/",
    action: "Open the dashboard and state that grade/triage evidence is Herlev and KOIL morphology evidence is separately SIPaKMeD.",
    proof: "Point to the measured metrics, zero Thai validation datasets, and the HPV boundary.",
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
    title: "Prove it is not cherry-picked",
    path: "/gallery",
    action: "Open the case gallery and show correct, incorrect, and high-uncertainty cases.",
    proof: "Reviewers can inspect real errors and explicit limitations.",
  },
  {
    n: "5",
    title: "Explain the workflow",
    path: "/workflow",
    action: "Walk through the safety gates from image to AI, human review, report, and follow-up.",
    proof: "The product is a controlled clinical workflow rather than an isolated classifier.",
  },
  {
    n: "6",
    title: "Open evidence package",
    path: "/research-report",
    action: "Show the research report, bibliography, model card, and validation roadmap.",
    proof: "The package includes submission-ready evidence and explicit claim boundaries.",
  },
];

export default function DemoMode() {
  return (
    <div className="mx-auto max-w-6xl px-6 py-14">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="kicker mb-2">Judge demo mode</div>
          <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Six-step demonstration script for reviewers</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-mut">
            Use this page as a teleprompter for a live demonstration, moving from current evidence to analysis,
            clinician sign-off, the honest gallery, workflow controls, and the evidence package.
          </p>
        </div>
        <Link href="/analyze" className="rounded-full bg-teal px-5 py-2.5 text-sm font-medium text-white transition hover:bg-teal-d">
          Start demo
        </Link>
      </div>

      <div className="mt-8 grid gap-4">
        {STEPS.map((s) => (
          <section key={s.n} className="card p-5">
            <div className="grid gap-4 md:grid-cols-[72px_1fr_auto] md:items-center">
              <div className="grid h-14 w-14 place-items-center rounded-2xl bg-teal font-mono text-xl font-semibold text-white">
                {s.n}
              </div>
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

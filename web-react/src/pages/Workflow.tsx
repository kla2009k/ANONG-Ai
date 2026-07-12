import { Link } from "wouter";

const FLOW = [
  ["1", "Image intake", "Receive a ThinPrep/Pap-style cytology image with a quality note.", "The image must be interpretable; reject or recollect when quality is inadequate."],
  ["2", "5-class cytology grade", "Suggest a Bethesda-style category: NILM, LSIL, HSIL, SCC, or the KOIL placeholder.", "The 5-class output is the product identity; binary triage is the safety layer."],
  ["3", "HPV morphology note", "Describe cellular morphology that may be HPV-related.", "This is not an HPV DNA/RNA test and does not confirm infection."],
  ["4", "Grad-CAM + uncertainty", "Show the emphasized image region and estimated uncertainty.", "Grad-CAM supports review; it is not causal proof."],
  ["5", "Clinician sign-off", "A qualified reviewer can confirm, edit, or reject the result.", "High uncertainty blocks the patient report."],
  ["6", "Report + follow-up", "Release clinician/patient reports after sign-off and record the demo audit entry.", "The localStorage audit is a demo; a pilot requires a server-side signed log."],
];

const SAFETY = [
  ["High uncertainty", "Route to independent human review", "Do not release an automatic patient report."],
  ["HSIL / SCC", "Prioritize prompt confirmatory referral", "This represents high-risk cytology, not HPV confirmation."],
  ["KOIL", "Keep as a Phase 2 target", "Herlev contains no true KOIL examples, so this class is not validated."],
  ["OOD / poor image", "Reject or recollect", "The model must not be forced to answer every case."],
];

export default function Workflow() {
  return (
    <div className="mx-auto max-w-6xl px-6 py-14">
      <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
        <div>
          <div className="kicker mb-2">Clinical pathway</div>
          <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">From cytology image to clinical follow-up</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-mut">
            CerviCo-Pilot is more than a classifier. It is a controlled workflow with an uncertainty gate, human sign-off, report lock, and demo audit trail.
          </p>
        </div>
        <div className="card p-5">
          <div className="font-mono text-xs uppercase tracking-[.2em] text-teal">Decision boundary</div>
          <p className="mt-2 text-sm text-mut">
            AI provides a pre-screen suggestion only. It does not diagnose, replace a cytotechnologist/pathologist, or detect HPV DNA/RNA.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <Link href="/analyze" className="inline-flex rounded-full bg-teal px-4 py-2 text-sm font-medium text-white">Try the workflow</Link>
            <Link href="/reports" className="inline-flex rounded-full border border-teal px-4 py-2 text-sm font-medium text-teal">Preview reports</Link>
          </div>
        </div>
      </div>

      <div className="mt-10 grid gap-4">
        {FLOW.map(([n, title, body, caveat], i) => (
          <div key={title} className="grid gap-4 rounded-2xl border border-line bg-surface p-5 md:grid-cols-[72px_1fr_320px]">
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-teal font-mono text-xl font-semibold text-white">{n}</div>
            <div>
              <h2 className="font-display text-xl font-semibold text-ink">{title}</h2>
              <p className="mt-1 text-sm leading-6 text-mut">{body}</p>
            </div>
            <div className="rounded-xl border border-dashed border-line p-3 text-xs leading-5 text-mut">
              {caveat}
            </div>
            {i < FLOW.length - 1 && <div className="hidden md:block" />}
          </div>
        ))}
      </div>

      <section className="mt-12">
        <div className="kicker mb-2">Safety gates</div>
        <h2 className="font-display text-2xl font-semibold text-ink">Where the system must stop and defer to a human</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          {SAFETY.map(([title, action, note]) => (
            <div key={title} className="card p-5">
              <h3 className="font-display text-lg font-semibold text-ink">{title}</h3>
              <p className="mt-2 text-sm text-teal">{action}</p>
              <p className="mt-1 text-xs leading-5 text-mut">{note}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

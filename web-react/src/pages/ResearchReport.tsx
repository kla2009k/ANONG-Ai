import { ArrowRight, BadgeInfo, BookOpen, Database, FileText, MessageCircleQuestion, PlayCircle, ServerCog } from "lucide-react";
import { Link } from "wouter";

const BASE = import.meta.env.BASE_URL;

const DOCS = [
  {
    title: "Independent KOIL validation report",
    file: "/docs/KOIL_REAL_DATA_VALIDATION_2026.md",
    desc: "Official SIPaKMeD provenance, source-cluster split, locked-test metrics, confidence intervals, error analysis, XAI, and claims policy.",
    tag: "MD",
  },
  {
    title: "WSEEC 2026 full paper - polished PDF",
    file: "/docs/CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.pdf",
    desc: "Polished 12-page English WSEEC submission, laid out in Microsoft Word and visually checked after rendering.",
    tag: "PDF",
  },
  {
    title: "WSEEC 2026 full paper - polished Word",
    file: "/docs/CerviCo_Pilot_WSEEC_2026_Full_Paper_Polished.docx",
    desc: "Editable Word file for final author names, logos, institution details, and PDF export.",
    tag: "DOCX",
  },
  {
    title: "Formal research report",
    file: "/docs/CerviCo_Pilot_Formal_Research_Report_2026_Polished.docx",
    desc: "Formal Thai-language research report with cover, approval page, abstracts, Chapters 1–5, references, and appendices.",
    tag: "DOCX",
  },
  {
    title: "Formal bibliography",
    file: "/docs/FORMAL_REFERENCES_BIBLIOGRAPHY.md",
    desc: "Source bibliography covering WHO, CDC, Bethesda, EfficientNet, Grad-CAM, MC Dropout, GMLP, CONSORT-AI, and DECIDE-AI.",
    tag: "MD",
  },
  {
    title: "Final polish checklist",
    file: "/docs/FORMAL_REPORT_FINAL_POLISH_CHECKLIST.md",
    desc: "Pre-submission checklist for Word pagination, figures, tables, and final PDF export.",
    tag: "MD",
  },
  {
    title: "Model card",
    file: "/docs/DATASET_MODEL_CARD.md",
    desc: "Herlev dataset scope, checkpoint provenance, metrics, intended use, and model limitations.",
    tag: "MD",
  },
  {
    title: "Validation roadmap",
    file: "/docs/VALIDATION_ROADMAP.md",
    desc: "Roadmap for Thai ThinPrep validation, paired HPV endpoints, a reader study, and a prospective pilot.",
    tag: "MD",
  },
  {
    title: "Claims ledger",
    file: "/docs/CLAIMS_LEDGER.md",
    desc: "Canonical ledger defining supported claims, prohibited claims, and approved wording.",
    tag: "MD",
  },
];

const EVIDENCE = [
  ["Grade/triage data", "Herlev public cervical cytology, 917 real images", "No Thai ThinPrep validation yet"],
  ["KOIL data", "SIPaKMeD, 4,049 cells from 966 source clusters", "Conventional Pap-smear crops; no paired HPV assay"],
  ["Grade model", "EfficientNet-B0, `models/best_cervical.pt`", "Interface exposes four supported grade classes"],
  ["KOIL endpoint", "Sensitivity 0.9624, specificity 0.9764, AUROC 0.9912", "Locked 641-cell test; cluster-bootstrap CIs reported"],
  ["Legacy grade evaluation", "Accuracy 0.6934, macro AUROC 0.7311", "Historical five-output head; KOIL unsupported in Herlev"],
  ["Binary triage", "Sensitivity 1.0, AUROC 0.964, TP 101 / TN 26 / FP 10 / FN 0", "Held-out Herlev split, not a Thai-domain result"],
  ["Cross-validation", "Binary sensitivity 0.9867 +/- 0.0086, AUROC 0.9435 +/- 0.0448", "Still limited to the Herlev domain"],
  ["Calibration", "Temperature scaling improved Herlev held-out ECE/Brier", "Not a fully calibrated external Thai model"],
];

const PROJECT_TOOLS = [
  { href: "/reports", title: "Report preview", detail: "Review clinician and patient report states and download model-generated PDF examples.", icon: FileText },
  { href: "/datasets", title: "Dataset registry", detail: "Separate current model evidence, external references, and candidate datasets with source links.", icon: Database },
  { href: "/model", title: "Model card", detail: "Inspect intended use, provenance, and limitations.", icon: BadgeInfo },
  { href: "/knowledge", title: "Knowledge guide", detail: "Review cytology terms and responsible interpretation.", icon: BookOpen },
  { href: "/demo", title: "Judge demo", detail: "Run the guided six-step presentation.", icon: PlayCircle },
  { href: "/deployment", title: "Deployment readiness", detail: "Check technical and pre-pilot requirements.", icon: ServerCog },
  { href: "/ask", title: "Ask Anong", detail: "Explore project information through the assistant.", icon: MessageCircleQuestion },
];

export default function ResearchReport() {
  return (
    <div className="mx-auto max-w-6xl px-6 py-14">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="kicker mb-2">Evidence & report package</div>
          <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Research reports and submission evidence</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-mut">
            This page collects the files reviewers and the project team should inspect before submission: research reports,
            bibliography, model card, validation roadmap, and claims ledger. Performance figures must come from the canonical JSON and these controlled reports.
          </p>
        </div>
        <a
          href={`${BASE}docs/CerviCo_Pilot_Formal_Research_Report_2026_Polished.docx`}
          className="rounded-full bg-teal px-5 py-2.5 text-sm font-medium text-white transition hover:bg-teal-d"
        >
          Download DOCX
        </a>
      </div>

      <section className="mt-8 grid gap-3 md:grid-cols-3">
        {[
          ["Final submission", "Use the _Polished.docx file", "Open it in Word, update contents and page numbers, then export the final PDF."],
          ["Claim control", "Run the audit before publishing", "python tools\\audit_claims.py --all"],
          ["Responsible framing", "HPV = morphology risk", "Not HPV DNA/RNA testing and not clinical deployment."],
        ].map(([title, value, note]) => (
          <div key={title} className="card p-5">
            <div className="font-mono text-xs uppercase tracking-[.18em] text-teal">{title}</div>
            <div className="mt-2 font-display text-xl font-semibold text-ink">{value}</div>
            <p className="mt-2 text-xs leading-5 text-mut">{note}</p>
          </div>
        ))}
      </section>

      <section className="mt-10">
        <h2 className="font-display text-2xl font-semibold text-ink">Evidence snapshot</h2>
        <div className="mt-4 overflow-hidden rounded-2xl border border-line bg-surface">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[780px] text-left text-sm">
              <thead className="border-b border-line text-xs uppercase tracking-[.16em] text-mut">
                <tr>
                  <th className="px-4 py-3">Layer</th>
                  <th className="px-4 py-3">Current evidence</th>
                  <th className="px-4 py-3">Boundary</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {EVIDENCE.map(([layer, evidence, boundary]) => (
                  <tr key={layer}>
                    <td className="px-4 py-3 font-semibold text-ink">{layer}</td>
                    <td className="px-4 py-3 text-mut">{evidence}</td>
                    <td className="px-4 py-3 text-mut">{boundary}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="mt-10">
        <h2 className="font-display text-2xl font-semibold text-ink">Download package</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {DOCS.map((doc) => (
            <a key={doc.file} href={`${BASE}${doc.file.replace(/^\//, "")}`} className="card card-hover block p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-display text-lg font-semibold text-ink">{doc.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-mut">{doc.desc}</p>
                </div>
                <span className="rounded-full border border-teal px-2 py-1 font-mono text-[10px] text-teal">{doc.tag}</span>
              </div>
            </a>
          ))}
        </div>
      </section>

      <section className="mt-10">
        <div className="kicker mb-2">Supporting tools</div>
        <h2 className="font-display text-2xl font-semibold text-ink">Explore the project in more detail</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-mut">
          These supporting views are kept together here so the primary navigation remains focused on the core clinical workflow.
        </p>
        <div className="mt-4 divide-y divide-line border-y border-line">
          {PROJECT_TOOLS.map(({ href, title, detail, icon: Icon }) => (
            <Link key={href} href={href} className="group flex items-center gap-4 px-1 py-4 transition hover:bg-paper sm:px-3">
              <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-aqua/25 text-teal">
                <Icon size={17} strokeWidth={1.8} aria-hidden />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block font-display font-semibold text-ink">{title}</span>
                <span className="block text-xs leading-5 text-mut">{detail}</span>
              </span>
              <ArrowRight className="shrink-0 text-mut transition group-hover:translate-x-1 group-hover:text-teal" size={17} aria-hidden />
            </Link>
          ))}
        </div>
      </section>

      <section className="mt-10 rounded-2xl border border-dashed border-line p-5">
        <h2 className="font-display text-xl font-semibold text-ink">Submission note</h2>
        <p className="mt-2 text-sm leading-6 text-mut">
          Browser download paths work after copying `docs/` into the deployed static bundle or serving the project root through a backend.
          If this page is deployed as a static site only, include the DOCX/PDF files in the hosting public directory before submission.
        </p>
      </section>
    </div>
  );
}

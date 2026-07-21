import { useMemo, useState } from "react";
import { Link } from "wouter";
import { AlertTriangle, ArrowRight, CheckCircle2, Dna, Eye, FileCheck2, Microscope, Route, TestTube2 } from "lucide-react";
import { METRICS } from "@/lib/data";

const BASE = import.meta.env.BASE_URL;

const WORKFLOW = [
  ["01", "Image intake", "Accept a Pap/ThinPrep-style image and apply quality checks. Reject images that are blurred, obscured or outside the supported domain."],
  ["02", "Separate AI endpoints", "Generate a four-class grade suggestion and an independent KOIL morphology score. Neither output is a final diagnosis."],
  ["03", "Review evidence", "Inspect uncertainty, grade Grad-CAM and KOIL-specific Grad-CAM. Attention maps are not segmentation or causal proof."],
  ["04", "Add clinical context", "Record age, symptoms, screening history and a separately reported laboratory HPV result without changing image-model probabilities."],
  ["05", "Clinician decision", "A qualified reviewer confirms, edits or rejects the output. High uncertainty or failed XAI keeps the report locked."],
  ["06", "Report and audit", "Release the decision-support report after sign-off and retain a traceable audit entry. The static demo stores data locally only."],
] as const;

const CO_FINDINGS = [
  ["Candida spp.", "Fungal morphology", "Not trained"],
  ["Trichomonas vaginalis", "Organism morphology", "Not trained"],
  ["Bacterial vaginosis pattern", "Flora shift / clue-cell pattern", "Not trained"],
  ["Actinomyces spp.", "Bacterial morphology", "Not trained"],
  ["HSV / CMV-associated change", "Viral cytopathic morphology", "Not trained"],
  ["Reactive / reparative change", "Non-neoplastic mimic", "Not trained"],
] as const;

export default function ClinicalEvidence() {
  const [grade, setGrade] = useState("NILM");
  const [koil, setKoil] = useState("negative");
  const [lab, setLab] = useState("not_performed");
  const [symptoms, setSymptoms] = useState(false);
  const guide = useMemo(() => interpretState(grade, koil, lab, symptoms), [grade, koil, lab, symptoms]);
  const k = METRICS.koil;

  return (
    <div className="pb-16">
      <section className="brand-band">
        <div className="mx-auto max-w-6xl px-6 py-12">
          <div className="kicker mb-3">Clinical evidence and workflow</div>
          <div className="grid gap-7 lg:grid-cols-[1.2fr_.8fr] lg:items-end">
            <div>
              <h1 className="max-w-4xl font-display text-4xl font-semibold text-ink md:text-5xl">One review path from cell morphology to clinician sign-off</h1>
              <p className="mt-4 max-w-3xl text-base leading-7 text-mut">KOIL evidence, HPV context and the release workflow are presented together so that an image finding cannot be mistaken for a molecular HPV result or an autonomous diagnosis.</p>
            </div>
            <div className="flex flex-wrap gap-3 lg:justify-end"><Link href="/analyze" className="inline-flex items-center gap-2 rounded-lg bg-teal px-4 py-2.5 text-sm font-semibold text-white">Open Analyze <ArrowRight size={16} aria-hidden /></Link><a href="#workflow" className="rounded-lg border border-line bg-surface px-4 py-2.5 text-sm font-semibold text-ink">View workflow</a></div>
          </div>
        </div>
      </section>

      <nav className="sticky top-14 z-30 border-b border-line bg-surface/95 px-6 py-3 backdrop-blur lg:top-0" aria-label="Clinical evidence sections">
        <div className="mx-auto flex max-w-6xl gap-5 overflow-x-auto whitespace-nowrap text-xs font-semibold text-mut"><a href="#koil" className="hover:text-teal">KOIL evidence</a><a href="#hpv" className="hover:text-teal">HPV boundary</a><a href="#bethesda" className="hover:text-teal">Bethesda co-findings</a><a href="#workflow" className="hover:text-teal">Clinical workflow</a></div>
      </nav>

      <main className="mx-auto max-w-6xl px-6">
        <section id="koil" className="scroll-mt-28 py-12" aria-labelledby="koil-title">
          <div className="grid gap-8 lg:grid-cols-[.72fr_1.28fr]">
            <div><div className="kicker mb-2">Independent morphology endpoint</div><h2 id="koil-title" className="font-display text-3xl font-semibold text-ink">KOIL evidence</h2><p className="mt-3 text-sm leading-6 text-mut">The KOIL model was trained and locked separately from the grade model. It identifies morphology consistent with SIPaKMeD's Koilocytotic class; it does not detect viral DNA, RNA, genotype or persistence.</p></div>
            <div className="grid grid-cols-2 gap-px overflow-hidden rounded-lg border border-line bg-line md:grid-cols-4">
              <Metric label="Sensitivity" value={k.sensitivity} note={`95% CI ${k.sensitivityCi}`} />
              <Metric label="Specificity" value={k.specificity} note={`95% CI ${k.specificityCi}`} />
              <Metric label="AUROC" value={k.auroc} note="Locked internal test" />
              <Metric label="LBC challenge" value={k.externalDetected} note="Positive-only subset" />
            </div>
          </div>

          <div className="mt-8 overflow-x-auto rounded-lg border border-line bg-surface"><table className="w-full min-w-[720px] border-collapse text-left text-sm"><thead className="bg-[var(--blush-soft)]"><tr><th className="p-4 text-ink">Evidence stage</th><th className="p-4 text-ink">Dataset and domain</th><th className="p-4 text-ink">What it supports</th></tr></thead><tbody className="divide-y divide-line"><tr><th className="p-4 text-ink">Development + locked test</th><td className="p-4 text-mut">4,049 SIPaKMeD conventional Pap-smear cells; 966 source clusters; cluster-disjoint split</td><td className="p-4 text-mut">Internal KOIL morphology discrimination and calibration</td></tr><tr><th className="p-4 text-ink">Limited domain challenge</th><td className="p-4 text-mut">20 prespecified CCCID v2 BD SurePath KOIL-positive images</td><td className="p-4 text-mut">19/20 positive detection; no external specificity or AUROC</td></tr><tr><th className="p-4 text-ink">Clinical ThinPrep validation</th><td className="p-4 text-mut">Negative-inclusive Thai cohort with paired laboratory HPV results</td><td className="p-4 font-semibold text-scc">Not yet performed</td></tr></tbody></table></div>

          <div className="mt-6 grid gap-4 md:grid-cols-3">
            {["koil-intermediate-01.jpg", "koil-superficial-01.jpg", "koil-intermediate-03.jpg"].map((file, index) => <figure key={file} className="overflow-hidden rounded-lg border border-line bg-surface"><img src={`${BASE}koil-gallery/${file}`} alt={`Expert-labelled KOIL morphology reference ${index + 1}`} className="aspect-[4/3] w-full object-cover" loading="lazy" /><figcaption className="p-3 text-xs text-mut">CCCID v2 expert-labelled KOIL reference · morphology only</figcaption></figure>)}
          </div>
          <div className="butter-panel mt-5 flex gap-3 rounded-lg border p-4 text-sm leading-6 text-mut"><AlertTriangle className="mt-0.5 shrink-0 text-hsil" size={19} aria-hidden /><p><b className="text-ink">Evidence limit:</b> the external CCCID subset contains positives only. Specificity, predictive values, calibration and clinical accuracy cannot be estimated from it.</p></div>
        </section>

        <section id="hpv" className="scroll-mt-28 border-t border-line py-12" aria-labelledby="hpv-title">
          <div className="kicker mb-2">Relationship, not equivalence</div><h2 id="hpv-title" className="font-display text-3xl font-semibold text-ink">Three evidence streams remain separate</h2>
          <div className="mt-6 grid gap-4 lg:grid-cols-3">
            <EvidenceCard icon={Eye} title="Image morphology" owner="AI + reviewer" body="Four-class cytology grade, KOIL score, uncertainty and class-specific Grad-CAM." boundary="Cannot establish HPV infection or genotype." />
            <EvidenceCard icon={TestTube2} title="Laboratory HPV assay" owner="External laboratory" body="A separately performed HPV result and reported genotype may be entered as report context." boundary="Never inferred from image pixels." />
            <EvidenceCard icon={FileCheck2} title="Clinical context" owner="Clinician entered" body="Age, symptoms, history and selected risk context support review and documentation." boundary="Does not alter current model probabilities." />
          </div>

          <div className="mt-8 grid gap-7 lg:grid-cols-[.78fr_1.22fr]">
            <div className="space-y-4">
              <Select label="Reviewed grade" value={grade} set={setGrade} options={["NILM", "LSIL", "HSIL", "SCC"]} />
              <Select label="KOIL morphology" value={koil} set={setKoil} options={["negative", "positive", "unavailable"]} />
              <Select label="Separate laboratory HPV result" value={lab} set={setLab} options={["not_performed", "negative", "positive", "unknown"]} />
              <label className="flex items-center gap-3 rounded-lg border border-line bg-surface p-3 text-sm text-mut"><input type="checkbox" checked={symptoms} onChange={(e) => setSymptoms(e.target.checked)} className="accent-[var(--teal)]" />Symptoms reported</label>
            </div>
            <div className="rounded-lg border border-line bg-surface p-6" aria-live="polite"><div className="font-mono text-[10px] uppercase tracking-[.16em] text-teal">Interpretation guide, not diagnosis</div><h3 className="mt-2 font-display text-2xl font-semibold text-ink">{guide.title}</h3><p className="mt-3 text-sm leading-6 text-mut">{guide.morphology}</p><dl className="mt-5 divide-y divide-line border-y border-line text-sm"><div className="grid gap-2 py-4 sm:grid-cols-[9rem_1fr]"><dt className="font-semibold text-ink">Laboratory evidence</dt><dd className="leading-6 text-mut">{guide.lab}</dd></div><div className="grid gap-2 py-4 sm:grid-cols-[9rem_1fr]"><dt className="font-semibold text-ink">Safety action</dt><dd className="leading-6 text-mut">{guide.action}</dd></div></dl></div>
          </div>
        </section>

        <section id="bethesda" className="scroll-mt-28 border-t border-line py-12" aria-labelledby="bethesda-title">
          <div className="grid gap-8 lg:grid-cols-[.72fr_1.28fr]">
            <div><div className="kicker mb-2">Bethesda-aligned expansion</div><h2 id="bethesda-title" className="font-display text-3xl font-semibold text-ink">Non-neoplastic co-findings need a separate model head</h2><p className="mt-3 text-sm leading-6 text-mut">Bethesda reporting allows organisms and reactive changes to be described within NILM. They can coexist with an epithelial abnormality, so they must not be forced into a mutually exclusive cancer-grade class.</p></div>
            <div className="overflow-hidden rounded-lg border border-line bg-surface"><table className="w-full text-left text-sm"><thead className="bg-[var(--blush-soft)]"><tr><th className="p-3 text-ink">Future co-finding</th><th className="hidden p-3 text-ink sm:table-cell">Endpoint</th><th className="p-3 text-ink">Status</th></tr></thead><tbody className="divide-y divide-line">{CO_FINDINGS.map(([name, endpoint, status]) => <tr key={name}><td className="p-3 font-medium text-ink">{name}</td><td className="hidden p-3 text-mut sm:table-cell">{endpoint}</td><td className="p-3"><span className="rounded-full border border-scc px-2 py-1 text-[10px] font-semibold text-scc">{status}</span></td></tr>)}</tbody></table></div>
          </div>
          <div className="blush-panel mt-6 rounded-lg border p-5 text-sm leading-6 text-mut"><b className="text-ink">Required training design:</b> expert multi-label annotations, organism-confirmation metadata where appropriate, slide/patient-grouped splits, enough positive cases per finding, mimic-focused error analysis and external ThinPrep validation. Synthetic augmentation can support robustness but cannot replace real positive support.</div>
          <p className="mt-4 text-xs leading-5 text-mut">Terminology reference: <a className="text-teal underline" href="https://screening.iarc.fr/atlasclassifbethesda.php?lang=1" target="_blank" rel="noreferrer">IARC Bethesda classification</a> and <a className="text-teal underline" href="https://www.cancer.gov/publications/dictionaries/cancer-terms/def/negative-for-intraepithelial-lesion-or-malignancy" target="_blank" rel="noreferrer">NCI NILM definition</a>.</p>
        </section>

        <section id="workflow" className="scroll-mt-28 border-t border-line py-12" aria-labelledby="workflow-title">
          <div className="flex items-center gap-3"><Route className="text-teal" size={24} aria-hidden /><div><div className="kicker mb-1">Controlled release path</div><h2 id="workflow-title" className="font-display text-3xl font-semibold text-ink">Clinical workflow</h2></div></div>
          <ol className="mt-7 divide-y divide-line border-y border-line">{WORKFLOW.map(([number, title, detail]) => <li key={number} className="grid gap-2 py-5 sm:grid-cols-[3rem_12rem_1fr]"><span className="font-mono text-sm text-teal">{number}</span><h3 className="font-semibold text-ink">{title}</h3><p className="text-sm leading-6 text-mut">{detail}</p></li>)}</ol>
          <div className="mt-6 grid gap-3 md:grid-cols-3"><Safety icon={Microscope} title="Uncertain or poor quality" body="Reject or route to independent human review." /><Safety icon={Dna} title="HPV-related morphology" body="Correlate with a separate assay when clinically indicated." /><Safety icon={CheckCircle2} title="Report release" body="Require named reviewer sign-off and preserve the audit record." /></div>
        </section>
      </main>
    </div>
  );
}

function Metric({ label, value, note }: { label: string; value: string; note: string }) { return <div className="bg-surface p-4"><div className="text-[10px] uppercase tracking-wide text-mut">{label}</div><div className="mt-1 font-mono text-xl font-semibold text-teal">{value}</div><div className="mt-1 text-[10px] text-mut">{note}</div></div>; }
function EvidenceCard({ icon: Icon, title, owner, body, boundary }: { icon: typeof Eye; title: string; owner: string; body: string; boundary: string }) { return <article className="rounded-lg border border-line bg-surface p-5"><div className="flex items-center justify-between"><span className="grid h-9 w-9 place-items-center rounded-lg bg-[var(--blush-soft)] text-teal"><Icon size={18} aria-hidden /></span><span className="font-mono text-[9px] uppercase text-mut">{owner}</span></div><h3 className="mt-4 font-display text-xl font-semibold text-ink">{title}</h3><p className="mt-2 text-sm leading-6 text-mut">{body}</p><p className="mt-4 border-t border-line pt-4 text-xs leading-5 text-mut"><b className="text-ink">Boundary:</b> {boundary}</p></article>; }
function Select({ label, value, set, options }: { label: string; value: string; set: (v: string) => void; options: string[] }) { return <label className="block text-xs text-mut">{label}<select value={value} onChange={(e) => set(e.target.value)} className="mt-1 w-full rounded-lg border border-line bg-surface px-3 py-2.5 text-sm text-ink">{options.map((option) => <option key={option} value={option}>{option.replaceAll("_", " ")}</option>)}</select></label>; }
function Safety({ icon: Icon, title, body }: { icon: typeof Eye; title: string; body: string }) { return <div className="rounded-lg border border-line bg-surface p-4"><Icon size={18} className="text-teal" aria-hidden /><h3 className="mt-3 font-semibold text-ink">{title}</h3><p className="mt-1 text-xs leading-5 text-mut">{body}</p></div>; }

function interpretState(grade: string, koil: string, lab: string, symptoms: boolean) {
  const title = symptoms ? "Symptoms require a separate clinical pathway" : grade === "HSIL" || grade === "SCC" ? "High-risk cytology remains the primary image finding" : koil === "positive" ? "Koilocytotic morphology was flagged" : "No prominent koilocytotic morphology was flagged";
  const morphology = koil === "positive" ? `The KOIL endpoint is positive alongside a reviewed ${grade} category. This supports morphology review but does not establish HPV infection.` : koil === "negative" ? `The KOIL endpoint is negative alongside a reviewed ${grade} category. Absence of this morphology does not rule out HPV.` : `The KOIL endpoint is unavailable. No KOIL inference should be made; the reviewed grade remains ${grade}.`;
  const labText = lab === "positive" ? "The separately reported positive molecular result is the relevant HPV evidence; it is not an image-model output." : lab === "negative" ? "The separately reported negative molecular result remains distinct from cytology and KOIL outputs." : "No interpretable laboratory HPV result is available in this state.";
  const action = symptoms ? "Evaluate symptoms independently regardless of the image result." : grade === "HSIL" || grade === "SCC" ? "Prioritize qualified review and the applicable confirmatory pathway." : "Use qualified review and the applicable screening pathway; molecular testing remains separate.";
  return { title, morphology, lab: labText, action };
}

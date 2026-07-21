import { Link } from "wouter";
import { AlertCircle, ArrowRight, ClipboardPlus, Dna, Eye, FileCheck2, TestTube2 } from "lucide-react";

const BASE = import.meta.env.BASE_URL;

const EVIDENCE_LAYERS = [
  { icon: Eye, title: "Image morphology", owner: "Anong AI + reviewer", detail: "Cytology grade, KOIL morphology score, uncertainty and class-specific Grad-CAM.", boundary: "Cannot identify viral DNA/RNA, genotype, persistence or infection status." },
  { icon: TestTube2, title: "Laboratory HPV assay", owner: "External laboratory", detail: "A separately performed HPV result and reported genotype may be entered as clinical context.", boundary: "The value is recorded from the laboratory report; Anong never infers it from pixels." },
  { icon: ClipboardPlus, title: "Clinical context", owner: "Clinician-entered", detail: "Age, symptoms, screening history and selected risk context appear in the review report.", boundary: "These fields currently do not alter image-model probabilities or generate a diagnosis." },
] as const;

const INTERPRETATION = [
  ["KOIL morphology positive", "The image crossed the morphology threshold.", "Review image quality and KOIL Grad-CAM; correlate with cytology grade and obtain/consider a separate HPV assay according to the clinical pathway."],
  ["KOIL morphology negative", "No prominent model-detected koilocytotic pattern.", "Does not rule out HPV. Molecular testing and follow-up remain governed by the screening pathway and clinical context."],
  ["Laboratory HPV positive", "A separately reported molecular result.", "Use the laboratory result and applicable guideline for risk stratification; do not treat the KOIL probability as genotype or viral load."],
  ["Symptoms reported", "A report-level safety flag independent of the model result.", "Evaluate symptoms separately. A NILM or low-risk image output must not be used as reassurance for a symptomatic patient."],
] as const;

const ROADMAP = [
  ["Paired cohort", "Thai ThinPrep images paired with the corresponding laboratory HPV assay and patient-level identifiers removed."],
  ["Prespecified endpoints", "HPV positivity, genotype group and persistence defined before analysis; cytology-grade and KOIL endpoints remain separate."],
  ["Patient-level evaluation", "No image, slide or patient leakage between training, calibration and external test partitions."],
  ["Clinical utility", "Calibration, subgroup performance, reader study and prospective workflow evaluation before deployment claims."],
] as const;

export default function HpvContext() {
  return (
    <div className="pb-16">
      <section className="brand-band">
        <div className="mx-auto max-w-6xl px-6 py-14">
          <div className="kicker mb-3">HPV context and claim boundary</div>
          <div className="grid gap-7 lg:grid-cols-[1.25fr_.75fr] lg:items-end">
            <div>
              <h1 className="max-w-4xl font-display text-4xl font-semibold text-ink md:text-5xl">Three evidence streams, kept separate until clinician review</h1>
              <p className="mt-4 max-w-3xl text-base leading-7 text-mut">Persistent high-risk HPV is central to cervical cancer prevention, but cytology morphology and molecular HPV testing are not interchangeable. Anong records their relationship without presenting one as the other.</p>
            </div>
            <div className="flex flex-wrap gap-3 lg:justify-end"><Link href="/analyze" className="inline-flex items-center gap-2 rounded-lg bg-teal px-4 py-2.5 text-sm font-semibold text-white hover:bg-teal-d">Enter clinical context <ArrowRight size={16} aria-hidden /></Link><Link href="/koil" className="rounded-lg border border-line bg-surface px-4 py-2.5 text-sm font-semibold text-ink hover:border-teal">Inspect KOIL evidence</Link></div>
          </div>
        </div>
      </section>

      <main className="mx-auto max-w-6xl px-6">
        <section className="py-12" aria-labelledby="layers-title">
          <div className="kicker mb-2">Evidence model</div><h2 id="layers-title" className="font-display text-3xl font-semibold text-ink">What each input can legitimately say</h2>
          <div className="mt-7 grid gap-4 lg:grid-cols-3">
            {EVIDENCE_LAYERS.map(({ icon: Icon, title, owner, detail, boundary }) => (
              <article key={title} className="rounded-lg border border-line bg-surface p-5">
                <div className="flex items-center justify-between gap-3"><span className="grid h-10 w-10 place-items-center rounded-lg bg-[var(--blush-soft)] text-teal"><Icon size={20} aria-hidden /></span><span className="font-mono text-[10px] uppercase text-mut">{owner}</span></div>
                <h3 className="mt-5 font-display text-xl font-semibold text-ink">{title}</h3><p className="mt-2 text-sm leading-6 text-mut">{detail}</p>
                <div className="mt-4 border-t border-line pt-4 text-xs leading-5 text-mut"><b className="text-ink">Boundary:</b> {boundary}</div>
              </article>
            ))}
          </div>
        </section>

        <section className="grid gap-8 border-y border-line py-12 lg:grid-cols-[.8fr_1.2fr]" aria-labelledby="relationship-title">
          <div>
            <div className="kicker mb-2">Relationship, not equivalence</div><h2 id="relationship-title" className="font-display text-3xl font-semibold text-ink">Why KOIL cannot become “HPV detected”</h2>
            <p className="mt-3 text-sm leading-6 text-mut">Koilocytosis combines perinuclear clearing with nuclear atypia and is associated with productive HPV-related change. However, many molecularly HPV-positive cases do not show a detectable cytologic correlate, while reactive or preparation-related changes may mimic parts of the pattern.</p>
          </div>
          <div className="space-y-3">
            <FlowStep number="01" title="Persistent high-risk HPV" detail="Biological risk factor assessed through an appropriate molecular screening assay." />
            <FlowStep number="02" title="Possible cellular effects" detail="Some infected cells develop recognizable cytopathic morphology; absence of morphology does not exclude infection." />
            <FlowStep number="03" title="Cytology and AI review" detail="The reviewer evaluates cell morphology, with AI suggestion, uncertainty and attention evidence." />
            <FlowStep number="04" title="Integrated clinical decision" detail="The clinician combines cytology, laboratory testing, history and applicable guidance. The AI does not make this decision." />
          </div>
        </section>

        <section className="py-12" aria-labelledby="states-title">
          <div className="kicker mb-2">Report interpretation</div><h2 id="states-title" className="font-display text-3xl font-semibold text-ink">How the current prototype handles common states</h2>
          <div className="mt-6 overflow-x-auto rounded-lg border border-line bg-surface"><table className="w-full min-w-[760px] border-collapse text-left text-sm"><thead className="bg-[var(--blush-soft)]"><tr><th className="p-4 text-ink">Observed state</th><th className="p-4 text-ink">Meaning inside Anong</th><th className="p-4 text-ink">Required interpretation</th></tr></thead><tbody className="divide-y divide-line">{INTERPRETATION.map(([state, meaning, action]) => <tr key={state}><th className="p-4 align-top font-semibold text-ink">{state}</th><td className="p-4 align-top leading-6 text-mut">{meaning}</td><td className="p-4 align-top leading-6 text-mut">{action}</td></tr>)}</tbody></table></div>
        </section>

        <section className="blush-panel rounded-lg border p-6" aria-labelledby="clinical-fields-title">
          <div className="flex items-start gap-3"><FileCheck2 className="mt-1 shrink-0 text-teal" size={22} aria-hidden /><div><h2 id="clinical-fields-title" className="font-display text-2xl font-semibold text-ink">Age, symptoms and HPV results are report context</h2><p className="mt-2 max-w-4xl text-sm leading-6 text-mut">The Analyze page accepts age, specimen type, screening history, symptoms, a separately reported HPV result/genotype, prior abnormal result, immune status and pregnancy. They are included for review safety and documentation, but they do not change the image prediction in the current prototype. Direct identifiers must not be entered.</p></div></div>
          <div className="mt-5 flex flex-wrap gap-3"><Link href="/analyze" className="rounded-lg bg-teal px-4 py-2.5 text-sm font-semibold text-white hover:bg-teal-d">Open Analyze</Link><Link href="/reports" className="rounded-lg border border-line bg-surface px-4 py-2.5 text-sm font-semibold text-ink hover:border-teal">Review report structure</Link></div>
        </section>

        <section className="py-12" aria-labelledby="visual-title">
          <div className="kicker mb-2">Visual reference</div><h2 id="visual-title" className="font-display text-3xl font-semibold text-ink">Expert-labelled KOIL reference cells</h2><p className="mt-3 max-w-4xl text-sm leading-6 text-mut">These CCCID v2 images illustrate the morphology category only. They do not include paired HPV DNA/RNA results and must not be used as visual proof of a molecular diagnosis.</p>
          <div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">{["koil-intermediate-01.jpg", "koil-superficial-01.jpg", "koil-intermediate-03.jpg", "koil-superficial-03.jpg"].map((file, index) => <figure key={file} className="overflow-hidden rounded-lg border border-line bg-surface"><img src={`${BASE}koil-gallery/${file}`} alt={`Expert-labelled KOIL morphology reference ${index + 1}`} className="aspect-square w-full object-cover" loading="lazy" /><figcaption className="p-3 text-xs text-mut">{index % 2 === 0 ? "Intermediate-type" : "Superficial-type"} koilocyte</figcaption></figure>)}</div>
        </section>

        <section className="grid gap-8 border-t border-line py-12 lg:grid-cols-[.72fr_1.28fr]" aria-labelledby="roadmap-title">
          <div><div className="kicker mb-2">Next evidence phase</div><h2 id="roadmap-title" className="font-display text-3xl font-semibold text-ink">What is needed for HPV risk research</h2><p className="mt-3 text-sm leading-6 text-mut">Adding “HPV” to an interface is not validation. A legitimate model requires paired molecular ground truth and a prespecified research protocol.</p></div>
          <ol className="divide-y divide-line border-y border-line">{ROADMAP.map(([title, detail], index) => <li key={title} className="grid gap-2 py-5 sm:grid-cols-[2rem_11rem_1fr]"><span className="font-mono text-sm text-teal">0{index + 1}</span><b className="text-sm text-ink">{title}</b><span className="text-sm leading-6 text-mut">{detail}</span></li>)}</ol>
        </section>

        <section className="butter-panel flex gap-3 rounded-lg border p-5 text-sm leading-6 text-mut"><AlertCircle className="mt-0.5 shrink-0 text-[var(--hsil)]" size={20} aria-hidden /><p><b className="text-ink">Safety statement:</b> No endpoint in this system is an HPV DNA/RNA assay or establishes viral genotype, persistence, infection status, treatment eligibility or a final diagnosis. Clinical management must follow qualified review and the applicable screening guideline.</p></section>

        <section className="mt-10 text-xs leading-6 text-mut" aria-labelledby="hpv-references-title"><div className="flex items-center gap-2"><Dna size={16} className="text-teal" aria-hidden /><h2 id="hpv-references-title" className="font-semibold text-ink">Primary references</h2></div><p className="mt-1"><a className="text-teal underline" href="https://www.who.int/publications/i/item/9789240121744" target="_blank" rel="noreferrer">WHO guideline on HPV DNA genotyping (2026)</a> · <a className="text-teal underline" href="https://www.ncbi.nlm.nih.gov/books/NBK321770/" target="_blank" rel="noreferrer">IARC: Human papillomavirus infection</a> · <a className="text-teal underline" href="https://www.ncbi.nlm.nih.gov/books/NBK568361/" target="_blank" rel="noreferrer">IARC: Cytology-histology correlation</a></p></section>
      </main>
    </div>
  );
}

function FlowStep({ number, title, detail }: { number: string; title: string; detail: string }) {
  return <div className="grid gap-2 rounded-lg border border-line bg-surface p-4 sm:grid-cols-[2.5rem_12rem_1fr]"><span className="font-mono text-sm text-teal">{number}</span><h3 className="font-semibold text-ink">{title}</h3><p className="text-sm leading-6 text-mut">{detail}</p></div>;
}

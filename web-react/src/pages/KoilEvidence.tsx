import { useEffect, useMemo, useState } from "react";
import { Link } from "wouter";
import { AlertTriangle, ArrowRight, CheckCircle2, Microscope, ShieldCheck } from "lucide-react";
import { METRICS } from "@/lib/data";

const BASE = import.meta.env.BASE_URL;

interface KoilReference {
  id: string;
  image: string;
  subtype: string;
  domain: string;
}

interface KoilManifest {
  attribution: string;
  dataset_url: string;
  license: string;
  license_url: string;
  items: KoilReference[];
}

interface ChallengeRow {
  id: string;
  positive: boolean;
  koil_probability: number;
  locked_threshold: number;
}

interface KoilChallenge {
  support_positive: number;
  true_positive: number;
  false_negative: number;
  sensitivity: number;
  sensitivity_wilson_95_ci: { lower: number; upper: number };
  rows: ChallengeRow[];
}

const MORPHOLOGY = [
  ["Perinuclear clearing", "A sharply defined halo or cavitation surrounding the nucleus, interpreted together with nuclear atypia."],
  ["Nuclear enlargement", "An enlarged nucleus relative to a mature squamous cell, rather than halo appearance alone."],
  ["Hyperchromasia and irregularity", "Darker chromatin and an irregular nuclear membrane strengthen a koilocytotic interpretation."],
  ["Bi- or multinucleation", "More than one atypical nucleus may occur, but no single feature is sufficient by itself."],
] as const;

const EVIDENCE = [
  ["Development domain", "SIPaKMeD conventional Pap-smear single-cell crops", "4,049 cells from 966 source clusters"],
  ["Locked internal test", "Source-cluster-disjoint split", "641 cells: 133 KOIL-positive and 508 negative"],
  ["External challenge", "CCCID v2 BD SurePath liquid-based cytology", "20 prespecified expert-labelled positives; no external negatives"],
] as const;

export default function KoilEvidence() {
  const [manifest, setManifest] = useState<KoilManifest | null>(null);
  const [challenge, setChallenge] = useState<KoilChallenge | null>(null);

  useEffect(() => {
    fetch(`${BASE}koil-gallery/index.json`).then((r) => r.json()).then(setManifest).catch(() => setManifest(null));
    fetch(`${BASE}evidence/cccid_koil_20_case_challenge.json`).then((r) => r.json()).then(setChallenge).catch(() => setChallenge(null));
  }, []);

  const examples = useMemo(() => {
    const result = new Map(challenge?.rows.map((row) => [row.id, row]) || []);
    return (manifest?.items || []).slice(0, 8).map((item) => ({ ...item, result: result.get(item.id) }));
  }, [manifest, challenge]);

  const k = METRICS.koil;
  return (
    <div className="pb-16">
      <section className="brand-band">
        <div className="mx-auto grid max-w-6xl gap-8 px-6 py-14 lg:grid-cols-[1.25fr_.75fr] lg:items-end">
          <div>
            <div className="kicker mb-3">Independent morphology endpoint</div>
            <h1 className="max-w-3xl font-display text-4xl font-semibold text-ink md:text-5xl">KOIL evidence, without turning morphology into an HPV test</h1>
            <p className="mt-4 max-w-3xl text-base leading-7 text-mut">
              Anong uses a separate model to flag koilocytotic morphology. This endpoint does not alter the four-class cytology grade and does not detect HPV DNA, HPV RNA, genotype, persistence, or infection status.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link href="/analyze" className="inline-flex items-center gap-2 rounded-lg bg-teal px-4 py-2.5 text-sm font-semibold text-white hover:bg-teal-d">Run the workflow <ArrowRight size={16} aria-hidden /></Link>
              <Link href="/gallery" className="rounded-lg border border-line bg-surface px-4 py-2.5 text-sm font-semibold text-ink hover:border-teal">Open all reference cases</Link>
            </div>
          </div>
          <div className="rounded-lg border border-line bg-surface p-5">
            <div className="flex items-center gap-2 text-sm font-semibold text-ink"><ShieldCheck size={18} className="text-teal" aria-hidden />Claim boundary</div>
            <p className="mt-3 text-sm leading-6 text-mut">A positive result means that image features crossed the locked KOIL morphology threshold. It is evidence for expert review, not molecular confirmation of HPV.</p>
          </div>
        </div>
      </section>

      <main className="mx-auto max-w-6xl px-6">
        <section className="grid border-b border-line py-9 sm:grid-cols-2 lg:grid-cols-4" aria-label="KOIL performance summary">
          <Metric label="Sensitivity" value={k.sensitivity} detail={`95% CI ${k.sensitivityCi}`} />
          <Metric label="Specificity" value={k.specificity} detail={`95% CI ${k.specificityCi}`} />
          <Metric label="AUROC" value={k.auroc} detail="Locked internal test" />
          <Metric label="External positives" value={k.externalDetected} detail={`95% CI ${k.externalSensitivityCi}`} />
        </section>

        <section className="grid gap-10 py-12 lg:grid-cols-[.72fr_1.28fr]" aria-labelledby="morphology-title">
          <div>
            <div className="kicker mb-2">What is reviewed</div>
            <h2 id="morphology-title" className="font-display text-3xl font-semibold text-ink">Koilocytotic morphology is a pattern, not one halo</h2>
            <p className="mt-3 text-sm leading-6 text-mut">Reactive change, glycogen and preparation artefact can resemble perinuclear clearing. The endpoint therefore remains a screening signal that requires expert review.</p>
          </div>
          <div className="divide-y divide-line border-y border-line">
            {MORPHOLOGY.map(([title, detail], index) => (
              <div key={title} className="grid gap-2 py-5 sm:grid-cols-[2rem_12rem_1fr]">
                <span className="font-mono text-sm text-teal">0{index + 1}</span>
                <h3 className="font-semibold text-ink">{title}</h3>
                <p className="text-sm leading-6 text-mut">{detail}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="py-10" aria-labelledby="validation-title">
          <div className="kicker mb-2">Validation ladder</div>
          <h2 id="validation-title" className="font-display text-3xl font-semibold text-ink">What has been tested, and what has not</h2>
          <div className="mt-6 overflow-x-auto rounded-lg border border-line bg-surface">
            <table className="w-full min-w-[680px] border-collapse text-left text-sm">
              <thead className="bg-[var(--blush-soft)] text-ink"><tr><th className="p-4">Evidence stage</th><th className="p-4">Domain</th><th className="p-4">Scope</th></tr></thead>
              <tbody className="divide-y divide-line">{EVIDENCE.map((row) => <tr key={row[0]}><th className="p-4 font-semibold text-ink">{row[0]}</th><td className="p-4 text-mut">{row[1]}</td><td className="p-4 text-mut">{row[2]}</td></tr>)}</tbody>
            </table>
          </div>
          <div className="butter-panel mt-4 flex gap-3 rounded-lg border p-4 text-sm leading-6 text-mut">
            <AlertTriangle className="mt-0.5 shrink-0 text-[var(--hsil)]" size={19} aria-hidden />
            <p><b className="text-ink">External limitation:</b> the CCCID challenge contains positives only. Its 19/20 detection result estimates sensitivity on this small prespecified set; it cannot estimate external specificity, AUROC, calibration, prevalence-adjusted predictive value, or clinical accuracy.</p>
          </div>
        </section>

        <section className="py-12" aria-labelledby="cases-title">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div><div className="kicker mb-2">External positive challenge</div><h2 id="cases-title" className="font-display text-3xl font-semibold text-ink">Prespecified liquid-based reference cells</h2></div>
            <div className="font-mono text-xs text-mut">{challenge ? `${challenge.true_positive}/${challenge.support_positive} detected` : "Loading evidence..."}</div>
          </div>
          <p className="mt-3 max-w-4xl text-sm leading-6 text-mut">These are the first eight of 20 expert-labelled CCCID v2 KOIL-positive center-focus images selected before model inference. They are not patient-level cases and are not a representative screening cohort.</p>
          <div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
            {examples.map((item) => (
              <figure key={item.id} className="overflow-hidden rounded-lg border border-line bg-surface">
                <div className="aspect-square bg-paper"><img src={`${BASE}${item.image}`} alt={`${item.subtype} reference cell ${item.id}`} className="h-full w-full object-cover" loading="lazy" /></div>
                <figcaption className="p-3">
                  <div className="flex items-center justify-between gap-2"><span className="truncate text-xs font-semibold text-ink">{item.id.replace("CCCID-KOIL-", "")}</span>{item.result && <CheckCircle2 size={15} className={item.result.positive ? "text-[var(--nilm)]" : "text-[var(--scc)]"} aria-label={item.result.positive ? "Detected" : "Missed"} />}</div>
                  <div className="mt-1 text-[11px] text-mut">{item.subtype}</div>
                  {item.result && <div className="mt-2 font-mono text-xs text-teal">p={item.result.koil_probability.toFixed(4)}</div>}
                </figcaption>
              </figure>
            ))}
          </div>
          <p className="mt-3 text-[11px] leading-5 text-mut">{manifest?.attribution || "CCCID v2"}. <a href={manifest?.dataset_url} target="_blank" rel="noreferrer" className="text-teal underline">Dataset record</a> · <a href={manifest?.license_url} target="_blank" rel="noreferrer" className="text-teal underline">{manifest?.license || "CC BY-NC 4.0"}</a>.</p>
        </section>

        <section className="grid gap-5 border-t border-line py-12 lg:grid-cols-2">
          <EvidenceFigure src="evidence/koil_test_performance.png" title="Locked-test discrimination" detail="ROC, precision-recall and confusion evidence at the locked threshold." />
          <EvidenceFigure src="evidence/koil_gradcam_paper.png" title="KOIL-specific class activation" detail="Grad-CAM shows regions contributing to the KOIL output. It is not segmentation or causal proof." />
        </section>

        <section className="blush-panel rounded-lg border p-5" aria-labelledby="release-boundary-title">
          <div className="flex items-center gap-2"><Microscope size={20} className="text-teal" aria-hidden /><h2 id="release-boundary-title" className="font-display text-xl font-semibold text-ink">Required before a clinical claim</h2></div>
          <p className="mt-3 text-sm leading-6 text-mut">A negative-inclusive external ThinPrep cohort, paired molecular HPV results, patient-level separation, external calibration, prespecified operating thresholds, blinded reader review and a prospective workflow study remain future validation work.</p>
        </section>

        <section className="mt-10 text-xs leading-6 text-mut" aria-labelledby="references-title">
          <h2 id="references-title" className="font-semibold text-ink">Morphology references</h2>
          <p className="mt-1"><a className="text-teal underline" href="https://www.ncbi.nlm.nih.gov/books/NBK532958/" target="_blank" rel="noreferrer">NCBI Bookshelf: Koilocytosis</a> · <a className="text-teal underline" href="https://www.ncbi.nlm.nih.gov/books/NBK568361/" target="_blank" rel="noreferrer">IARC/NCBI: Cytology-histology correlation</a></p>
        </section>
      </main>
    </div>
  );
}

function Metric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return <div className="border-line px-4 py-3 first:pl-0 sm:border-l sm:first:border-l-0"><div className="text-xs uppercase tracking-wide text-mut">{label}</div><div className="mt-1 font-mono text-2xl font-semibold text-teal">{value}</div><div className="mt-1 text-[11px] text-mut">{detail}</div></div>;
}

function EvidenceFigure({ src, title, detail }: { src: string; title: string; detail: string }) {
  return <figure><div className="overflow-hidden rounded-lg border border-line bg-white"><img src={`${BASE}${src}`} alt={title} className="h-auto w-full" loading="lazy" /></div><figcaption className="mt-3"><h3 className="font-semibold text-ink">{title}</h3><p className="mt-1 text-xs leading-5 text-mut">{detail}</p></figcaption></figure>;
}

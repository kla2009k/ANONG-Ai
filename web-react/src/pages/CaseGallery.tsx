import { useEffect, useMemo, useState } from "react";
import { X, ZoomIn } from "lucide-react";
import { classInfo } from "@/lib/data";

const BASE = import.meta.env.BASE_URL;
const GRADES = ["NILM", "LSIL", "HSIL", "SCC"];

interface LatestCase {
  id: string;
  fold: number;
  group_id: string;
  cell_id: number;
  original: string;
  gradcam: string;
  true_label: string;
  predicted_label: string;
  correct: boolean;
  confidence: number;
  accepted_at_0_60: boolean;
  review_status: "accepted_correct" | "accepted_error" | "abstained";
  probabilities: Record<string, number>;
  cam_target: string;
  cam_method: string;
  cam_disclaimer: string;
}

interface LatestManifest {
  dataset: string;
  model: string;
  protocol: string;
  selective_threshold: number;
  case_selection: string;
  count: number;
  cases: LatestCase[];
}

interface ReferenceCase {
  id: string;
  image: string;
  class: string;
  source_image_id?: number;
  source_cell_id?: number;
  subtype?: string;
  source_doi: string;
  domain: string;
}

interface ReferenceManifest {
  dataset: string;
  dataset_url: string;
  license: string;
  license_url: string;
  attribution: string;
  count: number;
  counts: Record<string, number>;
  items: ReferenceCase[];
}

const STATUS: Record<string, string> = {
  accepted_correct: "Accepted · correct",
  accepted_error: "Accepted · error",
  abstained: "Abstained · human review",
};

const KOIL_FIGURES = [
  { file: "evidence/koil_test_performance.png", title: "KOIL locked-test performance", detail: "Independent SIPaKMeD morphology evidence, not CRIC grade performance or molecular HPV detection." },
  { file: "evidence/koil_calibration.png", title: "KOIL calibration", detail: "Internal locked-test reliability; external negative-inclusive ThinPrep calibration remains required." },
  { file: "evidence/koil_error_gallery.png", title: "KOIL errors", detail: "False positives and false negatives are retained instead of presenting only favorable examples." },
  { file: "evidence/koil_gradcam_paper.png", title: "KOIL Grad-CAM audit", detail: "Post-hoc class activation for the separate KOIL endpoint; not segmentation or proof of HPV infection." },
] as const;

function ProbabilityBars({ probabilities }: { probabilities: Record<string, number> }) {
  return <div className="mt-4 space-y-2">{GRADES.map((grade) => { const value = probabilities[grade] || 0; const info = classInfo(grade); return <div key={grade} className="grid grid-cols-[2.5rem_1fr_3rem] items-center gap-2 text-[10px]"><span className="font-semibold" style={{ color: info.color }}>{grade}</span><div className="h-1.5 overflow-hidden rounded-full bg-line"><div className="h-full rounded-full" style={{ width: `${value * 100}%`, background: info.color }} /></div><span className="text-right font-mono text-mut">{(value * 100).toFixed(1)}%</span></div>; })}</div>;
}

export default function CaseGallery() {
  const [latest, setLatest] = useState<LatestManifest | null>(null);
  const [cric, setCric] = useState<ReferenceManifest | null>(null);
  const [koil, setKoil] = useState<ReferenceManifest | null>(null);
  const [view, setView] = useState<"latest" | "reference" | "koil">("latest");
  const [gradeFilter, setGradeFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [referenceFilter, setReferenceFilter] = useState("ALL");
  const [visibleReferences, setVisibleReferences] = useState(24);
  const [selected, setSelected] = useState<LatestCase | null>(null);

  useEffect(() => {
    fetch(`${BASE}cric-model-gallery/index.json`).then((response) => response.json()).then(setLatest).catch(() => setLatest(null));
    fetch(`${BASE}cric-gallery/index.json`).then((response) => response.json()).then(setCric).catch(() => setCric(null));
    fetch(`${BASE}koil-gallery/index.json`).then((response) => response.json()).then(setKoil).catch(() => setKoil(null));
  }, []);

  useEffect(() => {
    if (!selected) return;
    const close = (event: KeyboardEvent) => { if (event.key === "Escape") setSelected(null); };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [selected]);

  const latestCases = useMemo(() => (latest?.cases || []).filter((item) => (gradeFilter === "ALL" || item.true_label === gradeFilter || item.predicted_label === gradeFilter) && (statusFilter === "ALL" || item.review_status === statusFilter)), [latest, gradeFilter, statusFilter]);
  const references = useMemo(() => {
    const items = [...(cric?.items || []), ...(koil?.items || [])];
    return referenceFilter === "ALL" ? items : items.filter((item) => item.class === referenceFilter);
  }, [cric, koil, referenceFilter]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><div className="kicker mb-2">Case gallery · latest evidence</div><h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Latest CRIC model heatmaps</h1><p className="mt-2 max-w-3xl text-sm leading-6 text-mut">Every default case uses the latest CRIC research checkpoint assigned to that case's held-out fold. Original crops, OOF predictions, and predicted-class Grad-CAM are displayed together.</p></div>
        <div className="rounded-lg border border-line bg-surface p-4"><div className="font-mono text-2xl font-semibold text-teal">{latest?.count ?? "—"}</div><div className="text-xs text-mut">auditable OOF cases · 5 per grade</div></div>
      </div>

      <div className="mt-7 grid gap-2 sm:grid-cols-3" role="tablist" aria-label="Case gallery views">
        {([[
          "latest", "Latest model heatmaps", "CRIC OOF · original + Grad-CAM",
        ], ["reference", "Reference data", "CRIC + CCCID labelled cells"], ["koil", "KOIL evidence", "Separate morphology endpoint"]] as const).map(([key, label, detail]) => <button key={key} type="button" role="tab" aria-selected={view === key} onClick={() => setView(key)} className={`rounded-lg border p-4 text-left ${view === key ? "border-teal bg-teal text-white" : "border-line bg-surface text-ink hover:border-teal"}`}><div className="text-sm font-semibold">{label}</div><div className={`mt-1 text-xs ${view === key ? "text-white/80" : "text-mut"}`}>{detail}</div></button>)}
      </div>

      {view === "latest" && <section className="mt-8" aria-labelledby="latest-gallery-title">
        <div className="flex flex-wrap items-end justify-between gap-3"><div><div className="kicker mb-2">Fold-specific explanations</div><h2 id="latest-gallery-title" className="font-display text-2xl font-semibold text-ink">Correct, incorrect, and abstained cases</h2><p className="mt-2 max-w-4xl text-sm leading-6 text-mut">Selection is fixed per true grade: three accepted correct cases, one accepted error, and one abstained case from different parent images. This prevents a favorable-only gallery.</p></div><div className="font-mono text-xs text-mut">Threshold 0.60 · OOF TTA probabilities</div></div>
        <div className="mt-5 flex flex-wrap gap-2">
          {['ALL', ...GRADES].map((grade) => <button key={grade} type="button" onClick={() => setGradeFilter(grade)} className={`rounded-full border px-3 py-1 text-xs ${gradeFilter === grade ? "border-teal bg-teal text-white" : "border-line text-mut"}`}>{grade}</button>)}
          <span className="mx-1 h-7 border-l border-line" />
          {[['ALL', 'All outcomes'], ['accepted_correct', 'Correct'], ['accepted_error', 'Errors'], ['abstained', 'Abstained']].map(([key, label]) => <button key={key} type="button" onClick={() => setStatusFilter(key)} className={`rounded-full border px-3 py-1 text-xs ${statusFilter === key ? "border-hsil bg-hsil text-white" : "border-line text-mut"}`}>{label}</button>)}
        </div>
        <div className="mt-5 grid gap-5 xl:grid-cols-2">
          {latestCases.map((item) => { const prediction = classInfo(item.predicted_label); const statusColor = item.review_status === "accepted_correct" ? "var(--nilm)" : item.review_status === "accepted_error" ? "var(--scc)" : "var(--hsil)"; return <article key={item.id} className="card overflow-hidden"><div className="grid grid-cols-2 gap-px bg-line"><figure className="bg-surface"><button type="button" onClick={() => setSelected(item)} className="group relative block w-full"><img src={`${BASE}${item.original}`} alt={`${item.id} original CRIC cell, true ${item.true_label}`} loading="lazy" className="aspect-square w-full object-cover" /><ZoomIn size={18} className="absolute bottom-3 right-3 text-white drop-shadow" aria-hidden /></button><figcaption className="border-t border-line px-3 py-2 text-xs font-semibold text-ink">Original · true {item.true_label}</figcaption></figure><figure className="bg-surface"><button type="button" onClick={() => setSelected(item)} className="block w-full"><img src={`${BASE}${item.gradcam}`} alt={`${item.id} latest fold ${item.fold} Grad-CAM targeting ${item.cam_target}`} loading="lazy" className="aspect-square w-full object-cover" /></button><figcaption className="border-t border-line px-3 py-2 text-xs font-semibold text-ink">Grad-CAM · predicted {item.predicted_label}</figcaption></figure></div><div className="p-4"><div className="flex flex-wrap items-start justify-between gap-3"><div><div className="font-mono text-[10px] text-mut">{item.id} · fold {item.fold} · {item.group_id} · cell {item.cell_id}</div><h3 className="mt-1 font-display text-lg font-semibold" style={{ color: prediction.color }}>{prediction.icon} Predicted {item.predicted_label} · {(item.confidence * 100).toFixed(1)}%</h3></div><span className="rounded-full border px-2 py-1 text-[10px] font-semibold" style={{ borderColor: statusColor, color: statusColor }}>{STATUS[item.review_status]}</span></div><ProbabilityBars probabilities={item.probabilities} /><p className="mt-4 border-t border-line pt-3 text-[11px] leading-5 text-mut">{item.cam_method}. {item.cam_disclaimer}</p></div></article>; })}
        </div>
        {!latest && <div className="mt-5 rounded-lg border border-scc/40 p-6 text-sm text-scc">Latest CRIC model manifest could not be loaded.</div>}
      </section>}

      {view === "reference" && <section className="mt-8" aria-labelledby="reference-title"><div className="kicker mb-2">Labelled source material</div><h2 id="reference-title" className="font-display text-2xl font-semibold text-ink">CRIC and CCCID reference cells</h2><p className="mt-2 max-w-4xl text-sm leading-6 text-mut">These are source-label references, not additional independent model validation. CRIC cells come from the same development source as the latest grade model; CCCID supplies KOIL-positive liquid-based references.</p><div className="mt-5 flex flex-wrap gap-2">{['ALL', ...GRADES, 'KOIL'].map((grade) => <button key={grade} type="button" onClick={() => { setReferenceFilter(grade); setVisibleReferences(24); }} className={`rounded-full border px-3 py-1 text-xs ${referenceFilter === grade ? "border-teal bg-teal text-white" : "border-line text-mut"}`}>{grade}</button>)}</div><div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">{references.slice(0, visibleReferences).map((item) => { const info = classInfo(item.class); return <figure key={item.id} className="card overflow-hidden"><img src={`${BASE}${item.image}`} alt={`${item.class} labelled reference ${item.id}`} loading="lazy" className="aspect-square w-full object-cover" /><figcaption className="p-3"><div className="flex justify-between gap-2"><b style={{ color: info.color }}>{info.icon} {item.class}</b><span className="font-mono text-[9px] text-mut">{item.id}</span></div><div className="mt-1 text-[10px] text-mut">{item.subtype || `Source ${item.source_image_id} · cell ${item.source_cell_id}`}</div><a href={`https://doi.org/${item.source_doi}`} target="_blank" rel="noreferrer" className="mt-2 inline-block text-[10px] text-teal underline">Source DOI</a></figcaption></figure>; })}</div>{visibleReferences < references.length && <div className="mt-6 text-center"><button type="button" onClick={() => setVisibleReferences((value) => value + 24)} className="rounded-full border border-teal px-5 py-2 text-sm text-teal">Load more ({references.length - visibleReferences})</button></div>}</section>}

      {view === "koil" && <section className="mt-8" aria-labelledby="koil-title"><div className="kicker mb-2">Independent morphology endpoint</div><h2 id="koil-title" className="font-display text-2xl font-semibold text-ink">KOIL performance and XAI</h2><p className="mt-2 max-w-4xl text-sm leading-6 text-mut">This section remains separate because the SIPaKMeD KOIL model answers a different morphological question. It does not inherit the CRIC 91.7% result and does not detect HPV infection.</p><div className="mt-5 grid gap-5 md:grid-cols-2">{KOIL_FIGURES.map((figure) => <figure key={figure.file} className="card overflow-hidden"><a href={`${BASE}${figure.file}`} target="_blank" rel="noreferrer" className="block bg-white"><img src={`${BASE}${figure.file}`} alt={figure.title} loading="lazy" className="aspect-[16/10] w-full object-contain" /></a><figcaption className="p-4"><h3 className="font-display text-base font-semibold text-ink">{figure.title}</h3><p className="mt-1 text-xs leading-5 text-mut">{figure.detail}</p></figcaption></figure>)}</div></section>}

      {selected && <div className="fixed inset-0 z-[80] grid place-items-center bg-black/75 p-4" role="dialog" aria-modal="true" aria-label={`Latest model case ${selected.id}`} onMouseDown={(event) => { if (event.target === event.currentTarget) setSelected(null); }}><div className="max-h-[94vh] w-full max-w-5xl overflow-y-auto rounded-lg border border-line bg-surface"><div className="flex items-start justify-between border-b border-line p-4"><div><div className="font-mono text-[10px] uppercase text-teal">Latest CRIC OOF · fold {selected.fold}</div><h2 className="font-display text-xl font-semibold text-ink">{selected.id} · {selected.predicted_label} at {(selected.confidence * 100).toFixed(1)}%</h2></div><button type="button" onClick={() => setSelected(null)} className="grid h-9 w-9 place-items-center rounded-lg border border-line text-mut" aria-label="Close viewer"><X size={17} aria-hidden /></button></div><div className="grid gap-px bg-line md:grid-cols-2"><figure className="bg-black p-3"><img src={`${BASE}${selected.original}`} alt={`${selected.id} original enlarged`} className="mx-auto max-h-[72vh] w-full object-contain" /></figure><figure className="bg-black p-3"><img src={`${BASE}${selected.gradcam}`} alt={`${selected.id} Grad-CAM enlarged`} className="mx-auto max-h-[72vh] w-full object-contain" /></figure></div><div className="grid gap-4 p-5 md:grid-cols-2"><div><b className="text-ink">True {selected.true_label} · predicted {selected.predicted_label}</b><ProbabilityBars probabilities={selected.probabilities} /></div><p className="text-xs leading-5 text-mut">The displayed probability is the three-view OOF TTA result. The heatmap is a single-view predicted-class Grad-CAM from the same fold-specific checkpoint. It is post-hoc attention, not segmentation or causal proof.</p></div></div></div>}
    </div>
  );
}

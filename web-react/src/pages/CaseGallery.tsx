import { useEffect, useMemo, useState } from "react";
import { Link } from "wouter";
import { CLASS_KEYS, classInfo } from "@/lib/data";

const BASE = import.meta.env.BASE_URL;

interface GalleryCase {
  id: string;
  image: string;
  gradcam: string;
  true_label: string;
  predicted_label: string;
  correct: boolean;
  confidence: number;
  uncertainty: { level: string; entropy?: number; flag?: boolean };
  error_bucket: string;
  engineering_review_note: string;
  expert_review_status: string;
}

interface ReferenceCase {
  id: string;
  image: string;
  class: string;
  source_label?: string;
  source_image_id?: number;
  source_cell_id?: number;
  subtype?: string;
  source_member?: string;
  focus_plane?: number;
  source_doi: string;
  license: string;
  domain: string;
}

interface ReferenceManifest {
  dataset: string;
  dataset_doi: string;
  dataset_url: string;
  license: string;
  license_url: string;
  attribution: string;
  intended_use: string;
  count: number;
  counts: Record<string, number>;
  items: ReferenceCase[];
}

interface KoilChallenge {
  support_positive: number;
  true_positive: number;
  false_negative: number;
  sensitivity: number;
  sensitivity_wilson_95_ci: { lower: number; upper: number };
  limitation: string;
}

const BUCKET_LABEL: Record<string, string> = {
  correct_reference_sample: "Correct reference",
  severity_overcall: "Severity overcall",
  class_boundary_confusion: "Boundary confusion",
  high_confidence_miss: "High-confidence miss",
};

const EVIDENCE_FIGURES = [
  { file: "evidence/koil_test_performance.png", title: "Locked-test discrimination", detail: "ROC, precision-recall, and locked-threshold confusion evidence for the independent KOIL one-vs-rest endpoint." },
  { file: "evidence/koil_calibration.png", title: "Probability calibration", detail: "Reliability evidence after validation-only temperature scaling; external clinical calibration is still required." },
  { file: "evidence/koil_error_gallery.png", title: "KOIL error gallery", detail: "False positives and false negatives are shown deliberately to expose failure modes rather than cherry-pick favorable cells." },
  { file: "evidence/koil_gradcam_paper.png", title: "KOIL class-activation audit", detail: "Representative class-specific Grad-CAM examples. Attention evidence is not cell segmentation or proof of HPV infection." },
] as const;

export default function CaseGallery() {
  const [cases, setCases] = useState<GalleryCase[]>([]);
  const [cric, setCric] = useState<ReferenceManifest | null>(null);
  const [koil, setKoil] = useState<ReferenceManifest | null>(null);
  const [koilChallenge, setKoilChallenge] = useState<KoilChallenge | null>(null);
  const [section, setSection] = useState<"atlas" | "audit" | "koil">("atlas");
  const [filter, setFilter] = useState("ALL");
  const [atlasFilter, setAtlasFilter] = useState("ALL");
  const [visibleAtlas, setVisibleAtlas] = useState(24);
  const [showCam, setShowCam] = useState<Record<string, boolean>>({});

  useEffect(() => {
    fetch(`${BASE}samples/error_cases.json`).then((r) => r.json()).then(setCases).catch(() => setCases([]));
    fetch(`${BASE}cric-gallery/index.json`).then((r) => r.json()).then(setCric).catch(() => setCric(null));
    fetch(`${BASE}koil-gallery/index.json`).then((r) => r.json()).then(setKoil).catch(() => setKoil(null));
    fetch(`${BASE}evidence/cccid_koil_20_case_challenge.json`).then((r) => r.json()).then(setKoilChallenge).catch(() => setKoilChallenge(null));
  }, []);

  const filtered = useMemo(() => (
    cases.filter((c) => filter === "ALL" || c.true_label === filter || c.predicted_label === filter || c.error_bucket === filter)
  ), [cases, filter]);
  const buckets = Array.from(new Set(cases.map((c) => c.error_bucket)));
  const atlasCases = useMemo(() => {
    const all = [...(cric?.items || []), ...(koil?.items || [])];
    if (atlasFilter !== "ALL") return all.filter((item) => item.class === atlasFilter);
    const classOrder = ["NILM", "LSIL", "HSIL", "SCC", "KOIL"];
    const grouped = Object.fromEntries(classOrder.map((key) => [key, all.filter((item) => item.class === key)]));
    return Array.from({ length: 20 }, (_, index) => classOrder.map((key) => grouped[key][index]).filter(Boolean)).flat();
  }, [cric, koil, atlasFilter]);
  const atlasCount = (cric?.count || 0) + (koil?.count || 0);
  const atlasCounts = { ...(cric?.counts || {}), ...(koil?.counts || {}) };

  function changeAtlasFilter(next: string) {
    setAtlasFilter(next);
    setVisibleAtlas(24);
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-14">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="kicker mb-2">Case gallery</div>
          <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Real-case gallery and error analysis</h1>
          <p className="mt-2 max-w-3xl text-sm text-mut">
            Review Herlev cases processed by the evaluated model, including correct outputs, errors, and high-uncertainty examples. The gallery intentionally avoids cherry-picking only favorable results.
          </p>
        </div>
        <div className="rounded-lg border border-line bg-surface p-4 text-sm">
          <div className="font-mono text-2xl font-semibold text-teal">{atlasCount} + {cases.length || 0}</div>
          <div className="text-xs text-mut">external references + model-audit cases</div>
        </div>
      </div>

      <div className="mt-7 grid gap-2 sm:grid-cols-3" role="tablist" aria-label="Gallery view">
        {([
          ["atlas", "External reference atlas", "100 cells · five morphology categories"],
          ["audit", "Herlev model audit", "Predictions, errors, and Grad-CAM"],
          ["koil", "KOIL evidence", "Performance, calibration, and XAI"],
        ] as const).map(([key, label, detail]) => (
          <button key={key} type="button" role="tab" aria-selected={section === key} onClick={() => setSection(key)}
            className={"rounded-lg border p-4 text-left transition " + (section === key ? "border-teal bg-teal text-white" : "border-line bg-surface text-ink hover:border-teal")}>
            <div className="text-sm font-semibold">{label}</div>
            <div className={"mt-1 text-xs " + (section === key ? "text-white/80" : "text-mut")}>{detail}</div>
          </button>
        ))}
      </div>

      {section === "atlas" && (
        <section className="mt-8" aria-labelledby="cric-atlas-title">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <div className="kicker mb-2">External morphology reference</div>
              <h2 id="cric-atlas-title" className="font-display text-2xl font-semibold text-ink">Open cervical morphology reference atlas</h2>
              <p className="mt-2 max-w-4xl text-sm leading-6 text-mut">
                Twenty real examples per displayed category. NILM, LSIL, HSIL, and SCC come from CRIC; KOIL contains ten superficial-type and ten intermediate-type expert-labelled center-focus images from CCCID liquid-based cytology.
              </p>
            </div>
            <div className="font-mono text-xs text-mut">{atlasCount} cells · 20 per category</div>
          </div>

          <div className="blush-panel mt-4 rounded-lg border p-4 text-xs leading-5 text-mut">
            <b className="text-ink">Attribution:</b> {cric?.attribution || "Rezende et al., CRIC Cervix Cell Classification (2020)"}. Licensed under{" "}
            <a className="text-teal underline" href={cric?.license_url || "https://creativecommons.org/licenses/by/4.0/"} target="_blank" rel="noreferrer">CC BY 4.0</a>.{" "}
            <a className="text-teal underline" href={cric?.dataset_url || "https://figshare.com/collections/CRIC_Cervix_Cell_Classification/4960286"} target="_blank" rel="noreferrer">Official Figshare collection</a>.
            This atlas is external reference material, not an external-validation result and not evidence of HPV infection.
          </div>

          <div className="mt-2 rounded-lg border border-line bg-surface p-4 text-xs leading-5 text-mut">
            <b className="text-ink">KOIL attribution:</b> {koil?.attribution || "Ohno et al., CCCID v2 (2026)"}. Licensed for non-commercial reuse under{" "}
            <a className="text-teal underline" href={koil?.license_url || "https://creativecommons.org/licenses/by-nc/4.0/"} target="_blank" rel="noreferrer">CC BY-NC 4.0</a>.{" "}
            <a className="text-teal underline" href={koil?.dataset_url || "https://zenodo.org/records/20807462"} target="_blank" rel="noreferrer">Official Zenodo record</a>.
            Center-focus plane 5 was selected before inference; these references do not establish HPV infection status.
          </div>

          <div className="mt-5 flex flex-wrap gap-1" role="tablist" aria-label="Filter reference cells">
            {["ALL", "NILM", "LSIL", "HSIL", "SCC", "KOIL"].map((key) => (
              <button key={key} onClick={() => changeAtlasFilter(key)} type="button"
                className={"rounded-full border px-3 py-1 text-xs transition " + (atlasFilter === key ? "border-teal bg-teal text-white" : "border-line text-mut hover:border-teal hover:text-teal")}>
                {key === "ALL" ? `All (${atlasCount})` : `${key} (${atlasCounts[key] || 0})`}
              </button>
            ))}
          </div>

          <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {atlasCases.slice(0, visibleAtlas).map((item) => {
              const info = classInfo(item.class);
              return (
                <figure key={item.id} className="card overflow-hidden">
                  <a href={`${BASE}${item.image}`} target="_blank" rel="noreferrer" className="block bg-paper">
                    <img src={`${BASE}${item.image}`} alt={`${item.class} reference cell ${item.id}`} loading="lazy" width={item.class === "KOIL" ? 384 : 256} height={item.class === "KOIL" ? 384 : 256} className="aspect-square w-full object-cover" />
                  </a>
                  <figcaption className="p-3">
                    <div className="flex items-center justify-between gap-2"><b style={{ color: info.color }}>{info.icon} {item.class}</b><span className="font-mono text-[10px] text-mut">{item.id}</span></div>
                    <div className="mt-1 text-[10px] text-mut">{item.subtype || `Source image ${item.source_image_id} · cell ${item.source_cell_id}`}</div>
                    <a href={`https://doi.org/${item.source_doi}`} target="_blank" rel="noreferrer" className="mt-2 inline-block text-[10px] text-teal underline">Source DOI</a>
                    {item.class === "KOIL" && <Link href={`/analyze?reference=${encodeURIComponent(item.image)}`} className="ml-3 mt-2 inline-block text-[10px] font-semibold text-koil underline">Open in analyzer</Link>}
                  </figcaption>
                </figure>
              );
            })}
          </div>
          {(!cric || !koil) && <div className="mt-5 rounded-lg border border-dashed border-line p-8 text-center text-sm text-mut">One or more reference manifests could not be loaded.</div>}
          {visibleAtlas < atlasCases.length && (
            <div className="mt-6 text-center"><button type="button" onClick={() => setVisibleAtlas((value) => value + 24)} className="rounded-full border border-teal px-5 py-2 text-sm text-teal hover:bg-teal hover:text-white">Load more references ({atlasCases.length - visibleAtlas} remaining)</button></div>
          )}
        </section>
      )}

      {section === "koil" && <section className="mt-8" aria-labelledby="koil-evidence-title">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <div className="kicker mb-2">Independent KOIL evidence</div>
            <h2 id="koil-evidence-title" className="font-display text-2xl font-semibold text-ink">Real SIPaKMeD evaluation figures</h2>
          </div>
          <div className="font-mono text-xs text-mut">4,049 cells · 966 source clusters · locked test n=641</div>
        </div>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-mut">
          These figures were generated from the official SIPaKMeD cropped-cell dataset. It contains 825 koilocytotic cells, but no paired molecular HPV DNA/RNA result. The endpoint therefore validates koilocytotic morphology only, in conventional Pap-smear crops rather than ThinPrep.
        </p>
        {koilChallenge && <div className="mt-4 grid gap-3 sm:grid-cols-4">
          <div className="rounded-lg border border-line bg-surface p-4"><div className="text-[10px] uppercase text-mut">CCCID positives</div><div className="font-mono text-2xl font-semibold text-koil">{koilChallenge.true_positive}/{koilChallenge.support_positive}</div></div>
          <div className="rounded-lg border border-line bg-surface p-4"><div className="text-[10px] uppercase text-mut">Sensitivity</div><div className="font-mono text-2xl font-semibold text-koil">{(koilChallenge.sensitivity * 100).toFixed(1)}%</div></div>
          <div className="rounded-lg border border-line bg-surface p-4"><div className="text-[10px] uppercase text-mut">Wilson 95% CI</div><div className="font-mono text-lg font-semibold text-ink">{(koilChallenge.sensitivity_wilson_95_ci.lower * 100).toFixed(1)}–{(koilChallenge.sensitivity_wilson_95_ci.upper * 100).toFixed(1)}%</div></div>
          <button type="button" onClick={() => { setSection("atlas"); changeAtlasFilter("KOIL"); }} className="rounded-lg border border-koil p-4 text-left text-sm font-semibold text-koil hover:bg-surface">View all 20 KOIL references</button>
          <p className="sm:col-span-4 text-xs leading-5 text-mut"><b className="text-ink">External positive-only challenge:</b> {koilChallenge.limitation} No threshold was tuned on CCCID.</p>
        </div>}
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {EVIDENCE_FIGURES.map((figure) => (
            <figure key={figure.file} className="card overflow-hidden">
              <a href={`${BASE}${figure.file}`} target="_blank" rel="noreferrer" className="block bg-white">
                <img src={`${BASE}${figure.file}`} alt={figure.title} loading="lazy" className="aspect-[16/10] w-full object-contain" />
              </a>
              <figcaption className="p-4"><h3 className="font-display text-base font-semibold text-ink">{figure.title}</h3><p className="mt-1 text-xs leading-5 text-mut">{figure.detail}</p></figcaption>
            </figure>
          ))}
        </div>
      </section>}

      {section === "audit" && <><div className="mt-10 flex flex-wrap gap-1" role="tablist" aria-label="Filter cases">
        {["ALL", ...CLASS_KEYS, ...buckets].map((k) => (
          <button
            key={k}
            onClick={() => setFilter(k)}
            className={"rounded-full border px-3 py-1 text-xs transition " + (filter === k ? "border-teal bg-teal text-white" : "border-line text-mut hover:border-teal hover:text-teal")}
            type="button"
          >
            {BUCKET_LABEL[k] || (k === "ALL" ? "All" : k)}
          </button>
        ))}
      </div>

      <div className="mt-6 grid gap-5 lg:grid-cols-2">
        {filtered.map((item) => {
          const trueInfo = classInfo(item.true_label);
          const predInfo = classInfo(item.predicted_label);
          const cam = showCam[item.id];
          return (
            <article key={item.id} className="card overflow-hidden">
              <div className="grid gap-0 md:grid-cols-[220px_1fr]">
                <div className="relative bg-paper">
                  <img
                    src={`${BASE}${cam ? item.gradcam : item.image}`}
                    alt={cam ? `Grad-CAM for ${item.id}` : `Cytology case ${item.id}`}
                    className="aspect-square h-full w-full object-cover"
                  />
                  <button
                    onClick={() => setShowCam((prev) => ({ ...prev, [item.id]: !prev[item.id] }))}
                    className="absolute right-2 top-2 rounded-full bg-ink/75 px-3 py-1 text-xs text-white"
                    type="button"
                  >
                    {cam ? "Original" : "Grad-CAM"}
                  </button>
                </div>
                <div className="p-5">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="font-mono text-xs text-mut">{item.id}</div>
                      <h2 className="mt-1 font-display text-xl font-semibold text-ink">
                        <span style={{ color: predInfo.color }}>{predInfo.icon} {item.predicted_label}</span>
                        <span className="mx-2 text-mut">vs</span>
                        <span style={{ color: trueInfo.color }}>{trueInfo.icon} {item.true_label}</span>
                      </h2>
                    </div>
                    <span className="rounded-full border px-2 py-1 text-[11px]" style={{ borderColor: item.correct ? "var(--nilm)" : "var(--scc)", color: item.correct ? "var(--nilm)" : "var(--scc)" }}>
                      {item.correct ? "Correct" : "Incorrect"}
                    </span>
                  </div>
                  <div className="mt-4 grid gap-2 sm:grid-cols-3">
                    <div className="rounded-xl border border-line p-3">
                      <div className="text-[10px] uppercase tracking-[.18em] text-mut">Confidence</div>
                      <div className="font-mono text-lg font-semibold text-ink">{Math.round(item.confidence * 100)}%</div>
                    </div>
                    <div className="rounded-xl border border-line p-3">
                      <div className="text-[10px] uppercase tracking-[.18em] text-mut">Uncertainty</div>
                      <div className="font-mono text-lg font-semibold text-ink">{item.uncertainty.level}</div>
                    </div>
                    <div className="rounded-xl border border-line p-3">
                      <div className="text-[10px] uppercase tracking-[.18em] text-mut">Bucket</div>
                      <div className="text-xs font-semibold text-ink">{BUCKET_LABEL[item.error_bucket] || item.error_bucket}</div>
                    </div>
                  </div>
                  <p className="mt-4 text-sm leading-6 text-mut">{item.engineering_review_note}</p>
                  <div className="mt-3 rounded-xl border border-dashed border-line p-3 text-xs text-mut">
                    Expert review status: <b>{item.expert_review_status}</b>. This gallery supports engineering review and demo transparency only; it has not been reviewed by a pathologist.
                  </div>
                </div>
              </div>
            </article>
          );
        })}
        {!filtered.length && (
          <div className="col-span-full rounded-2xl border border-dashed border-line p-12 text-center text-sm text-mut">
            No cases match this filter.
          </div>
        )}
      </div>
      </>}
    </div>
  );
}

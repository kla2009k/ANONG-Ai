import { useEffect, useMemo, useState } from "react";
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

const BUCKET_LABEL: Record<string, string> = {
  correct_reference_sample: "Correct reference",
  severity_overcall: "Severity overcall",
  class_boundary_confusion: "Boundary confusion",
  high_confidence_miss: "High-confidence miss",
};

export default function CaseGallery() {
  const [cases, setCases] = useState<GalleryCase[]>([]);
  const [filter, setFilter] = useState("ALL");
  const [showCam, setShowCam] = useState<Record<string, boolean>>({});

  useEffect(() => {
    fetch(`${BASE}samples/error_cases.json`).then((r) => r.json()).then(setCases).catch(() => setCases([]));
  }, []);

  const filtered = useMemo(() => (
    cases.filter((c) => filter === "ALL" || c.true_label === filter || c.predicted_label === filter || c.error_bucket === filter)
  ), [cases, filter]);
  const buckets = Array.from(new Set(cases.map((c) => c.error_bucket)));

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
        <div className="rounded-2xl border border-line bg-surface p-4 text-sm">
          <div className="font-mono text-2xl font-semibold text-teal">{cases.length || 0}</div>
          <div className="text-xs text-mut">review cases · not pathologist-reviewed</div>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-1" role="tablist" aria-label="Filter cases">
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
    </div>
  );
}

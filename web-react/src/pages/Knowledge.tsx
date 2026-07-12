import { CLASSES } from "@/lib/data";

const GLOSS = [
  ["Sensitivity", "The proportion of truly abnormal cases detected; critical for screening."],
  ["Specificity", "The proportion of truly normal cases correctly identified."],
  ["AUROC / AUPRC", "Discrimination across thresholds; AUPRC is useful with imbalanced classes."],
  ["QWK", "Agreement for ordered categories, making it relevant to Bethesda-style grades."],
  ["Held-out", "A test split the model did not use during training."],
  ["5-fold CV", "Five rotating evaluations so every image is tested in one fold."],
];

export default function Knowledge() {
  return (
    <div className="mx-auto max-w-5xl px-6 py-14">
      <div className="kicker mb-2">Knowledge</div>
      <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Understand the clinical context and system in three minutes</h1>

      <h2 className="mt-10 font-display text-2xl font-semibold text-ink">Bethesda-style cytology categories</h2>
      <div className="mt-4 flex h-2.5 overflow-hidden rounded-full">
        {CLASSES.filter((c) => c.key !== "KOIL").map((c) => <div key={c.key} className="flex-1" style={{ background: c.color }} />)}
      </div>
      <div className="mt-4 grid gap-4 md:grid-cols-4">
        {CLASSES.filter((c) => c.key !== "KOIL").map((c) => (
          <div key={c.key} className="card card-hover p-4" style={{ borderTop: `3px solid ${c.color}` }}>
            <div className="flex items-center gap-1.5 font-mono text-xs" style={{ color: c.color }}>
              <span aria-label={`${c.key} category`} title={c.en}>{c.icon}</span>{c.key}
            </div>
            <div className="font-semibold text-ink">{c.en}</div>
            <p className="mt-1 text-xs text-mut">{c.desc}</p>
            <p className="mt-2 text-xs" style={{ color: c.color }}>{c.triage}</p>
          </div>
        ))}
      </div>

      <div className="mt-10 grid gap-6 md:grid-cols-2">
        <div className="card p-6">
          <h3 className="font-display text-xl font-semibold text-ink">HPV and koilocyte morphology</h3>
          <p className="mt-2 text-sm text-mut">Persistent infection with high-risk HPV is the primary cause of cervical cancer. Cytology may show koilocytic changes such as a perinuclear halo, but microscopy does not detect the virus itself. Confirmatory HPV DNA/RNA testing remains separate.</p>
        </div>
        <div className="card p-6">
          <h3 className="font-display text-xl font-semibold text-ink">Explainability and uncertainty</h3>
          <p className="mt-2 text-sm text-mut"><b className="text-ink">Grad-CAM</b> highlights image regions that influenced the model output. <b className="text-ink">MC Dropout</b> repeats inference to estimate uncertainty; dispersed outputs trigger human review.</p>
        </div>
      </div>

      <div className="card mt-6 p-6">
        <h3 className="font-display text-xl font-semibold text-ink">Key metrics in plain language</h3>
        <div className="mt-3 grid gap-x-8 gap-y-2 text-sm text-mut md:grid-cols-2">
          {GLOSS.map(([t, d]) => <div key={t}><b className="text-ink">{t}</b> — {d}</div>)}
        </div>
      </div>
    </div>
  );
}

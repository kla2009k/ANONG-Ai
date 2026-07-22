import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Database, ExternalLink } from "lucide-react";

const BASE = import.meta.env.BASE_URL;

interface DatasetRecord {
  id: string;
  name: string;
  status: string;
  modality: string;
  available_count: number | null;
  available_parent_count?: number;
  available_instance_count?: number;
  current_use_count: number;
  unit: string;
  current_use: string;
  paired_hpv: string;
  source_url: string;
}

interface DatasetRegistryPayload {
  updated: string;
  current_evidence_sources: number;
  catalogued_sources: number;
  current_model_development_images: number;
  warning: string;
  records: DatasetRecord[];
}

const STATUS_LABEL: Record<string, string> = {
  current_model_development: "Model development",
  external_positive_challenge: "External positive challenge",
  external_reference_atlas: "Reference atlas",
  candidate_only: "Candidate only",
  candidate_restricted: "Restricted candidate",
  candidate_provenance_review: "Provenance review",
  candidate_segmentation: "Segmentation candidate",
  candidate_different_stain: "Different-stain candidate",
  candidate_thinprep: "ThinPrep candidate",
  candidate_different_modality: "Different modality",
};

export default function DatasetRegistry() {
  const [registry, setRegistry] = useState<DatasetRegistryPayload | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [filter, setFilter] = useState<"all" | "current" | "candidate">("all");

  function loadRegistry() {
    setState("loading");
    fetch(`${BASE}evidence/dataset_registry.json`).then((response) => {
      if (!response.ok) throw new Error("Dataset registry unavailable");
      return response.json();
    }).then((data) => { setRegistry(data); setState("ready"); }).catch(() => { setRegistry(null); setState("error"); });
  }

  useEffect(loadRegistry, []);
  const rows = useMemo(() => (registry?.records || []).filter((record) => filter === "all" || (filter === "current" ? record.current_use_count > 0 : record.current_use_count === 0)), [registry, filter]);

  return <div className="mx-auto max-w-6xl px-6 py-14">
    <div className="kicker mb-2">Dataset evidence registry</div>
    <h1 className="max-w-4xl font-display text-4xl font-semibold text-ink">More sources do not mean more training data</h1>
    <p className="mt-3 max-w-4xl text-sm leading-6 text-mut">This registry documents the current model evidence, external references, access constraints and candidate datasets under review. Candidate counts are shown for planning but are never added to current training or validation totals.</p>

    {state === "loading" && <div className="mt-8 grid gap-3 sm:grid-cols-3">{Array.from({ length: 3 }, (_, index) => <div key={index} className="h-28 animate-pulse rounded-lg border border-line bg-surface" />)}</div>}
    {state === "error" && <div className="mt-8 rounded-lg border border-scc/40 p-5 text-sm text-scc" role="alert">Dataset registry could not be loaded. <button onClick={loadRegistry} className="ml-2 font-semibold underline" type="button">Retry</button></div>}
    {registry && <>
      <section className="mt-8 grid border-y border-line py-6 sm:grid-cols-3">
        <RegistryMetric label="Current model-development images" value={registry.current_model_development_images.toLocaleString()} detail="Herlev + SIPaKMeD only" />
        <RegistryMetric label="Current evidence sources" value={String(registry.current_evidence_sources)} detail="Development, challenge, and atlas" />
        <RegistryMetric label="Catalogued sources" value={String(registry.catalogued_sources)} detail="Includes unused candidates" />
      </section>
      <div className="butter-panel mt-6 flex gap-3 rounded-lg border p-4 text-sm leading-6 text-mut"><AlertTriangle className="mt-0.5 shrink-0 text-[var(--hsil)]" size={19} aria-hidden /><p><b className="text-ink">Counting rule:</b> {registry.warning}</p></div>
      <div className="mt-7 flex flex-wrap gap-2" role="group" aria-label="Filter dataset registry">{(["all", "current", "candidate"] as const).map((item) => <button key={item} type="button" onClick={() => setFilter(item)} className={"rounded-lg border px-3 py-1.5 text-xs font-semibold capitalize " + (filter === item ? "border-teal bg-teal text-white" : "border-line text-mut hover:border-teal")}>{item}</button>)}</div>
      <div className="mt-4 overflow-x-auto rounded-lg border border-line bg-surface">
        <table className="w-full min-w-[980px] text-left text-sm"><thead className="bg-[var(--blush-soft)]"><tr><th className="p-4">Dataset</th><th className="p-4">Status</th><th className="p-4">Available at source</th><th className="p-4">Used now</th><th className="p-4">HPV pairing</th><th className="p-4">Scope</th></tr></thead><tbody className="divide-y divide-line">{rows.map((record) => <tr key={record.id}><td className="p-4 align-top"><a href={record.source_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 font-semibold text-teal underline">{record.name}<ExternalLink size={12} aria-hidden /></a><div className="mt-1 max-w-52 text-xs leading-5 text-mut">{record.modality}</div></td><td className="p-4 align-top"><span className={"rounded-full border px-2 py-1 text-[10px] " + (record.current_use_count > 0 ? "border-nilm text-nilm" : "border-line text-mut")}>{STATUS_LABEL[record.status] || record.status}</span></td><td className="p-4 align-top font-mono text-xs text-ink">{record.available_count == null ? "Not summarized" : `${record.available_count.toLocaleString()} ${record.unit}`}{record.available_parent_count ? <div className="mt-1 text-[10px] text-mut">from {record.available_parent_count.toLocaleString()} parent cases/fields</div> : null}{record.available_instance_count ? <div className="mt-1 text-[10px] text-mut">~{record.available_instance_count.toLocaleString()} annotations</div> : null}</td><td className="p-4 align-top font-mono text-xs font-semibold text-ink">{record.current_use_count.toLocaleString()}</td><td className="p-4 align-top text-xs text-mut">{record.paired_hpv.replaceAll("_", " ")}</td><td className="p-4 align-top text-xs leading-5 text-mut">{record.current_use}</td></tr>)}</tbody></table>
      </div>
      <p className="mt-3 text-[11px] text-mut">Registry updated {registry.updated}. Source-page counts describe repositories, not necessarily independent patients or deployable model inputs. Licensing, patient-level separation, label review and domain suitability must be resolved before use.</p>
    </>}
  </div>;
}

function RegistryMetric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return <div className="px-4 py-3 first:pl-0 sm:border-l sm:border-line sm:first:border-l-0"><div className="flex items-center gap-2 text-xs uppercase tracking-wide text-mut"><Database size={14} aria-hidden />{label}</div><div className="mt-2 font-mono text-3xl font-semibold text-teal">{value}</div><div className="mt-1 text-xs text-mut">{detail}</div></div>;
}

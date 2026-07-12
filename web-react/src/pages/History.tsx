import { useEffect, useMemo, useState } from "react";
import { Link } from "wouter";
import { classInfo, CLASS_KEYS } from "@/lib/data";
import { clearAudit, downloadAudit, loadAudit, loadAuditServer, saveAuditServer, type AuditEntry, type SignStatus } from "@/lib/audit";

const STATUS_LABEL: Record<SignStatus, string> = {
  pending: "Pending clinician review",
  confirmed: "Confirmed",
  edited: "Edited",
  rejected: "Slide rejected",
};

export default function History() {
  const [items, setItems] = useState<AuditEntry[]>([]);
  const [filter, setFilter] = useState("ALL");
  const [serverState, setServerState] = useState("Mock server audit has not been connected.");

  useEffect(() => setItems(loadAudit()), []);

  const filtered = useMemo(() => (
    items.filter((i) => filter === "ALL" || i.finalLabel === filter || i.aiTop === filter)
  ), [items, filter]);

  const totals = useMemo(() => {
    const signed = items.filter((i) => i.status === "confirmed" || i.status === "edited").length;
    const edited = items.filter((i) => i.status === "edited").length;
    const highUnc = items.filter((i) => i.uncertainty === "high").length;
    return { signed, edited, highUnc };
  }, [items]);

  function clear() {
    clearAudit();
    setItems([]);
  }

  async function syncServer() {
    setServerState("Synchronizing with the mock server audit...");
    try {
      for (const item of loadAudit()) await saveAuditServer(item);
      const serverItems = await loadAuditServer();
      if (serverItems.length) setItems(serverItems);
      setServerState("Synchronized with the mock server audit.");
    } catch {
      setServerState("Synchronization failed. Start FastAPI on port 8003 before using the mock server audit.");
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-14">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="kicker mb-2">Local audit trail</div>
          <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Analysis and sign-off history</h1>
          <p className="mt-2 max-w-2xl text-sm text-mut">
            This history uses localStorage and can synchronize with a mock server audit for demonstration purposes. It is not a regulated audit log.
          </p>
          <p className="mt-1 text-xs text-mut">{serverState}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={syncServer} className="rounded-full border border-line px-4 py-2 text-sm text-mut hover:border-teal hover:text-teal">Sync mock server</button>
          <button onClick={downloadAudit} className="rounded-full bg-teal px-4 py-2 text-sm font-medium text-white">Export JSON</button>
          <button onClick={clear} className="rounded-full border px-4 py-2 text-sm" style={{ borderColor: "var(--scc)", color: "var(--scc)" }}>Clear history</button>
        </div>
      </div>

      <div className="mt-8 grid gap-3 sm:grid-cols-3">
        <div className="card p-5">
          <div className="font-mono text-3xl font-semibold text-teal">{items.length}</div>
          <div className="mt-1 text-xs text-mut">total audit entries</div>
        </div>
        <div className="card p-5">
          <div className="font-mono text-3xl font-semibold text-nilm">{totals.signed}</div>
          <div className="mt-1 text-xs text-mut">confirmed or edited cases</div>
        </div>
        <div className="card p-5">
          <div className="font-mono text-3xl font-semibold text-hsil">{totals.edited} / {totals.highUnc}</div>
          <div className="mt-1 text-xs text-mut">clinician edits / high uncertainty</div>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-1" role="tablist" aria-label="Filter history by category">
        {["ALL", ...CLASS_KEYS].map((k) => (
          <button
            key={k}
            onClick={() => setFilter(k)}
            className={"rounded-full border px-3 py-1 text-xs transition " + (filter === k ? "border-teal bg-teal text-white" : "border-line text-mut hover:border-teal hover:text-teal")}
            type="button"
          >
            {k === "ALL" ? "All" : k}
          </button>
        ))}
      </div>

      <div className="mt-5 overflow-hidden rounded-2xl border border-line bg-surface">
        {filtered.length ? (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-left text-sm">
              <thead className="border-b border-line text-xs uppercase tracking-[.18em] text-mut">
                <tr>
                  <th className="px-4 py-3">Case</th>
                  <th className="px-4 py-3">Time</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">AI → Final</th>
                  <th className="px-4 py-3">Confidence</th>
                  <th className="px-4 py-3">HPV note</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {filtered.map((item) => {
                  const finalInfo = classInfo(item.finalLabel);
                  return (
                    <tr key={`${item.caseId}-${item.ts}`}>
                      <td className="px-4 py-3 font-mono text-xs text-ink">{item.caseId}</td>
                      <td className="px-4 py-3 text-xs text-mut">{new Date(item.ts).toLocaleString("en-GB")}</td>
                      <td className="px-4 py-3">{STATUS_LABEL[item.status]}</td>
                      <td className="px-4 py-3">
                        <span className="text-mut">{item.aiTop}</span>
                        <span className="mx-2 text-mut">→</span>
                        <b style={{ color: finalInfo.color }}>{finalInfo.icon} {item.finalLabel}</b>
                      </td>
                      <td className="px-4 py-3 font-mono">{Math.round(item.confidence * 100)}% · {item.uncertainty}</td>
                      <td className="px-4 py-3 text-xs text-mut">{item.hpvRisk}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="grid place-items-center px-6 py-16 text-center">
            <div className="text-4xl" aria-hidden>📋</div>
            <h2 className="mt-3 font-display text-xl font-semibold text-ink">No history yet</h2>
            <p className="mt-1 max-w-md text-sm text-mut">Open Analyze, select an example or upload an image, then confirm, edit, or reject the result to create a demo audit entry.</p>
            <Link href="/analyze" className="mt-5 rounded-full bg-teal px-5 py-2 text-sm font-medium text-white">Start analysis</Link>
          </div>
        )}
      </div>
    </div>
  );
}

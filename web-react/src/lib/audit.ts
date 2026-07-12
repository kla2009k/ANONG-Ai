export type SignStatus = "pending" | "confirmed" | "edited" | "rejected";

export interface AuditEntry {
  caseId: string;
  ts: string;
  status: SignStatus;
  aiTop: string;
  finalLabel: string;
  confidence: number;
  uncertainty: string;
  hpvRisk: string;
  source: string;
}

export const AUDIT_KEY = "cervico_audit_trail_v1";

function canonicalHpvRisk(label: string) {
  if (label === "KOIL") return "Consider confirmatory HPV testing";
  if (label === "LSIL") return "May be HPV-related";
  if (label === "HSIL" || label === "SCC") return "High cytology risk";
  return "No prominent HPV-related morphology";
}

function normalizeLegacyEntry(entry: AuditEntry): AuditEntry {
  const containsThai = (value: string) => /[\u0E00-\u0E7F]/.test(value || "");
  const localServer = entry.source?.includes(":8003");
  return {
    ...entry,
    hpvRisk: containsThai(entry.hpvRisk) ? canonicalHpvRisk(entry.finalLabel) : entry.hpvRisk,
    source: containsThai(entry.source)
      ? localServer
        ? "Model output from the local FastAPI server on port 8003."
        : "Real Herlev example processed by the evaluated model (held-out; not used for training)."
      : entry.source,
  };
}

export function loadAudit(): AuditEntry[] {
  try {
    const parsed = JSON.parse(localStorage.getItem(AUDIT_KEY) || "[]");
    return Array.isArray(parsed) ? parsed.map(normalizeLegacyEntry) : [];
  } catch {
    return [];
  }
}

export function saveAudit(entry: AuditEntry) {
  const next = [entry, ...loadAudit()].slice(0, 50);
  localStorage.setItem(AUDIT_KEY, JSON.stringify(next));
  return next;
}

export async function saveAuditServer(entry: AuditEntry) {
  const r = await fetch(API_BASE + "/api/audit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(entry),
  });
  if (!r.ok) throw new Error("audit server");
  return r.json();
}

export async function loadAuditServer(): Promise<AuditEntry[]> {
  const r = await fetch(API_BASE + "/api/audit");
  if (!r.ok) throw new Error("audit server");
  const data = await r.json();
  return (data.entries || []).map(normalizeLegacyEntry);
}

export function clearAudit() {
  localStorage.removeItem(AUDIT_KEY);
}

export function downloadAudit() {
  const blob = new Blob([JSON.stringify(loadAudit(), null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `cervico-audit-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
}
import { API_BASE } from "@/lib/api";

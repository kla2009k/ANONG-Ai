const configured = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
const isLocalHost = location.hostname === "localhost" || location.hostname === "127.0.0.1";
const localBackend = isLocalHost
  ? (location.port === "8003" ? "" : `${location.protocol}//${location.hostname}:8003`)
  : "";

export const API_BASE = configured || localBackend;
export const API_IS_CONFIGURED = Boolean(configured || isLocalHost);

export interface ClinicalContext {
  age_years: number | null;
  symptoms: string[];
  other_symptoms: string;
  specimen_type: "unknown" | "thinprep_lbc" | "conventional_pap";
  last_screening: "unknown" | "never" | "within_3_years" | "3_to_5_years" | "over_5_years";
  hpv_test: "not_performed" | "unknown" | "negative" | "positive";
  hpv_genotype: string;
  prior_abnormal_result: boolean;
  immunocompromised: boolean;
  pregnant: boolean;
}

export async function backendStatus(): Promise<{ available: boolean; ready: boolean; detail: string }> {
  if (!API_IS_CONFIGURED) {
    return { available: false, ready: false, detail: "Static evidence mode: no production analysis API is configured." };
  }
  try {
    const response = await fetch(`${API_BASE}/api/health`, { signal: AbortSignal.timeout(5_000) });
    if (!response.ok) return { available: false, ready: false, detail: `Backend health check returned HTTP ${response.status}.` };
    const health = await response.json();
    const gradeReady = health?.model_status?.grade_mode === "model" || health?.mode === "model";
    const koilReady = health?.model_status?.koil_mode === "model";
    const dualReady = Boolean(gradeReady && koilReady);
    return {
      available: true,
      ready: dualReady,
      detail: dualReady ? "Analysis API connected; trained grade and KOIL models reported active." : "Backend connected, but both trained model endpoints are not ready.",
    };
  } catch {
    return { available: false, ready: false, detail: isLocalHost ? "Local API is offline. Start FastAPI on port 8003." : "The configured analysis API is unreachable." };
  }
}

async function errorDetail(response: Response, fallback: string) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    const body = await response.json().catch(() => ({}));
    if (typeof body.detail === "string") return body.detail;
  }
  return `${fallback} (HTTP ${response.status}).`;
}

export async function createReviewedPdf(payload: {
  case_id: string;
  analysis: Record<string, unknown>;
  review: Record<string, unknown>;
  clinical_context: ClinicalContext;
}): Promise<Blob> {
  if (!API_IS_CONFIGURED) throw new Error("A PDF API is not configured for this static deployment.");
  const reportResponse = await fetch(`${API_BASE}/api/report`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload), signal: AbortSignal.timeout(30_000),
  });
  if (!reportResponse.ok) throw new Error(await errorDetail(reportResponse, "Report generation failed"));
  const report = await reportResponse.json();
  const pdfResponse = await fetch(`${API_BASE}/api/report/export/pdf`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...payload, report }), signal: AbortSignal.timeout(30_000),
  });
  if (!pdfResponse.ok) throw new Error(await errorDetail(pdfResponse, "PDF export failed"));
  return pdfResponse.blob();
}

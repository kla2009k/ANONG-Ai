// CerviCo-Pilot — shared data: Bethesda classes, real metrics, sample types.
import { API_BASE, API_IS_CONFIGURED } from "@/lib/api";

export type Kind = "normal" | "low" | "high" | "cancer" | "hpv";

export interface ClassInfo {
  key: string; en: string; kind: Kind; color: string;
  desc: string; triage: string; icon: string;
}

// Icons accompany color so clinical categories are not communicated by color alone.
export const CLASSES: ClassInfo[] = [
  { key: "NILM", en: "Negative (NILM)", kind: "normal", color: "var(--color-nilm)", icon: "✓",
    desc: "Model result: no abnormal cervical cells identified.", triage: "Repeat screening at the guideline-recommended interval." },
  { key: "LSIL", en: "Low-grade SIL", kind: "low", color: "var(--color-lsil)", icon: "◐",
    desc: "Low-grade cellular changes that may be HPV-related.", triage: "Clinical follow-up; consider HPV testing under applicable guidance." },
  { key: "HSIL", en: "High-grade SIL", kind: "high", color: "var(--color-hsil)", icon: "⚠",
    desc: "High-grade cellular changes requiring prompt specialist review.", triage: "Prompt colposcopy referral according to clinical guidance." },
  { key: "SCC", en: "Squamous Cell Carcinoma", kind: "cancer", color: "var(--color-scc)", icon: "⛔",
    desc: "Cellular features warranting urgent confirmatory assessment.", triage: "Urgent specialist assessment and confirmatory work-up." },
  { key: "KOIL", en: "Koilocyte", kind: "hpv", color: "var(--color-koil)", icon: "◆",
    desc: "Independent koilocytotic-morphology endpoint; not an HPV infection test.", triage: "Expert morphology review and separate HPV testing when clinically indicated." },
];

export const VERSION = { name: "Phase 1.6 dual endpoint", date: "2026-07", model: "EfficientNet-B0 x2" };

export const MODEL_CARD = {
  name: "CerviCo-Pilot — Cervical Cytology Screening Model",
  intendedUse: "Assist medical personnel in screening Pap/ThinPrep-style cervical cytology images to support triage and referral prioritization.",
  users: "Clinicians, pathologists, and cytotechnologists",
  decisionPoint: "Pre-screen triage before confirmatory colposcopy or HPV testing",
  data: "Herlev: 917 images for grade/triage; SIPaKMeD: 4,049 cells from 966 clusters for KOIL training/locked testing; CCCID v2: 20 preselected LBC KOIL positives for a limited external challenge; no Thai-domain validation",
  training: "Separate EfficientNet-B0 models: four-class grade display from the historical Herlev checkpoint and source-cluster-disjoint SIPaKMeD KOIL training",
  doNotUse: [
    "Final diagnosis without qualified clinician review",
    "Replacement for a clinician, pathologist, or cytotechnologist",
    "Detection of HPV infection, DNA, or RNA",
    "Out-of-distribution images without validation and appropriate adaptation",
  ],
  limitations: [
    "KOIL has a 20-positive CCCID liquid-based challenge, but no negative-inclusive external ThinPrep validation",
    "Moderate specificity (about 0.70) may cause over-referral",
    "Post-hoc temperature scaling was evaluated on Herlev only; external Thai calibration is still required",
    "The small public dataset creates domain-shift risk for Thai clinical images",
  ],
};
export const CLASS_KEYS = CLASSES.map((c) => c.key);
export const GRADE_CLASSES = CLASSES.filter((c) => c.key !== "KOIL");
export const GRADE_CLASS_KEYS = GRADE_CLASSES.map((c) => c.key);
export const classInfo = (k: string) => CLASSES.find((c) => c.key === k) ?? CLASSES[0];

export interface Sample {
  id: string; file: string; cam: string; true_label: string; top: string;
  correct: boolean; conf: number; probs: Record<string, number>;
  uncertainty: { entropy: number; std: number; level: string; flag: boolean };
}

// ── honest metrics (best_cervical.pt, real Herlev held-out + 5-fold CV) ──
export const METRICS = {
  dataset: { name: "Herlev (public)", total: 917, test: 137 },
  triage: {
    held: { sensitivity: "1.00", auroc: "0.964", accuracy: "0.927", specificity: "0.722", ci_auroc: "0.925–0.991" },
    cv: { sensitivity: "0.987 ± 0.009", auroc: "0.944 ± 0.045", auprc: "0.976 ± 0.022", specificity: "0.691 ± 0.115", mcc: "0.756 ± 0.092", bacc: "0.839 ± 0.059" },
    highRisk: "100%",
  },
  fiveClass: {
    acc: "0.690 ± 0.062", qwk: "0.698 ± 0.087", recall_hs: "0.686 ± 0.055",
    bacc: "0.701 ± 0.058", mcc: "0.600 ± 0.079", auc: "0.727 ± 0.025",
  },
  cricGrade: {
    dataset: "CRIC Cervix Cell Classification",
    cells: 10003, parents: 395,
    accuracy: "0.8883", accuracyMeanSd: "0.8883 ± 0.0288", accuracyCi: "0.8628–0.9109",
    macroF1: "0.7410", sccRecall: "0.5031", hsilRecall: "0.8467",
    selectiveThreshold: "0.60", selectiveAccuracy: "0.9166", selectiveAccuracyCi: "0.8954–0.9346",
    selectiveCoverage: "0.9408", selectiveCoverageCi: "0.9276–0.9528", accepted: 9411, abstained: 592,
  },
  perClass: [
    { k: "NILM", recall: 0.72 }, { k: "LSIL", recall: 0.61 },
    { k: "HSIL", recall: 0.87 }, { k: "SCC", recall: 0.59 },
  ],
  folds: [
    ["1", "0.587", "0.553", "0.978", "0.861"],
    ["2", "0.701", "0.700", "0.985", "0.952"],
    ["3", "0.667", "0.678", "0.993", "0.940"],
    ["4", "0.727", "0.743", "0.978", "0.978"],
    ["5", "0.771", "0.817", "1.000", "0.986"],
    ["μ ± SD", "0.690±.06", "0.698±.09", "0.987±.01", "0.944±.04"],
  ],
  // numeric per-fold for charts: [acc, qwk, sens, auroc]
  foldNum: [
    { fold: 1, acc: 0.587, qwk: 0.553, sens: 0.978, auroc: 0.861 },
    { fold: 2, acc: 0.701, qwk: 0.700, sens: 0.985, auroc: 0.952 },
    { fold: 3, acc: 0.667, qwk: 0.678, sens: 0.993, auroc: 0.940 },
    { fold: 4, acc: 0.727, qwk: 0.743, sens: 0.978, auroc: 0.978 },
    { fold: 5, acc: 0.771, qwk: 0.817, sens: 1.000, auroc: 0.986 },
  ],
  // Historical matrix storage. The supported grade display uses the first 4x4;
  // KOIL had zero Herlev support and is now evaluated by a separate endpoint.
  confusion: [
    [26, 1, 7, 2, 0],
    [1, 30, 16, 2, 0],
    [1, 0, 26, 3, 0],
    [0, 0, 9, 13, 0],
    [0, 0, 0, 0, 0],
  ],
  binaryConfusion: { TP: 101, TN: 26, FP: 10, FN: 0 },
  koil: {
    dataset: "SIPaKMeD official cropped cells",
    total: 4049, clusters: 966, test: 641, positive: 133, negative: 508,
    sensitivity: "0.9624", sensitivityCi: "0.9167-0.9921",
    specificity: "0.9764", specificityCi: "0.9583-0.9916",
    auroc: "0.9912", auprc: "0.9810", f1: "0.9377", ece: "0.0134",
    multiclassAccuracy: "0.9750", multiclassMacroF1: "0.9753",
    threshold: "0.3367", confusion: { TP: 128, TN: 496, FP: 12, FN: 5 },
    externalDataset: "CCCID v2 BD SurePath liquid-based cytology",
    externalDetected: "19 / 20", externalSensitivity: "0.9500", externalSensitivityCi: "0.7639-0.9911",
  },
};

export async function analyzeReal(imageDataUrl: string) {
  if (!API_IS_CONFIGURED) {
    throw new Error("Uploaded-image analysis is unavailable in this static deployment because no production API is configured. Use a precomputed evidence case or run the local FastAPI server.");
  }
  let r: Response;
  try {
    r = await fetch(API_BASE + "/api/analyze", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imageDataUrl }),
      signal: AbortSignal.timeout(120_000),
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "TimeoutError") {
      throw new Error("Analysis timed out after 120 seconds. Check the backend and GPU status, then try again.");
    }
    throw new Error("The local analysis server is unavailable on port 8003. Start FastAPI or select a precomputed example.");
  }
  if (!r.ok) {
    const body = await r.json().catch(() => ({}));
    const detail = typeof body.detail === "string" ? body.detail : `Analysis failed with HTTP ${r.status}.`;
    throw new Error(detail);
  }
  return r.json();
}

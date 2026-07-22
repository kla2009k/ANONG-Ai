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

export const VERSION = { name: "Phase 1.9 evidence package", date: "2026-07-23", model: "Endpoint-specific EfficientNet-B0 models" };

export const MODEL_CARD = {
  name: "CerviCo-Pilot — Cervical Cytology Screening Model",
  intendedUse: "Assist medical personnel in screening Pap/ThinPrep-style cervical cytology images to support triage and referral prioritization.",
  users: "Clinicians, pathologists, and cytotechnologists",
  decisionPoint: "Pre-screen triage before confirmatory colposcopy or HPV testing",
  data: "Deployed baseline: 917 Herlev grade/triage images. KOIL development: 4,049 SIPaKMeD cells from 966 source clusters; CCCID contributes only a 20-positive external challenge. Separate CRIC research: 10,003 cells from 395 parent images for parent-image-disjoint four-grade evaluation. These are not one combined cohort.",
  training: "The upload workflow retains separate Herlev grade and SIPaKMeD KOIL EfficientNet-B0 checkpoints. A separate CRIC four-grade candidate was evaluated across five parent-image-disjoint folds and is not deployed.",
  doNotUse: [
    "Final diagnosis without qualified clinician review",
    "Replacement for a clinician, pathologist, or cytotechnologist",
    "Detection of HPV infection, DNA, or RNA",
    "Out-of-distribution images without validation and appropriate adaptation",
  ],
  limitations: [
    "KOIL has a 20-positive CCCID liquid-based challenge, but no negative-inclusive external ThinPrep validation",
    "Herlev binary-triage specificity was 69.1% ± 11.5% in five-fold CV, so the deployed screening baseline may over-refer",
    "Post-hoc temperature scaling was evaluated on Herlev only; external Thai calibration is still required",
    "Herlev and CRIC are conventional Pap datasets; APCData testing shows major transfer failure on an external liquid-based domain",
    "CRIC selective grade accuracy is 91.7% at 94.1% coverage, but full-cohort accuracy is 88.8% and SCC recall is 50.3%",
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

// Endpoint-specific measured evidence. These datasets and protocols must never
// be combined into one sample count or a single model-performance claim.
export const METRICS = {
  herlevBaseline: {
    dataset: "Herlev Pap Smear Dataset",
    role: "Deployed upload baseline",
    images: 917,
    heldOut: 137,
    binaryTriage: {
      held: { sensitivity: "100.0%", auroc: "0.964", accuracy: "92.7%", specificity: "72.2%", aurocCi: "0.925–0.991" },
      cv: { sensitivity: "98.7% ± 0.9%", auroc: "0.944 ± 0.045", auprc: "0.976 ± 0.022", specificity: "69.1% ± 11.5%", mcc: "0.756 ± 0.092", balancedAccuracy: "83.9% ± 5.9%" },
    },
    fourGrade: {
      accuracy: "69.0% ± 6.2%",
      qwk: "0.698 ± 0.087",
      highGradeRecall: "0.686 ± 0.055",
    },
  },
  cricGrade: {
    dataset: "CRIC Cervix Cell Classification",
    cells: 10003, parents: 395,
    accuracy: "0.8883", accuracyMeanSd: "0.8883 ± 0.0288", accuracyCi: "0.8619–0.9110",
    macroF1: "0.7410", sccRecall: "0.5031", hsilRecall: "0.8467",
    highGradeCapture: "0.9056", highGradeCaptured: 1688, highGradeSupport: 1864,
    sccHighGradeCapture: "0.9627", sccHighGradeCaptured: 155, sccSupport: 161,
    selectiveThreshold: "0.60", selectiveAccuracy: "0.9166", selectiveAccuracyCi: "0.8960–0.9349",
    selectiveCoverage: "0.9408", selectiveCoverageCi: "0.9278–0.9529", accepted: 9411, abstained: 592,
    classMetrics: {
      NILM: { support: 6779, precision: 0.942466, recall: 0.944830, f1: 0.943646 },
      LSIL: { support: 1360, precision: 0.721386, recall: 0.704412, f1: 0.712798 },
      HSIL: { support: 1703, precision: 0.855786, recall: 0.846741, f1: 0.851240 },
      SCC: { support: 161, precision: 0.417526, recall: 0.503106, f1: 0.456338 },
    },
  },
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

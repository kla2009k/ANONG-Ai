import { useEffect, type ReactNode } from "react";
import { useLocation } from "wouter";
import { Navbar } from "@/components/Navbar";

const META: Record<string, [string, string]> = {
  "/": ["Anong | Explainable Cervical Cytology Screening", "Evidence-oriented cervical cytology screening-support research prototype with XAI, uncertainty, and clinician review."],
  "/analyze": ["Analyze | Anong", "Review four-class cervical cytology grade, independent KOIL morphology, uncertainty, XAI, and report release gates."],
  "/koil": ["KOIL Evidence | Anong", "Inspect locked SIPaKMeD evidence, the CCCID positive challenge, threshold behavior, Grad-CAM, and limitations."],
  "/hpv": ["HPV Context | Anong", "Understand the boundary between cytology morphology, a separate laboratory HPV assay, and clinical context."],
  "/datasets": ["Dataset Registry | Anong", "Trace current model-development data, external references, and unused candidate cervical cytology datasets."],
  "/gallery": ["Case Gallery | Anong", "Inspect real morphology references, model errors, uncertainty, provenance, and KOIL evidence."],
  "/reports": ["Report Evidence | Anong", "Preview clinician and patient report gates and download de-identified PDFs generated from real local model runs."],
};

export function Layout({ children }: { children: ReactNode }) {
  const [location] = useLocation();
  useEffect(() => {
    const [title, description] = META[location] || ["Anong | CerviCo-Pilot", "Cervical cytology screening-support research evidence and workflow."];
    document.title = title;
    const descriptionMeta = document.querySelector('meta[name="description"]');
    descriptionMeta?.setAttribute("content", description);
    let canonical = document.querySelector('link[rel="canonical"]') as HTMLLinkElement | null;
    if (!canonical) {
      canonical = document.createElement("link");
      canonical.rel = "canonical";
      document.head.appendChild(canonical);
    }
    canonical.href = `${window.location.origin}${window.location.pathname}`;
  }, [location]);
  return (
    <div className="relative z-[2] flex min-h-screen flex-col lg:pl-64">
      <Navbar />
      <main className="flex-1">{children}</main>
      <footer className="border-t border-line py-6 text-center text-xs text-mut">
        <span className="font-display font-semibold text-teal">Anong</span> · <span className="font-mono">CerviCo-Pilot</span> · Research decision support · Clinician sign-off required · No HPV DNA/RNA endpoint · Evidence version 2026-07-21
      </footer>
    </div>
  );
}

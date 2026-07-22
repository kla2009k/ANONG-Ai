import { useEffect, type ReactNode } from "react";
import { useLocation } from "wouter";
import { Navbar } from "@/components/Navbar";

const META: Record<string, [string, string]> = {
  "/": ["Anong | Cervical Cytology and HPV-Associated Morphology Risk", "Cervical cytology screening and HPV-associated cytomorphology risk assessment. This research system does not confirm HPV infection."],
  "/analyze": ["Analyze | Anong", "Review cervical cytology grade, independent KOIL morphology, HPV-associated cytomorphology risk, uncertainty, XAI, and report release gates."],
  "/login": ["Reviewer Sign-in | Anong", "Create or delete a local demonstration reviewer profile on this device."],
  "/datasets": ["Dataset Registry | Anong", "Trace current model-development data, external references, and unused candidate cervical cytology datasets."],
  "/gallery": ["Case Gallery | Anong", "Inspect real morphology references, model errors, uncertainty, provenance, and KOIL evidence."],
  "/reports": ["Report Evidence | Anong", "Preview clinician and patient report gates and download de-identified PDFs generated from real local model runs."],
};

export function Layout({ children }: { children: ReactNode }) {
  const [location] = useLocation();
  useEffect(() => {
    const [title, description] = META[location] || ["Anong | CerviCo-Pilot", "Cervical cytology screening and HPV-associated cytomorphology risk assessment; not HPV infection confirmation."];
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
    <div className="relative z-[2] flex min-h-screen min-w-0 flex-col overflow-x-hidden lg:pl-64">
      <Navbar />
      <main className="min-w-0 flex-1">{children}</main>
      <footer className="border-t border-line py-6 text-center text-xs text-mut">
        <span className="font-display font-semibold text-teal">Anong</span> · <span className="font-mono">CerviCo-Pilot</span> · Research decision support · Clinician sign-off required · No HPV DNA/RNA endpoint · Evidence version 2026-07-22
      </footer>
    </div>
  );
}

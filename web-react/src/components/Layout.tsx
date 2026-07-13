import type { ReactNode } from "react";
import { Navbar } from "@/components/Navbar";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="relative z-[2] flex min-h-screen flex-col lg:pl-64">
      <Navbar />
      <main className="flex-1">{children}</main>
      <footer className="border-t border-line py-6 text-center text-xs text-mut">
        <span className="font-display font-semibold text-teal">Anong</span> · <span className="font-mono">CerviCo-Pilot</span> · Decision-support research tool · Clinician sign-off required · Herlev + SIPaKMeD evidence
      </footer>
    </div>
  );
}

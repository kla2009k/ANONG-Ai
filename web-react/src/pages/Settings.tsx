import { useState } from "react";
import { getTheme, applyTheme, type Theme } from "@/lib/theme";

export default function Settings() {
  const [theme, setTheme] = useState<Theme>(getTheme());
  const set = (t: Theme) => { applyTheme(t); setTheme(t); };

  return (
    <div className="mx-auto max-w-3xl px-6 py-14">
      <div className="kicker mb-2">Settings</div>
      <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">System settings</h1>
      <p className="mt-3 text-sm text-mut">Adjust the display theme and review connection details.</p>

      {/* theme */}
      <section className="card mt-8 p-6">
        <h2 className="font-display text-lg font-semibold text-ink">Display theme</h2>
        <p className="mt-1 text-sm text-mut">Choose a light or dark theme. The selection is stored on this device.</p>
        <div className="mt-4 grid grid-cols-2 gap-3">
          {([["light", "☀ Light", "For bright rooms and formal documents"],
             ["dark", "☾ Dark", "For low-light review environments"]] as const).map(([key, label, sub]) => (
            <button key={key} onClick={() => set(key)}
              className={"rounded-xl border p-4 text-left transition " +
                (theme === key ? "border-teal ring-2 ring-teal/30" : "border-line hover:border-teal/50")}>
              <div className="font-medium text-ink">{label}</div>
              <div className="mt-1 text-xs text-mut">{sub}</div>
            </button>
          ))}
        </div>
      </section>

      {/* server */}
      <section className="card mt-5 p-6">
        <h2 className="font-display text-lg font-semibold text-ink">Model connection</h2>
        <div className="mt-3 space-y-2 text-sm text-mut">
          <div className="flex items-center justify-between border-b border-line pb-2">
            <span>FastAPI server (uploaded-image analysis)</span>
            <span className="font-mono text-xs">http://localhost:8003</span>
          </div>
          <div className="flex items-center justify-between border-b border-line pb-2">
            <span>Precomputed real examples (offline)</span>
            <span className="font-mono text-xs text-nilm">Ready ✓</span>
          </div>
          <p className="pt-1 text-xs">Start the server with: <span className="font-mono">cd server &amp;&amp; uvicorn app:app --port 8003</span></p>
        </div>
      </section>

      {/* about/disclaimer */}
      <section className="card mt-5 p-6">
        <h2 className="font-display text-lg font-semibold text-ink">System information</h2>
        <div className="mt-3 grid gap-x-6 gap-y-1.5 text-sm text-mut sm:grid-cols-2">
          <div>Version <span className="font-mono text-ink">Phase 1 POC</span></div>
          <div>Model <span className="font-mono text-ink">EfficientNet-B0</span></div>
          <div>Dataset <span className="font-mono text-ink">Herlev 917</span></div>
          <div>Output <span className="font-mono text-ink">Bethesda 5-class</span></div>
        </div>
        <p className="mt-4 rounded-lg p-3 text-xs leading-relaxed" style={{ background: "color-mix(in srgb, var(--scc) 8%, transparent)", color: "var(--scc)" }}>
          ⚠️ Research decision-support tool. Clinician sign-off is always required. Not a final diagnosis and not an HPV DNA/RNA test.
        </p>
      </section>
    </div>
  );
}

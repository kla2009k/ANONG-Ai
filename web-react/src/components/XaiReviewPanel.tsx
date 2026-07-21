export interface CamDiagnostics {
  valid?: boolean;
  reason?: string;
  std?: number;
  dynamic_range?: number;
  positive_fraction?: number;
}

export interface XaiState {
  ok: boolean;
  provenance: "live" | "precomputed";
  primaryMethod?: string;
  failureReason?: string;
  diagnostics?: Record<string, CamDiagnostics>;
}

interface XaiReviewPanelProps {
  image: string;
  cam?: string;
  camSource?: string;
  activationMap?: string;
  activationCoverage?: number;
  activationThreshold?: number;
  xai: XaiState;
  endpointLabel?: string;
}

function methodLabel(method?: string) {
  if (!method) return "Unavailable";
  return ({
    gradcam: "Grad-CAM",
    "gradcam++": "Grad-CAM++",
    layercam: "Layer-CAM",
    scorecam: "Score-CAM",
  } as Record<string, string>)[method] || method;
}

export function XaiReviewPanel({
  image,
  cam,
  camSource,
  activationMap,
  activationCoverage,
  activationThreshold,
  xai,
  endpointLabel = "Grade endpoint",
}: XaiReviewPanelProps) {
  const [view, setView] = useState<"compare" | "overlay" | "boundary">("compare");
  const [opacity, setOpacity] = useState(70);
  const [zoom, setZoom] = useState(1);
  const hasReliableCam = xai.ok && Boolean(cam);
  const coverage = activationCoverage != null ? activationCoverage * 100 : null;
  const primaryDiagnostics = xai.primaryMethod && xai.diagnostics
    ? xai.diagnostics[xai.primaryMethod]
    : undefined;
  const viewModes: Array<"compare" | "overlay" | "boundary"> = activationMap
    ? ["compare", "overlay", "boundary"]
    : ["compare", "overlay"];

  function downloadExplanation() {
    if (!cam) return;
    const anchor = document.createElement("a");
    anchor.href = cam;
    anchor.download = `${endpointLabel.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-${methodLabel(xai.primaryMethod).toLowerCase()}.png`;
    anchor.click();
  }

  return (
    <section className="rounded-lg border border-line p-3" aria-labelledby="xai-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="font-mono text-[10px] uppercase tracking-[.15em] text-teal">{endpointLabel}</div>
          <h2 id="xai-heading" className="mt-1 font-display text-lg font-semibold text-ink">What the AI focused on</h2>
          <p className="mt-1 max-w-2xl text-xs leading-5 text-mut">
            The source image and explanation use the same uncropped field of view. Warm colors indicate stronger contribution to the selected class.
          </p>
        </div>
        <span className={"rounded-full border px-2.5 py-1 text-[10px] font-medium " + (hasReliableCam ? "border-nilm text-nilm" : "border-scc text-scc")}>
          {hasReliableCam ? (xai.provenance === "precomputed" ? "Precomputed explanation" : "Validated map") : "Explanation unavailable"}
        </span>
      </div>

      {hasReliableCam && (
        <div className="mt-4 flex flex-wrap items-center gap-2 border-y border-line py-3">
          {viewModes.map((mode) => <button key={mode} type="button" onClick={() => setView(mode)} className={"rounded-lg border px-3 py-1.5 text-xs font-semibold capitalize " + (view === mode ? "border-teal bg-teal text-white" : "border-line text-mut hover:border-teal")}>{mode}</button>)}
          <label className="ml-auto flex items-center gap-2 text-xs text-mut"><span>Opacity</span><input type="range" min="10" max="100" value={opacity} onChange={(event) => setOpacity(Number(event.target.value))} disabled={view !== "overlay"} aria-label="Heatmap opacity" className="w-24 accent-[var(--teal)] disabled:opacity-40" /><span className="w-8 font-mono">{opacity}%</span></label>
          <label className="flex items-center gap-2 text-xs text-mut"><ZoomIn size={14} aria-hidden /><input type="range" min="1" max="3" step="0.25" value={zoom} onChange={(event) => setZoom(Number(event.target.value))} aria-label="Image zoom" className="w-20 accent-[var(--teal)]" /></label>
          <button type="button" onClick={() => setZoom(1)} className="grid h-8 w-8 place-items-center rounded-lg border border-line text-mut hover:border-teal" title="Reset zoom" aria-label="Reset image zoom"><RotateCcw size={14} aria-hidden /></button>
          <button type="button" onClick={downloadExplanation} className="grid h-8 w-8 place-items-center rounded-lg border border-line text-mut hover:border-teal" title="Download explanation" aria-label={`Download ${endpointLabel} explanation`}><Download size={14} aria-hidden /></button>
        </div>
      )}

      <div className={"mt-3 grid gap-3 " + (view === "compare" ? "sm:grid-cols-2" : "grid-cols-1")}>
        {view === "overlay" && hasReliableCam ? (
          <figure className="min-w-0">
            <div className="relative mx-auto aspect-square max-w-2xl overflow-auto rounded-lg border border-line bg-paper">
              <img src={image} className="absolute inset-0 h-full w-full object-contain transition-transform" style={{ transform: `scale(${zoom})` }} alt="Analyzed cytology image" />
              <img src={cam} className="absolute inset-0 h-full w-full object-contain transition-transform" style={{ opacity: opacity / 100, transform: `scale(${zoom})` }} alt={`${methodLabel(xai.primaryMethod)} overlay`} />
            </div>
            <figcaption className="mt-1 text-xs font-medium text-ink">Adjustable explanation overlay</figcaption>
          </figure>
        ) : view === "boundary" && activationMap ? (
          <figure className="min-w-0">
            <div className="grid aspect-square max-w-2xl place-items-center overflow-auto rounded-lg border border-line bg-paper p-1">
              <img src={activationMap} className="max-h-full max-w-full object-contain transition-transform" style={{ transform: `scale(${zoom})` }} alt="Thresholded class-activation regions" />
            </div>
            <figcaption className="mt-1 text-xs font-medium text-ink">Activation boundary{coverage != null ? ` · ${coverage.toFixed(1)}% of image` : ""}</figcaption>
          </figure>
        ) : <>
        <figure className="min-w-0">
          <div className="grid aspect-square place-items-center overflow-hidden rounded-lg border border-line bg-paper p-1">
            <img src={image} className="max-h-full max-w-full object-contain transition-transform" style={{ transform: `scale(${zoom})` }} alt="Analyzed cytology image" />
          </div>
          <figcaption className="mt-1 text-xs font-medium text-ink">Original image</figcaption>
        </figure>

        {hasReliableCam ? (
          <figure className="min-w-0">
            <div className="grid aspect-square place-items-center overflow-hidden rounded-lg border border-line bg-paper p-1">
              <img src={cam} className="max-h-full max-w-full object-contain transition-transform" style={{ transform: `scale(${zoom})` }} alt={`${methodLabel(xai.primaryMethod)} heatmap`} />
            </div>
            <figcaption className="mt-1 text-xs font-medium text-ink">{methodLabel(xai.primaryMethod)} heatmap</figcaption>
          </figure>
        ) : (
          <div className="grid aspect-square place-items-center rounded-lg border border-dashed border-scc/50 bg-paper p-5 text-center sm:self-start" role="status">
            <div>
              <div className="font-display font-semibold text-scc">No stable activation map</div>
              <p className="mt-2 text-xs leading-5 text-mut">
                The explanation failed its validity checks. Review the image independently; no fallback visualization is presented as XAI.
              </p>
              {xai.failureReason && <div className="mt-2 font-mono text-[10px] text-mut">{xai.failureReason}</div>}
            </div>
          </div>
        )}

        </>}
      </div>

      {hasReliableCam && (
        <div className="mt-3 rounded-lg bg-paper p-3 text-[11px] leading-5 text-mut">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
            <b className="text-ink">Contribution scale</b>
            <span className="inline-flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-full bg-scc" />Higher</span>
            <span className="inline-flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-full bg-aqua" />Intermediate</span>
            <span className="inline-flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-full bg-navy" />Lower</span>
          </div>
          <p className="mt-1">
            <b className="text-ink">Source:</b> {camSource || methodLabel(xai.primaryMethod)}. The yellow boundary thresholds the strongest class activation; it is not cell or lesion segmentation and is not causal proof.
          </p>
          {xai.provenance === "live" && (
            <details className="mt-2">
              <summary className="cursor-pointer font-medium text-teal">Explanation diagnostics</summary>
              <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 font-mono text-[10px] sm:grid-cols-4">
                <div><dt className="text-mut">Method</dt><dd className="text-ink">{methodLabel(xai.primaryMethod)}</dd></div>
                <div><dt className="text-mut">Map std</dt><dd className="text-ink">{primaryDiagnostics?.std?.toFixed(4) ?? "-"}</dd></div>
                <div><dt className="text-mut">Dynamic range</dt><dd className="text-ink">{primaryDiagnostics?.dynamic_range?.toFixed(4) ?? "-"}</dd></div>
                <div><dt className="text-mut">Threshold</dt><dd className="text-ink">{activationThreshold?.toFixed(4) ?? "-"}</dd></div>
              </dl>
            </details>
          )}
        </div>
      )}
    </section>
  );
}
import { useState } from "react";
import { Download, RotateCcw, ZoomIn } from "lucide-react";

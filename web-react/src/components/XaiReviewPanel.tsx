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
}: XaiReviewPanelProps) {
  const hasReliableCam = xai.ok && Boolean(cam);
  const coverage = activationCoverage != null ? activationCoverage * 100 : null;
  const primaryDiagnostics = xai.primaryMethod && xai.diagnostics
    ? xai.diagnostics[xai.primaryMethod]
    : undefined;

  return (
    <section className="rounded-lg border border-line p-3" aria-labelledby="xai-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="xai-heading" className="font-display text-lg font-semibold text-ink">What the AI focused on</h2>
          <p className="mt-1 max-w-2xl text-xs leading-5 text-mut">
            The source image and explanation use the same uncropped field of view. Warm colors indicate stronger contribution to the selected class.
          </p>
        </div>
        <span className={"rounded-full border px-2.5 py-1 text-[10px] font-medium " + (hasReliableCam ? "border-nilm text-nilm" : "border-scc text-scc")}>
          {hasReliableCam ? (xai.provenance === "precomputed" ? "Precomputed explanation" : "Validated map") : "Explanation unavailable"}
        </span>
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <figure className="min-w-0">
          <div className="grid aspect-square place-items-center overflow-hidden rounded-lg border border-line bg-paper p-1">
            <img src={image} className="max-h-full max-w-full object-contain" alt="Analyzed cytology image" />
          </div>
          <figcaption className="mt-1 text-xs font-medium text-ink">Original image</figcaption>
        </figure>

        {hasReliableCam ? (
          <figure className="min-w-0">
            <div className="grid aspect-square place-items-center overflow-hidden rounded-lg border border-line bg-paper p-1">
              <img src={cam} className="max-h-full max-w-full object-contain" alt={`${methodLabel(xai.primaryMethod)} heatmap`} />
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

        {hasReliableCam && activationMap && coverage != null && coverage > 0 && (
          <figure className="min-w-0">
            <div className="grid aspect-square place-items-center overflow-hidden rounded-lg border border-line bg-paper p-1">
              <img src={activationMap} className="max-h-full max-w-full object-contain" alt="Thresholded class-activation regions" />
            </div>
            <figcaption className="mt-1 text-xs font-medium text-ink">
              Activation boundary · {coverage.toFixed(1)}% of image
            </figcaption>
          </figure>
        )}
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

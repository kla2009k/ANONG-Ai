export default function About() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-14">
      <div className="kicker mb-2">About</div>
      <h1 className="font-display text-4xl font-bold text-ink md:text-5xl">Anong</h1>
      <p className="mt-1 font-display text-lg font-semibold text-teal">CerviCo-Pilot · Cervical Cytology Co-pilot</p>
      <p className="mt-4 text-mut">An explainable AI research project for screening support from ThinPrep/Pap-style cervical cytology images.
        It adds an HPV-related morphology-risk note, Grad-CAM, uncertainty, and clinician sign-off to support transparent review in
        community-hospital and resource-limited settings. It is a <b className="text-ink">decision-support tool</b>, not a replacement for clinical diagnosis.</p>

      <div className="mt-8 grid gap-5 text-sm md:grid-cols-2">
        <div className="card p-5">
          <div className="mb-2 font-semibold text-ink">Datasets</div>
          <ul className="space-y-1 text-mut"><li>· Herlev (917 images — Phase 1)</li><li>· SIPaKMeD / RepoMedUNM (Phase 2 targets)</li></ul>
        </div>
        <div className="card p-5">
          <div className="mb-2 font-semibold text-ink">Technology</div>
          <ul className="space-y-1 text-mut"><li>· EfficientNet-B0 + Grad-CAM + MC Dropout</li><li>· FastAPI + React with an offline-capable static demo</li></ul>
        </div>
      </div>

      <div className="card mt-5 p-5 text-sm">
        <div className="mb-3 font-semibold text-ink">Community-hospital clinical workflow</div>
        <div className="grid gap-3 text-mut md:grid-cols-5">
          <div><b className="text-teal">1</b><br />Upload a ThinPrep/Pap image</div>
          <div><b className="text-teal">2</b><br />Review the 5-class suggestion</div>
          <div><b className="text-teal">3</b><br />Inspect HPV risk + Grad-CAM</div>
          <div><b className="text-teal">4</b><br />Confirm, edit, or reject</div>
          <div><b className="text-teal">5</b><br />Release a reviewed report</div>
        </div>
        <p className="mt-3 text-xs text-mut">
          The goal is to support Bethesda-style grading, communicate HPV-related morphology risk, and strengthen follow-up without replacing a clinician. The binary triage layer accepts some over-referral to prioritize sensitivity. It is not an HPV DNA/RNA test.
        </p>
      </div>

      <div className="card mt-5 p-5 text-sm">
        <div className="mb-3 font-semibold text-ink">Development roadmap</div>
        <div className="grid gap-4 text-mut md:grid-cols-3">
          <div><b className="text-teal">Phase 1 evidence</b><br />Real Herlev data, 5-class output, morphology-risk framing, binary safety triage, XAI, and sign-off ✓</div>
          <div><b className="text-teal">Phase 2 prototype</b><br />Thai ThinPrep data, paired HPV results, KOIL, segmentation, and WSI workflow</div>
          <div><b className="text-teal">Phase 3 validation</b><br />Reader study, external calibration, regulatory/privacy work, and regional expansion</div>
        </div>
      </div>

      <div className="mt-6 text-xs leading-relaxed text-mut">
        References: WHO 90-70-90 (2020) · Hologic Genius FDA 2024 · Bai et al., Nature Communications 2025 · Chansaenroj et al. (2016)<br />
        Disclaimer: Research and education only. Clinician sign-off is required. Not a final diagnosis and not an HPV DNA/RNA test.
      </div>
      <div className="mt-4 font-mono text-xs text-mut">Samsung Solve for Tomorrow · IID 2026 · WSEEC · Academic year 2025/26</div>
    </div>
  );
}

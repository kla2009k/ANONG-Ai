import { useMemo, useState } from "react";

interface Msg { role: "ai" | "user"; text: string }

const QUICK = [
  "Does this replace HPV DNA/RNA testing?",
  "What should happen after an HSIL result?",
  "Why does the system use Grad-CAM?",
  "What does high uncertainty mean?",
];

function answer(q: string) {
  const s = q.toLowerCase();
  if (s.includes("hpv")) {
    return "CerviCo-Pilot does not directly detect HPV infection. Confirming HPV requires a separate molecular DNA/RNA test. This system only describes HPV-related morphology risk from cellular patterns such as LSIL or koilocytic change, followed by clinician review.";
  }
  if (s.includes("hsil") || s.includes("scc")) {
    return "HSIL and SCC are high-risk cytology categories that require prompt specialist review under applicable clinical guidance. This website provides decision support only; a qualified clinician or cytology expert must confirm the result before patient communication.";
  }
  if (s.includes("grad") || s.includes("heat") || s.includes("explain")) {
    return "Grad-CAM highlights image regions that influenced the model output so a clinician can inspect and challenge it. It is not proof that the model understands the biological cause, so it must be interpreted alongside uncertainty and clinician sign-off.";
  }
  if (s.includes("confidence") || s.includes("uncertain") || s.includes("uncertainty")) {
    return "A high-uncertainty case is deferred to independent human review, and the website blocks automatic patient-report release. This safety gate prevents a weak model output from being communicated as if it were clinically confirmed.";
  }
  return "Use this system only as cervical cytology screening support, not as a final diagnosis. The core framing is a 5-class Bethesda-style output, binary safety triage, HPV-related morphology risk, Grad-CAM, uncertainty, and clinician sign-off.";
}

export default function Ask() {
  const [messages, setMessages] = useState<Msg[]>([
    { role: "ai", text: "Ask Anong about CerviCo-Pilot, HPV, ThinPrep, Grad-CAM, uncertainty, or how to explain the project to reviewers. This is a project knowledge assistant, not personal medical advice." },
  ]);
  const [text, setText] = useState("");
  const suggested = useMemo(() => QUICK.filter((q) => !messages.some((m) => m.text.includes(q))).slice(0, 4), [messages]);

  function ask(q = text) {
    const clean = q.trim();
    if (!clean) return;
    setMessages((prev) => [...prev, { role: "user", text: clean }, { role: "ai", text: answer(clean) }]);
    setText("");
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-14">
      <div className="kicker mb-2">Project knowledge</div>
      <h1 className="font-display text-3xl font-semibold text-ink md:text-4xl">Ask Anong</h1>
      <p className="mt-2 max-w-2xl text-sm text-mut">
        A plain-language project assistant grounded in the evidence and safety boundaries: no diagnosis, no clinician replacement, and no claim of HPV DNA/RNA detection.
      </p>

      <div className="blush-panel mt-6 rounded-lg border p-4">
        <div className="max-h-[520px] space-y-3 overflow-y-auto pr-1" role="log" aria-live="polite" aria-label="Conversation with Anong">
          {messages.map((m, i) => (
            <div key={i} className={"flex " + (m.role === "user" ? "justify-end" : "justify-start")}>
              <div className={"max-w-[82%] rounded-lg px-4 py-3 text-sm leading-6 " + (m.role === "user" ? "bg-teal text-white" : "border border-line bg-surface text-ink")}>
                {m.text}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {suggested.map((q) => (
            <button key={q} onClick={() => ask(q)} className="rounded-full border border-line px-3 py-1.5 text-xs text-mut transition hover:border-teal hover:text-teal" type="button">
              {q}
            </button>
          ))}
        </div>

        <form
          className="mt-4 flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            ask();
          }}
        >
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="min-w-0 flex-1 rounded-full border border-line bg-paper px-4 py-3 text-sm text-ink"
            placeholder="Ask a question, for example: Why not just use ChatGPT?"
            aria-label="Question about the project"
          />
          <button className="rounded-full bg-teal px-5 py-3 text-sm font-medium text-white transition hover:bg-teal-d disabled:cursor-not-allowed disabled:opacity-50" type="submit" disabled={!text.trim()}>Send</button>
        </form>
      </div>

      <p className="mt-3 text-xs text-mut">
        Note: This is a rule-based project demo, not a patient-facing medical chatbot.
      </p>
    </div>
  );
}

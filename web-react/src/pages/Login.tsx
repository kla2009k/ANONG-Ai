import { useEffect, useState, type FormEvent } from "react";
import { Link } from "wouter";
import { LockKeyhole, ShieldCheck, Trash2, UserRound } from "lucide-react";
import { clearDemoProfile, loadDemoProfile, saveDemoProfile, type DemoProfile } from "@/lib/session";

const ROLES: DemoProfile["role"][] = ["Clinician", "Cytotechnologist", "Researcher", "Student"];

export default function Login() {
  const [profile, setProfile] = useState<DemoProfile | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [role, setRole] = useState<DemoProfile["role"]>("Clinician");
  const [organization, setOrganization] = useState("");
  const [consent, setConsent] = useState(false);

  useEffect(() => setProfile(loadDemoProfile()), []);

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!displayName.trim() || !consent) return;
    const next = { displayName: displayName.trim(), role, organization: organization.trim(), createdAt: new Date().toISOString() };
    saveDemoProfile(next);
    setProfile(next);
  }

  function remove() {
    clearDemoProfile();
    setProfile(null);
    setDisplayName("");
    setOrganization("");
    setConsent(false);
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-12 md:py-16">
      <div className="grid gap-10 lg:grid-cols-[.85fr_1.15fr] lg:items-start">
        <section>
          <div className="kicker mb-3">Local demo workspace</div>
          <h1 className="font-display text-4xl font-semibold text-ink">Reviewer sign-in</h1>
          <p className="mt-4 text-sm leading-6 text-mut">Create a local reviewer profile for demonstrations on this browser. It identifies the person operating the prototype; it does not authenticate against a hospital identity provider.</p>
          <div className="butter-panel mt-6 rounded-lg border p-4 text-sm leading-6 text-mut">
            <div className="flex items-center gap-2 font-semibold text-ink"><LockKeyhole size={17} aria-hidden />Static deployment boundary</div>
            <p className="mt-2">No password is requested or stored. A production deployment requires server-side authentication, encrypted storage, role-based access, session expiry, consent management and an immutable audit log.</p>
          </div>
          <ul className="mt-6 space-y-3 text-sm text-mut">
            <li className="flex gap-3"><ShieldCheck className="mt-0.5 shrink-0 text-teal" size={18} aria-hidden /><span>Stored only in this browser's localStorage.</span></li>
            <li className="flex gap-3"><ShieldCheck className="mt-0.5 shrink-0 text-teal" size={18} aria-hidden /><span>Do not enter patient names, identifiers, passwords or clinical records.</span></li>
            <li className="flex gap-3"><ShieldCheck className="mt-0.5 shrink-0 text-teal" size={18} aria-hidden /><span>Use the delete control below to remove the profile immediately.</span></li>
          </ul>
        </section>

        <section className="card p-6 md:p-8">
          {profile ? (
            <div>
              <div className="grid h-12 w-12 place-items-center rounded-lg bg-teal text-lg font-semibold text-white"><UserRound size={22} aria-hidden /></div>
              <div className="mt-5 text-xs uppercase tracking-wide text-mut">Signed in on this device</div>
              <h2 className="mt-1 font-display text-2xl font-semibold text-ink">{profile.displayName}</h2>
              <dl className="mt-5 divide-y divide-line border-y border-line text-sm">
                <div className="grid grid-cols-[8rem_1fr] gap-3 py-3"><dt className="text-mut">Role</dt><dd className="font-medium text-ink">{profile.role}</dd></div>
                <div className="grid grid-cols-[8rem_1fr] gap-3 py-3"><dt className="text-mut">Organization</dt><dd className="font-medium text-ink">{profile.organization || "Not entered"}</dd></div>
                <div className="grid grid-cols-[8rem_1fr] gap-3 py-3"><dt className="text-mut">Storage</dt><dd className="font-medium text-ink">Local browser only</dd></div>
              </dl>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link href="/analyze" className="rounded-lg bg-teal px-4 py-2.5 text-sm font-semibold text-white">Open Analyze</Link>
                <button type="button" onClick={remove} className="inline-flex items-center gap-2 rounded-lg border border-scc px-4 py-2.5 text-sm font-semibold text-scc"><Trash2 size={16} aria-hidden />Delete local profile</button>
              </div>
            </div>
          ) : (
            <form onSubmit={submit}>
              <h2 className="font-display text-2xl font-semibold text-ink">Create reviewer profile</h2>
              <div className="mt-6 space-y-4">
                <label className="block text-sm font-medium text-ink">Display name <span className="text-scc">*</span><input required maxLength={80} value={displayName} onChange={(e) => setDisplayName(e.target.value)} className="mt-1.5 w-full rounded-lg border border-line bg-paper px-3 py-2.5 text-ink" autoComplete="name" /></label>
                <label className="block text-sm font-medium text-ink">Professional role<select value={role} onChange={(e) => setRole(e.target.value as DemoProfile["role"])} className="mt-1.5 w-full rounded-lg border border-line bg-paper px-3 py-2.5 text-ink">{ROLES.map((item) => <option key={item}>{item}</option>)}</select></label>
                <label className="block text-sm font-medium text-ink">Organization <span className="font-normal text-mut">(optional)</span><input maxLength={100} value={organization} onChange={(e) => setOrganization(e.target.value)} className="mt-1.5 w-full rounded-lg border border-line bg-paper px-3 py-2.5 text-ink" autoComplete="organization" /></label>
                <label className="flex items-start gap-3 rounded-lg border border-line bg-paper p-3 text-xs leading-5 text-mut"><input required type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} className="mt-1 accent-[var(--teal)]" /><span>I understand this is a local demonstration profile, not secure clinical authentication, and I will not enter patient information.</span></label>
              </div>
              <button type="submit" disabled={!displayName.trim() || !consent} className="mt-6 w-full rounded-lg bg-teal px-4 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50">Continue to local workspace</button>
            </form>
          )}
        </section>
      </div>
    </div>
  );
}

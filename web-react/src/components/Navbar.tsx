import { useEffect, useState } from "react";
import { Link, useLocation } from "wouter";
import {
  BarChart3,
  Home,
  Images,
  Menu,
  Moon,
  ScanLine,
  Sun,
  X,
  UserRound,
  type LucideIcon,
} from "lucide-react";
import { getTheme, toggleTheme } from "@/lib/theme";
import { loadDemoProfile, PROFILE_EVENT, type DemoProfile } from "@/lib/session";

type NavItem = { href: string; label: string; icon: LucideIcon };

const NAV: NavItem[] = [
  { href: "/", label: "Overview", icon: Home },
  { href: "/analyze", label: "Analyze", icon: ScanLine },
  { href: "/gallery", label: "Case Gallery", icon: Images },
  { href: "/performance", label: "Performance", icon: BarChart3 },
];

export function Navbar() {
  const [loc] = useLocation();
  const [dark, setDark] = useState(getTheme() === "dark");
  const [open, setOpen] = useState(false);
  const [profile, setProfile] = useState<DemoProfile | null>(() => loadDemoProfile());
  useEffect(() => {
    const refresh = () => setProfile(loadDemoProfile());
    window.addEventListener(PROFILE_EVENT, refresh);
    window.addEventListener("storage", refresh);
    return () => { window.removeEventListener(PROFILE_EVENT, refresh); window.removeEventListener("storage", refresh); };
  }, []);
  return (
    <>
      <header className="sticky top-0 z-50 border-b border-line bg-surface lg:hidden">
        <div className="flex h-14 items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2" onClick={() => setOpen(false)}>
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-teal text-sm font-bold text-white ring-4 ring-aqua/20">A</span>
            <span className="font-display text-lg font-bold text-ink">Anong</span>
          </Link>
          <button
            onClick={() => setOpen(!open)}
            className="inline-flex items-center gap-2 rounded-lg border border-line bg-paper px-3 py-2 text-sm text-ink transition hover:border-teal"
            aria-expanded={open}
            aria-label={open ? "Close navigation" : "Open navigation"}
            type="button"
          >
            {open ? <X size={17} aria-hidden /> : <Menu size={17} aria-hidden />}
            <span>Menu</span>
          </button>
        </div>
        {open && <NavList loc={loc} dark={dark} setDark={setDark} profile={profile} onNavigate={() => setOpen(false)} mobile />}
      </header>

      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 border-r border-line bg-surface p-4 lg:flex lg:flex-col">
        <Link href="/" className="flex items-center gap-3 px-2 py-3">
          <span className="grid h-11 w-11 place-items-center rounded-lg bg-teal font-display text-xl font-bold text-white ring-4 ring-aqua/20">A</span>
          <span className="min-w-0">
            <span className="block font-display text-xl font-bold text-ink">Anong</span>
            <span className="block font-mono text-[9px] tracking-[.1em] text-mut">CerviCo-Pilot</span>
          </span>
        </Link>
        <NavList loc={loc} dark={dark} setDark={setDark} profile={profile} />
        <div className="butter-panel mt-auto rounded-lg border p-3 text-[11px] leading-5 text-mut">
          <div className="font-semibold text-ink">Phase 1.9 · endpoint-specific evidence</div>
          <div className="mt-1">Herlev upload baseline + SIPaKMeD KOIL + CRIC grade research; not HPV DNA/RNA detection.</div>
        </div>
      </aside>
    </>
  );
}

function NavList({ loc, dark, setDark, profile, onNavigate, mobile = false }: {
  loc: string;
  dark: boolean;
  setDark: (value: boolean) => void;
  profile: DemoProfile | null;
  onNavigate?: () => void;
  mobile?: boolean;
}) {
  return (
    <nav className={mobile ? "grid max-h-[calc(100vh-3.5rem)] content-start gap-0.5 overflow-y-auto border-t border-line bg-surface p-3" : "mt-4 grid min-h-0 flex-1 auto-rows-min content-start gap-0.5 overflow-y-auto pr-1"} aria-label="Primary navigation">
      {NAV.map((n) => {
        const active = loc === n.href;
        const Icon = n.icon;
        return (
          <Link
            key={n.href}
            href={n.href}
            onClick={onNavigate}
            aria-current={active ? "page" : undefined}
            className={"flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition " +
              (active ? "bg-teal text-white" : "text-mut hover:bg-paper hover:text-ink")}
          >
            <span className={"grid h-6 w-6 place-items-center rounded-md " + (active ? "bg-white/20 text-white" : "bg-aqua/25 text-teal")}>
              <Icon size={15} strokeWidth={1.8} aria-hidden />
            </span>
            <span>{n.label}</span>
          </Link>
        );
      })}
      <Link href="/login" onClick={onNavigate} aria-current={loc === "/login" ? "page" : undefined} className={"mt-2 flex items-center gap-3 rounded-lg border px-3 py-2 text-sm transition " + (loc === "/login" ? "border-teal bg-teal text-white" : "border-line text-mut hover:border-teal hover:text-ink")}>
        <UserRound size={16} aria-hidden />
        <span className="min-w-0 flex-1 truncate">{profile ? profile.displayName : "Reviewer sign-in"}</span>
        <span className="text-[9px] uppercase">{profile ? "Local" : "Demo"}</span>
      </Link>
      <button
        onClick={() => setDark(toggleTheme() === "dark")}
        aria-label={dark ? "Use light theme" : "Use dark theme"}
        className="mt-2 flex items-center justify-between rounded-lg border border-line px-3 py-2 text-sm text-mut transition hover:border-teal hover:text-teal"
        type="button"
      >
        <span className="flex items-center gap-3">
          {dark ? <Sun size={16} aria-hidden /> : <Moon size={16} aria-hidden />}
          Theme
        </span>
        <span>{dark ? "Light" : "Dark"}</span>
      </button>
    </nav>
  );
}

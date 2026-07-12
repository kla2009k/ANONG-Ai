export type Theme = "light" | "dark";
const KEY = "cervico-theme";

export function getTheme(): Theme {
  const s = localStorage.getItem(KEY) as Theme | null;
  if (s === "light" || s === "dark") return s;
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function applyTheme(t: Theme) {
  document.documentElement.classList.toggle("dark", t === "dark");
  localStorage.setItem(KEY, t);
}

export function toggleTheme(): Theme {
  const next: Theme = getTheme() === "dark" ? "light" : "dark";
  applyTheme(next);
  return next;
}

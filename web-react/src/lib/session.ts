export interface DemoProfile {
  displayName: string;
  role: "Clinician" | "Cytotechnologist" | "Researcher" | "Student";
  organization: string;
  createdAt: string;
}

const PROFILE_KEY = "anong.demo.profile.v1";
export const PROFILE_EVENT = "anong-profile-change";

export function loadDemoProfile(): DemoProfile | null {
  try {
    const value = localStorage.getItem(PROFILE_KEY);
    if (!value) return null;
    const parsed = JSON.parse(value) as Partial<DemoProfile>;
    if (!parsed.displayName || !parsed.role || !parsed.createdAt) return null;
    return parsed as DemoProfile;
  } catch {
    return null;
  }
}

export function saveDemoProfile(profile: DemoProfile) {
  localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
  window.dispatchEvent(new Event(PROFILE_EVENT));
}

export function clearDemoProfile() {
  localStorage.removeItem(PROFILE_KEY);
  window.dispatchEvent(new Event(PROFILE_EVENT));
}

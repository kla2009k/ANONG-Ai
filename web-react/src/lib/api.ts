const configured = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
const localBackend = location.hostname === "localhost" || location.hostname === "127.0.0.1"
  ? (location.port === "8003" ? "" : `${location.protocol}//${location.hostname}:8003`)
  : "";

export const API_BASE = configured || localBackend;

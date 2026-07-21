import { createRoot } from "react-dom/client";
import { Router } from "wouter";
import App from "./App";
import "./index.css";

const routerBase = import.meta.env.VITE_ROUTER_BASE || undefined;

createRoot(document.getElementById("root")!).render(
  <Router base={routerBase}>
    <App />
  </Router>,
);

if ("serviceWorker" in navigator && import.meta.env.PROD) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register(`${import.meta.env.BASE_URL}sw.js`).catch(() => {
      // Offline support is optional; application behavior must not depend on it.
    });
  });
}

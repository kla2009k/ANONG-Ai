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

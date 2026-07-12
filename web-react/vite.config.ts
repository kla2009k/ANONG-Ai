import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

// Build output goes to ../web so the FastAPI backend serves it (WEB = ROOT/"web").
// In dev, proxy /api to the Python server on :8002.
export default defineConfig({
  base: process.env.VITE_BASE_PATH || "./",
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
  server: {
    port: 5173,
    proxy: { "/api": "http://localhost:8003" },
  },
  build: {
    outDir: path.resolve(__dirname, "../web-dist"),
    emptyOutDir: true,
  },
});

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

// Build output goes to ../web-dist for FastAPI or static deployment.
// In development, proxy /api to the local Python server on :8003.
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

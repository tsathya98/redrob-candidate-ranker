import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

// base: './' so the build works when served from a Hugging Face Space root.
// Dev proxy forwards /api to the FastAPI backend on :8000.
export default defineConfig({
  base: "./",
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": path.resolve(__dirname, "src") } },
  server: {
    proxy: { "/api": "http://localhost:8000" },
  },
});

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// On GitHub Pages the app is served from https://<user>.github.io/<repo>/, so the
// build needs base="/<repo>/". The deploy workflow sets VITE_BASE; local dev/build
// fall back to "/".
export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE ?? "/",
  server: {
    port: 5173
  }
});

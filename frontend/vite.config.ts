import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// On GitHub Pages the app is served from https://<user>.github.io/<repo>/, so the
// build needs base="/<repo>/". The deploy workflow sets VITE_BASE; local dev/build
// fall back to "/".
export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE ?? "/",
  // Ketcher references `global` and `process.env` at runtime. Map global -> window
  // and stub process.env (empty, to avoid inlining the host environment).
  define: {
    "process.env": {},
    global: "window"
  },
  // Ketcher's packages mix ESM and CommonJS. Pre-bundle them in dev, and let the
  // build's CommonJS plugin rewrite `require(...)` found inside ES modules — without
  // this, stray `require` calls survive into the bundle and throw
  // "require is not defined" at runtime (blanking the page).
  optimizeDeps: {
    include: ["ketcher-core", "ketcher-react", "ketcher-standalone"]
  },
  build: {
    commonjsOptions: { transformMixedEsModules: true }
  },
  server: {
    port: 5173
  }
});

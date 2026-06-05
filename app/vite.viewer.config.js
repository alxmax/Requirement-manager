import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));

// Builds viewer.html into ONE self-contained file (JS + CSS inlined) — the
// pre-built template the engine injects per-repo data into. See install-viewer.mjs.
export default defineConfig({
  base: "./",
  plugins: [react(), viteSingleFile()],
  build: {
    outDir: "dist-viewer",
    rollupOptions: { input: resolve(here, "viewer.html") },
  },
});

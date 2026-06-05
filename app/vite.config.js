import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Relative base so the built bundle works when opened from any path
// (e.g. served alongside the engine's requirements/ output, or from a sub-path).
export default defineConfig({
  base: "./",
  plugins: [react()],
});

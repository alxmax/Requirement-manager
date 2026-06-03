/* Copy the built single-file viewer into the plugin so the stdlib engine can
 * ship + inject it. Run by `npm run build:viewer` after the vite build. */
import { copyFileSync, mkdirSync, statSync, readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const appRoot = resolve(here, "..");
const src = resolve(appRoot, "dist-viewer", "viewer.html");
const destDir = resolve(appRoot, "..", "plugin", "scripts");
const dest = resolve(destDir, "_map_viewer.html");

// Sanity: the engine relies on this exact marker to inject data.
const html = readFileSync(src, "utf-8");
if (!html.includes("<!--REQMAP_DATA-->")) {
  console.error("[viewer] ERROR: built file is missing the <!--REQMAP_DATA--> marker — the engine could not inject data.");
  process.exit(1);
}

mkdirSync(destDir, { recursive: true });
copyFileSync(src, dest);
console.log(`[viewer] ${(statSync(src).size / 1024).toFixed(0)} KB`);
console.log(`[viewer] ${src}\n      -> ${dest}`);

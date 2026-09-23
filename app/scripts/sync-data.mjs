// implements: ARCH-VIEWER-007
/* Copy the engine's registry export into the app so it ships with live data.
 *
 *   1. python ../plugin/scripts/reqmap.py export
 *      (writes requirements/_map.json)
 *   2. npm run sync
 *      (this script → public/data.json)
 *
 * Resolves the engine export relative to the repo root, trying the dogfooded
 * plugin/requirements first, then a top-level requirements/. Prints a clear
 * message and exits 0 (non-fatal) when no export is found — the app falls back
 * to its baked dataset.
 *
 * `--require` makes that fallback fatal. The SSR smoke exists to check
 * the viewer against this repo's REAL registry; with the export
 * missing it would silently run against the baked stand-in and report
 * green, so CI passes the flag and a missing export fails loudly
 * there while a local `npm run sync` still falls back. */
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const appRoot = resolve(here, "..");
const repoRoot = resolve(appRoot, "..");

const candidates = [
  resolve(repoRoot, "plugin", "requirements", "_map.json"),
  resolve(repoRoot, "requirements", "_map.json"),
];

const required = process.argv.includes("--require");

const src = candidates.find(existsSync);
if (!src) {
  console.log("[sync] no _map.json found — run `reqmap.py export` first.");
  console.log("[sync] looked in:\n  " + candidates.join("\n  "));
  if (required) {
    console.error(
      "[sync] --require: refusing to fall back to the baked dataset.",
    );
    process.exit(1);
  }
  console.log("[sync] the app will use its baked fallback dataset.");
  process.exit(0);
}

const destDir = resolve(appRoot, "public");
mkdirSync(destDir, { recursive: true });
const dest = resolve(destDir, "data.json");
copyFileSync(src, dest);
console.log(
  `[sync] copied ${src}\n     → ${dest}`,
);

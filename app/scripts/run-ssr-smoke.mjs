/* Bundle ssr-smoke.jsx with esbuild (JSX automatic runtime) and run it. */
import { build } from "esbuild";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const out = resolve(here, ".ssr-smoke.bundle.cjs");

await build({
  entryPoints: [resolve(here, "ssr-smoke.jsx")],
  bundle: true,
  format: "cjs",
  platform: "node",
  jsx: "automatic",
  outfile: out,
  logLevel: "warning",
});

await import(pathToFileURL(out).href);

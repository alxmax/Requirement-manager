// implements: ARCH-VIEWER-007
/* What every part of the render smoke test shares: the real engine export, adopted once,
 * and the `test(label, ok)` helper that counts failures. */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { adoptMapExport, REQ_BY_ID } from "../../src/lib/data.js";
import { adaptNode } from "../../src/lib/loadData.js";
import { SpecDoc } from "../../src/views/SpecDoc.jsx";

// feed the real engine export through the adapter, exactly as the browser would
// (run from the app/ directory: `node scripts/run-ssr-smoke.mjs`)
export const json = JSON.parse(readFileSync(resolve(process.cwd(), "public/data.json"), "utf8"));
adoptMapExport({ nodes: json.nodes.map(adaptNode) });

export const noop = () => {};
// The Spec TAB was removed (Explorer renders the same document beside a richer
// nav); every check below was about the DOCUMENT, so each one renders it directly.
// REQ_BY_ID is a live binding, so this reads whatever fixture was last adopted.
export const specOf = (id) => <SpecDoc r={REQ_BY_ID[id]} onNav={noop} />;

let failures = 0;
export function test(label, ok) {
  console.log(`${ok ? "ok  " : "FAIL"} ${label}`);
  if (!ok) failures++;
}

/** A failure that is not a labelled check, such as a view that threw while rendering. */
export function fail(message) {
  console.error(message);
  failures++;
}

export function finish() {
  console.log(failures ? `\n${failures} failure(s)` : "\nall render checks passed");
  process.exit(failures ? 1 : 0);
}

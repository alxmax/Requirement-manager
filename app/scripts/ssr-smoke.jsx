/* Render-time smoke test: server-render every view against the engine-adapted
 * dataset and assert real content appears. Catches render-throws and bad data
 * assumptions the build cannot. Bundled + run by run-ssr-smoke.mjs. */
import { renderToString } from "react-dom/server";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import App from "../src/App.jsx";
import { setRegistry, REQUIREMENTS } from "../src/lib/data.js";
import { adaptNode } from "../src/lib/loadData.js";
import { MapView } from "../src/views/MapView.jsx";
import { ProblemsView } from "../src/views/ProblemsView.jsx";
import { RoadmapView } from "../src/views/RoadmapView.jsx";
import { SpecView } from "../src/views/SpecView.jsx";

// feed the real engine export through the adapter, exactly as the browser would
// (run from the app/ directory: `node scripts/run-ssr-smoke.mjs`)
const json = JSON.parse(readFileSync(resolve(process.cwd(), "public/data.json"), "utf8"));
setRegistry(json.nodes.map(adaptNode));

const noop = () => {};
const cases = {
  App: <App />,
  MapView: <MapView selId="CORE-PARSE-001" setSelId={noop} openSpec={noop} highlightId={null} setHighlightId={noop} />,
  ProblemsView: <ProblemsView openSpec={noop} />,
  RoadmapView: <RoadmapView openSpec={noop} />,
  SpecView: <SpecView selId="REQ-MAP-007" setSelId={noop} />,
};

let failures = 0;
for (const [name, el] of Object.entries(cases)) {
  try {
    const html = renderToString(el);
    if (html.length < 200) { console.error(`FAIL ${name}: output too short (${html.length})`); failures++; }
    else console.log(`ok   ${name} (${html.length} chars)`);
  } catch (e) {
    console.error(`FAIL ${name}: ${e.message}`); failures++;
  }
}

// content assertions against the live (engine) registry
const appHtml = renderToString(<App />);
const checks = [
  ["registry loaded from engine", REQUIREMENTS.length >= 13],
  ["renders a real capability id", appHtml.includes("CORE-PARSE-001")],
  ["renders the brand", appHtml.includes("Manager")],
  ["renders Problems nav", appHtml.includes("Problems")],
];
for (const [label, ok] of checks) {
  console.log(`${ok ? "ok  " : "FAIL"} ${label}`);
  if (!ok) failures++;
}

// XSS regression: untrusted requirement HTML must render ESCAPED in both
// dangerouslySetInnerHTML sinks (MapView DetailPanel + SpecView), never live.
setRegistry([adaptNode({
  id: "XSS-TEST-001", title: "xss", area: "XSS", layer: "feature", status: "confirmed",
  intent: "i", contract: ['danger <img src=x onerror="boom()">'],
  acc: ['<script>boom()</script>'], members: [], deps: [], used_by: [],
})]);
const xssMap = renderToString(
  <MapView selId="XSS-TEST-001" setSelId={noop} openSpec={noop} highlightId={null} setHighlightId={noop} />);
const xssSpec = renderToString(<SpecView selId="XSS-TEST-001" setSelId={noop} />);
const xssChecks = [
  ["MapView escapes injected contract HTML", xssMap.includes("&lt;img") && !xssMap.includes("<img src=x onerror")],
  ["SpecView escapes injected acceptance HTML", xssSpec.includes("&lt;script&gt;") && !xssSpec.includes("<script>boom")],
];
for (const [label, ok] of xssChecks) {
  console.log(`${ok ? "ok  " : "FAIL"} ${label}`);
  if (!ok) failures++;
}

console.log(failures ? `\n${failures} failure(s)` : "\nall render checks passed");
process.exit(failures ? 1 : 0);

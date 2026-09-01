// tested-by: REQ-VIEWER-007
// tested-by: REQ-SEARCH-036
/* Render-time smoke test: server-render every view against the engine-adapted
 * dataset and assert real content appears. Catches render-throws and bad data
 * assumptions the build cannot. Bundled + run by run-ssr-smoke.mjs. */
import { renderToString } from "react-dom/server";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import App from "../src/App.jsx";
import { rankRequirements } from "../src/lib/search.js";
import { setRegistry, REQUIREMENTS } from "../src/lib/data.js";
import { adaptNode } from "../src/lib/loadData.js";
import { MapView } from "../src/views/MapView.jsx";
import { ProblemsView } from "../src/views/ProblemsView.jsx";
import { RoadmapView } from "../src/views/RoadmapView.jsx";
import { SpecView } from "../src/views/SpecView.jsx";
import { I18nProvider, translate } from "../src/lib/i18n.jsx";
import { computeLayout } from "../src/lib/layout.js";

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
function test(label, ok) {
  console.log(`${ok ? "ok  " : "FAIL"} ${label}`);
  if (!ok) failures++;
}
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
for (const [label, ok] of checks) test(label, ok);

// ranked-search parity (REQ-SEARCH-036): the viewer's search must rank by the
// SAME TF-IDF model as the engine `search` CLI. This golden fixture is asserted
// identically in the Python `Search` tests (class SearchParity) — the query
// scores 0.4112 on REQ-DRIFT-001 in BOTH runtimes, and a no-overlap query floors
// out to nothing. If either runtime drifts from the model, one of these fails.
const SEARCH_FIXTURE = [
  { id: "REQ-DRIFT-001", title: "Drift", intent: "detect divergence",
    contract: ["detect when a contract changes against the lock hash baseline"] },
  { id: "REQ-MAP-002", title: "Map", intent: "diagram",
    contract: ["render mermaid diagrams of the requirement graph"] },
  { id: "REQ-SCAN-003", title: "Scan", intent: "find tags",
    contract: ["walk the code and find implements and tested-by tags in source files"] },
];
const ranked = rankRequirements(SEARCH_FIXTURE, "contract changed against the lock hash");
const nomatch = rankRequirements(SEARCH_FIXTURE, "banana photosynthesis wombat");
const searchChecks = [
  ["ranked search returns the drift requirement first", ranked[0]?.req.id === "REQ-DRIFT-001"],
  ["ranked search score matches the engine (0.4112)", ranked[0] && Math.abs(ranked[0].score - 0.4112) < 1e-4],
  ["ranked search shows a score per hit", typeof ranked[0]?.score === "number"],
  ["ranked search floors out a no-overlap query", nomatch.length === 0],
];
for (const [label, ok] of searchChecks) test(label, ok);

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
for (const [label, ok] of xssChecks) test(label, ok);

// i18n: the toggle must translate UI CHROME and leave requirement content alone.
// Rendered inside the provider with the locale forced, since the provider's own
// initial value comes from localStorage, which does not exist here.
setRegistry(json.nodes.map(adaptNode));
const spec = (locale) => renderToString(
  <I18nProvider initialLocale={locale}>
    <SpecView selId="REQ-MAP-007" setSelId={noop} />
  </I18nProvider>);
const specEn = spec("en"), specRo = spec("ro");
const reqUnderTest = REQUIREMENTS.find(r => r.id === "REQ-MAP-007");
const i18nChecks = [
  ["i18n: English is the default rendering", specEn.includes("Where — Members in code")],
  ["i18n: Romanian translates a section header",
    specRo.includes("Unde — Membri în cod") && !specRo.includes("Where — Members in code")],
  ["i18n: an unknown string falls back to English rather than blanking",
    translate("ro", "Not In The Dictionary") === "Not In The Dictionary"],
  ["i18n: placeholders interpolate", translate("ro", "{n} members bound", { n: 7 }) === "7 membri legați"],
  // The boundary the feature exists to respect: the artifact under review is never translated.
  ["i18n: requirement title stays in the author's language", specRo.includes(reqUnderTest.title)],
  ["i18n: engine vocabulary stays literal (status value, not a translation)",
    specRo.includes(reqUnderTest.status)],
];
for (const [label, ok] of i18nChecks) test(label, ok);

// i18n content translation (opt-in, cached, always marked) — REQ-TRANSLATE-042.
// A node with a cached en-locale translation renders the translated text WITH the
// "machine-translated, unreviewed" badge; a node with no cache entry (the default
// for every requirement until `reqmap.py translate` runs) renders the author's
// text and shows no badge at all — the untranslated path must stay unchanged.
setRegistry([adaptNode({
  id: "I18N-CONTENT-TEST-001", title: "Titlu original", area: "I18N", layer: "feature",
  status: "confirmed", intent: "Motivul original.", contract: ["- Clauza originală."],
  acc: ["- Criteriul original."], members: [], deps: [], used_by: [],
  i18n: { en: { title: "Original title", intent: "The original reason.",
                contract: "- The original clause.", acceptance: "- The original criterion." } },
})]);
const translatedSpecEn = renderToString(
  <I18nProvider initialLocale="en"><SpecView selId="I18N-CONTENT-TEST-001" setSelId={noop} /></I18nProvider>);
const translatedSpecRo = renderToString(
  <I18nProvider initialLocale="ro"><SpecView selId="I18N-CONTENT-TEST-001" setSelId={noop} /></I18nProvider>);
setRegistry([adaptNode({
  id: "I18N-NOCACHE-TEST-001", title: "Titlu fără cache", area: "I18N", layer: "feature",
  status: "confirmed", intent: "Motiv.", contract: ["- Clauză."], acc: ["- Criteriu."],
  members: [], deps: [], used_by: [],
})]);
const noCacheSpecEn = renderToString(
  <I18nProvider initialLocale="en"><SpecView selId="I18N-NOCACHE-TEST-001" setSelId={noop} /></I18nProvider>);
const i18nContentChecks = [
  ["i18n content: cached en translation renders the translated title", translatedSpecEn.includes("Original title")],
  ["i18n content: cached translation shows the machine-translated badge", translatedSpecEn.includes("machine-translated, unreviewed")],
  ["i18n content: no cache entry for ro falls back to the author's title", translatedSpecRo.includes("Titlu original") && !translatedSpecRo.includes("Original title")],
  ["i18n content: no cache entry at all shows no badge", noCacheSpecEn.includes("Titlu f") && !noCacheSpecEn.includes("machine-translated, unreviewed")],
];
for (const [label, ok] of i18nContentChecks) test(label, ok);
// ---- acceptance criteria keep their Given/When/Then lines ------------------
// The engine emits BOTH `accept` (the raw labelled Gherkin block) and `acc` (the
// same criteria folded to one line each, for search and counting). `gwt` used to be
// set only when `acc` was empty — true for every requirement until the engine
// learned to parse the block form (v2.29.0), and false for every one after, which
// silently turned every criterion into a single run-on line.
const GWT_ACCEPT = "AC-1\n  Given  a repo with no requirements/\n  When   `init` runs\n  Then   it creates the directory";
setRegistry([adaptNode({
  id: "GWT-TEST-001", title: "Acceptance block", area: "GWT", layer: "feature",
  status: "confirmed", intent: "Reason.", contract: ["- A clause."],
  acc: ["AC-1 — Given  a repo with no requirements/ When   `init` runs Then   it creates the directory"],
  accept: GWT_ACCEPT, members: [], deps: [], used_by: [],
})]);
const gwtSpec = renderToString(<SpecView selId="GWT-TEST-001" setSelId={noop} />);
const gwtChecks = [
  ["acceptance: a labelled block renders as the multi-line gwt block, not a folded bullet",
    gwtSpec.includes('class="gwt"')],
  ["acceptance: the folded one-line form is not what the reader sees",
    gwtSpec.includes("Given") && gwtSpec.includes("Then")
    && !gwtSpec.includes("AC-1 — Given")],
  ["acceptance: adaptNode still exposes acc for search and counting",
    adaptNode({ id: "X", acc: ["AC-1 — a"], accept: GWT_ACCEPT }).acc.length === 1],
];
for (const [label, ok] of gwtChecks) test(label, ok);
// ---- layout on a CYCLIC registry -------------------------------------------
// A `depends_on` cycle is a modelling error the gate reports, but the viewer still
// has to draw the registry. Longest-path ranking never converges on a cycle: it
// ran its full pass budget and returned maxRank 236 for a real 59-node corpus
// (a DAG of 59 cannot exceed 58), i.e. a 71,000px canvas of empty columns.
const cyc = [
  { id: "A-1", deps: ["B-2"] },
  { id: "B-2", deps: ["C-3"] },
  { id: "C-3", deps: ["A-1"] },          // closes the cycle
  { id: "D-4", deps: ["A-1"] },
];
const cycLayout = computeLayout(cyc);
const cycMaxRank = Math.max(...Object.values(cycLayout.rankOf));
const chain = Array.from({ length: 12 }, (_, i) => ({
  id: `L-${i}`, deps: i < 11 ? [`L-${i + 1}`] : [],       // an honest 12-deep DAG
}));
const chainMaxRank = Math.max(...Object.values(computeLayout(chain).rankOf));
const layoutChecks = [
  ["layout: a cycle cannot rank beyond the node count", cycMaxRank <= cyc.length - 1],
  ["layout: a cyclic graph stays in a bounded canvas", cycLayout.width < 2000],
  ["layout: every node still gets a position", cyc.every((r) => cycLayout.pos[r.id])],
  ["layout: cycle-closing edges are still drawn", cycLayout.edges.length === 4],
  ["layout: a deep DAG still ranks by longest path", chainMaxRank === 11],
];
for (const [label, ok] of layoutChecks) test(label, ok);

setRegistry(json.nodes.map(adaptNode));   // restore the real dataset for anything after this point

console.log(failures ? `\n${failures} failure(s)` : "\nall render checks passed");
process.exit(failures ? 1 : 0);

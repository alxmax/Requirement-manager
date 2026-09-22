// tested-by: REQ-TRANSLATE-938  // tested-by: REQ-VIEWER-942  // tested-by: REQ-VIEWER-943
// tested-by: ARCH-VIEWER-007
// tested-by: REQ-VIEWER-944  // tested-by: REQ-VIEWER-945  // tested-by: REQ-VIEWER-966
// tested-by: ARCH-SEARCH-036
// tested-by: REQ-SEARCH-965  // tested-by: REQ-VIEWER-969
// tested-by: REQ-VIEWER-964
// tested-by: REQ-VIEWER-984  // tested-by: REQ-VIEWER-995  // tested-by: REQ-TRANSLATE-996
// tested-by: REQ-VIEWER-999  // tested-by: REQ-PLANCADENCE-1000
// tested-by: REQ-HISTORY-1003
/* Render smoke test, part: every view renders; spec document; acceptance; layout. */
import { renderToString } from "react-dom/server";

import App from "../../src/App.jsx";
import { rankRequirements, searchRequirements } from "../../src/lib/search.js";
import { adoptMapExport, REQUIREMENTS, ROADMAP, HISTORY, TARGETS } from "../../src/lib/data.js";
import { adaptNode, loadData } from "../../src/lib/loadData.js";
import { MapView } from "../../src/views/MapView.jsx";
import { ProblemsView, computeProblems, computeQuestions } from "../../src/views/ProblemsView.jsx";
import { RoadmapView } from "../../src/views/RoadmapView.jsx";
import {
  PlanGantt, noteText, matchItem, ShippedNote, VersionNote,
} from "../../src/views/roadmap/PlanGantt.jsx";
import { stackBars, buildDayBands } from "../../src/lib/timeline.js";
import { SpecDoc } from "../../src/views/SpecDoc.jsx";
import { REQ_BY_ID } from "../../src/lib/data.js";
import { ExplorerView } from "../../src/views/ExplorerView.jsx";
import { CommandsView } from "../../src/views/CommandsView.jsx";

import { I18nProvider, translate } from "../../src/lib/i18n.jsx";
import { computeLayout } from "../../src/lib/layout.js";
import {
  buildHierarchy, defaultExpanded, allExpanded, flattenTree, ancestorsOf,
  keepSetFor, openQuestions, levelOf,
} from "../../src/lib/tree.js";
import { json, noop, specOf, test, fail } from "./harness.jsx";

const cases = {
  App: <App />,
  MapView: <MapView selId="ARCH-PARSE-001" setSelId={noop} openSpec={noop} highlightId={null}
                    setHighlightId={noop} />,
  ProblemsView: <ProblemsView openSpec={noop} />,
  RoadmapView: <RoadmapView openSpec={noop} />,
  SpecDoc: specOf("ARCH-MAP-007"),
  ExplorerView: <ExplorerView selId="ARCH-MAP-007" setSelId={noop} />,
};
for (const [name, el] of Object.entries(cases)) {
  try {
    const html = renderToString(el);
    if (html.length < 200) fail(`FAIL ${name}: output too short (${html.length})`);
    else console.log(`ok   ${name} (${html.length} chars)`);
  } catch (e) {
    fail(`FAIL ${name}: ${e.message}`);
  }
}

// The roadmap's one lane, and that every item lands in it.  // tested-by: REQ-VIEWER-995
// Rendered against a tiny synthetic registry so the assertion is about the RULE, not
// about whatever TODO.md happens to hold today. Every legacy lane value is present in
// the fixture on purpose: `lane:` must still PARSE and still be ignored by the chart.
{
  const ms = "v9.9";
  adoptMapExport({ nodes: [
    adaptNode({ id: "LANE-REQ-001", title: "A shipped capability", status: "confirmed",
                layer: "bus", milestone: ms, deps: [], used_by: [], depends_on: [] }),
  ] });
  const todoNames = ["Crash on empty stdin", "Old style item", "Plain feature item"];
  adoptMapExport({ todos: [
    { name: todoNames[0], lane: "bug",     milestone: ms, done: false },
    { name: todoNames[1], lane: "ops",     milestone: ms, done: false },
    { name: todoNames[2], lane: "feature", milestone: ms, done: false },
    { name: "Already shipped", lane: "feature", milestone: ms, done: true },
  ] });
  const html = renderToString(<RoadmapView openSpec={noop} />);
  const laneLabels = (html.match(/>(Implementations|Bugs|Features|Bus|Need|Ops)</g) || []);
  const laneChecks = [
    ["roadmap shows exactly one lane, labelled Implementations",  // verifies: REQ-VIEWER-995#CASE-1
      laneLabels.length === 1 && laneLabels[0] === ">Implementations<"],
    ["every open TODO item lands in it, whatever its lane says",  // verifies: REQ-VIEWER-995#CASE-2
      todoNames.every(n => html.includes(n)) && !html.includes("Already shipped")],
    ["a milestoned requirement lands in it",                      // verifies: REQ-VIEWER-995#CASE-3
      html.includes("A shipped capability")],
  ];
  for (const [label, ok] of laneChecks) test(label, ok);
  adoptMapExport({ nodes: json.nodes.map(adaptNode) });           // back to the live registry
  adoptMapExport({ todos: json.todos || [] });
}

// LANGUAGE sets the viewer's default locale.  // tested-by: REQ-TRANSLATE-996
// SSR has no window; a minimal one with only the inlined blob is exactly the state the
// provider sees at mount time in the single-file viewer (no localStorage = no reader choice).
{
  const RO_MARKERS = ["verzi", "Întrebări", "Nicio", "deschis", "cerin"];
  const renderWith = (language) => {
    globalThis.window = { __REQMAP_DATA__: { language } };
    try { return renderToString(<I18nProvider><App /></I18nProvider>); }
    finally { delete globalThis.window; }
  };
  const roHtml = renderWith("ro"), enHtml = renderWith("en"), bothHtml = renderWith("both");
  const hasRo = (h) => RO_MARKERS.some(m => h.includes(m));
  const langChecks = [
    // verifies: REQ-TRANSLATE-996#CASE-7
    ["LANGUAGE ro opens the viewer in Romanian",            hasRo(roHtml)],
    // verifies: REQ-TRANSLATE-996#CASE-7
    ["LANGUAGE en opens the viewer in English",             !hasRo(enHtml)],
    // verifies: REQ-TRANSLATE-996#CASE-7
    ["LANGUAGE both opens in English",                      !hasRo(bothHtml)],
    ["a reader's own choice beats the engine default",
      !hasRo(renderToString(<I18nProvider initialLocale="en"><App /></I18nProvider>))],
  ];
  for (const [label, ok] of langChecks) test(label, ok);
}

// content assertions against the live (engine) registry
const appHtml = renderToString(<App />);
const checks = [
  ["registry loaded from engine", REQUIREMENTS.length >= 13],
  ["renders a real capability id", appHtml.includes("ARCH-PARSE-001")],
  ["renders the brand", appHtml.includes("Manager")],
  ["renders Problems nav", appHtml.includes("Problems")],
];
for (const [label, ok] of checks) test(label, ok);

// ranked-search parity (ARCH-SEARCH-036): the viewer's search must rank by the
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
const searchChecks = [  // tested-by: REQ-SEARCH-912
  ["ranked search returns the drift requirement first", ranked[0]?.req.id === "REQ-DRIFT-001"],
  // verifies: REQ-SEARCH-912#CASE-5
  ["ranked search score matches the engine (0.4112)",
    ranked[0] && Math.abs(ranked[0].score - 0.4112) < 1e-4],
  ["ranked search shows a score per hit", typeof ranked[0]?.score === "number"],
  ["ranked search floors out a no-overlap query", nomatch.length === 0],
];
for (const [label, ok] of searchChecks) test(label, ok);

// XSS regression: untrusted requirement HTML must render ESCAPED in both
// dangerouslySetInnerHTML sinks (MapView DetailPanel + SpecDoc), never live.
adoptMapExport({ nodes: [adaptNode({
  id: "XSS-TEST-001", title: "xss", area: "XSS", layer: "feature", status: "confirmed",
  intent: "i", contract: ['danger <img src=x onerror="boom( })">'],
  acc: ['<script>boom()</script>'], members: [], deps: [], used_by: [],
})] });
const xssMap = renderToString(
  <MapView selId="XSS-TEST-001" setSelId={noop} openSpec={noop} highlightId={null}
           setHighlightId={noop} />);
const xssSpec = renderToString(specOf("XSS-TEST-001"));
const xssChecks = [
  ["MapView escapes injected contract HTML",
    xssMap.includes("&lt;img") && !xssMap.includes("<img src=x onerror")],
  ["SpecDoc escapes injected acceptance HTML",
    xssSpec.includes("&lt;script&gt;") && !xssSpec.includes("<script>boom")],
];
for (const [label, ok] of xssChecks) test(label, ok);

// ---- cross-references and header fields (REQ-VIEWER-944) -------------------
// `[[ID]]` is how an author points one requirement at another. Rendered
// literally it was a pair of brackets leading nowhere, on every architecture
// requirement in the corpus.
adoptMapExport({ nodes: [
  adaptNode({ id: "LINK-SRC-001", title: "source", area: "LINK", layer: "feature",
    status: "confirmed",
    intent: "i", contract: ['see [[LINK-DST-002]] and [[LINK-GONE-999]] <b>x</b>'],
    acc: [], members: [], deps: [], used_by: [] }),
  adaptNode({ id: "LINK-DST-002", title: "target", area: "LINK", layer: "feature",
    status: "confirmed",
    intent: "i", contract: ["a clause"], acc: [], members: [], deps: [], used_by: [] }),
] });
const linkSpec = renderToString(specOf("LINK-SRC-001"));
const linkChecks = [
  // verifies: REQ-VIEWER-944#CASE-1
  ["links: a resolvable cross-reference renders as a control carrying the id",
    linkSpec.includes('data-req="LINK-DST-002"') && !linkSpec.includes("[[LINK-DST-002]]")],
  ["links: a dangling cross-reference is marked, not linked",  // verifies: REQ-VIEWER-944#CASE-2
    linkSpec.includes("wikilink off") && !linkSpec.includes('data-req="LINK-GONE-999"')],
  ["links: markup beside a cross-reference stays escaped",  // verifies: REQ-VIEWER-944#CASE-3
    linkSpec.includes("&lt;b&gt;") && !linkSpec.includes("<b>x</b>")],
  // verifies: REQ-VIEWER-944#CASE-4
  ["links: the header states no owner, a field the export never carried",
    !linkSpec.includes("owner")],
];
for (const [label, ok] of linkChecks) test(label, ok);

// i18n: the toggle must translate UI CHROME and leave requirement content alone.
// Rendered inside the provider with the locale forced, since the provider's own
// initial value comes from localStorage, which does not exist here.
adoptMapExport({ nodes: json.nodes.map(adaptNode) });
const spec = (locale) => renderToString(
  <I18nProvider initialLocale={locale}>
    {specOf("ARCH-MAP-007")}
  </I18nProvider>);
const specEn = spec("en"), specRo = spec("ro");
const reqUnderTest = REQ_BY_ID["ARCH-MAP-007"];
const i18nChecks = [
  // verifies: REQ-VIEWER-943#CASE-1
  ["i18n: English is the default rendering", specEn.includes("Where — Members in code")],
  ["i18n: Romanian translates a section header",  // verifies: REQ-VIEWER-943#CASE-2
    specRo.includes("Unde — Membri în cod") && !specRo.includes("Where — Members in code")],
  // verifies: REQ-VIEWER-943#CASE-3
  ["i18n: an unknown string falls back to English rather than blanking",
    translate("ro", "Not In The Dictionary") === "Not In The Dictionary"],
  // verifies: REQ-VIEWER-943#CASE-4
  ["i18n: placeholders interpolate",
    translate("ro", "{n} members bound", { n: 7 }) === "7 membri legați"],
  // verifies: REQ-VIEWER-943#CASE-6
  ["i18n: engine vocabulary stays literal (status value, not a translation)",
    specRo.includes(reqUnderTest.status)],
];
for (const [label, ok] of i18nChecks) test(label, ok);

// i18n content translation (opt-in, cached, always marked) — REQ-TRANSLATE-042.
// A node with a cached en-locale translation renders the translated text WITH the
// "machine-translated, unreviewed" badge; a node with no cache entry (the default
// for every requirement until `reqmap.py translate` runs) renders the author's
// text and shows no badge at all — the untranslated path must stay unchanged.
adoptMapExport({ nodes: [adaptNode({
  id: "I18N-CONTENT-TEST-001", title: "Titlu original", area: "I18N", layer: "feature",
  status: "confirmed", intent: "Motivul original.", contract: ["- Clauza originală."],
  acc: ["- Criteriul original."], members: [], deps: [], used_by: [],
  i18n: { en: { title: "Original title", intent: "The original reason.",
                contract: "- The original clause.", acceptance: "- The original criterion." } },
})] });
const translatedSpecEn = renderToString(
  <I18nProvider initialLocale="en">{specOf("I18N-CONTENT-TEST-001")}</I18nProvider>);
const translatedSpecRo = renderToString(
  <I18nProvider initialLocale="ro">{specOf("I18N-CONTENT-TEST-001")}</I18nProvider>);
adoptMapExport({ nodes: [adaptNode({
  id: "I18N-NOCACHE-TEST-001", title: "Titlu fără cache", area: "I18N", layer: "feature",
  status: "confirmed", intent: "Motiv.", contract: ["- Clauză."], acc: ["- Criteriu."],
  members: [], deps: [], used_by: [],
})] });
const noCacheSpecEn = renderToString(
  <I18nProvider initialLocale="en">{specOf("I18N-NOCACHE-TEST-001")}</I18nProvider>);
const noCacheSpecRo = renderToString(
  <I18nProvider initialLocale="ro">{specOf("I18N-NOCACHE-TEST-001")}</I18nProvider>);
const i18nContentChecks = [
  // verifies: REQ-TRANSLATE-938#CASE-4
  ["i18n content: cached en translation renders the translated title",
    translatedSpecEn.includes("Original title")],
  // verifies: REQ-TRANSLATE-938#CASE-4
  ["i18n content: cached translation shows the machine-translated badge",
    translatedSpecEn.includes("machine-translated, unreviewed")],
  // verifies: REQ-TRANSLATE-938#CASE-4
  ["i18n content: no cache entry for ro falls back to the author's title",
    translatedSpecRo.includes("Titlu original") && !translatedSpecRo.includes("Original title")],
  // verifies: REQ-TRANSLATE-938#CASE-4
  ["i18n content: no cache entry at all shows no badge",
    noCacheSpecEn.includes("Titlu f")
      && !noCacheSpecEn.includes("machine-translated, unreviewed")],
  // COUNT, not presence. The four checks above assert the badge string appears SOMEWHERE
  // in the rendered document, which no single render site owns: a mutation matrix over all
  // four `<TranslatedBadge />` sites in SpecDoc.jsx (title, contract, intent, acceptance)
  // killed 0 of 4 — deleting any one left every check green, so a refactor could drop a
  // badge and ship machine-translated prose as the author's own with nothing failing.
  // The fixture caches all four fields, so a fully-translated node owes exactly four badges.
  // verifies: REQ-TRANSLATE-938#CASE-4
  ["i18n content: every translated field carries its own badge, not just one somewhere",
    (translatedSpecEn.match(/machine-translated, unreviewed/g) || []).length === 4],
  // The boundary the feature exists to respect: the CHROME toggle never translates the
  // artifact under review. Asserted on a requirement with NO `i18n` cache entry, because
  // a cached translation IS rendered, with a badge — that is REQ-TRANSLATE-938's job and
  // a different axis. Until the Spec tab was removed this read `specRo.includes(title)`
  // against ARCH-MAP-007, which the repo's own cache DOES translate; it passed only
  // because the tab's 220px nav listed every title untranslated beside the document.
  // verifies: REQ-VIEWER-943#CASE-5
  ["i18n: the chrome toggle leaves an untranslated requirement alone",
    noCacheSpecRo.includes("Titlu f") && !noCacheSpecRo.includes("machine-translated, unreviewed")],
];
for (const [label, ok] of i18nContentChecks) test(label, ok);
// ---- acceptance criteria keep their Given/When/Then lines ------------------
// The engine emits BOTH `accept` (the raw labelled Gherkin block) and `acc` (the
// same criteria folded to one line each, for search and counting). `gwt` used to be
// set only when `acc` was empty — true for every requirement until the engine
// learned to parse the block form (v2.29.0), and false for every one after, which
// silently turned every criterion into a single run-on line.
const GWT_ACCEPT = "AC-1\n  Given  a repo with no requirements/\n  When   `init` runs\n"
  + "  Then   it creates the directory";
adoptMapExport({ nodes: [adaptNode({
  id: "GWT-TEST-001", title: "Acceptance block", area: "GWT", layer: "feature",
  status: "confirmed", intent: "Reason.", contract: ["- A clause."],
  acc: ["AC-1 — Given  a repo with no requirements/ When   `init` runs "
    + "Then   it creates the directory"],
  accept: GWT_ACCEPT, members: [], deps: [], used_by: [],
})] });
const gwtSpec = renderToString(specOf("GWT-TEST-001"));
const gwtChecks = [
  // verifies: REQ-VIEWER-942#CASE-5
  ["acceptance: a labelled block renders as the multi-line gwt block, not a folded bullet",
    gwtSpec.includes('class="gwt"')],
  // verifies: REQ-VIEWER-942#CASE-5
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
  // verifies: REQ-VIEWER-942#CASE-3
  ["layout: a cycle cannot rank beyond the node count", cycMaxRank <= cyc.length - 1],
  // verifies: REQ-VIEWER-942#CASE-3
  ["layout: a cyclic graph stays in a bounded canvas", cycLayout.width < 2000],
  // verifies: REQ-VIEWER-942#CASE-2
  ["layout: every node still gets a position", cyc.every((r) => cycLayout.pos[r.id])],
  // verifies: REQ-VIEWER-942#CASE-2
  ["layout: cycle-closing edges are still drawn", cycLayout.edges.length === 4],
  // verifies: REQ-VIEWER-942#CASE-1
  ["layout: a deep DAG still ranks by longest path", chainMaxRank === 11],
];
for (const [label, ok] of layoutChecks) test(label, ok);

// ---- the map carries accept once; the viewer folds it (v8.3.0) ------------------
const FOLD_ACCEPT = "CASE-1 — first\n  Given  a\n  When   b\n  Then   c\n\n"
  + "CASE-2\n  Given  d <!-- verifiable by: automated test -->\n  Then   e";
const folded = adaptNode({ id: "FOLD-001", title: "t", accept: FOLD_ACCEPT,
                           depends_on: ["DEP-001"] });
const legacy = adaptNode({ id: "FOLD-002", title: "t", acc: ["AC-1 — kept"], deps: ["OLD-001"] });
const foldChecks = [
  // verifies: REQ-VIEWER-942#CASE-4
  ["fold: a node with no acc gets one folded entry per criterion",
    JSON.stringify(folded.acc) === JSON.stringify(
      ["CASE-1 — — first Given  a When   b Then   c", "CASE-2 — Given  d  Then   e"])],
  ["fold: an acc the engine still emits (atomic form, older map) is kept as is",
    JSON.stringify(legacy.acc) === JSON.stringify(["AC-1 — kept"])],
  ["deps: depends_on is read, and an older map's deps still is",
    folded.deps[0] === "DEP-001" && legacy.deps[0] === "OLD-001"],
];
for (const [label, ok] of foldChecks) test(label, ok);

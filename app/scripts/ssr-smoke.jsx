// tested-by: ARCH-VIEWER-007  // tested-by: REQ-TRANSLATE-938  // tested-by: REQ-VIEWER-942  // tested-by: REQ-VIEWER-943
// tested-by: ARCH-SEARCH-036  // tested-by: REQ-VIEWER-944  // tested-by: REQ-VIEWER-945  // tested-by: REQ-VIEWER-966
// tested-by: REQ-VIEWER-964  // tested-by: REQ-SEARCH-965  // tested-by: REQ-VIEWER-969  // tested-by: REQ-VIEWER-977
// tested-by: REQ-VIEWER-984  // tested-by: REQ-VIEWER-995  // tested-by: REQ-TRANSLATE-996
// tested-by: REQ-VIEWER-999  // tested-by: REQ-PLANCADENCE-1000
// tested-by: REQ-HISTORY-1003
/* Render-time smoke test: server-render every view against the engine-adapted
 * dataset and assert real content appears. Catches render-throws and bad data
 * assumptions the build cannot. Bundled + run by run-ssr-smoke.mjs. */
import { renderToString } from "react-dom/server";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import App from "../src/App.jsx";
import { rankRequirements, searchRequirements } from "../src/lib/search.js";
import { adoptMapExport, REQUIREMENTS, ROADMAP, HISTORY, TARGETS } from "../src/lib/data.js";
import { adaptNode, loadData } from "../src/lib/loadData.js";
import { MapView } from "../src/views/MapView.jsx";
import { ProblemsView, computeProblems, computeQuestions } from "../src/views/ProblemsView.jsx";
import { RoadmapView } from "../src/views/RoadmapView.jsx";
import { PlanGantt, noteText, matchItem, ShippedNote, VersionNote } from "../src/views/roadmap/PlanGantt.jsx";
import { stackBars } from "../src/lib/timeline.js";
import { SpecDoc } from "../src/views/SpecDoc.jsx";
import { REQ_BY_ID } from "../src/lib/data.js";
import { ExplorerView } from "../src/views/ExplorerView.jsx";
import { CommandsView } from "../src/views/CommandsView.jsx";

import { I18nProvider, translate } from "../src/lib/i18n.jsx";
import { computeLayout } from "../src/lib/layout.js";
import {
  buildHierarchy, defaultExpanded, allExpanded, flattenTree, ancestorsOf,
  keepSetFor, openQuestions, levelOf,
} from "../src/lib/tree.js";

// feed the real engine export through the adapter, exactly as the browser would
// (run from the app/ directory: `node scripts/run-ssr-smoke.mjs`)
const json = JSON.parse(readFileSync(resolve(process.cwd(), "public/data.json"), "utf8"));
adoptMapExport({ nodes: json.nodes.map(adaptNode) });

const noop = () => {};
// The Spec TAB was removed (Explorer renders the same document beside a richer
// nav); every check below was about the DOCUMENT, so each one renders it directly.
// REQ_BY_ID is a live binding, so this reads whatever fixture was last adopted.
const specOf = (id) => <SpecDoc r={REQ_BY_ID[id]} onNav={noop} />;
const cases = {
  App: <App />,
  MapView: <MapView selId="ARCH-PARSE-001" setSelId={noop} openSpec={noop} highlightId={null} setHighlightId={noop} />,
  ProblemsView: <ProblemsView openSpec={noop} />,
  RoadmapView: <RoadmapView openSpec={noop} />,
  SpecDoc: specOf("ARCH-MAP-007"),
  ExplorerView: <ExplorerView selId="ARCH-MAP-007" setSelId={noop} />,
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
    ["LANGUAGE ro opens the viewer in Romanian",            hasRo(roHtml)],     // verifies: REQ-TRANSLATE-996#CASE-7
    ["LANGUAGE en opens the viewer in English",             !hasRo(enHtml)],    // verifies: REQ-TRANSLATE-996#CASE-7
    ["LANGUAGE both opens in English",                      !hasRo(bothHtml)],  // verifies: REQ-TRANSLATE-996#CASE-7
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
  ["ranked search score matches the engine (0.4112)", ranked[0] && Math.abs(ranked[0].score - 0.4112) < 1e-4],  // verifies: REQ-SEARCH-912#CASE-5
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
  <MapView selId="XSS-TEST-001" setSelId={noop} openSpec={noop} highlightId={null} setHighlightId={noop} />);
const xssSpec = renderToString(specOf("XSS-TEST-001"));
const xssChecks = [
  ["MapView escapes injected contract HTML", xssMap.includes("&lt;img") && !xssMap.includes("<img src=x onerror")],
  ["SpecDoc escapes injected acceptance HTML", xssSpec.includes("&lt;script&gt;") && !xssSpec.includes("<script>boom")],
];
for (const [label, ok] of xssChecks) test(label, ok);

// ---- cross-references and header fields (REQ-VIEWER-944) -------------------
// `[[ID]]` is how an author points one requirement at another. Rendered
// literally it was a pair of brackets leading nowhere, on every architecture
// requirement in the corpus.
adoptMapExport({ nodes: [
  adaptNode({ id: "LINK-SRC-001", title: "source", area: "LINK", layer: "feature", status: "confirmed",
    intent: "i", contract: ['see [[LINK-DST-002]] and [[LINK-GONE-999]] <b>x</b>'],
    acc: [], members: [], deps: [], used_by: [] }),
  adaptNode({ id: "LINK-DST-002", title: "target", area: "LINK", layer: "feature", status: "confirmed",
    intent: "i", contract: ["a clause"], acc: [], members: [], deps: [], used_by: [] }),
] });
const linkSpec = renderToString(specOf("LINK-SRC-001"));
const linkChecks = [
  ["links: a resolvable cross-reference renders as a control carrying the id",  // verifies: REQ-VIEWER-944#CASE-1
    linkSpec.includes('data-req="LINK-DST-002"') && !linkSpec.includes("[[LINK-DST-002]]")],
  ["links: a dangling cross-reference is marked, not linked",  // verifies: REQ-VIEWER-944#CASE-2
    linkSpec.includes("wikilink off") && !linkSpec.includes('data-req="LINK-GONE-999"')],
  ["links: markup beside a cross-reference stays escaped",  // verifies: REQ-VIEWER-944#CASE-3
    linkSpec.includes("&lt;b&gt;") && !linkSpec.includes("<b>x</b>")],
  ["links: the header states no owner, a field the export never carried",  // verifies: REQ-VIEWER-944#CASE-4
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
  ["i18n: English is the default rendering", specEn.includes("Where — Members in code")],  // verifies: REQ-VIEWER-943#CASE-1
  ["i18n: Romanian translates a section header",  // verifies: REQ-VIEWER-943#CASE-2
    specRo.includes("Unde — Membri în cod") && !specRo.includes("Where — Members in code")],
  ["i18n: an unknown string falls back to English rather than blanking",  // verifies: REQ-VIEWER-943#CASE-3
    translate("ro", "Not In The Dictionary") === "Not In The Dictionary"],
  ["i18n: placeholders interpolate", translate("ro", "{n} members bound", { n: 7 }) === "7 membri legați"],  // verifies: REQ-VIEWER-943#CASE-4
  ["i18n: engine vocabulary stays literal (status value, not a translation)",  // verifies: REQ-VIEWER-943#CASE-6
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
  ["i18n content: cached en translation renders the translated title", translatedSpecEn.includes("Original title")],  // verifies: REQ-TRANSLATE-938#CASE-4
  ["i18n content: cached translation shows the machine-translated badge", translatedSpecEn.includes("machine-translated, unreviewed")],  // verifies: REQ-TRANSLATE-938#CASE-4
  ["i18n content: no cache entry for ro falls back to the author's title", translatedSpecRo.includes("Titlu original") && !translatedSpecRo.includes("Original title")],  // verifies: REQ-TRANSLATE-938#CASE-4
  ["i18n content: no cache entry at all shows no badge", noCacheSpecEn.includes("Titlu f") && !noCacheSpecEn.includes("machine-translated, unreviewed")],  // verifies: REQ-TRANSLATE-938#CASE-4
  // COUNT, not presence. The four checks above assert the badge string appears SOMEWHERE
  // in the rendered document, which no single render site owns: a mutation matrix over all
  // four `<TranslatedBadge />` sites in SpecDoc.jsx (title, contract, intent, acceptance)
  // killed 0 of 4 — deleting any one left every check green, so a refactor could drop a
  // badge and ship machine-translated prose as the author's own with nothing failing.
  // The fixture caches all four fields, so a fully-translated node owes exactly four badges.
  ["i18n content: every translated field carries its own badge, not just one somewhere",  // verifies: REQ-TRANSLATE-938#CASE-4
    (translatedSpecEn.match(/machine-translated, unreviewed/g) || []).length === 4],
  // The boundary the feature exists to respect: the CHROME toggle never translates the
  // artifact under review. Asserted on a requirement with NO `i18n` cache entry, because
  // a cached translation IS rendered, with a badge — that is REQ-TRANSLATE-938's job and
  // a different axis. Until the Spec tab was removed this read `specRo.includes(title)`
  // against ARCH-MAP-007, which the repo's own cache DOES translate; it passed only
  // because the tab's 220px nav listed every title untranslated beside the document.
  ["i18n: the chrome toggle leaves an untranslated requirement alone",  // verifies: REQ-VIEWER-943#CASE-5
    noCacheSpecRo.includes("Titlu f") && !noCacheSpecRo.includes("machine-translated, unreviewed")],
];
for (const [label, ok] of i18nContentChecks) test(label, ok);
// ---- acceptance criteria keep their Given/When/Then lines ------------------
// The engine emits BOTH `accept` (the raw labelled Gherkin block) and `acc` (the
// same criteria folded to one line each, for search and counting). `gwt` used to be
// set only when `acc` was empty — true for every requirement until the engine
// learned to parse the block form (v2.29.0), and false for every one after, which
// silently turned every criterion into a single run-on line.
const GWT_ACCEPT = "AC-1\n  Given  a repo with no requirements/\n  When   `init` runs\n  Then   it creates the directory";
adoptMapExport({ nodes: [adaptNode({
  id: "GWT-TEST-001", title: "Acceptance block", area: "GWT", layer: "feature",
  status: "confirmed", intent: "Reason.", contract: ["- A clause."],
  acc: ["AC-1 — Given  a repo with no requirements/ When   `init` runs Then   it creates the directory"],
  accept: GWT_ACCEPT, members: [], deps: [], used_by: [],
})] });
const gwtSpec = renderToString(specOf("GWT-TEST-001"));
const gwtChecks = [
  ["acceptance: a labelled block renders as the multi-line gwt block, not a folded bullet",  // verifies: REQ-VIEWER-942#CASE-5
    gwtSpec.includes('class="gwt"')],
  ["acceptance: the folded one-line form is not what the reader sees",  // verifies: REQ-VIEWER-942#CASE-5
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
  ["layout: a cycle cannot rank beyond the node count", cycMaxRank <= cyc.length - 1],  // verifies: REQ-VIEWER-942#CASE-3
  ["layout: a cyclic graph stays in a bounded canvas", cycLayout.width < 2000],  // verifies: REQ-VIEWER-942#CASE-3
  ["layout: every node still gets a position", cyc.every((r) => cycLayout.pos[r.id])],  // verifies: REQ-VIEWER-942#CASE-2
  ["layout: cycle-closing edges are still drawn", cycLayout.edges.length === 4],  // verifies: REQ-VIEWER-942#CASE-2
  ["layout: a deep DAG still ranks by longest path", chainMaxRank === 11],  // verifies: REQ-VIEWER-942#CASE-1
];
for (const [label, ok] of layoutChecks) test(label, ok);

// ---- hierarchy / module explorer -------------------------------------------
// The corpus this view exists for is a strict tree (one parent, one root,
// depth == level). These assert the SHAPE the outline depends on, plus the two
// degradations that must not throw: a registry with no `satisfies` at all (the
// baked fallback) and a `satisfies` cycle.
adoptMapExport({ nodes: json.nodes.map(adaptNode) });
const H = buildHierarchy(REQUIREMENTS);
const exp0 = defaultExpanded(H);
const rows0 = flattenTree(H, { expanded: exp0, keep: null });
const rowsAll = flattenTree(H, { expanded: allExpanded(H), keep: null });
const codeRows = REQUIREMENTS.filter((r) => levelOf(r) === "code");
const deepId = (codeRows[0] || {}).id;
const flatH = buildHierarchy([
  { id: "A-1", title: "a", level: "architecture", satisfies: [], satisfiedBy: [], deps: [] },
  { id: "A-2", title: "b", level: "architecture", satisfies: [], satisfiedBy: [], deps: [] },
]);
const cycH = buildHierarchy([
  { id: "C-1", title: "c1", level: "architecture", satisfies: ["C-2"], satisfiedBy: [] },
  { id: "C-2", title: "c2", level: "architecture", satisfies: ["C-1"], satisfiedBy: [] },
]);
const treeChecks = [
  ["tree: every requirement appears exactly once when fully expanded",
    rowsAll.length === REQUIREMENTS.length],
  ["tree: the default expansion collapses the code level to its parents",
    rows0.length < REQUIREMENTS.length && rows0.every((row) => levelOf(row.r) !== "code")],
  ["tree: adaptNode carries level/satisfies/satisfied_by through",
    REQUIREMENTS.some((r) => r.level === "code") && REQUIREMENTS.some((r) => r.satisfies.length)],
  ["tree: a code requirement has an ancestor chain to open",
    !!deepId && ancestorsOf(H, deepId).length > 0],
  ["tree: a filter keeps the ancestors of a match as context rows",
    (() => {
      if (!deepId) return false;
      const keep = keepSetFor(H, [deepId]);
      const rows = flattenTree(H, { expanded: exp0, keep });
      return rows.some((row) => row.id === deepId) && rows.length === ancestorsOf(H, deepId).length + 1;
    })()],
  ["tree: no `satisfies` anywhere degrades to a flat list",
    flatH.flat === true && flattenTree(flatH, { expanded: allExpanded(flatH), keep: null }).length === 2],
  ["tree: a satisfies cycle still renders every row exactly once",
    flattenTree(cycH, { expanded: { "C-1": true, "C-2": true }, keep: null }).length === 2],
  // 0 real findings today: every `verify` bullet in the export is the
  // "None — …" placeholder that `collect_findings` filters out.
  ["findings: the placeholder verify bullet is not a finding",
    openQuestions({ verify: ["None — authored from known intent, not reconstructed from code."] }).length === 0],
  ["findings: a real verify bullet IS a finding",
    openQuestions({ verify: ["Is a stale tested-by range an error or a warning?"] }).length === 1],
  ["findings: the live corpus reports zero open questions",
    computeQuestions().length === 0],
];
for (const [label, ok] of treeChecks) test(label, ok);

// The baked fallback has no `level` at all — adaptNode must default it so the
// outline still renders, and the Explorer must not throw on that registry.
const fallbackLevel = adaptNode({ id: "NOLEVEL-001", title: "t" }).level;
const explorerHtml = renderToString(<ExplorerView selId="ARCH-MAP-007" setSelId={noop} />);
const explorerChecks = [
  ["explorer: a node with no level defaults to architecture", fallbackLevel === "architecture"],
  ["explorer: the outline renders the root of the trace", explorerHtml.includes("SYS-SSOT-001")],
  ["explorer: the selected requirement's document renders beside it",
    explorerHtml.includes("ARCH-MAP-007") && explorerHtml.includes("Links — traceability")],
  ["explorer: a collapsed parent advertises its clause count", explorerHtml.includes("clauses")],
];
for (const [label, ok] of explorerChecks) test(label, ok);

// The empty state is a property of the VIEW, so it is asserted against an empty
// registry. It used to run against this repo's own map and passed only because the
// corpus happened to have nothing to fix — so the first draft requirement anyone
// added broke a test whose name says nothing about the corpus.
adoptMapExport({ nodes: [] });
test("problems: an empty inbox renders the named empty state, not a badge",
  renderToString(<ProblemsView openSpec={noop} />).includes("Nothing to fix."));

// ---- registry tally scopes the outline (REQ-VIEWER-945) ---------------------
adoptMapExport({ nodes: json.nodes.map(adaptNode) });
const unscoped = renderToString(<ExplorerView selId="ARCH-MAP-007" setSelId={noop} />);
const scopedDraft = renderToString(
  <ExplorerView selId="ARCH-MAP-007" setSelId={noop} focus="draft" clearFocus={noop} />);
const scopedOrphan = renderToString(
  <ExplorerView selId="ARCH-MAP-007" setSelId={noop} focus="orphan" clearFocus={noop} />);
const rowsOf = (html) => {
  const m = /(\d+) of (\d+) shown/.exec(html.replace(/<[^>]+>/g, ""));
  return m ? Number(m[1]) : -1;
};
const focusChecks = [
  ["focus: a status slice narrows the outline on the first render",  // verifies: REQ-VIEWER-945#CASE-1
    rowsOf(scopedDraft) >= 0 && rowsOf(scopedDraft) < rowsOf(unscoped)],
  ["focus: the active slice is shown as a chip that can clear it",  // verifies: REQ-VIEWER-945#CASE-3
    scopedDraft.includes("ex-chip on")],
  ["focus: orphan scopes to the gate's condition, not to a status",  // verifies: REQ-VIEWER-945#CASE-2
    rowsOf(scopedOrphan) === 0 && scopedOrphan.includes("No requirement matches these filters.")],
];
for (const [label, ok] of focusChecks) test(label, ok);

// ---- the command reference (REQ-VIEWER-964) --------------------------------
const CLI_FIXTURE = [
  { name: "gate", group: "build", summary: "Run the commit/CI gate.", arg: null,
    flags: [{ flag: "--strict", help: "promote warnings to errors" }] },
  // deliberately a name the Romanian dictionary does not carry, so the fallback is exercised
  { name: "wibble", group: "read", summary: "A command no dictionary knows.",
    arg: "AREA-NAME-NNN", flags: [] },
];
adoptMapExport({ commands: CLI_FIXTURE });
const cmdsEn = renderToString(<I18nProvider initialLocale="en"><CommandsView /></I18nProvider>);
const cmdsRo = renderToString(<I18nProvider initialLocale="ro"><CommandsView /></I18nProvider>);
adoptMapExport({ commands: [] });
const cmdsEmpty = renderToString(<I18nProvider initialLocale="en"><CommandsView /></I18nProvider>);
adoptMapExport({ commands: CLI_FIXTURE });
const cmdChecks = [
  ["commands: each verb is listed with its invocation and flags",  // verifies: REQ-VIEWER-964#CASE-1
    cmdsEn.includes("reqmap.py gate") && cmdsEn.includes("--strict")
    && cmdsEn.includes("reqmap.py wibble AREA-NAME-NNN")],
  ["commands: the summary follows the chosen language",  // verifies: REQ-VIEWER-964#CASE-2
    cmdsRo.includes("Verdictul complet") && !cmdsRo.includes("Run the commit/CI gate.")],
  ["commands: an untranslated command falls back to the engine's English",  // verifies: REQ-VIEWER-964#CASE-3
    cmdsRo.includes("A command no dictionary knows.")],
  ["commands: a map with no list renders the named empty state",  // verifies: REQ-VIEWER-964#CASE-4
    cmdsEmpty.includes("No command list in this map.")],
  ["commands: flag names are never translated",
    cmdsRo.includes("--strict")],
];
for (const [label, ok] of cmdChecks) test(label, ok);

// ---- id and literal-text search (REQ-SEARCH-965) ---------------------------
// The id is the primary key of this corpus and is in none of the ranked text: the
// viewer used to answer `ARCH-CHECK-006` with a different requirement entirely.
const SEARCH_LAYERS = [
  { id: "AREA-X-001", title: "Locking", intent: "why", contract: ["`gate` writes the lock."],
    acc: [], i18n: { ro: { title: "Blocare", intent: "de ce",
                           contract: "- `gate` scrie fisierul de blocare unic",
                           acceptance: "" } } },
  { id: "AREA-X-002", title: "Sync", intent: "why", contract: ["`sync` advances the baseline."],
    acc: ["CASE-1 a tag `GHOST-CAP-001` nothing defines"] },
];
const byId = searchRequirements(SEARCH_LAYERS, "AREA-X-001");
const byText = searchRequirements(SEARCH_LAYERS, "GHOST-CAP-001");
const byRo = searchRequirements(SEARCH_LAYERS, "fisierul de blocare unic");
const byWords = searchRequirements(SEARCH_LAYERS, "baseline advances");
const layerChecks = [
  ["search: an exact id is the first hit, marked as an id match",  // verifies: REQ-SEARCH-965#CASE-1
    byId[0] && byId[0].req.id === "AREA-X-001" && byId[0].kind === "id"],
  ["search: a phrase inside a case is found as a text match",  // verifies: REQ-SEARCH-965#CASE-3
    byText[0] && byText[0].req.id === "AREA-X-002" && byText[0].kind === "text"],
  ["search: a phrase from the cached translation is found",  // verifies: REQ-SEARCH-965#CASE-4
    byRo[0] && byRo[0].req.id === "AREA-X-001"],
  ["search: a plain query still comes from the ranked model",  // verifies: REQ-SEARCH-965#CASE-5
    byWords.length > 0 && byWords.every((h) => h.kind === "score")],
];
for (const [label, ok] of layerChecks) test(label, ok);

// ---- author questions live in Problems (REQ-VIEWER-966) --------------------
// Two screens until v4.0.0: Problems was ~618 rows of draft review noise and a real
// question dropped in there was invisible. What survives the merge is the
// distinction — origin is a tab, never a severity.
adoptMapExport({ nodes: [
  adaptNode({ id: "Q-ASKED-001", title: "asked", area: "Q", layer: "feature", status: "confirmed",
    intent: "i", contract: ["a clause"], acc: [], members: [{ role: "implements", loc: "a.py:1" }],
    verify: ["Is a stale tested-by range an error or a warning?"], deps: [], used_by: [] }),
  adaptNode({ id: "Q-QUIET-002", title: "quiet", area: "Q", layer: "feature", status: "confirmed",
    intent: "i", contract: ["a clause"], acc: [], members: [{ role: "implements", loc: "b.py:1" }],
    verify: ["None — authored from known intent."], deps: [], used_by: [] }),
] });
const merged = computeProblems();
const asked = computeQuestions();
const mergedHtml = renderToString(<ProblemsView openSpec={noop} />);
const mergeChecks = [
  ["problems: an author's open question is a row here",  // verifies: REQ-VIEWER-966#CASE-1
    merged.some((p) => p.id === "Q-ASKED-001" && p.sev === "QUESTION")],
  // it may still raise a computed WARN (confirmed, no tested-by) — what it must not
  // raise is a QUESTION, because no human asked anything
  ["problems: the placeholder verify bullet is still not a question",  // verifies: REQ-VIEWER-966#CASE-2
    !merged.some((p) => p.id === "Q-QUIET-002" && p.sev === "QUESTION")],
  ["problems: questions are counted apart from computed signals",  // verifies: REQ-VIEWER-966#CASE-3
    asked.length === 1 && asked[0].id === "Q-ASKED-001"],
  ["problems: the question tab is offered, and the question text is shown",  // verifies: REQ-VIEWER-966#CASE-4
    mergedHtml.includes("Questions") && mergedHtml.includes("stale tested-by range")],
];
for (const [label, ok] of mergeChecks) test(label, ok);

// ---- the rail's two engine-emitted readings (REQ-VIEWER-969) ---------------
adoptMapExport({ nodes: json.nodes.map(adaptNode) });
const SCORES = [{ score: 78, healthy: 39, total: 50 },
                { score: 23, clean_files: 7, files: 30 }];
adoptMapExport({ health: SCORES[0], design: SCORES[1] });
const railHtml = renderToString(<App />);
adoptMapExport({ health: null, design: null });                       // an older map carries neither key
const railBare = renderToString(<App />);
adoptMapExport({ health: SCORES[0], design: SCORES[1] });
const gaugeChecks = [
  ["rail: both readings render the engine's own numbers",  // verifies: REQ-VIEWER-969#CASE-1
    railHtml.includes("39/50 green") && railHtml.includes("7/30 files clean")
    && railHtml.includes(">78<") && railHtml.includes(">23<")],
  ["rail: a mid-band score takes the partial tone, not the green one",  // verifies: REQ-VIEWER-969#CASE-2
    railHtml.includes('stroke="var(--cov-partial)"')
    && !railHtml.includes('stroke="var(--cov-tested)"')],
  ["rail: the advisory design ring stays in one neutral ink",  // verifies: REQ-VIEWER-969#CASE-2
    // 23 would be red on the health scale; the design score is advice, never a failure
    railHtml.includes('stroke="var(--fg-muted)"')
    && !railHtml.includes('stroke="var(--cov-untested)"')],
  ["rail: a map with neither record shows no gauge at all",  // verifies: REQ-VIEWER-969#CASE-3
    !railBare.includes("rail-gauges") && !railBare.includes("gauge-row")],
  ["rail: health is a control, the advisory design score is not",  // verifies: REQ-VIEWER-969#CASE-4
    railHtml.includes("gauge-row static")],
  ["rail: the labels follow the chosen language",  // verifies: REQ-VIEWER-969#CASE-5
    translate("ro", "Health") === "Sănătate"
    && translate("ro", "{a}/{b} green", { a: 39, b: 50 }) === "39/50 verzi"],
];
for (const [label, ok] of gaugeChecks) test(label, ok);

// ---- the advisory design tab (REQ-VIEWER-977) -----------------------------
// The engine ships its code-review candidates in `_map.json`; the tab lists them by
// pillar, and since 2026-09-07 each is one computed signal (so the rail counts it) at
// its own severity, never a Warning row and never a row of "All". A map written before
// that carries no `findings`, so the tab must simply not appear rather than render an
// empty shell, and nothing is counted.
const DESIGN_WITH = {
  score: 23, clean_files: 7, files: 30,
  candidates: { encapsulation: 1, abstraction: 1, inheritance: 0, polymorphism: 0, standards: 0 },
  findings: [
    { pillar: "encapsulation", kind: "long-parameter-list", file: "src/thing.py",
      line: 12, name: "build", detail: "`build` takes 9 parameters (over 6)" },
    { pillar: "abstraction", kind: "long-function", file: "src/thing.py",
      line: 40, name: "run", detail: "`run` is 120 lines (over 80)" },
  ],
  advice: { "long-parameter-list": "a parameter list this long is an object waiting to be named",
            "long-function": "a function this long hides several steps" },
};
adoptMapExport({ health: null, design: DESIGN_WITH });
const designHtml = renderToString(<ProblemsView openSpec={noop} />);
const designRows = computeProblems().filter(p => p.signal === "design");
adoptMapExport({ health: null, design: { score: 23, clean_files: 7, files: 30, candidates: {} } });
const designBare = renderToString(<ProblemsView openSpec={noop} />);
adoptMapExport({ health: null, design: null });
const designChecks = [
  ["design: the tab is offered with the candidate count",  // verifies: REQ-VIEWER-977#CASE-1
    designHtml.includes("Design") && designHtml.includes(">2<")],
  ["design: no tab when the map carries no candidates",  // verifies: REQ-VIEWER-977#CASE-2
    !designBare.includes(">Design<")],
  ["design: candidates are counted at their own severity, listed only in their tab",  // verifies: REQ-VIEWER-977#CASE-3
    designRows.length === 2 && designRows.every(p => p.sev === "DESIGN" && p.noSpec)
    && designRows.some(p => p.loc === "src/thing.py:12")
    && !designHtml.includes("src/thing.py:12")
    && computeProblems().every(p => p.signal !== "design")],
];
for (const [label, ok] of designChecks) test(label, ok);

adoptMapExport({ nodes: json.nodes.map(adaptNode) });   // restore the real dataset for anything after this point

// ---- roadmap zoom and density (REQ-VIEWER-984) ----------------------------
// The wheel handler is NOT reachable from here: renderToString has no DOM and
// dispatches no events. What IS observable is the primitive each control uses,
// which is where both of this feature's real bugs lived.
const roadZoomed  = renderToString(<RoadmapView openSpec={noop} initialZoom={40} />);
const roadCompact = renderToString(<RoadmapView openSpec={noop} initialDensity="compact" />);
const roadDefault = renderToString(<RoadmapView openSpec={noop} />);
const roadmapChecks = [
  ["roadmap: scaling uses CSS zoom, not a transform",  // verifies: REQ-VIEWER-984#CASE-1
    // text-transform:uppercase is all over the markup, so the assertion has to name the scale itself
    roadZoomed.includes("zoom:0.4") && !roadZoomed.includes("transform:scale")],
  ["roadmap: compact truncates the title and keeps it in the tooltip",  // verifies: REQ-VIEWER-984#CASE-2
    roadCompact.includes("text-overflow:ellipsis")
    && roadCompact.includes("max-width:108px")
    && /title="[^"]{40,}"/.test(roadCompact)],
  ["roadmap: the defaults are the pre-control view",  // verifies: REQ-VIEWER-984#CASE-3
    roadDefault.includes("zoom:1") && roadDefault.includes(">100%<")
    && !roadDefault.includes("text-overflow:ellipsis")],
];
for (const [label, ok] of roadmapChecks) test(label, ok);

// A milestone whose TODO items have all shipped. The chips are still filtered to the
// open ones, so the column is empty — what is asserted is that it EXISTS, because the
// version it names is finished, not skipped.
adoptMapExport({ todos: [{ title: "a shipped item", done: true, milestone: "v99.9", lane: "feature" }] });
const roadAllDone = renderToString(<RoadmapView openSpec={noop} />);
adoptMapExport({ todos: [] });
test("roadmap: a milestone whose every item is complete still gets a column",  // verifies: REQ-VIEWER-995#CASE-4
  roadAllDone.includes(">v99.9<") && !roadAllDone.includes("a shipped item"));

// Plan and Versions read one planned list, `bars` (REQ-PLANSTALE-1013). A bar used to
// create its version's column and never appear in it, because the column read
// `milestones[].items[]` — a second list nobody wrote.
adoptMapExport({ todos: [], planning: { lanes: ["Feature"], milestones: { "v99.8": { items: ["ghost"] } },
  bars: [{ title: "the planned bar", lane: "Feature", start: "2026-09-21", end: "2026-09-27", milestone: "v99.7" }] } });
const roadBars = renderToString(<RoadmapView openSpec={noop} initialMode="versions" />);
adoptMapExport({ todos: [], planning: json.planning || null });
test("roadmap: a bar appears in its version's column, and items[] is not read",  // verifies: REQ-PLANSTALE-1013#CASE-7
  roadBars.includes(">v99.7<") && roadBars.includes("the planned bar") && !roadBars.includes("ghost"));

// ---- roadmap horizons (REQ-VIEWER-999) -----------------------------------
// `initialRoadmap` is the seam the other two controls already open with
// `initialZoom` / `initialDensity`: a fixture without mutating the loaded export.
const HZ = [
  { name: "the open one", horizon: "now", req: json.nodes[0].id, unpark: null, done: false },
  { name: "the done one", horizon: "now", req: null, unpark: null, done: true },
  { name: "the queued one", horizon: "next", req: "NOPE-X-999", unpark: null, done: false },
  { name: "the parked one", horizon: "later", req: null, unpark: "a named consumer asks", done: false },
];
const hzNone = renderToString(<RoadmapView openSpec={noop} initialRoadmap={[]} />);
const barNoteChecks = [
  ["roadmap: the Horizons mode is gone",  // verifies: REQ-VIEWER-999#CASE-4
    // Items are still carried — the panel reads them — but no mode renders columns.
    (() => {
      const withItems = renderToString(
        <RoadmapView openSpec={noop} initialRoadmap={HZ} />);
      return !withItems.includes(">Horizons<")
        && !(withItems.includes(">Now<") && withItems.includes(">Later<"));
    })()],
  ["roadmap: a stored Horizons choice lands on Plan, not on nothing",  // verifies: REQ-VIEWER-999#CASE-4
    !hzNone.includes(">Horizons<")],
  ["roadmap: an HTML-comment note renders as its text",  // verifies: REQ-VIEWER-999#CASE-3
    noteText("<!-- the reason -->") === "the reason"],
  ["roadmap: a multi-line note keeps its breaks and loses its indent",  // verifies: REQ-VIEWER-999#CASE-3
    noteText(["<!--", "  first", "  second", "-->"].join("\n"))
      === ["first", "second"].join("\n")],
  ["roadmap: a bar finds its item by req:",  // verifies: REQ-VIEWER-999#CASE-1
    (() => {
      const it = matchItem({ reqId: json.nodes[0].id }, HZ);
      return !!it && it.name === "the open one";
    })()],
  ["roadmap: a bar with no req, or an unmatched one, has no item",  // verifies: REQ-VIEWER-999#CASE-2
    // NOT `NOPE-X-999`: the registry does not have it but the fixture's `next` item
    // carries it, so the join finds that item and should. The join is bar->item, and
    // whether the id also resolves to a requirement is the panel's separate question.
    matchItem({ reqId: null }, HZ) === null
    && matchItem({ reqId: "ABSENT-Z-000" }, HZ) === null],
  ["roadmap: the roadmap payload survives the mode's removal",  // verifies: REQ-VIEWER-999#CASE-5
    (() => {
      const adopted = adoptMapExport({ nodes: json.nodes.map(adaptNode), roadmap: HZ });
      const kept = (adopted && adopted.roadmap) || ROADMAP;
      adoptMapExport({ nodes: json.nodes.map(adaptNode) });
      return Array.isArray(kept) && kept.length === HZ.length;
    })()],
];
for (const [label, ok] of barNoteChecks) test(label, ok);

// ---- release cadence (REQ-PLANCADENCE-1000) --------------------------------
// The chart PLACES engine-computed dates and derives none. Asserted by handing it
// a date the weekday arithmetic would never produce: if a rule appears for it, the
// viewer is reading the list; if the viewer recomputed, it would not be there.
test("cadence: a release past the last bar still gets a column",  // verifies: REQ-PLANCADENCE-1000#CASE-1
  (() => {
    // `until` running past everything scheduled is the whole point of a cadence: the
    // months after the last bar are exactly where the next releases land. Before the
    // range counted release dates, those were emitted and then dropped by the
    // in-range filter — the engine said a release lands and the chart showed nothing.
    const far = renderToString(<PlanGantt planning={{
      lanes: ["Feature"],
      bars: [{ title: "b", lane: "Feature", start: "2026-09-21", end: "2026-09-27" }],
      cadence: { every: "month", on: "last", lane: "Release", until: "2026-12-31" },
      releases: ["2026-09-30", "2026-12-31"],
    }} history={[]} locale="en" t={(x) => x} zoom={100} />);
    return far.includes("2026-12-31") || far.toLowerCase().includes("dec");
  })());

test("cadence: a plan with only a cadence still draws its calendar",  // verifies: REQ-PLANHORIZON-1010#CASE-3
  (() => {
    // The seeded shape: no bars, no milestone dues, no history. It used to render the
    // "add milestones or bars" dead end — the empty case being the one with nothing to
    // look at, which is backwards for a repo that has planned nothing yet.
    const bare = renderToString(<PlanGantt planning={{
      lanes: ["Feature", "Bug", "Release"],
      cadence: { every: "month", on: "last", lane: "Release" },
      milestones: {}, bars: [],
      releases: ["2026-09-30", "2026-10-31", "2026-11-30", "2026-12-31"],
    }} history={[]} locale="en" t={(x) => x} zoom={100} />);
    return !bare.includes("Add milestones with due dates")
      && bare.includes("Feature") && bare.includes("Release");
  })());

test("roadmap: the shipped band is named by the branch",  // verifies: REQ-PLANBRANCH-1011#CASE-4
  (() => {
    const hist = [{ month: "2026-06", count: 2, first: "2026-06-01", last: "2026-06-30",
                    versions: ["v1.0.0"], landmark: "v1.0.0", headline: "first" }];
    const named = renderToString(<PlanGantt planning={{ lanes: ["Feature"], bars: [] }}
      history={hist} branch="feat/plan-bar-note" locale="en" t={(x) => x} zoom={100} />);
    const bare = renderToString(<PlanGantt planning={{ lanes: ["Feature"], bars: [] }}
      history={hist} locale="en" t={(x) => x} zoom={100} />);
    // a branch shows its own name; no branch keeps the former label rather than a blank
    return named.includes("feat/plan-bar-note") && !named.includes(">Shipped<")
      && bare.includes("Shipped");
  })());

// ---- overlapping short bars ------------------------------------------------
// tested-by: REQ-PLANSTACK-1012 @unit
// Two ONE-DAY bars on consecutive days. Widening the day to 11px took week-long bars out
// of the floor entirely (a week is 71px of its own, starts are 77px apart), so the case
// that remains is the short one: a single day draws 5px and is floored to 30, while the
// next day starts 11px along. Dates say no overlap; pixels say 19px of it.
const stackPlan = {
  lanes: ["Feature"],
  bars: [
    { title: "primul lucru cu titlu lung", lane: "Feature", start: "2026-09-21", end: "2026-09-21" },
    { title: "al doilea lucru",            lane: "Feature", start: "2026-09-22", end: "2026-09-22" },
  ],
};
test("gantt: two one-day bars on consecutive days take separate rows",  // verifies: REQ-PLANSTACK-1012#CASE-1
  (() => {
    const a = { startIdx: 0, endIdx: 0 }, b = { startIdx: 1, endIdx: 1 };
    const extent = (x) => ({ left: x.startIdx * 11 + 3,
                             width: Math.max((x.endIdx - x.startIdx + 1) * 11 - 6, 30) });
    // dates say "no overlap"; pixels say otherwise, and pixels are what is painted
    const rows = stackBars([a, b], extent);
    const rowsByDate = stackBars([{ ...a }, { ...b }]);
    return rows === 2 && rowsByDate === 1;
  })());

test("gantt: bars that really are apart still share one row",  // verifies: REQ-PLANSTACK-1012#CASE-2
  (() => {
    // a full week each, a week apart: 71px of bar, 77px between starts, no clash at all —
    // which is what widening the day bought, and the stacker must not invent a row for it
    const a = { startIdx: 0, endIdx: 6 }, b = { startIdx: 7, endIdx: 13 };
    const extent = (x) => ({ left: x.startIdx * 11 + 3,
                             width: Math.max((x.endIdx - x.startIdx + 1) * 11 - 6, 30) });
    return stackBars([a, b], extent) === 1;
  })());

test("gantt: the chart itself stacks them, not just the helper",  // verifies: REQ-PLANSTACK-1012#CASE-1
  (() => {
    // The two checks above exercise stackBars directly, so they stay green even if
    // PlanGantt forgets to hand it `extent` — which is the whole fix. This asserts the
    // WIRING: render the clashing pair and read the two bars' `top` out of the markup.
    const html = renderToString(<PlanGantt planning={stackPlan} history={[]}
      locale="en" t={(x) => x} zoom={100} />);
    // React SSR writes inline styles as `top:10px`, no space, so the probe is a plain
    // substring: with both bars on row 0 the markup carries `top:10px` twice and
    // `top:36px` (PAD + ROW_H) not at all.
    const secondRow = (html.match(/top:68px/g) || []).length;   // PAD 10 + ROW_H 58
    if (!secondRow) { console.log("   (bars share a row — stacking not wired)"); }
    return secondRow >= 1;
  })());

test("gantt: the guides mark the work, not today or the milestones",  // verifies: REQ-PLANSTACK-1012#CASE-3
  (() => {
    const html = renderToString(<PlanGantt planning={{
      ...stackPlan,
      milestones: { "v9.9": { due: "2026-09-30" } },
    }} history={[]} locale="en" t={(x) => x} zoom={100} />);
    // the milestone keeps its header pill; what goes is the full-height dashed rule
    return html.includes("v9.9") && !html.includes("dashed var(--indigo-400)");
  })());

test("gantt: a guide stays in its bar's lane",  // verifies: REQ-PLANSTACK-1012#CASE-3
  (() => {
    // Drawn from the chart's top, a guide crossed the shipped band and every empty lane.
    // Inside the lane it is positioned top:0, bottom:0 and never at the header's height.
    const html = renderToString(<PlanGantt planning={{ ...stackPlan, lanes: ["Feature", "Fix"] }}
      history={[]} locale="en" t={(x) => x} zoom={100} />);
    const guides = html.match(/data-guide="(start|end)" style="[^"]*"/g) || [];
    return guides.length === 4 && guides.every((g) => g.includes("top:0;bottom:0"));
  })());

const cadencePlan = {
  lanes: ["Engine"],
  bars: [{ title: "a bar", lane: "Engine", start: "2026-09-13", end: "2026-09-30" }],
  cadence: { every: "week", on: "friday", lane: "Release" },
  releases: ["2026-09-18", "2026-09-25"],
};
const withCadence = renderToString(
  <PlanGantt planning={cadencePlan} locale="en" t={(s) => s} zoom={100} openSpec={noop} />);
const noCadence = renderToString(
  <PlanGantt planning={{ ...cadencePlan, cadence: undefined, releases: undefined }}
             locale="en" t={(s) => s} zoom={100} openSpec={noop} />);
const cadenceChecks = [
  ["cadence: a rule is drawn for every emitted release date",  // verifies: REQ-PLANCADENCE-1000#CASE-1
    (withCadence.match(/release · 2026-09-/g) || []).length === 2],
  ["cadence: a release is a tick on the ruler, not a line through the lanes",  // verifies: REQ-PLANCADENCE-1000#CASE-1
    // A weekly cadence drew one full-height rule per Friday across every lane, ruling
    // through the bars it was meant to date. The ruler tick carries the same date.
    !withCadence.includes("color-mix(in oklch, var(--fg-faint) 45%, transparent)")],
  ["cadence: a version is drawn in the release lane, and a date with no version draws nothing there",  // verifies: REQ-PLANCADENCE-1000#CASE-1
    (() => {
      const html = renderToString(<PlanGantt planning={{ ...cadencePlan, lanes: ["Engine", "Release"],
        milestones: { "v9.8.0": { due: "2026-09-25" } } }}
        locale="en" t={(s) => s} zoom={100} openSpec={noop} />);
      return html.includes('data-version="v9.8.0"') && !html.includes("rotate(45deg)");
    })()],
  ["cadence: no releases means no rules",  // verifies: REQ-PLANCADENCE-1000#CASE-2
    !noCadence.includes("release · ")],
  ["cadence: the chart places the emitted dates and computes none",  // verifies: REQ-PLANCADENCE-1000#CASE-1
    // 2026-09-20 is a Sunday, so a viewer doing its own Friday arithmetic could not
    // produce it. It renders because it was in the list.
    renderToString(<PlanGantt planning={{ ...cadencePlan, releases: ["2026-09-20"] }}
                              locale="en" t={(s) => s} zoom={100} openSpec={noop} />)
      .includes("release · 2026-09-20")],
];
for (const [label, ok] of cadenceChecks) test(label, ok);

// ---- selecting a shipped month or a version opens what is in it -----------
test("gantt: a shipped month and a version are selectable",  // verifies: REQ-HISTORY-1003#CASE-6
  (() => {
    const hist = [{ month: "2026-08", count: 2, first: "2026-08-03", last: "2026-08-20",
                    versions: ["v2.28.0", "v2.29.0"], landmark: "v2.29.0", headline: "x" }];
    const html = renderToString(<PlanGantt planning={{ lanes: ["Feature", "Release"],
      cadence: { every: "week", on: "friday", lane: "Release" }, releases: ["2026-09-25"],
      milestones: { "v9.8.0": { due: "2026-09-25" } }, bars: [] }}
      history={hist} locale="en" t={(x) => x} zoom={100} />);
    return /data-month="2026-08" role="button" tabindex="0"/.test(html)
      && /data-version="v9.8.0" role="button" tabindex="0"/.test(html);
  })());

test("gantt: an opened month lists every release with what it did",  // verifies: REQ-HISTORY-1003#CASE-6
  (() => {
    const html = renderToString(<ShippedNote t={(x) => x} onClose={noop} month={{
      month: "2026-08", count: 2, first: "2026-08-03", last: "2026-08-20",
      versions: ["v2.28.0", "v2.29.0"],
      entries: [{ version: "v2.29.0", date: "2026-08-20", headline: "Ten findings fixed" },
                { version: "v2.28.0", date: "2026-08-03", headline: "The viewer splits" }] }} />);
    return html.includes("Ten findings fixed") && html.includes("The viewer splits")
      && html.indexOf("v2.29.0") < html.indexOf("v2.28.0");
  })());

test("gantt: an opened version lists the work planned on it",  // verifies: REQ-PLANCADENCE-1000#CASE-1
  (() => {
    const bars = [{ key: "a", title: "on it", milestone: "v9.8.0", start: "2026-09-21", end: "2026-09-25" },
                  { key: "b", title: "elsewhere", milestone: "v9.9.0", start: "2026-09-28", end: "2026-10-02" }];
    const html = renderToString(<VersionNote version={{ ms: "v9.8.0", due: "2026-09-25", label: "L" }}
      bars={bars} t={(x) => x} onClose={noop} onPickBar={noop} />);
    return html.includes("on it") && !html.includes("elsewhere") && html.includes("2026-09-25");
  })());
// ---- ISO week header ------------------------------------------------------
// The week row is labelled with the week OF THE YEAR, not a count from the chart's left
// edge: the same calendar week has to read the same in two charts and in a conversation
// about it. 2026-09-13 is a Sunday, so it closes W37 alone and the next band is a full W38.
const weekChecks = [
  ["gantt: the header carries ISO week-of-year labels, not a count from the left edge",
    withCadence.includes(">W37<") && withCadence.includes(">W38<")],
  ["gantt: a range starting mid-week keeps the real week number, not W1",
    !withCadence.includes(">W1<")],
];
for (const [label, ok] of weekChecks) test(label, ok);

// ---- the Spec tab is gone; the Explorer is the one place a spec is read -----
const navHtml = renderToString(<App />);
test("nav: no Spec tab — the Explorer renders the same document",  // verifies: REQ-VIEWER-945#CASE-1
  !/>Spec</.test(navHtml) && navHtml.includes(">Explorer<"));

// ---- shipped history (REQ-HISTORY-1003) ------------------------------------
// The band is engine-computed rows placed on the plan's own timeline, left of today.
const HIST = [
  { month: "2026-06", count: 10, first: "2026-06-04", last: "2026-06-26",
    versions: ["v1.11.0", "v2.0.0", "v2.8.1"], landmark: "v2.0.0",
    headline: "Breaking - intent-verb CLI" },
  { month: "2026-07", count: 4, first: "2026-07-03", last: "2026-07-05",
    versions: ["v2.11.0", "v2.13.0"], landmark: "v2.13.0",
    headline: "Ranked requirement search" },
];
const withHist = renderToString(
  <PlanGantt planning={cadencePlan} history={HIST} locale="en" t={(s) => s} zoom={100} openSpec={noop} />);
const noHist = renderToString(
  <PlanGantt planning={cadencePlan} history={[]} locale="en" t={(s) => s} zoom={100} openSpec={noop} />);
const historyChecks = [
  ["history: one band row per shipped month, labelled by its landmark",  // verifies: REQ-HISTORY-1003#CASE-4
    withHist.includes(">Shipped<") && withHist.includes(">v2.0.0<") && withHist.includes(">v2.13.0<")],
  ["history: the month's headline is shown, not its version list",  // verifies: REQ-HISTORY-1003#CASE-1
    withHist.includes("Breaking - intent-verb CLI")],
  ["history: no history means no band",  // verifies: REQ-HISTORY-1003#CASE-5
    !noHist.includes(">Shipped<")],
  ["history: the chart reaches back to the first shipped month",
    // The plan's own bars start 2026-09-13; the band pulls the origin back to June.
    withHist.includes("Jun") && !noHist.includes("Jun")],
];
for (const [label, ok] of historyChecks) test(label, ok);

// ---- loadData forwards the WHOLE export (REQ-VIEWER-969) --------------------
// The bug this exists for: `loadData` copied the export key by key, and two keys
// added later — `roadmap` (v7.6.0) and `history` (v7.8.0) — were never added to that
// list. The engine emitted them, the page carried them in `window.__REQMAP_DATA__`,
// and the app never saw them, so the Horizons mode and the Shipped band silently did
// not render. Every other check adopts the export DIRECTLY, which is why all of them
// passed while the real viewer was wrong. This one goes through loadData.
const prevWindow = globalThis.window;
globalThis.window = {
  __REQMAP_DATA__: {
    engine_version: "test",
    nodes: json.nodes.slice(0, 3),
    roadmap: [{ name: "an item", horizon: "now", req: null, unpark: null, done: false }],
    history: [{ month: "2026-06", count: 2, first: "2026-06-01", last: "2026-06-20",
                versions: ["v1.0.0", "v1.1.0"], landmark: "v1.0.0", headline: "A month" }],
    planning: { releases: ["2026-06-30"], cadence: { every: "month", on: "last" } },
    todos: [], commands: [], repo: "t/t",
  },
};
// Not awaited: the inline branch adopts BEFORE it returns, and this bundle is CJS so
// top-level await is unavailable. If an await is ever introduced ahead of the
// adoption, these three checks fail loudly — which is the right answer, not a
// silent pass.
loadData();
globalThis.window = prevWindow;
// The badge read 0 the day this repo retired its own TODO.md, with ten open horizon
// items one click away — which reads as "nothing here".
const railAfterLoad = renderToString(<App />);
const loadChecks = [
  ["rail: the Roadmap badge counts horizons too, not only TODO.md items",  // verifies: REQ-VIEWER-999#CASE-1
    // The fixture has 0 todos and 1 open horizon item, so the badge must read exactly 1.
    (() => {
      const at = railAfterLoad.indexOf("Roadmap");
      const after = railAfterLoad.slice(at, at + 220).replace(/<!--[^>]*-->/g, "").replace(/<[^>]+>/g, "|");
      const n = (after.match(/\|+\s*(\d+)/) || [])[1];
      return n === "1";
    })()],
  ["loadData: the horizon plan survives adoption", ROADMAP.length === 1],
  ["loadData: the shipped history survives adoption", HISTORY.length === 1],
  ["loadData: the planning sidecar survives adoption", (TARGETS?.releases || []).length === 1],
];
for (const [label, ok] of loadChecks) test(label, ok);
// Put the real dataset back for anything after this point.
adoptMapExport({ ...json, nodes: json.nodes.map(adaptNode) });

console.log(failures ? `\n${failures} failure(s)` : "\nall render checks passed");
process.exit(failures ? 1 : 0);

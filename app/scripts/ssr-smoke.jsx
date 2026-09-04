// tested-by: ARCH-VIEWER-007  // tested-by: REQ-TRANSLATE-938  // tested-by: REQ-VIEWER-942  // tested-by: REQ-VIEWER-943
// tested-by: ARCH-SEARCH-036  // tested-by: REQ-VIEWER-944  // tested-by: REQ-VIEWER-945  // tested-by: REQ-VIEWER-966
// tested-by: REQ-VIEWER-964  // tested-by: REQ-SEARCH-965
/* Render-time smoke test: server-render every view against the engine-adapted
 * dataset and assert real content appears. Catches render-throws and bad data
 * assumptions the build cannot. Bundled + run by run-ssr-smoke.mjs. */
import { renderToString } from "react-dom/server";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import App from "../src/App.jsx";
import { rankRequirements, searchRequirements } from "../src/lib/search.js";
import { setRegistry, REQUIREMENTS } from "../src/lib/data.js";
import { adaptNode } from "../src/lib/loadData.js";
import { MapView } from "../src/views/MapView.jsx";
import { ProblemsView, computeProblems, computeQuestions } from "../src/views/ProblemsView.jsx";
import { RoadmapView } from "../src/views/RoadmapView.jsx";
import { SpecView } from "../src/views/SpecView.jsx";
import { ExplorerView } from "../src/views/ExplorerView.jsx";
import { CommandsView } from "../src/views/CommandsView.jsx";
import { setCommands } from "../src/lib/data.js";
import { I18nProvider, translate } from "../src/lib/i18n.jsx";
import { computeLayout } from "../src/lib/layout.js";
import {
  buildHierarchy, defaultExpanded, allExpanded, flattenTree, ancestorsOf,
  keepSetFor, openQuestions, levelOf,
} from "../src/lib/tree.js";

// feed the real engine export through the adapter, exactly as the browser would
// (run from the app/ directory: `node scripts/run-ssr-smoke.mjs`)
const json = JSON.parse(readFileSync(resolve(process.cwd(), "public/data.json"), "utf8"));
setRegistry(json.nodes.map(adaptNode));

const noop = () => {};
const cases = {
  App: <App />,
  MapView: <MapView selId="ARCH-PARSE-001" setSelId={noop} openSpec={noop} highlightId={null} setHighlightId={noop} />,
  ProblemsView: <ProblemsView openSpec={noop} />,
  RoadmapView: <RoadmapView openSpec={noop} />,
  SpecView: <SpecView selId="ARCH-MAP-007" setSelId={noop} />,
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

// ---- cross-references and header fields (REQ-VIEWER-944) -------------------
// `[[ID]]` is how an author points one requirement at another. Rendered
// literally it was a pair of brackets leading nowhere, on every architecture
// requirement in the corpus.
setRegistry([
  adaptNode({ id: "LINK-SRC-001", title: "source", area: "LINK", layer: "feature", status: "confirmed",
    intent: "i", contract: ['see [[LINK-DST-002]] and [[LINK-GONE-999]] <b>x</b>'],
    acc: [], members: [], deps: [], used_by: [] }),
  adaptNode({ id: "LINK-DST-002", title: "target", area: "LINK", layer: "feature", status: "confirmed",
    intent: "i", contract: ["a clause"], acc: [], members: [], deps: [], used_by: [] }),
]);
const linkSpec = renderToString(<SpecView selId="LINK-SRC-001" setSelId={noop} />);
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
setRegistry(json.nodes.map(adaptNode));
const spec = (locale) => renderToString(
  <I18nProvider initialLocale={locale}>
    <SpecView selId="ARCH-MAP-007" setSelId={noop} />
  </I18nProvider>);
const specEn = spec("en"), specRo = spec("ro");
const reqUnderTest = REQUIREMENTS.find(r => r.id === "ARCH-MAP-007");
const i18nChecks = [
  ["i18n: English is the default rendering", specEn.includes("Where — Members in code")],  // verifies: REQ-VIEWER-943#CASE-1
  ["i18n: Romanian translates a section header",  // verifies: REQ-VIEWER-943#CASE-2
    specRo.includes("Unde — Membri în cod") && !specRo.includes("Where — Members in code")],
  ["i18n: an unknown string falls back to English rather than blanking",  // verifies: REQ-VIEWER-943#CASE-3
    translate("ro", "Not In The Dictionary") === "Not In The Dictionary"],
  ["i18n: placeholders interpolate", translate("ro", "{n} members bound", { n: 7 }) === "7 membri legați"],  // verifies: REQ-VIEWER-943#CASE-4
  // The boundary the feature exists to respect: the artifact under review is never translated.
  ["i18n: requirement title stays in the author's language", specRo.includes(reqUnderTest.title)],  // verifies: REQ-VIEWER-943#CASE-5
  ["i18n: engine vocabulary stays literal (status value, not a translation)",  // verifies: REQ-VIEWER-943#CASE-6
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
  ["i18n content: cached en translation renders the translated title", translatedSpecEn.includes("Original title")],  // verifies: REQ-TRANSLATE-938#CASE-5
  ["i18n content: cached translation shows the machine-translated badge", translatedSpecEn.includes("machine-translated, unreviewed")],  // verifies: REQ-TRANSLATE-938#CASE-5
  ["i18n content: no cache entry for ro falls back to the author's title", translatedSpecRo.includes("Titlu original") && !translatedSpecRo.includes("Original title")],  // verifies: REQ-TRANSLATE-938#CASE-5
  ["i18n content: no cache entry at all shows no badge", noCacheSpecEn.includes("Titlu f") && !noCacheSpecEn.includes("machine-translated, unreviewed")],  // verifies: REQ-TRANSLATE-938#CASE-5
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
setRegistry(json.nodes.map(adaptNode));
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
  ["problems: an empty inbox renders the named empty state, not a badge",
    renderToString(<ProblemsView openSpec={noop} />).includes("Nothing to fix.")],
];
for (const [label, ok] of explorerChecks) test(label, ok);

// ---- registry tally scopes the outline (REQ-VIEWER-945) ---------------------
setRegistry(json.nodes.map(adaptNode));
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
setCommands(CLI_FIXTURE);
const cmdsEn = renderToString(<I18nProvider initialLocale="en"><CommandsView /></I18nProvider>);
const cmdsRo = renderToString(<I18nProvider initialLocale="ro"><CommandsView /></I18nProvider>);
setCommands([]);
const cmdsEmpty = renderToString(<I18nProvider initialLocale="en"><CommandsView /></I18nProvider>);
setCommands(CLI_FIXTURE);
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
setRegistry([
  adaptNode({ id: "Q-ASKED-001", title: "asked", area: "Q", layer: "feature", status: "confirmed",
    intent: "i", contract: ["a clause"], acc: [], members: [{ role: "implements", loc: "a.py:1" }],
    verify: ["Is a stale tested-by range an error or a warning?"], deps: [], used_by: [] }),
  adaptNode({ id: "Q-QUIET-002", title: "quiet", area: "Q", layer: "feature", status: "confirmed",
    intent: "i", contract: ["a clause"], acc: [], members: [{ role: "implements", loc: "b.py:1" }],
    verify: ["None — authored from known intent."], deps: [], used_by: [] }),
]);
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

setRegistry(json.nodes.map(adaptNode));   // restore the real dataset for anything after this point

console.log(failures ? `\n${failures} failure(s)` : "\nall render checks passed");
process.exit(failures ? 1 : 0);

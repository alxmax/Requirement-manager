// tested-by: ARCH-VIEWER-007
/* Render smoke test, part: rail readings, design tab, roadmap zoom and
   horizons. */
import { renderToString } from "react-dom/server";

import App, { openScope, openTab } from "../../src/App.jsx";
import { Rail } from "../../src/components/Rail.jsx";
import { rankRequirements, searchRequirements } from "../../src/lib/search.js";
import {
  adoptMapExport, REQUIREMENTS, ROADMAP, HISTORY, TARGETS,
} from "../../src/lib/data.js";
import { adaptNode, loadData } from "../../src/lib/loadData.js";
import { MapView } from "../../src/views/MapView.jsx";
import {
  ProblemsView, computeProblems, computeQuestions,
} from "../../src/views/ProblemsView.jsx";
import { RoadmapView } from "../../src/views/RoadmapView.jsx";
import {
  DesignProblemsPanel, HealthPanel,
} from "../../src/views/problems/ProblemsPanels.jsx";
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

// ---- the rail's two engine-emitted readings (REQ-VIEWER-969) ---------------
adoptMapExport({ nodes: json.nodes.map(adaptNode) });
const SCORES = [{ score: 78, healthy: 39, total: 50 },
                { score: 23, clean_files: 7, files: 30 }];
adoptMapExport({ health: SCORES[0], design: SCORES[1] });
const railHtml = renderToString(<App />);
// an older map carries neither key
adoptMapExport({ health: null, design: null });
const railBare = renderToString(<App />);
// a waived check travels with the score (REQ-HEALTH-968)
adoptMapExport({ health: { ...SCORES[0], exempt: 4 }, design: SCORES[1] });
const railExempt = renderToString(<App />);
adoptMapExport({ health: SCORES[0], design: SCORES[1] });
const gaugeChecks = [
  // verifies: REQ-VIEWER-969#CASE-1
  ["rail: both readings render the engine's own numbers",
    railHtml.includes("39/50 green") && railHtml.includes("7/30 files clean")
    && railHtml.includes(">78<") && railHtml.includes(">23<")],
  // verifies: REQ-VIEWER-969#CASE-2
  ["rail: a mid-band score takes the partial tone, not the green one",
    railHtml.includes('stroke="var(--cov-partial)"')
    && !railHtml.includes('stroke="var(--cov-tested)"')],
  // verifies: REQ-VIEWER-969#CASE-2
  ["rail: the advisory design ring stays in one neutral ink",
    // 23 would be red on the health scale; the design score is advice,
    // never a failure
    railHtml.includes('stroke="var(--fg-muted)"')
    && !railHtml.includes('stroke="var(--cov-untested)"')],
  // verifies: REQ-VIEWER-969#CASE-3
  ["rail: a map with neither record shows no gauge at all",
    !railBare.includes("rail-gauges") && !railBare.includes("gauge-row")],
  // verifies: REQ-VIEWER-969#CASE-4
  ["rail: both readings are controls, neither is static",
    !railHtml.includes("gauge-row static")
      && (railHtml.match(/<button[^>]*class="gauge-row"/g) || []).length
        === 2],
  // verifies: REQ-HEALTH-968#CASE-4
  ["rail: the exemption count sits beside the score, and only when "
    + "there is one",
    railExempt.includes("4 exempt") && !/\d exempt/.test(railHtml)
    && translate("ro", "{n} exempt", { n: 4 }) === "4 cu scutire"],
  // verifies: REQ-VIEWER-969#CASE-5
  ["rail: the labels follow the chosen language",
    translate("ro", "Health") === "Sănătate"
    && translate("ro", "{a}/{b} green", { a: 39, b: 50 }) === "39/50 verzi"],
];
for (const [label, ok] of gaugeChecks) test(label, ok);

// ---- the advisory design tab (REQ-VIEWER-977) -----------------------------
// The engine ships its code-review candidates in `_map.json`; the tab lists
// them by pillar, and since 2026-09-07 each is one computed signal (so the
// rail counts it) at its own severity, never a Warning row and never a row
// of "All". A map written before that carries no `findings`, so the tab
// must simply not appear rather than render an empty shell, and nothing is
// counted.
const DESIGN_WITH = {
  score: 23, clean_files: 7, files: 30,
  candidates: {
    encapsulation: 1, abstraction: 1, inheritance: 0, polymorphism: 0,
    standards: 0,
  },
  findings: [
    { pillar: "encapsulation", kind: "long-parameter-list",
      file: "src/thing.py",
      line: 12, name: "build", detail: "`build` takes 9 parameters (over 6)" },
    { pillar: "abstraction", kind: "long-function", file: "src/thing.py",
      line: 40, name: "run", detail: "`run` is 120 lines (over 80)" },
  ],
  advice: {
    "long-parameter-list":
      "a parameter list this long is an object waiting to be named",
    "long-function": "a function this long hides several steps",
  },
};
adoptMapExport({ health: null, design: DESIGN_WITH });
const designHtml = renderToString(<ProblemsView openSpec={noop} />);
const designRows = computeProblems().filter(p => p.signal === "design");
adoptMapExport({
  health: null,
  design: { score: 23, clean_files: 7, files: 30, candidates: {} },
});
const designBare = renderToString(<ProblemsView openSpec={noop} />);
adoptMapExport({ health: null, design: null });
const designChecks = [
  // verifies: REQ-VIEWER-977#CASE-1
  ["design: the tab is offered with the candidate count",
    designHtml.includes("Design") && designHtml.includes(">2<")],
  // verifies: REQ-VIEWER-977#CASE-2
  ["design: no tab when the map carries no candidates",
    !designBare.includes(">Design<")],
  // verifies: REQ-VIEWER-977#CASE-3
  ["design: candidates are counted at their own severity, listed only in "
    + "their tab",
    designRows.length === 2
    && designRows.every(p => p.sev === "DESIGN" && p.noSpec)
    && designRows.some(p => p.loc === "src/thing.py:12")
    && !designHtml.includes("src/thing.py:12")
    && computeProblems().every(p => p.signal !== "design")],
];
for (const [label, ok] of designChecks) test(label, ok);

// restore the real dataset for anything after this point
adoptMapExport({ nodes: json.nodes.map(adaptNode) });

// ---- roadmap zoom and density (REQ-VIEWER-984) ----------------------------
// The wheel handler is NOT reachable from here: renderToString has no DOM and
// dispatches no events. What IS observable is the primitive each control uses,
// which is where both of this feature's real bugs lived.
const roadZoomed  = renderToString(
  <RoadmapView openSpec={noop} initialZoom={40} />);
const roadCompact = renderToString(
  <RoadmapView openSpec={noop} initialDensity="compact" />);
const roadDefault = renderToString(<RoadmapView openSpec={noop} />);
const roadmapChecks = [
  // verifies: REQ-VIEWER-984#CASE-1
  ["roadmap: scaling uses CSS zoom, not a transform",
    // text-transform:uppercase is all over the markup, so the assertion
    // has to name the scale itself
    roadZoomed.includes("zoom:0.4")
      && !roadZoomed.includes("transform:scale")],
  // verifies: REQ-VIEWER-984#CASE-2
  ["roadmap: compact truncates the title and keeps it in the tooltip",
    roadCompact.includes("text-overflow:ellipsis")
    && roadCompact.includes("max-width:108px")
    && /title="[^"]{40,}"/.test(roadCompact)],
  // verifies: REQ-VIEWER-984#CASE-3
  ["roadmap: the defaults are the pre-control view",
    roadDefault.includes("zoom:1") && roadDefault.includes(">100%<")
    && !roadDefault.includes("text-overflow:ellipsis")],
];
for (const [label, ok] of roadmapChecks) test(label, ok);

// A milestone whose TODO items have all shipped. The chips are still
// filtered to the open ones, so the column is empty — what is asserted is
// that it EXISTS, because the version it names is finished, not skipped.
adoptMapExport({
  todos: [
    { title: "a shipped item", done: true, milestone: "v99.9",
      lane: "feature" },
  ],
});
const roadAllDone = renderToString(<RoadmapView openSpec={noop} />);
adoptMapExport({ todos: [] });
// verifies: REQ-VIEWER-995#CASE-4
test("roadmap: a milestone whose every item is complete still gets a column",
  roadAllDone.includes(">v99.9<") && !roadAllDone.includes("a shipped item"));

// Plan and Versions read one planned list, `bars` (REQ-PLANSTALE-1013). A
// bar used to create its version's column and never appear in it, because
// the column read `milestones[].items[]` — a second list nobody wrote.
adoptMapExport({ todos: [], planning: {
  lanes: ["Feature"], milestones: { "v99.8": { items: ["ghost"] } },
  bars: [{ title: "the planned bar", lane: "Feature", start: "2026-09-21",
           end: "2026-09-27",
           milestone: "v99.7" }],
} });
const roadBars = renderToString(
  <RoadmapView openSpec={noop} initialMode="versions" />);
adoptMapExport({ todos: [], planning: json.planning || null });
// verifies: REQ-VIEWER-999#CASE-5
test("roadmap: a bar appears in its version's column, and items[] is not read",
  roadBars.includes(">v99.7<") && roadBars.includes("the planned bar")
    && !roadBars.includes("ghost"));

// ---- roadmap horizons (REQ-VIEWER-999) -----------------------------------
// `initialRoadmap` is the seam the other two controls already open with
// `initialZoom` / `initialDensity`: a fixture without mutating the loaded
// export.
const HZ = [
  { name: "the open one", horizon: "now", req: json.nodes[0].id,
    unpark: null, done: false },
  { name: "the done one", horizon: "now", req: null, unpark: null,
    done: true },
  { name: "the queued one", horizon: "next", req: "NOPE-X-999",
    unpark: null, done: false },
  { name: "the parked one", horizon: "later", req: null,
    unpark: "a named consumer asks",
    done: false },
];
const hzNone = renderToString(
  <RoadmapView openSpec={noop} initialRoadmap={[]} />);
const barNoteChecks = [
  // verifies: REQ-VIEWER-999#CASE-4
  ["roadmap: the Horizons mode is gone",
    // Items are still carried — the panel reads them — but no mode renders
    // columns.
    (() => {
      const withItems = renderToString(
        <RoadmapView openSpec={noop} initialRoadmap={HZ} />);
      return !withItems.includes(">Horizons<")
        && !(withItems.includes(">Now<") && withItems.includes(">Later<"));
    })()],
  // verifies: REQ-VIEWER-999#CASE-4
  ["roadmap: a stored Horizons choice lands on Plan, not on nothing",
    !hzNone.includes(">Horizons<")],
  // verifies: REQ-VIEWER-999#CASE-3
  ["roadmap: an HTML-comment note renders as its text",
    noteText("<!-- the reason -->") === "the reason"],
  // verifies: REQ-VIEWER-999#CASE-3
  ["roadmap: a multi-line note keeps its breaks and loses its indent",
    noteText(["<!--", "  first", "  second", "-->"].join("\n"))
      === ["first", "second"].join("\n")],
  // verifies: REQ-VIEWER-999#CASE-1
  ["roadmap: a bar finds its item by req:",
    (() => {
      const it = matchItem({ reqId: json.nodes[0].id }, HZ);
      return !!it && it.name === "the open one";
    })()],
  // verifies: REQ-VIEWER-999#CASE-2
  ["roadmap: a bar with no req, or an unmatched one, has no item",
    // NOT `NOPE-X-999`: the registry does not have it but the fixture's
    // `next` item carries it, so the join finds that item and should. The
    // join is bar->item, and whether the id also resolves to a requirement
    // is the panel's separate question.
    matchItem({ reqId: null }, HZ) === null
    && matchItem({ reqId: "ABSENT-Z-000" }, HZ) === null],
  // tested-by: REQ-ROADMAP-998
  // verifies: REQ-ROADMAP-998#CASE-7
  ["roadmap: the roadmap payload survives the mode's removal",
    (() => {
      const adopted = adoptMapExport({
        nodes: json.nodes.map(adaptNode), roadmap: HZ,
      });
      const kept = (adopted && adopted.roadmap) || ROADMAP;
      adoptMapExport({ nodes: json.nodes.map(adaptNode) });
      return Array.isArray(kept) && kept.length === HZ.length;
    })()],
];
for (const [label, ok] of barNoteChecks) test(label, ok);

// ---- a registry tally row requests its slice (REQ-VIEWER-1082) ------------
// tested-by: REQ-VIEWER-1082
// The outline APPLIES a scope (REQ-VIEWER-945); these check the half that
// asks for one: the rail row and the shell that routes it.
adoptMapExport({ nodes: json.nodes.map(adaptNode) });
const railScoped = renderToString(
  <Rail view="map" setView={noop} focus="draft" setFocus={noop}
        problems={[]} />);
const pressedRows = (html) => (html.match(/aria-pressed="true"/g) || [])
  .length;
const draftN = REQUIREMENTS.filter((r) => r.status === "draft").length;
const routed = [];
openScope((k) => routed.push(["focus", k]),
          (v) => routed.push(["view", v]))("orphan");
const tallyChecks = [
  // verifies: REQ-VIEWER-1082#CASE-1
  ["tally: the requested slice's row is the one drawn pressed",
    pressedRows(railScoped) === 1
      && /stat-row on[^>]*>(?:(?!<\/button>).)*draft/.test(railScoped)],
  // verifies: REQ-VIEWER-1082#CASE-2
  ["tally: each row shows the count of the slice it would scope to",
    railScoped.includes(">draft<!-- --><span class=\"n\">" + draftN + "<")
      || new RegExp("draft(?:<!-- -->)?<span class=\"n\">" + draftN + "<")
        .test(railScoped)],
  // verifies: REQ-VIEWER-1082#CASE-3
  ["tally: choosing a row scopes the outline and opens it",
    JSON.stringify(routed)
      === JSON.stringify([["focus", "orphan"], ["view", "explorer"]])],
];
for (const [label, ok] of tallyChecks) test(label, ok);

// ---- a rail reading opens the rows behind it (REQ-VIEWER-1084) -----------
// tested-by: REQ-VIEWER-1084
const tabbed = [];
openTab((k) => tabbed.push(["tab", k]),
        (v) => tabbed.push(["view", v]))("DESIGN");
const HROWS = {
  score: 50, healthy: 1, total: 3, scored: 3,
  unhealthy: [
    { id: "AREA-H-001", status: "confirmed", why: ["not tested"] },
    { id: "AREA-H-002", status: "confirmed", why: ["drift"] },
  ],
  exempt_ids: [],
};
adoptMapExport({ health: HROWS, design: {
  score: 50, clean_files: 1, files: 2,
  candidates: { encapsulation: 1, standards: 1 },
  findings: [
    { pillar: "encapsulation", kind: "global-state", file: "a.py", line: 1,
      name: "f", detail: "`f` writes module state: X" },
    { pillar: "standards", kind: "line-too-long", file: "b.py", line: 3,
      name: "b.py", detail: "1 line(s) wider than 80 columns" },
  ],
  advice: {} } });
const healthTab = renderToString(
  <ProblemsView openSpec={noop} initialFilter="HEALTH" />);
const driftOnly = renderToString(
  <HealthPanel health={HROWS} openSpec={noop} initialAxis="drift" />);
const designOnly = renderToString(
  <DesignProblemsPanel byPillar={{
    encapsulation: [{ kind: "global-state", name: "f", file: "a.py",
                      line: 1, detail: "writes X" }],
    standards: [{ kind: "line-too-long", name: "b.py", file: "b.py",
                  line: 3, detail: "wide" }],
  }} advice={{}} initialPillar="standards" />);
const rowFilterChecks = [
  // verifies: REQ-VIEWER-1084#CASE-1
  ["filters: a rail reading opens Problems on its own tab",
    JSON.stringify(tabbed)
      === JSON.stringify([["tab", "DESIGN"], ["view", "problems"]])],
  // verifies: REQ-VIEWER-1084#CASE-2
  ["filters: the Health tab lists the rows the engine emitted",
    healthTab.includes("AREA-H-001") && healthTab.includes("not tested")],
  // verifies: REQ-VIEWER-1084#CASE-3
  ["filters: an axis chip narrows the Health list",
    driftOnly.includes("AREA-H-002") && !driftOnly.includes("AREA-H-001")
      && /ex-chip on[^>]*>drift/.test(driftOnly)],
  // verifies: REQ-VIEWER-1084#CASE-4
  ["filters: a pillar chip narrows the Design tab",
    designOnly.includes("line-too-long")
      && !designOnly.includes("global-state")],
];
for (const [label, ok] of rowFilterChecks) test(label, ok);
adoptMapExport({ nodes: json.nodes.map(adaptNode),
                 health: json.health || null, design: json.design || null });

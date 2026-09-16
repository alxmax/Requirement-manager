// tested-by: ARCH-VIEWER-007
/* Render smoke test, part: nav, shipped history, loadData. */
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
import { cadencePlan } from "./plan.jsx";

// ---- the Spec tab is gone; the Explorer is the one place a spec is read -----
const navHtml = renderToString(<App />);
// verifies: REQ-VIEWER-945#CASE-1
test("nav: no Spec tab — the Explorer renders the same document",
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
  <PlanGantt planning={cadencePlan} history={HIST} locale="en" t={(s) => s} zoom={100}
             openSpec={noop} />);
const noHist = renderToString(
  <PlanGantt planning={cadencePlan} history={[]} locale="en" t={(s) => s} zoom={100}
             openSpec={noop} />);
const historyChecks = [
  // verifies: REQ-HISTORY-1003#CASE-4
  ["history: one band row per shipped month, labelled by its landmark",
    withHist.includes(">Shipped<") && withHist.includes(">v2.0.0<")
      && withHist.includes(">v2.13.0<")],
  // verifies: REQ-HISTORY-1003#CASE-1
  ["history: the month's headline is shown, not its version list",
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
  // verifies: REQ-VIEWER-999#CASE-1
  ["rail: the Roadmap badge counts horizons too, not only TODO.md items",
    // The fixture has 0 todos and 1 open horizon item, so the badge must read exactly 1.
    (() => {
      const at = railAfterLoad.indexOf("Roadmap");
      const after = railAfterLoad.slice(at, at + 220)
        .replace(/<!--[^>]*-->/g, "").replace(/<[^>]+>/g, "|");
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

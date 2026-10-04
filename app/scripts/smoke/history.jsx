// tested-by: ARCH-VIEWER-007
/* Render smoke test, part: nav, shipped history, loadData. */
import { renderToString } from "react-dom/server";

import App from "../../src/App.jsx";
import { rankRequirements, searchRequirements } from "../../src/lib/search.js";
import {
  adoptMapExport, REQUIREMENTS, ROADMAP, HISTORY, TARGETS,
} from "../../src/lib/data.js";
import { adaptNode, loadData } from "../../src/lib/loadData.js";
import {
  ProblemsView, computeProblems, computeQuestions,
} from "../../src/views/ProblemsView.jsx";
import { RoadmapView } from "../../src/views/RoadmapView.jsx";
import {
  PlanGantt, noteText, matchItem, ShippedNote, ReleaseNote, VersionNote,
} from "../../src/views/roadmap/PlanGantt.jsx";
import { stackBars, buildDayBands } from "../../src/lib/timeline.js";
import {
  layoutPlan, shipExtent, PX, LABEL_CHAR,
} from "../../src/views/roadmap/ganttLayout.js";
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

// ---- shipped history (REQ-HISTORY-1081) ------------------------------------
// tested-by: REQ-HISTORY-1081
// The band is engine-computed rows placed on the plan's own timeline, left
// of today.
const rel = (version, day, headline) => ({
  version, date: day, headline, first_commit: day, last_commit: day,
});
const HIST = [
  { month: "2026-06", count: 3, first: "2026-06-04", last: "2026-06-26",
    versions: ["v1.11.0", "v2.0.0", "v2.8.1"], landmark: "v2.0.0",
    headline: "Breaking - intent-verb CLI",
    entries: [
      rel("v1.11.0", "2026-06-04", "old"),
      rel("v2.0.0", "2026-06-15", "Breaking - intent-verb CLI"),
      rel("v2.8.1", "2026-06-26", "later"),
    ] },
  { month: "2026-07", count: 2, first: "2026-07-03", last: "2026-07-05",
    versions: ["v2.11.0", "v2.13.0"], landmark: "v2.13.0",
    headline: "Ranked requirement search",
    entries: [
      rel("v2.11.0", "2026-07-03", "search"),
      rel("v2.13.0", "2026-07-05", "Ranked requirement search"),
    ] },
];
const withHist = renderToString(
  <PlanGantt planning={cadencePlan} history={HIST} locale="en"
             t={(s) => s} zoom={100} openSpec={noop} />);
const noHist = renderToString(
  <PlanGantt planning={cadencePlan} history={[]} locale="en"
             t={(s) => s} zoom={100} openSpec={noop} />);
const historyChecks = [
  // verifies: REQ-HISTORY-1081#CASE-1
  ["history: one block per shipped release, labelled by its version",
    withHist.includes(">Shipped<")
      && withHist.includes('data-release="v2.0.0"')
      && withHist.includes('data-release="v2.13.0"')
      && !withHist.includes("data-month=")],
  // verifies: REQ-HISTORY-1081#CASE-2
  ["history: the block shows the version and not the headline",
    withHist.includes('data-release="v2.0.0"')
      && !withHist.includes("Breaking - intent-verb CLI")
      && !withHist.includes("Ranked requirement search")],
  ["history: no history means no band",  // verifies: REQ-HISTORY-1081#CASE-3
    !noHist.includes(">Shipped<")],
  ["history: the chart reaches back to the first shipped month",
    // The plan's own bars start 2026-09-13; the band pulls the origin back
    // to June.
    withHist.includes("Jun") && !noHist.includes("Jun")],
];
for (const [label, ok] of historyChecks) test(label, ok);

// verifies: REQ-HISTORY-1081#CASE-5
test("history: a second row only where the dates overlap", () => {
  const month = (entries) => [{
    month: "2026-06", count: entries.length, first: "2026-06-01",
    last: "2026-06-30", versions: entries.map((e) => e.version),
    landmark: entries[0].version, headline: "h", entries,
  }];
  const row = (lay, version) =>
    lay.pastBars.find((b) => b.version === version).subRow;
  const apart = layoutPlan({ lanes: ["Feature"] }, month([
    { version: "v1", date: "2026-06-10", headline: "a",
      first_commit: "2026-06-01", last_commit: "2026-06-10" },
    { version: "v2", date: "2026-06-25", headline: "b",
      first_commit: "2026-06-20", last_commit: "2026-06-25" },
  ]), "en");
  const over = layoutPlan({ lanes: ["Feature"] }, month([
    { version: "v1", date: "2026-06-15", headline: "a",
      first_commit: "2026-06-01", last_commit: "2026-06-15" },
    { version: "v2", date: "2026-06-20", headline: "b",
      first_commit: "2026-06-10", last_commit: "2026-06-20" },
  ]), "en");
  return row(apart, "v1") === row(apart, "v2")
    && row(over, "v1") !== row(over, "v2");
});

// verifies: REQ-HISTORY-1081#CASE-2
test("history: the note shows the headline the block omits", () => {
  const words = "Breaking - intent-verb CLI";
  const note = renderToString(
    <ReleaseNote release={{
      version: "v2.0.0", start: "2026-06-02", end: "2026-06-02", headline: words,
    }} t={(s) => s} onClose={noop} />);
  return note.includes(words) && note.includes('data-note="release"');
});

// verifies: REQ-HISTORY-1081#CASE-6
test("history: a one-day release widens to its version", () => {
  const words = "Re-seed consumer repos with the scaffold page inline";
  const lay = layoutPlan({ lanes: ["Feature"] }, [{
    month: "2026-06", count: 2, first: "2026-06-14", last: "2026-06-15",
    versions: ["v1.35.0", "v2.0.0"], landmark: "v1.35.0", headline: words,
    entries: [
      { version: "v1.35.0", date: "2026-06-14", headline: words,
        first_commit: "2026-06-14", last_commit: "2026-06-14" },
      { version: "v2.0.0", date: "2026-06-15", headline: "Breaking change",
        first_commit: "2026-06-15", last_commit: "2026-06-15" },
    ],
  }], "en");
  const wide = lay.pastBars.find((b) => b.version === "v1.35.0");
  const next = lay.pastBars.find((b) => b.version === "v2.0.0");
  return shipExtent(wide).width > PX
    && shipExtent(wide).width < words.length * LABEL_CHAR
    && wide.subRow !== next.subRow;
});

// verifies: REQ-HISTORY-1081#CASE-7
test("history: patch releases of one minor share a vX.Y.x block", () => {
  const lay = layoutPlan({ lanes: ["Feature"] }, [{
    month: "2026-09", count: 4, first: "2026-09-01", last: "2026-09-28",
    versions: ["v7.21.0", "v7.21.1", "v7.21.10", "v7.22.0"],
    landmark: "v7.21.0", headline: "x",
    entries: [
      { version: "v7.21.10", date: "2026-09-20", headline: "ten",
        first_commit: "2026-09-18", last_commit: "2026-09-20" },
      { version: "v7.21.1", date: "2026-09-10", headline: "one",
        first_commit: "2026-09-08", last_commit: "2026-09-10" },
      { version: "v7.21.0", date: "2026-09-02", headline: "zero",
        first_commit: "2026-09-01", last_commit: "2026-09-02" },
      { version: "v7.22.0", date: "2026-09-28", headline: "next",
        first_commit: "2026-09-25", last_commit: "2026-09-28" },
    ],
  }], "en");
  const group = lay.pastBars.find((b) => b.version === "v7.21.x");
  const alone = lay.pastBars.find((b) => b.version === "v7.22.0");
  return lay.pastBars.length === 2 && group && alone
    && group.start === "2026-09-01" && group.end === "2026-09-20"
    && group.members.map((m) => m.version).join()
      === "v7.21.0,v7.21.1,v7.21.10";
});

// verifies: REQ-HISTORY-1081#CASE-6
test("history: releases that start on one day share a range block", () => {
  const day = "2026-09-06";
  const entry = (version, start, end) => ({
    version, date: end || start, headline: "h",
    first_commit: start, last_commit: end || start,
  });
  const lay = layoutPlan({ lanes: ["Feature"] }, [{
    month: "2026-09", count: 4, first: "2026-09-06", last: "2026-09-08",
    versions: ["v5.10.0", "v5.10.1", "v6.3.0", "v6.4.0"],
    landmark: "v6.3.0", headline: "x",
    entries: [
      entry("v5.10.1", day),
      entry("v6.3.0", day),
      entry("v5.10.0", day),
      entry("v6.4.0", "2026-09-08"),
    ],
  }], "en");
  const range = lay.pastBars.find((b) => b.version === "v5.10.x-v6.3.0");
  const alone = lay.pastBars.find((b) => b.version === "v6.4.0");
  return lay.pastBars.length === 2 && range && alone
    && range.start === day
    && range.members.map((m) => m.version).join() === "v5.10.0,v5.10.1,v6.3.0";
});

// ---- loadData forwards the WHOLE export (REQ-VIEWER-969) --------------------
// The bug this exists for: `loadData` copied the export key by key, and two
// keys added later — `roadmap` (v7.6.0) and `history` (v7.8.0) — were never
// added to that list. The engine emitted them, the page carried them in
// `window.__REQMAP_DATA__`, and the app never saw them, so the Horizons
// mode and the Shipped band silently did not render. Every other check
// adopts the export DIRECTLY, which is why all of them passed while the
// real viewer was wrong. This one goes through loadData.
const prevWindow = globalThis.window;
globalThis.window = {
  __REQMAP_DATA__: {
    engine_version: "test",
    nodes: json.nodes.slice(0, 3),
    roadmap: [
      { name: "an item", horizon: "now", req: null, unpark: null, done: false },
    ],
    history: [{ month: "2026-06", count: 2, first: "2026-06-01",
                last: "2026-06-20",
                versions: ["v1.0.0", "v1.1.0"], landmark: "v1.0.0",
                headline: "A month" }],
    planning: {
      releases: ["2026-06-30"], cadence: { every: "month", on: "last" },
    },
    todos: [], commands: [], repo: "t/t",
  },
};
// Not awaited: the inline branch adopts BEFORE it returns, and this bundle
// is CJS so top-level await is unavailable. If an await is ever introduced
// ahead of the adoption, these three checks fail loudly — which is the
// right answer, not a silent pass.
loadData();
globalThis.window = prevWindow;
// The badge read 0 the day this repo retired its own TODO.md, with ten open
// horizon items one click away — which reads as "nothing here".
const railAfterLoad = renderToString(<App />);
const loadChecks = [
  // verifies: REQ-VIEWER-999#CASE-1
  ["rail: the Roadmap badge counts horizons too, not only TODO.md items",
    // The fixture has 0 todos and 1 open horizon item, so the badge must
    // read exactly 1.
    (() => {
      const at = railAfterLoad.indexOf("Roadmap");
      const after = railAfterLoad.slice(at, at + 220)
        .replace(/<!--[^>]*-->/g, "").replace(/<[^>]+>/g, "|");
      const n = (after.match(/\|+\s*(\d+)/) || [])[1];
      return n === "1";
    })()],
  ["loadData: the horizon plan survives adoption", ROADMAP.length === 1],
  ["loadData: the shipped history survives adoption", HISTORY.length === 1],
  ["loadData: the planning sidecar survives adoption",
    (TARGETS?.releases || []).length === 1],
];
for (const [label, ok] of loadChecks) test(label, ok);
// Put the real dataset back for anything after this point.
adoptMapExport({ ...json, nodes: json.nodes.map(adaptNode) });

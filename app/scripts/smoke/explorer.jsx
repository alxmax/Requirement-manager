// tested-by: ARCH-VIEWER-007
/* Render smoke test, part: explorer, tally, commands, search, questions. */
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
      return rows.some((row) => row.id === deepId)
        && rows.length === ancestorsOf(H, deepId).length + 1;
    })()],
  ["tree: no `satisfies` anywhere degrades to a flat list",
    flatH.flat === true
      && flattenTree(flatH, { expanded: allExpanded(flatH), keep: null }).length === 2],
  ["tree: a satisfies cycle still renders every row exactly once",
    flattenTree(cycH, { expanded: { "C-1": true, "C-2": true }, keep: null }).length === 2],
  // 0 real findings today: every `verify` bullet in the export is the
  // "None — …" placeholder that `collect_findings` filters out.
  ["findings: the placeholder verify bullet is not a finding",
    openQuestions({
      verify: ["None — authored from known intent, not reconstructed from code."],
    }).length === 0],
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
  // verifies: REQ-VIEWER-945#CASE-1
  ["focus: a status slice narrows the outline on the first render",
    rowsOf(scopedDraft) >= 0 && rowsOf(scopedDraft) < rowsOf(unscoped)],
  // verifies: REQ-VIEWER-945#CASE-3
  ["focus: the active slice is shown as a chip that can clear it",
    scopedDraft.includes("ex-chip on")],
  // verifies: REQ-VIEWER-945#CASE-2
  ["focus: orphan scopes to the gate's condition, not to a status",
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
  // verifies: REQ-VIEWER-964#CASE-1
  ["commands: each verb is listed with its invocation and flags",
    cmdsEn.includes("reqmap.py gate") && cmdsEn.includes("--strict")
    && cmdsEn.includes("reqmap.py wibble AREA-NAME-NNN")],
  ["commands: the summary follows the chosen language",  // verifies: REQ-VIEWER-964#CASE-2
    cmdsRo.includes("Verdictul complet") && !cmdsRo.includes("Run the commit/CI gate.")],
  // verifies: REQ-VIEWER-964#CASE-3
  ["commands: an untranslated command falls back to the engine's English",
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
  // verifies: REQ-SEARCH-965#CASE-1
  ["search: an exact id is the first hit, marked as an id match",
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
  // verifies: REQ-VIEWER-966#CASE-2
  ["problems: the placeholder verify bullet is still not a question",
    !merged.some((p) => p.id === "Q-QUIET-002" && p.sev === "QUESTION")],
  // verifies: REQ-VIEWER-966#CASE-3
  ["problems: questions are counted apart from computed signals",
    asked.length === 1 && asked[0].id === "Q-ASKED-001"],
  // verifies: REQ-VIEWER-966#CASE-4
  ["problems: the question tab is offered, and the question text is shown",
    mergedHtml.includes("Questions") && mergedHtml.includes("stale tested-by range")],
];
for (const [label, ok] of mergeChecks) test(label, ok);

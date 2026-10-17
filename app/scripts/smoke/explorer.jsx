// tested-by: ARCH-VIEWER-007
/* Render smoke test, part: explorer, tally, commands, search, questions. */
import { renderToString } from "react-dom/server";

import App from "../../src/App.jsx";
import { rankRequirements, searchRequirements } from "../../src/lib/search.js";
import {
  adoptMapExport, REQUIREMENTS, ROADMAP, HISTORY, TARGETS,
} from "../../src/lib/data.js";
import { adaptNode, loadData } from "../../src/lib/loadData.js";
import {
  ProblemsView, computeProblems,
} from "../../src/views/ProblemsView.jsx";
import {
  QuestionsView, computeQuestions, questionCount,
} from "../../src/views/QuestionsView.jsx";
import { Rail } from "../../src/components/Rail.jsx";
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
// degradations that must not throw: a registry with no `satisfies` at all (a
// map written before the field) and a `satisfies` cycle.
adoptMapExport({ nodes: json.nodes.map(adaptNode) });
const H = buildHierarchy(REQUIREMENTS);
const exp0 = defaultExpanded(H);
const rows0 = flattenTree(H, { expanded: exp0, keep: null });
const rowsAll = flattenTree(H, { expanded: allExpanded(H), keep: null });
const codeRows = REQUIREMENTS.filter((r) => levelOf(r) === "code");
const deepId = (codeRows[0] || {}).id;
const flatH = buildHierarchy([
  { id: "A-1", title: "a", level: "architecture", satisfies: [],
    satisfiedBy: [], deps: [] },
  { id: "A-2", title: "b", level: "architecture", satisfies: [],
    satisfiedBy: [], deps: [] },
]);
const cycH = buildHierarchy([
  { id: "C-1", title: "c1", level: "architecture", satisfies: ["C-2"],
    satisfiedBy: [] },
  { id: "C-2", title: "c2", level: "architecture", satisfies: ["C-1"],
    satisfiedBy: [] },
]);
const treeChecks = [
  ["tree: every requirement appears exactly once when fully expanded",
    rowsAll.length === REQUIREMENTS.length],
  ["tree: the default expansion collapses the code level to its parents",
    rows0.length < REQUIREMENTS.length
      && rows0.every((row) => levelOf(row.r) !== "code")],
  ["tree: adaptNode carries level/satisfies/satisfied_by through",
    REQUIREMENTS.some((r) => r.level === "code")
      && REQUIREMENTS.some((r) => r.satisfies.length)],
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
      && flattenTree(flatH, { expanded: allExpanded(flatH), keep: null })
        .length === 2],
  ["tree: a satisfies cycle still renders every row exactly once",
    flattenTree(cycH, { expanded: { "C-1": true, "C-2": true }, keep: null })
      .length === 2],
  // 0 real findings today: every `verify` bullet in the export is the
  // "None — …" placeholder that `collect_findings` filters out.
  ["findings: the placeholder verify bullet is not a finding",
    openQuestions({
      verify: [
        "None — authored from known intent, not reconstructed from code.",
      ],
    }).length === 0],
  ["findings: a real verify bullet IS a finding",
    openQuestions({
      verify: ["Is a stale tested-by range an error or a warning?"],
    }).length === 1],
  ["findings: the live corpus reports zero open questions",
    computeQuestions().person.length === 0
      && computeQuestions().code.length === 0],
];
for (const [label, ok] of treeChecks) test(label, ok);

// A map written before `level` existed has none — adaptNode must default it so
// the outline still renders, and the Explorer must not throw on that registry.
const fallbackLevel = adaptNode({ id: "NOLEVEL-001", title: "t" }).level;
const explorerHtml = renderToString(
  <ExplorerView selId="ARCH-MAP-007" setSelId={noop} />);
const explorerChecks = [
  ["explorer: a node with no level defaults to architecture",
    fallbackLevel === "architecture"],
  ["explorer: the outline renders the root of the trace",
    explorerHtml.includes("SYS-SSOT-001")],
  ["explorer: the selected requirement's document renders beside it",
    explorerHtml.includes("ARCH-MAP-007")
      && explorerHtml.includes("Links — traceability")],
  ["explorer: a collapsed parent advertises its clause count",
    explorerHtml.includes("clauses")],
];
for (const [label, ok] of explorerChecks) test(label, ok);
adoptMapExport({ nodes: [
  { id: "HUB-1", title: "The hub", status: "confirmed", layer: "feature",
    level: "architecture", depends_on: ["NEED-1"], used_by: ["USE-1"] },
  { id: "NEED-1", title: "The foundation", status: "confirmed", layer: "bus",
    level: "architecture", depends_on: [], used_by: ["HUB-1"] },
  { id: "USE-1", title: "The user", status: "confirmed", layer: "feature",
    level: "architecture", depends_on: ["HUB-1"], used_by: [] },
].map(adaptNode) });
const around = renderToString(
  <ExplorerView selId="HUB-1" setSelId={noop} />);
const shell = renderToString(<App />);
const pictureAt = around.indexOf("neigh");
const linksAt = around.indexOf("Links — traceability");
const descAt = around.indexOf("Description");
// verifies: REQ-VIEWER-942#CASE-6
test("spec: the neighborhood closes the spec, and there is no Map page",
  around.includes("NEED-1") && around.includes("USE-1")
    && descAt >= 0 && descAt < pictureAt && pictureAt < linksAt
    && !/Map<span class="count"/.test(shell));

// The empty state is a property of the VIEW, so it is asserted against an
// empty registry. It used to run against this repo's own map and passed only
// because the corpus happened to have nothing to fix — so the first draft
// requirement anyone added broke a test whose name says nothing about the
// corpus.
adoptMapExport({ nodes: [] });
test("problems: an empty inbox renders the named empty state, not a badge",
  renderToString(<ProblemsView openSpec={noop} />).includes("Nothing to fix."));

// ---- registry tally scopes the outline (REQ-VIEWER-945) ---------------------
adoptMapExport({ nodes: json.nodes.map(adaptNode) });
const unscoped = renderToString(
  <ExplorerView selId="ARCH-MAP-007" setSelId={noop} />);
const scopedDraft = renderToString(
  <ExplorerView selId="ARCH-MAP-007" setSelId={noop} focus="draft"
    clearFocus={noop} />);
const scopedOrphan = renderToString(
  <ExplorerView selId="ARCH-MAP-007" setSelId={noop} focus="orphan"
    clearFocus={noop} />);
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
    rowsOf(scopedOrphan) === 0
      && scopedOrphan.includes("No requirement matches these filters.")],
];
for (const [label, ok] of focusChecks) test(label, ok);

// ---- the command reference (REQ-VIEWER-964) --------------------------------
const CLI_FIXTURE = [
  { name: "gate", group: "build", summary: "Run the commit/CI gate.", arg: null,
    flags: [{ flag: "--strict", help: "promote warnings to errors" }] },
  // deliberately a name the Romanian dictionary does not carry, so the
  // fallback is exercised
  { name: "wibble", group: "read", summary: "A command no dictionary knows.",
    arg: "AREA-NAME-NNN", flags: [] },
];
adoptMapExport({ commands: CLI_FIXTURE });
const cmdsEn = renderToString(
  <I18nProvider initialLocale="en"><CommandsView /></I18nProvider>);
const cmdsRo = renderToString(
  <I18nProvider initialLocale="ro"><CommandsView /></I18nProvider>);
adoptMapExport({ commands: [] });
const cmdsEmpty = renderToString(
  <I18nProvider initialLocale="en"><CommandsView /></I18nProvider>);
adoptMapExport({ commands: CLI_FIXTURE });
const cmdChecks = [
  // verifies: REQ-VIEWER-964#CASE-1
  ["commands: each verb is listed with its invocation and flags",
    cmdsEn.includes("reqmap.py gate") && cmdsEn.includes("--strict")
    && cmdsEn.includes("reqmap.py wibble AREA-NAME-NNN")],
  // verifies: REQ-VIEWER-964#CASE-2
  ["commands: the summary follows the chosen language",
    cmdsRo.includes("Verdictul complet")
      && !cmdsRo.includes("Run the commit/CI gate.")],
  // verifies: REQ-VIEWER-964#CASE-3
  ["commands: an untranslated command falls back to the engine's English",
    cmdsRo.includes("A command no dictionary knows.")],
  // verifies: REQ-VIEWER-964#CASE-4
  ["commands: a map with no list renders the named empty state",
    cmdsEmpty.includes("No command list in this map.")],
  ["commands: flag names are never translated",
    cmdsRo.includes("--strict")],
];
for (const [label, ok] of cmdChecks) test(label, ok);

// ---- id and literal-text search (REQ-SEARCH-965) ---------------------------
// The id is the primary key of this corpus and is in none of the ranked
// text: the viewer used to answer `ARCH-CHECK-006` with a different
// requirement entirely.
const SEARCH_LAYERS = [
  { id: "AREA-X-001", title: "Locking", intent: "why",
    contract: ["`gate` writes the lock."],
    acc: [], i18n: { ro: { title: "Blocare", intent: "de ce",
                           contract: "- `gate` scrie fisierul de blocare unic",
                           acceptance: "" } } },
  { id: "AREA-X-002", title: "Sync", intent: "why",
    contract: ["`sync` advances the baseline."],
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
  // verifies: REQ-SEARCH-965#CASE-3
  ["search: a phrase inside a case is found as a text match",
    byText[0] && byText[0].req.id === "AREA-X-002"
      && byText[0].kind === "text"],
  // verifies: REQ-SEARCH-965#CASE-4
  ["search: a phrase from the cached translation is found",
    byRo[0] && byRo[0].req.id === "AREA-X-001"],
  // verifies: REQ-SEARCH-965#CASE-5
  ["search: a plain query still comes from the ranked model",
    byWords.length > 0 && byWords.every((h) => h.kind === "score")],
];
for (const [label, ok] of layerChecks) test(label, ok);

// ---- questions have a page of their own (REQ-VIEWER-1101) ------------------
// tested-by: REQ-VIEWER-1101
// ADR-0070: three sources of question, one page, grouped by where each came
// from; Problems keeps only what is broken or awaits review.
const CLARIFY_Q = (rule, severity) => ({ rule, severity, where: "clause 1",
  quote: "`gate` retries 3 times.", question: `the ${rule} question`,
  suggest: "say it" });
adoptMapExport({ nodes: [
  adaptNode({ id: "Q-ASKED-001", title: "asked", area: "Q", layer: "feature",
    status: "confirmed",
    intent: "i", contract: ["a clause"], acc: [],
    members: [{ role: "implements", loc: "a.py:1" }],
    verify: ["Is a stale tested-by range an error or a warning?"], deps: [],
    used_by: [] }),
  adaptNode({ id: "Q-QUIET-002", title: "quiet", area: "Q", layer: "feature",
    status: "confirmed",
    intent: "i", contract: ["a clause"], acc: [],
    members: [{ role: "implements", loc: "b.py:1" }],
    verify: ["None — authored from known intent."], deps: [], used_by: [] }),
  adaptNode({ id: "Q-SEEN-003", title: "seen", area: "Q", layer: "feature",
    status: "draft", intent: "i", contract: [], acc: [], members: [],
    verify: ["Observed at `src/x.py:6`: `except OSError:` swallows the "
      + "error. Intended fail-open, or a bug to fix?"], deps: [],
    used_by: [] }),
  adaptNode({ id: "Q-TEXT-004", title: "text", area: "Q", layer: "feature",
    status: "draft", intent: "i", contract: [], acc: [], members: [],
    verify: [], deps: [], used_by: [],
    clarify: [CLARIFY_Q("vague-term", "advisory"),
      CLARIFY_Q("no-cases", "blocking")] }),
] });
const merged = computeProblems();
const asked = computeQuestions();
const problemsHtml = renderToString(<ProblemsView openSpec={noop} />);
const pageHtml = (origin) => renderToString(
  <QuestionsView openSpec={noop} initialOrigin={origin} />);
const railHtml = renderToString(
  <Rail view="questions" setView={noop} focus={null} setFocus={noop}
    problems={merged} openProblems={noop} />);
const navAt = (label) => railHtml.indexOf(`</svg>${label}<`);
const mergeChecks = [
  // verifies: REQ-VIEWER-1101#CASE-1
  ["questions: a person's question is on the page, under its own origin",
    asked.person.length === 1 && asked.person[0].id === "Q-ASKED-001"
      && pageHtml("person").includes("stale tested-by range")],
  // verifies: REQ-VIEWER-1101#CASE-2
  ["questions: an Observed bullet is listed as code, never as a person's",
    asked.code.length === 1 && asked.code[0].id === "Q-SEEN-003"
      && !asked.person.some((r) => r.id === "Q-SEEN-003")
      && pageHtml("code").includes("src/x.py:6")],
  // verifies: REQ-VIEWER-1101#CASE-3
  ["questions: the placeholder verify bullet is still not a question",
    !Object.values(asked).flat().some((r) => r.id === "Q-QUIET-002")],
  // verifies: REQ-VIEWER-1101#CASE-4
  ["questions: clarify questions are listed, blocking ones first",
    asked.clarify.length === 1
      && asked.clarify[0].questions[0].rule === "no-cases"
      && pageHtml("clarify").includes("the vague-term question")],
  // verifies: REQ-VIEWER-1101#CASE-5
  ["questions: the rail counts what blocks and what a human wrote, not advice",
    questionCount(asked) === 3],
  // verifies: REQ-VIEWER-1101#CASE-6
  ["questions: Problems has no Questions tab and lists no question row",
    !problemsHtml.includes(">Questions<")
      && !merged.some((p) => p.sev === "QUESTION")],
  // verifies: REQ-VIEWER-1101#CASE-7
  ["questions: the page sits in the rail below Commands",
    navAt("Questions") > navAt("Commands") && navAt("Commands") > 0],
];
for (const [label, ok] of mergeChecks) test(label, ok);

// ---- a cached translation is shown, always marked (REQ-TRANSLATE-1080) -----
// tested-by: REQ-TRANSLATE-1080
// The reading half is the engine's (ARCH-TRANSLATE-044); this is the showing
// half: a cached entry is rendered only in its own locale, and never
// without the marker that says nobody reviewed it.
adoptMapExport({ nodes: json.nodes.map(adaptNode) });
const trBase = REQUIREMENTS[0];
const trNode = { ...trBase, i18n: { ro: { title: "Titlu tradus unic" } } };
const specIn = (r, locale) => renderToString(
  <I18nProvider initialLocale={locale}>
    <SpecDoc r={r} onNav={noop} />
  </I18nProvider>);
const trRo = specIn(trNode, "ro");
const trEn = specIn(trNode, "en");
const trNone = specIn({ ...trBase, i18n: undefined }, "ro");
const MARK = "machine-translated, unreviewed";
const translationChecks = [
  // verifies: REQ-TRANSLATE-1080#CASE-1
  ["translation: a cached title renders in its locale, with the marker",
    trRo.includes("Titlu tradus unic") && trRo.includes(MARK)],
  // verifies: REQ-TRANSLATE-1080#CASE-2
  ["translation: the authored locale shows the source, unmarked",
    !trEn.includes("Titlu tradus unic") && !trEn.includes(MARK)],
  // verifies: REQ-TRANSLATE-1080#CASE-3
  ["translation: no cache entry means the source text and no marker",
    !trNone.includes(MARK)],
];
for (const [label, ok] of translationChecks) test(label, ok);

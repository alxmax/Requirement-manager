// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-1139
// implements: REQ-VIEWER-1145
/* The Report page's numbers, computed once from what the map carries. Every
 * count either comes from the map or is `null` ("not measured"): nothing is
 * estimated, and a count that is null adds no recommendation. */
import {
  REQUIREMENTS, BUGS, BUGS_FIXED, HEALTH, ENGINE_VERSION, BRANCH,
  GENERATED_AT, AUDIT, TRACE,
} from "./data.js";
import { openQuestions, isAuditFinding, auditKind } from "./tree.js";
import { isFix } from "./bugStats.js";
import { ENFORCED } from "../views/SpecDoc.jsx";
import {
  computeQuestions, questionTabs, priorityOf,
} from "../views/QuestionsView.jsx";

const PRIO_RANK = { high: 0, medium: 1, low: 2 };
const BUG_PRIOS = ["P0", "P1", "P2", "P3", "P4"];
const has = (r, role) => (r.members || []).some((m) => m.role === role);
const brief = (r) => ({ id: r.id, title: r.title, status: r.status });
const firstLine = (s) => String(s).split("\n")[0]
  .replace(/^[*_ ]+|[*_ ]+$/g, "").trim();

/** Requirements that are held to carry code: live, and not a `need` or an
 * `aggregate` (those are covered by their links, not by tags). */
function codeHeld() {
  return REQUIREMENTS.filter((r) => r.status !== "deprecated"
    && r.layer !== "need" && r.layer !== "aggregate");
}

function traceCounts() {
  const held = codeHeld();
  const noImpl = held.filter((r) => !has(r, "implements"));
  const testable = held.filter((r) => !r.test_exempt);
  const noTest = testable.filter((r) => has(r, "implements")
    && !has(r, "tested-by"));
  // cases the engine measured: `clauses` labelled criteria, `covered` proven
  const unproven = testable
    .filter((r) => r.clauses != null && r.covered != null
      && r.covered < r.clauses)
    .map((r) => ({ ...brief(r), gap: r.clauses - r.covered }));
  return {
    noImplConfirmed: noImpl.filter((r) => ENFORCED[r.status]).map(brief),
    noImplDraft: noImpl.filter((r) => !ENFORCED[r.status]).map(brief),
    noTest: noTest.map(brief),
    unproven,
    unprovenCases: unproven.reduce((n, r) => n + r.gap, 0),
  };
}

function bugCounts() {
  const open = BUGS;
  const byPrio = {};
  BUG_PRIOS.forEach((p) => {
    const n = open.filter((b) => b.prio === p).length;
    if (n) byPrio[p] = n;
  });
  return {
    open: [...open].sort((a, b) => String(a.prio).localeCompare(b.prio)),
    byPrio,
    fixed: BUGS_FIXED.filter(isFix).length,
    fixedRows: BUGS_FIXED,
    urgent: (byPrio.P0 || 0) + (byPrio.P1 || 0),
  };
}

/** Every open question as one ranked list: High before Medium before Low,
 * then a confirmed requirement before a draft, then the one more others
 * depend on, then by id. */
export function rankedQuestions(qs = computeQuestions()) {
  const byId = Object.fromEntries(REQUIREMENTS.map((r) => [r.id, r]));
  const out = [];
  const push = (id, prio, kind, text) => {
    const r = byId[id] || {};
    out.push({ id, title: r.title, status: r.status, prio, kind, text,
      fanIn: (r.usedBy || []).length });
  };
  qs.person.forEach((row) => row.questions.forEach((q) =>
    push(row.id, "high", "asked by a person", firstLine(q))));
  qs.code.forEach((row) => row.questions.forEach((q) =>
    push(row.id, "medium", "observed in code", firstLine(q))));
  qs.clarify.forEach((row) => row.questions.forEach((q) =>
    push(row.id, priorityOf(q), q.rule, q.question)));
  return out.sort((a, b) => PRIO_RANK[a.prio] - PRIO_RANK[b.prio]
    || (ENFORCED[b.status] ? 1 : 0) - (ENFORCED[a.status] ? 1 : 0)
    || b.fanIn - a.fanIn
    || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
}

/** One line per open problem kind, most severe first, each with its count
 * and what closes it. A count that is not measured gives none. */
function recommend(c) {
  const rec = [];
  const add = (n, text) => { if (n) rec.push({ n, text }); };
  add(c.dangling && c.dangling.length,
    "tags name no requirement (RM001): fix the id or remove the tag; "
    + "`gate` lists each line");
  add(c.trace.noImplConfirmed.length,
    "confirmed requirements have no code: tag it with `# implements: ID`, "
    + "or set them back to draft");
  add(c.drift && c.drift.length,
    "requirements changed since the lock: re-check their code, then "
    + "`sync --accept-drift \"reason\"`");
  add(c.questions.high,
    "High questions are open: answer each in its requirement's Description "
    + "or Cases");
  add(c.findings.filter((f) => /bug|not implemented|unimplemented/
    .test(f.kind)).reduce((n, f) => n + f.n, 0),
    "audit findings say the code does not do what a clause says: confirm "
    + "each with a reproduction, then fix it or file a bug");
  add(c.tiers && c.tiers.A.length,
    "requirements have a test that already names them: add the "
    + "`# tested-by: ID` tag the suggestion gives");
  add(Math.max(0, c.trace.noTest.length - (c.tiers ? c.tiers.A.length : 0)),
    "requirements have code but no test: tag the test with "
    + "`# tested-by: ID`, or write one");
  add(c.findings.filter((f) => /false coverage/.test(f.kind))
    .reduce((n, f) => n + f.n, 0),
    "audit findings say a test cannot fail when the code is wrong: "
    + "strengthen those tests first");
  add(c.vacuous && c.vacuous.length,
    "tagged tests cannot fail: they assert nothing, a constant, or a value "
    + "against itself; assert the behaviour, or drop the `# verifies:` tag");
  add(c.hygiene && c.hygiene.duplicates.length,
    "requirements repeat another's text word for word: merge or "
    + "retire one of each pair");
  add(c.hygiene && c.hygiene.title_only_confirmed.length,
    "confirmed requirements have a title and no clause: write the "
    + "clause or set them back to draft");
  add(c.designRules.reduce((n, r) => n + r.count, 0),
    "places break the repository's own design rules: see each rule's "
    + "list under Problem types");
  add(c.trace.unprovenCases,
    "cases are not proven by a test: add `# verifies: ID#CASE-N` on the "
    + "test that proves each");
  add(c.bugs.urgent,
    "P0/P1 bugs are open: fix them, then `sync --fix ID`");
  add(c.questions.medium,
    "Medium questions are open: read them once the High ones are answered");
  return rec;
}

/** The findings an audit wrote into Verify intent, by kind, each with the
 * requirements behind it, most frequent kind first. */
function auditFindings() {
  const kinds = {};
  REQUIREMENTS.forEach((r) => {
    if (r.status === "deprecated") return;
    openQuestions(r).filter(isAuditFinding).forEach((q) => {
      const k = auditKind(q);
      (kinds[k] = kinds[k] || { n: 0, ids: new Set() }).n += 1;
      kinds[k].ids.add(r.id);
    });
  });
  return Object.entries(kinds).map(([kind, v]) => ({ kind, n: v.n,
    ids: [...v.ids].sort() })).sort((a, b) => b.n - a.n
    || a.kind.localeCompare(b.kind));
}

/** The audit session, when one runs: reviewed out of planned, the counters
 * and the three rates as the engine computed them. */
function auditSession() {
  if (!AUDIT) return null;
  return { planned: AUDIT.plan.ranked + AUDIT.plan.random,
    reviewed: AUDIT.reviewed.total, counters: AUDIT.counters || {},
    rates: AUDIT.rates || {}, band: AUDIT.band };
}

/** tested-by suggestions by tier, from the map's trace block. */
function suggestionTiers() {
  if (!TRACE) return null;
  const tiers = { A: [], B: [], C: [] };
  Object.entries(TRACE.suggestions || {}).forEach(([id, s]) => {
    if (tiers[s.tier]) tiers[s.tier].push({ id, tests: s.tests || [] });
  });
  Object.values(tiers).forEach((l) => l.sort((a, b) => (a.id < b.id ? -1 : 1)));
  return tiers;
}

/** What the audit leaves behind and where: the two exports this page makes,
 * then the files `sync` writes beside the requirements, each only when the
 * map shows it exists. Paths are relative to the requirements folder. */
function deliverables(c) {
  const out = [
    { path: "report.md", what: "this page as Markdown (Export Markdown)" },
    { path: "report.pdf", what: "this page as PDF (Export PDF)" },
    { path: "_map.json", what: "the graph the map and this page read" },
    { path: "_map.md", what: "the map as text" },
    { path: "_findings.md", what: "the open findings, per requirement" },
  ];
  if (c.audit) {
    out.push({ path: "_audit.json", what: "the audit session: plan, reads, rates" });
  }
  if (c.bugs.open.length || c.bugs.fixed) {
    out.push({ path: "bugs/", what: "the bug files, one per module" });
  }
  return out;
}

/** Everything the Report page shows. */
export function computeReport() {
  const qs = computeQuestions();
  const tabs = questionTabs(qs);
  const n = (key) => (tabs.find((t) => t.key === key) || {}).n || 0;
  const live = REQUIREMENTS.filter((r) => r.status !== "deprecated");
  const files = new Set();
  REQUIREMENTS.forEach((r) => (r.members || []).forEach((m) =>
    files.add(String(m.loc || "").split(":")[0])));
  files.delete("");
  const ranked = rankedQuestions(qs);
  const rules = {};
  qs.clarify.forEach((row) => row.questions.forEach((q) => {
    (rules[q.rule] = rules[q.rule] || new Set()).add(row.id);
  }));
  const c = {
    method: {
      engine: ENGINE_VERSION, branch: BRANCH, at: GENERATED_AT,
      requirements: REQUIREMENTS.length, files: files.size,
    },
    health: HEALTH ? { score: HEALTH.score, healthy: HEALTH.healthy,
      scored: HEALTH.scored ?? HEALTH.total } : null,
    total: live.length,
    confirmed: live.filter((r) => ENFORCED[r.status]).length,
    bugs: bugCounts(),
    questions: { high: n("high"), medium: n("medium"), low: n("low"),
      all: n("all") },
    highReqs: [...new Set(ranked.filter((q) => q.prio === "high")
      .map((q) => q.id))],
    questionIds: Object.fromEntries(["high", "medium", "low"].map((p) =>
      [p, [...new Set(ranked.filter((q) => q.prio === p).map((q) => q.id))]
        .sort()])),
    // implements: REQ-VIEWER-1155 - what the questions chart draws
    questionSplit: ["high", "medium", "low"].map((prio) => {
      const rows = ranked.filter((q) => q.prio === prio);
      const confirmed = rows.filter((q) => ENFORCED[q.status]).length;
      return { prio, confirmed, other: rows.length - confirmed };
    }),
    trace: traceCounts(),
    dangling: HEALTH
      ? (HEALTH.gate_error_lines || []).filter((l) => /RM001/.test(l)) : null,
    drift: HEALTH
      ? (HEALTH.unhealthy || []).filter((u) => (u.why || []).includes("drift"))
        .map((u) => u.id)
      : null,
    rules: Object.entries(rules).map(([rule, ids]) => ({ rule, n: ids.size,
      ids: [...ids].sort() })).sort((a, b) => b.n - a.n),
    top: ranked.slice(0, 10),
    audit: auditSession(),
    findings: auditFindings(),
    coverage: TRACE ? TRACE.coverage : null,
    tiers: suggestionTiers(),
    hygiene: TRACE ? TRACE.hygiene : null,
    // implements: REQ-TESTGAPS-1146 - absent from an older map: not measured
    vacuous: TRACE && TRACE.vacuous ? TRACE.vacuous : null,
    designRules: TRACE && TRACE.rules ? TRACE.rules.filter((x) => x.count > 0)
      : [],
  };
  c.recommendations = recommend(c);
  c.deliverables = deliverables(c);
  return c;
}

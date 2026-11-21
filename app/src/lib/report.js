// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-1139
/* The Report page's numbers, computed once from what the map carries. Every
 * count either comes from the map or is `null` ("not measured"): nothing is
 * estimated, and a count that is null adds no recommendation. */
import {
  REQUIREMENTS, BUGS, BUGS_FIXED, HEALTH, ENGINE_VERSION, BRANCH,
  GENERATED_AT,
} from "./data.js";
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
  add(c.trace.noTest.length,
    "requirements have code but no test: tag the test with "
    + "`# tested-by: ID`");
  add(c.trace.unprovenCases,
    "cases are not proven by a test: add `# verifies: ID#CASE-N` on the "
    + "test that proves each");
  add(c.bugs.urgent,
    "P0/P1 bugs are open: fix them, then `sync --fix ID`");
  add(c.questions.medium,
    "Medium questions are open: read them once the High ones are answered");
  return rec;
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
  };
  c.recommendations = recommend(c);
  return c;
}

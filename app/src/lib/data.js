// implements: ARCH-VIEWER-007
/* Requirement Manager dataset.
 *
 * The baked fallback lives in `baked.json` — the 13 authored requirements lifted
 * from the real registry plus two in-flight states (a draft + a fresh orphan)
 * and one deprecated capability, so Risk / Problems / Console have signals to
 * show with no engine present. It is JSON rather than code so the gate's RM017 can
 * read it as data (`json.load`) and compare it with the live registry. At startup
 * `loadData()` (see loadData.js) tries the engine's `_map.json` export and, when
 * found, adopts it in place of this. Importers use named imports — these are ES
 * live bindings, so a reassignment is seen everywhere. */
import BAKED from "./baked.json";

/* The demo fixture's one partially-covered case. Real corpora get these three
   fields from the engine (`_map.json`) or not at all — never from a heuristic. */
function applyBakedCoverage(list) {
  const m = list.find(r => r.id === "ARCH-MAP-007");
  if (m) { m.clauses = 4; m.covered = 3; m.gap = "no `verifies:` tag for AC-4"; }
  return list;
}

// ---- live bindings: reassigned by setRegistry() / setRepo() ----------------
export let REQUIREMENTS = applyBakedCoverage(BAKED);
export let REQ_EDGES = [];
export let REQ_BY_ID = {};
// owner/repo the loaded map describes (engine-emitted); null = no engine data,
// header falls back to a generic label.
export let REPO = null;
export let TODOS = [];
// The repository's declared requirements language (`en` | `ro` | `both`), emitted by the
// engine from requirements/_config.json. It sets the viewer's DEFAULT locale; a reader's
// own choice (localStorage) still wins, because a preference beats a default.
export let LANGUAGE = "en";                          // implements: REQ-TRANSLATE-996
// The CLI as data, straight off _map.json (generated from the engine's command
// registry). Empty in the baked fallback: a map produced before v4.0.0 carries none.
export let COMMANDS = [];
/* The engine's own `health` record, verbatim. Deliberately NOT recomputed here:
 * `next` already prints this number, and a second definition in JavaScript is
 * how the CLI and the viewer come to disagree about how the repo is doing. Null
 * until a map carrying it is loaded — an older map has no key, and the rail then
 * shows nothing rather than an invented zero. The engine stopped emitting a
 * `design` record in v8.2.0 (ADR-0047).  implements: REQ-VIEWER-969 */
export let HEALTH = null;
/* Planning sidecar from requirements/_planning.json (legacy: `targets` key).
 * Lanes, bars, milestone due dates and the release cadence. Null until loaded. */
export let TARGETS = null;
/* ROADMAP.md's horizon plan, as the engine parsed it: one entry per `- [ ]` / `- [x]`
 * item under Now / Next / Later / Not now, with its `req:` and `unpark:`. Empty for a
 * repo with no ROADMAP.md and for any map written before v7.6.0, which is what gates
 * the Horizons mode off — absent is NOT an empty plan, it is no plan file.
 * implements: REQ-VIEWER-999 */
export let ROADMAP = [];
/* What already shipped, one row per calendar month, derived by the engine from
 * CHANGELOG.md. Facts, not plan — the Gantt draws it left of the today line.
 * implements: REQ-HISTORY-1003 */
export let HISTORY = [];
/* The branch git was on when the map was written, when it could say. Absent is not a
 * wrong answer — a detached HEAD or no work tree both read as unknown, and the band
 * keeps its former label.  implements: REQ-PLANBRANCH-1011 */
export let BRANCH = null;

function derive() {
  REQ_EDGES = REQUIREMENTS.flatMap(r => (r.deps || []).map(d => [r.id, d]));
  REQ_BY_ID = Object.fromEntries(REQUIREMENTS.map(r => [r.id, r]));
}
derive();

/** Adopt one engine `_map.json` export — the single entry point loadData uses. */
export function adoptMapExport(data) {               // implements: REQ-VIEWER-969
  if (!data || typeof data !== "object") return;
  if (Array.isArray(data.nodes)) { REQUIREMENTS = data.nodes; derive(); }
  if ("repo" in data) REPO = data.repo || null;
  if ("language" in data) {
    LANGUAGE = (data.language === "ro" || data.language === "both") ? data.language : "en";
  }
  if ("todos" in data) TODOS = Array.isArray(data.todos) ? data.todos : [];
  if ("roadmap" in data) ROADMAP = Array.isArray(data.roadmap) ? data.roadmap : [];
  if ("history" in data) HISTORY = Array.isArray(data.history) ? data.history : [];
  if ("branch" in data) {
    BRANCH = typeof data.branch === "string" && data.branch ? data.branch : null;
  }
  if ("commands" in data) COMMANDS = Array.isArray(data.commands) ? data.commands : [];
  const health = data.health;
  HEALTH = (health && typeof health.score === "number") ? health : null;
  const planning = data.planning || data.targets;
  TARGETS = (planning && typeof planning === "object") ? planning : null;
}

/* ---- coverage --------------------------------------------------------------
   This is a TEST axis and nothing else. `status: draft` is a REVIEW state and is
   shown by the status pill; folding it in here reported a draft with twenty tests
   as "untested" — a whole corpus of 55 read untested until it was promoted, and
   `health` jumped 0 → 96 without a single test being written.
   `clauses`/`covered`/`gap` are emitted by the engine (per labelled criterion) or
   not at all: absent means NOT MEASURED, and nothing here may substitute a number
   of its own. The previous fallback took `clauses` from the CONTRACT line count and
   `covered` from the tested-by badge, so a requirement with three real tests
   displayed "0 / 8 clauses covered". */
export function coverageOf(r) {
  if (r.status === "deprecated") return "exempt";
  if (r.test_exempt) return "exempt";
  // covered by an edge, not by code
  if (r.layer === "need" || r.layer === "aggregate") return "exempt";
  const hasImpl = r.members.some(m => m.role === "implements");
  const hasTest = r.members.some(m => m.role === "tested-by");
  if (!hasImpl) return "untested";                 // orphan — nothing to cover
  if (r.covered != null && r.clauses)              // engine-measured per-criterion data
    return r.covered >= r.clauses ? "tested" : (r.covered > 0 ? "partial" : "untested");
  return hasTest ? "tested" : "untested";
}

/* Why a requirement is exempt — three different reasons that used to render as one
   ("test-exempt — skipped by the gate"), including for a `need` that carries real
   tests and no `test_exempt` at all. */
export function exemptReason(r) {
  if (r.status === "deprecated") return "deprecated — skipped by the gate";
  if (r.test_exempt) return "test-exempt — skipped by the gate";
  if (r.layer === "need") return "satisfied by other requirements — no code of its own";
  if (r.layer === "aggregate") return "covered by its dependencies — no code of its own";
  return "";
}

export function coverageDetail(r) {
  const state = coverageOf(r);
  const measured = r.covered != null && r.clauses != null;
  return {
    state, measured, gap: r.gap,
    clauses: measured ? r.clauses : 0,
    covered: measured ? r.covered : 0,
  };
}

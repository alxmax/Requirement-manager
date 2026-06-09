/* Requirement Manager dataset.
 *
 * The baked array below is the fallback — the 13 authored requirements lifted
 * from the real registry plus two in-flight states (a draft + a fresh orphan)
 * and one deprecated capability, so Risk / Problems / Console have signals to
 * show with no engine present. At startup `loadData()` (see loadData.js) tries
 * the engine's `_map.json` export and, when found, calls `setRegistry()` to
 * replace this with live data. Importers use named imports — these are ES live
 * bindings, so a `setRegistry()` reassignment is seen everywhere. */

const BAKED = [
  { id:"CORE-PARSE-001", area:"CORE", title:"Requirement reading", layer:"bus", status:"confirmed",
    intent:"Turn the requirement files on disk into structured records the rest of the tool reasons about.",
    contract:[
      "It shall parse each `requirements/*.md` into a record `{meta, body, path}` — `meta` is parsed frontmatter, `body` the markdown after it.",
      "The frontmatter grammar shall support scalars, inline `[a, b]` lists, and block-style lists; a trailing `# comment` shall be stripped.",
      "Files whose name starts with `_` shall be excluded; a leading UTF-8 BOM shall be tolerated." ],
    acc:[
      "A file with valid frontmatter yields its scalar and list fields in `meta`.",
      "A file without a leading `---` block returns empty `meta` and the whole text as body.",
      "Files starting with `_` are excluded from the result." ],
    impl:["`parse_frontmatter`, `load_requirements` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:73-128"},{role:"tested-by",loc:"scripts/test_reqmap.py:47-800"}],
    deps:[], usedBy:["REQ-CHECK-006","REQ-FINDINGS-010","REQ-MAP-007","REQ-NEW-004","REQ-PROMOTE-011","REQ-SCAN-005"],
    risks:[{signal:"blast-radius",advice:"High fan-in — many capabilities depend on this. Change it only behind its contract, run the full gate + dependents' tests."}] },

  { id:"CORE-SCAN-002", area:"CORE", title:"Member discovery", layer:"bus", status:"confirmed",
    intent:"Find every place in the code that claims membership of a capability, by scanning for tags.",
    contract:[
      "It shall walk a code root and find inline `implements:` / `tested-by:` tags in every known source extension.",
      "Tag IDs shall match `[A-Z][A-Z0-9]*(-[A-Z0-9]+)+`; the same `(role, ID)` on one line is recorded once.",
      "`.git`, `node_modules`, `__pycache__` and the SSOT `requirements/` directory shall be excluded." ],
    acc:[
      "A file containing `# implements: <ID>` produces a member `(implements, file, line)` under `<ID>`.",
      "Excluded directories are not scanned; member paths are POSIX-relative.",
      "An unreadable file is skipped without aborting the scan." ],
    impl:["`scan_members`, `_prune_dirs`, `load_ignore`, `TAG_RE` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:144-181"},{role:"tested-by",loc:"scripts/test_reqmap.py:146"}],
    deps:[], usedBy:["REQ-CANDIDATES-009","REQ-CHECK-006","REQ-EXTRACT-008","REQ-MAP-007","REQ-SCAN-005"],
    risks:[{signal:"blast-radius",advice:"High fan-in — many capabilities depend on this. Treat it as shared foundation (bus)."}] },

  { id:"CORE-DRIFT-003", area:"CORE", title:"Contract hashing & lock", layer:"bus", status:"confirmed",
    intent:"Detect when a requirement's binding contract changes, so stale code can be re-checked.",
    contract:[
      "It shall compute a stable 12-char hex content hash over only the NORMATIVE sections of a requirement.",
      "The hash shall be deterministic for identical normative content.",
      "It shall read and write the per-id hash baseline at `requirements/_reqlock.json`." ],
    acc:[
      "Editing only the Description/Notes section does not change the hash.",
      "Editing the Contract section changes the hash.",
      "`load_lock` on a missing or corrupt lock file returns an empty dict (no crash)." ],
    impl:["`binding_hash`, `lock_path`, `load_lock`, `save_lock` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:209-240"},{role:"tested-by",loc:"scripts/test_reqmap.py:103-116"}],
    deps:[], usedBy:["REQ-CHECK-006"],
    risks:[{signal:"drift",advice:"Lock hash differs from current contract. Re-check the named members, then `check --update-lock`."}],
    drift:true },

  { id:"REQ-CHECK-006", area:"REQ", title:"The gate", layer:"feature", status:"confirmed",
    intent:"Fail the build when code and requirements have fallen out of sync.",
    contract:[
      "It shall report an `ERROR` and exit non-zero for a dangling tag, invalid status/layer, a `depends_on` to a missing id, or an enforced requirement with no `implements:` member.",
      "It shall report drift as a `WARN` (never an error), naming the member `file:line` locations to re-check.",
      "With `--update-lock` it shall write the current binding hashes to `requirements/_reqlock.json`." ],
    acc:[
      "A tag referencing a non-existent capability produces an `ERROR` and exit 1.",
      "A `confirmed` requirement with no `implements` member produces an `ERROR`.",
      "A drifted contract produces a `WARN` (not an error) naming the member locations." ],
    impl:["`cmd_check`, `warn_if_stale` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:247-296"},{role:"tested-by",loc:"scripts/test_reqmap.py:93-958"}],
    deps:["CORE-PARSE-001","CORE-SCAN-002","CORE-DRIFT-003"], usedBy:["REQ-INIT-012"], risks:[] },

  { id:"REQ-EXTRACT-008", area:"REQ", title:"Legacy extraction", layer:"feature", status:"confirmed",
    intent:"Bootstrap a registry on a brownfield codebase by proposing draft requirements from untagged code.",
    contract:[
      "It shall walk untagged source files and propose one `requirements/DRAFT-*.md` per file, skipping tagged files.",
      "Every proposal shall be `status: draft` with a TODO body — it captures observed behavior, never canonizing intent.",
      "It shall assign a cheap risk score and route a score ≥ 2 to `REVIEW`, else `auto-baseline`." ],
    acc:[
      "An untagged `.py`/`.js`/`.ts`/`.c`/`.cpp` file yields one `DRAFT-*` draft.",
      "A file matching a `.reqmapignore` pattern is skipped (no draft proposed).",
      "A file containing `TODO`/`FIXME` scores higher risk and is flagged `REVIEW`." ],
    impl:["`cmd_extract`, `_draft_id`, `_risk`, `classify_prose` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:495-641"},{role:"tested-by",loc:"scripts/test_reqmap.py:194-429"}],
    deps:["CORE-SCAN-002"], usedBy:["REQ-INIT-012"], risks:[] },

  { id:"REQ-CANDIDATES-009", area:"REQ", title:"Capability candidates", layer:"feature", status:"confirmed",
    intent:"Stage 1 of AI extraction: emit a deterministic capability plan from legacy code, writing no requirement files.",
    contract:[
      "It shall emit a single JSON object (`{engine_version, bus[], candidates[]}`) to stdout or `--out PATH`.",
      "Each candidate shall carry `{suggested_id, suggested_layer, files[], docstrings{}, depends_on[]}`.",
      "Grouping shall use `requirements/_capmap.json` when present, otherwise one candidate per file." ],
    acc:[
      "Running `candidates` writes zero `.md` files and emits valid JSON.",
      "An import of a local module yields a `depends_on` edge to that module's candidate.",
      "A module imported by ≥ the bus threshold is suggested as `bus`." ],
    impl:["`cmd_candidates`, `_py_facts`, `_js_facts`, `_load_capmap` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:658-805"},{role:"tested-by",loc:"scripts/test_reqmap.py:521-908"}],
    deps:["CORE-SCAN-002"], usedBy:[], risks:[] },

  { id:"REQ-FINDINGS-010", area:"REQ", title:"Open-findings report", layer:"feature", status:"confirmed",
    intent:"Roll up every requirement's open \"verify intent\" questions into one reviewable _findings.md.",
    contract:[
      "It shall aggregate the bullets under each `## WHAT — Verify intent` section into a single `_findings.md`.",
      "It shall exclude the \"None —\" placeholder bullet.",
      "When a `_findings_triage.json` sidecar exists it shall render a classified view: confirmed bugs first, by severity." ],
    gwt:"AC-1\n  Given  two requirements, one with two Verify-intent bullets and one with only the \"None —\" placeholder\n  When   findings runs in raw mode\n  Then   _findings.md lists the two bullets and reports \"2 open finding(s) across 1 requirement(s)\"",
    impl:["`cmd_findings`, `render_findings` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:911-998"},{role:"tested-by",loc:"scripts/test_reqmap.py:594-891"}],
    deps:["CORE-PARSE-001"], usedBy:[], risks:[] },

  { id:"REQ-MAP-007", area:"REQ", title:"Requirement map (HTML + MD)", layer:"feature", status:"confirmed",
    intent:"Render the whole registry as navigable diagrams a human can read at a glance.",
    contract:[
      "It shall generate `_map.md` (Mermaid blocks), `_map.json` (a `{nodes, edges}` graph), and `_map.html` (a self-contained viewer with the graph inlined) when the viewer template is present.",
      "There shall be one node per requirement and one edge per `depends_on`.",
      "All requirement-derived text shall be JSON-encoded in `_map.json` (no markup context to break out of)." ],
    acc:[
      "The generated files contain one node per requirement and one edge per `depends_on`.",
      "`_map.md` contains 4 Mermaid code blocks, each with a legend.",
      "`_map.json` parses to `{engine_version, nodes, edges}` with one node per requirement." ],
    impl:["`cmd_map`, `render_html`, `render_md`, the `_mermaid_*` generators in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:1033-1948"},{role:"tested-by",loc:"scripts/test_reqmap.py:237-1069"}],
    deps:["CORE-PARSE-001","CORE-SCAN-002"], usedBy:["REQ-INIT-012","REQ-NEXT-013"], risks:[] },

  { id:"REQ-NEW-004", area:"REQ", title:"Scaffold a requirement", layer:"feature", status:"confirmed",
    intent:"Create a new requirement file from the template, so every capability starts in the same shape.",
    contract:[
      "Given a capability id `AREA-NAME-NNN`, it shall write `requirements/<ID>.md` stamped from the template.",
      "The scaffold shall be the engine's built-in template unless an on-disk `templates/requirement.md` exists.",
      "It shall refuse to overwrite an existing file (exit non-zero, write nothing)." ],
    acc:[
      "`new FOO-NEW-099` on an empty registry creates `requirements/FOO-NEW-099.md` with that id.",
      "Running `new` for an id that already exists exits non-zero and writes nothing." ],
    impl:["`cmd_new`, `REQUIREMENT_TEMPLATE` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:425"},{role:"tested-by",loc:"scripts/test_reqmap.py:463"}],
    deps:["CORE-PARSE-001"], usedBy:[], risks:[] },

  { id:"REQ-PROMOTE-011", area:"REQ", title:"Promote", layer:"feature", status:"confirmed",
    intent:"One command to perform the human-validation step — flip a reviewed requirement to confirmed.",
    contract:[
      "`promote <ID>` shall set `status` to `confirmed` by editing only the first `status:` line, preserving comments.",
      "It shall refuse (non-zero, no write) when the requirement has no `implements:` member.",
      "It shall be idempotent and shall warn when no `tested-by:` member is linked." ],
    gwt:"AC-1\n  Given  a baseline requirement with an implements: member\n  When   promote <ID> runs\n  Then   its frontmatter status becomes confirmed, the body is byte-identical, and exit is 0",
    impl:["`cmd_promote`, `_set_frontmatter_status` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:446-461"},{role:"tested-by",loc:"scripts/test_reqmap.py:1114"}],
    deps:["CORE-PARSE-001"], usedBy:[], risks:[] },

  { id:"REQ-SCAN-005", area:"REQ", title:"List members per capability", layer:"feature", status:"confirmed",
    intent:"Show, for every capability, which code claims it — and which capabilities have no code.",
    contract:[
      "It shall print every capability id (the union of loaded requirements and discovered tags).",
      "A capability with no members shall print `(no members found)`.",
      "A tag pointing at an id with no requirement shall still appear (so orphans surface)." ],
    acc:[
      "A capability with two tags prints both `role file:line` lines under its id.",
      "A requirement with no members prints `(no members found)`." ],
    impl:["`cmd_scan` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:260"},{role:"tested-by",loc:"scripts/test_reqmap.py:507"}],
    deps:["CORE-PARSE-001","CORE-SCAN-002"], usedBy:[], risks:[] },

  { id:"REQ-INIT-012", area:"REQ", title:"First-use bootstrap", layer:"feature", status:"confirmed",
    intent:"One command that turns a fresh repo into a tracked one — scaffold, draft, lock, map, and say what's next.",
    contract:[
      "It shall create the requirements directory and seed a `.reqmapignore` only when none exists.",
      "It shall draft from untagged code via extract, then build the drift lock and the map.",
      "It shall be safe to re-run: a second invocation refreshes lock + map without destroying authored work." ],
    acc:[
      "`init` on a fresh repo creates `requirements/` and a `.reqmapignore`.",
      "After `init`, `_map.md`, `_map.json` and the drift lock exist.",
      "`init` on a repo with no extractable code prints the distinct \"no requirements were extracted\" message." ],
    impl:["`cmd_init` in `reqmap.py` — orchestrates extract → check → map."],
    members:[{role:"implements",loc:"scripts/reqmap.py:1210-1237"},{role:"tested-by",loc:"scripts/test_reqmap.py:1265"}],
    deps:["REQ-EXTRACT-008","REQ-CHECK-006","REQ-MAP-007"], usedBy:[], risks:[] },

  { id:"REQ-NEXT-013", area:"REQ", title:"What-should-I-do-next report", layer:"feature", status:"confirmed",
    intent:"Render the map's risk surface in the terminal as counted, actionable buckets.",
    contract:[
      "It shall group open risk signals into action buckets, reusing the same source that drives the Risk tab.",
      "It shall print a header `N requirement(s) · X confirmed · Y tested · Z draft(s)`.",
      "It shall surface Orphans, Needs tests, Needs intent review, Drafts to review — most-urgent first; omit blast-radius." ],
    acc:[
      "The output starts with a progress header carrying confirmed/tested/draft counts.",
      "A confirmed requirement with code but no `tested-by` lists under \"Needs tests\".",
      "An empty registry prints the \"no requirements yet\" message; it writes no files and returns 0." ],
    impl:["`cmd_next`, `_risk_score` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:1083-1093"},{role:"tested-by",loc:"scripts/test_reqmap.py:1174"}],
    deps:["REQ-MAP-007"], usedBy:[], risks:[] },

  /* ---- realistic in-flight states (extraction + a fresh orphan tag) ------- */
  { id:"DRAFT-cache-utils", area:"REQ", title:"cache_utils (drafted)", layer:"feature", status:"draft",
    intent:"TODO — observed behavior of scripts/cache_utils.py, captured by extract. Not yet reviewed.",
    contract:["TODO: author the contract. Observed: an in-memory LRU with a TTL sweep and a `# FIXME: race on evict` marker."],
    acc:["TODO: promote acceptance from the existing tests, if any."],
    impl:["scripts/cache_utils.py (untagged at draft time)"],
    members:[], deps:[], usedBy:[],
    risks:[{signal:"unreviewed",advice:"Drafted from code by extract — review intent, then `promote DRAFT-cache-utils`."}],
    riskScore:2 },

  { id:"REQ-SYNC-014", area:"REQ", title:"Background sync", layer:"feature", status:"in-progress",
    intent:"Keep the local registry in step with a remote mirror on a timer.",
    contract:["It shall reconcile local and remote requirement files on an interval without blocking the gate."],
    acc:["TODO"],
    impl:["src/sync.py:88 — tag present, no requirement matched at scan time"],
    members:[], deps:["CORE-PARSE-001"], usedBy:[],
    risks:[{signal:"unimplemented",advice:"Confirmed/in-progress but no resolving member — the gate reports this as an ERROR (orphan). Add the `implements:` tag or the requirement file."}] },

  /* one deprecated capability — kept, not deleted; the gate skips it */
  { id:"REQ-CACHE-014", area:"REQ", title:"In-memory response cache", layer:"feature", status:"deprecated",
    intent:"Superseded by the shared cache service — kept for history, skipped by the gate.",
    contract:["It shall memoize parsed requirement records for the duration of a single run."],
    acc:["A second load within one run returns the memoized record."],
    impl:["scripts/cache.py (retired)"],
    members:[{role:"implements",loc:"scripts/cache.py:18-74"}],
    deps:[], usedBy:[], risks:[], supersededBy:"REQ-PARSE-021" },
];

/* the partial case from the brief: REQ-MAP-007's HTML-escaping clause is uncovered */
function applyBakedCoverage(list) {
  const m = list.find(r => r.id === "REQ-MAP-007");
  if (m) { m.clauses = 4; m.covered = 3; m.gap = "HTML-escaping clause has no acceptance test"; }
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

function derive() {
  REQ_EDGES = REQUIREMENTS.flatMap(r => (r.deps || []).map(d => [r.id, d]));
  REQ_BY_ID = Object.fromEntries(REQUIREMENTS.map(r => [r.id, r]));
}
derive();

/** Replace the registry with live data (from the engine export adapter). */
export function setRegistry(list) {
  REQUIREMENTS = list;
  derive();
}

/** Set the owner/repo name the loaded map describes (engine-emitted). */
export function setRepo(name) {
  REPO = name || null;
}

/** Replace the TODO list with data parsed from TODO.md (engine-emitted). */
export function setTodos(list) {
  TODOS = Array.isArray(list) ? list : [];
}

/* ---- coverage + git-derived dates (computed, not stored) ----------------- */
/* coverage falls out of the clause↔acceptance mapping; a stale tested-by ref demotes to untested */
export function coverageOf(r) {
  if (r.status === "deprecated") return "exempt";
  if (r.test_exempt) return "exempt";
  if (r.layer === "need") return "exempt";          // satisfied-by, not implemented/tested by code (REQ-TRACE-020)
  const hasImpl = r.members.some(m => m.role === "implements");
  const hasTest = r.members.some(m => m.role === "tested-by");
  if (!hasImpl) return "untested";                 // orphan — nothing to cover
  if (r.covered != null && r.clauses)              // explicit per-clause data
    return r.covered >= r.clauses ? "tested" : (r.covered > 0 ? "partial" : "untested");
  if (r.status === "draft") return "untested";
  return hasTest ? "tested" : "untested";
}

export function coverageDetail(r) {
  const state = coverageOf(r);
  const clauses = r.clauses || r.contract.length;
  const covered = r.covered != null ? r.covered : (state === "tested" ? clauses : 0);
  return { state, clauses, covered, gap: r.gap };
}

/* deterministic stand-in for `git log` dates (the real tool reads these live) */
export function datesOf(r) {
  if (r.status === "deprecated") return { deprecated: "2026-04-02" };
  const s = r.id.length,
    mm = String((s % 5) + 1).padStart(2, "0"),
    dd = String((s * 7 % 26) + 1).padStart(2, "0"),
    uu = String((s * 3 % 27) + 1).padStart(2, "0");
  return { created: `2026-${mm}-${dd}`, updated: `2026-05-${uu}` };
}

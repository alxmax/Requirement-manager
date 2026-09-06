// implements: ARCH-VIEWER-007
/*[
      "`confirm <ID>` sets the requirement's `status` to `confirmed`.",
      "`confirm` edits only the value of the first `status:` line in the leading frontmatter.",
      "`confirm` preserves that line's indentation and any trailing inline comment.",
      "`confirm` leaves the body untouched.",
      "`confirm` refuses a requirement with no `implements:` member: it exits non-zero and writes nothing. A `confirmed` requirement with no code is a gate error.",
      "`confirm` exempts a `need` and an `aggregate` from that rule, matching the gate. Both are covered by an edge rather than by a tag.",
      "`confirm` refuses an `aggregate` whose `depends_on` list is empty, because an aggregate with no dependency is an orphan.",
      "A refusal prints the tag the caller needs to add.",
      "`confirm` exits non-zero with a clear message for an unknown id, meaning no `requirements/<ID>.md` exists.",
      "`confirm` warns, without failing, when no `tested-by:` member is linked.",
      "That warning points at the test tag to add, or at the `test_exempt:` opt-out.",
      "`confirm` reminds the caller to refresh the lock and regenerate the map afterwards.",
      "`confirm` is idempotent. An already-`confirmed` requirement is reported, left unchanged, and exits zero.",
    ]Requirement Manager dataset.
 *
 * The baked array below is the fallback — the 13 authored requirements lifted
 * from the real registry plus two in-flight states (a draft + a fresh orphan)
 * and one deprecated capability, so Risk / Problems / Console have signals to
 * show with no engine present. At startup `loadData()` (see loadData.js) tries
 * the engine's `_map.json` export and, when found, calls `setRegistry()` to
 * replace this with live data. Importers use named imports — these are ES live
 * bindings, so a `setRegistry()` reassignment is seen everywhere. */

const BAKED = [
  { id:"ARCH-PARSE-001", area:"CORE", title:"Requirement reading", layer:"bus", status:"confirmed",
    intent:"Turn the requirement files on disk into structured records the rest of the tool reasons about.",
    contract:[
      "`load_requirements` parses each `requirements/*.md` file into a record `{meta, body, path}`, keyed by the frontmatter `id:` or the filename stem. [[REQ-PARSE-890]]",
      "The hand-rolled frontmatter grammar accepts scalars, inline `[a, b]` lists, and block-style `key:` / indented `- item` lists — no external YAML library. [[REQ-PARSE-891]]",
      "A file with no leading `---` block, an underscore-prefixed filename, or a leading UTF-8 BOM are all handled without raising. [[REQ-PARSE-892]]" ],
    acc:[
      "A file with valid frontmatter yields its scalar and list fields in `meta`.",
      "A file without a leading `---` block returns empty `meta` and the whole text as body.",
      "Files starting with `_` are excluded from the result." ],
    impl:["`parse_frontmatter`, `load_requirements` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:73-128"},{role:"tested-by",loc:"scripts/test_reqmap.py:47-800"}],
    deps:[], usedBy:["ARCH-CHECK-006","ARCH-FINDINGS-010","ARCH-MAP-007","ARCH-NEW-004","ARCH-PROMOTE-011"],
    risks:[{signal:"blast-radius",advice:"High fan-in — many capabilities depend on this. Change it only behind its contract, run the full gate + dependents' tests."}] },

  { id:"ARCH-SCAN-002", area:"CORE", title:"Member discovery", layer:"bus", status:"confirmed",
    intent:"Find every place in the code that claims membership of a capability, by scanning for tags.",
    contract:[
      "`scan_members` walks a code root and, in every source file with a known extension, finds inline `role: <ID>` tags and returns `cap_id -> [(role, relative_file, line), ...]`. [[REQ-SCAN-908]]",
      "A single tag may bind several requirements through a comma-separated id list, written `role: <ID>, <ID>, ...`, and `scan_all` runs member, per-criterion and test-level scanning in one walk. [[REQ-SCAN-909]]" ],
    acc:[
      "A file containing `# implements: <ID>` produces a member `(implements, file, line)` under `<ID>`.",
      "Excluded directories are not scanned; member paths are POSIX-relative.",
      "An unreadable file is skipped without aborting the scan." ],
    impl:["`scan_members`, `_prune_dirs`, `load_ignore`, `TAG_RE` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:144-181"},{role:"tested-by",loc:"scripts/test_reqmap.py:146"}],
    deps:[], usedBy:["ARCH-CANDIDATES-009","ARCH-CHECK-006","ARCH-EXTRACT-008","ARCH-MAP-007"],
    risks:[{signal:"blast-radius",advice:"High fan-in — many capabilities depend on this. Treat it as shared foundation (bus)."}] },

  { id:"ARCH-DRIFT-003", area:"CORE", title:"Contract hashing & lock", layer:"bus", status:"confirmed",
    intent:"Detect when a requirement's binding contract changes, so stale code can be re-checked.",
    contract:[
      "`binding_hash` computes a stable 12-character hex content hash over only the normative sections of a requirement body. [[REQ-DRIFT-841]]",
      "`load_lock`/`save_lock` read and write the per-id hash baseline at `requirements/_reqlock.json`, failing open to `{}` on a missing or corrupt file. [[REQ-DRIFT-842]]",
      "Waiving the drift check records who was waived and why, in a versioned sidecar the diff shows, so the one escape hatch in the gate is not also the one thing nobody reviews. [[REQ-DRIFT-988]]" ],
    acc:[
      "Editing only the Description/Notes section does not change the hash.",
      "Editing the Contract section changes the hash.",
      "`load_lock` on a missing or corrupt lock file returns an empty dict (no crash)." ],
    impl:["`binding_hash`, `lock_path`, `load_lock`, `save_lock` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:209-240"},{role:"tested-by",loc:"scripts/test_reqmap.py:103-116"}],
    deps:[], usedBy:["ARCH-CHECK-006"],
    risks:[{signal:"drift",advice:"Lock hash differs from current contract. Re-check the named members, then `check --update-lock`."}],
    drift:true },

  { id:"ARCH-CHECK-006", area:"REQ", title:"The gate", layer:"feature", status:"confirmed",
    intent:"Fail the build when code and requirements have fallen out of sync.",
    contract:["`gate` reports an `ERROR` and exits non-zero for a dangling tag, an invalid status/layer/form/level, a missing `depends_on` target, or an enforced requirement with no `implements:` member. [[REQ-CHECK-828]] details the behaviour.", "`gate` warns (not errors) on contract drift against the lock, a confirmed requirement with no `tested-by:` link, or a confirmed requirement missing its `## Description`/`## Cases` section; `--strict` promotes most of these to errors. [[REQ-CHECK-829]] details the behaviour.", "`gate` warns on a malformed `milestone:` value, and on a corrupt or git-untracked lock file, without affecting the exit code. [[REQ-CHECK-830]] details the behaviour.", "`gate` counts legacy-schema requirements in its summary and warns, without affecting the exit code, on an unvalidated confirmed need, a bus requirement tested only at `@system`, or a `depends_on` cycle. [[REQ-CHECK-831]] details the behaviour.", "`gate` prints the open verify-intent finding count and a summary of requirements, members, errors and warnings; neither affects the exit code. [[REQ-CHECK-832]] details the behaviour.", "With `--update-lock` — always passed by `sync` — `gate` writes the current binding hashes to `requirements/_reqlock.json`; the bare `gate` verb is otherwise report-only. [[REQ-CHECK-833]] details the behaviour."],
    acc:[
      "A tag referencing a non-existent capability produces an `ERROR` and exit 1.",
      "A `confirmed` requirement with no `implements` member produces an `ERROR`.",
      "A drifted contract produces a `WARN` (not an error) naming the member locations." ],
    impl:["`cmd_check`, `warn_if_stale` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:247-296"},{role:"tested-by",loc:"scripts/test_reqmap.py:93-958"}],
    deps:["ARCH-PARSE-001","ARCH-SCAN-002","ARCH-DRIFT-003"], usedBy:["ARCH-INIT-012"], risks:[] },

  { id:"ARCH-EXTRACT-008", area:"REQ", title:"Legacy extraction", layer:"feature", status:"confirmed",
    intent:"Bootstrap a registry on a brownfield codebase by proposing draft requirements from untagged code.",
    contract:[
      "`draft` walks every untagged scannable code file, skipping tagged and `.reqmapignore`-matched ones. [[REQ-EXTRACT-849]] details the behaviour.",
      "`draft` proposes one `requirements/DRAFT-*.md` per remaining file, marked `status: draft` with a TODO contract. [[REQ-EXTRACT-850]] details the behaviour.",
      "`draft` assigns a cheap risk score from `TODO`/`FIXME`/`HACK`/`XXX` markers, suppressions and file size, and never overwrites an existing draft. [[REQ-EXTRACT-851]] details the behaviour.",
      "Extraction drafts all three specification rungs and marks every one it invented, so a corpus starts as a pyramid the author corrects rather than a flat list. [[REQ-EXTRACT-981]] details the behaviour." ],
    acc:[
      "An untagged `.py`/`.js`/`.ts`/`.c`/`.cpp` file yields one `DRAFT-*` draft.",
      "A file matching a `.reqmapignore` pattern is skipped (no draft proposed).",
      "A file containing `TODO`/`FIXME` scores higher risk and is flagged `REVIEW`." ],
    impl:["`cmd_extract`, `_draft_id`, `_risk`, `classify_prose` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:495-641"},{role:"tested-by",loc:"scripts/test_reqmap.py:194-429"}],
    deps:["ARCH-SCAN-002"], usedBy:["ARCH-INIT-012"], risks:[] },

  { id:"ARCH-CANDIDATES-009", area:"REQ", title:"Capability candidates", layer:"feature", status:"confirmed",
    intent:"Stage 1 of AI extraction: emit a deterministic capability plan from legacy code, writing no requirement files.",
    contract:["`draft --plan` emits a single JSON object, to stdout or to `--out PATH`, shaped `{engine_version, bus[], candidates[]}`, and writes no `.md` files. [[REQ-CANDIDATES-826]]", "Each candidate carries `{suggested_id, suggested_layer, files[], docstrings{}, signatures[], imports[], depends_on[], tested_by[], importer_count, existing_req, loc, split_candidate, is_test}`. [[REQ-CANDIDATES-827]]"],
    acc:[
      "Running `candidates` writes zero `.md` files and emits valid JSON.",
      "An import of a local module yields a `depends_on` edge to that module's candidate.",
      "A module imported by ≥ the bus threshold is suggested as `bus`." ],
    impl:["`cmd_candidates`, `_py_facts`, `_js_facts`, `_load_capmap` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:658-805"},{role:"tested-by",loc:"scripts/test_reqmap.py:521-908"}],
    deps:["ARCH-SCAN-002"], usedBy:[], risks:[] },

  { id:"ARCH-FINDINGS-010", area:"REQ", title:"Open-findings report", layer:"feature", status:"confirmed",
    intent:"Roll up every requirement's open \"verify intent\" questions into one reviewable _findings.md.",
    contract:["`sync` collects the bullet items under each requirement's `## Verify intent` section. [[REQ-FINDINGS-853]]", "In raw mode, `sync` groups the collected findings by requirement and writes the raw report. [[REQ-FINDINGS-854]]", "When a `_findings_triage.json` sidecar exists and raw mode is off, `sync` renders a classified view ordered by severity. [[REQ-FINDINGS-855]]", "`sync` is deterministic and stdlib-only; `map` and `gate` fold its output in without ever classifying a finding themselves. [[REQ-FINDINGS-856]]"],
    gwt:"AC-1\n  Given  two requirements, one with two Verify-intent bullets and one with only the \"None —\" placeholder\n  When   findings runs in raw mode\n  Then   _findings.md lists the two bullets and reports \"2 open finding(s) across 1 requirement(s)\"",
    impl:["`cmd_findings`, `render_findings` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:911-998"},{role:"tested-by",loc:"scripts/test_reqmap.py:594-891"}],
    deps:["ARCH-PARSE-001"], usedBy:[], risks:[] },

  { id:"ARCH-MAP-007", area:"REQ", title:"Requirement graph (_map.json)", layer:"feature", status:"confirmed",
    intent:"Render the whole registry as navigable diagrams a human can read at a glance.",
    contract:["`sync` generates `_map.json` under `requirements/`, one node per requirement and one edge per `depends_on`. [[REQ-MAP-870]]", "`_map.json` carries top-level `repo`, `engine_version` and `todos` fields; `repo`/`engine_version` are excluded from the freshness diff since each varies with the build environment, not the corpus. [[REQ-MAP-871]]", "Reading a requirement's clauses folds a wrapped line back into the clause above it, so a multi-line clause is never truncated to its first physical line. [[REQ-MAP-872]]", "The `intent` field carries a requirement's first blockquote, joined into one line, and is empty when that quote just repeats the Contract. [[REQ-MAP-873]]"],
    acc:[
      "The generated files contain one node per requirement and one edge per `depends_on`.",
      "`_map.md` contains 4 Mermaid code blocks, each with a legend.",
      "`_map.json` parses to `{engine_version, nodes, edges}` with one node per requirement." ],
    impl:["`cmd_map`, `render_html`, `render_md`, the `_mermaid_*` generators in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:1033-1948"},{role:"tested-by",loc:"scripts/test_reqmap.py:237-1069"}],
    deps:["ARCH-PARSE-001","ARCH-SCAN-002"], usedBy:["ARCH-INIT-012","ARCH-NEXT-013"], risks:[] },

  { id:"ARCH-NEW-004", area:"REQ", title:"Scaffold a requirement", layer:"feature", status:"confirmed",
    intent:"Create a new requirement file from the template, so every capability starts in the same shape.",
    contract:[
      "Given a capability id, `new` writes `requirements/<ID>.md`, stamped from the scaffold (an on-disk `templates/requirement.md` if present, else the built-in template) with the placeholder `AREA-NAME-NNN` replaced by that id, creating the requirements directory if needed. [[REQ-NEW-881]]",
      "`new` refuses to overwrite an existing file, exiting non-zero and writing nothing; it warns but still succeeds on a same-area number collision, and its scaffold is pre-shaped to pass the linter's own authoring rules. [[REQ-NEW-882]]" ],
    acc:[
      "`new FOO-NEW-099` on an empty registry creates `requirements/FOO-NEW-099.md` with that id.",
      "Running `new` for an id that already exists exits non-zero and writes nothing." ],
    impl:["`cmd_new`, `REQUIREMENT_TEMPLATE` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:425"},{role:"tested-by",loc:"scripts/test_reqmap.py:463"}],
    deps:["ARCH-PARSE-001"], usedBy:[], risks:[] },

  { id:"ARCH-PROMOTE-011", area:"REQ", title:"Confirmation is a human's answer", layer:"feature", status:"draft",
    intent:"Confirming is not a command — a human writes the status, and an edit takes it back.",
    contract:[
      "There is **no `confirm` command.** A status is set by editing the frontmatter, which is what a human sign-off is: someone read it and wrote it down. The engine still owns the edit mechanics, so nothing else has to get them right. [[REQ-PROMOTE-894]] details the behaviour.",
      "**An edited confirmed contract goes back to `draft`.** When `sync` finds that a `confirmed` or `implemented` requirement's binding content no longer matches the lock, it writes `draft` into that requirement and advances the baseline. [[REQ-PROMOTE-974]] details the behaviour.",
      "**`--accept-drift` is the escape hatch, and it is a human saying so:** it keeps the status and advances the baseline. It exists because \"I edited it and it is still valid\" is a real answer — it just has to be given, not assumed.",
      "**The invariant that a confirmed requirement points at code is enforced by the gate, not by a command.** `RM006` is an error, so a status written by hand with no `implements:` member fails at the next run." ],
    gwt:"CASE-1\n  Given  a confirmed requirement whose contract has just been edited\n  When   sync runs without --accept-drift\n  Then   its frontmatter reads status: draft, the run says so by name, and the lock advances",
    impl:["`_write_frontmatter_status` and the demotion branch of `cmd_check` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:446-461"},{role:"tested-by",loc:"scripts/test_reqmap.py:1114"}],
    deps:["ARCH-PARSE-001"], usedBy:[], risks:[] },


  { id:"ARCH-INIT-012", area:"REQ", title:"First-use bootstrap", layer:"feature", status:"confirmed",
    intent:"One command that turns a fresh repo into a tracked one — scaffold, draft, lock, map, and say what's next.",
    contract:[
      "`init` creates the requirements folder and a starter `.reqmapignore` when either is missing, never overwriting one that already exists. [[REQ-INIT-860]]",
      "`init` drafts requirements from untagged code, writes the lock, then builds the map, in that order, and ends with a short summary pointing at the one next command. [[REQ-INIT-861]]" ],
    acc:[
      "`init` on a fresh repo creates `requirements/` and a `.reqmapignore`.",
      "After `init`, `_map.md`, `_map.json` and the drift lock exist.",
      "`init` on a repo with no extractable code prints the distinct \"no requirements were extracted\" message." ],
    impl:["`cmd_init` in `reqmap.py` — orchestrates extract → check → map."],
    members:[{role:"implements",loc:"scripts/reqmap.py:1210-1237"},{role:"tested-by",loc:"scripts/test_reqmap.py:1265"}],
    deps:["ARCH-EXTRACT-008","ARCH-CHECK-006","ARCH-MAP-007"], usedBy:[], risks:[] },

  { id:"ARCH-NEXT-013", area:"REQ", title:"What-should-I-do-next report", layer:"feature", status:"confirmed",
    intent:"Render the map's risk surface in the terminal as counted, actionable buckets.",
    contract:[
      "`next` groups every requirement's open risk signals — read from the same `_risk_signals`/`RISK_ADVICE` source the Risk tab uses — into action buckets, behind a progress header. [[REQ-NEXT-883]]",
      "`next` surfaces exactly the actionable buckets, most urgent first: `unimplemented` (Orphans), `untested` (Needs tests), `unverified-intent` (Needs intent review), `unreviewed` (Drafts to review), plus advisory Granularity/Redundancy buckets and an Untagged-files bucket. [[REQ-NEXT-884]]",
      "Within a bucket, `next` orders items by `priority` rank, then by descending extract `risk:` score, then by id, and names the file to open. [[REQ-NEXT-885]]",
      "By default `next` shows at most the top few items of a bucket, truncating each independently with a `... N more` line; `--all` lists everything. [[REQ-NEXT-886]]",
      "With no requirements at all, `next` prints a distinct message pointing at `init`/`new`; otherwise it prints the all-clear line when nothing is open. Either way it writes no file and always exits 0. [[REQ-NEXT-887]]" ],
    acc:[
      "The output starts with a progress header carrying confirmed/tested/draft counts.",
      "A confirmed requirement with code but no `tested-by` lists under \"Needs tests\".",
      "An empty registry prints the \"no requirements yet\" message; it writes no files and returns 0." ],
    impl:["`cmd_next`, `_risk_score` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:1083-1093"},{role:"tested-by",loc:"scripts/test_reqmap.py:1174"}],
    deps:["ARCH-MAP-007"], usedBy:[], risks:[] },

  /* ---- realistic in-flight states (extraction + a fresh orphan tag) ------- */
  { id:"DRAFT-cache-utils", area:"REQ", title:"cache_utils (drafted)", layer:"feature", status:"draft",
    intent:"TODO — observed behavior of scripts/cache_utils.py, captured by extract. Not yet reviewed.",
    contract:["TODO: author the contract. Observed: an in-memory LRU with a TTL sweep and a `# FIXME: race on evict` marker."],
    acc:["TODO: promote acceptance from the existing tests, if any."],
    impl:["scripts/cache_utils.py (untagged at draft time)"],
    members:[], deps:[], usedBy:[],
    risks:[{signal:"unreviewed",advice:"Drafted from code by extract — review intent, then `promote DRAFT-cache-utils`."}],
    riskScore:2 },

  { id:"REQ-SYNC-014", demoOnly:true, area:"REQ", title:"Background sync", layer:"feature", status:"in-progress",
    intent:"Keep the local registry in step with a remote mirror on a timer.",
    contract:["It shall reconcile local and remote requirement files on an interval without blocking the gate."],
    acc:["TODO"],
    impl:["src/sync.py:88 — tag present, no requirement matched at scan time"],
    members:[], deps:["ARCH-PARSE-001"], usedBy:[],
    risks:[{signal:"unimplemented",advice:"Confirmed/in-progress but no resolving member — the gate reports this as an ERROR (orphan). Add the `implements:` tag or the requirement file."}] },

  /* one deprecated capability — kept, not deleted; the gate skips it */
  { id:"REQ-CACHE-014", demoOnly:true, area:"REQ", title:"In-memory response cache", layer:"feature", status:"deprecated",
    intent:"Superseded by the shared cache service — kept for history, skipped by the gate.",
    contract:["It shall memoize parsed requirement records for the duration of a single run."],
    acc:["A second load within one run returns the memoized record."],
    impl:["scripts/cache.py (retired)"],
    members:[{role:"implements",loc:"scripts/cache.py:18-74"}],
    deps:[], usedBy:[], risks:[], supersededBy:"REQ-PARSE-021" },
];

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
// The CLI as data, straight off _map.json (generated from the engine's command
// registry). Empty in the baked fallback: a map produced before v4.0.0 carries none.
export let COMMANDS = [];
/* The engine's own `health` and `design` records, verbatim. Deliberately NOT
 * recomputed here: `next` already prints these two numbers, and a second
 * definition in JavaScript is how the CLI and the viewer come to disagree
 * about how the repo is doing. Null until a map carrying them is loaded —
 * an older map has neither key, and the rail then shows nothing rather than
 * an invented zero.  implements: REQ-VIEWER-969 */
export let HEALTH = null;
export let DESIGN = null;

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

/** Adopt the engine's health + design records (both absent on older maps). */
export function setScores(health, design) {          // implements: REQ-VIEWER-969
  HEALTH = (health && typeof health.score === "number") ? health : null;
  DESIGN = (design && typeof design.score === "number") ? design : null;
}

/** Replace the documented command list (engine-emitted; absent on older maps). */
export function setCommands(list) { COMMANDS = Array.isArray(list) ? list : []; }

/** Set the owner/repo name the loaded map describes (engine-emitted). */
export function setRepo(name) {
  REPO = name || null;
}

/** Replace the TODO list with data parsed from TODO.md (engine-emitted). */
export function setTodos(list) {
  TODOS = Array.isArray(list) ? list : [];
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
  if (r.layer === "need" || r.layer === "aggregate") return "exempt";  // covered by an edge, not by code
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

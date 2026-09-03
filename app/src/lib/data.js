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
      "`load_requirements` parses each `requirements/*.md` file into a record `{meta, body, path}`.",
      "`meta` is the parsed frontmatter, and `body` is the markdown after the frontmatter block.",
      "The `id` comes from the frontmatter `id:` field, falling back to the filename stem.",
      "The grammar supports scalars, inline `[a, b]` lists, and block-style lists written as `key:` then indented `- item`.",
      "A trailing `# comment` is stripped from a value.",
      "Matching surrounding quotes are removed from a scalar.",
      "An inline list missing its closing `]` is parsed leniently, rather than kept as a literal string.",
      "A file with no leading `---` block yields empty `meta` and the whole text as `body`.",
      "A file whose name starts with `_` (a lock, the generated map) is excluded.",
      "A leading UTF-8 BOM is tolerated." ],
    acc:[
      "A file with valid frontmatter yields its scalar and list fields in `meta`.",
      "A file without a leading `---` block returns empty `meta` and the whole text as body.",
      "Files starting with `_` are excluded from the result." ],
    impl:["`parse_frontmatter`, `load_requirements` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:73-128"},{role:"tested-by",loc:"scripts/test_reqmap.py:47-800"}],
    deps:[], usedBy:["ARCH-CHECK-006","ARCH-FINDINGS-010","ARCH-MAP-007","ARCH-NEW-004","ARCH-PROMOTE-011","ARCH-SCAN-005"],
    risks:[{signal:"blast-radius",advice:"High fan-in — many capabilities depend on this. Change it only behind its contract, run the full gate + dependents' tests."}] },

  { id:"ARCH-SCAN-002", area:"CORE", title:"Member discovery", layer:"bus", status:"confirmed",
    intent:"Find every place in the code that claims membership of a capability, by scanning for tags.",
    contract:[
      "`scan_members` walks a code root and, in every source file with a known extension, finds the inline tags.",
      "`scan_members` returns `cap_id -> [(role, relative_file, line), ...]`.",
      "A role is one of `implements`, `generated-from`, `validated-against` and `tested-by`.",
      "A tag ID matches `[A-Z][A-Z0-9]*(-[A-Z0-9]+)+`.",
      "A left-boundary guard prevents a substring match such as `reimplements:` or `x-implements:` being read as a real tag.",
      "The same `(role, ID)` appearing twice on one line is recorded once.",
      "File paths are reported repo-root-relative, with POSIX separators.",
      "A single tag may bind several requirements through a comma-separated id list, written `role: <ID>, <ID>, ...`.",
      "Each id in that list is recorded as a member of the same `(role, file, line)`.",
      "A whole-system doc generated from many requirements (`generated-from: A, B, C`) is therefore a member of each, and drifts when ANY of them changes.",
      "`.git`, `node_modules`, `__pycache__` and the SSOT `requirements/` directory are skipped.",
      "The SSOT directory is matched by realpath, so a source package merely named `requirements/` is still scanned.",
      "Paths matching `.reqmapignore` are excluded.",
      "An unreadable file is skipped without aborting the scan.",
      "`scan_all` returns the members, the per-criterion coverage and the verification levels from a single walk, and each result equals what the three separate scanners return." ],
    acc:[
      "A file containing `# implements: <ID>` produces a member `(implements, file, line)` under `<ID>`.",
      "Excluded directories are not scanned; member paths are POSIX-relative.",
      "An unreadable file is skipped without aborting the scan." ],
    impl:["`scan_members`, `_prune_dirs`, `load_ignore`, `TAG_RE` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:144-181"},{role:"tested-by",loc:"scripts/test_reqmap.py:146"}],
    deps:[], usedBy:["ARCH-CANDIDATES-009","ARCH-CHECK-006","ARCH-EXTRACT-008","ARCH-MAP-007","ARCH-SCAN-005"],
    risks:[{signal:"blast-radius",advice:"High fan-in — many capabilities depend on this. Treat it as shared foundation (bus)."}] },

  { id:"ARCH-DRIFT-003", area:"CORE", title:"Contract hashing & lock", layer:"bus", status:"confirmed",
    intent:"Detect when a requirement's binding contract changes, so stale code can be re-checked.",
    contract:[
      "`binding_hash` computes a stable 12-character hex content hash over only the normative sections of a requirement body.",
      "The normative sections are the `Contract` and `Acceptance` headings, plus the legacy `Input`/`Output`/`Acceptance` headings kept for back-compat.",
      "Rationale, notes, verify-intent, links and the member list stay outside the hash, so they may change without tripping drift.",
      "The hash is deterministic for identical normative content.",
      "`load_lock` and `save_lock` read and write the per-id hash baseline at `requirements/_reqlock.json`.",
      "A missing, empty or unparseable lock loads as an empty mapping, never a crash.",
      "`save_lock` creates the requirements directory if it is absent.",
      "`save_lock` writes sorted, indented JSON, so the lock file is diff-stable." ],
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
    contract:[[
      "`gate` reports an `ERROR` and exits non-zero for every condition in this group.",
      "A dangling tag — a code tag referencing a capability no requirement defines — is such a condition.",
      "An invalid `status` or an invalid `layer` is such a condition.",
      "A `depends_on` pointing at a missing id is such a condition.",
      "An enforced requirement with no `implements:` member is such a condition.",
      "A requirement is enforced when its status is `in-progress`, `implemented` or `confirmed`.",
      "A `layer: need` requirement is exempt from that `implements:` rule — see [[ARCH-TRACE-020]].",
      "`gate` reports drift as a `WARN` under plain `gate`: a `confirmed` requirement whose binding hash differs from the lock.",
      "The drift warning names the member `file:line` locations to re-check.",
      "`gate --strict` promotes drift (and the no-`tested-by:` warning below, and member drift) to an `ERROR`. The `depends_on`-cycle warning and the legacy-schema warning are the two exceptions — they stay warnings even under `--strict`.",
      "A `confirmed` requirement with no `tested-by:` member is a `WARN`.",
      "A requirement carrying a `test_exempt: <reason>` opt-out in its frontmatter is exempt from that test warning.",
      "A `layer: need` requirement is exempt from it too.",
      "A `confirmed` requirement missing a `## Description` section is a `WARN`, in both the `bus` and `feature` layers. It does not affect the exit code.",
      "A `confirmed` requirement missing a `## Cases` section is a `WARN`, in both the `bus` and `feature` layers. It does not affect the exit code.",
      "The requirement `milestone:` field is optional. When present it matches the version shape `v<digits>[.<digits>…]`, for example `v1.14`.",
      "A malformed `milestone:` value is a `WARN`, because that field is roadmap-only metadata and never build-critical.",
      "A `deprecated` requirement is exempt from the `milestone:` shape check.",
      "A present-but-unreadable `_reqlock.json` is a `WARN`. Drift is skipped for that run rather than crashing.",
      "A lock sidecar (`_reqlock.json` or `_memberlock.json`) that exists on disk but is **not git-tracked** is a `WARN` naming the file.",
      "An uncommitted lock silently disables drift detection on a fresh CI checkout, which has no baseline to compare against.",
      "That git-tracking check is fail-open: `gate` stays silent when git is unavailable or the tree is not a work tree.",
      "`gate` names every sectioned-form requirement whose body lacks a `## Verify intent` section in one aggregated legacy-schema `WARN`. Atomic-form requirements (`form: atomic`) carry no such heading by design and are excluded from this check.",
      "`gate` counts those legacy-schema requirements in the summary.",
      "The legacy-schema warning does not affect the exit code.",
      "A confirmed `need` with no `validated-against:` member is a `WARN`, once the repo carries at least one such tag (see [[ARCH-VLEVEL-037]]).",
      "A confirmed `bus` requirement whose levelled `tested-by:` links are all `@system` is a `WARN`.",
      "A `depends_on` cycle is a `WARN` naming the whole chain, once per distinct cycle.",
      "The cycle warning stays a warning under `--strict`, so an existing corpus keeps its exit code when the engine is upgraded.",
      "`gate` prints an advisory line carrying the open verify-intent finding count when that count is above zero.",
      "That advisory line does not affect the exit code.",
      "`gate` prints a summary of requirements, members, errors and warnings.",
      "With `--update-lock`, `gate` writes the current binding hashes to `requirements/_reqlock.json`.",
      "`sync` always passes `--update-lock`. The deprecated `check` alias does not — it only advances the lock when the caller explicitly passes `--update-lock`.",
      "The `gate` verb itself is report-only.",
    ]],
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
      "`draft` walks every untagged scannable code file — the extensions and basenames the scan reads — plus prose in the capability bucket.",
      "`draft` skips a file that already carries a member tag.",
      "`draft` honors `.reqmapignore`, the same fnmatch globs `scan` respects.",
      "A file matching an ignore pattern is never drafted — notably the vendored `scripts/reqmap.py` engine itself.",
      "`draft` proposes one `requirements/DRAFT-*.md` per remaining file.",
      "Every proposal carries `status: draft` and a TODO body. It captures observed behavior, and never canonizes intent or correctness.",
      "A proposal's Contract section opens with \"Every bullet below is binding.\", matching what `new` scaffolds, so promoting a draft needs no reshaping.",
      "`draft` creates the requirements directory if it is absent.",
      "Draft ids are path-aware, so two files sharing a basename do not collide.",
      "`draft` assigns a cheap risk score from `TODO`/`FIXME`/`HACK`/`XXX` markers, suppressions and file size.",
      "`draft` routes a score of 2 or more to `REVIEW`, and any lower score to `auto-baseline`.",
      "Re-running `draft` never overwrites an existing draft.",
      "A code proposal's WHERE section lists the file's observed surface — the module docstring's first line and its top-level signatures — when the language has a parser.",
      "That surface is an authoring hint under WHERE, never a Contract line. The Contract stays a TODO until a human writes it." ],
    acc:[
      "An untagged `.py`/`.js`/`.ts`/`.c`/`.cpp` file yields one `DRAFT-*` draft.",
      "A file matching a `.reqmapignore` pattern is skipped (no draft proposed).",
      "A file containing `TODO`/`FIXME` scores higher risk and is flagged `REVIEW`." ],
    impl:["`cmd_extract`, `_draft_id`, `_risk`, `classify_prose` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:495-641"},{role:"tested-by",loc:"scripts/test_reqmap.py:194-429"}],
    deps:["ARCH-SCAN-002"], usedBy:["ARCH-INIT-012"], risks:[] },

  { id:"ARCH-CANDIDATES-009", area:"REQ", title:"Capability candidates", layer:"feature", status:"confirmed",
    intent:"Stage 1 of AI extraction: emit a deterministic capability plan from legacy code, writing no requirement files.",
    contract:[
      "`plan` emits a single JSON object, to stdout or to `--out PATH`, shaped `{engine_version, bus[], candidates[]}`.",
      "`plan` writes NO `.md` files. It cannot repeat `draft`'s empty-stub failure.",
      "`plan` walks the code with the same exclusions as scanning: noise dirs, the SSOT dir, and `.reqmapignore` resolved in `requirements/` first.",
      "`plan` gathers per-file facts: module and symbol docstrings, top-level signatures, import targets, and line count.",
      "`plan` lists every scannable code file as a candidate, the same set `draft` walks. A file in a language `plan` cannot parse is still a candidate, with empty facts.",
      "`plan` reads top-level signatures from Python via `ast` — functions, classes and the public methods of each class — and from JS/TS via best-effort parsing.",
      "An unparseable file yields empty facts. It never aborts the plan.",
      "Each candidate carries `{suggested_id, suggested_layer, files[], docstrings{}, signatures[], imports[], depends_on[], tested_by[], importer_count, existing_req, loc, split_candidate, is_test}`.",
      "`is_test` is true when every file of the candidate is test code by convention: a `tests/`-style directory segment, a `test_*` basename, or a `*_test`/`*.spec` suffix.",
      "`depends_on` is derived from imports resolved to other candidates.",
      "`suggested_layer` is `bus` when `importer_count ≥ BUS_FANIN_THRESHOLD`, else `feature`.",
      "A file already carrying an `implements:` tag is reported via `existing_req`.",
      "`plan` groups files by `requirements/_capmap.json` when that file is present, and treats it as authoritative.",
      "Absent `_capmap.json`, `plan` falls back to one candidate per file." ],
    acc:[
      "Running `candidates` writes zero `.md` files and emits valid JSON.",
      "An import of a local module yields a `depends_on` edge to that module's candidate.",
      "A module imported by ≥ the bus threshold is suggested as `bus`." ],
    impl:["`cmd_candidates`, `_py_facts`, `_js_facts`, `_load_capmap` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:658-805"},{role:"tested-by",loc:"scripts/test_reqmap.py:521-908"}],
    deps:["ARCH-SCAN-002"], usedBy:[], risks:[] },

  { id:"ARCH-FINDINGS-010", area:"REQ", title:"Open-findings report", layer:"feature", status:"confirmed",
    intent:"Roll up every requirement's open \"verify intent\" questions into one reviewable _findings.md.",
    contract:[
      "`findings` scans every requirement and collects the bullet items under each one's `## Verify intent` section.",
      "`findings` writes them into a single `_findings.md` in the requirements directory.",
      "`findings` excludes the \"None — …\" placeholder bullet. A requirement that recorded no open question therefore contributes nothing.",
      "In raw mode, `findings` groups the findings by requirement.",
      "Each group and the document header carry a count.",
      "With zero findings, `findings` still writes a well-formed file stating that none are open.",
      "With the raw flag set, `findings` ignores any sidecar and emits the raw grouped list.",
      "When the sidecar exists and raw mode is off, `findings` renders a classified view.",
      "That view puts confirmed bugs first, ordered by severity from high to low, then product/config decisions, then intentional, then false-positive.",
      "A bug entry shows its location and its recommended fix when those are present.",
      "`findings` emits an advisory staleness note when the count of raw verify-intent items differs from the count of triaged items in the sidecar.",
      "`findings` is deterministic and stdlib-only. It never classifies a finding itself.",
      "`findings` writes no file other than `_findings.md`.",
      "`map` rewrites `_findings.md` when that file already exists. `sync` runs `map`, so it refreshes a committed report along with the map.",
      "`map` never creates `_findings.md`. Running `findings` once opts a repo in.",
      "`map --check` reports `_findings.md` stale when the committed copy differs from a fresh render, the same way it judges `_map.md` and `_map.json`. An absent file is never stale.",
      "The gate prints a non-error advisory line carrying the open-findings count, whenever that count is greater than zero.",
      "The open-findings count never changes the gate's exit code." ],
    gwt:"AC-1\n  Given  two requirements, one with two Verify-intent bullets and one with only the \"None —\" placeholder\n  When   findings runs in raw mode\n  Then   _findings.md lists the two bullets and reports \"2 open finding(s) across 1 requirement(s)\"",
    impl:["`cmd_findings`, `render_findings` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:911-998"},{role:"tested-by",loc:"scripts/test_reqmap.py:594-891"}],
    deps:["ARCH-PARSE-001"], usedBy:[], risks:[] },

  { id:"ARCH-MAP-007", area:"REQ", title:"Requirement graph (_map.json)", layer:"feature", status:"confirmed",
    intent:"Render the whole registry as navigable diagrams a human can read at a glance.",
    contract:[[
      "`map` generates `_map.json` under `requirements/`, and `export` writes the same file alone.",
      "`_map.json` is a derived view. It is regenerated, never edited.",
      "`_map.json` carries one node per requirement and one edge per `depends_on`.",
      "Each node carries its requirement's id, layer, status, area, title, intent, Contract/Verify-intent/Notes bullets, acceptance, members (`role`/`loc`), `deps`, `used_by`, and risk signals.",
      "A node's `acc` list carries one entry per acceptance criterion, whether the criterion is written as a labelled `AC-N` block or as a bullet.",
      "`_map.json` carries a top-level `repo` field: a best-effort `owner/repo`, else the repo directory name, else null.",
      "`repo` identifies the project the map describes, for display in the viewer header.",
      "`repo` is derived from the git remote, so it differs across forks and clones. It is therefore excluded from the `map --check` freshness diff.",
      "Resolving `repo` never raises and never blocks map generation, because git may be absent or the tree may not be a checkout.",
      "`engine_version` is likewise excluded from the `map --check` freshness diff. Updating the vendored engine alone never makes a committed map stale; the next `sync` refreshes it.",
      "`_map.json` carries a top-level `todos` array, derived from `TODO.md` via `_parse_todos`, so the viewer's Roadmap tab can show planned work alongside requirements.",
      "Reading a requirement's clauses folds a wrapped line back into the clause above it, so a multi-line clause is never truncated to its first physical line.",
      "A clause-group label groups the clauses below it: a bold-only line written flush left. A label is a heading, not a clause, and never folds into the clause above.",
      "Position decides a label, not the bold markers alone. An indented wrapped line folds even when it opens and closes on bold spans, so a two-part clause keeps both halves.",
      "The `intent` field carries a requirement's first blockquote, joined into one line.",
      "The `intent` field is empty when that quote and the Contract say the same thing.",
      "An atomic requirement is that case: its quote is its single obligation, so the map emits the text once, under `contract`.",
      "`show` follows the same rule, printing no intent line above a Contract that repeats it.",
      "`map --check` fails when a committed generated file differs from a fresh render.",
      "The gate reports the same staleness as a warning, so a commit prepared with `gate` alone cannot be surprised by that failure in CI.",
      "The gate never regenerates the map. It only reports.",
      "All requirement-derived text is JSON-encoded in `_map.json`, which neutralizes any hostile id, title or body by construction. There is no markup context to break out of.",
    ]],
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
      "Given a capability id, `new` writes `requirements/<ID>.md`, stamped from the scaffold with the placeholder `AREA-NAME-NNN` replaced by that id.",
      "`new` creates the requirements directory if it is absent.",
      "The scaffold is the engine's built-in template.",
      "An on-disk `templates/requirement.md`, when present, overrides the built-in template.",
      "`new` refuses to overwrite an existing file. It exits non-zero and writes nothing.",
      "The emitted Contract section opens with \"Every bullet below is binding.\", so the author writes clauses in present tense without a `shall` or `must` on each line.",
      "The scaffold's guidance names the authoring rules the linter enforces, so a file written from it starts clean.",
      "`new` warns, and still exits zero, when another requirement in the same area already uses the same `NNN` number. Ids stay unique by their full text; the warning keeps numbers unambiguous in conversation." ],
    acc:[
      "`new FOO-NEW-099` on an empty registry creates `requirements/FOO-NEW-099.md` with that id.",
      "Running `new` for an id that already exists exits non-zero and writes nothing." ],
    impl:["`cmd_new`, `REQUIREMENT_TEMPLATE` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:425"},{role:"tested-by",loc:"scripts/test_reqmap.py:463"}],
    deps:["ARCH-PARSE-001"], usedBy:[], risks:[] },

  { id:"ARCH-PROMOTE-011", area:"REQ", title:"Promote", layer:"feature", status:"confirmed",
    intent:"One command to perform the human-validation step — flip a reviewed requirement to confirmed.",
    contract:[[
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
    ]],
    gwt:"AC-1\n  Given  a baseline requirement with an implements: member\n  When   promote <ID> runs\n  Then   its frontmatter status becomes confirmed, the body is byte-identical, and exit is 0",
    impl:["`cmd_promote`, `_set_frontmatter_status` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:446-461"},{role:"tested-by",loc:"scripts/test_reqmap.py:1114"}],
    deps:["ARCH-PARSE-001"], usedBy:[], risks:[] },

  { id:"ARCH-SCAN-005", area:"REQ", title:"List members per capability", layer:"feature", status:"confirmed",
    intent:"Show, for every capability, which code claims it — and which capabilities have no code.",
    contract:[
      "`scan` prints every capability id, followed by its `role file:line` members, one member per line.",
      "The listed ids are the union of the loaded requirements and the discovered members, in sorted order.",
      "A capability with no members prints `(no members found)`.",
      "A tag pointing at an id with no requirement still appears in the listing, so orphan tags and unimplemented requirements both surface." ],
    acc:[
      "A capability with two tags prints both `role file:line` lines under its id.",
      "A requirement with no members prints `(no members found)`." ],
    impl:["`cmd_scan` in `reqmap.py`."],
    members:[{role:"implements",loc:"scripts/reqmap.py:260"},{role:"tested-by",loc:"scripts/test_reqmap.py:507"}],
    deps:["ARCH-PARSE-001","ARCH-SCAN-002"], usedBy:[], risks:[] },

  { id:"ARCH-INIT-012", area:"REQ", title:"First-use bootstrap", layer:"feature", status:"confirmed",
    intent:"One command that turns a fresh repo into a tracked one — scaffold, draft, lock, map, and say what's next.",
    contract:[
      "`init` creates the requirements folder if it is missing.",
      "`init` writes a starter `.reqmapignore` only if the repo has none. It never overwrites one that is already there.",
      "The starter file lists `scripts/reqmap.py`. Without that line, the engine's own tags look like they point at requirements that do not exist.",
      "The starter file also lists `.worktrees/**` and `.claude/worktrees/**` — the two places an isolated agent worktree is created. Each holds a full second copy of the repo, so without those lines every member is counted twice and the copies' tags read as dangling refs: errors that are not in the code, in files a clean CI checkout never has.",
      "One exception: if the engine describes itself in this repo, `init` leaves the line out and writes a comment saying why. There the engine is ordinary tracked code, so the scan keeps reading it.",
      "\"Describes itself\" means `scripts/reqmap.py` carries tags whose ids match requirements already in the repo.",
      "`init` drafts requirements from untagged code, writes the lock, then builds the map, in that order. When it finishes, the repo passes the gate and has a map.",
      "`init` ends with a short summary naming one next command: `reqmap.py next`. Not a list of every option.",
      "If nothing was drafted, `init` says so in plain words and points at `new`. It never prints a count summary that hides an empty result.",
      "Running `init` twice is safe. The second run refreshes the lock and the map, then prints the summary again.",
      "A second run never deletes a requirement someone wrote, and never edits an existing `.reqmapignore`." ],
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
      "`next` groups every requirement's open risk signals into action buckets.",
      "`next` reads those signals from `_risk_signals` and their wording from `RISK_ADVICE`, the same two sources that drive the Risk tab. There is never a second signal path.",
      "`next` prints a progress header `N requirement(s) · X confirmed · Y tested · Z draft(s)` before the buckets.",
      "In that header, `tested` counts the requirements that have a `tested-by` member.",
      "`next` surfaces exactly the actionable buckets: `unimplemented` (Orphans), `untested` (Needs tests), `unverified-intent` (Needs intent review), `unreviewed` (Drafts to review).",
      "`next` prints those four buckets in that order, most urgent first.",
      "`next` also prints two advisory buckets below the four action buckets: `Granularity` (a requirement with more acceptance criteria than lint's `LINT_AC_MAX`) and `Redundancy` (requirements whose Description states the same obligation, byte-identical once normalized).",
      "Granularity's set comes from `_oversize`, the one predicate `lint_requirement`'s `ac-count-high` check also calls — the same threshold, the same `LINT_STATUSES` scope, and the same `lint_exempt: [ac-count-high]` honoring, so `next` and `lint` never disagree on which requirement is oversize.",
      "Redundancy's set comes from `_redundant_groups`, the exact-match floor `dupes` also uses.",
      "Neither advisory bucket changes `next`'s exit code.",
      "`next` omits `blast-radius`, because that signal is a caution, not a task.",
      "`next` surfaces every scannable file that carries no membership tag as an \"Untagged files\" bucket, ranked lowest of all.",
      "That bucket omits prose in the auto-draft \"ignore\" bucket (`CLAUDE.md`, `TODO.md`, `CHANGELOG.md`, `LICENSE`, `_`-prefixed files): those are invisible to reqmap by contract.",
      "`next` skips that untagged scan when the caller gives no `code_root`.",
      "An Orphans item may have members recorded in the committed `_map.json` that this scan did not find. Then `next` adds a note naming one such member and suggesting `--code <dir>`. The note is advice; the item stays in the bucket.",
      "Within a bucket, `next` orders items by `priority` rank, then by descending extract `risk:` score, then by id.",
      "Priority rank runs `must-have` < `should-have` < `could-have` < `wont-have`. A requirement with no `priority` ranks last.",
      "`next` tags an item whose `risk:` is 2 or more with `[REVIEW]`.",
      "`next` names the requirement file to open, as `requirements/<ID>.md`.",
      "By default `next` shows at most the top few items of a bucket.",
      "`next` prints a `... N more` line when a bucket holds more items than it showed.",
      "With `--all`, `next` lists every item.",
      "The \"Untagged files\" bucket truncates the same way as the others.",
      "With a registry that holds no requirements, `next` prints a distinct \"no requirements yet\" message pointing at `init`/`new`. `next` never prints the all-clear line in that case.",
      "With requirements but no open signal, `next` prints the all-clear line.",
      "`next` is deterministic and writes no file.",
      "`next` always exits zero. The report is advice, not a gate." ],
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

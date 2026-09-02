#!/usr/bin/env python3
"""reqmap — requirement manager engine (stdlib only).

Subcommands:
  init              first-use bootstrap: scaffold requirements/ + .reqmapignore, draft
                    requirements from existing code, build the lock + map, print next steps
  new AREA-NAME-NNN   scaffold a requirement from the built-in template (--from-todo seeds from TODO.md)
  scan              list code members (implements/generated-from/... tags) per capability
  gate              the gate: link sync + drift + test-link integrity; exit non-zero on error (pre-commit/CI)
  sync              rescan + advance the drift baseline + regen the map and a committed _findings.md (--accept-drift for an edited contract)
  map               generate requirements/_map.md (Mermaid) + _map.json (graph) [+ _map.html viewer]
  site              inject/refresh engine-owned regions into a presentation page (--attach/--regions/--diagram)
  export            emit the registry graph as requirements/_map.json (for a front-end)
  next              terminal 'what should I do next': counted, actionable risk buckets
  lint [--strict]   readability/structure check on non-draft requirements (warn; --strict fails on errors)
  show <ID>         consolidated dossier for one requirement (contract, deps, members, risk)
  dupes [--threshold T]  flag requirement pairs with overlapping contracts (TF-IDF cosine)
  health [--json]   corpus coherence score + component counts (--json for a CI badge)
  draft             draft requirements from legacy code (status: draft, risk-scored)
  plan              read-only JSON capability-extraction plan (writes no .md)
  findings          aggregate open verify-intent items into requirements/_findings.md
  confirm <ID>      flip a reviewed requirement's status to confirmed (one frontmatter edit)
  review [ID]       emit a JSON review plan (intent/contract/acceptance/anchors) for AI-assisted quality review
  translate [--to ro|en]  manual, opt-in: cache a `claude -p` translation of the corpus's
                    majority-language requirements into requirements/_i18n/<locale>.json.
                    Never called by gate/sync/lint/map/the pre-commit hook.
  check             DEPRECATED alias for `gate` (report) / `sync` (with --update-lock); removed in v4.0.0

Layout on disk (relative to repo root, override with --root / --reqs / --code):
  requirements/*.md     the source of truth (markdown + YAML-ish frontmatter)
  <code>/**            scanned for tags like:  # implements: <ID>
"""
import argparse, ast, errno, fnmatch, hashlib, json, math, os, re, subprocess, sys

ROLES = ("implements", "generated-from", "validated-against", "tested-by")
# Both tag patterns are BUILT from ROLES rather than repeating it. The three used to be
# maintained by hand, which made ROLES look authoritative while driving nothing: adding a
# role there changed no behaviour, and the real vocabulary lived inside two regex literals.
_ROLE_ALT = "|".join(ROLES)
# the (?<![\w-]) left boundary stops substring matches like `reimplements:` or
# `x-implements:` from being picked up as a real `implements:` tag
_ID_PAT = r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+"
TAG_RE = re.compile(r"(?<![\w-])(" + _ROLE_ALT + r")\s*:\s*(" + _ID_PAT + r")")
# A single tag may bind several requirements via a comma-separated id list (one
# `<!-- generated-from: ... -->` listing several ids) — used for a whole-system doc
# generated from many requirements, so a contract drift on ANY of them lists the doc
# to re-sync. TAG_RE (single id) stays for callers that only need the tag's start
# position; TAG_LIST_RE captures the whole id list, which _findall_tags expands.
TAG_LIST_RE = re.compile(r"(?<![\w-])(" + _ROLE_ALT + r")\s*:\s*("
                         + _ID_PAT + r"(?:\s*,\s*" + _ID_PAT + r")*)")
_ID_RE = re.compile(_ID_PAT)


def _findall_tags(text):
    """Like ``TAG_RE.findall`` but expands a comma-separated id list into one
    ``(role, id)`` pair per id, so ``generated-from: A-1, B-2`` yields two members."""
    out = []
    for role, idlist in TAG_LIST_RE.findall(text):
        for cap in _ID_RE.findall(idlist):
            out.append((role, cap))
    return out


# Phantom-member exclusion helpers used in _scan_file_tags
_FENCE_RE = re.compile(r'^(`{3,}|~{3,})')   # CommonMark fence opener/closer
# NOTE: only handles single-backtick spans; double/triple-backtick spans (CommonMark-valid)
# are not filtered. No instances exist in this corpus, but this is a known gap.
_BACKTICK_RE = re.compile(r'`[^`]*`')         # inline backtick span (strip before tag search)
# Per-acceptance-criterion coverage tag, placed in a test: `# verifies: REQ-X#AC-1`.
# Finer-grained sibling of `tested-by` — links ONE test to ONE labelled criterion so
# "Verifiable" becomes machine-checked per criterion, not just per requirement. The
# `#AC-N` suffix is what distinguishes it from a plain requirement reference.
AC_VERIFY_RE = re.compile(r"(?<![\w-])verifies\s*:\s*(" + _ID_PAT + r")#((?:CASE|AC)-\d+)")
# Verification level on a `tested-by:` tag, written `# tested-by: <ID> @integration`.
# The id is spelled `<ID>` here on purpose: a real-looking id in a PLAIN COMMENT would be
# scanned as an actual tag. `_scan_file_tags` strips backticked spans only on the .md/.html
# path; on the code path its guard is `_strip_py_strings`, which masks string literals and
# leaves comments alone. Docstrings are safe; comments are not.
# The level applies to the whole tag, so a comma-separated id list shares it — the only
# unambiguous reading, and it matches how TAG_LIST_RE already groups ids. The suffix is
# invisible to TAG_RE/TAG_LIST_RE, so an older vendored engine reads a levelled tag,
# resolves the id, and ignores the level (ARCH-VLEVEL-037).
TEST_LEVELS = ("unit", "integration", "system")
TEST_LEVEL_RE = re.compile(
    r"(?<![\w-])tested-by\s*:\s*(" + _ID_PAT + r"(?:\s*,\s*" + _ID_PAT + r")*)"
    r"\s*@(" + "|".join(TEST_LEVELS) + r")\b")
CODE_EXTS = (".py", ".js", ".ts", ".tsx", ".jsx", ".c", ".cpp", ".h", ".hpp",
             ".cc", ".java", ".go", ".rs", ".html", ".css", ".sql", ".yaml", ".yml",
             ".sh", ".tf",
             ".prisma", ".graphql", ".proto",   # schema files: a consumer tagged schema.prisma and nothing read it
             ".scss", ".sass", ".less", ".vue", ".svelte", ".mjs", ".cjs", ".mts", ".cts",   # frontend run: excalidraw's ONLY stylesheet format was .scss
             ".cs", ".php", ".rb", ".kt", ".kts", ".swift", ".scala", ".ex", ".exs", ".dart", ".toml",   # infra/backend runs
             ".md")  # .md scanned for tags so prose capabilities (prompts/specs) can be members

# Extensionless filenames scanned by exact basename match (no case-fold — CODE_EXTS
# is suffix-based and case-sensitive too, so this stays consistent). Git hook names
# (pre-commit, pre-push, ...) are as conventional and unambiguous as Dockerfile/
# Makefile — a repo's own .githooks/ scripts are exactly the kind of scannable
# pipeline code v2.9's "tag your own pipeline" item covers; an unrelated file that
# happens to share one of these names is a harmless no-op scan (no tag = no member).
BASENAME_CODE_FILES = {"Dockerfile", "Makefile",
                       "Caddyfile", "Jenkinsfile", "Procfile", "Vagrantfile",
                       "pre-commit", "pre-push", "pre-receive", "post-receive",
                       "commit-msg", "prepare-commit-msg", "post-checkout", "post-merge"}

# A repo whose source language the default set doesn't cover can declare extra
# scannable extensions via the REQMAP_EXTRA_CODE_EXTS env var — comma-separated,
# leading dot optional (e.g. "REQMAP_EXTRA_CODE_EXTS=.foo,bar"). Merged here so
# every scan site (endswith(CODE_EXTS)) picks them up without forking the engine.
_extra_exts = tuple(
    (e if e.startswith(".") else "." + e)
    for e in (x.strip() for x in os.environ.get("REQMAP_EXTRA_CODE_EXTS", "").split(","))
    if e.strip()
)
if _extra_exts:
    CODE_EXTS = CODE_EXTS + _extra_exts


def _is_code_file(fn):  # implements: ARCH-SCAN-002
    """True if fn should be scanned as code: matches CODE_EXTS, an extensionless
    basename like Dockerfile/Makefile, or a Dockerfile variant (`Dockerfile.dev`,
    `Dockerfile.converter` — a consumer tagged one and nothing read it)."""
    return fn.endswith(CODE_EXTS) or fn in BASENAME_CODE_FILES or fn.startswith("Dockerfile.")

# ---- prose auto-draft classification (cmd_extract) ----
# These buckets govern AUTO behavior (drafting) ONLY. scan_members still honors an
# explicit tag on ANY file, regardless of bucket — buckets never suppress a real tag.
PROSE_EXTS = (".md", ".html")
# Bucket 1 — meta/boilerplate: never auto-drafted, never sync-checked. Basename match.
META_IGNORE_NAMES = {"CLAUDE.md", "AGENTS.md", "GEMINI.md", "CONTRIBUTING.md",
                     "SKILL.md", "TODO.md", "CHANGELOG.md"}

VALID_STATUS = {"draft", "baseline", "in-progress", "implemented", "confirmed", "deprecated"}
# 'need'      = an upstream stakeholder need, satisfied-by (not implemented-by)
# 'aggregate' = a requirement whose implementation IS its dependencies' — it adds no
#               behavior of its own, it asserts that N capabilities work together
#               (an MVP acceptance requirement is the archetype). Covered by its
#               depends_on edges, the mirror of how a need is covered by satisfies.
VALID_LAYER = {"bus", "feature", "need", "aggregate"}
# The V-model specification level, an axis ORTHOGONAL to `layer:` and deliberately not a
# rename of it. `layer:` says how a requirement sits in the dependency graph (a `bus` is
# defined by fan-in; a `need`/`aggregate` is covered by an edge instead of a tag, which is
# what IMPL_EXEMPT_LAYERS keys on). `level:` says how abstract it is. They are independent:
# an `architecture` requirement OWNS code, so it must stay gate-checked, whereas `aggregate`
# is exempt precisely because it owns none — which is why `architecture` cannot be an alias
# of `aggregate`. Optional and absent by default: a corpus that never adopts it behaves
# exactly as before.
VALID_LEVEL = {"system", "architecture", "code"}   # implements: ARCH-LEVEL-051
# The rungs of the V: the verification level that discharges each specification level.
# Left arm `level:` <-> right arm `tested-by: <ID> @<level>`. Read only when the author has
# declared BOTH sides — a requirement with no `level:`, or with no levelled test link, is
# never judged, so the rule is silent on arrival in every existing corpus.
LEVEL_TEST_PAIR = {"system": "system", "architecture": "integration", "code": "unit"}
# Hierarchy breadth on the `satisfies:` graph: a parent normally carries between these many
# children. Warn-only, and silent on a leaf — a requirement nothing satisfies is not a
# malformed parent, it is simply not a parent.
LINT_FANOUT_MIN = 5
LINT_FANOUT_MAX = 20
MILESTONE_RE = re.compile(r"^v\d+(\.\d+)*$")  # roadmap milestone shape: v1, v1.0, v1.14 — validated (warn) in the gate
ENFORCED = {"in-progress", "implemented", "confirmed"}
# System Map declutter: hide depends_on edges into a node this many capabilities
# depend on (a hub) — the bus is hidden regardless of count. Full graph stays in
# the Dependency Map tab.
SYSTEM_HUB_FANIN = 8

# Scripted, deterministic guidance per risk signal — surfaced in the Risk tab,
# the detail panel, and the _map.md risk table so a flagged requirement comes
# with a concrete next action, not just a color.
RISK_ADVICE = {
    "unimplemented": "Confirmed but no code linked: tag the implementing code "
                     "`# implements: <ID>`, or drop status back to in-progress/draft "
                     "until it is built. A confirmed requirement must point to code.",
    "unreviewed": "Draft/baseline, not yet validated: review the contract, wire its "
                  "`tested-by` tests, then promote to `confirmed`. Until then it is "
                  "tracked, not enforced.",
    "untested": "Implemented but no `tested-by` member: write an acceptance test and tag "
                "it `# tested-by: <ID>`, or set `test_exempt: <reason>` in the frontmatter "
                "to acknowledge it intentionally and silence this signal.",
    "unverified-intent": "Has open `## Verify intent` question(s): run "
                         "`reqmap.py findings`, resolve each in `requirements/_findings.md`, "
                         "then fold the answer into the Contract or delete the bullet.",
}

# Bumped on any change to this engine. `check` warns a seeded repo when its
# vendored copy is older than the installed plugin's. ISO date with an optional
# `.N` same-day revision suffix (YYYY-MM-DD[.N]): lexicographic order ==
# chronological order, so a plain string compare is enough.
MAP_ENGINE_VERSION = "2026-09-03.3"

# Declared support floor, deliberately equal to the OLDEST version CI actually runs
# (the `tests` matrix in .github/workflows/ci.yml). The code itself needs only 3.7
# (subprocess.run's capture_output/text, stream.reconfigure), but 3.7 and 3.8 are not
# installable on current GitHub runners, so promising them would be a claim nothing
# proves - the failure mode this project exists to prevent. Move this only together
# with the matrix that tests it.
MIN_PYTHON = (3, 9)


def _python_floor_error(version_info=None):  # implements: ARCH-PYFLOOR-040
    """Return a message when the interpreter is below MIN_PYTHON, else None.

    A pure predicate rather than an inline exit, so a test can pin the floor on any
    interpreter - a test process cannot spawn a 3.8 to watch the real thing happen.
    Note what this cannot catch: the module uses f-strings, so an interpreter below
    3.6 fails at COMPILE time and never reaches this check. 3.6-3.8 - the range a
    real user plausibly still has - get the readable message. ASCII only: a legacy
    Windows codepage is exactly where an old interpreter turns up.
    """
    major, minor = tuple(version_info or sys.version_info)[:2]
    if (major, minor) >= MIN_PYTHON:
        return None
    return ("reqmap needs Python %d.%d or newer (running %d.%d). The engine is stdlib-only, "
            "so a newer interpreter is the entire fix - no install, no dependencies: re-run "
            "with one, e.g. `python%d.%d scripts/reqmap.py ...`."
            % (MIN_PYTHON[0], MIN_PYTHON[1], major, minor, MIN_PYTHON[0], MIN_PYTHON[1]))

# ---------------------------------------------------------------------------
# COMMANDS registry — single source of truth for the CLI command set.
# Each entry describes one user-facing command: its summary, the positional
# argument it accepts (or None), and the flags it owns (subset of the shared
# argparse flag pool; global flags --root/--reqs/--code/--cache are omitted).
# Later tasks will derive argparse choices, tool_definition.json, and a
# markdown command table from this registry — do NOT add behaviour here.
# ---------------------------------------------------------------------------
# implements: ARCH-CMDREGISTRY-033
COMMANDS = {
    "init": {
        "summary": (
            "First-use bootstrap: scaffold requirements/ and .reqmapignore if missing, "
            "draft requirements from existing code/prose, build the lock and map, and "
            "print guided next steps. Idempotent — safe to re-run; never clobbers an "
            "existing .reqmapignore. Run once per repo to get started."
        ),
        "arg": None,
        "params": [
            {
                "name": "wipe",
                "flag": "--wipe",
                "type": "bool",
                "help": (
                    "Hard-reset: delete all non-generated requirements and strip "
                    "membership tags from source files before re-extracting."
                ),
            },
            {
                "name": "no_site",
                "flag": "--no-site",
                "type": "bool",
                "help": "Skip the final site step (scaffolding docs/architecture.html).",
            },
        ],
    },
    "new": {
        "summary": (
            "Scaffold a new blank requirement from the built-in template. "
            "Use --from-todo and --id together to pre-fill from a TODO.md item instead."
        ),
        "arg": "AREA-NAME-NNN",
        "params": [
            {
                "name": "id",
                "flag": "--id",
                "type": "str",
                "help": (
                    "Requirement ID in AREA-NAME-NNN format (e.g. AUTH-LOGIN-001). "
                    "Required when using --from-todo."
                ),
            },
            {
                "name": "from_todo",
                "flag": "--from-todo",
                "type": "str",
                "help": (
                    "Scaffold the requirement from a TODO.md item matched by this name "
                    "(use with --id; add --mark-done to flip the item to [x])."
                ),
            },
            {
                "name": "mark_done",
                "flag": "--mark-done",
                "type": "bool",
                "help": (
                    "Also flip the matched TODO.md item to [x] (off by default). "
                    "Only used with --from-todo."
                ),
            },
        ],
    },
    "scan": {
        "summary": (
            "List which code files belong to which requirement, grouped by capability. "
            "Shows all code members (implements:, generated-from:, validated-against:, "
            "tested-by:) discovered by scanning the repo."
        ),
        "arg": None,
        "params": [],
    },
    "gate": {
        "summary": (
            "Run the commit/CI gate (report-only): verify every code tag resolves to a "
            "real requirement, every confirmed requirement has at least one implements: "
            "member, and drift has not been introduced since the last sync. Exits "
            "non-zero on link-sync errors only (drift and test-link integrity are "
            "warnings). Never touches _reqlock.json. Run before every commit and in CI."
        ),
        "arg": None,
        "params": [
            {
                "name": "strict",
                "flag": "--strict",
                "type": "bool",
                "help": (
                    "Promote drift and test-link integrity warnings to errors. "
                    "Useful in CI when all requirements are confirmed."
                ),
            },
            {
                "name": "json",
                "flag": "--json",
                "type": "bool",
                "help": "Emit structured JSON output instead of human-readable text.",
            },
            {
                "name": "since",
                "flag": "--since",
                "type": "str",
                "help": (
                    "Scope the gate to requirements whose member files changed since "
                    "this git ref (e.g. 'main', 'HEAD~1')."
                ),
            },
        ],
    },
    "sync": {
        "summary": (
            "Rescan code members, advance the drift baseline, and regenerate the map in "
            "one step (a committed _findings.md is refreshed too). Run after editing "
            "requirement files or tagging new code members. "
            "Use --accept-drift when a confirmed or implemented contract changed."
        ),
        "arg": None,
        "params": [
            {
                "name": "accept_drift",
                "flag": "--accept-drift",
                "type": "bool",
                "help": (
                    "Explicitly advance the baseline when a confirmed or implemented "
                    "contract changed. Required when those contracts differ from the "
                    "lock; sync exits non-zero without it."
                ),
            },
            {
                "name": "strict",
                "flag": "--strict",
                "type": "bool",
                "help": "Promote drift and test-link integrity from warn to error.",
            },
        ],
    },
    "check": {
        "summary": (
            "Deprecated alias for 'gate' (report-only) / 'sync' (with --update-lock). "
            "Preserved for backward compatibility with consumer hooks, CI, and the "
            "GitHub Action. Will be removed in v4.0.0 — use 'gate' or "
            "'sync' instead."
        ),
        "arg": None,
        "params": [
            {
                "name": "strict",
                "flag": "--strict",
                "type": "bool",
                "help": "Promote drift and test-link integrity warnings to errors.",
            },
            {
                "name": "json",
                "flag": "--json",
                "type": "bool",
                "help": "Emit structured JSON output (for CI/badge consumption).",
            },
            {
                "name": "since",
                "flag": "--since",
                "type": "str",
                "help": "Scope the gate to requirements whose member files changed since this git ref.",
            },
            {
                "name": "update_lock",
                "flag": "--update-lock",
                "type": "bool",
                "help": "Also regenerate the lock and map (mirrors legacy 'sync' behavior).",
            },
        ],
    },
    "map": {
        "summary": (
            "Generate requirements/_map.md (4 Mermaid diagrams), requirements/_map.json "
            "(graph with nodes, edges, todos), and requirements/_map.html (a "
            "self-contained React viewer). The viewer is only emitted when "
            "scripts/_map_viewer.html is vendored beside the engine."
        ),
        "arg": None,
        "params": [
            {
                "name": "check_fresh",
                "flag": "--check",
                "type": "bool",
                "help": (
                    "Freshness gate: rebuild the map in memory and exit non-zero if the "
                    "committed _map.* is stale. Use in CI alongside gate."
                ),
            },
        ],
    },
    "export": {
        "summary": (
            "Write requirements/_map.json (the graph with engine_version, nodes, edges) "
            "for feeding an external front-end. Same output as map, without rebuilding "
            "_map.md and _map.html."
        ),
        "arg": None,
        "params": [
            {
                "name": "out",
                "flag": "--out",
                "type": "str",
                "help": "Output path override. Use '-' for stdout (--out -); omit for requirements/_map.json.",
            },
        ],
    },
    "next": {
        "summary": (
            "Show what to do next: a prioritized, actionable list of risk buckets "
            "(Orphans, Needs tests, Needs intent review, Drafts to review). "
            "Read-only, always exits 0. The best follow-up command to run after any action."
        ),
        "arg": None,
        "params": [
            {
                "name": "show_all",
                "flag": "--all",
                "type": "bool",
                "help": "Expand all buckets to show every item instead of just the top few.",
            },
        ],
    },
    "lint": {
        "summary": (
            "Readability and structure check on non-draft requirements: stacked conditions (3+ and/or joins in one normative line), "
            "contract clauses with an unnamed 'It' subject, over-long contract clauses, "
            "missing Contract or Acceptance sections. Read-only unless --decompose is "
            "passed; exit-neutral by default."
        ),
        "arg": None,
        "params": [
            {
                "name": "strict",
                "flag": "--strict",
                "type": "bool",
                "help": "Exit non-zero on error-severity findings (warnings remain advisory).",
            },
            {
                "name": "decompose",
                "flag": "--decompose",
                "type": "bool",
                "help": ("Scaffold one draft requirement per statement-size finding. Opt-in and "
                         "never used by the gate, the hook or CI \u2014 the only lint mode that writes."),
            },
        ],
    },
    "show": {
        "summary": (
            "Print a consolidated dossier for one requirement: header, intent, Contract "
            "bullets, dependencies in both directions, code members grouped by role with "
            "file:line, open Verify intent questions, and risk signals. Answers 'what "
            "does this do / where is X' in one command. Read-only."
        ),
        "arg": "ID",
        "params": [],
    },
    "dupes": {
        "summary": (
            "Flag requirement pairs whose contracts overlap (TF-IDF cosine similarity), "
            "so a divergent re-implementation is caught before it lands. Read-only, "
            "advisory — a human decides if a flagged pair is a real duplicate."
        ),
        "arg": None,
        "params": [
            {
                "name": "threshold",
                "flag": "--threshold",
                "type": "float",
                "help": "Cosine similarity cutoff in (0,1] for reporting a pair (default 0.35). Lower = more pairs flagged.",
            },
        ],
    },
    "search": {
        "summary": (
            "Rank requirements by lexical relevance to a free-text query (same TF-IDF "
            "cosine as dupes, reused). Read-only. Prints each hit's score, and says so "
            "explicitly when nothing clears the relevance floor rather than showing a "
            "spurious top result. Lexical, not synonym-aware."
        ),
        "arg": "QUERY",
        "params": [
            {
                "name": "top",
                "flag": "--top",
                "type": "int",
                "help": "Maximum number of ranked matches to show (default 5).",
            },
        ],
    },
    "health": {
        "summary": (
            "Print a corpus coherence snapshot: a headline score (percentage of "
            "requirements fully green on every axis: confirmed + member + tested + no "
            "open questions + not drifted) plus component counts. Use for a CI badge "
            "with --json."
        ),
        "arg": None,
        "params": [
            {
                "name": "json",
                "flag": "--json",
                "type": "bool",
                "help": "Emit parseable JSON for a CI badge (--json).",
            },
            {
                "name": "badge",
                "flag": "--badge",
                "type": "bool",
                "help": "Emit Shields.io endpoint JSON (schemaVersion, label, message, color).",
            },
        ],
    },
    "draft": {
        "summary": (
            "Draft one requirement per untagged file (code and prose). Input is existing "
            "untagged source code and Markdown. Emits draft requirements — never "
            "confirmed. After drafting, run gate and report the result. Remind the user "
            "to review and confirm the real ones."
        ),
        "arg": None,
        "params": [],
    },
    "plan": {
        "summary": (
            "Read-only JSON capability-extraction plan: emit a capability map from "
            "legacy code without writing any .md files. Safer than draft — a human "
            "authors and confirms each candidate. Use before draft to preview what would "
            "be extracted."
        ),
        "arg": None,
        "params": [
            {
                "name": "out",
                "flag": "--out",
                "type": "str",
                "help": "Write plan JSON here ('-' or omit = stdout).",
            },
            {
                "name": "md_glob",
                "flag": "--md-glob",
                "type": "str",
                "help": (
                    "Also discover .md files matching this glob (repeatable; "
                    "comma-separated ok). Off unless given. "
                    "e.g. --md-glob 'prompts/**' --md-glob 'modes/**'."
                ),
            },
        ],
    },
    "findings": {
        "summary": (
            "Aggregate open 'Verify intent' items across all requirements into "
            "requirements/_findings.md. Surfaces every open human-review question in "
            "one place."
        ),
        "arg": None,
        "params": [
            {
                "name": "raw",
                "flag": "--raw",
                "type": "bool",
                "help": "Ignore the triage sidecar and emit the raw grouped list.",
            },
        ],
    },
    "confirm": {
        "summary": (
            "Mark a reviewed requirement as confirmed — the human sign-off step. Flips "
            "status to confirmed in the frontmatter. The engine refuses if the "
            "requirement has no implements: member (a confirmed requirement must point "
            "to code). Run sync after confirming."
        ),
        "arg": "ID",
        "params": [],
    },
    "review": {
        "summary": (
            "Emit a JSON review plan (intent, contract, acceptance criteria, structural "
            "anchors) for all requirements or one. Used as an AI feed for semantic "
            "quality review. Read-only."
        ),
        "arg": "ID",
        "params": [],
    },
    "translate": {
        "summary": (
            "Manual, opt-in: detect the corpus's majority language (per-file `lang:` "
            "frontmatter override honored first), then cache a `claude -p` translation "
            "of every requirement written in that language into "
            "requirements/_i18n/<target>.json. A structural-fidelity check (backticked "
            "spans, numbers, heading/bullet markers) gates every cache write; a missing "
            "`claude` CLI, a timeout, or a failed check skips that entry with a warning "
            "instead of aborting. `map`/`export` inline the cache into the graph "
            "read-only, with no `claude` call of their own — this command is the ONLY "
            "way a `claude` subprocess runs; it is never invoked by gate/sync/lint/map "
            "or the pre-commit hook."
        ),
        "arg": None,
        "params": [
            {
                "name": "translate_to",
                "flag": "--to",
                "type": "str",
                "help": "Target locale, 'ro' or 'en' (default: the other of the two from "
                        "the detected corpus majority).",
            },
        ],
    },
    "site": {
        "summary": (
            "Inject or refresh engine-owned regions (nav links + stats counts) into a "
            "project presentation page. Scaffolds a full page if the target does not "
            "exist. Run after map to keep the page current."
        ),
        "arg": None,
        "params": [
            {
                "name": "attach",
                "flag": "--attach",
                "type": "str",
                "help": "Target HTML page to inject engine-owned regions into (scaffolds it if absent).",
            },
            {
                "name": "regions",
                "flag": "--regions",
                "type": "str",
                "help": "Comma-separated list of regions to inject (nav,stats). Default: nav.",
            },
            {
                "name": "diagram",
                "flag": "--diagram",
                "type": "str",
                "help": "Relative path (from the page) to an Excalidraw HTML viewer; linked only if it exists.",
            },
            {
                "name": "detect",
                "flag": "--detect",
                "type": "bool",
                "help": "Scan docs/ and print the suggested command — writes nothing.",
            },
        ],
    },
    "coverage": {
        "summary": (
            "Read-only report of untagged-code coverage signal: lists source files that "
            "carry no implements: tag, grouped by directory. Use to identify gaps in "
            "requirement traceability."
        ),
        "arg": None,
        "params": [
            {
                "name": "json",
                "flag": "--json",
                "type": "bool",
                "help": "Emit structured JSON output (for CI consumption).",
            },
        ],
    },
    "suggest-verifies": {
        "summary": (
            "Propose `# verifies: <id>#CASE-N` tags for tests already named after the "
            "criterion they check (e.g. `test_ac3_...`), so per-criterion coverage can "
            "be adopted on an existing corpus. Read-only; --apply writes the tags."
        ),
        "arg": None,
        "params": [
            {
                "name": "apply",
                "flag": "--apply",
                "type": "bool",
                "help": "Write the proposed tags into the test files (ambiguous matches are never written).",
            },
        ],
    },
    "gen-integration": {
        "summary": (
            "Regenerate the multi-AI integration artifacts (tool_definition.json) from "
            "the command registry."
        ),
        "arg": None,
        "params": [],
        "internal": True,
    },
}


def _cli_choices():
    """The CLI command names, derived from the registry (single source of truth)."""
    return list(COMMANDS)


def _generate_schema():  # implements: ARCH-CMDREGISTRY-033
    """Function-calling schema (OpenAI tool format) generated from COMMANDS.
    Returns a JSON string (indent=2, trailing newline) — byte-stable for the gate
    drift-compare. Internal commands are excluded from the AI-facing schema."""
    _TYPE = {"bool": "boolean", "str": "string", "float": "number", "int": "integer"}
    tools = []
    for name, spec in COMMANDS.items():
        if spec.get("internal"):
            continue
        props = {"root": {"type": "string",
                          "description": "Repo root where requirements/ lives; defaults to the current directory."}}
        if spec.get("arg"):
            props["arg"] = {"type": "string", "description": spec["arg"]}
        for p in spec["params"]:
            props[p["name"]] = {"type": _TYPE[p["type"]], "description": p["help"]}
        tools.append({"type": "function", "function": {
            "name": "reqmap_" + name.replace("-", "_"),
            "description": spec["summary"],
            "parameters": {"type": "object", "properties": props, "required": []},
        }})
    return json.dumps(tools, indent=2, ensure_ascii=False) + "\n"


def _generate_command_table():
    """A markdown table of the user CLI commands from COMMANDS, for the generated
    region inside SKILL.universal.md. Internal commands are excluded."""
    rows = ["| Command | What it does | Flags |", "|---|---|---|"]
    for name, spec in COMMANDS.items():
        if spec.get("internal"):
            continue
        flags = ", ".join("`" + p["flag"] + "`" for p in spec["params"]) or "—"
        rows.append("| `{}` | {} | {} |".format(name, spec["summary"], flags))
    return "\n".join(rows)


_REGION_RE = re.compile(r"(<!--##REQMAP:COMMANDS##-->)(.*?)(<!--##/REQMAP:COMMANDS##-->)", re.DOTALL)


def _write_region(path, body):
    """Replace the delimited region body in `path`; prose outside is untouched."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    new = _REGION_RE.sub(lambda m: m.group(1) + "\n" + body + "\n" + m.group(3), text)
    if new != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)


def cmd_gen_integration(reqs_dir, code_root):
    """Write tool_definition.json (OpenAI function-calling schema) generated from COMMANDS."""
    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(plugin_root, "tool_definition.json"), "w", encoding="utf-8") as f:
        f.write(_generate_schema())
    print("wrote tool_definition.json")
    skill = os.path.join(plugin_root, "skills", "requirement-manager", "SKILL.universal.md")
    if os.path.exists(skill):
        _write_region(skill, _generate_command_table())
        print("wrote SKILL.universal.md command table")
    return 0


def _check_integration_fresh(plugin_root):
    """Return a list of stale generated artifacts (empty = fresh). Compares the
    committed tool_definition.json + the SKILL.universal.md command-table region
    against a fresh generation from the registry. Mirrors map --check. Artifacts
    that don't exist (e.g. a consumer repo that doesn't ship them) are skipped, so
    this never breaks a vendored-engine gate."""
    stale = []
    tj = os.path.join(plugin_root, "tool_definition.json")
    if os.path.exists(tj):
        with open(tj, encoding="utf-8") as _f:
            if _f.read() != _generate_schema():
                stale.append("tool_definition.json")
    skill = os.path.join(plugin_root, "skills", "requirement-manager", "SKILL.universal.md")
    if os.path.exists(skill):
        with open(skill, encoding="utf-8") as _f:
            m = _REGION_RE.search(_f.read())
        if m and m.group(2).strip() != _generate_command_table().strip():
            stale.append("skills/requirement-manager/SKILL.universal.md")
    return stale


# ---------- parsing ----------
def _as_list(v):  # implements: ARCH-PARSE-001
    """Coerce a frontmatter value to a list: lists pass through, a bare scalar
    becomes a one-element list, empty/None becomes []. Guards callers that
    iterate list-valued keys (e.g. depends_on) against a string written without
    brackets being walked character-by-character."""
    if isinstance(v, list):
        return v
    return [v] if v else []


def _scalar_value(v):  # implements: ARCH-PARSE-001
    """One frontmatter scalar value. If it opens with a matching quote, take the
    quoted span verbatim — a '#' inside is DATA, and any text after the closing
    quote (e.g. an inline comment) is dropped. Otherwise drop a ' #' / leading '#'
    comment, preserving an embedded '#' with no leading space (issue#123)."""
    v = v.strip()
    if len(v) >= 2 and v[0] in "\"'":
        end = v.find(v[0], 1)
        if end != -1:
            return v[1:end]                       # quoted: inner '#' is data
    return re.split(r'(?:^|\s)#', v, 1)[0].strip()


def _clean_item(s):  # implements: ARCH-PARSE-001
    """One list element: unquote a quoted item verbatim, else drop a trailing
    `# comment` and trim. A '#' is a comment only at the token start or after
    whitespace, so an embedded '#' (e.g. issue#123) is preserved — matching the
    scalar parse path."""
    return _scalar_value(s)


def parse_frontmatter(text):  # implements: ARCH-PARSE-001
    """Return (meta_dict, body). Minimal YAML: scalars, inline [a, b] lists, and the
    block form (`key:` then indented `- item` lines). An inline list missing its
    closing `]` is parsed leniently rather than silently kept as a literal string."""
    meta, body = {}, text.lstrip("﻿")  # tolerate a stray UTF-8 BOM
    if body.startswith("---"):
        end = body.find("\n---", 3)
        if end != -1:
            block = body[3:end]
            body = body[end + 4:].lstrip("\r\n")   # tolerate a CRLF close (\r\n--- )
            lines = block.splitlines()
            i = 0
            while i < len(lines):
                line = lines[i]; i += 1
                s = line.strip()
                if not s or s.startswith("#") or ":" not in line:
                    continue
                k, v = line.split(":", 1)
                k, v = k.strip(), v.strip()
                if v.startswith("["):
                    # inline list; tolerate a missing `]` (lenient) — a '#' inside
                    # the brackets is data, a '#' after the close is a comment
                    inner = v[1:v.index("]")] if "]" in v else v[1:]
                    meta[k] = [x for x in (_clean_item(x) for x in inner.split(",")) if x]
                elif not v:
                    # block-style list: consume following indented `- item` lines.
                    # No items -> keep the empty scalar (e.g. an unset superseded_by).
                    items = []
                    while i < len(lines) and lines[i].lstrip().startswith("- "):
                        items.append(_clean_item(lines[i].lstrip()[2:]))
                        i += 1
                    meta[k] = [x for x in items if x] if items else ""
                else:
                    # A quoted value keeps an inner '#' verbatim; a bare value treats
                    # '#' as a comment only at the start or after whitespace (so
                    # "issue#123" is preserved). See _scalar_value.
                    meta[k] = _scalar_value(v)
    return meta, body


# A requirement file may hold SEVERAL requirements, one per frontmatter block — a module
# in the DOORS sense: the architecture requirement, then the code requirements beneath it.
# A block begins at a `---` line immediately followed by `id:`. That lookahead is what makes
# the split unambiguous: a bare `---` is a markdown horizontal rule and a frontmatter close,
# both of which appear inside a body, and neither is followed by an id line.
_REQ_BLOCK_RE = re.compile(r"(?m)^---[ \t]*\r?\n(?=id:)")   # implements: ARCH-MODULEFILE-056


def split_requirement_blocks(text):  # implements: ARCH-MODULEFILE-056
    """Split one file's text into its requirement blocks, each ready for
    `parse_frontmatter`. A single-requirement file yields exactly one block, byte-identical
    to the whole text, so nothing about the existing corpus changes."""
    text = text.lstrip("\ufeff")
    parts = _REQ_BLOCK_RE.split(text)
    if len(parts) <= 1:
        return [text]
    out = []
    if parts[0].strip():                 # anything before the first block is a file preamble
        out.append(parts[0])
    for chunk in parts[1:]:
        out.append("---\n" + chunk)
    return out or [text]


def load_requirements(reqs_dir):  # implements: ARCH-PARSE-001  # implements: ARCH-MODULEFILE-056
    reqs = {}
    if not os.path.isdir(reqs_dir):
        return reqs
    for name in sorted(os.listdir(reqs_dir)):
        if not name.endswith(".md") or name.startswith("_"):
            continue
        path = os.path.join(reqs_dir, name)
        with open(path, encoding="utf-8-sig") as f:  # tolerate a UTF-8 BOM
            text = f.read()
        for _i, _blk in enumerate(split_requirement_blocks(text)):
            meta, body = parse_frontmatter(_blk)
            # only the FIRST block may fall back to the filename; a later block without an
            # explicit id is a malformed block, not a second requirement named after the file.
            rid = meta.get("id") or (os.path.splitext(name)[0] if _i == 0 else None)
            if not rid:
                continue
            if rid in reqs:
                # two blocks claim the same id: keep the first (sorted) and warn, rather
                # than let the later one silently shadow it (the gate can't catch this —
                # the id still resolves, just to the wrong block).
                print("WARNING: duplicate requirement id {!r} in {!r} — keeping {!r}".format(
                    rid, name, os.path.basename(reqs[rid]["path"])), file=sys.stderr)
                continue
            reqs[rid] = {"meta": meta, "body": body, "path": path, "block": _i}
    return reqs


_REQS_REAL_CACHE = {}   # reqs_dir -> realpath, resolved once per process


def _prune_dirs(dirpath, dirs, reqs_dir, code_root=None, ignore=()):  # implements: ARCH-SCAN-002
    """Drop noise dirs and the SSOT output dir from an os.walk in place.

    Excludes ONLY the actual requirements dir (by realpath), not every folder
    that happens to be named 'requirements' — a source package named
    requirements/ must still be scanned. The realpath comparison runs only for a
    directory whose NAME matches the SSOT dir's: resolving every directory on the
    walk was 62% of one consumer's gate time (4,900 upload folders, 35k realpath
    calls for a 216-file scan).

    With `code_root` and `ignore`, a directory that a `.reqmapignore` pattern ending
    in `/**` or `/*` already covers is not descended at all. Every file under it
    matched the pattern anyway, so the result is identical — only the stat calls go."""
    reqs_name = os.path.normcase(os.path.basename(os.path.normpath(reqs_dir))) if reqs_dir else None
    dir_pats = [p for p in ignore if p.endswith(("/**", "/*"))]
    keep = []
    for d in dirs:
        if d in (".git", "node_modules", "__pycache__"):
            continue
        if reqs_name and os.path.normcase(d) == reqs_name:
            real = _REQS_REAL_CACHE.get(reqs_dir)
            if real is None:
                real = _REQS_REAL_CACHE[reqs_dir] = os.path.realpath(reqs_dir)
            if os.path.realpath(os.path.join(dirpath, d)) == real:
                continue
        if dir_pats and code_root is not None:
            rel = os.path.relpath(os.path.join(dirpath, d), code_root).replace(os.sep, "/") + "/"
            if any(fnmatch.fnmatch(rel, p) for p in dir_pats):
                continue
        keep.append(d)
    dirs[:] = keep


def load_ignore(code_root, reqs_dir=None):  # implements: ARCH-SCAN-002
    """Read optional `.reqmapignore` (fnmatch globs over POSIX rel paths, one per
    line, blanks and # comments skipped). Looked up in `requirements/` first (the
    consolidated home for reqmap files) then at the scan root; first found wins.
    Patterns are still matched against repo-root-relative paths regardless of where
    the file lives. Fail-open: a missing/unreadable file yields no patterns."""
    pats = []
    for base in ([reqs_dir] if reqs_dir else []) + [code_root]:
        try:
            with open(os.path.join(base, ".reqmapignore"), encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if s and not s.startswith("#"):
                        pats.append(s)
            break   # first .reqmapignore found wins
        except OSError:
            continue
    return pats


def _strip_py_strings(s):
    """Mask Python string literal contents with spaces; detect an unclosed triple-quote.

    Handles single-line '' / "" strings and triple-quoted forms (both ''' and \""").
    Triple-quote detection takes precedence over single-quote detection.
    A '#' after all string content is consumed is preserved as-is (it starts a comment).

    Returns (masked_line, in_triple_or_None):
      masked_line        — line with all string *content* replaced by spaces
      in_triple_or_None  — the triple-quote delimiter ('\"\"\"' or \"'''\") if one opened
                           and did not close on this line, else None.
    """
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if i + 2 < n and s[i:i+3] in ('"""', "'''"):
            q = s[i:i+3]
            out.append('   ')    # mask the opening delimiter
            i += 3
            j = s.find(q, i)
            if j == -1:
                out.append(' ' * (n - i))
                return ''.join(out), q
            out.append(' ' * (j - i + 3))
            i = j + 3
        elif c in ('"', "'"):
            out.append(' ')
            i += 1
            while i < n and s[i] != c and s[i] != '\n':
                if s[i] == '\\' and i + 1 < n:
                    out.append('  ')
                    i += 2
                else:
                    out.append(' ')
                    i += 1
            if i < n and s[i] == c:
                out.append(' ')
                i += 1
        elif c == '#':
            out.append(s[i:])
            break
        else:
            out.append(c)
            i += 1
    return ''.join(out), None


def _scan_file_tags(fp, lines=None):  # implements: ARCH-SCAN-002
    """Membership tags in one file as [[role, cap, line], ...], or None on read error.

    `lines` lets a caller that has already read the file hand the content over, so the
    single-walk scanner (`scan_all`) reads each file once for all three extractors
    instead of three times. `fp` is still required: the masking rules key off its
    extension. Reading it here when `lines` is None keeps every existing caller working.

    Context-aware per file class — admits a tag only when NOT in an excluded zone:

    PROSE (.md, .html):  excluded if in a fenced code block (``` / ~~~, CommonMark
      length-matched), a backtick span, or a >=4-space / tab indent block.
      <!-- implements: X --> in prose (outside any exclusion zone) remains valid.

    PY:  excluded if in a triple-quoted string (state carried across lines) or a
      single-line string literal. Comment tags (code()  # implements: X) are kept.

    Other extensions: no filtering — all positions valid (original behavior).

    State is local — resets per file call (no cross-file leak).
    """
    ext = os.path.splitext(fp)[1].lower()
    out = []
    if lines is None:
        try:
            with open(fp, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except OSError:
            return None

    if ext in PROSE_EXTS:
        fence = None   # None = not fenced; else the opening fence string e.g. "```"
        for i, raw in enumerate(lines, 1):
            s = raw.rstrip("\n\r")
            # Markdown indented code block (>=4 spaces / tab): treat as code so an
            # indented ```-prefixed line never opens a phantom fence that would
            # swallow every later tag, and an indented tag is excluded. Checked
            # BEFORE fence detection. HTML has no indented-code concept, so the
            # guard is Markdown-only — an indented tag comment in HTML stays valid.
            if ext == ".md" and (s.startswith("    ") or s.startswith("\t")):
                continue
            stripped = s.lstrip()
            fm = _FENCE_RE.match(stripped)
            if fm:
                marker = fm.group(1)
                rest = stripped[len(marker):].strip()
                if fence is None:
                    fence = marker
                    continue
                elif marker[0] == fence[0] and len(marker) >= len(fence) and not rest:
                    fence = None    # closer must be bare (no info string)
                    continue
            if fence is not None:
                continue
            clean = _BACKTICK_RE.sub("", s)
            seen = set()
            for role, cap in _findall_tags(clean):
                key = (role, cap)
                if key not in seen:
                    seen.add(key)
                    out.append([role, cap, i])

    elif ext == ".py":
        in_triple = None   # None or the opening triple-quote delimiter
        for i, raw in enumerate(lines, 1):
            s = raw.rstrip("\n\r")
            if in_triple is not None:
                idx = s.find(in_triple)
                if idx == -1:
                    continue
                s = s[idx + len(in_triple):]
                in_triple = None
            s, in_triple = _strip_py_strings(s)
            seen = set()
            for role, cap in _findall_tags(s):
                key = (role, cap)
                if key not in seen:
                    seen.add(key)
                    out.append([role, cap, i])

    else:
        for i, raw in enumerate(lines, 1):
            seen = set()
            for role, cap in _findall_tags(raw):
                key = (role, cap)
                if key not in seen:
                    seen.add(key)
                    out.append([role, cap, i])

    return out


def _scancache_path(reqs_dir):  # implements: ARCH-SCANCACHE-023
    return os.path.join(reqs_dir, "_scancache.json")


def _load_scancache(reqs_dir):  # implements: ARCH-SCANCACHE-023
    """Read the opt-in scan-cache sidecar; {} when absent/corrupt (fails open)."""
    try:
        with open(_scancache_path(reqs_dir), encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_scancache(reqs_dir, cache):  # implements: ARCH-SCANCACHE-023
    """Write the scan cache, best-effort — an unwritable cache must never fail the scan."""
    try:
        with open(_scancache_path(reqs_dir), "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, sort_keys=True)
    except OSError:
        pass


def _walk_code(code_root, reqs_dir=None):  # implements: ARCH-SCAN-002
    """Yield (abs_path, posix_rel_path) for every scannable file under `code_root`.

    The one place the walk discipline lives: prune noise dirs and the SSOT output dir,
    descend and read in sorted order so a generated map is identical across platforms,
    keep only known code files, and honour `.reqmapignore`. Three scanners used to carry
    a byte-for-byte copy of this loop, which is how they drifted apart in the first place.
    """
    ignore = load_ignore(code_root, reqs_dir)
    for dirpath, dirs, files in os.walk(code_root):
        _prune_dirs(dirpath, dirs, reqs_dir, code_root, ignore)
        dirs.sort()                  # deterministic descent — raw os.walk order is OS-dependent
        for fn in sorted(files):     # deterministic file order — the map must not depend on the filesystem
            if not _is_code_file(fn):
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, code_root).replace(os.sep, "/")
            if any(fnmatch.fnmatch(rel, pat) for pat in ignore):
                continue
            yield fp, rel


def _extract_coverage(fp, rel, lines, ac_out, level_out):  # implements: ARCH-ACVERIFY-019
    """Accumulate `verifies:` and levelled `tested-by:` hits from one file's lines.

    One masking pass feeding both regexes, because the two scanners this replaces did
    the identical per-line work twice. The asymmetry is preserved exactly: only the
    levelled scan strips backticked spans first, so a documented EXAMPLE of a levelled
    tag does not register as real coverage, while `verifies:` keeps its raw scan.
    """
    is_py = fp.endswith(".py")
    in_triple = None
    for i, line in enumerate(lines, 1):
        s = line
        if is_py:
            s = s.rstrip("\n\r")
            if in_triple is not None:
                idx = s.find(in_triple)
                if idx == -1:
                    continue
                s = s[idx + len(in_triple):]
                in_triple = None
            s, in_triple = _strip_py_strings(s)
        for cap, ac in AC_VERIFY_RE.findall(s):
            ac_out.setdefault(cap, {}).setdefault(ac, []).append((rel, i))
        for idlist, level in TEST_LEVEL_RE.findall(_BACKTICK_RE.sub("", s)):
            for cap in _ID_RE.findall(idlist):
                level_out.setdefault(cap, {}).setdefault(level, []).append((rel, i))


def scan_all(code_root, reqs_dir=None):  # implements: ARCH-SCAN-002
    """(members, ac_cover, level_cover) from ONE walk that reads each file once.

    The gate used to call three scanners that each walked the whole tree and opened
    every file: on a 10,000-file tree that measured 3.06s + 2.76s + 2.81s of its 8.49s
    total — the scan was essentially the entire runtime, done three times. Results are
    identical to calling `scan_members` / `scan_ac_verifies` / `scan_test_levels`
    separately; a test asserts that equality rather than trusting the refactor.

    `scan_members`'s opt-in mtime cache is deliberately not reproduced here: it is off
    on the gate/CI path this exists to speed up, and duplicating its invalidation rules
    would trade a measured win for a correctness risk.
    """
    members, ac_cover, level_cover = {}, {}, {}
    for fp, rel in _walk_code(code_root, reqs_dir):
        try:
            with open(fp, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except OSError:
            continue          # unreadable file is skipped, never fatal — matches scan_members
        for role, cap, line in _scan_file_tags(fp, lines) or []:
            members.setdefault(cap, []).append((role, rel, line))
        _extract_coverage(fp, rel, lines, ac_cover, level_cover)
    return members, ac_cover, level_cover



def scan_members(code_root, reqs_dir=None, cache=False):  # implements: ARCH-SCAN-002
    """Walk the code root for `implements:`/`tested-by:` tags → {cap_id: [(role, file, line)]}.

    Opt-in (cache=True with reqs_dir set): a sidecar keyed by (mtime_ns, size) lets an
    unchanged file skip the read+parse. The cache is a PURE performance optimization —
    results are byte-identical to cache=False — and is OFF by default, so the gate/CI
    path is unaffected. A changed/new file is re-parsed and refreshed; a vanished file is
    pruned (it is absent from the rewritten cache)."""
    members = {}  # cap_id -> list[(role, file, line)]
    ignore = load_ignore(code_root, reqs_dir)
    use_cache = bool(cache and reqs_dir)
    old = _load_scancache(reqs_dir) if use_cache else {}
    new = {}
    for dirpath, dirs, files in os.walk(code_root):
        _prune_dirs(dirpath, dirs, reqs_dir)
        dirs.sort()                  # deterministic descent — raw os.walk order is filesystem/OS-dependent
        for fn in sorted(files):     # deterministic file order so the generated map is identical across platforms
            if not _is_code_file(fn):
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, code_root).replace(os.sep, "/")
            if any(fnmatch.fnmatch(rel, pat) for pat in ignore):
                continue
            if use_cache:
                try:
                    st = os.stat(fp)
                except OSError:
                    continue
                ent = old.get(rel)
                if ent and ent.get("mtime_ns") == st.st_mtime_ns and ent.get("size") == st.st_size:
                    tags = ent.get("tags") or []
                else:
                    tags = _scan_file_tags(fp)
                    if tags is None:
                        continue
                new[rel] = {"mtime_ns": st.st_mtime_ns, "size": st.st_size, "tags": tags}
            else:
                tags = _scan_file_tags(fp)
                if tags is None:
                    continue
            for role, cap, line in tags:
                members.setdefault(cap, []).append((role, rel, line))
    if use_cache:
        _save_scancache(reqs_dir, new)   # `new` omits vanished files → prune
    return members


_VDS_STRING_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')
_VDS_ID_CONTRACT_START_RE = re.compile(r'id:"([A-Z][A-Z0-9-]+)"[^{}]*?contract:\[')
# An entry the fixture INVENTS: the viewer's demo dataset carries a fake orphan and a
# fake deprecated capability so the Risk and Problems tabs have something to show with
# no engine present. Those ids cannot exist in any registry, so comparing them against
# one reported permanent drift - the check crying wolf about data that is doing its job.
# Marked entries are skipped; an UNMARKED id missing from the registry still reports,
# because that is the real signal (a requirement renamed out from under the fixture).
_VDS_DEMO_ONLY_RE = re.compile(r'demoOnly\s*:\s*true')


def _vds_normalize(strings):
    return sorted(" ".join(s.split()) for s in strings)


def _vds_scan_array_body(text, start):
    """From text[start] (the char right after the '[' that opens a JS array),
    return the array's raw source text up to its matching ']' — tracking
    quoted-string state so a stray ']'/'[' INSIDE a contract bullet's own text
    (e.g. a bullet describing `[a, b]` syntax) doesn't end the scan early.
    Returns None if the array never closes before EOF."""
    depth, in_string, i = 1, False, start
    while i < len(text):
        c = text[i]
        if in_string:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_string = False
        elif c == '"':
            in_string = True
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return text[start:i]
        i += 1
    return None


def _vds_parse_baked(text):
    """{id: [contract strings]} from data.js's BAKED array, minus `demoOnly:true` entries."""
    out = {}
    for m in _VDS_ID_CONTRACT_START_RE.finditer(text):
        if _VDS_DEMO_ONLY_RE.search(m.group(0)):
            continue                      # invented demo state — no registry counterpart
        block = _vds_scan_array_body(text, m.end())
        if block is None:
            continue
        out[m.group(1)] = [s.replace('\\"', '"') for s in _VDS_STRING_RE.findall(block)]
    return out


def check_viewer_data_sync(data_js_path, map_nodes):  # implements: ARCH-VIEWER-007
    """Compare app/src/lib/data.js's hand-authored BAKED requirement fixture
    against the live registry (map_nodes: [{"id":..., "contract":[...]}, ...]).
    Returns a sorted list of requirement IDs where the two disagree — a baked id
    missing from the live registry, or a whitespace-normalized mismatch in its
    `contract` bullets. A warn-only heuristic (not a byte-exact diff): it locates
    each BAKED entry's `contract:[...]` array via bracket-depth + quoted-string
    tracking (a naive non-greedy regex stops at the FIRST ']', which truncates
    any bullet whose own text contains a bracket — this repo's actual contracts
    do, e.g. describing `[a, b]` syntax, so that naive form is not just imprecise
    but wrong on real data). Returns None (not []) when data_js_path doesn't
    exist OR can't be decoded as UTF-8 — fail-open, matching load_ignore()'s
    convention for an optional file."""
    try:
        with open(data_js_path, encoding="utf-8") as f:
            text = f.read()
    except (OSError, ValueError):   # ValueError covers UnicodeDecodeError
        return None
    baked = _vds_parse_baked(text)
    live = {n["id"]: n.get("contract", []) for n in map_nodes}
    drift = [rid for rid, contract in baked.items()
             if rid not in live or _vds_normalize(contract) != _vds_normalize(live[rid])]
    return sorted(drift)


DOC_BUNDLE_MIN_BYTES = 50_000   # a docs/ HTML doc this big is a generated bundle, not a stub


def untracked_members(code_root, members):  # implements: ARCH-TRACKED-042
    """Sorted rel-paths of member files git does not track, or None when unknowable.

    The invariant: a committed generated artifact must depend only on TRACKED files.
    Break it and the map records members a fresh checkout cannot produce, so the
    committed _map.json is unreproducible - `map --check` then fails in CI for a file
    that is not in the repo, which reads as a mystery rather than a mistake. That
    happened twice in one day here: a subagent worktree (a full second copy of the
    tree, gitignored) and a Consilium report carrying a real `generated-from:` tag.
    Both were invisible locally, because the local scan can see what CI never will.

    One `git ls-files` call, not one `check-ignore` per path: being untracked is the
    property that matters, and it also catches a file that is merely uncommitted
    rather than ignored. Returns None - the fail-open signal, matching
    `_since_changed_files` - when git is absent or `code_root` is not a work tree.
    """
    try:
        result = subprocess.run(
            ["git", "-c", "core.quotepath=off", "ls-files", "-z"],
            capture_output=True, text=True, encoding="utf-8", cwd=code_root, timeout=30,
        )
        if result.returncode != 0:
            return None
    except Exception:
        return None
    tracked = {os.path.normcase(p.replace("/", os.sep))
               for p in result.stdout.split("\0") if p}
    seen = set()
    for hits in members.values():
        for _role, fp, _ln in hits:
            seen.add(fp)
    return sorted(fp for fp in seen
                  if os.path.normcase(fp.replace("/", os.sep)) not in tracked)



# Never worth opening for a tag: a tag can only live in text a human wrote.
_BINARY_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".gz", ".tgz", ".7z",
                ".woff", ".woff2", ".ttf", ".otf", ".eot", ".docx", ".xlsx", ".pptx", ".exe",
                ".dll", ".so", ".dylib", ".bin", ".jar", ".class", ".pyc", ".lock", ".mp3", ".mp4")
_UNSCANNED_MAX_BYTES = 1_000_000


def tagged_unscanned_files(code_root, reqs_dir=None):  # implements: ARCH-UNSCANNEDTAG-045
    """Sorted rel-paths of TRACKED files the scan never reads (extension/basename
    outside CODE_EXTS/BASENAME_CODE_FILES) that nonetheless carry a membership tag,
    or None when git cannot answer. A tag in such a file is silently not a member:
    the first consumer run had a tagged Caddyfile and a tagged Prisma schema, both
    invisible. Bounded by `git ls-files` like untracked_members, skips `.reqmapignore`
    matches, the SSOT dir, `_`-prefixed and binary/oversized files; a non-UTF-8 file
    is skipped, never reported."""
    try:
        result = subprocess.run(
            ["git", "-c", "core.quotepath=off", "ls-files", "-z"],
            capture_output=True, text=True, encoding="utf-8", cwd=code_root, timeout=30,
        )
        if result.returncode != 0:
            return None
    except Exception:
        return None
    ignore = load_ignore(code_root, reqs_dir)
    reqs_rel = None
    if reqs_dir:
        try:
            reqs_rel = os.path.relpath(reqs_dir, code_root).replace(os.sep, "/") + "/"
        except ValueError:
            reqs_rel = None
    out = []
    for rel in result.stdout.split("\0"):
        if not rel:
            continue
        fn = os.path.basename(rel)
        # git's and the engine's own dotfiles quote tags as examples (this repo's
        # .reqmapignore explains an illustration id); any other dotfile — .env was the
        # infra run's case — is as tag-worthy as a Makefile and is reported
        if _is_code_file(fn) or fn.startswith(("_", ".git", ".reqmap")) or fn.lower().endswith(_BINARY_EXTS):
            continue
        if reqs_rel and not reqs_rel.startswith("../") and rel.startswith(reqs_rel):
            continue
        if any(fnmatch.fnmatch(rel, pat) for pat in ignore):
            continue
        fp = os.path.join(code_root, rel.replace("/", os.sep))
        try:
            if os.path.getsize(fp) > _UNSCANNED_MAX_BYTES:
                continue
            with open(fp, encoding="utf-8") as f:
                text = f.read()
        except (OSError, ValueError):
            continue
        if TAG_RE.search(text):
            out.append(rel)
    return sorted(out)


def untagged_doc_bundles(code_root, members, reqs_dir=None):  # implements: ARCH-DOCBUNDLE-026
    """Sorted rel-paths of large `docs/` HTML docs that carry no `generated-from:`
    tag — the doc-sync blind spot: a whole-system doc (built from many requirements)
    that drifts from them with nothing linking the two. A bare `generated-from:` only
    pins ONE id, but the multi-id list (ARCH-SCAN-002) lets one doc name all its
    sources. Walk discipline matches scan_members: honors `.reqmapignore`, prunes
    noise. Skips engine-generated outputs (`_`-prefixed, the published `map.html`
    viewer). Threshold-only + warn-only by design, so it nudges without false alarms."""
    tagged = {fp for hits in members.values()
              for (role, fp, _ln) in hits if role == "generated-from"}
    ignore = load_ignore(code_root, reqs_dir)
    out = []
    for dirpath, dirs, files in os.walk(code_root):
        _prune_dirs(dirpath, dirs, reqs_dir, code_root, ignore)
        for fn in sorted(files):
            if not fn.endswith(".html") or fn.startswith("_") or fn == "map.html":
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, code_root).replace(os.sep, "/")
            if not (rel == "docs" or rel.startswith("docs/")):
                continue
            if rel in tagged or any(fnmatch.fnmatch(rel, pat) for pat in ignore):
                continue
            try:
                if os.path.getsize(fp) >= DOC_BUNDLE_MIN_BYTES:
                    out.append(rel)
            except OSError:
                continue
    return sorted(out)


def _scan_untagged(code_root, reqs_dir=None):  # implements: ARCH-NEXT-013
    """Return sorted relative paths of scannable files that carry no membership tags.
    Same walk discipline as scan_members: honors .reqmapignore, prunes .git/node_modules."""
    ignore = load_ignore(code_root, reqs_dir)
    untagged = []
    for dirpath, dirs, files in os.walk(code_root):
        _prune_dirs(dirpath, dirs, reqs_dir, code_root, ignore)
        dirs.sort()
        for fn in sorted(files):
            if not _is_code_file(fn):
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, code_root).replace(os.sep, "/")
            if any(fnmatch.fnmatch(rel, pat) for pat in ignore):
                continue
            if fn.endswith(PROSE_EXTS) and classify_prose(rel) == "ignore":
                continue   # CLAUDE.md, TODO.md, CHANGELOG.md, LICENSE, _-prefixed: invisible by contract (ARCH-PROSE-024)
            tags = _scan_file_tags(fp)
            if tags is not None and not tags:
                untagged.append(rel)
    return sorted(untagged)


ORPHAN_CODE_MIN_LOC = 150   # a program file this big with no tag is a coverage hole, not a stub
# program-logic extensions only: prose/config/styling coverage is ARCH-DOCBUNDLE-026's concern
ORPHAN_CODE_EXTS = (".py", ".js", ".ts", ".tsx", ".jsx", ".c", ".cc", ".cpp",
                    ".h", ".hpp", ".java", ".go", ".rs",
                    ".mjs", ".cjs", ".mts", ".cts", ".vue", ".svelte",
                    ".cs", ".php", ".rb", ".kt", ".kts", ".swift", ".scala", ".ex", ".exs", ".dart")


def orphan_code_files(code_root, covered, reqs_dir=None):  # implements: ARCH-ORPHANCODE-034
    """Sorted rel-paths of program-logic files >= ORPHAN_CODE_MIN_LOC lines that
    carry no requirement link — code implementing behavior no requirement describes.
    `covered` is the rel-path set already linked (membership tags + `verifies:`
    coverage), derived from the caller's existing scans so this adds no second tag
    scan. Walk discipline matches scan_members: honors `.reqmapignore`, prunes noise.
    Warn-only at ANY flag combination (the ARCH-COVERAGE-029 Senate audit capped
    coverage signals at advisory — a hard gate makes hollow tags the way to pass CI)."""
    ignore = load_ignore(code_root, reqs_dir)
    out = []
    for dirpath, dirs, files in os.walk(code_root):
        _prune_dirs(dirpath, dirs, reqs_dir, code_root, ignore)
        for fn in sorted(files):
            if not fn.endswith(ORPHAN_CODE_EXTS):
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, code_root).replace(os.sep, "/")
            if rel in covered or any(fnmatch.fnmatch(rel, pat) for pat in ignore):
                continue
            try:
                with open(fp, encoding="utf-8", errors="ignore") as f:
                    loc = sum(1 for _ in f)
            except OSError:
                continue
            if loc >= ORPHAN_CODE_MIN_LOC:
                out.append(rel)
    return sorted(out)


def scan_ac_verifies(code_root, reqs_dir=None):  # implements: ARCH-ACVERIFY-019
    """Walk the code for `# verifies: REQ-X#AC-N` tags and return
    `{cap_id: {ac_label: [(file, line)]}}` — which labelled criterion each test
    covers. Same walk discipline as `scan_members` (respects .reqmapignore, prunes
    .git/node_modules). Empty when no `verifies:` tag exists anywhere."""
    cover = {}  # cap_id -> {ac_label -> [(file, line)]}
    ignore = load_ignore(code_root, reqs_dir)
    for dirpath, dirs, files in os.walk(code_root):
        _prune_dirs(dirpath, dirs, reqs_dir, code_root, ignore)
        dirs.sort()                  # deterministic descent (cross-platform stable), mirrors scan_members
        for fn in sorted(files):
            if not _is_code_file(fn):
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, code_root).replace(os.sep, "/")
            if any(fnmatch.fnmatch(rel, pat) for pat in ignore):
                continue
            try:
                with open(fp, encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            except OSError:
                continue
            # For .py, mask string-literal content (mirrors _scan_file_tags) so a
            # `verifies:` inside a docstring/string is not counted as real coverage;
            # other file types keep the raw scan.
            is_py = fp.endswith(".py")
            in_triple = None
            for i, line in enumerate(lines, 1):
                s = line
                if is_py:
                    s = s.rstrip("\n\r")
                    if in_triple is not None:
                        idx = s.find(in_triple)
                        if idx == -1:
                            continue
                        s = s[idx + len(in_triple):]
                        in_triple = None
                    s, in_triple = _strip_py_strings(s)
                for cap, ac in AC_VERIFY_RE.findall(s):
                    cover.setdefault(cap, {}).setdefault(ac, []).append((rel, i))
    return cover


def scan_test_levels(code_root, reqs_dir=None):  # implements: ARCH-VLEVEL-037
    """Walk the code for `# tested-by: REQ-X @level` tags and return
    `{cap_id: {level: [(file, line)]}}` — at which V-model level each requirement is
    verified. Kept separate from `scan_members` on purpose: folding the level into the
    member tuples would change the `(role, file, line)` shape that `_map.json` and every
    member consumer depend on. Same walk discipline as `scan_ac_verifies` (respects
    .reqmapignore, prunes .git/node_modules). Empty when no levelled tag exists."""
    cover = {}  # cap_id -> {level -> [(file, line)]}
    ignore = load_ignore(code_root, reqs_dir)
    for dirpath, dirs, files in os.walk(code_root):
        _prune_dirs(dirpath, dirs, reqs_dir)
        dirs.sort()                  # deterministic descent, mirrors scan_members
        for fn in sorted(files):
            if not _is_code_file(fn):
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, code_root).replace(os.sep, "/")
            if any(fnmatch.fnmatch(rel, pat) for pat in ignore):
                continue
            try:
                with open(fp, encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            except OSError:
                continue
            # For .py, mask string-literal content (mirrors _scan_file_tags) so a levelled
            # tag inside a docstring is not counted as real coverage.
            is_py = fp.endswith(".py")
            in_triple = None
            for i, line in enumerate(lines, 1):
                s = line
                if is_py:
                    s = s.rstrip("\n\r")
                    if in_triple is not None:
                        idx = s.find(in_triple)
                        if idx == -1:
                            continue
                        s = s[idx + len(in_triple):]
                        in_triple = None
                    s, in_triple = _strip_py_strings(s)
                # Strip backticked spans before the search, the same phantom-member guard
                # `_scan_file_tags` applies: a documented EXAMPLE of a levelled tag must not
                # register as real coverage. Without it this scanner matches the example in
                # its own constant's comment.
                s = _BACKTICK_RE.sub("", s)
                for idlist, level in TEST_LEVEL_RE.findall(s):
                    for cap in _ID_RE.findall(idlist):
                        cover.setdefault(cap, {}).setdefault(level, []).append((rel, i))
    return cover


_AC_LABEL_RE = re.compile(r"^((?:CASE|AC)-\d+)\b")   # CASE-N is current, AC-N legacy
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
# The template records how a criterion is checked as an HTML comment on its label:
# `AC-1  <!-- verifiable by: automated test -->`. Only this vocabulary marks a
# criterion a machine can never verify; an ABSENT marker means automatable, so a
# corpus that never adopted the marker keeps exactly the behavior it had.
_AC_VERIFIABLE_RE = re.compile(r"verifiable\s+by\s*:([^>]*)", re.I)
_AC_MANUAL_WORDS = ("manual", "inspection", "review", "demo", "walkthrough", "sign-off")


def _acc_blocks(body):  # implements: ARCH-ACVERIFY-019  # implements: ARCH-ATOMICFORM-053
    """Parse the HOW — Acceptance section into one record per criterion:
    `{"label": "AC-1" or "", "text": <folded prose>, "manual": bool}`.

    Two authoring shapes exist and both count: the labelled Gherkin BLOCK the
    template prescribes (`AC-1` followed by indented Given/When/Then lines) and a
    plain `- ` bullet. `_bullets` sees only the second, which is why the emitted
    `acc` list was empty for every requirement written the prescribed way — the map,
    the viewer, and any downstream count had nothing to read (50/50 nodes here).

    An atomic body has no Acceptance heading: its single `Scenario:` block is the one
    criterion, returned unlabelled so `# verifies: <ID>#AC-N` has nothing to point at —
    at one criterion per requirement, `tested-by:` is already per-criterion precision.

    One parser, three callers (`_acc_items`, `_labeled_acs`, `_count_ac`) so a
    criterion cannot be counted by one and missed by another. The block-start test
    is `_count_ac`'s verbatim, keeping `len(_acc_blocks(b)) == _count_ac(b)`."""
    _sp = _atomic_spans(body)
    if _sp:                                        # atomic: the Scenario is the one criterion
        _txt = " ".join(l.strip() for l in _sp[1])
        return [{"label": "", "text": _txt, "manual": bool(_AC_VERIFIABLE_RE.search(_txt))
                 and any(w in _txt.lower() for w in _AC_MANUAL_WORDS)}]
    out, grab, seen, fenced = [], False, False, False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):
            fenced = not fenced                  # skip fenced examples, like _count_ac
            continue
        if fenced:
            continue
        if s.lower().startswith("## "):
            grab = (not seen) and any(_heading_label_is(s, n) for n in ACCEPTANCE_LABELS)
            if grab:
                seen = True
            continue
        if not grab:
            continue
        m = _AC_LABEL_RE.match(s)
        if m or s.startswith("- "):
            label = m.group(1) if m else ""
            out.append({"label": label, "raw": [s[len(label):] if m else s[2:]]})
        elif s and out:
            # continuation of the criterion above (an indented Given/When/Then line,
            # or a marker comment on its own line) — folded in, so a multi-line
            # criterion is never truncated to its first physical line.
            out[-1]["raw"].append(s)
    blocks = []
    for b in out:
        raw = " ".join(b["raw"]).strip()
        mark = _AC_VERIFIABLE_RE.search(raw)
        marker = mark.group(1) if mark else ""
        blocks.append({
            "label": b["label"],
            "text": _HTML_COMMENT_RE.sub("", raw).strip(),
            # `|` means the template's unedited placeholder list ("automated test |
            # manual | inspection | load test") — an author who never chose is not
            # declaring the criterion manual.
            "manual": "|" not in marker and any(w in marker.lower() for w in _AC_MANUAL_WORDS),
        })
    return blocks


def _acc_items(body):  # implements: ARCH-MAP-007
    """Acceptance criteria as display strings, for the emitted `acc` list: an
    `AC-1 — Given … When … Then …` line per labelled block, or the bullet text."""
    out = []
    for b in _acc_blocks(body):
        label, text = b["label"], b["text"]
        item = f"{label} — {text}" if label and text else (label or text)
        if item:
            out.append(item)
    return out


def _labeled_acs(body):  # implements: ARCH-ACVERIFY-019
    """Ordered list of `AC-N` labels declared in the HOW — Acceptance section.
    Empty when the requirement writes bullet ACs without labels — per-AC coverage
    only applies to requirements that label their criteria, so unlabelled ones are
    silently exempt (no false 'unverified' warning)."""
    out = []
    for b in _acc_blocks(body):
        if b["label"] and b["label"] not in out:
            out.append(b["label"])
    return out


def _automatable_acs(body):  # implements: ARCH-ACVERIFY-019
    """`_labeled_acs` minus the criteria marked `verifiable by: inspection|manual`.
    A criterion a human checks by reading can never carry a `# verifies:` tag, so
    counting it as unverified is a warning no one can ever clear — the marker the
    template already prescribes is the answer, it simply was not read here."""
    return [b["label"] for b in _acc_blocks(body)
            if b["label"] and not b["manual"]]


# ---------- hashing / drift ----------
# A normative section heading: the canonical `## WHAT — Contract …` / `## HOW —
# Acceptance …`, or a legacy bare `## Contract`/`## Acceptance`/`## Input`/`## Output`.
# Anchored so the keyword must be the label (right after `## ` or after a WHAT/HOW —
# prefix), NOT anywhere in the heading — otherwise a commentary heading like
# `## Notes — contract caveats` would leak into the drift hash.
# prefix set MUST stay in lockstep with _heading_label_is so the drift hash and
# section detection agree on which heading is a normative section (see its docstring)
_NORMATIVE_HEADING_RE = re.compile(
    r"^##\s+(?:(?:what|why|where|how)\s*[—–-]?\s*)?"
    r"(?:description|contract|acceptan|input|output)", re.I)

# The binding-clause section, current name first. `## Description` merged the standalone
# `> WHY:` blockquote and `## WHAT — Contract (normative)` into one section: a reader met
# the same capability described twice, once as rationale and once as obligation, under two
# headings that both said WHAT. The legacy name keeps working forever — a consumer repo's
# existing files are not a migration this tool gets to demand.
CONTRACT_LABELS = ("description", "contract")   # implements: ARCH-DESCRIPTION-057

# The acceptance-criteria section, current name first. `## Cases` and its `CASE-N` labels
# replaced `## HOW — Acceptance (= tests)` and `AC-N`: a criterion IS a test case, and the
# old name made the section sound like a sign-off step rather than the cases a reader can
# run. Both names are honoured, and `# verifies: <ID>#AC-N` keeps working — the label is an
# identifier a tag points at, so dropping the old spelling would break every consumer tag
# already written against it.
ACCEPTANCE_LABELS = ("cases", "acceptan")       # implements: ARCH-DESCRIPTION-057


def _heading_label_is(heading, name):  # implements: ARCH-CHECK-006
    """True if a `## ` heading's LABEL is `name` (case-insensitive), allowing an
    optional `WHAT`/`HOW` prefix whose dash is optional — so `## WHAT — Contract`,
    `## WHAT Contract`, and bare `## Contract` all match name='contract'. Anchored
    to the label start so a commentary heading like `## Notes — contract caveats`
    does NOT match name='contract'. Keeps section detection (the gate, the linter)
    in agreement with the drift hash (_NORMATIVE_HEADING_RE) — see the silent-drift
    inconsistency this guards against."""
    return bool(re.match(
        r"##\s+(?:(?:what|why|where|how)\s*[—–-]?\s*)?" + re.escape(name.lower()),
        heading.strip().lower()))


_ATOMIC_SCENARIO_RE = re.compile(r"^\s*Scenario\s*:", re.I)
VALID_FORM = {"atomic"}                            # implements: ARCH-ATOMICFORM-053


def _atomic_spans(body):  # implements: ARCH-ATOMICFORM-053
    """`(statement_lines, scenario_lines)` for a body in the atomic form, else None.

    The atomic form carries no normative `## ` heading at all: a `>` blockquote states the
    single obligation and an unlabelled `Scenario:` block states its acceptance, both sitting
    between the `# ` title and the first `## ` (which begins the auto sections). Both parts
    are required, so a classic body — whose `>` WHY sits above `## WHAT — Contract` and whose
    Given/When/Then lives under a heading — returns None and every existing code path is
    unchanged.

    Detected from the BODY, not from `form: atomic` in the frontmatter, because every
    consumer of these spans (binding_hash, _has_section, _acc_blocks, _bullets) is handed a
    body and no meta. The frontmatter key is validated separately, as documentation."""
    story, scen, in_scen = [], [], False
    for line in body.splitlines():
        st = line.strip()
        if st.startswith("## "):
            break                                  # auto sections end the normative span
        if st.startswith("# "):
            continue                               # the title is not normative
        if _ATOMIC_SCENARIO_RE.match(line):
            in_scen = True
            scen.append(line.rstrip())
            continue
        if in_scen:
            if st:
                scen.append(line.rstrip())
            continue
        if st.startswith(">"):
            story.append(line.rstrip())
    if not story or not scen:
        return None
    return story, scen


def binding_hash(body):  # implements: ARCH-DRIFT-003  # implements: ARCH-ATOMICFORM-053
    """Hash only the NORMATIVE sections — the Contract and the Acceptance criteria.
    Everything else (Verify-intent, Notes, Current-implementation, links) is
    commentary and may drift freely without tripping the gate. (Legacy docs used
    Input/Output/Acceptance; those headers are still honored for back-compat.)"""
    keep, grab = [], False
    for line in body.splitlines():
        h = line.strip().lower()
        if h.startswith("## "):
            new_grab = bool(_NORMATIVE_HEADING_RE.match(h))
            if new_grab:
                # section boundary sentinel: keeps Contract and Acceptance distinct so
                # relocating a clause between them is not invisible to the drift hash.
                keep.append("\x1e")
            grab = new_grab
            continue
        if grab and line.strip():
            if line.strip().startswith(">"):
                # `## Description` opens with the intent blockquote — rationale, not an
                # obligation. Hashing it would report DRIFT on a confirmed contract every
                # time someone improved the explanation, which is the opposite of what
                # drift is for. The atomic form draws the same line, keeping `rationale:`
                # in the frontmatter and out of the span. No requirement carried a
                # blockquote inside a normative section when this was added, so no
                # existing hash changes.
                continue
            # rstrip (not strip): leading indent is structure — unnesting a sub-clause
            # is a real change and must drift.
            keep.append(line.rstrip())
    if not keep:
        # No normative heading: either the atomic form, whose obligation and Scenario ARE the
        # normative span, or a malformed body. Hashing the atomic span is what keeps drift
        # alive — without it every heading-less requirement hashes the empty string and
        # collides with every other, so no content change could ever be detected.
        _sp = _atomic_spans(body)
        if _sp:
            keep = _sp[0] + ["\x1e"] + _sp[1]
    return hashlib.sha256("\n".join(keep).encode()).hexdigest()[:12]


def lock_path(reqs_dir):  # implements: ARCH-DRIFT-003
    return os.path.join(reqs_dir, "_reqlock.json")


def load_lock(reqs_dir):  # implements: ARCH-DRIFT-003
    p = lock_path(reqs_dir)
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
            # a valid-JSON-but-non-object lock ([], null, 42) must also fail open —
            # consumers call lock.get(rid); fail open like load_memberlock/_load_scancache
            return data if isinstance(data, dict) else {}
        except (ValueError, OSError):
            # empty / corrupt / merge-conflicted / non-UTF-8 lock: treat as no lock.
            # ValueError covers both json.JSONDecodeError and UnicodeDecodeError, so
            # a binary-garbage lock fails open here instead of crashing the gate.
            return {}
    return {}


def save_lock(reqs_dir, lock):  # implements: ARCH-DRIFT-003
    os.makedirs(reqs_dir, exist_ok=True)
    with open(lock_path(reqs_dir), "w", encoding="utf-8") as f:
        json.dump(lock, f, indent=2, sort_keys=True)


# ---------- member-hash drift (reverse direction) ----------
# _reqlock.json keeps ONE hash per requirement = the contract; drift in that file only
# fires prose-ahead-of-code. The reverse — a MEMBER's content changed while the contract
# stayed put (behaviour shipped, spec not updated) — is invisible there. Member hashes
# live in a SEPARATE, versioned sidecar so _reqlock.json stays a byte-stable cross-repo
# contract: an older seeded engine never reads _memberlock.json and is wholly unaffected.
MEMBERLOCK_SCHEMA = 1
MEMBER_ROLES = ("implements", "generated-from")   # roles that bind code/doc content to a contract


def _memberlock_path(reqs_dir):  # implements: ARCH-MEMBERDRIFT-027
    return os.path.join(reqs_dir, "_memberlock.json")


def load_memberlock(reqs_dir):  # implements: ARCH-MEMBERDRIFT-027
    """Return {rid: {relfile: sha}} from the sidecar, or {} when absent/corrupt or
    written by a NEWER schema than this engine knows — fail open (no false drift) the
    same way load_lock and the scan cache do, so a forward-incompatible sidecar degrades
    to 'reverse-drift off this run' rather than crashing or mis-comparing."""
    try:
        with open(_memberlock_path(reqs_dir), encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict) or data.get("_schema") != MEMBERLOCK_SCHEMA:
        return {}
    members = data.get("members")
    return members if isinstance(members, dict) else {}


def save_memberlock(reqs_dir, member_hashes):  # implements: ARCH-MEMBERDRIFT-027
    os.makedirs(reqs_dir, exist_ok=True)
    payload = {"_schema": MEMBERLOCK_SCHEMA, "members": member_hashes}
    with open(_memberlock_path(reqs_dir), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def untracked_locks(reqs_dir):  # implements: ARCH-CHECK-006
    """Lock sidecars (`_reqlock.json`, `_memberlock.json`) are committed-by-design: an
    uncommitted one silently disables drift detection on a fresh CI checkout (no baseline
    to compare against). Return the paths of any that exist on disk but are NOT git-tracked.
    Fail-open: returns [] when git is unavailable or the tree is not a work tree, so the
    gate never breaks on a non-git consumer — the same discipline the map's git-derived
    `repo` field uses."""
    paths = [p for p in (lock_path(reqs_dir), _memberlock_path(reqs_dir)) if os.path.isfile(p)]
    if not paths:
        return []
    root = os.path.dirname(os.path.abspath(reqs_dir)) or "."
    try:
        inside = subprocess.run(["git", "-C", root, "rev-parse", "--is-inside-work-tree"],
                                capture_output=True, text=True, timeout=3)
        if inside.returncode != 0 or inside.stdout.strip() != "true":
            return []
        out = []
        for p in paths:
            r = subprocess.run(["git", "-C", root, "ls-files", "--error-unmatch", os.path.abspath(p)],
                               capture_output=True, text=True, timeout=3)
            if r.returncode != 0:
                out.append(p)
        return out
    except (OSError, subprocess.SubprocessError):
        return []


def _file_sha(path):  # implements: ARCH-MEMBERDRIFT-027
    """SHA-256 of a member file with line endings normalized to LF, so the hash is identical
    whether the tree was checked out LF (Linux/CI) or CRLF (Windows core.autocrlf=true).
    Without this, a lock generated on one platform shows spurious whole-repo member drift on
    the other — under `gate --strict` that turns every member into a false error. Mirrors the
    contract hash, which is already LF-normalized via the text-mode body parse."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def compute_member_hashes(code_root, members):  # implements: ARCH-MEMBERDRIFT-027
    """{rid: {relfile: sha}} for member files dedicated to ONE requirement. A file that
    is an implements/generated-from member of several requirements (e.g. a single engine
    file) is excluded: a change there cannot be attributed to one contract without noise."""
    owners = {}   # relfile -> set(rid)
    for rid, hits in members.items():
        for role, fp, _ln in hits:
            if role in MEMBER_ROLES:
                owners.setdefault(fp, set()).add(rid)
    out = {}
    for fp, rids in owners.items():
        if len(rids) == 1:
            sha = _file_sha(os.path.join(code_root, fp))
            if sha is not None:
                out.setdefault(next(iter(rids)), {})[fp] = sha
    return out


def member_drift(reqs, members, lock, memberlock, code_root, current=None):  # implements: ARCH-MEMBERDRIFT-027
    """Sorted (rid, relfile) where a confirmed requirement's dedicated member changed
    since the member-lock while the requirement's OWN contract did not. A requirement
    whose contract also drifted is skipped — that is forward drift (the spec WAS
    re-touched) and the contract-drift warning already owns it. A member with no recorded
    baseline is skipped, so a freshly-tagged file is baselined on the next sync, not nagged.

    `current` lets a caller that already computed `compute_member_hashes(code_root, members)`
    (e.g. to also rebaseline `_memberlock.json` from the same member set) pass it in instead
    of paying for a second identical hash pass; omit it to compute it here as before."""
    if current is None:
        current = compute_member_hashes(code_root, members)
    out = []
    for rid, r in reqs.items():
        if r["meta"].get("status") != "confirmed":
            continue
        if lock.get(rid) and lock[rid] != binding_hash(r["body"]):
            continue   # forward drift owns this requirement
        recorded = memberlock.get(rid, {})
        for rel, sha in current.get(rid, {}).items():
            old = recorded.get(rel)
            if old and old != sha:
                out.append((rid, rel))
    return sorted(out)


# ---------- commands ----------
def _has_section(body, name):  # implements: ARCH-CHECK-006
    """True if the body has a normative `## ` heading whose LABEL is `name`
    (case-insensitive), e.g. `## WHAT — Verify intent` for name='verify intent'.
    Anchored to the label (see `_heading_label_is`) so a commentary heading that
    merely mentions the word — `## Notes — contract caveats` — does not count as a
    Contract section, and a dash-less `## WHAT Contract` does. This keeps the gate's
    section-presence check in agreement with the drift hash, closing the
    silent-drift gap where a heading passed the gate but produced an empty hash.
    The atomic form (ARCH-ATOMICFORM-053) has no normative headings by design; its statement
    and Scenario stand in for both, so it answers True for those two names."""
    if name in CONTRACT_LABELS + ACCEPTANCE_LABELS and _atomic_spans(body):
        return True
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("## ") and _heading_label_is(s, name):
            return True
    return False


def _has_any(body, names):  # implements: ARCH-DESCRIPTION-057
    """True if the body carries any of `names` as a section. One requirement never uses two
    spellings of the same section at once, so 'any' is not a merge — it is 'whichever name
    this file happens to use'."""
    return any(_has_section(body, n) for n in names)


def _from_any(fn, body, names):  # implements: ARCH-DESCRIPTION-057
    """`fn(body, name)` for the first of `names` that yields content, else the empty value
    `fn` returns for the first name — so the caller's type (list, str) is preserved."""
    for n in names:
        got = fn(body, n)
        if got:
            return got
    return fn(body, names[0])


def cmd_scan(reqs, members):  # implements: ARCH-SCAN-005
    for cap in sorted(set(list(reqs) + list(members))):
        print(cap)
        for role, fp, ln in members.get(cap, []):
            print(f"    {role:18} {fp}:{ln}")
        if cap not in members:
            print("    (no members found)")


def _engine_version_at(path):
    """Best-effort MAP_ENGINE_VERSION parsed from a reqmap.py at `path`; None on any failure."""
    try:
        with open(path, encoding="utf-8") as f:
            # whole file + line-anchored: a bounded read() silently returned None
            # once the header outgrew the bound, and an unanchored search could
            # match a docstring mention before the real assignment.
            m = re.search(r'(?m)^MAP_ENGINE_VERSION\s*=\s*"([^"]+)"', f.read())
        return m.group(1) if m else None
    except Exception:  # fail open — never let the staleness probe break the gate
        return None


def _ver_key(v):  # implements: ARCH-CHECK-006
    """Sortable key for a MAP_ENGINE_VERSION (`YYYY-MM-DD` + optional `.N` suffix).
    Compares the numeric suffix as an int so `.10` sorts after `.9` (lexicographic
    string compare gets that wrong)."""
    date, _, n = (v or "").partition(".")
    return (date, int(n) if n.isdigit() else 0)


def warn_if_stale():  # implements: ARCH-CHECK-006
    """Print a non-fatal notice when this vendored copy is older than the installed
    plugin's. Silent in CI: only runs when CLAUDE_PLUGIN_ROOT is set. Never raises,
    never affects the exit code."""
    try:
        root = os.environ.get("CLAUDE_PLUGIN_ROOT")
        if not root:
            return
        plugin_ver = _engine_version_at(os.path.join(root, "scripts", "reqmap.py"))
        if plugin_ver and _ver_key(plugin_ver) > _ver_key(MAP_ENGINE_VERSION):
            print(f"WARN  vendored reqmap.py is stale ({MAP_ENGINE_VERSION} < plugin "
                  f"{plugin_ver}) - re-seed: cp \"$CLAUDE_PLUGIN_ROOT/scripts/reqmap.py\" "
                  f"scripts/reqmap.py")
    except Exception:
        return


# Unambiguous test markers, trusted in ANY file: Python `def test…(`, JS/TS
# `function test…(`, Go `func TestX/Benchmark/Example/Fuzz(`, Rust `#[test]` /
# `#[tokio::test]`. Used only to confirm a tested-by file holds tests — not to count.
# Case-insensitive for Python/JS/Rust idioms, but the Go branch stays
# case-sensitive: `go test` only runs exported TestXxx/BenchmarkXxx/ExampleXxx/
# FuzzXxx — a private `func testHelper(` is NOT a test and must not satisfy a link.
_DEF_TEST_RE = re.compile(
    r"(?i:def\s+test\w*\s*\()|(?i:function\s+test\w*\s*\()|"
    r"func\s+(?:Test|Benchmark|Example|Fuzz)\w*\s*\(|"
    r"(?i:#\[\s*(?:[\w:]+::)?test\b)")
# The bare Jest/Mocha `it(` / `test(` call is too common a word to trust in prose or
# config (e.g. "it (the parser) returns None" in a .md), so it is honored ONLY in a
# JS/TS source file, where it is a genuine test idiom.
_CALL_TEST_RE = re.compile(r"\b(?:it|test)\s*\(", re.IGNORECASE)
_CALL_TEST_EXTS = (".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs")

# A stdlib-only Python suite often exposes no `def test…` — it drives its checks from a
# runnable entry point (`run` / `run_tests` / `main`) under an `if __name__ == "__main__"`
# guard, signalling pass/fail via the process exit code. Honored ONLY for a `tested-by`
# target (the author has already declared the file a test) and ONLY in a `.py` file, so a
# non-test module that merely defines a `main()` is never mistaken for a test elsewhere.
_PY_TEST_ENTRY_RE = re.compile(r"^\s*def\s+(?:run|run_tests|main)\s*\(", re.MULTILINE)
_PY_MAIN_GUARD_RE = re.compile(r"""if\s+__name__\s*==\s*["']__main__["']""")

# A shell suite declares a test as a bash function (`test_x() {`, `function test_x {`)
# or a bats case (`@test "…" {`) — none of which match the Python/JS/Go/Rust idioms
# above, so four real bash suites warned permanently in a consumer repo. The filename
# conventions are honored too: naming a file `*.test.sh` AND tagging it `tested-by`
# are two independent declarations that it is a test.
_SH_TEST_EXTS = (".sh", ".bash", ".zsh", ".bats")
_SH_TEST_NAME_RE = re.compile(r"(?:^|[._-])test[._-]|[._-]test$|^test[._-]", re.I)
_SH_TEST_RE = re.compile(
    r"(?m)^\s*(?:@test\b"
    r"|(?:function\s+)?(?:test|assert|check|expect|should)[\w:.-]*\s*\(\s*\)"
    r"|function\s+(?:test|assert|check|expect|should)[\w:.-]*\b)", re.I)


# A requirement whose implementation is not its own code. Both layers are covered by
# an EDGE instead of an `implements:` tag: a `need` by the `satisfies:` edges pointing
# up at it, an `aggregate` by its own `depends_on` edges pointing down.
IMPL_EXEMPT_LAYERS = ("need", "aggregate")


def _impl_exempt(meta):  # implements: ARCH-TRACE-020
    """True when a requirement is exempt from the "confirmed code must exist" rule.

    One predicate, four callers (gate link-sync, `health`, the risk signals, and
    `confirm`). They disagreed before: three exempted `layer: need` and `confirm` did
    not, so the layer's own reference case could not be promoted by the command that
    exists to promote it — `SYS-SSOT-001` is `confirmed` here only because the file
    was hand-edited around `confirm`."""
    return (meta or {}).get("layer") in IMPL_EXEMPT_LAYERS


def _test_link_problem(path):  # implements: ARCH-TESTLINK-018
    """Return a short reason a `tested-by` file fails the behavior-sync check, or ''
    when it is fine. A file that is missing, unreadable, or holds no recognizable
    test function means the link asserts coverage it does not have. Deterministic
    and warn-only — it never proves per-criterion coverage, only that real tests
    exist at the link target (per-AC mapping needs a per-AC tag, deferred)."""
    if not os.path.isfile(path):
        return "does not exist (broken tested-by link)"
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            src = f.read()
    except OSError:
        return "is unreadable"
    if _DEF_TEST_RE.search(src):
        return ""
    if path.lower().endswith(_CALL_TEST_EXTS) and _CALL_TEST_RE.search(src):
        return ""
    if (path.lower().endswith(".py")
            and _PY_TEST_ENTRY_RE.search(src) and _PY_MAIN_GUARD_RE.search(src)):
        return ""
    if path.lower().endswith(_SH_TEST_EXTS):  # implements: ARCH-TESTLINK-018
        stem = os.path.splitext(os.path.basename(path))[0]
        if _SH_TEST_NAME_RE.search(stem) or _SH_TEST_RE.search(src):
            return ""
    return ("contains no test function "
            "(def test.../func TestX.../#[test]/it()/bash test_x()/py run|main under __main__)")


def cmd_check(reqs, members, reqs_dir, update_lock, code_root=".", strict=False, as_json=False, since=None, accept_drift=True,
              ac_cover=None, level_cover=None):  # implements: ARCH-CHECK-006
    errors, warns = [], []
    strict_warns = []   # warns promoted to errors under --strict
    warn_if_stale()
    cap_ids = set(reqs)

    # The reverse-drift baseline (_memberlock) must always cover the FULL member
    # set; --since narrows `members` only to scope the gate's checks, so keep an
    # unfiltered copy for the memberlock re-baseline below.
    full_members = members

    # --since: scope checks to requirements whose member files changed since ref.
    # Fail-open: fall back to full scan with WARN if git is unavailable or ref invalid.
    if since:
        changed = _since_changed_files(since, code_root)
        if changed is None:
            warns.append(f"--since {since!r}: git diff failed or ref not found; falling back to full scan")
        else:
            # Keep only members whose file appears in the changed set
            filtered = {}
            for cap, entries in members.items():
                kept = [
                    (role, fp, ln) for role, fp, ln in entries
                    if _path_key(os.path.join(code_root, fp)) in changed
                ]
                if kept:
                    filtered[cap] = kept
            members = filtered

    # Both coverage maps come from the caller on the CLI path, where `scan_all` already
    # produced them in the same walk that produced `members` — three passes over the
    # tree collapsed into one. Computed here when absent, so every other caller
    # (tests, an embedding tool) keeps working unchanged.
    if ac_cover is None:
        ac_cover = scan_ac_verifies(code_root, reqs_dir)  # {cap: {AC-N: [...]}}
    # V-model opt-in triggers, computed once. Neither this rule nor the level-fit rule can
    # fire until the repo has deliberately adopted the vocabulary, so installing this engine
    # adds no warnings to a repo that never annotates a tag (ARCH-VLEVEL-037).
    any_validation = any(x[0] == "validated-against"
                         for hits in members.values() for x in hits)
    if level_cover is None:
        level_cover = scan_test_levels(code_root, reqs_dir)   # {cap: {level: [...]}}
    satisfied_by = {rid: [] for rid in reqs}          # reverse upstream edges
    for _rid, _r in reqs.items():
        for _up in _as_list(_r["meta"].get("satisfies")):
            if _up in satisfied_by:
                satisfied_by[_up].append(_rid)

    for cap, hits in members.items():
        if cap not in cap_ids:
            errors.append(f"dangling tag: code references {cap} but no requirement exists")

    for rid, r in reqs.items():
        m = r["meta"]
        if m.get("status") not in VALID_STATUS:
            errors.append(f"{rid}: invalid status {m.get('status')!r}")
        _frm = m.get("form")                              # implements: ARCH-ATOMICFORM-053
        if _frm and _frm not in VALID_FORM:
            errors.append(f"{rid}: invalid form {_frm!r} (expected one of {sorted(VALID_FORM)})")
        if _frm == "atomic" and not _atomic_spans(r["body"]):
            errors.append(f"{rid}: form: atomic but the body has no `>` statement plus "
                          f"`Scenario:` block before the first `## ` heading")
        _lvl = m.get("level")                             # implements: ARCH-LEVEL-051
        if _lvl and _lvl not in VALID_LEVEL:
            errors.append(f"{rid}: invalid level {_lvl!r} (expected one of {sorted(VALID_LEVEL)})")
        if m.get("layer") not in VALID_LAYER:
            errors.append(f"{rid}: invalid layer {m.get('layer')!r}")
        # milestone (warn): an optional, roadmap-only field. A malformed value silently fails
        # to sort in the Roadmap (semverCmp treats junk as 0) rather than breaking the build,
        # so it warns (never errors), only when present and not deprecated.
        ms = m.get("milestone")
        if ms and m.get("status") != "deprecated" and not MILESTONE_RE.match(str(ms).strip()):
            warns.append(f"{rid}: milestone {ms!r} is malformed (expected v<digits>[.<digits>…], e.g. v1.14)")
        for dep in _as_list(m.get("depends_on")):
            if dep not in cap_ids:
                errors.append(f"{rid}: depends_on missing {dep}")
        # upstream traceability (warn-only): a `satisfies` id should resolve to a real
        # requirement, but a dangling one is a WARN not an ERROR — an upstream need may
        # be authored later or live in an external tracker.  # implements: ARCH-TRACE-020
        for up in _as_list(m.get("satisfies")):
            if up not in cap_ids:
                warns.append(f"{rid}: satisfies {up} but no such requirement (upstream trace dangling)")
        # a `need`/`aggregate` is covered by edges (satisfies:/depends_on), not code — so
        # it is exempt from the code-coverage gates. # implements: ARCH-TRACE-020
        is_need = m.get("layer") == "need"
        impl_exempt = _impl_exempt(m)
        impls = [x for x in members.get(rid, []) if x[0] == "implements"]
        # When --since filters members, skip code-coverage checks for reqs with no members in the diff
        if m.get("status") in ENFORCED and not impls and not impl_exempt:
            if rid in members:
                # Requirement is in the filtered scope but has no implements tag
                errors.append(f"{rid}: status {m['status']} but no implements: tag found in code")
            elif not since:
                # Full scan and requirement is enforced but has no impl tag
                errors.append(f"{rid}: status {m['status']} but no implements: tag found in code")
        tests = [x for x in members.get(rid, []) if x[0] == "tested-by"]
        if m.get("status") == "confirmed" and not tests and not m.get("test_exempt") and not impl_exempt:
            # Similar logic for test checks: only enforce if the requirement is in scope
            if rid in members or not since:
                warns.append(f"{rid}: confirmed but no tested-by: tag — acceptance tests not linked")
        # V-model validation (warn-only): a `need` is validated, not tested. A unit test
        # cannot show the RIGHT thing was built, so a need with only code coverage is
        # false confidence exactly where it costs most. Opt-in via `any_validation`.
        if is_need and m.get("status") == "confirmed" and any_validation:
            if not [x for x in members.get(rid, []) if x[0] == "validated-against"]:
                warns.append(f"{rid}: confirmed need with no `validated-against:` tag — "
                             "nothing shows the need was actually met")
        # V-model level fit (warn-only): foundation code covered only end-to-end is slow,
        # fragile, and localises failures poorly. Unlevelled links are ignored rather than
        # assumed low-level — assuming would make the rule unfireable in exactly the
        # half-migrated repos it helps most. Opt-in: no levelled link, no judgement.
        if m.get("status") == "confirmed" and m.get("layer") == "bus":
            levels = set(level_cover.get(rid, {}))
            if levels == {"system"}:
                warns.append(f"{rid}: bus capability verified only at @system level — "
                             "add a @unit or @integration `tested-by:` link")
        # V-model rungs (warn): a requirement that declares its specification level and
        # carries levelled test links should carry at least one at the paired verification
        # level — system requirements answered by system tests, architecture by integration,
        # detailed design by unit. Deliberately narrow: it judges nothing without BOTH
        # declarations, so it cannot fire on a corpus that has adopted neither, and it does
        # not infer a level from `layer:` — that inference is what ADR-0007 measured at
        # 36-of-40 and rejected. # implements: ARCH-VRUNGS-054
        _want = LEVEL_TEST_PAIR.get(m.get("level"))
        if m.get("status") == "confirmed" and _want:
            _have = set(level_cover.get(rid, {}))
            if _have and _want not in _have:
                warns.append(f"{rid}: level: {m['level']} is verified at "
                             f"{'/'.join('@' + x for x in sorted(_have))} but not @{_want} — "
                             f"add a @{_want} `tested-by:` link, or change the level")
        # owner accountability (warn): a confirmed requirement with owner: auto was never
        # claimed by a human reviewer — assign an owner before the corpus grows anonymous.
        if m.get("status") == "confirmed" and m.get("owner", "auto") in ("auto", "", None):
            warns.append(f"{rid}: confirmed requirement has owner: auto — assign a named owner")
        # behavior-sync (warn-only): a tested-by link must point at a file that
        # exists and actually holds tests, else it asserts coverage it lacks.
        # Checked at EVERY status, not only `confirmed`: a link pointing at a React
        # component instead of its spec is wrong the day it is written, and hiding
        # that until promotion means the corpus is audited exactly when it is largest.
        # A non-confirmed requirement warns but is never strict-promoted, so a
        # draft-heavy consumer's `--strict` CI cannot start failing on this.
        if tests:
            for fp in sorted({t[1] for t in tests}):  # implements: ARCH-TESTLINK-018
                problem = _test_link_problem(os.path.join(code_root, fp))
                if problem:
                    bucket = strict_warns if m.get("status") == "confirmed" else warns
                    bucket.append(f"{rid}: tested-by {fp} {problem}")
        # per-AC coverage (warn-only): a confirmed requirement that LABELS its criteria
        # (AC-1, AC-2, ...) should have a `# verifies: <id>#AC-N` tag for each. Only
        # fires once at least one criterion is covered, so adopting per-AC tagging is
        # opt-in: a requirement with zero verifies tags keeps the coarse tested-by check.
        # ONE aggregated line, not one per missing criterion: a corpus that tagged 110
        # criteria correctly saw its warning count fall only 171 -> 98, because every
        # requirement that entered the regime lit up a warning per criterion still to
        # do. Partial adoption is the step being asked for; it must not cost more than
        # tagging nothing. Machine-unverifiable criteria are excluded (_automatable_acs).
        if m.get("status") == "confirmed":  # implements: ARCH-ACVERIFY-019
            labels = _automatable_acs(r["body"])
            covered = ac_cover.get(rid, {})
            if labels and covered:
                missing = [ac for ac in labels if ac not in covered]
                if missing:
                    warns.append(
                        f"{rid}: {len(labels) - len(missing)}/{len(labels)} automatable criteria "
                        f"carry a `# verifies:` tag — missing " + ", ".join(missing))
        if m.get("status") == "confirmed":
            if not _has_any(r["body"], CONTRACT_LABELS):
                warns.append(
                    f"{rid}: confirmed but missing '## Description' section — "
                    "add the normative contract or drop status back to in-progress"
                )
            if not _has_any(r["body"], ACCEPTANCE_LABELS):
                warns.append(
                    f"{rid}: confirmed but missing '## Cases' section — "
                    "add acceptance criteria or drop status back to in-progress"
                )
        # reverse upstream traceability (warn-only): a stakeholder `need` that nothing
        # satisfies is unaddressed — surface it so a need does not silently lack a
        # requirement that fulfils it.  # implements: ARCH-TRACE-020
        if is_need and m.get("status") in ENFORCED and not satisfied_by.get(rid):
            warns.append(f"{rid}: need has no requirement that satisfies it (upstream trace unaddressed)")

    lock = load_lock(reqs_dir)
    # load_lock fails open ({}) on an absent OR corrupt/merge-conflicted lock; the
    # two look identical to the drift loop (every `old` is None -> no drift ever
    # fires). Surface the corrupt case so a silently-disabled drift signal is visible.
    lp = lock_path(reqs_dir)
    if os.path.exists(lp):
        try:
            with open(lp, encoding="utf-8") as f:
                json.load(f)
        except (ValueError, OSError):  # JSONDecodeError + UnicodeDecodeError both subclass ValueError
            warns.append("_reqlock.json present but unreadable (corrupt/merge-conflicted) "
                         "— drift detection skipped this run; re-run with --update-lock")

    # app/src/lib/data.js drift (warn-only): the viewer's fallback fixture vs the
    # live registry. Skipped entirely (no _viewer_nodes build) unless a data.js
    # actually exists — true for every consumer repo without a vendored viewer.
    for _candidate in (os.path.join(code_root, "app", "src", "lib", "data.js"),
                        os.path.join(code_root, "..", "app", "src", "lib", "data.js")):
        if os.path.exists(_candidate):
            # Built here (not via _build_map_data) since only id+contract is
            # needed — avoids computing used_by/satisfied_by for a check that
            # discards them.
            _viewer_nodes = [{"id": rid,
                              "contract": _from_any(_bullets, r["body"], CONTRACT_LABELS)}
                              for rid, r in reqs.items()]
            _drifted = check_viewer_data_sync(_candidate, _viewer_nodes)
            if _drifted:
                warns.append(
                    "app/src/lib/data.js out of sync with {} requirement(s): {} — regenerate its "
                    "BAKED fixture or accept the drift is intentional for this fallback demo data."
                    .format(len(_drifted), ", ".join(_drifted)))
            break

    # Reverse depends_on index: a contract drift's blast radius is its direct
    # dependents (one edge, not the transitive closure — a reviewer follows the
    # chain one hop at a time).  # implements: ARCH-DRIFTIMPACT-035
    dependents = {}
    for _rid, _r in reqs.items():
        for _dep in _as_list(_r["meta"].get("depends_on")):
            dependents.setdefault(_dep, set()).add(_rid)
    new_lock = {}
    for rid, r in reqs.items():
        h = binding_hash(r["body"])
        new_lock[rid] = h
        old = lock.get(rid)
        if old and old != h and r["meta"].get("status") == "confirmed":
            # name the member locations so the warning is actionable, not "its members"
            locs = [f"{fp}:{ln}" for (_role, fp, ln) in members.get(rid, [])]
            where = ", ".join(locs) if locs else "no members tagged — add an implements: tag"
            deps_of = sorted(dependents.get(rid, ()))
            fanout = "; review dependent(s): " + ", ".join(deps_of) if deps_of else ""
            strict_warns.append(f"{rid}: DRIFT — contract changed since lock; "
                               f"re-check {len(locs)} member(s): {where}{fanout}")

    # Reverse-direction drift: a dedicated member changed while the contract stayed put
    # (behaviour shipped, spec not updated). Warn-only, --strict-promotable (ARCH-MEMBERDRIFT-027).
    memberlock = load_memberlock(reqs_dir)
    # sync/init on a full scan (no --since) needs this same full-member hash set again
    # below to re-baseline _memberlock.json — compute it once and hand it to member_drift
    # instead of hashing every dedicated member file twice in one invocation.
    _reuse_full_hashes = update_lock and members is full_members
    _full_member_hashes = compute_member_hashes(code_root, full_members) if _reuse_full_hashes else None
    for rid, rel in member_drift(reqs, members, lock, memberlock, code_root, current=_full_member_hashes):
        strict_warns.append(f"{rid}: MEMBER DRIFT — {rel} changed since lock but the contract "
                            "was not re-touched; re-check the requirement, or run sync to re-baseline")

    # Tracking guard (warn-only): a committed-by-design lock that exists on disk but is not
    # git-tracked silently disables drift detection in CI — a fresh checkout has no baseline,
    # so accumulated member drift goes unseen. Surface it so an uncommitted lock cannot hide.
    for lp_rel in untracked_locks(reqs_dir):
        warns.append(f"{lp_rel} exists on disk but is not git-tracked — `git add {lp_rel}` so "
                     "drift detection works in CI (an uncommitted lock is invisible to a fresh checkout)")

    # Doc-sync blind spot: a large docs/ HTML doc generated from requirements but with
    # no generated-from: lineage drifts from them unnoticed (warn-only — see ARCH-DOCBUNDLE-026).
    for rel in untagged_doc_bundles(code_root, full_members, reqs_dir):  # full set: a doc's generated-from membership is independent of the --since diff
        warns.append(f"{rel}: large docs/ HTML bundle ({DOC_BUNDLE_MIN_BYTES // 1000}KB+) has no "
                     "generated-from: tag — link it to the requirement(s) it derives from "
                     "(`<!-- generated-from: A, B -->`), or add it to .reqmapignore")

    # Members git does not track: the committed map records them, but a fresh checkout
    # has none, so the map cannot be reproduced and `map --check` fails in CI for a file
    # that is not in the repo. Warn-only and fail-open (silent outside a work tree), so a
    # consumer who deliberately tags an ignored file is nudged, not blocked.
    _untracked = untracked_members(code_root, full_members)   # implements: ARCH-TRACKED-042
    if _untracked:
        warns.append(
            "{} member(s) are not tracked by git: {} — the committed map records them, but a "
            "fresh checkout has no such file, so it cannot be regenerated there. Commit them, "
            "or exclude them in .reqmapignore.".format(
                len(_untracked), ", ".join(_untracked[:5])
                + ("" if len(_untracked) <= 5 else ", …")))

    # Tags the scan cannot see: a tag in a file type outside CODE_EXTS is not a member,
    # and until now nothing said so. Warn-only, fail-open outside a work tree.
    _unscanned = tagged_unscanned_files(code_root, reqs_dir)   # implements: ARCH-UNSCANNEDTAG-045
    if _unscanned:
        warns.append(
            "{} tag(s) in file type(s) the scan never reads: {} — those files are not members. "
            "Move the tag into a scannable file, or ask for the type to be added to the scan.".format(
                len(_unscanned), ", ".join(_unscanned[:5])
                + ("" if len(_unscanned) <= 5 else ", …")))

    # Coverage erosion: a sizeable program file with no requirement link implements
    # behavior no requirement describes. Plain warn — NEVER strict-promoted (the
    # ARCH-COVERAGE-029 Senate audit capped coverage at advisory).  # implements: ARCH-ORPHANCODE-034
    covered = {fp for hits in full_members.values() for (_role, fp, _ln) in hits}
    covered.update(fp for acs in ac_cover.values()
                   for locs in acs.values() for (fp, _ln) in locs)
    for rel in orphan_code_files(code_root, covered, reqs_dir):
        warns.append(f"{rel}: {ORPHAN_CODE_MIN_LOC}+-line code file has no membership tag — "
                     "link it (`# implements: <ID>`), draft a requirement for it "
                     "(`reqmap.py draft`), or add it to .reqmapignore")

    # Health signals (non-blocking): how much of the corpus is human-validated, and
    # how much still uses the legacy body schema. Surfaced so an all-baseline corpus
    # (drift fires only on `confirmed`, so the gate enforces nothing yet) and a
    # silently-inactive `findings` cannot be mistaken for a clean, enforcing SSOT.
    n_confirmed = sum(1 for r in reqs.values() if r["meta"].get("status") == "confirmed")
    legacy = [rid for rid in sorted(reqs)                       # implements: ARCH-ATOMICFORM-053
              if not _has_section(reqs[rid]["body"], "verify intent")
              and not _atomic_spans(reqs[rid]["body"])]           # atomic form has none by design
    if legacy:
        warns.append("{}/{} requirement(s) use the legacy schema (no '## Verify "
                     "intent' section) — `findings` is inactive for them: {}"
                     .format(len(legacy), len(reqs), ", ".join(legacy)))

    # depends_on cycles (warn-only): a cycle makes the dependency order unsatisfiable.
    # Warn and not error, deliberately: a dangling `depends_on` target is a typo with
    # one fix, while a cycle is a modelling call across several requirements — turning
    # it into an error would fail a build that was green yesterday, on an upgrade, with
    # no line of the consumer's own changed (ADR-0002).  # implements: ARCH-CHECK-006
    for _cyc in _dependency_cycles(reqs):
        warns.append("depends_on cycle: " + " -> ".join(_cyc)
                     + " — no requirement in a cycle can be built before the others; "
                       "drop the edge that closes it")

    # Map freshness (warn-only): the committed map is GENERATED from this registry, so
    # a requirement edit leaves it stale — and `gate` said nothing, so a consumer who
    # runs only `gate` before committing (what this repo's own docs tell them to do)
    # learns it from a red CI run. Reported here; still enforced by `map --check`.
    # Skipped under update_lock: `sync` regenerates the map moments later.
    if not update_lock:  # implements: ARCH-MAP-007
        try:
            stale_map = _stale_artifacts(
                # full_members, not the --since-filtered view: a scoped gate must not
                # report the map stale for members it deliberately did not look at.
                _assemble_map_data(reqs, full_members, reqs_dir, code_root, ac_cover),
                reqs_dir, code_root, reqs)
        except Exception:
            stale_map = []            # fail-open — a freshness probe never blocks the gate
        if stale_map:
            warns.append("committed map is stale: " + ", ".join(stale_map)
                         + " — run `reqmap.py sync` (or `map`) and commit the result")

    if strict:
        errors.extend(strict_warns)
    else:
        warns.extend(strict_warns)

    lock_blocked = False
    if update_lock:
        changed = [(rid, lock.get(rid), h)
                   for rid, h in sorted(new_lock.items()) if lock.get(rid) != h]
        removed = [rid for rid in sorted(lock) if rid not in new_lock]
        for rid, old_h, new_h in changed:
            old_short = old_h[:8] if old_h else "new"
            print(f"  lock update: {rid} hash changed ({old_short}->{new_h[:8]})")
        for rid in removed:
            print(f"  lock update: {rid} removed from lock")
        # sync drift guard: refuse to silently re-baseline an EDITED confirmed/implemented
        # contract unless the caller explicitly accepts it (accept_drift). A brand-new
        # requirement (old hash None) is not drift.  # implements: ARCH-CHECK-006
        confirmed_drift = [rid for (rid, old_h, _h) in changed
                           if old_h is not None
                           and reqs.get(rid, {}).get("meta", {}).get("status") in ("confirmed", "implemented")]
        if confirmed_drift and not accept_drift:
            lock_blocked = True
            print("Contract drift on confirmed requirements; re-run with --accept-drift "
                  "to advance the baseline:", file=sys.stderr)
            for rid in confirmed_drift:
                print(f"  drift: {rid}", file=sys.stderr)
        else:
            save_lock(reqs_dir, new_lock)
            # re-baseline reverse drift over the FULL member set — using the
            # --since-filtered `members` here would drop every unchanged member's
            # baseline and silently disable reverse-drift detection for them.
            # Reuse the hashes computed above when they cover the same full set.
            save_memberlock(reqs_dir, _full_member_hashes
                             if _full_member_hashes is not None
                             else compute_member_hashes(code_root, full_members))
            print("lock updated.")

    # Integration-artifact freshness: stale tool_definition.json or command-table region
    # in SKILL.universal.md means someone edited COMMANDS without running gen-integration.
    # Skipped silently when the artifacts don't exist (consumer/vendored repos).
    # Must run BEFORE the as_json early-return so --json (the CI/badge path) also
    # exits non-zero on a stale artifact.  # implements: ARCH-CMDREGISTRY-033
    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _stale = _check_integration_fresh(plugin_root)
    if _stale:
        errors = list(errors) + ["stale integration artifact(s): " + ", ".join(_stale)]

    if as_json:
        print(json.dumps({"ok": not (errors or lock_blocked), "errors": errors, "warnings": warns}))
        return 1 if (errors or lock_blocked) else 0

    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    if _stale:
        print("ERROR: stale generated integration artifact(s): " + ", ".join(_stale)
              + " — run `python scripts/reqmap.py gen-integration` and commit.", file=sys.stderr)

    n_find = sum(len(items) for _rid, _t, items in collect_findings(reqs))
    if n_find:
        print(f"info  {n_find} open verify-intent finding(s) — run `reqmap.py findings`")

    print(f"\n{len(reqs)} requirements ({n_confirmed} confirmed, {len(legacy)} legacy-schema), "
          f"{sum(len(v) for v in members.values())} members, "
          f"{len(errors)} errors, {len(warns)} warnings.")
    return 1 if (errors or lock_blocked) else 0


# Built-in scaffold so `new` needs no separate templates/ dir — the engine is
# self-contained (one file). An on-disk templates/requirement.md still overrides
# it when cmd_new is given a tmpl_path that exists.
REQUIREMENT_TEMPLATE = """\
---
id: AREA-NAME-NNN
status: draft        # draft | baseline | in-progress | implemented | confirmed | deprecated
layer: feature       # bus | feature | need | aggregate
owner: Alex
priority:            # must-have | should-have | could-have | wont-have (optional)
depends_on: []       # ids of bus/other capabilities this builds on
superseded_by:       # <ID>, if replaced
# level:             # optional: system | architecture | code — the V-model left arm.
#                    #   Adopting it turns on the level-fit and rung checks; a corpus
#                    #   that never sets it keeps the pre-V-model behaviour exactly.
# satisfies: []      # optional: the level above this one (system <- architecture <- code)
# area:              # optional: System Map grouping label (else the id prefix is used)
---

# Short name

## Description
> 1–3 plain sentences anyone can follow — what this is, why it exists, and what
> breaks without it. No jargon; this is the angle a non-expert reads first. The
> quote is rationale, not an obligation: it is not hashed and never trips drift.

Every bullet below is binding.
<!-- Audience: a first-year engineering student, new to this project. Six rules:
     1. Name the subject: "`init` creates the folder", never "It creates the folder".
     2. Present tense — no "shall", no "must". The line above already binds every clause.
     3. One binding statement per bullet, in at most three sentences; the extra
        sentences state the first's consequence, never a second obligation.
     4. Define project terms. Two or more: open with a glossary comment like this one.
     5. Group clauses past five, with bold labels (see below).
     6. Keep a clause to at most 3 sentences and 150 words — `lint` enforces both.
     Scope: one capability = one behavior that fails independently. Many clauses AND
     many acceptance criteria together mean several capabilities — split them
     (`lint` flags this as 'over-scoped'). -->

**What it does**
- `<subject>` does one thing, stated so a test could check it. No function names; true
  regardless of how the code is implemented.
  <!-- Rationale: why this specific behavior, one clause, only when not self-evident -->

**What it produces**
- `<subject>` returns <output shape and allowed values>.
- `<subject>` handles a missing or invalid optional input by <behavior>.

## Verify intent (open questions for the human)
- Observed: <a behavior that may be an AI accident — swallowed error, empty-string
  fallback, magic constant, unreachable branch>. Intended, or a bug to fix?

## Cases (= tests)
<!-- Keep Given/When/Then concrete and self-explanatory; spell out any term the
     Description introduced. -->
CASE-1  <!-- verifiable by: automated test | manual | inspection | load test -->
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>   (one test per case; each maps to tested-by)

## Context (non-binding)
<!-- Everything here is commentary: not hashed, not linted, never trips drift. On
     any conflict with the Description + Cases above, they win. Bold sub-labels
     are the same clause-group convention the Description uses (ADR-0017) — keep
     only the ones you need. -->
**Notes**
- A known fragility/footgun the implementer should know but which is NOT enforced.

**Example**
- e.g. Ana marks AUTH-001 confirmed, later edits its contract text; at commit
  `check` tells her "DRIFT — contract changed since lock" so she re-reviews.

**Current implementation**
- How the code does it today (the volatile narrative — may drift from the contract).

## Links
- Used by: (auto)
## Members in code (auto)
"""


def _warn_number_collision(reqs_dir, cap_id):  # implements: ARCH-NEW-004
    """Advisory: another requirement in the same area already uses this NNN. Ids are
    unique by their full text, so nothing breaks — but ARCH-MAP-007 beside
    ARCH-VIEWER-007 is the kind of pair people talk past each other about."""
    parts = cap_id.split("-")
    if len(parts) < 3:
        return
    area, num = parts[0], parts[-1]
    try:
        names = sorted(os.listdir(reqs_dir))
    except OSError:
        return
    for fn in names:
        if not fn.endswith(".md") or fn.startswith("_"):
            continue
        other = fn[:-3]
        op = other.split("-")
        if other != cap_id and len(op) >= 3 and op[0] == area and op[-1] == num:
            print("WARN  {} already uses number {} in area {} — ids stay unique by their full "
                  "text, but a distinct NNN keeps the two from being confused.".format(other, num, area))


def cmd_new(reqs_dir, tmpl_path, cap_id):  # implements: ARCH-NEW-004
    dest = os.path.join(reqs_dir, cap_id + ".md")
    if os.path.exists(dest):
        print(f"exists: {dest}"); return 1
    t = None
    if tmpl_path:                      # an on-disk template, if supplied, wins
        try:
            with open(tmpl_path, encoding="utf-8") as f:
                t = f.read()
        except OSError:
            t = None
    if t is None:                      # otherwise use the built-in scaffold
        t = REQUIREMENT_TEMPLATE
    t = t.replace("AREA-NAME-NNN", cap_id)
    os.makedirs(reqs_dir, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(t)
    print(f"created {dest}")
    _warn_number_collision(reqs_dir, cap_id)
    return 0


def cmd_promote_todo(reqs_dir, tmpl_path, name, cap_id, mark_done=False, root="."):  # implements: ARCH-PROMOTE-TODO-001
    """Scaffold a requirement draft from an unfinished TODO.md item (matched by name),
    seeding title / layer / milestone from the item. Requires an explicit cap_id — the
    engine runs headless (CI, pre-commit hook), so there is no interactive prompt. With
    mark_done it flips the matched TODO line to [x]; otherwise TODO.md is never touched."""
    if not cap_id:
        print('usage: reqmap new --from-todo "<todo name>" --id AREA-NAME-NNN [--mark-done]'); return 2
    key = name.strip().casefold()
    open_todos = [t for t in _parse_todos(root) if not t["done"]]
    matches = [t for t in open_todos if t["name"].strip().casefold() == key]
    if not matches:
        avail = "; ".join(t["name"] for t in open_todos) or "(none)"
        print(f"no open TODO named {name!r}. Open items: {avail}"); return 1
    if len(matches) > 1:
        where = ", ".join(t["milestone"] for t in matches)
        print(f"ambiguous: {len(matches)} open TODOs named {name!r} (milestones {where}) — rename to disambiguate")
        return 1
    todo = matches[0]
    dest = os.path.join(reqs_dir, cap_id + ".md")
    if os.path.exists(dest):
        print(f"exists: {dest}"); return 1
    t = None
    if tmpl_path:
        try:
            with open(tmpl_path, encoding="utf-8") as f:
                t = f.read()
        except OSError:
            t = None
    if t is None:
        t = REQUIREMENT_TEMPLATE
    layer = todo["lane"] if todo["lane"] in VALID_LAYER else "feature"   # 'ops' is a TODO lane, not a layer
    t = t.replace("AREA-NAME-NNN", cap_id)
    t = re.sub(r"(?m)^layer:\s*feature\b", f"layer: {layer}", t, count=1)
    # inject milestone at the template's anchor; if a custom template lacks it,
    # fall back to the frontmatter fence, else warn rather than silently drop it
    if "superseded_by:" in t:
        t = t.replace("superseded_by:", f"milestone: {todo['milestone']}\nsuperseded_by:", 1)
    elif t.startswith("---\n"):
        t = t.replace("---\n", f"---\nmilestone: {todo['milestone']}\n", 1)
    else:
        print(f"warning: template has no frontmatter anchor; milestone {todo['milestone']} not recorded")
    if "# Short name" in t:
        t = t.replace("# Short name", "# " + todo["name"], 1)
    else:
        print(f"warning: template has no '# Short name' title anchor; TODO title {todo['name']!r} not inserted")
    os.makedirs(reqs_dir, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(t)
    print(f"created {dest} (draft, milestone {todo['milestone']}, layer {layer}) from TODO {todo['name']!r}")
    _warn_number_collision(reqs_dir, cap_id)
    if mark_done:
        n = _mark_todo_done(root, todo["name"])
        print(f"marked TODO {todo['name']!r} done in TODO.md" if n
              else "warning: could not mark the TODO done (TODO.md not writable or line not found)")
    return 0


def _mark_todo_done(root, name):  # implements: ARCH-PROMOTE-TODO-001
    """Flip the first unfinished TODO.md line whose name matches to [x]. Best-effort:
    returns 1 if a line was rewritten, 0 if TODO.md is absent/unwritable or no line matched."""
    key = name.strip().casefold()
    for base in dict.fromkeys([root, os.path.dirname(os.path.abspath(root))]):
        path = os.path.join(base, "TODO.md")
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8", newline="") as f:
                lines = f.readlines()
        except OSError:
            continue          # unreadable here -> try the next candidate (parent), like _parse_todos
        changed = 0
        for i, line in enumerate(lines):
            m = re.match(r"^(\s*-\s+\[)[ ](\]\s+)(.+?)(\r?\n?)$", line)
            # rsplit on the LAST '|' to mirror _parse_todos_from_text's name
            # derivation — else a TODO whose name contains a '|' never matches
            if m and m.group(3).rsplit("|", 1)[0].strip().casefold() == key:
                lines[i] = m.group(1) + "x" + m.group(2) + m.group(3) + m.group(4)
                changed = 1
                break
        if changed:
            try:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.writelines(lines)
            except OSError:
                return 0
        return changed
    return 0


def _set_frontmatter_status(text, value):  # implements: ARCH-PROMOTE-011
    """Replace the value of the first `status:` line inside the leading frontmatter
    block, preserving its indentation and any trailing inline comment. Returns
    (new_text, n_replaced); n=0 when there is no frontmatter or no status line."""
    body = text.lstrip("﻿")            # drop a BOM if present (rewritten without it)
    if not body.startswith("---"):
        return text, 0
    end = body.find("\n---", 3)
    if end == -1:
        return text, 0
    head, rest = body[:end], body[end:]     # only the frontmatter block, never the body
    # Replace only the VALUE, keeping any trailing inline comment (and its spacing).
    # The value group excludes '#' so a blank `status:  # hint` line is filled in
    # place instead of swallowing the '#' as the value (which glued the leftover
    # comment text onto the status, corrupting the YAML).
    def _repl(m):
        comment = m.group(3)
        if comment:
            return m.group(1) + " " + value + (m.group(2) or "  ") + comment
        return m.group(1) + " " + value
    new_head, n = re.subn(
        r"(?m)^([ \t]*status[ \t]*:)[ \t]*[^#\r\n]*?([ \t]*)(#[^\r\n]*)?$",
        _repl, head, count=1)
    return new_head + rest, n


def cmd_promote(reqs, members, cap_id):  # implements: ARCH-PROMOTE-011
    """Flip a requirement's status to `confirmed` (the human-validation step) by a
    single frontmatter edit. Refuses if the requirement has no `implements:` member
    (a confirmed requirement must point to code — else the gate would error), and
    warns when no `tested-by:` member is linked."""
    r = reqs.get(cap_id)
    if not r:
        print(f"no requirement with id {cap_id} (expected requirements/{cap_id}.md)")
        return 1
    cur = r["meta"].get("status")
    if cur == "confirmed":
        print(f"{cap_id} is already confirmed.")
        return 0
    roles = [m[0] for m in members.get(cap_id, [])]
    meta = r["meta"]
    if _impl_exempt(meta):
        # `need`/`aggregate` are covered by an edge, not by a tag — the same exemption
        # the gate, `health` and the risk map already apply (_impl_exempt). The edge is
        # still checked, so the exemption is a different rule, not a hole: an aggregate
        # with no dependencies is exactly the orphan this refusal exists to catch.
        if meta.get("layer") == "aggregate" and not _as_list(meta.get("depends_on")):
            print(f"refusing: {cap_id} is `layer: aggregate` but its `depends_on` is empty — "
                  "an aggregate is implemented BY its dependencies; list them first.")
            return 1
    elif "implements" not in roles:
        print(f"refusing: {cap_id} has no `implements:` member — a confirmed requirement "
              f"must point to code. Tag the implementing code `# implements: {cap_id}` first.")
        return 1
    # newline="" on both ends: read/write the file's own line endings verbatim so a
    # CRLF-committed requirement file isn't silently flipped to LF on a POSIX host
    # (universal-newline translation on read + os.linesep on write would do exactly that).
    with open(r["path"], encoding="utf-8-sig", newline="") as f:
        raw = f.read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n") if eol == "\r\n" else raw
    # A module file holds several requirements; flip the status of THIS one, not of the
    # first block in the file. # implements: ARCH-MODULEFILE-056
    blocks = split_requirement_blocks(text)
    if len(blocks) > 1:
        idx = r.get("block", 0)
        blocks[idx], n = _set_frontmatter_status(blocks[idx], "confirmed")
        new_text = "".join(blocks)
    else:
        new_text, n = _set_frontmatter_status(text, "confirmed")
    if n == 0:
        print(f"could not find a `status:` line in {r['path']}")
        return 1
    if eol == "\r\n":
        new_text = new_text.replace("\n", "\r\n")
    with open(r["path"], "w", encoding="utf-8", newline="") as f:
        f.write(new_text)
    print(f"promoted {cap_id}: {cur or '(unset)'} -> confirmed")
    if _impl_exempt(meta):
        print(f"  note: `layer: {meta.get('layer')}` — covered by its "
              f"{'satisfies:' if meta.get('layer') == 'need' else 'depends_on'} edges, "
              "not by an implements: tag.")
        print("  next: reqmap.py sync")
        return 0
    if "tested-by" not in roles:
        print(f"  note: no `tested-by:` member — wire an acceptance test (`# tested-by: {cap_id}`) "
              f"or set `test_exempt: <reason>` to silence the untested signal.")
    print("  next: reqmap.py sync")
    return 0


def _draft_id(rel):  # implements: ARCH-EXTRACT-008
    """Mint a draft capability id from a file's relative path. Path-aware so
    same-basename files in different dirs don't collide; falls back to FILE when
    the name has no usable A-Z0-9 token (e.g. `_.py`, non-ASCII stems)."""
    slug = re.sub(r"[^A-Z0-9]+", "-", os.path.splitext(rel)[0].upper()).strip("-")
    return "DRAFT-" + (slug or "FILE")


def classify_prose(rel):  # implements: ARCH-PROSE-024
    """Bucket a POSIX-relative .md/.html path for the auto-draft path. Returns
    'ignore' (meta/boilerplate, invisible), 'sync_only' (README/docs/*.html — never
    drafted, but a drift- and semantic-checked member when explicitly tagged), or
    'capability' (prompt/spec prose — auto-drafted as a `draft` stub). Governs AUTO
    behavior only: scan_members still honors an explicit tag on any file."""
    base = os.path.basename(rel)
    # Bucket 1 — meta/boilerplate.
    if base in META_IGNORE_NAMES:
        return "ignore"
    if base == "LICENSE" or base.startswith("LICENSE."):
        return "ignore"
    if base.startswith("_"):                      # generated _map.*, _findings.md
        return "ignore"
    # Bucket 2 — sync-only.
    if base.upper() == "README" or base.upper().startswith("README."):   # readme.md is a README too
        return "sync_only"
    if rel == "docs" or rel.startswith("docs/"):
        return "sync_only"
    if rel.endswith(".html"):                      # all HTML is an overview/derived doc
        return "sync_only"
    # Bucket 3 — capability source (prompts/specs/modes and other prose .md).
    return "capability"


def _prose_facts(src):  # implements: ARCH-PROSE-024
    """(title, [headings]) from markdown/HTML prose, for a draft scaffold.
    Title: markdown frontmatter `title:`, else first `# ` H1, else <title>/<h1>.
    Headings: markdown `## ` H2 lines, else <h2>. Returns (None, []) when absent.
    The scaffold lists headings as an authoring hint — never the contract."""
    meta, body = parse_frontmatter(src)
    title = meta.get("title") or None
    headings, h1_sections = [], []
    for line in body.splitlines():
        s = line.strip()
        if title is None:
            m = re.match(r"#\s+(.+)", s)                      # markdown H1
            if m:
                title = m.group(1).strip()
                continue
            m = re.search(r"<(?:title|h1)[^>]*>(.*?)</(?:title|h1)>", s, re.I)
            if m:
                title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                # no continue: a line may carry both <title> and <h2> (see test_html_title_and_h2)
        m = re.match(r"##\s+(.+)", s)                         # markdown H2 (not H3)
        if m:
            headings.append(m.group(1).strip())
            continue
        m = re.match(r"#\s+(.+)", s)                          # a further H1: flat, single-level prose
        if m:
            h1_sections.append(m.group(1).strip())
            continue
        for inner in re.findall(r"<h2[^>]*>(.*?)</h2>", s, re.I):  # html H2
            headings.append(re.sub(r"<[^>]+>", "", inner).strip())
    # A prompt corpus (fabric: 255 files) writes every section as `# `: with no H2 at
    # all, the later H1s ARE the sections, and the hint would otherwise be empty.
    return title, (headings or h1_sections)


def cmd_extract(reqs, members, code_root, reqs_dir):  # implements: ARCH-EXTRACT-008  # implements: ARCH-PROSE-024
    """Propose DRAFT requirements for code files that have no member tag yet."""
    tagged = {fp for hits in members.values() for (_, fp, _) in hits}
    ignore = load_ignore(code_root, reqs_dir)   # honor .reqmapignore, same as scan
    proposed, used = 0, set()
    os.makedirs(reqs_dir, exist_ok=True)
    for dirpath, dirs, files in os.walk(code_root):
        _prune_dirs(dirpath, dirs, reqs_dir)   # skip noise + the SSOT output dir
        dirs.sort()                            # deterministic id/suffix assignment
        for fn in sorted(files):
            is_code = _is_code_file(fn) and not fn.endswith(PROSE_EXTS)
            is_prose = fn.endswith(PROSE_EXTS)
            if not (is_code or is_prose):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), code_root).replace(os.sep, "/")
            if any(fnmatch.fnmatch(rel, pat) for pat in ignore):  # ignored -> never draft
                continue
            if rel in tagged:
                continue
            if is_prose and classify_prose(rel) != "capability":
                continue                           # bucket 1/2 -> never auto-drafted
            cap = base = _draft_id(rel)
            k = 2
            while cap in used:                 # residual collision (case/ext only)
                cap = "{}-{}".format(base, k); k += 1
            used.add(cap)
            dest = os.path.join(reqs_dir, cap + ".md")
            if os.path.exists(dest):
                continue
            with open(os.path.join(dirpath, fn), encoding="utf-8", errors="ignore") as f:
                src = f.read()
            if is_prose:
                title, headings = _prose_facts(src)
                review = "REVIEW"   # intent is unrecoverable from prose — always author
                hint = "\n".join("  - {}".format(h) for h in headings) \
                    or "  - (no section headings detected)"
                # str.format (not f-string): the template embeds literal {cap}/{rel} inside backticked instructions
                with open(dest, "w", encoding="utf-8") as f:
                    f.write("---\nid: {cap}\nstatus: draft\nlayer: feature\n"
                            "owner: auto\ndepends_on: []\n"
                            "risk: 2  # REVIEW — prose capability, author the contract "
                            "before promoting\n---\n\n"
                            "# {title}\n\n"
                            "> DRAFT extracted from {rel} (prose capability). The source "
                            "prose is NOT the contract — author the normative behavior "
                            "below, then tag the source `# generated-from: {cap}` "
                            "(HTML: `<!-- generated-from: {cap} -->`) and promote.\n\n"
                            "## Description\n"
                            "Every bullet below is binding.\n"
                            "<!-- Name the subject, write in present tense, one statement per "
                            "bullet, at most 3 sentences and 150 words. -->\n"
                            "- TODO: the capability this prose defines (author from "
                            "intent, do not copy the prose).\n\n"
                            "## Verify intent (open questions for the human)\n"
                            "- TODO: which source sections are normative vs illustrative?\n\n"
                            "Source sections detected (authoring hint, not the contract):\n"
                            "{hint}\n\n"
                            "## Cases (= tests)\n"
                            "- TODO: Given/When/Then checks for the contract above.\n\n"
                            "## Context (non-binding)\n**Current implementation**\n- {rel}\n".format(
                                cap=cap, title=(title or os.path.splitext(fn)[0]),
                                rel=rel, hint=hint))
            else:
                risk = _risk(src)
                review = "REVIEW" if risk >= 2 else "auto-baseline"
                surface = _observed_surface(_file_facts(os.path.join(dirpath, fn), rel))
                with open(dest, "w", encoding="utf-8") as f:
                    # emission schema matches REQUIREMENT_TEMPLATE so a promoted draft
                    # needs no reshaping
                    f.write(f"---\nid: {cap}\nstatus: draft\nlayer: feature\n"
                            f"owner: auto\ndepends_on: []\n"
                            f"risk: {risk}  # {review} — author triage hint, not read by the engine\n---\n\n"
                            f"# {os.path.splitext(fn)[0]}\n\n"
                            f"> DRAFT extracted from {rel}. Describes observed behavior, "
                            f"not validated intent.\n\n"
                            f"## Description\n"
                            f"Every bullet below is binding.\n"
                            f"<!-- Name the subject, write in present tense, one statement per "
                            f"bullet, at most 3 sentences and 150 words. -->\n"
                            f"- TODO: the observed behavior (characterization — correctness UNVERIFIED).\n\n"
                            f"## Verify intent (open questions for the human)\n"
                            f"- TODO: anything that looks like an accident (swallowed error, magic "
                            f"constant, dead branch) — intended, or a bug to fix?\n\n"
                            f"## Cases (= tests)\n"
                            f"- characterization: current behavior captured, correctness UNVERIFIED\n\n"
                            f"## Context (non-binding)\n**Current implementation**\n- {rel}\n{surface}")
            proposed += 1
            print(f"{review:14} {cap}  <- {rel}")
    print(f"\n{proposed} draft requirements proposed. Review the REVIEW ones before promoting.")
    return 0


def _observed_surface(facts, limit=12):  # implements: ARCH-EXTRACT-008
    """Authoring hint for a code draft's Context/Current-implementation group: the
    module docstring's first line and the top-level signatures `plan` already knows
    how to read. Empty string when the language has no parser. Non-binding by
    construction — it lives under Context, never in the Contract, so a promoted
    draft still needs an authored contract."""
    sigs = list(facts.get("signatures") or [])
    doc = (facts.get("docstrings") or {}).get("module")
    if not sigs and not doc:
        return ""
    lines = ["", "Observed surface (auto, non-binding — an authoring hint, not the contract):"]
    if doc:
        lines.append("- module: {}".format(doc))
    lines += ["- `{}`".format(s) for s in sigs[:limit]]
    if len(sigs) > limit:
        lines.append("- … {} more".format(len(sigs) - limit))
    return "\n".join(lines) + "\n"


def _risk(src):  # implements: ARCH-EXTRACT-008
    score = 0
    if re.search(r"\b(TODO|FIXME|HACK|XXX)\b", src): score += 1
    if "# noqa" in src or "eslint-disable" in src: score += 1
    if len(src.splitlines()) > 300: score += 1
    return score


# ---------- candidates (capability extraction plan) ----------
# Stage 1 of AI extraction: gather the raw material an authoring step (a human or
# an LLM agent) needs to write a real, capability-level requirement. READ-ONLY —
# emits a JSON plan, writes NO .md, so it cannot repeat extract's empty-stub failure.
# Languages `plan` can read FACTS from (docstrings, signatures). Every scannable code
# file is a candidate regardless — three evidence runs (zlib: 0 candidates for 94 C
# files, gin: none for 99 Go files, awesome-compose: none for 35 Dockerfiles) showed
# a plan that silently omitted most of what `draft` then produced.
CANDIDATE_EXTS = (".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".mts", ".cts")
_TEST_DIR_NAMES = {"test", "tests", "spec", "specs", "__tests__", "testing", "e2e"}
_TEST_FILE_SUFFIXES = ("_test.py", "_test.go", "_test.rs", "_spec.rb", ".test.ts", ".test.tsx",
                       ".test.js", ".test.jsx", ".spec.ts", ".spec.tsx", ".spec.js", ".e2e.ts")


def _is_test_path(rel):  # implements: ARCH-CANDIDATES-009
    """Test code by convention (a `tests/` segment, `test_*.py`, `*_test.go`, `*.spec.ts`)."""
    parts = rel.replace(os.sep, "/").split("/")
    base = parts[-1]
    return (any(p in _TEST_DIR_NAMES for p in parts[:-1])
            or base.startswith("test_") or base.endswith(_TEST_FILE_SUFFIXES))
BUS_FANIN_THRESHOLD = 5      # a module this many capabilities depend on is bus-like
SPLIT_LOC_THRESHOLD = 300    # oversize file -> flag for human split, do not auto-split


def _py_facts(src):  # implements: ARCH-CANDIDATES-009
    """Module/symbol docstrings, top-level signatures and import targets via the
    stdlib `ast`. A SyntaxError/ValueError yields empty facts so one unparseable
    file (incl. a source with an embedded NUL byte, which ast.parse rejects with
    ValueError, not SyntaxError) never aborts the whole plan."""
    facts = {"signatures": [], "docstrings": {}, "imports": []}
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return facts
    mod_doc = ast.get_docstring(tree)
    if mod_doc:
        facts["docstrings"]["module"] = mod_doc.strip().splitlines()[0][:200]
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            facts["signatures"].append("def {}({})".format(
                node.name, ", ".join(a.arg for a in node.args.args)))
        elif isinstance(node, ast.ClassDef):
            facts["signatures"].append("class {}".format(node.name))
            # the public surface of a class-based module IS its methods (httpx's
            # _client.py hid 78 of them behind 3 module-level helpers)
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and not sub.name.startswith("_"):
                    facts["signatures"].append("def {}.{}({})".format(
                        node.name, sub.name, ", ".join(a.arg for a in sub.args.args if a.arg != "self")))
        else:
            continue
        d = ast.get_docstring(node)
        if d:
            facts["docstrings"][node.name] = d.strip().splitlines()[0][:200]
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imports.add(node.module.split(".")[0])
    facts["imports"] = sorted(imports)
    return facts


def _js_facts(src):  # implements: ARCH-CANDIDATES-009
    """Best-effort JS/TS facts via regex (no stdlib JS parser): the leading block
    comment as the module doc, and top-level function/binding names. Imports are
    not resolved for JS in v1 (the agent and _capmap.json fill that gap)."""
    facts = {"signatures": [], "docstrings": {}, "imports": []}
    # Leading block comment via plain string scan over a capped prefix — NOT a regex.
    # The old `/\*+(.*?)\*/` backtracks O(n^2) on a file opening with a long run of
    # `*` (a DoS on `candidates`); str.find is linear and cannot backtrack. The
    # leading `*`s of `/***` are stripped by the per-line `.strip(" *")` below.
    head_src = src[:8000].lstrip()
    if head_src.startswith("/*"):
        close = head_src.find("*/", 2)
        if close != -1:
            head = [ln.strip(" *") for ln in head_src[2:close].strip().splitlines()
                    if ln.strip(" *")]
            if head:
                facts["docstrings"]["module"] = head[0][:200]
    names = re.findall(r"(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)", src)
    names += re.findall(r"(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=", src)
    facts["signatures"] = list(dict.fromkeys(names))   # dedupe, keep order
    return facts


def _md_facts(src):  # implements: ARCH-CANDIDATES-009
    """Best-effort capability facts from a Markdown prompt/spec file (no parser):
    the first H1 (`# `) is the title, the first blockquote (`>`) AFTER that H1 is the
    intent, and each `## ` H2 heading is a structural-signature line. Free prose is
    never hashed — these facts only seed a human-authored requirement (Stage 2); the
    binding hash anchors on the authored Contract+Acceptance, like any code requirement."""
    facts = {"signatures": [], "docstrings": {}, "imports": []}
    title, intent, after_h1 = None, None, False
    for line in src.splitlines():
        s = line.strip()
        if title is None and s.startswith("# "):
            title = s[2:].strip(); after_h1 = True; continue
        if after_h1 and intent is None and s.startswith(">"):
            intent = s.lstrip(">").strip()
        if s.startswith("## "):
            facts["signatures"].append("## " + s[3:].strip())
    if title:
        facts["docstrings"]["title"] = title[:200]
    if intent:
        facts["docstrings"]["module"] = intent[:200]
    return facts


def _file_facts(path, rel):  # implements: ARCH-CANDIDATES-009
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            src = f.read()
    except OSError:
        return {"signatures": [], "docstrings": {}, "imports": [], "loc": 0}
    if rel.endswith(".py"):
        facts = _py_facts(src)
    elif rel.endswith(".md"):
        facts = _md_facts(src)
    elif rel.endswith(CANDIDATE_EXTS):
        facts = _js_facts(src)
    else:   # a candidate the engine has no parser for: still listed, facts empty
        facts = {"signatures": [], "docstrings": {}, "imports": []}
    facts["loc"] = len(src.splitlines())
    facts["signatures"] = facts["signatures"][:40]
    return facts


def _load_capmap(reqs_dir):  # implements: ARCH-CANDIDATES-009
    """Optional `requirements/_capmap.json`: a hand-authored capability grouping,
    authoritative when present. Shape: {"capabilities": [{id, layer, files:[...]}]}
    (a bare list is also accepted). Returns []; fail-open on absent/unreadable."""
    try:
        with open(os.path.join(reqs_dir, "_capmap.json"), encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    caps = data.get("capabilities", []) if isinstance(data, dict) else data
    out = []
    if isinstance(caps, list):
        for c in caps:
            if isinstance(c, dict) and c.get("id") and c.get("files"):
                out.append({"id": c["id"], "layer": c.get("layer"),
                            "files": [f.replace(os.sep, "/") for f in _as_list(c["files"])]})
    return out


def _mint_cap_id(rel):  # implements: ARCH-CANDIDATES-009
    """A TAG_RE-valid suggested id from a path stem (Stage 2 may rename it)."""
    slug = re.sub(r"[^A-Z0-9]+", "-", os.path.splitext(rel)[0].upper()).strip("-")
    return (slug or "MOD") + "-001"


def _collect_files(code_root, reqs_dir, md_globs=None):  # implements: ARCH-CANDIDATES-009
    """Sorted rel paths of candidate source files, honoring _prune_dirs (noise +
    the SSOT dir) and .reqmapignore — the same exclusions scan_members uses.

    `md_globs` is the opt-in, scope-bounding allowlist for non-code discovery: a
    `.md` file is included ONLY when it matches one of these globs (and is not
    ignored). Empty/None -> no `.md` is ever collected (behavior unchanged). The
    presence of a glob IS the opt-in; there is no separate on/off flag."""
    ignore = load_ignore(code_root, reqs_dir)   # match scan_members: look in requirements/ first
    md_globs = md_globs or []
    out = []
    for dirpath, dirs, files in os.walk(code_root):
        _prune_dirs(dirpath, dirs, reqs_dir)
        dirs.sort()
        for fn in sorted(files):
            rel = os.path.relpath(os.path.join(dirpath, fn), code_root).replace(os.sep, "/")
            if any(fnmatch.fnmatch(rel, pat) for pat in ignore):
                continue
            if _is_code_file(fn) and not fn.endswith(PROSE_EXTS):
                out.append(rel)
            elif fn.endswith(".md") and any(fnmatch.fnmatch(rel, g) for g in md_globs):
                out.append(rel)
    return out


def cmd_candidates(reqs, members, code_root, reqs_dir, out, md_globs=None):  # implements: ARCH-CANDIDATES-009
    """Emit a deterministic JSON capability-extraction plan and write NO .md.
    Grouping: authoritative `requirements/_capmap.json` when present, else one
    candidate per file (the Stage-2 agent merges/splits using judgment).
    `md_globs` opts non-code `.md` files (prompts, specs) into discovery — advisory
    only, never auto-written; a human authors + confirms each into the SSOT."""
    files = _collect_files(code_root, reqs_dir, md_globs)
    facts_by_file = {rel: _file_facts(os.path.join(code_root, rel), rel) for rel in files}

    tagged = {}   # file -> already-implemented requirement id (idempotency hint)
    for cap, hits in members.items():
        for role, fp, _ln in hits:
            if role == "implements":
                tagged.setdefault(fp, cap)

    # depends_on is resolved by matching an import name to a file STEM. Known
    # limitation (Stage-1 heuristic): an import that shadows a stdlib/3rd-party name
    # (e.g. `import json` next to a local json.py) or collides with a same-basename
    # file in another dir can yield a false edge — the Stage-2 author prunes these.
    stem_of = {os.path.splitext(os.path.basename(r))[0]: r for r in files}  # for depends_on

    # ----- grouping: _capmap.json wins; uncovered files fall back to one-per-file
    groups, claimed = [], set()
    for entry in _load_capmap(reqs_dir):
        present = [f for f in entry["files"] if f in facts_by_file]
        if present:
            groups.append({"id": entry["id"], "layer": entry.get("layer"), "files": present})
            claimed.update(present)
    # de-duplicate minted ids: two files sharing a slug (foo.py + foo.js, or
    # foo-bar + foo_bar) would otherwise mint the same id and conflate two
    # distinct candidates downstream — bump the numeric suffix on collision.
    # Seed from capmap groups AND existing requirement ids so a minted id never
    # duplicates a real requirement either.
    used_ids = {g["id"] for g in groups} | set(reqs)
    for rel in files:
        if rel in claimed:
            continue
        cid = _mint_cap_id(rel)
        if cid in used_ids:
            stem = cid[:-3]                 # _mint_cap_id always ends in "-001"
            n = 2
            while "{}{:03d}".format(stem, n) in used_ids:
                n += 1
            cid = "{}{:03d}".format(stem, n)
        used_ids.add(cid)
        groups.append({"id": cid, "layer": None, "files": [rel]})

    group_id_of_file = {f: g["id"] for g in groups for f in g["files"]}

    cands = []
    for g in groups:
        sigs, docs, imps, loc = [], {}, set(), 0
        my_stems = set()
        for f in g["files"]:
            ff = facts_by_file[f]
            sigs += ["{}: {}".format(f, s) for s in ff["signatures"]]
            for k, v in ff["docstrings"].items():
                docs["{}:{}".format(f, k)] = v
            imps.update(ff["imports"])
            loc += ff.get("loc", 0)
            my_stems.add(os.path.splitext(os.path.basename(f))[0])
        own = set(g["files"])
        deps = sorted({group_id_of_file[stem_of[m]] for m in imps
                       if m in stem_of and stem_of[m] not in own})
        tested_by = sorted(
            r for r in files
            if os.path.basename(r).startswith("test_")
            and os.path.splitext(os.path.basename(r))[0][len("test_"):] in my_stems)
        existing = next((tagged[f] for f in g["files"] if f in tagged), None)
        cands.append({
            "suggested_id": g["id"], "_layer": g["layer"], "files": g["files"],
            "docstrings": docs, "signatures": sigs[:60], "imports": sorted(imps),
            "depends_on": deps, "tested_by": tested_by, "loc": loc,
            "existing_req": existing, "split_candidate": loc > SPLIT_LOC_THRESHOLD,
            "is_test": bool(g["files"]) and all(_is_test_path(f) for f in g["files"]),
        })

    fanin = {}
    for c in cands:
        for d in c["depends_on"]:
            fanin[d] = fanin.get(d, 0) + 1
    for c in cands:
        n = fanin.get(c["suggested_id"], 0)
        c["importer_count"] = n
        c["suggested_layer"] = c.pop("_layer") or ("bus" if n >= BUS_FANIN_THRESHOLD else "feature")

    authored = sum(1 for c in cands if c["existing_req"])
    plan = {
        "engine_version": MAP_ENGINE_VERSION,
        # surfaces the unfilled-plan gap so an advisory plan nobody authored cannot
        # masquerade as coverage (with_existing_req = candidates already tagged in code)
        "coverage_summary": {"total_candidates": len(cands), "with_existing_req": authored},
        "lineage_note": ("A generated-from/implements tag records authoring lineage only; it "
                         "does NOT mean the requirement auto-tracks later edits to the source "
                         "file. Re-touch the requirement's Contract+Acceptance when the source's "
                         "behavior changes."),
        "bus": sorted(c["suggested_id"] for c in cands if c["suggested_layer"] == "bus"),
        "candidates": cands,
    }
    text = json.dumps(plan, indent=2, ensure_ascii=False)
    if out and out != "-":
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote {} ({} candidates)".format(out, len(cands)))
    else:
        print(text)
    return 0


# ---------- findings (open verify-intent items) ----------
FINDINGS_SIDECAR = "_findings_triage.json"
_SEV_RANK = {"high": 0, "medium": 1, "low": 2, "none": 3, "": 4}
_SEV_BADGE = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"}


def _req_title(body, rid):
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return rid


def collect_findings(reqs):  # implements: ARCH-FINDINGS-010
    """Per requirement, the open '## WHAT — Verify intent' bullets minus the
    'None - ...' placeholder. Returns [(rid, title, [item, ...]), ...] for reqs
    that have >=1 real finding, in id order. Deterministic; reads only the md."""
    out = []
    for rid in sorted(reqs):
        body = reqs[rid]["body"]
        items = [b for b in _bullets(body, "verify intent")
                 if b and not b.lstrip("*_ ").lower().startswith("none")]
        if items:
            out.append((rid, _req_title(body, rid), items))
    return out


def _render_findings_raw(groups, total):
    L = ["# Open findings", "",
         "> {} open verify-intent item(s) across {} requirement(s), aggregated from each "
         "requirement's `## WHAT — Verify intent` section by `reqmap.py findings`."
         .format(total, len(groups)),
         ">",
         "> These are open questions raised while reconstructing intent from code - NOT "
         "confirmed bugs. Resolve each by fixing the code or promoting the behavior into a "
         "Contract line. Run the AI triage pass (see SKILL.md) and drop a `{}` beside this "
         "file for a verified, prioritized view.".format(FINDINGS_SIDECAR),
         "", "---", ""]
    if not groups:
        L.append("_No open findings._")
        return "\n".join(L) + "\n", 0, 0
    for rid, title, items in groups:
        L.append("## {} - {}  ({})".format(rid, title, len(items)))
        L.append("")
        for it in items:
            L.append("- {}".format(it))
        L.append("")
    return "\n".join(L) + "\n", 0, 0


def _render_findings_triaged(triage, raw_total):
    items = [it for it in triage.get("items", []) if isinstance(it, dict)]
    buckets = {"REAL_BUG": [], "USER_DECISION": [], "INTENTIONAL": [], "FALSE_POSITIVE": []}
    for it in items:
        # an unknown/typo'd/missing classification folds into USER_DECISION rather
        # than landing in an orphan bucket that no block renders (silent loss). The
        # AI triage sidecar is LLM-authored, so an off-enum value is realistic.
        cls = it.get("classification")
        buckets[cls if cls in buckets else "USER_DECISION"].append(it)
    bugs = sorted(buckets.get("REAL_BUG", []),
                  key=lambda x: _SEV_RANK.get((x.get("severity") or "").lower(), 9))
    n = len(items)
    L = ["# Open findings - triaged", "",
         "> {} finding(s) classified: {} confirmed bug(s), {} product/config decision(s), "
         "{} intentional, {} false-positive. Source: `{}`{}."
         .format(n, len(bugs), len(buckets.get("USER_DECISION", [])),
                 len(buckets.get("INTENTIONAL", [])), len(buckets.get("FALSE_POSITIVE", [])),
                 FINDINGS_SIDECAR,
                 " (generated {})".format(triage["generated_at"]) if triage.get("generated_at") else "")]
    if raw_total and raw_total != n:
        L += [">", "> WARN  {} raw verify-intent item(s) currently in the requirements vs {} "
                   "triaged - re-run the AI triage pass to refresh.".format(raw_total, n)]
    L += ["", "---", ""]

    def block(title, rows, detail):
        L.append("## {} ({})".format(title, len(rows)))
        L.append("")
        for it in rows:
            rid = it.get("req_id", "?")
            sev = (it.get("severity") or "").lower()
            head = "**[{}] `{}`**".format(_SEV_BADGE[sev], rid) if (detail and sev in _SEV_BADGE) \
                else "**`{}`**".format(rid)
            L.append("- {} {}".format(head, it.get("finding", "")))
            if detail and it.get("location"):
                L.append("  - where: `{}`".format(it["location"]))
            if detail and it.get("fix"):
                L.append("  - fix: {}".format(it["fix"]))
        L.append("")

    if bugs:
        block("Confirmed bugs", bugs, True)
    if buckets.get("USER_DECISION"):
        block("Your call - config / product decisions", buckets["USER_DECISION"], True)
    if buckets.get("INTENTIONAL"):
        block("Intentional", buckets["INTENTIONAL"], False)
    if buckets.get("FALSE_POSITIVE"):
        block("False-positive", buckets["FALSE_POSITIVE"], False)
    return "\n".join(L) + "\n", n, len(bugs)


def _render_findings(reqs, reqs_dir, raw=False):  # implements: ARCH-FINDINGS-010
    """The `_findings.md` text and its counts, without writing anything. Shared by
    `findings` (which writes it) and `map --check` (which compares the committed
    copy against it). Returns (md, total, n_groups, used_triage, n_tri, n_bugs)."""
    groups = collect_findings(reqs)
    total = sum(len(items) for _rid, _t, items in groups)

    triage = None
    if not raw:
        sidecar = os.path.join(reqs_dir, FINDINGS_SIDECAR)
        if os.path.exists(sidecar):
            try:
                with open(sidecar, encoding="utf-8") as f:
                    triage = json.load(f)
            except (json.JSONDecodeError, OSError):
                triage = None

    if triage and isinstance(triage.get("items"), list):
        md, n_tri, n_bugs = _render_findings_triaged(triage, total)
        used_triage = True
    else:
        md, n_tri, n_bugs = _render_findings_raw(groups, total)
        used_triage = False
    return md, total, len(groups), used_triage, n_tri, n_bugs


def cmd_findings(reqs, reqs_dir, raw=False):  # implements: ARCH-FINDINGS-010
    """Aggregate every requirement's open verify-intent items into
    requirements/_findings.md. If a `_findings_triage.json` sidecar exists (and
    --raw is off), render the verified, classified view from it instead; else the
    raw grouped list. Stdlib-only: the AI triage that produces the sidecar lives
    in the skill, not here (same split as candidates vs AI-authoring)."""
    md, total, n_groups, used_triage, n_tri, n_bugs = _render_findings(reqs, reqs_dir, raw)
    os.makedirs(reqs_dir, exist_ok=True)
    out = os.path.join(reqs_dir, "_findings.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    # gate the suffix on the renderer actually used — a malformed sidecar that is
    # truthy but whose `items` is not a list falls back to raw, so don't claim a
    # triage view was rendered
    extra = ", {} triaged, {} confirmed bug(s)".format(n_tri, n_bugs) if used_triage else ""
    print("{} open finding(s) across {} requirement(s){} -> {}"
          .format(total, n_groups, extra, out))
    return 0


# ---------- map (HTML) ----------
def _attach_ac_coverage(node, body, covered):  # implements: ARCH-ACVERIFY-019
    """Add `clauses` / `covered` / `gap` to a node, but ONLY when the requirement has
    adopted per-AC tagging: it labels criteria AND at least one carries a `verifies:`
    tag. Absent means "not measured", and every reader must render it as such.

    The viewer used to invent the pair when it was absent — `clauses` from the number
    of CONTRACT lines, `covered` all-or-nothing from the tested-by badge — so a
    requirement with three real tests read "0 / 8 clauses covered" and sent its owner
    on an investigation. A number nobody computed is worse than no number."""
    labels = [b["label"] for b in _acc_blocks(body) if b["label"] and not b["manual"]]
    if not labels or not covered:
        return
    missing = [ac for ac in labels if ac not in covered]
    node["clauses"] = len(labels)
    node["covered"] = len(labels) - len(missing)
    if missing:
        node["gap"] = "no `verifies:` tag for " + ", ".join(missing)


def _build_map_data(reqs, members, ac_cover=None):  # implements: ARCH-MAP-007
    """Assemble the {nodes, edges} registry graph that drives every rendered
    surface (HTML map, Mermaid blocks, and the JSON export). Pure: no IO.

    `ac_cover` ({id: {AC-N: [...]}}, from `scan_ac_verifies`) is what turns the
    per-criterion coverage the gate already computes into something the viewer can
    render honestly; omitted, the coverage fields are simply absent."""
    used_by = {rid: [] for rid in reqs}
    for rid, r in reqs.items():
        for dep in _as_list(r["meta"].get("depends_on")):
            if dep in used_by:
                used_by[dep].append(rid)
    satisfied_by = {rid: [] for rid in reqs}  # reverse upstream edges  # implements: ARCH-TRACE-020
    for rid, r in reqs.items():
        for up in _as_list(r["meta"].get("satisfies")):
            if up in satisfied_by:
                satisfied_by[up].append(rid)
    data = {"nodes": [], "edges": [], "upstream_edges": []}
    for rid, r in reqs.items():
        m = r["meta"]
        data["nodes"].append({
            "id": rid, "layer": m.get("layer", "feature"),
            "level": m.get("level"),                       # implements: ARCH-LEVEL-051
            "status": m.get("status", "draft"),
            "area": (m.get("area") or "").strip() or _area_of(rid),
            "title": _title(r["body"]),
            "intent": _first_quote(r["body"]),
            # new emission schema (Contract / Verify-intent / Notes / Current-impl)
            "contract": _from_any(_bullets, r["body"], CONTRACT_LABELS),
            "verify": _bullets(r["body"], "verify intent"),
            # legacy per-topic heading first; ADR-0017's consolidated Context section
            # (bold **Notes**/**Current implementation** sub-groups) is the fallback,
            # never both at once in one file, so this never masks real content.
            "notes": _bullets(r["body"], "notes") or _context_group(r["body"], "notes"),
            "current_impl": (_bullets(r["body"], "current implementation")
                              or _context_group(r["body"], "current implementation")),
            "acc": _acc_items(r["body"]),                    # AC blocks AND bullets
            "accept": _from_any(_section_raw, r["body"], ACCEPTANCE_LABELS),  # raw, line breaks kept
            # legacy schema (Input / Description / Output) — kept so old docs still render
            "input": _section(r["body"], "input"),
            "output": _section(r["body"], "output"),
            # Only the legacy Input/Description/Output triad, never the current
            # `## Description` — which is the Contract and is emitted above.
            "desc": (_section(r["body"], "description")
                     if _has_any(r["body"], ("input", "output")) else ""),
            "deps": _as_list(m.get("depends_on")),
            "used_by": used_by.get(rid, []),
            "satisfies": _as_list(m.get("satisfies")),       # upstream needs this fulfils
            "satisfied_by": satisfied_by.get(rid, []),       # requirements fulfilling this need
            "members": [{"role": x[0], "loc": f"{x[1]}:{x[2]}"} for x in members.get(rid, [])],
            "test_exempt": m.get("test_exempt"),
            "milestone": m.get("milestone"),
            "priority": m.get("priority", ""),
            "risks": [{"signal": s, "advice": RISK_ADVICE[s]} for s in _risk_signals(
                {"status": m.get("status", "draft"), "layer": m.get("layer", "feature"),
                 "members": members.get(rid, []),
                 "verify": _bullets(r["body"], "verify intent"), "test_exempt": m.get("test_exempt")})],
        })
        _attach_ac_coverage(data["nodes"][-1], r["body"], (ac_cover or {}).get(rid, {}))
    for rid, r in reqs.items():
        for dep in _as_list(r["meta"].get("depends_on")):
            if dep in reqs:                    # skip dangling targets — no phantom node
                data["edges"].append([rid, dep])
        for up in _as_list(r["meta"].get("satisfies")):  # implements: ARCH-TRACE-020
            if up in reqs:
                data["upstream_edges"].append([rid, up])
    return data


def _roadmap_signals(root):  # implements: ARCH-ROADMAP-038
    """Read TODO.md and report two read-only roadmap signals, or None when the file
    is absent (most repos have no TODO.md, and they must see nothing).

    Returns {"newest_milestone": "vX.Y" or None, "unversioned_headings": [str]}.

    `unversioned_headings` is the one that bites. `_parse_todos_from_text` keeps the
    CURRENT milestone when a `## ` heading does not start with a version, so items
    under such a heading are silently attributed to the section above instead of being
    skipped. A cosmetic rename therefore mis-files entries with no visible error."""
    for base in dict.fromkeys([root, os.path.dirname(os.path.abspath(root))]):
        path = os.path.join(base, "TODO.md")
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            return None
        versions, bad = [], []
        for line in text.splitlines():
            s = line.strip()
            if not s.startswith("## "):
                continue
            m = re.match(r"^##\s+(v\d[\d.]*)\b", s)
            if m:
                versions.append(m.group(1))
            else:
                bad.append(s[3:].strip())
        newest = max(versions, key=_version_key) if versions else None
        return {"newest_milestone": newest, "unversioned_headings": bad}
    return None


def _version_key(v):  # implements: ARCH-ROADMAP-038
    """Sort key for a `vX.Y.Z` string: compare numerically per segment, so v2.10
    sorts above v2.9 where a string compare would not."""
    return tuple(int(p) for p in v.lstrip("v").split(".") if p.isdigit())


def _parse_todos_from_text(text):
    """Parse TODO.md content → list of {name, lane, milestone, done} dicts. Pure.
    Items before the first ## vX.Y heading are silently ignored (milestone is required)."""
    todos, current_ms = [], None
    for line in text.splitlines():
        # match the version token at the heading start; a trailing annotation
        # like `## v2.8 (deferred — demand-gated)` is harmless (the capture group
        # isolates the version) and must not drop the milestone's items.
        ms_m = re.match(r"^##\s+(v\d[\d.]*)\b", line.strip())
        if ms_m:
            current_ms = ms_m.group(1)
            continue
        item_m = re.match(r"^-\s+\[([ xX])\]\s+(.+)$", line.strip())
        if item_m and current_ms:
            done = item_m.group(1).lower() == "x"
            rest = item_m.group(2)
            if "|" in rest:
                name_part, meta = rest.rsplit("|", 1)
                name = name_part.strip()
                lane_m = re.search(r"lane:\s*(\w+)", meta)  # lane must be a single word (bus|feature|ops)
                lane = lane_m.group(1) if lane_m else "feature"
            else:
                name, lane = rest.strip(), "feature"
            todos.append({"name": name, "lane": lane, "milestone": current_ms, "done": done})
    return todos


def _parse_todos(root):
    """Read TODO.md; tries root first, then one level up (covers plugin/ dogfood layout).
    Returns list of todo dicts; empty list if absent in both locations."""
    for base in dict.fromkeys([root, os.path.dirname(os.path.abspath(root))]):
        path = os.path.join(base, "TODO.md")
        try:
            with open(path, encoding="utf-8") as f:
                return _parse_todos_from_text(f.read())
        except OSError:
            continue
    return []


# ---------------------------------------------------------------------------
# Content translation (`translate`) — implements: ARCH-TRANSLATE-044
#
# Manual and opt-in only. NOTHING in this block is called from gate/sync/lint/
# map/the pre-commit hook — `translate` is reached exclusively by typing
# `reqmap.py translate`. That is deliberate: it is the only subcommand that
# shells out to an external LLM CLI, and this engine's gate/sync/CI path must
# stay usable on a machine that has never heard of `claude`. `map`/`export`
# below only ever READ an already-committed cache file — never the CLI — so
# they stay exactly as deterministic as before this block existed.
# ---------------------------------------------------------------------------
TRANSLATOR_VERSION = "1"   # bump to invalidate every cached translation at once
                           # (e.g. after changing _TRANSLATE_PROMPT or the model)

_RO_DIACRITICS = "ăâîșțĂÂÎȘȚ"
# Small, deliberately generic stopword lists — this is a majority-vote signal over
# a whole corpus, not a per-sentence classifier, so it does not need to be exhaustive.
_RO_STOPWORDS = frozenset({
    "și", "este", "sunt", "pentru", "care", "această", "acest", "aceste", "dacă",
    "sau", "din", "cu", "la", "de", "un", "o", "nu", "se", "fi", "prin", "între",
    "toate", "fiecare", "asupra", "unde", "cum", "atunci", "fără", "după",
})
_EN_STOPWORDS = frozenset({
    "the", "and", "is", "are", "for", "this", "that", "with", "from", "not",
    "be", "to", "of", "in", "on", "a", "an", "when", "where", "each", "every",
    "without", "after", "then", "if", "or",
})


def _strip_code(text):  # implements: ARCH-TRANSLATE-044
    """Drop fenced code blocks and inline `backticked` spans before a prose scan —
    an identifier's language must never sway a language-detection heuristic."""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    return re.sub(r"`[^`]*`", " ", text)


def detect_lang(text):  # implements: ARCH-TRANSLATE-044
    """RO/EN classifier over prose stripped of code spans. Romanian diacritics are a
    near-certain signal; below that, whichever stopword list scores more hits wins.
    Returns 'ro', 'en', or None when neither signal fires (too little prose, or a
    requirement that is nearly all code/identifiers) — None means 'undetermined',
    not 'English'."""
    bare = _strip_code(text)
    if any(ch in bare for ch in _RO_DIACRITICS):
        return "ro"
    words = [w.lower() for w in _WORD_RE.findall(bare)]
    ro_hits = sum(1 for w in words if w in _RO_STOPWORDS)
    en_hits = sum(1 for w in words if w in _EN_STOPWORDS)
    if ro_hits == 0 and en_hits == 0:
        return None
    return "ro" if ro_hits > en_hits else "en"


def _translation_source_text(body, title):  # implements: ARCH-TRANSLATE-044
    """The exact span that gets translated and hashed: title + WHY + Contract +
    Acceptance. Deliberately wider than binding_hash() (Contract+Acceptance only) —
    a title-only edit must also invalidate a cached translation."""
    return "\n".join([
        title, _first_quote(body),
        _from_any(_section_raw, body, CONTRACT_LABELS),
        _from_any(_section_raw, body, ACCEPTANCE_LABELS),
    ])


def translation_hash(body, title):  # implements: ARCH-TRANSLATE-044
    """Cache-invalidation key for one requirement's translation. NOT binding_hash() —
    see _translation_source_text. Includes TRANSLATOR_VERSION so bumping the prompt
    or the model invalidates every cached entry in one step, not file-by-file."""
    h = hashlib.sha256()
    h.update(_translation_source_text(body, title).encode("utf-8"))
    h.update(TRANSLATOR_VERSION.encode("utf-8"))
    return h.hexdigest()[:12]


def _effective_lang(r):  # implements: ARCH-TRANSLATE-044
    """A requirement's language: an explicit `lang: ro|en` frontmatter override wins;
    otherwise it is detected from the translated span. The override is the escape
    hatch for the rare file the heuristic gets wrong (e.g. a Romanian requirement
    whose Contract is mostly backticked English identifiers)."""
    override = (r["meta"].get("lang") or "").strip().lower()
    if override in ("ro", "en"):
        return override
    return detect_lang(_translation_source_text(r["body"], _title(r["body"])))


def corpus_lang(reqs):  # implements: ARCH-TRANSLATE-044
    """Majority language across the whole corpus (per-file lang: override honored
    first). Returns 'ro' or 'en'; None only when every file is undetermined (e.g.
    an empty registry) — never guessed."""
    counts = {"ro": 0, "en": 0}
    for r in reqs.values():
        lang = _effective_lang(r)
        if lang in counts:
            counts[lang] += 1
    if counts["ro"] == 0 and counts["en"] == 0:
        return None
    return "ro" if counts["ro"] >= counts["en"] else "en"


def _structural_signature(text):  # implements: ARCH-TRANSLATE-044
    """(backtick-span multiset, numeric-literal multiset, ordered structural markers,
    ordered `AC-N` labels, Gherkin-keyword multiset) — what a translation must preserve
    exactly. Used to gate a cache write: a translation that drops a backticked identifier
    or a number is a mistranslation of normative text, not a style choice.

    The last two are identifiers, not prose, and the first three checks are blind to both:
    `AC-1` -> `CA-1` keeps the same digit and is neither heading nor bullet, and
    `Given` -> `Dat fiind` touches nothing at all. But `AC-N` is what a test points at
    (`# verifies: <ID>#AC-N`), and Given/When/Then are engine vocabulary the viewer
    highlights — the same reason `confirmed` and `draft` are left untranslated (i18n.jsx).
    A reader given "Dat fiind" cannot match the criterion back to the .md file of record."""
    backticks = tuple(sorted(re.findall(r"`[^`]*`", text)))
    numbers = tuple(sorted(re.findall(r"\d+(?:[.,]\d+)?", text)))
    markers = tuple(re.findall(r"^(#{1,6}\s|-\s|\d+\.\s)", text, flags=re.MULTILINE))
    labels = tuple(re.findall(r"^\s*((?:CASE|AC)-\d+)\b", text, flags=re.MULTILINE))
    keywords = tuple(sorted(re.findall(r"\b(?:Given|When|Then)\b", text)))
    return (backticks, numbers, markers, labels, keywords)


def _translation_preserves_structure(source, translated):  # implements: ARCH-TRANSLATE-044
    return _structural_signature(source) == _structural_signature(translated)


_LANG_NAMES = {"ro": "Romanian", "en": "English"}
_TRANSLATE_MARKERS = ("TITLE", "INTENT", "CONTRACT", "ACCEPTANCE")
_TRANSLATE_PROMPT = (
    "Translate the following software requirement from {src} to {dst}. This is a "
    "technical, normative document - preserve meaning exactly. Keep all markdown "
    "formatting, every backticked `identifier` verbatim and unchanged, every number "
    "unchanged, and the same list/heading structure line for line.\n"
    "Two more things are identifiers, not prose, and must appear verbatim: the "
    "criterion labels `CASE-1`, `CASE-2`, ... (a test refers to one by name), and the "
    "Gherkin keywords Given / When / Then. Translate the words after them, never "
    "the keywords themselves.\n\n"
    "Return EXACTLY four sections, each starting on its own line with the literal "
    "marker shown below, and nothing else - no commentary, no code fence:\n"
    "===TITLE===\n<translated title>\n"
    "===INTENT===\n<translated intent>\n"
    "===CONTRACT===\n<translated contract>\n"
    "===ACCEPTANCE===\n<translated acceptance>\n\n"
    "--- SOURCE ---\n"
    "===TITLE===\n{title}\n"
    "===INTENT===\n{intent}\n"
    "===CONTRACT===\n{contract}\n"
    "===ACCEPTANCE===\n{acceptance}\n"
)


def _parse_translated_sections(text):  # implements: ARCH-TRANSLATE-044
    """Split the model's marker-delimited response into {title, intent, contract,
    acceptance}. Returns None on any malformed response (a missing marker) — a
    partial parse is never used, only all four fields or none."""
    pattern = "(%s)" % "|".join("===%s===" % m for m in _TRANSLATE_MARKERS)
    chunks = re.split(pattern, text)
    parts, current = {}, None
    for chunk in chunks:
        m = re.match(r"===(\w+)===$", chunk)
        if m:
            current = m.group(1)
            continue
        if current:
            parts[current] = chunk.strip()
            current = None
    if not all(m in parts for m in _TRANSLATE_MARKERS):
        return None
    return {k.lower(): parts[k] for k in _TRANSLATE_MARKERS}


def _run_claude_translate(title, intent, contract, acceptance, src_lang, dst_lang):  # implements: ARCH-TRANSLATE-044
    """Invoke `claude -p` once per requirement and parse its four-section response.
    Returns {title, intent, contract, acceptance} on success, or None on ANY
    failure — CLI missing, non-zero exit, timeout, or a malformed response. The
    caller treats None as 'skip this entry', never as an error to propagate: this
    is the fail-open boundary between an optional external tool and everything
    else in the engine."""
    prompt = _TRANSLATE_PROMPT.format(
        src=_LANG_NAMES[src_lang], dst=_LANG_NAMES[dst_lang],
        title=title, intent=intent, contract=contract, acceptance=acceptance)
    try:
        # The prompt travels on stdin, not argv: a whole requirement in one argument
        # would hit Windows' ~32k command-line ceiling on a large corpus.
        proc = subprocess.run(
            ["claude", "-p"], input=prompt,
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    return _parse_translated_sections(proc.stdout)


def cmd_translate(reqs, reqs_dir, target=None):  # implements: ARCH-TRANSLATE-044
    """Translate every requirement written in the corpus's detected majority
    language into `target` (default: the other of {ro, en}), caching results in
    requirements/_i18n/<target>.json. Manual and opt-in — see the module-level
    comment above this block. Fails open per entry: a missing/erroring `claude`
    CLI, a timeout, or a translation that fails the structural-fidelity check is
    skipped with a warning; it never aborts the batch or raises. Cache hits (hash
    unchanged since the last successful translation) are skipped without calling
    the CLI. Always exits 0 — this is a report-and-cache tool, never a gate."""
    src = corpus_lang(reqs)
    if src is None:
        print("translate: no requirements to classify - nothing to do.")
        return 0
    dst = target or ("en" if src == "ro" else "ro")
    if dst == src:
        print("translate: target '{}' matches the corpus's detected language "
              "'{}' - nothing to translate.".format(dst, src))
        return 0

    cache_path = os.path.join(reqs_dir, "_i18n", "{}.json".format(dst))
    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, encoding="utf-8") as f:
                cache = json.load(f)
        except (OSError, ValueError):
            cache = {}

    translated = cached = skipped = 0
    for rid, r in sorted(reqs.items()):
        if _effective_lang(r) != src:
            continue   # already in the target language (or undetermined) - leave it
        title = _title(r["body"])
        intent = _first_quote(r["body"])
        contract = _from_any(_section_raw, r["body"], CONTRACT_LABELS)
        acceptance = _from_any(_section_raw, r["body"], ACCEPTANCE_LABELS)
        h = translation_hash(r["body"], title)
        entry = cache.get(rid)
        if entry and entry.get("hash") == h:
            cached += 1
            continue
        parsed = _run_claude_translate(title, intent, contract, acceptance, src, dst)
        if parsed is None:
            print("  WARN  {}: claude CLI unavailable, failed, or returned a "
                  "malformed response - skipped".format(rid))
            skipped += 1
            continue
        source_text = "\n".join([title, intent, contract, acceptance])
        translated_text = "\n".join([parsed["title"], parsed["intent"],
                                      parsed["contract"], parsed["acceptance"]])
        if not _translation_preserves_structure(source_text, translated_text):
            print("  WARN  {}: translation failed the structural-fidelity check "
                  "(backtick/number/heading mismatch) - skipped".format(rid))
            skipped += 1
            continue
        cache[rid] = dict(parsed, hash=h)
        translated += 1

    if translated:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2, sort_keys=True)
        print("wrote {}".format(cache_path))
    print("translate: {} translated, {} cache hit, {} skipped ({} -> {})".format(
        translated, cached, skipped, src, dst))
    return 0


def _load_translations(reqs, reqs_dir):  # implements: ARCH-TRANSLATE-044
    """Read every requirements/_i18n/<locale>.json cache file and return
    {rid: {locale: {title, intent, contract, acceptance}}} for entries whose
    stored hash still matches the requirement's CURRENT content. A stale entry
    (source edited since the last `translate` run) is silently dropped rather
    than served — this is what keeps `map`/`map --check` deterministic and
    `claude`-free: they only ever read a file already sitting on disk, and they
    never serve a translation known to be out of date."""
    i18n_dir = os.path.join(reqs_dir, "_i18n")
    if not os.path.isdir(i18n_dir):
        return {}
    out = {}
    for fname in sorted(os.listdir(i18n_dir)):
        if not fname.endswith(".json"):
            continue
        locale = fname[:-len(".json")]
        try:
            with open(os.path.join(i18n_dir, fname), encoding="utf-8") as f:
                cache = json.load(f)
        except (OSError, ValueError):
            continue
        for rid, entry in cache.items():
            r = reqs.get(rid)
            if not r or not isinstance(entry, dict):
                continue
            title = _title(r["body"])
            if entry.get("hash") != translation_hash(r["body"], title):
                continue
            out.setdefault(rid, {})[locale] = {
                k: entry.get(k, "") for k in ("title", "intent", "contract", "acceptance")
            }
    return out


def _attach_translations(data, reqs, reqs_dir):  # implements: ARCH-TRANSLATE-044
    """Mutate data['nodes'] in place, adding node['i18n'] = {locale: {...}} for
    any node with a fresh cached translation. Shared by cmd_map and cmd_export
    so both emit the same graph — no `claude` call here, file reads only."""
    i18n = _load_translations(reqs, reqs_dir)
    for node in data["nodes"]:
        if node["id"] in i18n:
            node["i18n"] = i18n[node["id"]]
    return data


def cmd_map(reqs, members, reqs_dir, root=".", check=False, ac_cover=None):  # implements: ARCH-MAP-007
    data = _assemble_map_data(reqs, members, reqs_dir, root, ac_cover)

    if check:
        return _map_check(data, reqs_dir, root, reqs)

    md_out   = render_md(data, reqs_dir)
    json_out = render_json(data, reqs_dir)
    html_out = render_html(data, reqs_dir)
    print("wrote {}".format(md_out))
    print("wrote {}".format(json_out))
    if html_out:
        print("wrote {}".format(html_out))
        docs_out = _docs_publish_path(root)  # implements: ARCH-PAGES-021
        if docs_out:
            with open(html_out, "rb") as src, open(docs_out, "wb") as dst:
                dst.write(src.read())
            print("wrote {}".format(docs_out))
    print("({} nodes, {} edges)".format(len(data["nodes"]), len(data["edges"])))
    if os.path.exists(os.path.join(reqs_dir, "_findings.md")):  # implements: ARCH-FINDINGS-010
        cmd_findings(reqs, reqs_dir)   # a committed report follows the requirements it summarizes
    return 0


def _assemble_map_data(reqs, members, reqs_dir, root=".", ac_cover=None):  # implements: ARCH-MAP-007
    """The graph plus the three fields every rendered surface needs on top of it
    (repo, todos, translations). One assembler, so `map`, `export` and the gate's
    freshness probe cannot build three subtly different documents and disagree about
    which one is stale."""
    if ac_cover is None:
        # `init` and any embedding caller pass none; computing it here (instead of
        # emitting a coverage-less map) keeps every writer of _map.json byte-identical,
        # so `map --check` cannot flag a map as stale merely because a different
        # command wrote it.
        ac_cover = scan_ac_verifies(root, reqs_dir)
    data = _build_map_data(reqs, members, ac_cover)
    data["repo"] = _repo_name(root)
    data["todos"] = _parse_todos(root)
    _attach_translations(data, reqs, reqs_dir)
    return data


def cmd_export(reqs, members, reqs_dir, root=".", out=None, ac_cover=None):  # implements: ARCH-MAP-007
    """Emit the registry graph as JSON for an external front-end to consume.
    Same {nodes, edges} shape that drives the map; '-' = stdout, --out PATH, or
    requirements/_map.json by default."""
    data = _assemble_map_data(reqs, members, reqs_dir, root, ac_cover)
    text = _build_json_text(data)
    target = out if out else os.path.join(reqs_dir, "_map.json")
    if target == "-":
        print(text)
        return 0
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote {} ({} nodes, {} edges)".format(target, len(data["nodes"]), len(data["edges"])))
    return 0


def _risk_score(meta):  # implements: ARCH-NEXT-013
    """Extract's per-file risk hint (0-3) from frontmatter, or 0 when absent /
    unparseable. Used only to float REVIEW-flagged drafts to the top of a bucket —
    never to gate. Hand-authored requirements have no `risk:` field -> 0."""
    try:
        return int(str(meta.get("risk")).strip())
    except (TypeError, ValueError):
        return 0


_PRIORITY_ORDER = {"must-have": 0, "should-have": 1, "could-have": 2, "wont-have": 3}


def _recorded_members(reqs_dir, ids):  # implements: ARCH-NEXT-013
    """{id: first member loc} from the committed `_map.json`, for those of `ids` whose
    node records a member there. The narrow default scan (no --code) cannot see a
    member outside its root, so a requirement lands in Orphans while the committed
    map proves it has code — this is what turns that into a hint instead of a
    puzzle. Fail-open ({}) when the map is absent or unreadable."""
    try:
        with open(os.path.join(reqs_dir, "_map.json"), encoding="utf-8") as f:
            nodes = json.load(f).get("nodes", [])
    except (OSError, ValueError):
        return {}
    want, out = set(ids), {}
    for n in nodes:
        mem = n.get("members") or []
        if n.get("id") in want and mem and isinstance(mem[0], dict):
            out[n["id"]] = mem[0].get("loc", "")
    return out


def _req_file(reqs, rid):  # implements: ARCH-MODULEFILE-056
    """Where to open `rid`, as `requirements/<file>`. One file may hold many requirements,
    so the id is NOT the filename: `load_requirements` records the real path per block and
    that is the only thing worth printing at a reader."""
    r = reqs.get(rid) or {}
    p = r.get("path")
    return "requirements/" + (os.path.basename(p) if p else str(rid) + ".md")


def cmd_next(reqs, members, show_all=False, top_n=3, code_root=None, reqs_dir=None):  # implements: ARCH-NEXT-013
    """Terminal 'what should I do next': a focused, counted worklist over the same
    `_risk_signals` + `RISK_ADVICE` that drive the Risk tab. Prints a progress
    header, leads with the most-urgent bucket, shows the top few per bucket (the
    extract REVIEW-flagged ones first), and collapses the rest behind --all. Each
    item names the requirement file to open. Also surfaces scannable files that
    carry no membership tag (untagged bucket). Read-only, always exit 0."""
    total = len(reqs)
    if total == 0:   # distinguish "nothing set up yet" from "all clean"
        print("No requirements yet. Run `reqmap.py init` to bootstrap from existing "
              "code, or `reqmap.py new AREA-NAME-NNN` to author one.")
        return 0
    confirmed = sum(1 for r in reqs.values() if r["meta"].get("status") == "confirmed")
    tested = sum(1 for rid in reqs if any(role == "tested-by" for role, *_ in members.get(rid, [])))
    drafts = sum(1 for r in reqs.values() if r["meta"].get("status", "draft") == "draft")
    print("{} requirement(s) · {} confirmed · {} tested · {} draft(s)\n".format(
        total, confirmed, tested, drafts))

    dependents = {rid: 0 for rid in reqs}
    for rid, r in reqs.items():
        for dep in _as_list(r["meta"].get("depends_on")):
            if dep in dependents:
                dependents[dep] += 1
    buckets = {}  # signal -> [(rid, risk_score)]
    for rid, r in reqs.items():
        m = r["meta"]
        node = {"status": m.get("status", "draft"), "layer": m.get("layer", "feature"),
                "members": members.get(rid, []),
                "verify": _bullets(r["body"], "verify intent"), "test_exempt": m.get("test_exempt")}
        for sig in _risk_signals(node):
            buckets.setdefault(sig, []).append((rid, _risk_score(m)))
    # Action buckets, MOST-URGENT FIRST: an unimplemented contract outranks an
    # unreviewed draft. Each bucket is shown and truncated
    # independently, so a high-priority bucket is never hidden below a long low one.
    PLAN = [
        ("unimplemented",     "Orphans (confirmed, no code)"),
        ("untested",          "Needs tests"),
        ("unverified-intent", "Needs intent review"),
        ("unreviewed",        "Drafts to review"),
    ]
    def _priority_ord(rid):
        p = reqs[rid]["meta"].get("priority", "")
        return _PRIORITY_ORDER.get(p, 99)

    pending = [(sig, label, sorted(buckets[sig], key=lambda x: (_priority_ord(x[0]), -x[1], x[0])))
               for sig, label in PLAN if buckets.get(sig)]
    untagged = _scan_untagged(code_root, reqs_dir) if code_root else []
    if not pending and not untagged:
        print("Nothing pending — every confirmed requirement is implemented, tested and intent-checked.")
        return 0
    if pending:
        total_actions = sum(len(ids) for _, _, ids in pending)
        print("{} item(s) need attention across {} {}:\n".format(
            total_actions, len(pending), "category" if len(pending) == 1 else "categories"))
    for sig, label, ids in pending:
        print("{} ({})".format(label, len(ids)))
        shown = ids if show_all else ids[:top_n]
        for rid, score in shown:
            flag = "  [REVIEW]" if score >= 2 else ""
            print("  {}{}   {}".format(rid, flag, _req_file(reqs, rid)))
        if not show_all and len(ids) > top_n:
            print("  ... {} more — run `reqmap.py next --all`".format(len(ids) - top_n))
        print("  -> {}\n".format(RISK_ADVICE[sig]))
        if sig == "unimplemented" and reqs_dir:
            recorded = _recorded_members(reqs_dir, [rid for rid, _ in ids])
            if recorded:
                rid0 = sorted(recorded)[0]
                print("  note: the committed _map.json records member(s) for {} of these (e.g. {} <- {}) "
                      "that this scan did not reach — if they live outside the scan root, "
                      "re-run with `--code <dir>`.\n".format(len(recorded), rid0, recorded[rid0]))
    if untagged:
        shown_u = untagged if show_all else untagged[:top_n]
        print("Untagged files ({})".format(len(untagged)))
        for fp in shown_u:
            print("  {}".format(fp))
        if not show_all and len(untagged) > top_n:
            print("  ... {} more — run `reqmap.py next --all`".format(len(untagged) - top_n))
        print("  -> Run `reqmap.py draft` to auto-extract requirements, "
              "or add to .reqmapignore to silence.\n")
    # Granularity advisory: requirements with many ACs covering disjoint behaviors
    AC_SPLIT_THRESHOLD = 5
    oversize = sorted(
        [(rid, _count_ac(r["body"]))
         for rid, r in reqs.items()
         if _count_ac(r["body"]) >= AC_SPLIT_THRESHOLD],   # _count_ac handles AC-N labels too (unlike _bullets)
        key=lambda x: (-x[1], x[0])
    )
    if oversize:
        print("Granularity ({})".format(len(oversize)))
        for rid, n in oversize:
            print("  {}   ({} ACs) — consider splitting   {}".format(
                rid, n, _req_file(reqs, rid)))
        print(
            "  -> A requirement with >={} acceptance criteria covering disjoint behaviors "
            "is a split candidate. Author two requirements, each with its own contract.\n"
            .format(AC_SPLIT_THRESHOLD)
        )
    # The other direction of the same concern: covering the code with FEWER requirements.
    # Granularity above says "this one does too much"; this says "these say the same thing".
    redundant = _redundant_groups(reqs)
    if redundant:
        spare = sum(len(g) - 1 for g in redundant)
        print("Redundancy ({})".format(len(redundant)))
        shown_r = redundant if show_all else redundant[:top_n]
        for g in shown_r:
            print("  {}   identical contract   {}".format(", ".join(g), _req_file(reqs, g[0])))
        if not show_all and len(redundant) > top_n:
            print("  ... {} more — run `reqmap.py next --all`".format(len(redundant) - top_n))
        print(
            "  -> {} requirement(s) state an obligation another already states, word for "
            "word. Fold each group into one and re-point the tags, or make the contracts "
            "say different things. Exact matches only — run `reqmap.py dupes` for the "
            "near-matches this cannot see.\n".format(spare)
        )
    return 0


# ---------- lint (readability / structure of requirement prose) ----------
# Makes the SKILL.md "Audience & writing level" rules mechanical so requirements
# stay easy to understand. Scoped narrowly to keep false positives near zero: only
# non-draft requirements (drafts are TODO stubs), only the Contract and Acceptance
# sections (Notes may stay dense by design). Jargon-before-definition is deliberately
# NOT checked in v1 — without a term dictionary it is too false-positive-prone on
# prose that carries code references.
LINT_STATUSES = {"baseline", "in-progress", "implemented", "confirmed"}
LINT_STACKED_CONNECTORS = 3    # a normative line with this many 'and'/'or' joins (warn)
LINT_CLAUSE_SENTENCES = 3      # a Contract bullet spanning MORE sentences than this is
                               # flagged by `statement-too-long` (warn). Sentence count is
                               # the only dimension this check measures; words per clause
                               # belong to `statement-size`. A clause may hold two or three
                               # sentences — the extra ones state the first's consequence.
                               # A per-SENTENCE word ceiling was dropped on 2026-09-03: see
                               # ARCH-LINTCHECKS-025's notes for what that gave up.
LINT_STATEMENT_WORDS = 150     # a Contract CLAUSE — continuation lines joined — over this
                               # many words is reported by `statement-size`. Advisory only:
                               # ARCH-ATOMICITY-049 makes atomicity the normative rule and this
                               # threshold an explicit heuristic, so a longer clause stays valid.
LINT_AC_MIN = 3                # fewer ACs than this suggests under-specified (warn)
LINT_AC_MAX = 7                # more ACs than this suggests over-scoped — split candidate (warn)
LINT_CONTRACT_MAX = 10         # contract clauses over this, COMBINED with AC over LINT_AC_MAX,
                               # is the composite 'over-scoped' cohesion signal (warn)
LINT_FILE_SPREAD_MAX = 3       # implements members spanning >= this many distinct files is a
                               # 'file-spread' diffuseness signal (warn) — auto-off below it,
                               # so silent in single-file repos (near-zero false positive)
LINT_BUS_FANOUT_MIN = 3        # a `layer: bus` with ZERO dependents and this many dependencies
                               # is the inverse of a bus ('layer-mismatch', warn). Three, because
                               # this corpus's largest fan-out is three and none of its bus
                               # requirements has zero fan-in — so the check is silent here and
                               # fires on the shape that produced it (0 in / 12 out).
# Closed list of vague QUALITY words that make a normative bullet un-testable
# (IEEE 29148 "Unambiguous"). Deliberately excludes size words (high/low/small/many)
# and weak modals — they are too often legitimately precise in this domain, and a
# false positive trains authors to ignore lint. Only words with no testable meaning.
LINT_VAGUE_TERMS = frozenset({
    "appropriate", "appropriately", "adequate", "adequately", "sufficient",
    "sufficiently", "reasonable", "reasonably", "robust", "robustly", "flexible",
    "efficient", "efficiently", "optimal", "scalable", "performant", "fast", "slow",
    "quick", "quickly", "easy", "easily", "simple", "user-friendly", "seamless",
    "seamlessly", "intuitive", "various", "etc",
})
# Redundant normative modals: the Contract section opens with "Every line in this
# section is binding.", so "shall"/"must" on each clause is dead weight — and in a
# non-English requirement corpus "shall" is also a stray anglicism (see Audience &
# writing level, rule 3). Closed list, checked as a whole word, case-insensitive.
LINT_MODAL_WORDS = frozenset({"shall", "must"})
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z-]*")


def _lint_prose(body, name):  # implements: ARCH-LINT-014
    """Yield the prose text lines under the FIRST `## ` heading whose text contains
    `name`, up to the next `## `. A bullet's leading `- ` is stripped so its text is
    linted as a sentence. Non-prose lines — headings, table rows, blockquotes, and
    anything inside a ``` fence — are skipped so the linter never flags code or
    markup as unreadable. Fence state is tracked BEFORE heading detection, so a
    `## ` comment inside a fenced block is treated as code, not a section boundary."""
    out, grab, seen, fenced = [], False, False, False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):          # fence first: an in-fence `## ` is code, not a heading
            fenced = not fenced
            continue
        if fenced:
            continue
        if s.startswith("## "):
            grab = (not seen) and _heading_label_is(s, name)   # anchored, agrees with _has_section
            if grab:
                seen = True
            continue
        if not grab or not s or s.startswith(("|", ">", "#")):
            continue
        if s == "-" or s.startswith("- "):   # a real bullet marker (not '--strict' / '-5')
            s = s[1:].strip()
        if s:
            out.append(s)
    return out


def _sentences(text):  # implements: ARCH-LINTCHECKS-025
    """Split a prose line into sentences on '.', '!', '?' boundaries. Crude but
    deterministic — enough to count words per sentence for the length check."""
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", text) if p.strip()]


def _clip(s, n=60):  # implements: ARCH-LINT-014
    """Shorten a snippet for one-line finding output."""
    return s if len(s) <= n else s[:n - 1] + "…"


def _clause_words(text):  # implements: ARCH-ATOMICITY-049
    """Word count for a Contract clause, counting each backticked span as one word.
    A clause carrying a long code sample is short prose, not a long statement. The span
    collapses to a bare token with no padding spaces: " x " would split trailing punctuation
    (`code`. -> "x" ".") into a second word and inflate every such clause by one."""
    return len(re.sub(r"`[^`]*`", "x", text).split())


def _contract_clauses(body):  # implements: ARCH-ATOMICITY-049
    """Yield (n, text) per clause of the Contract section, n 1-based.

    A clause is one bullet at ANY indent — a nested sub-bullet is its own clause because
    it states its own obligation — with its wrapped continuation lines joined back on.
    This is deliberately not `_lint_prose`, which yields physical LINES: these files are
    hard-wrapped near 95 columns, so a 90-word clause reaches `_lint_prose` as six ~15-word
    lines and no per-line ceiling can ever see it. Bold group labels, table rows, block
    quotes, fenced code and HTML comments are not clauses and are skipped."""
    out, cur, grab, seen, fenced, in_comment = [], None, False, False, False, False

    def flush():
        if cur is not None:
            out.append(cur)

    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):              # fence first: an in-fence `## ` is code
            fenced = not fenced
            continue
        if fenced:
            continue
        if in_comment:                       # glossary comments are guidance, not clauses
            if "-->" in s:
                in_comment = False
            continue
        if s.startswith("<!--"):
            if "-->" not in s:
                in_comment = True
            continue
        if s.startswith("## "):
            flush(); cur = None
            grab = (not seen) and any(_heading_label_is(s, n) for n in CONTRACT_LABELS)
            if grab:
                seen = True
            continue
        if not grab:
            continue
        if not s or s.startswith(("|", ">", "#")) or (s.startswith("**") and s.endswith("**")):
            flush(); cur = None
            continue
        if s == "-" or s.startswith("- "):
            flush()
            cur = s[1:].strip()
        elif cur is not None:
            cur += " " + s
    flush()
    return list(enumerate([c for c in out if c], 1))


def _count_ac(body):
    """Count acceptance criteria in the HOW — Acceptance section.
    Handles both bullet-list ACs (- ...) and labeled AC blocks (AC-N ...).
    Delegates to `_acc_blocks`, the single parser of that section, so the count
    `lint` and `next` reason about cannot drift from the criteria the map emits."""
    return len(_acc_blocks(body))


def lint_requirement(rid, r, member_list=None, fanin=None, children=None):  # implements: ARCH-LINT-014  # implements: ARCH-LINTCHECKS-025  # implements: ARCH-FANOUT-052
    """Return a list of {severity, check, detail} findings for one requirement;
    an empty list means clean. Checks the Contract + Acceptance sections only.
    `member_list` (optional [(role, file, line), ...]) enables the member-based
    file-spread check; when omitted, that check is skipped.
    `fanin` (optional int — how many requirements depend on this one) enables the
    layer-mismatch check; when omitted, that check is skipped.
    `children` (optional int — how many requirements declare `satisfies:` this one) enables
    the fan-out check; when omitted, or when it is zero, that check is skipped.
    Checks named in the requirement's `lint_exempt:` frontmatter list are silently
    skipped and not counted against the requirement."""
    exempt = set(_as_list(r["meta"].get("lint_exempt")))
    findings = []
    body = r["body"]
    # structural (error): a non-draft must carry both load-bearing sections
    if not _has_any(body, CONTRACT_LABELS):
        findings.append({"severity": "error", "check": "missing-section",
                         "detail": "no '## Description' section"})
    if not _has_any(body, ACCEPTANCE_LABELS):
        findings.append({"severity": "error", "check": "missing-section",
                         "detail": "no '## Cases' section"})
    # empty-section (warn): the heading is present but carries no clauses/criteria — it
    # passes `missing-section` yet documents nothing (and `ac-count-low` skips the zero
    # case). Precise zero/non-zero test, so near-zero false positive.
    if _has_any(body, CONTRACT_LABELS) and not _from_any(_bullets, body, CONTRACT_LABELS):
        findings.append({"severity": "warn", "check": "empty-section",
                         "detail": "'## Description' section present but has no clauses"})
    if _has_any(body, ACCEPTANCE_LABELS) and _count_ac(body) == 0:
        findings.append({"severity": "warn", "check": "empty-section",
                         "detail": "'## Cases' section present but has no criteria"})
    # prose readability (warn): only on the Contract + Acceptance sections
    for name in (CONTRACT_LABELS[0], CONTRACT_LABELS[1],
                 ACCEPTANCE_LABELS[0], ACCEPTANCE_LABELS[1]):
        for ln in _lint_prose(body, name):
            low = ln.lower()
            # Every line in a Contract/Acceptance section is normative by virtue of the
            # section it sits in, so the join count applies to all of them. This used to be
            # gated on `"shall" in low or "must" in low`, which made the check silent for the
            # plain present-tense voice — a clarity rule keyed on a magic word misses clauses.
            joins = len(re.findall(r"\b(?:and|or)\b", low))
            if joins >= LINT_STACKED_CONNECTORS:
                findings.append({
                    "severity": "warn", "check": "stacked-conditions",
                    "detail": "{} 'and'/'or' joins in one normative line: {}".format(
                        joins, _clip(ln))})
            # Contract only: a clause whose subject is a bare "It" forces the reader to hold
            # the requirement's title in their head to know what is being promised. Name it.
            # Acceptance prose is exempt — a Then clause saying "it returns …" reads fine.
            if name in CONTRACT_LABELS and re.match(r"^It\s+[a-z]", ln):
                findings.append({
                    "severity": "warn", "check": "anonymous-subject",
                    "detail": "clause opens with an unnamed 'It' — name the subject: {}".format(
                        _clip(ln))})
    # statement atomicity (warn): a Contract bullet spanning more than
    # LINT_CLAUSE_SENTENCES sentences packs several statements into one clause (split it).
    # Sentence COUNT is the only dimension here — `long-sentence` owns words per sentence
    # and `statement-size` owns words per clause — so the three checks never flag the same
    # line for the same reason, and a correct two- or three-sentence clause stays silent.
    # Read whole CLAUSES, not the physical lines `_lint_prose` yields. These files wrap
    # near 95 columns, so a line-based count can never see a clause that spans several
    # lines — which is why this check reported 0 corpus-wide while measuring the wrong
    # unit. Measured before the switch: 0 of 625 non-draft clauses hold more than three
    # sentences, so widening the unit changes nothing the check says today.
    for _cn, ln in _contract_clauses(body):
        sents = _sentences(ln)
        if len(sents) > LINT_CLAUSE_SENTENCES:
            findings.append({
                "severity": "warn", "check": "statement-too-long",
                "detail": "statement spans {} sentences (>{}): {}".format(
                    len(sents), LINT_CLAUSE_SENTENCES, _clip(ln))})
    # statement-size (warn, advisory): a Contract clause well past the length a single
    # obligation normally needs. Measured per CLAUSE, not per line — see _contract_clauses.
    # Advisory by contract: exceeding the threshold never makes a clause invalid and never
    # asserts that it holds two obligations, which the engine cannot observe
    # (ARCH-ATOMICITY-049). The finding carries clause_n/clause_text so `--decompose` can
    # scaffold from the same clause without re-parsing.
    for _n, _clause in _contract_clauses(body):
        _cw = _clause_words(_clause)
        if _cw > LINT_STATEMENT_WORDS:
            findings.append({
                "severity": "warn", "check": "statement-size",
                "clause_n": _n, "clause_text": _clause,
                "detail": "clause {} is {} words (>{}) \u2014 re-read it for decomposition: {}".format(
                    _n, _cw, LINT_STATEMENT_WORDS, _clip(_clause))})
    # ac count (warn): too few = under-specified; too many = over-scoped
    if _has_any(body, ACCEPTANCE_LABELS):
        ac_n = _count_ac(body)
        # An atomic requirement holds ONE obligation, so one criterion is the correct
        # number, not an under-specified one. LINT_AC_MIN guards a dossier.
        if 0 < ac_n < LINT_AC_MIN and not _atomic_spans(body):
            findings.append({
                "severity": "warn", "check": "ac-count-low",
                "detail": "{} AC (< {}): requirement may be under-specified".format(
                    ac_n, LINT_AC_MIN)})
        elif ac_n > LINT_AC_MAX:
            findings.append({
                "severity": "warn", "check": "ac-count-high",
                "detail": "{} AC (> {}): consider splitting into two requirements".format(
                    ac_n, LINT_AC_MAX)})
    # cohesion (warn): over BOTH the contract and acceptance ceilings at once is a strong
    # "several capabilities bundled into one" signal — each contract clause is a separate
    # binding, each AC an independent failure mode. Requiring BOTH axes (a composite) keeps
    # false positives near zero: a large-but-cohesive capability rarely maxes both. Advisory
    # only — it surfaces split candidates; the split decision stays with the human.
    if _has_any(body, CONTRACT_LABELS) and _has_any(body, ACCEPTANCE_LABELS):
        # Scope units, not sentences. A contract that groups its clauses under bold labels
        # states one facet per group, so the group count is what says how much the
        # requirement promises; the clause count only says how finely the prose was split.
        # Counting clauses alone punished the atomic voice — one obligation per bullet
        # multiplies bullets without widening scope at all. Ungrouped contracts fall back
        # to the clause count, which is what this check has always used.
        # Counted off _section_raw, not _lint_prose: _lint_prose strips each line, and a
        # label is defined by sitting at column 0 (see _is_label_line). Given stripped
        # input every wrapped clause that opens and closes on bold spans counts as a
        # group, inflating contract_n — and `over-scoped` is an ERROR under --strict, so
        # that miscount fails CI on a requirement that is not over-scoped.
        groups = sum(1 for ln in _from_any(_section_raw, body, CONTRACT_LABELS).split("\n")
                     if _is_label_line(ln))
        contract_n = groups or len(_from_any(_bullets, body, CONTRACT_LABELS))
        ac_count = _count_ac(body)
        if contract_n > LINT_CONTRACT_MAX and ac_count > LINT_AC_MAX:
            findings.append({
                "severity": "warn", "check": "over-scoped",
                "detail": "{} contract {} + {} AC (both over {}/{}): likely several "
                          "capabilities — consider splitting".format(
                              contract_n, "groups" if groups else "clauses",
                              ac_count, LINT_CONTRACT_MAX, LINT_AC_MAX)})
    # fan-out (warn): a parent in the `satisfies:` hierarchy normally carries 5-20 children.
    # Too few and the level buys no grouping; too many and it is a bucket, not a level.
    # Counted on the satisfies graph, NOT on `depends_on` — the two are different axes, and
    # `depends_on` depth here maxes out at 3, so a band of 5-20 read against it would flag
    # every requirement in the corpus. A leaf (zero children) is skipped: it is not a
    # malformed parent, it is not a parent at all.
    if children:
        if not (LINT_FANOUT_MIN <= children <= LINT_FANOUT_MAX):
            findings.append({
                "severity": "warn", "check": "fan-out",
                "detail": "{} requirement(s) satisfy this one (outside {}-{}): {}".format(
                    children, LINT_FANOUT_MIN, LINT_FANOUT_MAX,
                    "too few to be a level" if children < LINT_FANOUT_MIN
                    else "too many — split it")})
    # vague terms (warn): a Contract bullet using a non-testable quality word is
    # ambiguous (IEEE 29148). Code spans (`backticked`) are stripped first so a
    # backticked identifier is never flagged. One finding per distinct term.
    seen_vague = set()
    for ln in _lint_prose(body, "contract"):
        bare = re.sub(r"`[^`]*`", " ", ln)
        for w in _WORD_RE.findall(bare):
            lw = w.lower()
            if lw in LINT_VAGUE_TERMS and lw not in seen_vague:
                seen_vague.add(lw)
                findings.append({
                    "severity": "warn", "check": "vague-term",
                    "detail": "vague word '{}' (no testable meaning): {}".format(
                        w, _clip(ln))})
    # redundant modal (warn): "shall"/"must" on a Contract clause is either dead weight
    # (the section header already binds every line) or a stray English modal dropped into
    # a non-English clause. Same one-finding-per-distinct-term shape as vague-term, above.
    seen_modal = set()
    for ln in _lint_prose(body, "contract"):
        bare = re.sub(r"`[^`]*`", " ", ln)
        for w in _WORD_RE.findall(bare):
            lw = w.lower()
            if lw in LINT_MODAL_WORDS and lw not in seen_modal:
                seen_modal.add(lw)
                findings.append({
                    "severity": "warn", "check": "redundant-modal",
                    "detail": "redundant modal '{}' (the Contract header already binds "
                              "every line — use plain present tense): {}".format(
                                  w, _clip(ln))})
    # file-spread (warn): a requirement whose implements members span many distinct FILES is
    # architecturally diffuse — a cohesion axis the intent-axis checks (over-scoped, ac-count)
    # cannot see, since a tight contract can still be smeared across many files. Auto-off when
    # the members live in fewer than LINT_FILE_SPREAD_MAX files, so it is silent in a single-file
    # repo (near-zero false positive). Needs member_list; skipped when not supplied.
    if member_list:
        impl_files = {m[1] for m in member_list if m and m[0] == "implements"}
        if len(impl_files) >= LINT_FILE_SPREAD_MAX:
            findings.append({
                "severity": "warn", "check": "file-spread",
                "detail": "implements span {} files (>= {}): capability may be diffuse — "
                          "confirm cohesion or split".format(len(impl_files), LINT_FILE_SPREAD_MAX)})
    # layer-mismatch (warn): `bus` is DEFINED by fan-in ("foundation, high fan-in"),
    # and nothing checked it. A requirement with no dependents and many dependencies is
    # the exact inverse — a roof labelled a foundation. It reads as bus in the map, in
    # `next`, and in every diagnostic built on the layer, so the mislabel misleads
    # precisely where the layer is supposed to help. `layer: aggregate` is the label
    # such a requirement wants.
    if (fanin is not None and r["meta"].get("layer") == "bus"
            and fanin == 0
            and len(_as_list(r["meta"].get("depends_on"))) >= LINT_BUS_FANOUT_MIN):
        findings.append({
            "severity": "warn", "check": "layer-mismatch",
            "detail": "layer: bus but nothing depends on it and it depends on {} "
                      "requirement(s) — that is a roof, not a foundation; consider "
                      "`layer: aggregate` or `feature`".format(
                          len(_as_list(r["meta"].get("depends_on"))))})
    if exempt:
        findings = [f for f in findings if f["check"] not in exempt]
    return findings


DECOMPOSED_TEMPLATE = """---
id: {new_id}
status: draft
layer: {layer}
owner: {owner}
depends_on: [{parent}]
superseded_by:
---

# Split from {parent} clause {n}

<!-- decomposed-from: {parent}#{n} -->

## Description
> Scaffolded by `lint --decompose` from a clause that ran past
> LINT_STATEMENT_WORDS words. Rewrite this quote before confirming: say what this
> capability is and what breaks without it.

Every bullet below is binding.
- {clause}

## Verify intent (open questions for the human)
- Does this clause state one obligation, or several? The split point was chosen by
  word count, so this file may hold a clause that was atomic all along.

## Cases (= tests)
CASE-1
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Context (non-binding)
**Notes**
- SCAFFOLD, NOT A DECISION. `lint --decompose` copied clause {n} of {parent} here
  verbatim. The split point was chosen by WORD COUNT, never by obligation — the engine
  cannot observe how many obligations a clause holds (ARCH-ATOMICITY-049). Read the clause
  and decide for yourself whether it should have been split at all.
- The clause is still over the threshold here, because only a human can divide it. Confirming
  this file unedited re-raises the same `statement-size` finding, which is the intended
  reminder.
- {parent} was not modified. Deleting this file restores the corpus exactly.

## Links
- Used by: (auto)
## Members in code (auto)
"""


def _next_free_number(reqs_dir):  # implements: ARCH-DECOMPOSE-050
    """Highest NNN across the corpus, plus one. Ids stay in AREA-NAME-NNN shape rather
    than taking a derived suffix such as REQ-AUTH-012-B: the suffix form passes _ID_PAT,
    but _warn_number_collision reads parts[-1] as the number and would compare "B"."""
    best = 0
    try:
        names = os.listdir(reqs_dir)
    except OSError:
        return 1
    for fn in names:
        if not fn.endswith(".md") or fn.startswith("_"):
            continue
        parts = fn[:-3].split("-")
        if len(parts) >= 3 and parts[-1].isdigit():
            best = max(best, int(parts[-1]))
    return best + 1


def _already_decomposed(reqs_dir, parent_id, n):  # implements: ARCH-DECOMPOSE-050
    """True when some requirement already carries the `decomposed-from: <parent>#<n>` marker.

    Re-running must be a no-op, and the allocated file NAME cannot detect that: the id comes
    from the next free number, so a second run picks a fresh name and `os.path.exists` never
    fires. Provenance is the only stable key. The marker is an HTML comment rather than a
    frontmatter field so it stays invisible to `binding_hash`, and `decomposed-from` is not
    a member role, so TAG_LIST_RE never reads it as a link."""
    needle = "decomposed-from: {}#{}".format(parent_id, n)
    try:
        names = os.listdir(reqs_dir)
    except OSError:
        return False
    for fn in names:
        if not fn.endswith(".md") or fn.startswith("_"):
            continue
        try:
            with open(os.path.join(reqs_dir, fn), encoding="utf-8") as f:
                if needle in f.read():
                    return True
        except OSError:
            continue
    return False


def _decompose_clause(reqs_dir, parent_id, parent, n, clause):  # implements: ARCH-DECOMPOSE-050
    """Scaffold one draft requirement from an over-threshold Contract clause.

    Creates exactly one file and never touches the parent, so a confirmed contract cannot
    drift and deleting the new file undoes the whole operation. Returns the created id, or
    None when this clause was already scaffolded (re-running is a no-op, reported by the
    caller)."""
    if _already_decomposed(reqs_dir, parent_id, n):
        return None
    parts = parent_id.split("-")
    stem = "-".join(parts[:-1]) if len(parts) >= 3 and parts[-1].isdigit() else parent_id
    new_id = "{}-{:03d}".format(stem, _next_free_number(reqs_dir))
    dest = os.path.join(reqs_dir, new_id + ".md")
    if os.path.exists(dest):
        return None
    meta = parent["meta"]
    text = DECOMPOSED_TEMPLATE.format(
        new_id=new_id, parent=parent_id, n=n, clause=clause,
        layer=meta.get("layer", "feature") or "feature",
        owner=meta.get("owner", "") or "")
    os.makedirs(reqs_dir, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(text)
    return new_id


def cmd_lint(reqs, strict=False, members=None, decompose=False, reqs_dir=None):  # implements: ARCH-LINT-014  # implements: ARCH-DECOMPOSE-050
    """Report readability/structure violations on non-draft requirements so they
    stay easy to understand — the SKILL.md 'Audience & writing level' rules made
    mechanical. Checks: missing-section (error),
    stacked-conditions (warn), statement-too-long (warn), ac-count-low (warn),
    ac-count-high (warn), vague-term (warn), redundant-modal (warn). Read-only. Exit-neutral by default; with
    --strict it exits non-zero on any error-severity finding AND promotes structural
    checks (ac-count-high) to error severity.
    Requirements with `lint_exempt: [check-name]` frontmatter silently skip those checks;
    active exemptions are printed after the requirement header.
    The default run writes nothing. With `decompose` (the opt-in `--decompose` flag) each
    `statement-size` finding also scaffolds one draft requirement from its clause. The gate,
    the pre-commit hook and CI never pass it: .githooks/pre-commit runs gate -> lint --strict
    -> map --check, so a file written during the lint step would fail the map --check step of
    the same hook run (ARCH-DECOMPOSE-050)."""
    # Checks promoted from warn→error in --strict mode (structural, not style).
    STRICT_PROMOTE = {"ac-count-high", "over-scoped"}
    targets = [(rid, r) for rid, r in sorted(reqs.items())
               if r["meta"].get("status") in LINT_STATUSES]
    fanin = {rid: 0 for rid in reqs}                      # implements: ARCH-LINTCHECKS-025
    kids = {rid: 0 for rid in reqs}                        # implements: ARCH-FANOUT-052
    for _rid, _r in reqs.items():                          # satisfies edges, child side
        for _up in _as_list(_r["meta"].get("satisfies")):
            if _up in kids:
                kids[_up] += 1
    for _rid, _r in reqs.items():
        for _dep in _as_list(_r["meta"].get("depends_on")):
            if _dep in fanin:
                fanin[_dep] += 1
    errors = warns = 0
    created = []
    for rid, r in targets:
        fs = lint_requirement(rid, r, (members or {}).get(rid), fanin.get(rid), kids.get(rid))
        exempt = set(_as_list(r["meta"].get("lint_exempt")))
        if not fs and not exempt:
            continue
        print("{}   requirements/{}.md".format(rid, rid))
        if exempt:
            print("  (exempt: {})".format(", ".join(sorted(exempt))))
        for f in fs:
            effective = f["severity"]
            if strict and f["check"] in STRICT_PROMOTE:
                effective = "error"
            if effective == "error":
                errors += 1; mark = "ERROR"
            else:
                warns += 1; mark = "warn "
            print("  {} {:18} {}".format(mark, f["check"], f["detail"]))
        if decompose and reqs_dir:
            for f in fs:
                if f["check"] != "statement-size":
                    continue
                made = _decompose_clause(reqs_dir, rid, r, f["clause_n"], f["clause_text"])
                if made:
                    created.append(made)
                    print("  created  requirements/{}.md  (draft, seeded from clause {})".format(
                        made, f["clause_n"]))
                else:
                    print("  skipped  clause {} \u2014 already scaffolded".format(f["clause_n"]))
    print("\n{} non-draft requirement(s) linted · {} error(s) · {} warning(s)".format(
        len(targets), errors, warns))
    if created:
        print("{} draft(s) scaffolded: {}".format(len(created), ", ".join(created)))
        print("note: each split point was chosen by word count, not by obligation \u2014 "
              "read each draft before confirming it.")
    if errors == 0 and warns == 0:
        print("All clean — every linted requirement is well-formed and readable.")
    if strict and errors:
        print("FAIL (--strict): {} structural error(s) (includes promoted structural warns).".format(errors))
        return 1
    return 0


def cmd_show(reqs, members, cap_id, levels=None):  # implements: ARCH-SHOW-015  # implements: ARCH-VLEVEL-037
    """Print one consolidated, human-readable dossier for a single requirement: its
    status/layer/intent, contract, dependencies (both directions), members grouped
    by role, open verify-intent questions, and risk signals — the 'what does this do
    / where is X' view in one command. Read-only; returns 1 on an unknown id so a
    typo is visible to a caller or CI. Reuses the same signal source as next/findings."""
    r = reqs.get(cap_id)
    if not r:
        print("no requirement with id {} (expected requirements/{}.md)".format(cap_id, cap_id))
        return 1
    m, body = r["meta"], r["body"]
    head = "{} · {} · {}".format(cap_id, m.get("status", "draft"), m.get("layer", "?"))
    if m.get("priority"):
        head += " · " + m["priority"]
    if m.get("milestone"):
        head += " · " + m["milestone"]
    print(head)
    print(_req_title(body, cap_id))
    intent = _first_quote(body)             # the full WHY block, gathered (not just line 1)
    if intent:
        print("  " + intent)

    contract = _from_any(_bullets, body, CONTRACT_LABELS)
    print("\nContract:")
    for b in contract:
        print("  - " + b)
    if not contract:
        print("  (none — no '## Description' section)")

    deps = _as_list(m.get("depends_on"))
    dependents = sorted(rid for rid, rr in reqs.items()
                        if cap_id in _as_list(rr["meta"].get("depends_on")))
    print("\nDepends on: " + (", ".join(deps) if deps else "(none)"))
    print("Depended on by: " + (", ".join(dependents) if dependents else "(none)"))

    # upstream traceability: only shown when the requirement participates in it,  # implements: ARCH-TRACE-020
    # so requirements that don't use `satisfies` get no extra noise.
    upstream = _as_list(m.get("satisfies"))
    satisfiers = sorted(rid for rid, rr in reqs.items()
                        if cap_id in _as_list(rr["meta"].get("satisfies")))
    if upstream or satisfiers:
        print("Satisfies (upstream): " + (", ".join(upstream) if upstream else "(none)"))
        print("Satisfied by: " + (", ".join(satisfiers) if satisfiers else "(none)"))

    mem = members.get(cap_id, [])
    # {(file, line): level} for this requirement, so a levelled tested-by link shows the
    # level it asserts rather than leaving the reader to open the file.
    at = {}
    for lvl, hits in (levels or {}).get(cap_id, {}).items():
        for hit in hits:
            at[hit] = lvl
    print("\nMembers in code ({}):".format(len(mem)))
    if mem:
        for role, fp, ln in sorted(mem):
            lvl = at.get((fp, ln))
            print("  {:18} {}:{}{}".format(role, fp, ln, " @" + lvl if lvl else ""))
    else:
        print("  (none tagged)")

    verify = [b for b in _bullets(body, "verify intent")
              if b and not b.lstrip("*_ ").lower().startswith("none")]
    if verify:
        print("\nOpen verify-intent:")
        for b in verify:
            print("  - " + b)

    node = {"status": m.get("status", "draft"), "layer": m.get("layer", "feature"), "members": mem,
            "verify": _bullets(body, "verify intent"), "test_exempt": m.get("test_exempt")}
    signals = _risk_signals(node)
    if signals:
        print("\nRisk signals:")
        for s in signals:
            print("  [{}] {}".format(s, RISK_ADVICE[s]))
    print("\n{}".format(r["path"]))
    return 0


# ---------- similar (duplicate-capability detection) ----------
# Flags requirement pairs whose contracts overlap, so a human can catch a divergent
# re-implementation before it lands. Stdlib TF-IDF + cosine over the normative text
# (title + intent + Contract); Notes is excluded as too dense/noisy.
SIMILAR_THRESHOLD = 0.35       # cosine above this -> reported as a probable-duplicate pair
_SIMILAR_STOP = frozenset((
    "the", "and", "for", "shall", "with", "that", "this", "from", "into", "its",
    "not", "are", "has", "have", "when", "then", "given", "each", "one", "any",
    "per", "via", "use", "used", "must", "code", "requirement", "requirements",
))


def _sim_tokens(text):  # implements: ARCH-SIMILAR-016
    """Lowercase alphanumeric tokens of length >= 3, minus stopwords and pure
    numbers — the bag of words a requirement is compared on. Deterministic."""
    return [t for t in re.findall(r"[a-z0-9]+", text.lower())
            if len(t) >= 3 and not t.isdigit() and t not in _SIMILAR_STOP]


def _placeholder_contract(body):  # implements: ARCH-SIMILAR-016
    """True when every Contract bullet is still a `TODO:` scaffold line. Five evidence
    runs scored thousands of freshly-drafted stubs as near-duplicates of each other on
    template text alone (fabric: 6,340 pairs for 638 drafts) — nothing authored, nothing
    to compare."""
    bullets = _from_any(_bullets, body, CONTRACT_LABELS)
    return bool(bullets) and all(b.strip().upper().startswith("TODO") for b in bullets)


def _redundant_groups(reqs):  # implements: ARCH-REDUNDANCY-058
    """Requirements whose Description clauses are IDENTICAL once case and whitespace are
    normalised, grouped, each group sorted and the groups ordered by their first id.

    This is the exact-match floor under `dupes`, not a second opinion on it: no threshold,
    no scoring, so a group is a duplicate by construction and never a judgement call. It
    exists because decomposing several architecture requirements can mint the same
    obligation twice — the same clause authored in two parents becomes two detailed-design
    requirements — and nothing else in the engine notices. `dupes` finds the near-matches
    this cannot; neither replaces the other.

    Draft placeholders are skipped: every freshly scaffolded requirement carries the same
    `TODO:` line, so counting those would report the scaffold as a duplicate of itself
    hundreds of times and drown the real finding."""
    groups = {}
    for rid, r in sorted(reqs.items()):
        body = r["body"]
        if _placeholder_contract(body):
            continue
        key = re.sub(r"\s+", " ", " ".join(_from_any(_bullets, body, CONTRACT_LABELS))).strip().lower()
        if key:
            groups.setdefault(key, []).append(rid)
    return sorted((sorted(v) for v in groups.values() if len(v) > 1), key=lambda g: g[0])


def _sim_text(body):  # implements: ARCH-SIMILAR-016
    """The text similarity is computed on: title, intent line, and Contract bullets.
    Notes & limitations is left out — it is dense and would only add noise."""
    parts = [_req_title(body, "")]
    for line in body.splitlines():
        if line.strip().startswith(">"):
            parts.append(line.strip().lstrip(">").strip())
            break
    parts += _from_any(_bullets, body, CONTRACT_LABELS)
    return " ".join(parts)


def _tfidf(docs):  # implements: ARCH-SIMILAR-016
    """docs: {id: token_list}. Returns {id: {term: weight}} with smoothed idf =
    log((1 + N) / (1 + df)) + 1 — always positive (so a 2-doc corpus does not
    collapse to zero), while still down-weighting terms common across requirements."""
    N = len(docs)
    df = {}
    for toks in docs.values():
        for t in set(toks):
            df[t] = df.get(t, 0) + 1
    vecs = {}
    for rid, toks in docs.items():
        tf = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        vecs[rid] = {t: c * (math.log((1 + N) / (1 + df[t])) + 1) for t, c in tf.items()}
    return vecs


def _cosine(a, b):  # implements: ARCH-SIMILAR-016
    """Cosine similarity of two {term: weight} vectors, in [0, 1]. The result is
    clamped to 1.0 because floating-point rounding can push parallel vectors a hair
    over 1.0 (e.g. 1.0000000000000002), which would break the documented range."""
    if not a or not b:
        return 0.0
    dot = sum(a[t] * b[t] for t in set(a) & set(b))
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return min(1.0, dot / (na * nb)) if na and nb else 0.0


def _threshold_arg(v):  # implements: ARCH-SIMILAR-016
    """argparse type for `--threshold`: a finite number in (0, 1]. Rejects nan/inf
    (which silently swallow or admit every pair under `>=`) and out-of-range cutoffs."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("threshold must be a number")
    if not math.isfinite(f) or not (0.0 < f <= 1.0):
        raise argparse.ArgumentTypeError("threshold must be a finite number in (0, 1]")
    return f


def _test_suite_pairs(members):
    """Pairs (A, B) where a `tested-by` member file of A is an `implements` member of B —
    i.e. B is the requirement that IS A's test suite. Such a pair shares vocabulary by
    construction and is a known link, not a duplicate. Empty when no member map is given."""
    impl_of = {}   # file -> set of requirement ids implemented in it
    for rid, mem in (members or {}).items():
        for role, f, _ in mem:
            if role == "implements":
                impl_of.setdefault(f, set()).add(rid)
    linked = set()
    for rid, mem in (members or {}).items():
        for role, f, _ in mem:
            if role == "tested-by":
                for other in impl_of.get(f, ()):
                    if other != rid:
                        linked.add(frozenset((rid, other)))
    return linked


def cmd_similar(reqs, threshold=SIMILAR_THRESHOLD, members=None):  # implements: ARCH-SIMILAR-016
    """Report requirement pairs whose contracts overlap at or above `threshold`
    (cosine over TF-IDF of title + intent + Contract), most-similar-first, so a human
    can spot a probable duplicate or a capability that should be merged. Read-only and
    always exit 0 (advisory). Smoothed idf down-weights shared boilerplate so it
    does not inflate the score. Callers pass a validated threshold in (0, 1].
    With `members`, a pair linked by `tested-by` (one requirement is the other's test
    suite) is skipped and counted instead of reported."""
    linked = _test_suite_pairs(members)
    placeholder = sorted(rid for rid, r in reqs.items() if _placeholder_contract(r["body"]))
    docs = {rid: _sim_tokens(_sim_text(r["body"])) for rid, r in reqs.items()
            if rid not in placeholder}
    docs = {rid: toks for rid, toks in docs.items() if toks}   # skip empty contracts
    if placeholder:
        print("skipped {} requirement(s) whose Contract is still the draft placeholder — "
              "dupes compares authored contracts only.\n".format(len(placeholder)))
    if len(docs) < 2:
        print("Need at least two requirements with contract text to compare.")
        return 0
    vecs = _tfidf(docs)
    ids = sorted(vecs)
    pairs = []
    skipped_linked = 0
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            s = _cosine(vecs[ids[i]], vecs[ids[j]])
            if s >= threshold:
                if frozenset((ids[i], ids[j])) in linked:
                    skipped_linked += 1
                    continue
                shared = sorted(set(vecs[ids[i]]) & set(vecs[ids[j]]),
                                key=lambda t: (-(vecs[ids[i]][t] + vecs[ids[j]][t]), t))[:5]
                pairs.append((s, ids[i], ids[j], shared))
    pairs.sort(key=lambda x: (-x[0], x[1], x[2]))
    if skipped_linked:
        print("skipped {} pair(s) linked by tested-by (a requirement and its own test suite "
              "share vocabulary by construction).\n".format(skipped_linked))
    if not pairs:
        print("No overlapping requirement pairs at or above {:.2f}. {} requirement(s) compared.".format(
            threshold, len(docs)))
        return 0
    print("{} probable-duplicate pair(s) at or above {:.2f} (of {} requirement(s)):\n".format(
        len(pairs), threshold, len(docs)))
    for s, a, b, shared in pairs:
        print("  {:.2f}  {}  <->  {}".format(s, a, b))
        print("        shared terms: {}".format(", ".join(shared) or "(none)"))
    print("\nThese contracts overlap — check they are not the same capability "
          "implemented twice. Merge or differentiate, then re-run.")
    return 0


# ---------- search (free-text requirement lookup) ----------
# Ranks requirements against a free-text query with the SAME lexical TF-IDF/cosine
# used by `dupes` — reused, not re-implemented. The floor is NOT the dupes 0.35
# pair-threshold: a short query is a sparse vector, so query-vs-doc cosine runs far
# lower than doc-vs-doc. Calibrated on the 39-requirement corpus, a correct top hit
# scores ~0.13-0.67 while a no-lexical-overlap query tops out ~0.00-0.04, so 0.05
# cleanly separates a real match from noise. Below it, `search` says so rather than
# presenting a spurious top result with the same authority as a real one.
SEARCH_FLOOR = 0.05
SEARCH_TOP = 5


def cmd_search(reqs, query, top=SEARCH_TOP, floor=SEARCH_FLOOR):  # implements: ARCH-SEARCH-036
    """Rank requirements by lexical relevance to `query` (cosine over TF-IDF of the
    same title + intent + Contract text `dupes` compares on). Read-only, always exit
    zero. Prints each hit's cosine score so a weak match is visible as weak, and emits
    an explicit no-strong-match line when the best score is below `floor` — so a
    lexical near-miss is never dressed up as an answer."""
    qtok = _sim_tokens(query or "")
    if not qtok:
        print("No searchable terms in {!r} (need a word of 3+ letters that is not a "
              "stopword). Nothing to rank.".format(query or ""))
        return 0
    docs = {rid: _sim_tokens(_sim_text(r["body"])) for rid, r in reqs.items()}
    docs = {rid: toks for rid, toks in docs.items() if toks}   # skip empty contracts
    if not docs:
        print("No requirements with contract text to search.")
        return 0
    top = max(1, top)
    corpus = dict(docs)
    corpus["\x00query"] = qtok        # fold the query into the corpus so idf spans docs+query
    vecs = _tfidf(corpus)
    qv = vecs["\x00query"]
    scored = sorted(((_cosine(qv, vecs[rid]), rid) for rid in docs),
                    key=lambda x: (-x[0], x[1]))
    hits = [(s, rid) for s, rid in scored if s >= floor][:top]
    if not hits:
        print("No strong match for {!r} (best {:.3f} is below the {:.2f} floor). "
              "This is lexical search — try different words, or `dupes`/grep.".format(
                  query, scored[0][0], floor))
        return 0
    print("{} match(es) for {!r} — cosine score, lexical (not synonym-aware):\n".format(
        len(hits), query))
    for s, rid in hits:
        print("  {:.3f}  {}  {}".format(s, rid, _req_title(reqs[rid]["body"], rid)))
    return 0


# ---------- health (corpus coherence snapshot) ----------
def cmd_coverage(reqs, members, code_root, reqs_dir, as_json=False):
    """Per-directory coverage report: how many scannable files in each top-level
    directory carry at least one membership tag vs. total scannable files.
    Helps identify which parts of the codebase have no requirement coverage."""
    ignore = load_ignore(code_root, reqs_dir)
    # requirements dir contains spec files, not implementation files — exclude from coverage
    reqs_abs = os.path.normcase(os.path.abspath(reqs_dir)) if reqs_dir else None
    tagged_files = set()
    for mlist in members.values():
        for _role, fp, _ln in mlist:
            tagged_files.add(os.path.normcase(os.path.abspath(os.path.join(code_root, fp))))

    buckets = {}  # dir_label -> [total, tagged]
    for dirpath, dirs, files in os.walk(code_root):
        dirs[:] = [d for d in sorted(dirs) if d not in (".git", "__pycache__", "node_modules")]
        for fn in sorted(files):
            if not _is_code_file(fn):
                continue
            fp = os.path.join(dirpath, fn)
            if reqs_abs and os.path.normcase(os.path.abspath(fp)).startswith(reqs_abs + os.sep):
                continue
            rel = os.path.relpath(fp, code_root).replace("\\", "/")
            if any(fnmatch.fnmatch(rel, p) for p in ignore):
                continue
            # Group by first path component (top-level directory or "." for root files)
            parts = rel.split("/")
            label = parts[0] if len(parts) > 1 else "."
            if label not in buckets:
                buckets[label] = [0, 0]
            buckets[label][0] += 1
            if os.path.normcase(os.path.abspath(fp)) in tagged_files:
                buckets[label][1] += 1

    rows = []
    for label in sorted(buckets):
        total, tagged = buckets[label]
        pct = round(100 * tagged / total) if total else 0
        rows.append({"dir": label, "total": total, "tagged": tagged, "pct": pct})

    if as_json:
        print(json.dumps(rows, indent=2))
        return 0

    if not rows:
        print("No scannable files found.")
        return 0

    w = max(len(r["dir"]) for r in rows)
    for r in rows:
        bar = "#" * (r["pct"] // 5) + "." * (20 - r["pct"] // 5)
        print("{:<{w}}  {:>3}/{:<3}  ({:>3}%)  [{}]".format(
            r["dir"], r["tagged"], r["total"], r["pct"], bar, w=w))
    total_all = sum(r["total"] for r in rows)
    tagged_all = sum(r["tagged"] for r in rows)
    pct_all = round(100 * tagged_all / total_all) if total_all else 0
    print("\nTotal: {}/{} files tagged ({:>3}%)".format(tagged_all, total_all, pct_all))
    return 0


def _link_sync_errors(reqs, members):
    """The two ERROR-level link-sync predicates `gate` enforces on a full scan:
    a code tag pointing at a requirement id that does not exist, and an
    ENFORCED-status requirement with no `implements:` member (`need`-layer
    requirements are exempt — covered by `satisfies:` edges, not code).
    Mirrors cmd_check's own checks so `health` can reflect gate's error state
    without a second, independently-maintained walk of `members`. Deliberately
    narrow: this does NOT catch a value changed with no supporting tag at all
    (nothing points at it, so there is no dangling reference and no missing-
    implements) — see RM-6 / Senate run reqmap-health-gate-cleanliness."""
    errs = []
    cap_ids = set(reqs)
    for cap in members:
        if cap not in cap_ids:
            errs.append(f"dangling tag: code references {cap} but no requirement exists")
    for rid, r in reqs.items():
        m = r["meta"]
        if _impl_exempt(m):
            continue
        impls = [x for x in members.get(rid, []) if x[0] == "implements"]
        if m.get("status") in ENFORCED and not impls:
            errs.append(f"{rid}: status {m['status']} but no implements: tag found in code")
    return errs


def _dependency_cycles(reqs):  # implements: ARCH-CHECK-006
    """Every `depends_on` cycle in the registry, as a list of id lists, each ending
    where it began (`A, B, C, A`). Deterministic: nodes and edges are walked in
    sorted order, so the same corpus always reports the same cycles in the same
    shape.

    A cycle means the layering claim is false — no requirement in it can be built
    before the others — and nothing looked for one. It surfaced as a rendering
    artifact instead: the viewer ranks by longest path, which never converges on a
    cycle, so a 59-requirement corpus with three cycles laid out 236 columns wide
    and drew its edges as endless horizontal lines. That is the symptom; this is
    the cause, and it belongs in the gate's report, not in a diagram."""
    adj = {rid: [d for d in sorted(_as_list(r["meta"].get("depends_on"))) if d in reqs]
           for rid, r in reqs.items()}
    state, stack, cycles, seen = {}, [], [], set()
    for root in sorted(adj):
        if state.get(root):
            continue
        # iterative DFS — a deep chain must not hit the interpreter's recursion limit
        work = [(root, iter(adj[root]))]
        state[root] = 1
        stack.append(root)
        while work:
            node, it = work[-1]
            nxt = next(it, None)
            if nxt is None:
                state[node] = 2
                stack.pop()
                work.pop()
                continue
            if state.get(nxt) == 1:                      # closes a cycle
                cyc = stack[stack.index(nxt):] + [nxt]
                key = frozenset(cyc)
                if key not in seen:
                    seen.add(key)
                    cycles.append(cyc)
            elif state.get(nxt) != 2:
                state[nxt] = 1
                stack.append(nxt)
                work.append((nxt, iter(adj[nxt])))
    return cycles


def _commits_since_reqs_touch(code_root, reqs_dir):  # implements: ARCH-REGISTRYLAG-035
    """Count commits on HEAD since the last commit that touched `reqs_dir`.

    The advisory "registry lag" signal: a large number means the registry has
    sat frozen while code raced ahead of it — the exact 18-day-freeze condition
    that let a money value drift with no requirement update. Returns None (not 0)
    when unmeasurable — git missing, `code_root` not a git worktree, or `reqs_dir`
    has no commit in history — so the reading is absent rather than falsely 0.
    Read-only; never a gate, never enters the score."""
    try:
        last = subprocess.run(
            ["git", "-C", code_root, "log", "-1", "--format=%H", "--", reqs_dir],
            capture_output=True, text=True, timeout=5)
        sha = last.stdout.strip()
        if last.returncode != 0 or not sha:
            return None
        cnt = subprocess.run(
            ["git", "-C", code_root, "rev-list", "--count", f"{sha}..HEAD"],
            capture_output=True, text=True, timeout=5)
        if cnt.returncode != 0:
            return None
        return int(cnt.stdout.strip())
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def cmd_health(reqs, members, reqs_dir, as_json=False, as_badge=False, code_root=None):  # implements: ARCH-HEALTH-017
    """Print a corpus coherence snapshot: a headline score plus component counts.
    The score is transparent — the percentage of requirements green on EVERY axis
    (confirmed, has an `implements` member, tested-or-`test_exempt`, no open
    verify-intent, not drifted vs the lock). A `layer: need` is covered by ≥1
    `satisfies:` edge instead of code and its test axis is waived, mirroring how
    `check` treats the need layer. `--json` emits the same numbers as a
    parseable object for a CI badge. Read-only, always exit 0.

    `gate_errors`/`gate_link_sync_clean` (informational, never enters `score`):
    the count of `gate`'s own ERROR-level link-sync problems (dangling tags,
    enforced-status requirements with no `implements:` member), so a 100/100
    reading here can no longer coexist with an unseen `gate` failure — see
    RM-6 (Senate run reqmap-health-gate-cleanliness). This does NOT detect a
    value changed with no tag at all; that class of drift needs a sourced/
    `validated-against:` convention on the changed file, which is out of
    scope for this signal."""
    total = len(reqs)
    lock = load_lock(reqs_dir)
    satisfied = set()  # need ids with >=1 `satisfies:` edge (ARCH-TRACE-020)
    for r in reqs.values():
        satisfied.update(_as_list(r["meta"].get("satisfies")))
    confirmed = implemented = tested = orphans = untested = open_intent = drifted = drafts = healthy = 0
    for rid, r in reqs.items():
        m, body = r["meta"], r["body"]
        status = m.get("status", "draft")
        roles = _member_roles(members.get(rid, []))
        has_impl = "implements" in roles
        # a need is covered by being satisfied, not implemented, and its test
        # axis is waived — a need is fulfilled by requirements, not by code.
        # An aggregate is covered the same way, downward: by its depends_on edges.
        is_need = m.get("layer") == "need"
        covered = has_impl
        if is_need:
            covered = rid in satisfied
        elif _impl_exempt(m):                     # aggregate: covered by its dependencies
            covered = bool(_as_list(m.get("depends_on")))
        has_test_member = "tested-by" in roles
        has_test = has_test_member or bool(m.get("test_exempt"))
        is_confirmed = status == "confirmed"
        open_now = status != "draft" and any(
            b and not b.lstrip("*_ ").lower().startswith("none")
            for b in _bullets(body, "verify intent"))
        old = lock.get(rid)
        is_drifted = bool(old) and old != binding_hash(body) and is_confirmed
        confirmed += is_confirmed
        implemented += has_impl
        tested += has_test_member
        drafts += status == "draft"
        orphans += is_confirmed and not covered
        untested += has_impl and not has_test_member and not m.get("test_exempt")
        open_intent += open_now
        drifted += is_drifted
        if is_confirmed and covered and (has_test or is_need) and not open_now and not is_drifted:
            healthy += 1
    score = round(100 * healthy / total) if total else 0
    gate_errors = _link_sync_errors(reqs, members)
    data = {"score": score, "total": total, "healthy": healthy,
            "confirmed": confirmed, "implemented": implemented, "tested": tested,
            "drafts": drafts, "orphans": orphans, "untested": untested,
            "open_intent": open_intent, "drift": drifted,
            "gate_errors": len(gate_errors), "gate_link_sync_clean": not gate_errors}
    # Untagged-code coverage signal (read-only): count of scannable code files
    # carrying no membership tag — code traced to no requirement. Reuses
    # _scan_untagged (ARCH-NEXT-013). Informational only: it counts FILES, not
    # requirements, so it never enters the per-requirement score, and it is
    # absent (not zero) when no code root is available, e.g. a unit-test caller.
    # implements: ARCH-COVERAGE-029
    untagged = _scan_untagged(code_root, reqs_dir) if code_root else None
    if untagged is not None:
        data["untagged"] = len(untagged)
    # Registry-lag signal (read-only): commits since requirements/ was last
    # touched — a frozen registry while code moves ahead. Absent (not 0) when
    # unmeasurable (no git / no code root), like `untagged`. implements: ARCH-REGISTRYLAG-035
    lag = _commits_since_reqs_touch(code_root, reqs_dir) if code_root else None
    if lag is not None:
        data["commits_since_req_touch"] = lag
    # Roadmap signals (read-only): does TODO.md still track what shipped, and does every
    # section heading actually parse as a milestone. Absent (not empty) when the repo has
    # no TODO.md, so a repo that does not keep one sees nothing. implements: ARCH-ROADMAP-038
    roadmap = _roadmap_signals(code_root) if code_root else None
    if roadmap is not None:
        newest_req = max((m["milestone"] for m in (r["meta"] for r in reqs.values())
                          if m.get("milestone")), key=_version_key, default=None)
        if roadmap["newest_milestone"] and newest_req and                 _version_key(roadmap["newest_milestone"]) < _version_key(newest_req):
            data["roadmap_behind"] = {"todo": roadmap["newest_milestone"],
                                      "requirements": newest_req}
        if roadmap["unversioned_headings"]:
            data["roadmap_unversioned_headings"] = roadmap["unversioned_headings"]
    if as_badge:
        color = "brightgreen" if score == 100 else "green" if score >= 80 else "yellow" if score >= 60 else "red"
        message = "{}/{} | {}%".format(confirmed, total, score)
        # a badge cannot read "clean" while gate has link-sync errors gate itself
        # would fail on — this is the exact false-positive RM-6 closes.
        if gate_errors:
            color = "red"
            message += " | gate:{}".format(len(gate_errors))
        badge = {"schemaVersion": 1, "label": "requirements",
                 "message": message, "color": color}
        print(json.dumps(badge))
        return 0
    if as_json:
        print(json.dumps(data, indent=2))
        return 0
    print("Requirement health: {}/100  ({}/{} green on every axis)".format(score, healthy, total))
    print("  confirmed:   {}/{}".format(confirmed, total))
    print("  implemented: {}/{}".format(implemented, total))
    print("  tested:      {}/{}".format(tested, total))
    print("  drafts:      {}".format(drafts))
    if orphans:     print("  orphans (confirmed, no code):     {}".format(orphans))
    if untested:    print("  untested (code, no tests):        {}".format(untested))
    if open_intent: print("  open verify-intent:               {}".format(open_intent))
    if drifted:     print("  drift (contract changed vs lock): {}".format(drifted))
    if gate_errors: print("  gate link-sync errors (not clean):{}".format(len(gate_errors)))
    if untagged:    print("  untagged code (no requirement):   {}".format(len(untagged)))
    if lag:         print("  commits since requirements touched:{}".format(lag))
    if total == 0:
        print("  (no requirements yet — run `reqmap.py init` or `new`)")
    return 0


def _strip_line_tag(line):
    """Remove a reqmap membership-tag comment from a source line.

    Strips only when a comment marker (#, //, <!--) *directly opens* the tag —
    i.e. nothing but whitespace sits between the marker and the tag id. A line
    that merely mentions a tag in prose or a heading (e.g. a doc line
    `# How implements: AREA-NAME-001 tags work`, or
    `<!-- note --> ... implements: AREA-NAME-001 is required <!-- end -->`) is
    left unchanged, so `init --wipe` never truncates documentation that
    documents the tagging convention. A multi-char heading/banner marker
    (`## `, `//// `) is removed whole rather than leaving a dangling bare `#`.
    Lines with no tag are returned unchanged."""
    m = TAG_RE.search(line)
    if m is None:
        return line
    pre = line[:m.start()]
    nl = "\n" if line.endswith("\n") else ""
    cut = -1
    for marker in ("#", "//", "<!--"):
        idx = pre.rfind(marker)
        # the marker opens the tag's comment only when the gap between the
        # marker token and the tag id is whitespace-only; otherwise it is an
        # unrelated heading / inline comment and must not anchor the cut
        if idx > cut and pre[idx + len(marker):].strip() == "":
            cut = idx
    if cut < 0:
        return line  # no comment marker directly opens the tag — leave unchanged
    # walk back over a contiguous run of the same marker char (`## `, `//// `)
    # so the whole heading/banner marker is removed, not just its last char
    while cut > 0 and pre[cut - 1] == pre[cut]:
        cut -= 1
    return line[:cut].rstrip() + nl


def _wipe(reqs_dir, code_root):
    """Hard-reset: delete non-generated requirement files (names not starting
    with `_`) and strip membership tags from every scanned source file so that
    `cmd_extract` can re-draft from a clean slate."""
    deleted = 0
    if os.path.isdir(reqs_dir):
        for fn in os.listdir(reqs_dir):
            if fn.endswith(".md") and not fn.startswith("_"):
                try:
                    os.remove(os.path.join(reqs_dir, fn))
                    deleted += 1
                except OSError:
                    pass
    stripped_files = 0
    ignore = load_ignore(code_root, reqs_dir)
    for dirpath, dirs, files in os.walk(code_root):
        _prune_dirs(dirpath, dirs, reqs_dir)
        for fn in files:
            if not _is_code_file(fn):
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, code_root).replace(os.sep, "/")
            if any(fnmatch.fnmatch(rel, pat) for pat in ignore):
                continue
            try:
                # surrogateescape (read AND write) round-trips any non-UTF-8 bytes
                # verbatim, so stripping a tag never silently corrupts e.g. a
                # Latin-1 comment elsewhere in the file (errors="ignore" dropped them).
                with open(fp, encoding="utf-8", errors="surrogateescape") as f:
                    lines = f.readlines()
                new_lines = [_strip_line_tag(l) for l in lines]
                if new_lines != lines:
                    with open(fp, "w", encoding="utf-8", errors="surrogateescape") as f:
                        f.writelines(new_lines)
                    stripped_files += 1
            except OSError:
                continue
    print("wipe: deleted {} requirement file(s), stripped tags from {} source file(s).".format(
        deleted, stripped_files))


def _reqmapignore_seed(code_root, reqs_dir):  # implements: ARCH-INIT-012
    """Content for a freshly-seeded `.reqmapignore`. Normally ignores the vendored
    engine at `scripts/reqmap.py` — its `implements:` self-tags would otherwise read
    as dangling refs in a consumer repo. EXCEPTION — a self-hosting repo: when that
    file carries membership tags that resolve to requirements already present, the
    engine IS the managed code and must stay scanned, so the line is omitted (a
    comment explains why) to avoid orphaning those requirements."""
    header = ("# Paths reqmap should not scan (one fnmatch glob per line, # comments ok).\n"
              "# The bundled single-file viewer is a generated artifact, never a member.\n"
              "scripts/_map_viewer.html\n"
              "# Isolated agent worktrees. Each holds a FULL second copy of this repo, so a\n"
              "# local scan counts every member twice and reads the copies' tags as dangling\n"
              "# refs — errors that do not exist in the code, in files CI never checks out.\n"
              "# Both spellings: Claude Code creates `.claude/worktrees/`, older\n"
              "# parallel-session tooling `.worktrees/`.\n"
              ".worktrees/**\n"
              ".claude/worktrees/**\n")
    engine = os.path.join(code_root, "scripts", "reqmap.py")
    req_ids = set(load_requirements(reqs_dir))
    if req_ids and os.path.isfile(engine):
        try:
            with open(engine, encoding="utf-8") as f:
                tagged = {cap for (_role, cap) in _findall_tags(f.read())}   # expand comma-lists like scan_members
        except OSError:
            tagged = set()
        if tagged & req_ids:   # self-hosting: the engine's tags point at local reqs
            return (header +
                    "# scripts/reqmap.py is intentionally NOT ignored: this repo hosts its own\n"
                    "# requirements there (its membership tags resolve to local requirements), so\n"
                    "# the engine must stay scanned. Add other vendored/generated paths below.\n")
    return (header +
            "# The engine carries its own `implements:` self-tags; ignore it so the\n"
            "# gate does not flag them as dangling refs.\n"
            "scripts/reqmap.py\n")


def cmd_init(reqs_dir, code_root, wipe=False, no_site=False):  # implements: ARCH-INIT-012
    """First-use bootstrap for a fresh repo: create requirements/, seed a minimal
    .reqmapignore (idempotent — never clobbers an existing one), draft requirements
    from existing code, build the lock + map, then print guided next steps.
    Pass wipe=True (--wipe flag) for a hard reset: all non-generated requirement
    files are deleted and membership tags stripped from source before re-extracting."""
    if wipe:
        _wipe(reqs_dir, code_root)
    created = []
    if not os.path.isdir(reqs_dir):
        os.makedirs(reqs_dir, exist_ok=True)
        created.append(os.path.relpath(reqs_dir, code_root).replace(os.sep, "/") + "/")
    ignore = os.path.join(code_root, ".reqmapignore")
    if not os.path.exists(ignore):
        with open(ignore, "w", encoding="utf-8") as f:
            f.write(_reqmapignore_seed(code_root, reqs_dir))
        created.append(".reqmapignore")
    print("Bootstrapping draft requirements from existing code...\n")
    reqs = load_requirements(reqs_dir)
    members = scan_members(code_root, reqs_dir)
    cmd_extract(reqs, members, code_root, reqs_dir)
    # extract wrote new files -> reload before locking + mapping
    reqs = load_requirements(reqs_dir)
    members = scan_members(code_root, reqs_dir)
    cmd_check(reqs, members, reqs_dir, update_lock=True, code_root=code_root)
    cmd_map(reqs, members, reqs_dir, code_root)
    # implements: ARCH-SITE-026 — best-effort project site. Never aborts init.
    if not no_site:
        target = _site_default_target(code_root)
        if target:
            try:
                _site_pages_bootstrap(os.path.dirname(target))   # .nojekyll + index.html redirect
                cmd_site(reqs, members, code_root, attach=target, regions=["nav", "stats"])
            except Exception as e:   # site is decorative; a failure must not break bootstrap
                print("note: site step skipped ({}).".format(e))
        else:
            print("note: no docs/ folder — run the requirement-manager skill to set up a project site.")
    print("\n" + "=" * 60)
    if not reqs:   # nothing to extract — don't masquerade as "all clean"
        print("reqmap initialized, but no requirements were extracted")
        print("(no supported source files found, or all are ignored by .reqmapignore).")
        if created:
            print("created: " + ", ".join(created))
        print("\nNext: author your first requirement with `reqmap.py new AREA-NAME-NNN`.")
        return 0
    print("reqmap initialized — {} requirement(s) tracked.".format(len(reqs)))
    if created:
        print("created: " + ", ".join(created))
    print("\nNext: run `reqmap.py next` — it shows what to do, most important first.")
    print("Then wire the gate: add `python scripts/reqmap.py gate` to your pre-commit hook.")
    return 0


def _strip_generated(text):
    """Drop volatile lines so a freshness diff compares content, not the
    environment: the `generated: <timestamp>` frontmatter line (`_map.md`) and the
    `"repo": ...` field (`_map.json`), which is git-derived and differs across
    forks/clones — comparing it would make `map --check` spuriously fail on a fork."""
    return "\n".join(l for l in text.splitlines()
                     if not l.startswith("generated: ")
                     and not l.lstrip().startswith('"repo":')
                     and not l.lstrip().startswith('"engine_version":'))


_ENGINE_STAT_RE = re.compile(r'<div class="stat"><b>[^<]*</b><span>engine</span></div>')


def _strip_engine_stat(html):  # implements: ARCH-SITE-026
    """Drop the `engine` stat cell before a site STATS-region freshness diff — it
    embeds the live MAP_ENGINE_VERSION, which changes on every engine change
    independent of requirement content, mirroring the `repo`/`engine_version`
    exclusions `_strip_generated` already applies to `_map.md`/`_map.json` for the
    same reason (a routine engine bump must not flag a committed site page stale)."""
    return _ENGINE_STAT_RE.sub("", html)


def _stale_artifacts(data, reqs_dir, root=".", reqs=None):  # implements: ARCH-MAP-007
    """Names of the committed generated artifacts that no longer match a fresh
    render of `data` — the whole of the freshness verdict, with no printing and no
    exit code, so `map --check` (which fails) and `gate` (which warns) read the same
    answer instead of implementing it twice."""
    stale = []
    for name, fresh in (("_map.md", _build_md_text(data)),
                        ("_map.json", _build_json_text(data))):
        path = os.path.join(reqs_dir, name)
        if not os.path.exists(path):
            continue   # nothing committed to be stale against
        with open(path, encoding="utf-8") as f:
            on_disk = f.read()
        if _strip_generated(on_disk) != _strip_generated(fresh):
            stale.append(name)
    # Committed findings report: derived from the requirements' verify-intent bullets,
    # so a committed copy goes stale exactly like _map.* does (this repo's sat stale
    # for eleven weeks). Absent = never generated = not stale, same convention.
    findings_out = os.path.join(reqs_dir, "_findings.md")  # implements: ARCH-FINDINGS-010
    if reqs is not None and os.path.exists(findings_out):
        with open(findings_out, encoding="utf-8") as f:
            on_disk = f.read()
        if on_disk != _render_findings(reqs, reqs_dir)[0]:
            stale.append("_findings.md")
    # Published GitHub Pages copy: docs/map.html must equal a fresh viewer render.
    # Reading text-mode (not bytes) normalises CRLF/LF so a copy written on Windows
    # is not falsely flagged against the LF in-memory render. The comparison runs
    # through _strip_generated for the same reason _map.json does: the injected blob
    # embeds the git-derived `repo` field, which differs across forks/clones — left
    # in, it would make `map --check` spuriously fail on any fork.
    docs_out = _docs_publish_path(root)  # implements: ARCH-PAGES-021
    tpl = _viewer_template_path()
    if docs_out and os.path.exists(docs_out) and os.path.exists(tpl):
        with open(tpl, encoding="utf-8") as f:
            fresh_html = _inject_viewer(f.read(), data)
        with open(docs_out, encoding="utf-8") as f:
            docs_html = f.read()
        if _strip_generated(docs_html) != _strip_generated(fresh_html):
            stale.append(os.path.basename(docs_out))
    # Site presentation page: gate the deterministic STATS region only. NAV embeds
    # the git-derived repo URL (fork-specific) and is excluded, mirroring the
    # `repo`-field exclusion in _strip_generated.  # implements: ARCH-SITE-026
    site_target = _site_default_target(root)
    if site_target and os.path.exists(site_target):
        with open(site_target, encoding="utf-8") as f:
            on_disk = f.read()
        disk_stats = _extract_region(on_disk, "stats")
        if disk_stats is not None:
            ctx = _site_context_from_data(data, repo_url=None, map_ok=False, diagram_rel=None)
            fresh_stats = _render_region("stats", ctx)
            if _strip_engine_stat(disk_stats) != _strip_engine_stat(fresh_stats):
                stale.append(os.path.basename(site_target))
    return stale


def _map_check(data, reqs_dir, root=".", reqs=None):  # implements: ARCH-MAP-007
    """Freshness gate: regenerate the map in memory and compare to the committed
    files. Stale (committed != freshly-built) -> exit 1 so a code/requirement edit
    that shifts the map can't be committed without regenerating it. A map that was
    never generated (file absent) is NOT stale — consumers who don't track maps pass.
    The `generated:` timestamp is ignored so an unchanged map never trips on time."""
    stale = _stale_artifacts(data, reqs_dir, root, reqs)
    if stale:
        print("FAIL  map is stale: {} — run `reqmap.py sync` and commit the result."
              .format(", ".join(stale)))
        return 1
    print("OK  map is fresh.")
    return 0


def _title(body):  # implements: ARCH-MAP-007
    """The human title from the requirement's first `# ` heading."""
    for line in body.splitlines():
        if line.strip().startswith("# "):
            return line.strip()[2:].strip()
    return ""


def _first_quote(body):  # implements: ARCH-MAP-007
    """The requirement's intent: the FIRST contiguous blockquote (the WHY), joined into
    one line. A multi-line `>` WHY (a richer plain-language summary) is gathered whole,
    not truncated to its first line. Fenced code is skipped so a `>` inside a fence
    never counts."""
    out, started, in_fence = [], False, False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if s.startswith(">"):
            content = s.lstrip(">").strip()
            if content:
                out.append(content)
            started = True
        elif started:            # first non-quote line after the block ends it
            break
    return " ".join(out)


def _section(body, name):  # implements: ARCH-MAP-007
    out, grab, seen, fenced = [], False, False, False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):
            fenced = not fenced               # a `## ` inside a fence is code, not a boundary
            continue
        if fenced:
            continue
        if s.lower().startswith("## "):
            grab = (not seen) and _heading_label_is(s, name)   # anchored, like _bullets
            if grab:
                seen = True
            continue
        if grab and s and not s.startswith("<!--"):
            out.append(s.lstrip("- "))
    return " ".join(out)


def _section_raw(body, name):  # implements: ARCH-MAP-007
    """Like _section but preserves line breaks + indentation — used for the
    multi-line Given/When/Then acceptance blocks so they read as written."""
    out, grab, seen, fenced = [], False, False, False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):
            fenced = not fenced               # a `## ` inside a fence is code, not a boundary
            continue
        if fenced:
            continue
        if s.lower().startswith("## "):
            grab = (not seen) and _heading_label_is(s, name)   # anchored, like _bullets
            if grab:
                seen = True
            continue
        if grab and not s.startswith("<!--"):
            out.append(line.rstrip())
    return "\n".join(out).strip()


def _is_label_line(line):  # implements: ARCH-MAP-007
    """True when `line` is a clause-group label: a bold-only line at column 0.

    The authoring voice groups clauses under bold labels once a contract passes
    five, and those labels are headings, not prose — folding one into the bullet
    above appends the NEXT group's title to the PREVIOUS group's last clause.

    Position, not marker shape, separates a label from a wrapped clause. A label
    is written flush left; a hanging-indent continuation is indented. Shape alone
    cannot tell them apart: a wrapped line may legitimately open and close on bold
    spans, and matching that as a heading silently deleted the containment half of
    a two-part join predicate. Pass the RAW line — a stripped string makes every
    clause look flush left and collapses the section to headings."""
    return not line[:1].isspace() and re.fullmatch(r"\*\*.+\*\*", line.strip()) is not None


def _bullets(body, name):  # implements: ARCH-MAP-007  # implements: ARCH-ATOMICFORM-053
    if name in CONTRACT_LABELS:
        _sp = _atomic_spans(body)
        if _sp:                                    # the atomic statement is the one clause
            return [" ".join(l.lstrip("> ").strip() for l in _sp[0]).strip()]
    out, grab, seen, fenced = [], False, False, False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):
            fenced = not fenced               # a `## ` inside a fence is code, not a boundary
            continue
        if fenced:
            continue
        if s.lower().startswith("## "):
            # anchored heading match (not substring) so a commentary heading like
            # `## Notes — contract caveats` doesn't capture the Contract section
            grab = (not seen) and _heading_label_is(s, name)
            if grab:
                seen = True
            continue
        if not grab:
            continue
        if s.startswith("-"):
            out.append(s[1:].strip())
        elif _is_label_line(line):
            # A clause-group label — a heading, not prose. Folding it in would append
            # the NEXT group's title to the previous group's last clause, which then
            # leaks into `show`, the map, and the dupes/search bag of words. The test
            # is positional (see _is_label_line), so an indented wrapped clause that
            # merely opens and closes on bold spans still folds below.
            continue
        elif s and not s.startswith("<!--") and out:
            # hanging-indent continuation of the current bullet — fold it back in
            # so multi-line clauses are not truncated to their first physical line.
            out[-1] = (out[-1] + " " + s).strip()
    return out


def _context_group(body, label):  # implements: ARCH-CONTEXT-048
    """Bullets under a bold `**<label>**` sub-group inside the consolidated
    `## Context (non-binding)` section — the form `new`'s template scaffolds since
    ADR-0017, replacing the legacy per-topic `## WHAT — Notes` / `## WHERE — Current
    implementation` headings for newly-authored requirements. Reuses the existing
    bold-label grouping convention (`_is_label_line`, already used by Contract
    clause-groups) rather than inventing a second syntax. Callers try the legacy
    heading via `_bullets()` first — this is the fallback for files that never had
    one, so an old-schema requirement is completely unaffected."""
    out, in_context, in_label, fenced = [], False, False, False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if s.lower().startswith("## "):
            in_context = _heading_label_is(s, "context")
            in_label = False
            continue
        if not in_context:
            continue
        if _is_label_line(line):
            in_label = s.strip("*").strip().lower() == label.lower()
            continue
        if not in_label:
            continue
        if s.startswith("-"):
            out.append(s[1:].strip())
        elif s and not s.startswith("<!--") and out:
            out[-1] = (out[-1] + " " + s).strip()
    return out


# ---------- mermaid generators ----------
def _safe_id(rid):
    """Mermaid-safe node ID: replace non-alphanumeric chars with underscores."""
    return re.sub(r"[^A-Za-z0-9]", "_", rid)


def _mlabel(text):
    """Make free text safe inside a quoted Mermaid node label.

    Even inside quotes, Mermaid's parser chokes on backticks, brackets,
    braces, pipes and backslashes; under securityLevel:loose, angle
    brackets would also be rendered as HTML. Neutralize all of them.
    """
    text = text or "—"
    for a, b in (('"', "'"), ("`", "'"), ("[", "("), ("]", ")"),
                 ("{", "("), ("}", ")"), ("|", "/"), ("\\", "/"),
                 ("<", "‹"), (">", "›")):
        text = text.replace(a, b)
    return text


def _node_label(n):
    """Two-line node label: human title big, capability id small below.

    The `<br>`/`<small>` tags are added outside `_mlabel` (which would
    otherwise neutralize the angle brackets); only the title text is
    passed through the sanitizer.
    """
    title = _mlabel(n.get("title") or n["id"])
    return "{}<br><small>{}</small>".format(title, _mlabel(n["id"]))


def _area_of(rid):  # implements: ARCH-MAP-007
    """Capability 'area' = the first id segment (BUS-PATHS-001 -> BUS). Used to
    cluster a large System Map into per-area subgraphs so 40+ nodes stay legible."""
    return rid.split("-", 1)[0] or rid


def _node_area(n):  # implements: ARCH-MAP-007
    """Grouping key for a node: an explicit `area:` frontmatter field wins (lets a
    repo group e.g. several standalone capabilities under one ANALYSIS box without
    renaming ids); otherwise fall back to the id prefix."""
    return (n.get("area") or "").strip() or _area_of(n["id"])


def _grouped_areas(nodes):  # implements: ARCH-MAPDIAGRAMS-055
    """Order nodes into [(area_label, [node,...]), ...]: multi-node areas first
    (sorted), then one 'misc' bucket of every single-node area. Shared by the
    System / Dependency / Risk diagrams so a 40+ node map stays navigable
    (Miller 7+-2 / C4 levels — split a big diagram by meaningful boundary)."""
    areas = {}
    for n in nodes:
        areas.setdefault(_node_area(n), []).append(n)
    groups = [(a, areas[a]) for a in sorted(areas) if len(areas[a]) > 1]
    singles = [n for a in sorted(areas) if len(areas[a]) == 1 for n in areas[a]]
    if singles:
        # fold the singletons into any pre-existing real "misc" multi-node group
        # rather than appending a second ("misc", …) tuple — two subgraphs with
        # the same _safe_id would break the Mermaid render
        existing = next((i for i, (a, _) in enumerate(groups) if a == "misc"), None)
        merged = sorted(singles, key=lambda n: n["id"])
        if existing is not None:
            groups[existing] = ("misc", groups[existing][1] + merged)
        else:
            groups.append(("misc", merged))
    return groups


def _emit_area_subgraphs(lines, nodes, label_fn=None):
    """Append per-area `subgraph` blocks (singletons collapse into 'misc')."""
    label_fn = label_fn or _node_label
    sg_used = {}
    for area, ns in _grouped_areas(nodes):
        base = _safe_id(area)
        k = sg_used.get(base, 0) + 1
        sg_used[base] = k
        # suffix on collision so two areas that sanitize to the same id (my-area /
        # my_area) don't emit duplicate `subgraph` ids and break the Mermaid render
        sg = base if k == 1 else "{}_{}".format(base, k)
        lines.append('  subgraph sg_{}["{}"]'.format(sg, area))
        for n in ns:
            lines.append('    {}["{}"]'.format(_safe_id(n["id"]), label_fn(n)))
        lines.append("  end")


def _bus_ids(nodes):
    return [n["id"] for n in nodes if n.get("layer") == "bus"]


def _hub_targets(data, bus_ids):
    """Bus nodes + any node with fan-in >= SYSTEM_HUB_FANIN (the hub hairball)."""
    fanin = {}
    for _src, tgt in data["edges"]:
        fanin[tgt] = fanin.get(tgt, 0) + 1
    return set(bus_ids) | {nid for nid, c in fanin.items() if c >= SYSTEM_HUB_FANIN}


def _mermaid_system(data):  # implements: ARCH-MAPDIAGRAMS-055
    # Per-area subgraphs + hide edges into bus/hubs (the hairball); the full graph
    # is in the Dependency Map. Bus nodes keep a thick stroke.
    lines = ["graph LR"]   # left-right fills a wide/landscape area better than top-down
    bus_ids = _bus_ids(data["nodes"])
    _emit_area_subgraphs(lines, data["nodes"])
    hubs = _hub_targets(data, bus_ids)
    for a, b in data["edges"]:
        if b not in hubs:
            lines.append("  {} --> {}".format(_safe_id(a), _safe_id(b)))
    for bid in bus_ids:
        lines.append("  style {} stroke-width:3px".format(_safe_id(bid)))
    return "\n".join(lines)


def _mermaid_hierarchy(data):  # implements: ARCH-MAPDIAGRAMS-055
    """The specification hierarchy: system -> architecture, over `satisfies:` edges.

    Drawn from `upstream_edges`, not `depends_on` — those are different axes, and only this
    one forms a hierarchy. The `code` level is counted, never drawn: a corpus that has split
    its clauses carries hundreds of them, and past a few hundred nodes Mermaid stops being
    something a reader can take in (or GitHub renders at all). Each architecture box shows
    how many code requirements sit under it, which is the fan-out the band judges."""
    levels = {n["id"]: n.get("level") for n in data["nodes"]}
    drawn = [n for n in data["nodes"] if levels.get(n["id"]) in ("system", "architecture")]
    if not drawn:
        return ""
    kids = {}
    for child, parent in data.get("upstream_edges", []):
        if levels.get(child) == "code":
            kids[parent] = kids.get(parent, 0) + 1
    lines = ["graph TD"]
    for n in drawn:
        rid = n["id"]
        label = rid if levels[rid] == "system" else "{}<br/>{} code".format(rid, kids.get(rid, 0))
        shape = "[[{}]]" if levels[rid] == "system" else "[{}]"
        lines.append("  {}{}".format(_safe_id(rid), shape.format(label)))
    for child, parent in data.get("upstream_edges", []):
        if levels.get(child) in ("system", "architecture") and parent in levels:
            lines.append("  {} --> {}".format(_safe_id(parent), _safe_id(child)))
    for n in drawn:
        if levels[n["id"]] == "system":
            lines.append("  style {} stroke-width:3px".format(_safe_id(n["id"])))
    return "\n".join(lines)


def _mermaid_deps(data):  # implements: ARCH-MAPDIAGRAMS-055
    # Area-level coupling overview (C4 'container' zoom-out): one box per area, an
    # edge A->B when ANY capability in A depends on one in B. Aggregating the
    # per-capability edges here kills the bus hub hairball; the System Map keeps
    # the per-capability detail and the detail panel lists each node's deps.
    groups = _grouped_areas(data["nodes"])
    if not groups:
        return 'graph LR\n  none["(no requirements)"]'
    label_of, counts, bus_areas = {}, {}, set()
    for label, ns in groups:
        counts[label] = len(ns)
        for n in ns:
            label_of[n["id"]] = label
            if n.get("layer") == "bus":
                bus_areas.add(label)
    edges = set()
    for a, b in data["edges"]:
        la, lb = label_of.get(a), label_of.get(b)
        if la and lb and la != lb:
            edges.add((la, lb))
    lines = ["graph LR"]
    for label in sorted(counts):
        lines.append('  a_{}["{}<br><small>{} caps</small>"]'.format(
            _safe_id(label), _mlabel(label), counts[label]))
    for la, lb in sorted(edges):
        lines.append("  a_{} --> a_{}".format(_safe_id(la), _safe_id(lb)))
    for label in sorted(bus_areas):
        lines.append("  style a_{} stroke-width:3px".format(_safe_id(label)))
    return "\n".join(lines)


def _mermaid_req_to_code(data):  # implements: ARCH-MAPDIAGRAMS-055
    lines = ["graph LR"]
    loc_sid, sid_used = {}, {}        # distinct file:line locs must get distinct node ids
    for n in data["nodes"]:
        rid = n["id"]
        sid = _safe_id(rid)
        lines.append('  {}["{}"]'.format(sid, _node_label(n)))
        if not n["members"]:
            # enforced-but-unlinked is a real gap (red); a baseline/draft not yet
            # tagged is expected, so render it muted grey rather than alarming red
            if n.get("status") in ENFORCED:
                lines.append("  style {} fill:#fee,stroke:#c66".format(sid))
            else:
                lines.append("  style {} fill:#eee,stroke:#bbb,color:#888".format(sid))
            continue
        # group by role+file, compute min/max line numbers
        groups = {}
        for m in n["members"]:
            c = m["loc"].rfind(":")
            f, ln = m["loc"][:c], int(m["loc"][c + 1:])
            k = m["role"] + "|" + f
            if k not in groups:
                groups[k] = {"role": m["role"], "f": f, "min": ln, "max": ln}
            else:
                groups[k]["min"] = min(groups[k]["min"], ln)
                groups[k]["max"] = max(groups[k]["max"], ln)
        for g in groups.values():
            loc = "{}:{}".format(g["f"], g["min"]) if g["min"] == g["max"] \
                  else "{}:{}-{}".format(g["f"], g["min"], g["max"])
            if loc in loc_sid:
                file_sid = loc_sid[loc]
            else:
                base = "f_" + re.sub(r"[^A-Za-z0-9]", "_", loc)
                k = sid_used.get(base, 0) + 1
                sid_used[base] = k
                # suffix on collision so two different locs that sanitize to the same
                # id (e.g. a-b.py vs a_b.py) don't merge into one mislabeled node
                file_sid = base if k == 1 else "{}_{}".format(base, k)
                loc_sid[loc] = file_sid
            lines.append('  {}["{}"]'.format(file_sid, _mlabel(loc)))
            lines.append("  {} -->|{}| {}".format(sid, g["role"], file_sid))
    return "\n".join(lines)


def _member_roles(members):
    """Roles of a node's members, tolerant of both member shapes in play: the raw
    scan tuples (role, file, line) used by cmd_scan/cmd_check and the {role, loc}
    dicts attached to map data nodes."""
    roles = []
    for m in members or []:
        if isinstance(m, dict):
            roles.append(m.get("role"))
        elif isinstance(m, (list, tuple)) and m:
            roles.append(m[0])
    return roles


def _risk_signals(node):
    signals = []
    # 'unimplemented' must mirror the gate, which errors when an ENFORCED requirement
    # has no `implements:` member (a `tested-by`-only member must not satisfy it).
    # Keying on the implements ROLE (not raw member-list emptiness) keeps next/show/
    # the Risk map agreeing with `check`. A `layer: need` is satisfied-by other
    # requirements, not implemented by code, so the gate exempts it (ARCH-TRACE-020) —
    # mirror that here, else the Risk/Problems views flag a passing gate as failing.
    roles = _member_roles(node.get("members"))
    if node["status"] in ENFORCED and "implements" not in roles and not _impl_exempt(node):
        signals.append("unimplemented")
    if node["status"] in ("draft", "baseline"):
        signals.append("unreviewed")
    # implemented-but-untested: has hand-written code linked but no acceptance test.
    # Gated on an implements member so not-yet-built drafts (already 'unreviewed')
    # are not double-flagged. Opt out per requirement with `test_exempt: <reason>`.
    if "implements" in roles and "tested-by" not in roles and not node.get("test_exempt"):
        signals.append("untested")
    # open verify-intent questions reconstructed from code — surface them on the map,
    # not just in the detail panel / _findings.md. Mirror collect_findings: a "None —"
    # placeholder bullet is not an open finding. A *draft* is suppressed here: its
    # intent questions are subsumed by 'unreviewed' (the whole draft is unreviewed),
    # and every auto-extracted draft carries a template verify TODO — flagging both
    # would double-count every draft. Re-surfaces once promoted past draft. This
    # rule lives in the shared signal source so `next` and the Risk tab agree.
    if node["status"] != "draft" and any(
            b and not b.lstrip("*_ ").lower().startswith("none") for b in (node.get("verify") or [])):
        signals.append("unverified-intent")
    return signals


def _mermaid_risk(data):  # implements: ARCH-MAPDIAGRAMS-055
    dep_count = {n["id"]: 0 for n in data["nodes"]}
    for _, b in data["edges"]:
        dep_count[b] = dep_count.get(b, 0) + 1

    risky = [(n, _risk_signals(n)) for n in data["nodes"]]
    risky = [(n, s) for n, s in risky if s]

    lines = ["graph LR"]
    if not risky:
        lines.append('  ok["No risk signals detected"]')
        return "\n".join(lines)

    # Grouped by area, colored by signal, NO edges — Risk answers "which
    # capabilities need attention", not topology (the Dependency Map has edges).
    sigs_by = {n["id"]: s for n, s in risky}
    _emit_area_subgraphs(lines, [n for n, _ in risky],
                         label_fn=lambda n: _node_label(n) + "<br>" + ", ".join(sigs_by[n["id"]]))
    for n, sigs in risky:
        sid = _safe_id(n["id"])
        if "unimplemented" in sigs:
            lines.append("  style {} fill:#fee,stroke:#c00,color:#900".format(sid))
        elif "unreviewed" in sigs:
            lines.append("  style {} fill:#fff3cd,stroke:#a66,color:#630".format(sid))
        else:
            lines.append("  style {} fill:#fff9c4,stroke:#aa0,color:#550".format(sid))
    return "\n".join(lines)


# Per-tab legends (parallel to the 4 diagrams, same order) so each view is
# self-explanatory. HTML uses colored swatches; markdown uses words.
_LEGEND_MD = [
    "Capabilities grouped by area; thick border = bus; arrows = `depends_on`. Edges into the bus/hubs are hidden (the Dependency Map shows area-level coupling).",
    "Each requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected).",
    "Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail.",
    "Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = untested (implemented but no tested-by — set `test_exempt` to silence), or unverified-intent (open verify-intent question).",
]


def _build_md_text(data):  # implements: ARCH-MAPDIAGRAMS-055
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    dep_count = {n["id"]: 0 for n in data["nodes"]}
    for _, b in data["edges"]:
        dep_count[b] = dep_count.get(b, 0) + 1

    diagrams = [
        ("Specification Hierarchy", _mermaid_hierarchy(data)),
        ("System Map",          _mermaid_system(data)),
        ("Requirement-to-Code", _mermaid_req_to_code(data)),
        ("Dependency Map",      _mermaid_deps(data)),
        ("Risk & Unknowns",     _mermaid_risk(data)),
    ]

    lines = [
        "---",
        "generated: {}".format(ts),
        "nodes: {}".format(len(data["nodes"])),
        "edges: {}".format(len(data["edges"])),
        "---",
        "",
        "# Requirement Map",
        "",
    ]
    for i, (title, diagram) in enumerate(diagrams):
        legend = _LEGEND_MD[i] if i < len(_LEGEND_MD) else ""
        lines += ["## {}".format(title), "", "_{}_".format(legend), "", "```mermaid", diagram, "```", ""]

    # risk table — each flagged requirement with its scripted recommendation
    risk_rows = []
    for n in data["nodes"]:
        sigs = _risk_signals(n)
        if sigs:
            rec = " ".join(RISK_ADVICE[s] for s in sigs).replace("|", "/").replace("\n", " ")
            risk_rows.append((n["id"], n["status"],
                              len(n["members"]), dep_count.get(n["id"], 0),
                              ", ".join(sigs), rec))
    if risk_rows:
        lines += [
            "### Risk Table", "",
            "| ID | status | members | dependents | risks | recommendation |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for row in risk_rows:
            lines.append("| {} | {} | {} | {} | {} | {} |".format(*row))
        lines.append("")

    return "\n".join(lines)


def render_md(data, reqs_dir):  # implements: ARCH-MAPDIAGRAMS-055
    out = os.path.join(reqs_dir, "_map.md")
    os.makedirs(reqs_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(_utf8_safe(_build_md_text(data)))
    return out


def _repo_name(root):  # implements: ARCH-MAP-007
    """Best-effort `owner/repo` (else the repo directory name) identifying the
    project this map describes, for display in the viewer header. Tries the git
    `remote.origin.url`, then the directory name; returns None when nothing
    resolves. Never raises and never blocks map generation — git may be absent or
    the tree may not be a checkout. Environment-derived (it differs across forks
    and clones), so it is excluded from the `map --check` freshness diff (see
    `_strip_generated`).

    `REQMAP_REPO` env var overrides the derived value: set it to a public-facing
    slug (e.g. on a private dev repo that publishes elsewhere, so the inlined
    `repo` never leaks the dev remote), or to "" to emit no repo at all."""
    override = os.environ.get("REQMAP_REPO")
    if override is not None:
        return override or None
    url = ""
    try:
        r = subprocess.run(["git", "-C", root, "config", "--get", "remote.origin.url"],
                           capture_output=True, text=True, timeout=3)
        if r.returncode == 0:
            url = r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        url = ""
    if url:
        slug = url[:-4] if url.endswith(".git") else url
        parts = [p for p in re.split(r"[:/]", slug.rstrip("/")) if p]
        if len(parts) >= 2:
            return "/".join(parts[-2:])
    return os.path.basename(os.path.abspath(root)) or None


def _normalise_remote(url):  # implements: ARCH-SITE-026
    """Normalise a git remote URL to a https web URL (https://host/owner/repo),
    or None when empty/unparseable. Handles scp-style (git@host:owner/repo.git),
    ssh:// and https:// forms; strips a trailing `.git`. Pure string work."""
    url = (url or "").strip()
    if not url:
        return None
    if url.endswith(".git"):
        url = url[:-4]
    m = re.match(r"^[\w.+-]+@([\w.-]+):(.+)$", url)          # scp-style
    if m:
        return "https://{}/{}".format(m.group(1), m.group(2))
    # optional :port (corporate / self-hosted ssh remotes) is dropped, keeping
    # group(1)=host and group(2)=path so the web URL stays clickable
    m = re.match(r"^(?:ssh|git|https?)://(?:[^@/]+@)?([\w.-]+)(?::\d+)?/(.+)$", url)
    if m:
        return "https://{}/{}".format(m.group(1), m.group(2))
    return url if "://" in url else None


def _git_remote_web_url(root):  # implements: ARCH-SITE-026
    """The project's web URL from git `remote.origin.url`, or None when git is
    absent / no remote / not a checkout. Honours the REQMAP_REPO override (a
    bare slug becomes https://github.com/<slug>; empty disables). Never raises."""
    override = os.environ.get("REQMAP_REPO")
    if override is not None:
        if not override:
            return None
        return override if "://" in override else "https://github.com/" + override
    url = ""
    try:
        r = subprocess.run(["git", "-C", root, "config", "--get", "remote.origin.url"],
                           capture_output=True, text=True, timeout=3)
        if r.returncode == 0:
            url = r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        url = ""
    return _normalise_remote(url)


SITE_REGIONS = ("nav", "stats")  # implements: ARCH-SITE-026  (commands/layers deferred to a follow-up)


def _region_markers(name):  # implements: ARCH-SITE-026
    key = name.upper()
    return "<!--##REQMAP:{}##-->".format(key), "<!--##/REQMAP:{}##-->".format(key)


def _inject_region(html, name, inner, anchor="<body>"):  # implements: ARCH-SITE-026
    """Replace the content between the paired markers for `name` with `inner`
    (idempotent). Markers absent -> insert a fresh marked block right after the
    first `anchor`; anchor absent too -> append. Only the marked block is
    written; surrounding (authored) bytes are untouched."""
    open_m, close_m = _region_markers(name)
    block = open_m + "\n" + inner + "\n" + close_m
    # find the close that belongs to THIS open (search after it) so a stray close
    # before the open isn't mistaken for the region end, which would append a
    # duplicate block on re-run instead of rewriting in place
    i = html.find(open_m)
    j = html.find(close_m, i + len(open_m)) if i != -1 else -1
    if i != -1 and j != -1:
        return html[:i] + block + html[j + len(close_m):]
    a = html.find(anchor)
    if a != -1:
        a += len(anchor)
        return html[:a] + "\n" + block + html[a:]
    return html + "\n" + block


def _extract_region(html, name):  # implements: ARCH-SITE-026
    """Inner text between the paired markers for `name`, or None when absent.
    Lets the freshness gate diff only engine-owned regions (prose is exempt)."""
    open_m, close_m = _region_markers(name)
    i = html.find(open_m)
    if i == -1:
        return None
    i += len(open_m)
    j = html.find(close_m, i)
    return html[i:j].strip("\n") if j != -1 else None


def _html_escape(s):  # implements: ARCH-SITE-026
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _site_context_from_data(data, repo_url, map_ok, diagram_rel):  # implements: ARCH-SITE-026
    """Deterministic region inputs derived from the map graph + already-resolved
    link facts. No wall-clock, no filesystem here — callers resolve repo_url /
    map_ok / diagram_rel, so a re-run with no change reproduces byte-identically."""
    nodes = data.get("nodes", [])
    layers = {n.get("layer", "feature") for n in nodes}
    return {
        "repo_url": repo_url,
        "map_ok": map_ok,
        "diagram_rel": diagram_rel,
        "counts": {
            "requirements": len(nodes),
            "confirmed": sum(1 for n in nodes if n.get("status") == "confirmed"),
            "layers": len(layers),
            "edges": len(data.get("edges", [])),
        },
    }


def _render_region(name, ctx):  # implements: ARCH-SITE-026
    """Inner HTML for an engine-owned region. NAV: plain target=_blank anchors,
    each emitted only when its target resolves (graceful degradation). STATS:
    deterministic stat cards from the graph counts + engine version."""
    if name == "nav":
        links = []
        if ctx.get("map_ok"):
            links.append('<a href="map.html" target="_blank" rel="noopener">Live Map ↗</a>')
        if ctx.get("diagram_rel"):
            links.append('<a href="{}" target="_blank" rel="noopener">Diagram ↗</a>'
                         .format(_html_escape(ctx["diagram_rel"])))
        if ctx.get("repo_url"):
            links.append('<a href="{}" target="_blank" rel="noopener">GitHub ↗</a>'
                         .format(_html_escape(ctx["repo_url"])))
        return '<nav class="reqmap-nav">' + "".join(links) + '</nav>'
    if name == "stats":
        c = ctx["counts"]
        cells = [("requirements", c["requirements"]), ("confirmed", c["confirmed"]),
                 ("layers", c["layers"]), ("edges", c["edges"]),
                 ("engine", MAP_ENGINE_VERSION)]
        items = "".join('<div class="stat"><b>{}</b><span>{}</span></div>'.format(v, k)
                        for k, v in cells)
        return '<div class="reqmap-stats">' + items + '</div>'
    return ""


# A self-contained default presentation page written by `site` scaffold mode.
# Inline (not a vendored file) so the engine stays hermetic. NAV and STATS are
# marker-delimited engine-owned regions; everything else is authored prose the
# user/skill rewrites. This template is the canonical source (the prototype that
# seeded it has been removed).
# Callers fill %%REPO_NAME%% / %%REPO_URL%% via str.replace (NOT str.format —
# the CSS contains literal braces).
SITE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>%%REPO_NAME%% — project site</title>
<!--
  ============================================================================
  PROTOTYPE of `reqmap.py site` — HYBRID model.
    • Regions marked  <!##REQMAP:...##>  are regenerated by the engine on every
      run (nav links, stats band, commands grid, layer model) — never stale.
    • Everything else is AUTHORED prose, preserved across regenerations.
  Self-contained: no CDN, no network. Plain anchor links (no file:// iframes).
  Diagram is link-only (no builder coupling). Applies the Senate
  (2026-06-14, MODIFY) blocking conditions.
  ============================================================================
-->
<style>
  :root{
    --paper:#ECE9E1; --paper-2:#F4F2EC; --card:#FBFAF6;
    --ink:#1F1D1A; --muted:#6B655C; --line:#D9D4C8;
    --accent:#9A3B2E; --accent-2:#1F6F5C; --gate:#9A3B2E;
    --eng:#1F6F5C; --auth:#9A6700;
    --radius:12px; --maxw:980px;
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{
    margin:0; background:var(--paper); color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    line-height:1.55; -webkit-font-smoothing:antialiased;
  }
  a{color:inherit}
  .wrap{max-width:var(--maxw); margin:0 auto; padding:0 24px}

  /* ============ <!##REQMAP:NAV##>  engine-owned top bar ============ */
  .nav{position:sticky; top:0; z-index:20; background:rgba(236,233,225,.86);
       backdrop-filter:saturate(140%) blur(8px); border-bottom:1px solid var(--line)}
  .nav-inner{max-width:var(--maxw); margin:0 auto; padding:12px 24px;
             display:flex; align-items:center; justify-content:space-between; gap:16px}
  .brand{display:flex; align-items:center; gap:10px; font-weight:700; letter-spacing:-.01em}
  .mark{width:26px; height:26px; border-radius:7px; background:var(--accent);
        display:grid; place-items:center; color:#fff; font-size:14px; font-weight:800}
  .nav-links{display:flex; gap:6px; align-items:center; flex-wrap:wrap}
  .nav-links a{display:inline-flex; align-items:center; gap:4px; text-decoration:none;
               color:var(--ink); font-size:.9rem; font-weight:600; padding:7px 12px;
               border-radius:8px; border:1px solid transparent}
  .nav-links a:hover{background:var(--card); border-color:var(--line); color:var(--accent)}
  .arrow{font-size:.8em; opacity:.7}

  /* legend chip explaining the hybrid coloring */
  .legend{display:flex; gap:14px; align-items:center; justify-content:center;
          font-size:.74rem; color:var(--muted); padding:8px; background:var(--paper-2);
          border-bottom:1px solid var(--line)}
  .dot{display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:5px; vertical-align:middle}
  .dot.eng{background:var(--eng)} .dot.auth{background:var(--auth)}

  /* region tag shown at the corner of engine/authored blocks */
  .tag{display:inline-block; font-size:.66rem; font-weight:700; letter-spacing:.04em;
       text-transform:uppercase; padding:.12rem .5rem; border-radius:999px}
  .tag.eng{color:var(--eng); background:#1F6F5C18; border:1px solid #1F6F5C40}
  .tag.auth{color:var(--auth); background:#9A670018; border:1px solid #9A670040}

  section{padding:56px 0; border-bottom:1px solid var(--line)}
  .eyebrow{font-size:.78rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--accent); margin:0 0 10px}
  h1{font-size:clamp(2rem,5vw,3.2rem); line-height:1.05; letter-spacing:-.02em; margin:.2em 0 .3em; font-weight:800}
  h2{font-size:clamp(1.4rem,3vw,2rem); letter-spacing:-.01em; margin:0 0 .4em; font-weight:750}
  .lead{font-size:1.12rem; color:var(--muted); max-width:60ch}

  /* hero */
  .hero{padding:72px 0 60px; background:
        radial-gradient(60% 80% at 80% -10%, #9A3B2E14, transparent 60%), var(--paper)}
  .hero .cta{margin-top:26px; display:flex; gap:12px; flex-wrap:wrap}
  .btn{display:inline-flex; align-items:center; gap:6px; text-decoration:none; font-weight:650; font-size:.95rem;
       padding:.62rem 1.05rem; border-radius:9px}
  .btn.primary{background:var(--accent); color:#fff}
  .btn.primary:hover{filter:brightness(1.07)}
  .btn.ghost{background:var(--card); border:1px solid var(--line); color:var(--ink)}
  .btn.ghost:hover{border-color:var(--accent); color:var(--accent)}

  /* stats band — engine */
  .band{background:var(--paper-2)}
  .stats{display:grid; grid-template-columns:repeat(6,1fr); gap:14px; margin-top:8px}
  .stat{background:var(--card); border:1px solid var(--line); border-radius:var(--radius); padding:16px 14px; text-align:center}
  .stat b{display:block; font-size:1.7rem; font-weight:800; letter-spacing:-.02em; color:var(--ink)}
  .stat span{font-size:.74rem; color:var(--muted); text-transform:uppercase; letter-spacing:.04em}
  .src{margin-top:14px; font-size:.78rem; color:var(--muted)}
  .src code{font-family:ui-monospace,Menlo,Consolas,monospace}

  /* pillars — authored */
  .pillars{display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin-top:10px}
  .pill{background:var(--card); border:1px solid var(--line); border-radius:var(--radius); padding:20px}
  .pill h3{margin:.1em 0 .35em; font-size:1.05rem}
  .pill p{margin:0; color:var(--muted); font-size:.92rem}

  /* commands grid — engine */
  .cmds{display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-top:10px}
  .cmd{background:var(--card); border:1px solid var(--line); border-radius:10px; padding:13px 14px}
  .cmd.gate{border-color:#9A3B2E66; box-shadow:0 0 0 1px #9A3B2E22 inset}
  .cmd code{font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.85rem; font-weight:700; color:var(--accent)}
  .cmd p{margin:.35em 0 0; font-size:.82rem; color:var(--muted)}

  /* layers — engine/data */
  .layers{display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-top:10px}
  .layer{border-radius:var(--radius); padding:18px; border:1px solid var(--line); background:var(--card)}
  .layer .l{font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.78rem; font-weight:700; margin-bottom:6px}
  .layer.bus .l{color:var(--accent)} .layer.feat .l{color:var(--accent-2)} .layer.need .l{color:#6b4ea8}
  .layer h3{margin:.1em 0 .3em; font-size:1rem}
  .layer p{margin:0 0 8px; font-size:.85rem; color:var(--muted)}
  .layer .ids{font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.72rem; color:var(--muted)}

  /* hybrid mechanism explainer */
  .mech pre{background:#1f1d1a; color:#e9e5db; border-radius:var(--radius); padding:18px 20px; overflow:auto; font-size:.82rem; line-height:1.5}
  .mech .c-eng{color:#7fd6bf} .mech .c-auth{color:#f0c674} .mech .c-dim{color:#9a948a}

  footer{padding:30px 0 60px; color:var(--muted); font-size:.82rem; text-align:center}
  footer code{font-family:ui-monospace,Menlo,Consolas,monospace}

  .secthead{display:flex; align-items:center; gap:10px; margin-bottom:4px}

  @media(max-width:760px){
    .stats{grid-template-columns:repeat(3,1fr)}
    .pillars,.cmds,.layers{grid-template-columns:1fr}
    .nav-links a{padding:6px 9px; font-size:.82rem}
  }
</style>
</head>
<body>

<div class="nav">
  <div class="nav-inner">
    <div class="brand"><span class="mark">R</span> %%REPO_NAME%%</div>
    <!--##REQMAP:NAV##--><!--##/REQMAP:NAV##-->
  </div>
</div>

<div class="legend">
  <span><span class="dot eng"></span>engine-generated (refreshed every run)</span>
  <span><span class="dot auth"></span>authored prose (preserved)</span>
</div>

<!-- HERO — authored -->
<header class="hero">
  <div class="wrap">
  <!-- author me -->
    <span class="tag auth">authored</span>
    <p class="eyebrow" style="margin-top:14px">Single source of truth</p>
    <h1>Keep your specs, code,<br>and intent in sync.</h1>
    <p class="lead">requirement-manager seeds one stdlib-only engine into any repo, then holds the line
      between what you <em>meant</em> to build and what the code actually does — a drift gate you run before
      every commit, a live map of every capability, and an answer to "where is this implemented?".</p>
    <div class="cta">
      <a class="btn primary" href="map.html" target="_blank" rel="noopener">Open the live map ↗</a>
      <a class="btn ghost" href="%%REPO_URL%%" target="_blank" rel="noopener">View on GitHub ↗</a>
    </div>
  </div>
</header>

<section class="band">
  <div class="wrap">
    <div class="secthead"><span class="tag eng">engine-generated</span></div>
    <p class="eyebrow">At a glance</p>
    <h2>The corpus, right now</h2>
    <div class="stats">
      <!--##REQMAP:STATS##--><!--##/REQMAP:STATS##-->
    </div>
    <p class="src">Auto-injected by <code>reqmap.py site</code> from <code>_map.json</code> — re-computed on every run, so it never drifts.</p>
  </div>
</section>

<!-- PILLARS — authored -->
<section>
  <div class="wrap">
    <div class="secthead"><span class="tag auth">authored</span></div>
    <p class="eyebrow">Why it exists</p>
    <h2>Three jobs, one engine</h2>
    <div class="pillars">
      <div class="pill"><h3>Catch drift early</h3><p>Every code tag resolves to a real requirement; every confirmed requirement has code behind it. <code>gate</code> fails the build the moment intent and implementation diverge.</p></div>
      <div class="pill"><h3>Map the system</h3><p>One command renders the whole capability graph — system map, req→code, dependencies, risk — into a self-contained viewer you open by double-click.</p></div>
      <div class="pill"><h3>Prevent duplicates</h3><p>Before a second team re-implements an existing capability, <code>dupes</code> flags the overlapping contracts. The SSOT is the place you look first.</p></div>
    </div>
  </div>
</section>

<!--##REQMAP:COMMANDS## — engine lists the registered subcommands -->
<section class="band">
  <div class="wrap">
    <div class="secthead"><span class="tag eng">engine-generated</span></div>
    <p class="eyebrow">Surface</p>
    <h2>All 18 commands</h2>
    <div class="cmds">
      <div class="cmd gate"><code>gate</code><p>The gate. Links resolve, drift detected, test-links verified. Run before every commit + in CI.</p></div>
      <div class="cmd"><code>sync</code><p>Rescan + advance the drift baseline + regen the map (and a committed _findings.md). --accept-drift for an edited confirmed contract.</p></div>
      <div class="cmd"><code>init</code><p>First-time bootstrap: scaffold, draft from code, lock, map, next-steps. Idempotent.</p></div>
      <div class="cmd"><code>map</code><p>Generate _map.md (Mermaid) + _map.json (graph) + _map.html (viewer).</p></div>
      <div class="cmd"><code>site</code><p>Inject engine-owned regions (nav links + counts) into a presentation page. --attach/--diagram.</p></div>
      <div class="cmd"><code>next</code><p>"What should I work on?" — prioritised, actionable risk buckets.</p></div>
      <div class="cmd"><code>show &lt;ID&gt;</code><p>Consolidated dossier: contract, deps, members by role, risk.</p></div>
      <div class="cmd"><code>lint</code><p>Readability/structure check on non-draft requirements.</p></div>
      <div class="cmd"><code>dupes</code><p>Flag requirement pairs with overlapping contracts (TF-IDF).</p></div>
      <div class="cmd"><code>health</code><p>Corpus coherence score + component counts. --json for a badge.</p></div>
      <div class="cmd"><code>confirm &lt;ID&gt;</code><p>Flip a reviewed requirement to confirmed (needs a member).</p></div>
      <div class="cmd"><code>review</code><p>Emit a JSON review plan (intent/contract/acceptance) for AI-assisted quality review.</p></div>
      <div class="cmd"><code>new</code><p>Scaffold a new requirement from the built-in template.</p></div>
      <div class="cmd"><code>scan</code><p>List which code members belong to which capability.</p></div>
      <div class="cmd"><code>draft</code><p>Draft requirements from untagged legacy code + prose.</p></div>
      <div class="cmd"><code>plan</code><p>Read-only JSON extraction plan (AI-assist), writes nothing.</p></div>
      <div class="cmd"><code>findings</code><p>Aggregate open verify-intent questions into _findings.md.</p></div>
      <div class="cmd"><code>export</code><p>Emit _map.json for an external front-end. --out PATH or -.</p></div>
    </div>
  </div>
</section>
<!--##/REQMAP:COMMANDS##-->

<!--##REQMAP:LAYERS## — engine derives layers from requirement frontmatter -->
<section>
  <div class="wrap">
    <div class="secthead"><span class="tag eng">engine-generated</span></div>
    <p class="eyebrow">Layer model</p>
    <h2>Bus, feature, need, aggregate</h2>
    <div class="layers">
      <div class="layer bus"><div class="l">layer: bus</div><h3>Foundation</h3><p>High fan-in capabilities — config, parse, scan, drift. Change only behind the contract.</p><div class="ids">ARCH-PARSE-001 · ARCH-SCAN-002 · ARCH-DRIFT-003</div></div>
      <div class="layer feat"><div class="l">layer: feature</div><h3>Composed</h3><p>Built on the bus via <code>depends_on</code>; each carries its own contract, acceptance, tests.</p><div class="ids">ARCH-CHECK-006 · ARCH-MAP-007 · ARCH-INIT-012</div></div>
      <div class="layer need"><div class="l">layer: need</div><h3>Stakeholder need</h3><p>An upstream need, satisfied-by features via <code>satisfies:</code>; exempt from the code gate.</p><div class="ids">SYS-SSOT-001</div></div>
      <div class="layer need"><div class="l">layer: aggregate</div><h3>Roof</h3><p>No code of its own: its implementation is its <code>depends_on</code> requirements'. Exempt from the code gate, like a need — downward instead of upward.</p><div class="ids">—</div></div>
    </div>
  </div>
</section>
<!--##/REQMAP:LAYERS##-->

<!-- HYBRID MECHANISM — meta, explains the split -->
<section class="mech">
  <div class="wrap">
    <div class="secthead"><span class="tag auth">authored</span></div>
    <p class="eyebrow">How this page stays current</p>
    <h2>The hybrid: markers</h2>
    <p class="lead" style="margin-bottom:18px">The engine only rewrites what lives between its markers. Your prose is never touched.
      Re-run <code>reqmap.py site</code> after any change and the nav links, stats, commands, and layers refresh — the hero and narrative survive.</p>
<pre><span class="c-dim">&lt;!--##REQMAP:NAV##--&gt;</span>      <span class="c-eng">← engine: Live Map / Diagram / GitHub, from `git remote` + artifact paths</span>
   ...your logo, your wording...   <span class="c-auth">← authored, preserved</span>
<span class="c-dim">&lt;!--##/REQMAP:NAV##--&gt;</span>

<span class="c-auth">&lt;header class="hero"&gt; ... your headline + story ... &lt;/header&gt;</span>   <span class="c-auth">← authored, preserved</span>

<span class="c-dim">&lt;!--##REQMAP:STATS##--&gt;</span>    <span class="c-eng">← engine: counts from _map.json, recomputed every run</span>
<span class="c-dim">&lt;!--##REQMAP:COMMANDS##--&gt;</span> <span class="c-eng">← engine: the registered subcommands</span>
<span class="c-dim">&lt;!--##REQMAP:LAYERS##--&gt;</span>   <span class="c-eng">← engine: layers from requirement frontmatter</span></pre>
  </div>
</section>

<footer>
  Prototype of <code>reqmap.py site</code> · hybrid (engine links + data / authored prose) ·
  self-contained, no network, no <code>file://</code> iframes · Senate 2026-06-14 verdict <strong>MODIFY</strong> conditions applied.
</footer>

</body>
</html>
"""  # implements: ARCH-SITE-026


def _path_key(path):  # implements: ARCH-CHECK-006
    """Comparison key for a filesystem path: fully resolved, then case-folded.

    `abspath` is not enough where a git-derived path meets a caller-derived one.
    It normalizes separators and (with normcase) case, but leaves an 8.3 SHORT
    component alone: `C:/Users/RUNNER~1/...` from the caller and
    `C:/Users/runneradmin/...` from `git rev-parse --show-toplevel` (always long
    form) are the same directory and compare unequal. In `--since` that made every
    member fall out of the changed-set, so the gate reported a clean tree with a
    dangling tag still in it - a gate failing OPEN, silently, on Windows only.
    Found by the CI portability matrix on its first run (ARCH-PYFLOOR-040).

    realpath resolves the short form, and symlinks with it - a repo reached through
    a symlinked path hit the same mismatch on POSIX. Both sides of every comparison
    go through this one function, so resolution can never apply to just one of them.
    """
    return os.path.normcase(os.path.realpath(path))


def _since_changed_files(ref, code_root):
    """Return set of absolute paths changed since `ref`, or None on failure.

    Returns None as the fail-open signal: caller must fall back to full scan.
    """
    try:
        result = subprocess.run(
            # core.quotepath=off: emit non-ASCII paths verbatim, not octal-escaped &
            # double-quoted — otherwise those files silently drop out of the since-set
            # and the gate falsely reports clean.
            ["git", "-c", "core.quotepath=off", "diff", "--name-only", f"{ref}...HEAD"],
            capture_output=True, text=True, encoding="utf-8", cwd=code_root, timeout=10,
        )
        if result.returncode != 0:
            return None
        # `git diff` emits paths relative to the repo ROOT, not to cwd. Resolve
        # the toplevel so these abspaths line up with member abspaths (which are
        # relative to code_root) even when code_root is a subdirectory of the
        # git root — otherwise the since-set and member-set never intersect and
        # the gate silently checks zero requirements. Fall back to code_root on
        # failure (mirrors _docs_publish_path).
        root = code_root
        try:
            top = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, encoding="utf-8", cwd=code_root, timeout=10,
            )
            if top.returncode == 0 and top.stdout.strip():
                root = top.stdout.strip()
        except Exception:
            pass
        files = set()
        for line in result.stdout.splitlines():
            line = line.strip()
            if line:
                files.add(_path_key(os.path.join(root, line)))
        return files
    except Exception:
        return None


def _utf8_safe(text):  # implements: ARCH-MAP-007
    """Text with any lone surrogate replaced by U+FFFD, so the write cannot fail.

    A lone surrogate has no UTF-8 encoding, so `open(..., encoding="utf-8").write()`
    raises UnicodeEncodeError and takes the whole `map` run down - and with it the
    gate's map-freshness check. It is not a theoretical input: os.walk hands back a
    filename whose bytes are not valid UTF-8 surrogate-escaped, and member paths go
    straight into the map. Losing one character beats losing the command.

    The fast path is a C-level encode that touches nothing; the per-character walk
    runs only for a string that genuinely cannot be encoded.
    """
    try:
        text.encode("utf-8")
        return text
    except UnicodeEncodeError:
        return "".join("\uFFFD" if 0xD800 <= ord(c) <= 0xDFFF else c for c in text)


def _build_json_text(data):  # implements: ARCH-MAP-007
    """The registry graph as a JSON string:
    {engine_version, repo, nodes, edges, upstream_edges, todos}.
    json.dumps neutralizes any hostile id/title/body by construction — there is
    no markup context to break out of — so no extra escaping is needed."""
    payload = {"engine_version": MAP_ENGINE_VERSION, "repo": data.get("repo"),
               "nodes": data["nodes"], "edges": data["edges"],
               # `satisfies:` edges — the specification hierarchy. Computed since
               # ARCH-TRACE-020 and, until now, discarded here: the graph carried the
               # dependency axis and dropped the level axis on the floor.
               "upstream_edges": data.get("upstream_edges", []),
               "todos": data.get("todos", [])}
    return _utf8_safe(json.dumps(payload, indent=2, ensure_ascii=False))


def render_json(data, reqs_dir):  # implements: ARCH-MAP-007
    out = os.path.join(reqs_dir, "_map.json")
    os.makedirs(reqs_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(_build_json_text(data))
    return out


# A pre-built, single-file React viewer ships next to this engine as
# `_map_viewer.html`. It carries the marker `<!--REQMAP_DATA-->`; the engine
# swaps that for a <script> assigning this repo's graph to window.__REQMAP_DATA__,
# producing a self-contained `_map.html` that opens by double-click (no server).
VIEWER_TEMPLATE = "_map_viewer.html"
_REQMAP_DATA_MARKER = "<!--REQMAP_DATA-->"


def _docs_publish_path(root):  # implements: ARCH-PAGES-021
    """Return docs/map.html path when docs/ carries a GitHub Pages signal
    (.nojekyll or index.html present), else None. Opt-in by folder contents —
    repos without the signal are unaffected.

    Uses the git root so repos where reqmap runs from a sub-directory (e.g.
    plugin/) still find docs/ at the project root. Falls back to root itself
    when git is absent or the tree is not a checkout."""
    try:
        git_root = subprocess.check_output(
            ["git", "-C", root, "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL, timeout=3
        ).decode().strip()
    except Exception:
        git_root = root
    docs = os.path.join(git_root, "docs")
    if not os.path.isdir(docs):
        return None
    if (os.path.exists(os.path.join(docs, ".nojekyll")) or
            os.path.exists(os.path.join(docs, "index.html"))):
        return os.path.join(docs, "map.html")
    return None


def _site_pages_bootstrap(docs_dir):  # implements: ARCH-SITE-026
    """Ensure docs/ carries a GitHub Pages signal so ARCH-PAGES-021 publishes and
    the page is servable: write .nojekyll and an index.html redirect when absent.
    Idempotent — never clobbers an existing index.html."""
    os.makedirs(docs_dir, exist_ok=True)
    nojekyll = os.path.join(docs_dir, ".nojekyll")
    if not os.path.exists(nojekyll):
        open(nojekyll, "w").close()
    index = os.path.join(docs_dir, "index.html")
    if not os.path.exists(index):
        with open(index, "w", encoding="utf-8") as f:
            f.write('<!doctype html><meta charset="utf-8">'
                    '<meta http-equiv="refresh" content="0; url=./architecture.html">'
                    '<link rel="canonical" href="./architecture.html">'
                    '<title>Project site</title>'
                    '<p>Redirecting to <a href="./architecture.html">the project site</a>…</p>\n')


def _site_diagram_ok(target_path, diagram_rel):  # implements: ARCH-SITE-026
    """True when `diagram_rel` (relative to the page's directory) names an existing
    file — so the Diagram link is emitted only when the artifact is actually there."""
    if not diagram_rel:
        return False
    return os.path.isfile(os.path.join(os.path.dirname(target_path) or ".", diagram_rel))


def _site_default_target(root):  # implements: ARCH-SITE-026
    """docs/architecture.html at the git root (so running from plugin/ still finds
    the project-root docs/), or None when there is no docs/. Mirrors
    _docs_publish_path's git-root resolution."""
    try:
        git_root = subprocess.check_output(
            ["git", "-C", root, "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL, timeout=3).decode().strip()
    except Exception:
        git_root = root
    docs = os.path.join(git_root, "docs")
    return os.path.join(docs, "architecture.html") if os.path.isdir(docs) else None


def cmd_site(reqs, members, root=".", attach=None,
             regions=None, diagram=None, detect=False):  # implements: ARCH-SITE-026
    """Inject engine-owned regions into a presentation page (attach mode) or write
    a default page when the target is absent (scaffold mode). Deterministic and
    headless-safe: never prompts, never raises on missing git/files. `detect`
    prints findings + the suggested command and writes nothing."""
    regions = regions or ["nav"]
    data = _build_map_data(reqs, members)
    repo_url = _git_remote_web_url(root)

    if detect:
        default = _site_default_target(root)
        cands = [p for p in (default,) if p and os.path.isfile(p)]
        print("repo: {}".format(repo_url or "(no remote)"))
        print("presentation candidates: {}".format(", ".join(cands) or "(none)"))
        tgt = default or os.path.join(root, "docs", "architecture.html")
        print("suggested: reqmap site --attach {} --regions nav,stats".format(tgt))
        return 0

    if not attach:
        print("usage: reqmap site --attach <page.html> [--regions nav,stats] [--diagram <rel>]")
        print("   or: reqmap site --detect")
        return 0

    map_ok = os.path.isfile(os.path.join(os.path.dirname(attach) or ".", "map.html"))
    diagram_rel = diagram if _site_diagram_ok(attach, diagram) else None
    ctx = _site_context_from_data(data, repo_url=repo_url, map_ok=map_ok, diagram_rel=diagram_rel)

    if os.path.isfile(attach):
        with open(attach, encoding="utf-8") as f:
            html = f.read()
        mode = "refreshed"
    else:                                   # scaffold mode
        os.makedirs(os.path.dirname(attach) or ".", exist_ok=True)
        # escape before substituting — a repo dir name or remote URL with < > " &
        # would otherwise break out of the title/href sinks in the scaffold template
        html = (SITE_TEMPLATE.replace("%%REPO_NAME%%", _html_escape(_repo_name(root) or "this project"))
                             .replace("%%REPO_URL%%", _html_escape(repo_url or "#")))
        mode = "scaffolded"

    for name in regions:
        if name in SITE_REGIONS:
            html = _inject_region(html, name, _render_region(name, ctx))

    with open(attach, "w", encoding="utf-8") as f:
        f.write(html)
    print("{} {} (regions: {})".format(mode, attach, ",".join(regions)))
    return 0


def _viewer_template_path():  # implements: ARCH-VIEWER-007
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), VIEWER_TEMPLATE)


def _inject_viewer(template_text, data):  # implements: ARCH-VIEWER-007
    """Replace the data marker with an inline <script> assigning the graph to
    window.__REQMAP_DATA__. Three sequences are escaped so the HTML5 parser
    never changes state mid-blob:
      `</`   → `<\\/`  prevents `</script>` from closing the element early
      `<!--` → `<\\!--` prevents entering "script data escaped" state
      `-->`  → `-\\->`  closes "script data escaped" state prematurely if unclosed
    All three are valid JS string escapes (backslash ignored for `/`, `!`, `-`)."""
    blob = (
        _build_json_text(data)
        .replace("</", "<\\/")
        .replace("<!--", "<\\!--")
        .replace("-->", "-\\->")
        # U+2028/U+2029 are LINE TERMINATORS in JavaScript but ordinary characters
        # in JSON, so ensure_ascii=False emits them raw and any engine older than
        # ES2019 reads the blob as an unterminated string - one character in one
        # requirement title kills the whole viewer. The escaped forms are valid JSON
        # for the same characters, so the parsed value is unchanged.
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    script = "<script>window.__REQMAP_DATA__=" + blob + ";</script>"
    return template_text.replace(_REQMAP_DATA_MARKER, script, 1)


def render_html(data, reqs_dir):  # implements: ARCH-VIEWER-007
    """Write the self-contained viewer `_map.html` by injecting `data` into the
    vendored template. Returns the path, or None when no template is present
    (the engine still emits _map.md + _map.json — the viewer is optional)."""
    tpl = _viewer_template_path()
    if not os.path.exists(tpl):
        return None
    with open(tpl, encoding="utf-8") as f:
        template_text = f.read()
    out = os.path.join(reqs_dir, "_map.html")
    os.makedirs(reqs_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(_inject_viewer(template_text, data))
    return out


# A test function's own NAME — never its class, never its parameter list. Both mislead:
# a class `TestCiUploadSiDosar` carries the tokens of TWO requirements, so every test
# inside it looked like it belonged to both; and a fixture parameter
# (`def test_export_ac2_x(self, ctx, campaign)`) made a test look like it belonged to
# the requirement whose token happens to name the fixture.
_FUNC_DEF_RE = re.compile(r"^[ \t]*(?:async\s+)?(?:def|function|func)\s+([A-Za-z_]\w*)\s*\(")
_JS_CASE_RE = re.compile(r"""^[ \t]*(?:it|test)\s*\(\s*["'`]([^"'`]{3,120})["'`]""")
_HASH_COMMENT_EXTS = (".py", ".sh", ".bash", ".rb", ".yaml", ".yml", ".tf", ".ex", ".exs", ".jl", ".pl", ".r")


def _test_functions(path):  # implements: ARCH-SUGGESTVERIFIES-047
    """`[(line_no, name)]` for the test cases declared in a file: a `def`/`function`/
    `func` whose own name says "test", plus the Jest/Mocha `it("…")` label. Names only
    (see above). Returns [] for an unreadable file — a suggestion tool never raises."""
    out = []
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except OSError:
        return out
    for i, line in enumerate(lines, 1):
        m = _FUNC_DEF_RE.match(line)
        if m and "test" in m.group(1).lower():
            out.append((i, m.group(1)))
            continue
        m = _JS_CASE_RE.match(line)
        if m:
            out.append((i, m.group(1)))
    return out


def _ac_name_re(ac):  # implements: ARCH-SUGGESTVERIFIES-047
    """Match `AC-3` inside a test name as `ac3`, `ac_3`, `ac-3` or `ac 3` — and NOT as
    a prefix of `ac30`, which is a different criterion."""
    n = ac.split("-", 1)[1]
    return re.compile(r"(?:^|[^a-z0-9])ac[ _-]?0*{}(?![0-9])".format(re.escape(n)), re.I)


def _comment_prefix(path):
    return "#" if path.lower().endswith(_HASH_COMMENT_EXTS) else "//"


def _verifies_proposals(reqs, members, code_root, ac_cover):  # implements: ARCH-SUGGESTVERIFIES-047
    """`(proposals, ambiguous)` — the machine-checkable half of "this test already
    verifies that criterion", recovered from naming.

    A proposal is made only when ALL of these hold, each rule paid for by a WRONG link
    it produced when it was missing:
      1. the test's name carries the criterion (`test_ac3_…`);
      2. the file belongs to exactly ONE requirement, OR the test name carries a token
         unique to this requirement's id — a `tested-by` file shared by four
         requirements holds four different `ac1` tests;
      3. the name carries no OTHER requirement's number — `test_ac1_083_…` sits in one
         requirement's file but verifies id 083;
      4. exactly one test matches. Two candidates are reported as ambiguous and never
         written: the tool proposes, the human confirms."""
    counts = {}
    for rid in reqs:
        for part in rid.lower().split("-"):
            counts[part] = counts.get(part, 0) + 1
    numbers = {}
    for rid in reqs:
        m = re.search(r"(\d{2,})$", rid)
        if m:
            numbers[rid] = m.group(1)
    owners = {}
    for rid, hits in members.items():
        for role, fp, _ln in hits:
            if role == "tested-by":
                owners.setdefault(fp, set()).add(rid)
    proposals, ambiguous = [], []
    for rid in sorted(reqs):
        labels = _automatable_acs(reqs[rid]["body"])
        covered = ac_cover.get(rid, {})
        missing = [ac for ac in labels if ac not in covered]
        if not missing:
            continue
        files = sorted({fp for role, fp, _ln in members.get(rid, []) if role == "tested-by"})
        distinctive = [p for p in rid.lower().split("-") if counts.get(p) == 1]
        foreign = {n for other, n in numbers.items() if other != rid}
        mine = numbers.get(rid)
        for ac in missing:
            want = _ac_name_re(ac)
            hits = []
            for fp in files:
                shared = len(owners.get(fp, ())) > 1
                for ln, name in _test_functions(os.path.join(code_root, fp)):
                    low = name.lower()
                    if not want.search(low):
                        continue
                    if shared and not any(d in low for d in distinctive):
                        continue
                    nums = set(re.findall(r"\d{2,}", low)) - {ac.split("-", 1)[1]}
                    if (nums & foreign) and mine not in nums:
                        continue
                    hits.append((fp, ln, name))
            if len(hits) == 1:
                proposals.append((rid, ac) + hits[0])
            elif hits:
                ambiguous.append((rid, ac, hits))
    return proposals, ambiguous


def _apply_verifies(proposals, code_root):  # implements: ARCH-SUGGESTVERIFIES-047
    """Append `# verifies: <id>#AC-N` to each proposed test's declaration line.
    Returns the number of lines written. Idempotent: a line already carrying that
    exact tag is left alone."""
    by_file = {}
    for rid, ac, fp, ln, _name in proposals:
        by_file.setdefault(fp, []).append((ln, rid, ac))
    written = 0
    for fp, items in sorted(by_file.items()):
        path = os.path.join(code_root, fp)
        try:
            with open(path, encoding="utf-8", newline="") as f:
                lines = f.readlines()
        except OSError:
            print("  skipped {} (unreadable)".format(fp))
            continue
        changed = False
        for ln, rid, ac in sorted(items):
            if ln > len(lines):
                continue
            line = lines[ln - 1]
            tag = "{} {}: {}#{}".format(_comment_prefix(fp), "verifies", rid, ac)
            if tag in line:
                continue
            body, nl = line.rstrip("\r\n"), line[len(line.rstrip("\r\n")):]
            lines[ln - 1] = "{}  {}{}".format(body, tag, nl)
            changed = True
            written += 1
        if changed:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.writelines(lines)
            print("  wrote {}".format(fp))
    return written


def cmd_suggest_verifies(reqs, members, code_root, reqs_dir, ac_cover=None, apply_tags=False):  # implements: ARCH-SUGGESTVERIFIES-047
    """Propose `# verifies: <id>#AC-N` tags for tests already NAMED after the criterion
    they check, so a corpus can adopt per-criterion coverage without re-deriving the
    matching rules (and their three traps) by hand. Read-only unless --apply."""
    if ac_cover is None:
        ac_cover = scan_ac_verifies(code_root, reqs_dir)
    proposals, ambiguous = _verifies_proposals(reqs, members, code_root, ac_cover)
    for rid, ac, fp, ln, name in proposals:
        print("{} {}\n  {}:{}  {}  -> {} {}: {}#{}".format(
            rid, ac, fp, ln, name, _comment_prefix(fp), "verifies", rid, ac))
    for rid, ac, hits in ambiguous:
        print("{} {}  AMBIGUOUS — {} candidates, none applied:".format(rid, ac, len(hits)))
        for fp, ln, name in hits:
            print("    {}:{}  {}".format(fp, ln, name))
    if not proposals and not ambiguous:
        print("no suggestions — every automatable criterion is tagged, or no test is "
              "named after one.")
        return 0
    print("\n{} proposal(s), {} ambiguous.".format(len(proposals), len(ambiguous)))
    if apply_tags and proposals:
        n = _apply_verifies(proposals, code_root)
        print("applied {} tag(s). Re-run `reqmap.py sync` to refresh the map.".format(n))
    elif proposals:
        print("re-run with --apply to write them (ambiguous ones are never written).")
    return 0


def cmd_review(reqs, one_id=None):  # implements: ARCH-REVIEW-022
    """Emit a DETERMINISTIC, read-only review PLAN as JSON for an out-of-band AI quality
    pass. The engine never calls an LLM and writes no file — it gathers each requirement's
    prose (WHY/contract/acceptance/verify-intent) plus cheap STRUCTURAL anchors the AI
    consumer should focus on, a corpus coverage_summary, and the finding contract. The plan
    is byte-reproducible across runs; the AI findings DERIVED from it are advisory and NOT
    reproducible, and no gate path reads this output or any AI sidecar."""
    if one_id and one_id not in reqs:
        print("no requirement with id {} (expected requirements/{}.md)".format(one_id, one_id))
        return 1
    ids = [one_id] if one_id else sorted(reqs)
    items = []
    for rid in ids:
        r = reqs.get(rid)
        if not r:
            continue
        body = r["body"]
        contract = _from_any(_bullets, body, CONTRACT_LABELS)
        intent = _first_quote(body)
        ac_n = _count_ac(body)
        intent_words = len(intent.split())
        items.append({
            "id": rid,
            "title": _title(body),
            "layer": r["meta"].get("layer", "feature"),
            "status": r["meta"].get("status", "draft"),
            "intent": intent,
            "contract": contract,
            "acceptance": _from_any(_bullets, body, ACCEPTANCE_LABELS),
            "verify_intent": _bullets(body, "verify"),
            # cheap STRUCTURAL anchors (deterministic facts, NOT judgments) the AI examines:
            "anchors": {
                "contract_clauses": len(contract),
                "acceptance_count": ac_n,
                "intent_words": intent_words,
                "intent_terse": intent_words < 12,                    # WHY may merely restate the title
                "more_contract_than_acceptance": len(contract) > ac_n,  # a clause may be uncovered
            },
        })
    plan = {
        "engine_version": MAP_ENGINE_VERSION,
        "advisory": ("DETERMINISTIC read-only review plan. AI findings derived from it are ADVISORY "
                     "and NON-reproducible; they are never part of the gate and never auto-applied."),
        "categories": [
            {"key": "untestable-contract", "desc": "a contract clause so vague it cannot be verified"},
            {"key": "why-restates-title", "desc": "the WHY restates the title instead of explaining why it exists"},
            {"key": "acceptance-doesnt-cover-contract", "desc": "a contract clause with no acceptance criterion exercising it"},
        ],
        "finding_contract": ("every AI finding MUST carry a concrete suggested_rewrite; emit only "
                             "high-confidence findings; severity is advisory-only (never error/warn, never the gate)."),
        "coverage_summary": {"total_requirements": len(reqs), "requirements_in_plan": len(items)},
        "requirements": items,
    }
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    return 0


def main():
    # Refuse an interpreter below the declared floor before anything else runs, so the
    # user gets one readable line instead of an AttributeError from some stdlib call
    # that did not exist yet.
    floor = _python_floor_error()
    if floor:
        print(floor)
        return 2
    # The engine prints non-ASCII (em-dashes in WARN/info lines, the JSON plan with
    # ensure_ascii=False). On a legacy Windows codepage (cp437/cp850) a bare `python
    # reqmap.py check` would crash with UnicodeEncodeError and fail the gate on an
    # encoding error, not a real violation. Force UTF-8 so no caller has to remember
    # `-X utf8`. Guarded: reconfigure() is Python 3.7+ and may be absent on exotic streams.
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError, OSError):
            pass
    ap = argparse.ArgumentParser(
        prog="reqmap",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Everyday:\n"
            "  init                 bootstrap a repo (scaffold + draft + lock + map)\n"
            "  new ID               scaffold one requirement   (--from-todo \"name\" --id ID: from a TODO.md item)\n"
            "  draft                derive draft requirements from untagged CODE\n"
            "  confirm ID           validate a reviewed requirement -> status confirmed\n"
            "  sync                 rescan + regenerate map + advance drift baseline (use --accept-drift on confirmed edits)\n"
            "  gate                 the commit/CI gate: link sync + drift + test-link (report-only)\n"
            "  next                 what to do next (counted risk buckets)\n"
            "  show ID              one-requirement dossier\n"
            "  search \"query\"        rank requirements by lexical relevance to a query\n"
            "\nAdvanced:\n"
            "  plan                 read-only extraction plan (writes nothing)\n"
            "  dupes                flag requirement pairs with overlapping contracts\n"
            "  scan / map / export / site / findings / lint / review / health\n"
            "\nDeprecated:\n"
            "  check                alias for 'gate' (removed in v4.0.0)\n"
        ),
    )
    ap.add_argument("cmd", choices=_cli_choices())
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--root", default=".")
    ap.add_argument("--reqs", default=None)
    ap.add_argument("--code", default=None)
    ap.add_argument("--out", default=None, help="candidates: write plan JSON here ('-' or omit = stdout); "
                    "export: write graph JSON here ('-' = stdout, omit = requirements/_map.json)")
    ap.add_argument("--md-glob", action="append", default=None,
                    help="candidates: also discover .md files matching this glob (repeatable; "
                         "comma-separated ok). Off unless given. e.g. --md-glob 'prompts/**' --md-glob 'modes/**'")
    ap.add_argument("--raw", action="store_true",
                    help="findings: ignore the triage sidecar and emit the raw grouped list")
    ap.add_argument("--all", dest="show_all", action="store_true",
                    help="next: list every pending item instead of the top few per bucket")
    ap.add_argument("--strict", action="store_true",
                    help="lint: exit non-zero on errors. check: promote drift and "
                         "test-link integrity from warn to error.")
    ap.add_argument("--decompose", action="store_true",
                    help="lint: scaffold one draft requirement per statement-size finding "
                         "(opt-in; the only lint mode that writes files)")
    ap.add_argument("--threshold", type=_threshold_arg, default=None,
                    help="similar: cosine cutoff in (0,1] for reporting a pair (default 0.35)")
    ap.add_argument("--top", type=int, default=None,
                    help="search: max ranked matches to show (default 5)")
    ap.add_argument("--json", dest="as_json", action="store_true",
                    help="check|health|coverage: emit structured JSON output (for CI/badge consumption)")
    ap.add_argument("--badge", dest="as_badge", action="store_true",
                    help="health: emit Shields.io endpoint JSON (schemaVersion, label, message, color)")
    ap.add_argument("--update-lock", action="store_true")
    ap.add_argument("--accept-drift", dest="accept_drift", action="store_true",
                    help="sync: advance the drift baseline even when a confirmed/implemented "
                         "contract changed (otherwise sync refuses and exits non-zero)")
    ap.add_argument("--since", metavar="REF",
                    help="check: scope gate to requirements whose member files changed since REF "
                         "(hypothesis: highest-frequency changes; falls back to full scan on git error)")
    ap.add_argument("--wipe", action="store_true",
                    help="init: hard-reset — delete all non-generated requirements and strip "
                         "membership tags from source files before re-extracting")
    ap.add_argument("--check", dest="check_fresh", action="store_true",
                    help="map: verify the committed _map.* is fresh (exit 1 if stale) instead of writing")
    ap.add_argument("--id", dest="new_id", default=None,
                    help="new --from-todo: the AREA-NAME-NNN id for the scaffolded requirement (required)")
    ap.add_argument("--from-todo", dest="from_todo", default=None,
                    help="new: scaffold the requirement from a TODO.md item matched by this name "
                         "(use with --id; add --mark-done to flip the item to [x])")
    ap.add_argument("--mark-done", dest="mark_done", action="store_true",
                    help="new --from-todo: also flip the matched TODO.md item to [x] (off by default)")
    ap.add_argument("--cache", action="store_true",
                    help="opt-in: reuse a per-file scan cache (requirements/_scancache.json) so unchanged "
                         "files skip re-parsing. Off by default; results are identical with or without it.")
    ap.add_argument("--attach", default=None,
                    help="site: target HTML to inject engine-owned regions into (scaffolds it if absent)")
    ap.add_argument("--regions", default="nav",
                    help="site: comma list of regions to inject (nav,stats); default nav")
    ap.add_argument("--diagram", default=None,
                    help="site: relative path (from the page) to an excalidraw HTML; linked only if it exists")
    ap.add_argument("--detect", action="store_true",
                    help="site: print docs/ findings + the suggested command; writes nothing")
    ap.add_argument("--no-site", dest="no_site", action="store_true",
                    help="init: skip the final site step")
    ap.add_argument("--apply", dest="apply_tags", action="store_true",
                    help="suggest-verifies: write the proposed `verifies:` tags into the test files")
    ap.add_argument("--to", dest="translate_to", default=None, choices=["ro", "en"],
                    help="translate: target locale (default: the other of ro/en from "
                         "the detected corpus majority)")
    a = ap.parse_args()
    reqs_dir = a.reqs or os.path.join(a.root, "requirements")
    code_root = a.code or a.root
    # prefer an on-disk templates/requirement.md if present (back-compat), else the
    # built-in REQUIREMENT_TEMPLATE — so no templates/ dir is required.
    here = os.path.dirname(os.path.abspath(__file__))
    tmpl = os.path.join(here, "..", "templates", "requirement.md")
    if not os.path.exists(tmpl):
        tmpl = None

    if a.cmd == "new":
        if getattr(a, "from_todo", None):
            return cmd_promote_todo(reqs_dir, tmpl, a.from_todo, a.new_id, a.mark_done, code_root)
        if not a.arg:
            print("usage: reqmap new AREA-NAME-NNN   |   reqmap new --from-todo \"<todo name>\" --id AREA-NAME-NNN"); return 2
        return cmd_new(reqs_dir, tmpl, a.arg)
    if a.cmd == "init":
        return cmd_init(reqs_dir, code_root, wipe=a.wipe, no_site=a.no_site)
    if a.cmd == "gen-integration":
        return cmd_gen_integration(reqs_dir, code_root)

    reqs = load_requirements(reqs_dir)
    # One walk for the commands that need coverage too (gate/sync/check); the rest only
    # ever asked for members. --cache stays on scan_members, the only scanner that
    # implements it — see scan_all's docstring for why it is not duplicated there.
    _ac_cover = _level_cover = None
    if a.cmd in ("gate", "check", "sync", "show") and not a.cache:
        members, _ac_cover, _level_cover = scan_all(code_root, reqs_dir)
    else:
        members = scan_members(code_root, reqs_dir, cache=a.cache)
    if a.cmd == "scan":
        cmd_scan(reqs, members); return 0
    if a.cmd == "next":
        return cmd_next(reqs, members, a.show_all, code_root=code_root, reqs_dir=reqs_dir)
    if a.cmd == "lint":
        return cmd_lint(reqs, a.strict, members, decompose=a.decompose, reqs_dir=reqs_dir)
    if a.cmd == "show":
        if not a.arg:
            print("usage: reqmap show <ID>"); return 2
        # scan_all above (the non-cache path) already produced level_cover in the same
        # walk; only re-walk via scan_test_levels when --cache forced the
        # scan_members-only path (cache is scan_members-only, see scan_all's docstring).
        levels = _level_cover if _level_cover is not None else scan_test_levels(code_root, reqs_dir)
        return cmd_show(reqs, members, a.arg, levels)
    if a.cmd == "dupes":
        return cmd_similar(reqs, a.threshold if a.threshold is not None else SIMILAR_THRESHOLD, members)
    if a.cmd == "search":
        if not a.arg:
            print("usage: reqmap search \"<query>\"   [--top N]"); return 2
        return cmd_search(reqs, a.arg, a.top if a.top is not None else SEARCH_TOP)
    if a.cmd == "health":
        return cmd_health(reqs, members, reqs_dir, a.as_json,
                          getattr(a, "as_badge", False), code_root=code_root)
    if a.cmd == "coverage":
        return cmd_coverage(reqs, members, code_root, reqs_dir, a.as_json)
    if a.cmd == "gate":
        # report-only: link sync + drift + test-link; never touches the lock.
        return cmd_check(reqs, members, reqs_dir, False, code_root, a.strict, a.as_json,
                         getattr(a, "since", None),
                         ac_cover=_ac_cover, level_cover=_level_cover)
    if a.cmd == "sync":
        # rescan + regenerate map + advance the drift baseline (guarded). Members were
        # already scanned above; cmd_check rewrites the lock unless confirmed drift is
        # detected without --accept-drift, then map regenerates only on success.
        rc = cmd_check(reqs, members, reqs_dir, True, code_root, strict=a.strict,
                       accept_drift=getattr(a, "accept_drift", False),
                       ac_cover=_ac_cover, level_cover=_level_cover)
        if rc == 0:
            cmd_map(reqs, members, reqs_dir, code_root, ac_cover=_ac_cover)
            # Deliberately here and not in cmd_check: `gate` runs on every commit via the
            # hook, and a corpus-shape advisory there is noise on work that is already
            # correct. `sync` is the moment the corpus was just rewritten, which is when
            # a newly-minted duplicate appears.  # implements: ARCH-REDUNDANCY-058
            _dups = _redundant_groups(reqs)
            if _dups:
                print("info  {} group(s) of requirements share an identical contract "
                      "({} could be folded away) — run `reqmap.py next` to see them"
                      .format(len(_dups), sum(len(g) - 1 for g in _dups)))
        else:
            # The lock may still have advanced above (it is written unless CONFIRMED
            # drift was refused), while the map was not regenerated — the two then
            # disagree, `gate` passes locally, and CI fails on `map --check`. Say so
            # where it happens instead of leaving the reader to infer it.
            print("sync: gate failed — the map was NOT regenerated. Fix the errors above "
                  "and re-run `sync`, or run `map` explicitly.", file=sys.stderr)
        return rc
    if a.cmd == "check":
        # deprecated alias for `gate` (report) / `sync` (regenerate). Preserves the
        # legacy behavior verbatim so consumer hooks/CI/Action keep working.
        print("reqmap: 'check' is deprecated — use 'gate' (report) or 'sync' (regenerate "
              "lock+map). Forwarding to legacy behavior; the alias is removed in v4.0.0.",
              file=sys.stderr)
        rc = cmd_check(reqs, members, reqs_dir, a.update_lock, code_root, a.strict, a.as_json,
                       getattr(a, "since", None), accept_drift=getattr(a, "accept_drift", False),
                       ac_cover=_ac_cover, level_cover=_level_cover)
        if a.update_lock and rc == 0:        # mirror sync: don't regen the map on a failing gate
            cmd_map(reqs, members, reqs_dir, code_root, ac_cover=_ac_cover)
        return rc
    if a.cmd == "map":
        return cmd_map(reqs, members, reqs_dir, code_root, a.check_fresh, ac_cover=_ac_cover)
    if a.cmd == "site":  # implements: ARCH-SITE-026
        regions = [x.strip() for x in (a.regions or "").split(",") if x.strip()]
        return cmd_site(reqs, members, code_root,
                        attach=a.attach, regions=regions, diagram=a.diagram, detect=a.detect)
    if a.cmd == "export":
        return cmd_export(reqs, members, reqs_dir, code_root, a.out, ac_cover=_ac_cover)
    if a.cmd == "draft":
        return cmd_extract(reqs, members, code_root, reqs_dir)
    if a.cmd == "plan":
        md_globs = []
        for g in (a.md_glob or []):
            md_globs += [x.strip() for x in g.split(",") if x.strip()]
        return cmd_candidates(reqs, members, code_root, reqs_dir, a.out, md_globs)
    if a.cmd == "findings":
        return cmd_findings(reqs, reqs_dir, a.raw)
    if a.cmd == "review":
        return cmd_review(reqs, a.arg)
    if a.cmd == "suggest-verifies":
        return cmd_suggest_verifies(reqs, members, code_root, reqs_dir,
                                    ac_cover=_ac_cover, apply_tags=a.apply_tags)
    if a.cmd == "translate":
        return cmd_translate(reqs, reqs_dir, target=a.translate_to)
    if a.cmd == "confirm":
        if not a.arg:
            print("usage: reqmap confirm AREA-NAME-NNN"); return 2
        return cmd_promote(reqs, members, a.arg)


def _pipe_closed():  # implements: ARCH-PIPE-046
    """The reader (`| head`) stopped listening: point stdout at the null device so the
    interpreter's shutdown flush cannot raise a second time, and exit clean."""
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
    except Exception:
        pass
    return 0


def _run_cli(entry=None):  # implements: ARCH-PIPE-046
    """Run `main` (or `entry`), turning a closed output pipe into a quiet exit 0.
    Windows has no SIGPIPE: a reader that closes early surfaces as OSError EINVAL (22),
    on POSIX as BrokenPipeError/EPIPE — `dupes | head` on a 1,141-requirement corpus
    died with a traceback on the primary supported OS. Every other OSError propagates."""
    try:
        return (entry or main)() or 0
    except BrokenPipeError:
        return _pipe_closed()
    except OSError as e:
        if e.errno in (errno.EPIPE, errno.EINVAL):
            return _pipe_closed()
        raise


if __name__ == "__main__":
    sys.exit(_run_cli())

---
name: requirement-manager
description: >
  Use when working on a project that needs a single source of truth for
  requirements/capabilities — especially with multiple agents or vibe coding,
  to prevent drift between code, docs and intent and to avoid duplicated /
  divergent implementations. Use to create or reconcile requirements, run the
  drift gate before a commit/merge, generate the requirement map, or extract
  draft requirements from legacy code. Trigger words: requirement, SSOT, spec,
  capability, drift, reconcile, "what does this do", "where is X implemented".
---

# Requirement manager

A capability registry that sits between intent and code. Each capability is one
markdown file (the single source of truth). Code points back to it with a tag.
A script reconciles the two and generates a navigable map.

## Setup (first use in a repo)

The engine is a single stdlib-only script. Seed it — and everything else reqmap
writes — under `requirements/`, so the tool leaves one tidy folder:

```bash
mkdir -p requirements
cp "${CLAUDE_PLUGIN_ROOT}/scripts/reqmap.py" requirements/reqmap.py
printf 'data/\narchive/\nbuild/\n' > requirements/.reqmapignore   # dirs to skip
```

From then on run `python requirements/reqmap.py <cmd>`, and commit it so the gate
works in CI without the plugin. Everything reqmap produces (`_map.html`, `_map.md`,
`_reqlock.json`, the requirement `.md` files) lands in `requirements/` too.

Because the engine lives **inside** `requirements/` — the one dir the scanner skips
— its own `# implements: CORE-*` self-tags are ignored automatically; you don't
list it in `.reqmapignore`. The requirement template is built into the engine, so
no `templates/` dir is needed.

**`.reqmapignore`** (in `requirements/`; fnmatch globs over repo-root-relative
paths) keeps generated/vendored dirs out of scanning — `data/`, `archive/`, build
output — so the registry stays about *your* code, not tooling.

> The plugin's own repo keeps the engine in `plugin/scripts/` instead — it
> *dogfoods*, so its `CORE-*`/`REQ-*` requirements need `reqmap.py` to be scanned.

## Core model

- **Source of truth**: one `.md` per capability in `requirements/`, with YAML
  frontmatter (machine-readable) + prose body (human-readable). Nothing else
  restates the contract — code and docs *reference* it by id, never re-describe it.
- **Two layers** (think Factorio main bus + cells):
  - `layer: bus` — foundation capabilities, defined once, shared (telemetry,
    config, logging, an invocation primitive). Crisp output → crisp boundary.
  - `layer: feature` — capabilities that compose the bus. They `depends_on` bus ids.
  - If you cannot tell where a requirement ends, factor the shared part onto the bus.
- **The thread**: code declares membership with a tag, by role:
  - `implements: <ID>`       — hand-written logic (reviewed + tested on change)
  - `generated-from: <ID>`   — derived artifact (regenerated on change)
  - `validated-against: <ID>`— config/data (re-validated on change)
  - `tested-by: <ID>`        — the acceptance tests
  The member list is **discovered by scanning code**, never hand-maintained.

## Authoring rules (read before touching anything)

1. **Before implementing**, run `reqmap.py map` or read `requirements/` and check
   whether a capability already covers the task. If yes, extend/reuse it — do not
   reimplement. Especially check the bus.
2. **A requirement is its output.** Fill `Input → Description → Output` first; the
   boundary follows from the output.
3. **Acceptance criteria are tests.** Write them as checkable statements; they map
   to `tested-by` test files.
4. **One fact, one home.** Reference ids; never copy a contract into a README.
5. **Authority is one-directional**: requirement → code. If they disagree, the
   requirement wins (fix the code, or fix the requirement — never let code be the
   silent truth).
6. **Authoring is bidirectional**: you may start in code (explore), but the change
   is not "done" until the requirement is updated in the *same* commit.

## Statuses

- `draft`     — auto-extracted from code, unreviewed. Not enforced.
- `baseline`  — descriptive: "this is what the code does now". The gate only
  alerts on *change* (characterization), it does not claim correctness.
- `in-progress` / `implemented` — being built / built.
- `confirmed` — intent validated by a human. The gate enforces it as truth.
- `deprecated` / `superseded-by: <ID>`

## The gate (run at commit/merge — keep it non-optional)

`python scripts/reqmap.py check` verifies three syncs and exits non-zero on error:
- **link sync**  — every code tag points to a real requirement; every confirmed
  requirement has ≥1 member; no dangling refs; `depends_on` targets exist.
- **behavior sync** — acceptance criteria run as tests (wire `tested-by` into CI).
- **drift** — content hash of each requirement compared to the lock; a changed
  `confirmed` requirement is flagged stale, and the WARN **names the member
  locations to re-check** (`file:line, …`) so it is actionable, not just "its members".

Intent sync is *not* automatable — it surfaces at human review (promote
`baseline → confirmed`).

### Make the gate non-optional
Run `check` on every commit (locally) and every push/PR (CI):

- **pre-commit hook** — ship `hooks/pre-commit` into the repo. From the repo root:
  `cp hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`
  (or team-shared: put it in `.githooks/` and `git config core.hooksPath .githooks`).
  It blocks a commit on **errors** only; drift stays advisory. Bypass once with
  `git commit --no-verify`.
- **CI** — gate every PR (stdlib-only, no deps to install):
  ```yaml
  # .github/workflows/reqmap.yml
  name: reqmap
  on: [push, pull_request]
  jobs:
    gate:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with: { python-version: "3.x" }
        - run: python scripts/reqmap.py check
  ```

## Commands

- `python scripts/reqmap.py new AREA-NAME-NNN`   — scaffold a requirement from the template
- `python scripts/reqmap.py scan`              — list code members per capability
- `python scripts/reqmap.py check`             — run the gate (use as pre-commit/CI hook)
- `python scripts/reqmap.py map`               — generate `requirements/_map.html` (5-tab interactive viewer) + `requirements/_map.md` (5 Mermaid diagrams)
- `python scripts/reqmap.py extract`           — quick one-draft-per-file scaffold (TODO bodies)
- `python scripts/reqmap.py candidates`        — emit a JSON capability-extraction plan (read-only; feeds AI authoring)

## Legacy / brownfield

Two ways to bootstrap a registry on existing code. **Neither invents intent** —
they lower the cost of writing requirements you then review. Nothing is ever
auto-`confirmed`: a bug is never canonized as correct.

### `extract` — quick scaffold (one draft per file)
`extract` walks untagged source and writes one `draft` requirement per file with a
**TODO body** and a cheap risk score (counts of `TODO`/`FIXME`/`HACK` markers, lint
suppressions, and file size). It does **not** read signatures or imports — the body
is left as TODO for a human to fill (this is the contract, see `REQ-EXTRACT-008`).
The console prints `auto-baseline` / `REVIEW` as a review *hint*; the file's
`status` field is always `draft`. Use it only for a fast, throwaway inventory — it
is one-draft-per-file, not capability-level, so it does not by itself produce a
useful registry.

### `candidates` + AI authoring — capability-level requirements (recommended)
`candidates` is **read-only** (writes no `.md`) and emits a JSON *extraction plan*.
It groups files into capabilities — authoritative `requirements/_capmap.json` when
present (a list of `{id, layer, files[]}`), else one candidate per file — and for
each derives docstrings + top-level signatures (Python via `ast`, JS/TS via regex),
the import graph as `depends_on`, test-file coverage, fan-in (a `bus` hint), and an
`existing_req` flag for files already tagged. An agent (or you) then authors a real
`requirements/<ID>.md` per candidate, choosing `bus`/`feature` and referencing
existing capabilities instead of duplicating them. Author bus first so feature
`depends_on` resolve, then tag the member files (`# implements: <ID>`) and run
`check --update-lock`. Promote `draft → baseline → confirmed` at human review.

**Emission rules (you are reconstructing intent from code, not authoring it).**
The code was often AI-written, so the danger is **laundering its accidents into a
contract**. Sort every observed behavior into one of three homes:
- **`## WHAT — Contract` (normative)** — binding, testable "shall" statements, one
  behavior per line, **no function names**; output shape + allowed values, required
  vs optional inputs and how it degrades, and the **decision logic** selecting each
  output (say so if delegated to a model/heuristic). Litmus: *can this be a
  pass/fail test, true regardless of implementation?* If no, it isn't contract.
- **`## WHAT — Verify intent`** — observed behaviors whose intent is unconfirmed
  (swallowed `except`, empty-string/`None` fallback, magic constant, dead param).
  State the observation, then the question; **never** promote these to a "shall".
  These are the highest-value lines — where the AI most likely did something unasked.
- **`## WHAT — Notes & known limitations`** — real fragilities that are not enforced.

Acceptance goes under **`## HOW — Acceptance (= tests)`** as numbered Given/When/Then
`AC-n` (one test each → maps to `tested-by`). The volatile "function X does A then
B" walkthrough goes under **`## WHERE — Current implementation`**, never the
contract. When intent is genuinely ambiguous, write "observed: X; intent
unconfirmed" rather than guessing. The drift gate tracks only Contract + Acceptance
— commentary may change freely.

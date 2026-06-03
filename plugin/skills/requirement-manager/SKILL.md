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

The engine is a single stdlib-only script. Seed it into the target repo once:

```bash
mkdir -p scripts requirements
cp "${CLAUDE_PLUGIN_ROOT}/scripts/reqmap.py" scripts/reqmap.py
```

The requirement template is **built into the engine** — `reqmap.py new` needs no
template file. (Optionally, drop a `templates/requirement.md` in the repo to override
the built-in scaffold; the engine uses it automatically when present.)

**Create `.reqmapignore` immediately after the copy** — `reqmap.py` carries its own
`implements:` self-tags. Without this file the gate fails with dangling-ref errors
on the first run:

```
scripts/reqmap.py
```

Add any other vendored or generated paths that should not be scanned (one fnmatch
glob per line, `#` comments ok). The engine itself is always the first entry.

From then on every command below runs against the repo's own `scripts/reqmap.py`.
Commit both the script and `.reqmapignore` so the gate works in CI without the
plugin present. When the plugin ships a newer `reqmap.py`, re-seed with:

```bash
cp "${CLAUDE_PLUGIN_ROOT}/scripts/reqmap.py" scripts/reqmap.py
```

**Plugin authors** — use `sync_reqmap.sh` (in the plugin source repo) to propagate
engine changes to the cache and any registered consumer repos in one command:

```bash
./sync_reqmap.sh /path/to/consumer-repo1 /path/to/consumer-repo2
```

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
2. **A requirement is its contract.** Fill `WHAT — Contract` (the normative,
   testable behavior) first; the boundary follows from the contract. (Legacy
   requirements may still use `Input → Description → Output`; the engine reads both.)
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
  `confirmed` requirement whose members were not re-touched is flagged stale.

Intent sync is *not* automatable — it surfaces at human review (promote
`baseline → confirmed`).

### Wiring the gate

**Git pre-commit hook** (one-time, per developer clone):

```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
python -X utf8 scripts/reqmap.py check
EOF
chmod +x .git/hooks/pre-commit
```

**GitHub Actions** (enforces the gate for the whole team) — use the published
action, pinned to `@v1`:

```yaml
# .github/workflows/reqmap.yml
name: reqmap gate
on: [push, pull_request]
permissions:
  contents: read            # least privilege — the gate only reads the tree
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: alxmax/requirement-manager/check@v1
        # with:
        #   reqmap-path: scripts/reqmap.py   # where you vendored the engine
        #   working-directory: .             # where requirements/ lives
```

`warn_if_stale` (the vendored-copy staleness notice) is gated on `CLAUDE_PLUGIN_ROOT`,
unset in CI — so it is silent and exit-neutral there by design; the action enforces
only the gate proper. If you prefer not to depend on the action, run the engine
directly instead of the `uses:` line: `- run: python -X utf8 scripts/reqmap.py check`.

The hook and the CI job are independent — wire both so the gate runs locally
before push *and* on the remote for PRs.

## Commands

- `python scripts/reqmap.py new AREA-NAME-NNN`   — scaffold a requirement from the template
- `python scripts/reqmap.py scan`              — list code members per capability
- `python scripts/reqmap.py check`             — run the gate (use as pre-commit/CI hook)
- `python scripts/reqmap.py map`               — generate `requirements/_map.html` (4-tab interactive viewer with search, yellow node highlight, ⊕ center button, fit-to-view) + `requirements/_map.md` (4 Mermaid diagrams)
- `python scripts/reqmap.py extract`           — draft one requirement per untagged file (brownfield bootstrap)
- `python scripts/reqmap.py candidates`        — read-only extraction plan: emit a JSON capability map from legacy code without writing any `.md` files (use before authoring, safer than `extract`). Add `--md-glob 'prompts/**' --md-glob 'modes/**'` to also discover capabilities in authoritative **non-code** files (prompt/spec markdown) — advisory only (writes no `.md`), allowlist-bounded, off unless a glob is given. A human authors + confirms each candidate; the source file is then tagged `generated-from:`/`implements:` and the drift hash anchors on the **authored** Contract+Acceptance, never the source prose (so the prompt may drift freely). The plan carries `coverage_summary` so an unfilled plan can't masquerade as coverage.
- `python scripts/reqmap.py findings`          — aggregate open verify-intent items across all requirements into `requirements/_findings.md`; accepts an AI-triage sidecar (`_findings_triage.json`) for a classified view

**Workflow order** — after modifying requirement files, run these three as a unit
so the lock and map stay in sync:

```bash
python scripts/reqmap.py scan
python scripts/reqmap.py check --update-lock
python scripts/reqmap.py map
```

## Legacy / brownfield (extract mode)

`extract` walks the code and proposes `draft` requirements (structure, input/output
from signatures, `depends_on` from imports). It **cannot** recover intent — it only
captures observed behavior, so:
- Everything it emits is `draft`/`baseline`, never `confirmed`. It never canonizes a
  bug as correct.
- Routing to review is by **risk = blast radius × uncertainty × proximity to known
  problems**, not by parsing ease (clean code can be a clean bug). High-risk →
  review; low-risk → accept as `baseline` (tracked, not asserted correct).
- Aim ~80% auto-`baseline` / ~20% human-`confirmed` as a *health signal*, not a quota.

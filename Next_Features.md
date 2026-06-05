# Next features (deferred)

Backlog of deliberated-but-deferred work. Each item records *why* it is not being
done now and the concrete signal that should reopen it — so "later" is a decision,
not a vague intention.

---

## P2 — `pip install reqmap` / standalone CLI

**Status:** deferred (Senate verdict MODIFY, 2026-06-03 — run
`runs/senate/2026-06-03_084314-reqmap-github-action-pip-cli.json`).

**What it is.** Publish the engine independently of Claude Code so any team can
`pip install reqmap` (and/or a standalone binary) and run the gate, widening the
audience beyond Claude Code users. The engine is already stdlib-only and already a
runnable argparse CLI, so the work is *packaging and distribution*, not new capability.

**Why deferred (not rejected).**
- **No demand evidence (n=0).** Zero issues, install attempts, or user requests show
  that lack of a PyPI package is what blocks adoption — the binding constraint is
  more likely discovery/problem-fit than packaging format. Shipping it now is a bet
  on an unmeasured outcome.
- **Breaks a documented principle.** The current design is intentionally
  "single-file, hermetic, copy-seed, no install friction" (see `CLAUDE.md`). PyPI
  packaging changes the engine from *a script you copy* to *an installable package* —
  a real category change that must be made knowingly, with `CLAUDE.md` updated to
  supersede the principle, not silently.
- **Recurring solo-maintainer cost.** A PyPI release pipeline + a `@`-pinned package
  contract + a 4th version-sync location is perpetual maintenance, not a one-time cost.
- **Silent-divergence risk.** A pip-installed engine and a copy-seeded one could run
  different logic for the same repo, so the gate passes on one install method and
  fails on the other — undetectable without version discipline.

**Reopen when ANY of these is true:**
- ≥3 external adoption reports of P1 (the `check@v1` action), **or** the first
  confirmed non-Claude-Code user, **or**
- one external proof-of-value: `reqmap.py` run successfully on a repo the maintainer
  does not own.

**Prerequisites before building it (don't skip):**
1. Reserve the PyPI name `reqmap` now (a `0.0.1` stub) to block squatters — cheap,
   reversible, keeps the option open even while deferred.
2. Automate version single-sourcing so a 4th location (`pyproject.toml`) cannot drift
   — extend `scripts/check_versions.py` and/or derive all versions from one source.
3. Update `CLAUDE.md` to record the deliberate move away from "hermetic copy-seed".

**Then it requires:** `pyproject.toml`, a package layout, `entry_points` console
script, a release pipeline, and a decision on the optional standalone binary
(stdlib-only Python already runs anywhere Python runs — the binary needs its own
demand justification).

---

## P3 — `extract` warns on low-information ID tokens

**Status:** deferred (Consilium deliberation, 2026-06-05 — `close_and_archive`,
conf=0.73. Source: `docs/findings/2026-06-02-requirement-manager-on-senate.md` §4).

**What it is.** When `extract` mints a requirement ID from a filename token, generic
tokens ("audit", "util", "manager", "handler") can produce misleading-but-plausible
IDs. Example: `senate_todo_audit.py` → `SENATE-AUDIT-001`, which *looks* like the
9-senator deliberation but actually owns the TODO checker. A quality warning at mint
time would flag these for human rename during the review step.

**Why deferred (not rejected).**
- **No demand evidence (n=0).** No external user has reported a confusing auto-generated
  ID. The observation comes from a single internal field test on the Senate repo.
- **Bounded blast radius.** The issue only affects the `extract` first-pass draft;
  users review and rename IDs before confirming. The gate catches orphaned IDs if a
  rename is forgotten.

**Reopen when ANY of these is true:**
- First external report of a confusing auto-generated ID that was not caught in review, **or**
- A prompt-based repo (LLM agent/skill) adopts the plugin and the ID-minting pattern
  produces 3+ misleading IDs in its first `extract` run.

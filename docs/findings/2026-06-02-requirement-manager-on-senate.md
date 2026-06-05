# Findings — requirement-manager applied to the `Senate` repo

Observations from running the plugin against the `Senate` repo
(a 9-senator deliberative-audit skill, stdlib-only Python in `scripts/`, behavior
defined in `prompts/senators/*.md`). Date: 2026-06-02.

---

> **Resolution status (2026-06-05):** §1 resolved in v1.11.0 (`warn_if_stale`, `REQ-CHECK-006`). §4 deferred to `Next_Features.md` (P3). §6 resolved in v1.11.0 (`.md` added to `CODE_EXTS`). All other items are Senate-repo-specific observations with no open plugin action.

---

## 1. The map renderer overlaps with many nodes (FIXED in plugin, stale in seeded repos)

**Symptom.** `requirements/_map.html` rendered with overlapping nodes/edges.

**Cause.** The seeded repo carried an **older** `scripts/reqmap.py` (17.9 KB) than
the updated plugin (26.9 KB). The old renderer hand-positioned nodes inside a fixed
`viewBox="0 0 680 300"` SVG — fine for a few nodes, but 19 nodes overflow and
collide. The new plugin version replaced the hand-rolled SVG with **Mermaid.js
auto-layout** across 5 tabbed panes (System Map / Req→Code / Behavioral /
Dependencies / Risk) and restored `_map.md` generation.

**Resolution in this repo.** Re-copied `scripts/reqmap.py` from the plugin cache,
re-ran `reqmap.py map`. Overlap gone; `_map.md` now produced.

**Plugin-level takeaway.** Because the engine is *vendored into each repo* (by
design, so CI runs without the plugin), a plugin update does **not** propagate to
already-seeded repos. Worth documenting a "re-seed / upgrade" step, and/or stamping
a version string in `reqmap.py` so `check` can warn when the vendored copy is older
than the installed plugin.

---

## 2. The registry is a faithful snapshot of the *Python code* — and nothing else

`reqmap.py scan` shows every requirement maps **1:1 to a `scripts/*.py` file** (or to
functions inside `reqmap.py`):

```
CORE-UTILS-001      → utils.py            SENATE-TODO-001       → senate_todo.py
CORE-MODELS-001     → senate_models.py    SENATE-TRANSCRIPT-001 → senate_transcript.py
SENATE-SYNTH-001    → senate_synth.py     SENATE-OUTCOME-001    → senate_outcome.py
SENATE-PRIORS-001   → senate_priors.py    SENATE-HISTORY-001    → senate_history.py
SENATE-VALID-001    → validate_report.py  SENATE-AUDIT-001      → senate_todo_audit.py
SENATE-TEST-001     → test_senate_synth.py   CORE-*/REQ-* → reqmap.py internals
```

These were bootstrapped by **`extract` (brownfield mode) walking the Python code** —
one draft requirement per script, input/output inferred from signatures. That single
fact explains the two gaps below.

---

## 3. Gap: the senate's actual behavioral core is unowned

The 9 senators — the heart of the skill — each live as a prompt file
(`prompts/senators/{wittgenstein,aurelius,confucius,socrate,musk,dimon,napoleon,deming,tacitus}.md`)
with an Input, an Output (strict JSON), and a `## Limits` lens boundary.

**No requirement covers them, and the prompts carry zero tags.** This is not a
deliberate omission — `extract` walks *code*, and the senators are prompt text, so
the extractor literally never saw them. It's a structural blind spot of extraction:
**behavior expressed in non-code artifacts is invisible to the registry.**

---

## 4. Gap: ID minted from filename can mislabel a capability *(deferred → Next_Features.md P3)*

`SENATE-AUDIT-001`'s title is "TODO drift detector" — it documents
`senate_todo_audit.py`, **not** the senate audit. The ID was minted from the
filename token "audit", so the ID that *looks* like it owns the 9-senator
deliberation actually owns the TODO checker. The real senate audit was never named.

**Plugin-level takeaway.** Extract derives IDs from filenames; a generic token
("audit", "manager", "util") can produce a misleading-but-plausible ID that then
sticks. Consider flagging low-information ID tokens for human rename during the
review step.

---

## 5. Should there be a requirement per senator? — No.

Each `prompts/senators/<name>.md` is *already* a markdown source-of-truth
(Input / Output / Limits). Creating 9 requirement files that restate "audits through
lens X, returns this JSON" would put the same contract in two places — a direct
violation of **"one fact, one home."** That manufactures drift instead of preventing
it.

**Better:** one shared requirement (e.g. `SENATE-SENATORS-001`) capturing the part
*no single prompt owns*:
- the output JSON schema every senator must emit (what `senate_synth.py` consumes),
- the lens-separation invariant ("keep scope from bleeding into another senator's"),
- the roster/topology: exactly these 9 names + dispatch models (from frontmatter).

The 9 prompt files become its **members**; `senate_models.py` (which parses that
frontmatter) is tagged to it too. Per-senator requirements are justified only if each
lens gets materially different *acceptance criteria* — it doesn't today (all are
exercised through `SENATE-TEST-001`).

---

## 6. Should requirements cover `.md` files at all? — Depends on role, and the scanner can't see them today *(resolved in v1.11.0)*

**The scanner does not read `.md`.** `CODE_EXTS` (reqmap.py:19-20) =
`.py .js .ts .tsx .jsx .c .cpp .h .hpp .cc .java .go .rs .html .css .sql .yaml .yml`
— no `.md`. A tag inside a prompt file would be **invisible to the gate**.

By role:
- **Docs** (`docs/senate.md`, `SKILL.md`, `README`, `CLAUDE.md`, `TODO.md`) → should
  *reference* requirement IDs, never become requirements. Turning a doc into a
  requirement duplicates the contract.
- **Prompts** (`prompts/senators/*.md`) → legitimate `validated-against` members
  (data/config that drives behavior). The one `.md` kind worth tracking.

**To make prompt membership real**, add `.md` to `CODE_EXTS` — but **scoped**.
Enabling `.md` blindly makes the scanner walk `requirements/*.md`, `docs/`,
`CLAUDE.md`, etc., any of which can mention a tag pattern *in prose or as an example*,
producing **false-positive members** (the strict `TAG_RE` still matches
`implements: AREA-NAME-001` in prose). Safer: restrict `.md` scanning to a configured
prompt directory, or require an explicit comment-style tag, or add an opt-out marker.

**Plugin-level takeaway.** Repos where behavior lives in prompts/specs (LLM skills,
agents, config-driven systems) are a real use case. Consider a first-class notion of
"prompt/spec artifact" the gate can track without the false-positive risk of scanning
all markdown.

---

## Suggested follow-up for the Senate repo (not yet implemented)

A small bundle, run through `consilium` first (multi-file change):
1. Author `SENATE-SENATORS-001` (shared senator contract).
2. Teach `reqmap.py scan` to read prompt `.md` — scoped to `prompts/` to avoid
   prose false-positives.
3. Tag the 9 prompts `validated-against: SENATE-SENATORS-001` and
   `senate_models.py implements: SENATE-SENATORS-001`.
4. Separately: rename/relabel `SENATE-AUDIT-001` → an ID that reflects "TODO drift
   detector" (e.g. `SENATE-TODOAUDIT-001`), freeing the "audit" name for the real
   deliberation if ever needed.

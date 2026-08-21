# ADR-0009 — The scan scope never widens itself

- **Status:** Accepted
- **Decided:** 2026-08-18, after a three-personality Trias deliberation
- **Evidence:** `CHANGELOG.md` `v2.18.0`, `v2.11.1`; the repo-root `.reqmapignore`

## Context

This repo nests the engine under `plugin/`, so every documented command scanned `plugin/` and
nothing else. Its own CI workflow, its published action, its git hooks and its sync script
carried **zero** membership tags, and the check built to catch an untagged generated `docs/`
bundle could not see this repo's own 99KB poster. The tool was blind to its own supply chain.

The tempting fix is to make the default scan root smarter — walk up to the git root, scan from
there. That would silently change behaviour for every repo that vendors the engine.

## Decision

Widening is **explicit, per invocation**: this repo's CI and hooks pass `--code ..` (or
`--code .` from the root). The shared default, `code_root = a.code or a.root`, is untouched.

A repo that needs extra file types sets `REQMAP_EXTRA_CODE_EXTS` rather than forking the
engine. A repo that needs paths excluded from a widened scan writes its own `.reqmapignore` —
and this repo keeps **two**, one at the root and one under `plugin/`, deliberately not merged:
relocating the original would silently stop excluding those paths for the narrow invocation.

## Consequences

- A consumer scoped to a subdirectory on purpose keeps that scope across every engine update.
  Auto-widening was rejected unanimously as a silent-failure risk to exactly those repos.
- The cost lands here: a `confirmed` requirement whose members all live outside `plugin/` — the
  pipeline-wiring one does — genuinely **errors** under the narrow invocation. That is accepted
  as loud-not-silent: CI and the hook always run widened, and a human running the bare command
  sees an immediately diagnosable error rather than a quiet divergence.
- Widening surfaces generated artifacts that inline requirement prose, and tag syntax quoted
  inside them reads as a real tag. Those paths are excluded by name, each with a comment saying
  why — a maintenance burden accepted in exchange for not making the scanner guess.
- Committed generated artifacts must depend only on **tracked** files, or a locally regenerated
  map cannot be reproduced on CI. That rule now has its own warning (`REQ-TRACKED-042`), added
  after it was broken twice in one day.

## Revisit when

Consumers report the narrow default as a recurring surprise. The fix would then be a
first-run-detected, explicitly-confirmed scope written into a config file — never an implicit
widening.

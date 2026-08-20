# ADR-0005 — Build output is committed, then re-derived in CI

- **Status:** Accepted
- **Decided:** 2026-06-04 (vendored viewer), reproducibility check added 2026-08-20
- **Evidence:** `CHANGELOG.md` `v1.11.0`, `v2.19.0`; `REQ-REPRO-041`; `app/CLAUDE.md`

## Context

The viewer is a Vite + React app. The engine is a stdlib-only Python file that must run in
repos with no Node, no npm and no network. Both statements are load-bearing: the map is much
more useful as an interactive page than as a Mermaid diagram, and requiring a JS toolchain to
get one would undo [ADR-0001](0001-single-file-stdlib-engine.md).

Committing build output is normally an anti-pattern, for a good reason: nothing proves the
committed file still matches the source it claims to come from.

## Decision

Commit the build output, and **re-derive it in CI to prove it matches**.

The viewer's single-file build is vendored beside the engine as `plugin/scripts/_map_viewer.html`,
carrying a `<!--REQMAP_DATA-->` marker. The stdlib engine injects each repo's `_map.json` into
that marker to produce `_map.html`. The same applies to `docs/full_architecture.html`, a
generated Excalidraw poster.

An `artifacts` CI job rebuilds both and compares byte for byte — a literal `git diff --exit-code`
for the viewer (the build overwrites the committed file in place), a temp-dir build and compare
for the poster.

## Consequences

- A consumer gets a rich viewer from a Python script and nothing else. That is the entire point,
  and it is only honest because the artifact is checked.
- Byte-reproducibility becomes a requirement of the build itself, and it is fragile in exactly
  one predictable place: line endings. The check failed on its first CI run, correctly — a
  Windows checkout hands Vite a CRLF template while the Linux build emits LF. Fixed at the
  source: `.gitattributes` pins the template and both artifacts to LF, and the Excalidraw
  builder passes an explicit newline on every write.
- Rebuilding the viewer after touching `app/` is a manual step a contributor must remember. The
  `artifacts` job is what makes forgetting it visible rather than silent.
- `docs/architecture.html` is deliberately **out** of this scheme: it is hand-authored, and only
  its engine-owned regions are checked, by `map --check`.

## Revisit when

A consumer environment can be assumed to have Node — which would mean the audience changed, not
that this trade got cheaper.

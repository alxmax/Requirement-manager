# ADR-0001 — One stdlib-only file, vendored into each repo

- **Status:** Accepted, with an open question about the file's size
- **Decided:** 2026-06-03 (first engine release), reaffirmed through v2.22.0
- **Evidence:** `CHANGELOG.md` `v1.11.0` upgrade notes, `v2.11.1`; `CLAUDE.md` "Single engine file"

## Context

The tool's job is to fail a build when code and requirements disagree. That only helps if it
actually runs — in CI, in a pre-commit hook, on a colleague's laptop, inside an agent session.
Every dependency is a place where it does not run: a package index the runner cannot reach, a
version solver that disagrees with the project's own, a lockfile someone has to maintain, an
install step that turns "try it on this repo" into an afternoon.

The alternative shape — a PyPI package with modules and an entry point — is the normal answer
and buys ordinary things: a smaller module, a real import graph, a version consumers pin.

## Decision

Ship **one** file, `plugin/scripts/reqmap.py`, importing only the standard library, and
**vendor** it: the consumer copies it into their repo (typically `scripts/reqmap.py`) rather
than installing it. All parsing, scanning, gating, mapping, drafting and reporting live in that
file. The published GitHub Action runs the consumer's own copy, not one it brings.

## Consequences

- Adoption cost is one `cp` and a Python that already exists. There is nothing to install, so
  nothing to fail to install.
- The engine is version-pinned by the act of copying: a consumer's build cannot change
  behaviour because an upstream release happened. That is the point, and it is also the cost —
  see [ADR-0010](0010-staleness-detection-in-the-action.md), the whole problem of a copy that
  never gets updated.
- The module is ~5,200 lines. It stays navigable because it is strictly layered (parse → scan →
  gate → render) and every capability carries a requirement id, but the number is a real
  liability and is tracked as an open roadmap item: split behind a concatenating build, or keep
  one file and add a CI line-count budget.
- Some things are simply refused. A YAML library ([ADR-0004](0004-hand-rolled-frontmatter-parser.md)),
  a Markdown parser, a graph library — each would be the smaller local change and the larger
  global one.
- The viewer is the deliberate exception, handled by
  [ADR-0005](0005-committed-build-artifacts.md): a React build is vendored as a pre-built HTML
  template so the stdlib engine can ship a rich UI without depending on Node.

## Revisit when

A dependency would buy something the current shape cannot express at all — not merely express
more tidily. Splitting into several stdlib-only modules is a separate, smaller question and is
already on the roadmap; it does not require reversing this record, only choosing a build step
that still lands one file in a consumer repo.

# ADR-0004 — A hand-rolled frontmatter parser, not a YAML library

- **Status:** Accepted
- **Decided:** 2026-06-03, with the `#`-truncation fix in the v1.16 hardening pass
- **Evidence:** `CLAUDE.md` "Requirement schema"; `TODO.md` v1.16; `CORE-PARSE-001`

## Context

Requirement files open with YAML-shaped frontmatter: `id`, `status`, `layer`, `owner`,
`depends_on`, `milestone`, `lint_exempt`, `test_exempt`. Parsing it properly means PyYAML,
which means a dependency, which [ADR-0001](0001-single-file-stdlib-engine.md) rules out.

## Decision

Parse the frontmatter by hand and constrain the schema to what a simple parser reads
correctly: **scalars and inline lists**. `depends_on: [A, B]` is supported; block sequences,
anchors, multi-line scalars, and nested maps are not. Trailing `#` comments are stripped, and
the field's own value is preserved when it legitimately contains a `#`.

## Consequences

- The schema is deliberately small, which turns out to suit the medium: frontmatter here is
  metadata about a document whose real content is prose, not a configuration language.
- The parser is a genuine source of bugs and has produced them — a `#` inside a scalar was once
  truncated, silently changing a field's value. Every such bug is ours, with no upstream to
  report it to and no upstream to fix it either. Each is now pinned by a regression test.
- Consumers occasionally write valid YAML the engine cannot read. The failure is visible (the
  field reads empty and the gate complains) rather than silent, which is the tolerable half of
  the trade.
- Requirement *bodies* are parsed by the same principle: `_bullets` and `_section_raw` are
  positional rules over Markdown, not a Markdown AST. The same class of bug lives there — see
  the v2.16.1 entry, where a bold-only continuation line was silently dropped from a contract.

## Revisit when

The schema needs a shape the constrained parser cannot express — nested structure, or
multi-line values — for a capability that cannot be redesigned around a flat field. Vendoring a
minimal YAML subset parser would then be the move, not adding a dependency.

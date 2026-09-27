# 0056 — The design review's line limit is 120 columns

Status: Accepted. Date: 2026-09-27. Supersedes the `DESIGN_LINE_MAX = 80` default of
[ADR-0051](0051-the-oop-design-review-returns-to-the-engine.md) (Decision 2); the rest of
that record stands.

## Context

ADR-0051 set the `ask --design` line limit to 80 columns, down from 100, and named its own
revisit condition: if `line-too-long` dominates a repo's report, 80 is a house rule of this
repository rather than a universal default. The maintainer has set the default at 120.

## Decision

`DESIGN_LINE_MAX` defaults to 120. It stays a `CONFIG_KEYS` entry, so a repo that wants a
narrower limit sets it in `requirements/_config.json`. `DESIGN_FILE_MAX_LINES` stays at 500.

## Consequences

- A line of 81 to 120 columns is no longer a `line-too-long` candidate anywhere the default
  applies, so a consumer's design score can only rise.
- This repository's code stays wrapped at 80 columns. Nothing rewraps it; `ask --design`
  simply no longer enforces that width here.

## Revisit when

- A consumer reports that 120 hides lines its reviewers find too wide in a diff.

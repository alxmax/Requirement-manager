# 0057 — Plan input the engine cannot read reaches the gate

Status: Accepted. Date: 2026-09-28. **Supersedes in part** [0040](0040-a-release-is-cut-from-the-plan.md)
(Decision 5, "every signal stays read-only", and the Status line's "no roadmap signal is a
gate rule") — for the planning sidecar's input integrity only. Follows the model of
[0054](0054-invalid-input-cannot-produce-a-passing-verdict.md).

## Context

`load_targets` reads `requirements/_planning.json` fail-open, which is right for a chart
and silent for its author. A bar with no `YYYY-MM-DD` `start` is dropped. An `end` that is
not a date becomes the `start`. A bar may end before it starts, name a lane the plan never
declared, or name a requirement that does not exist or was deprecated. A file that is not
valid JSON reads as an empty plan. None of it was reported anywhere.

Measured on 2026-09-28, with the rule run read-only over every repository on this machine
that has a corpus (eight, four of them with a plan):

- One repository fired, with two findings: two bars naming deprecated requirements. Both
  were real defects in the plan.
- A first draft also reported milestone names that are not versions. One repository plans
  named phases on purpose and never cuts a release; it would have carried five warnings on
  every commit, the noise [0049](0049-a-bare-gate-says-only-what-is-broken.md) removed. That
  check was dropped before this record was written.
- The same consumer carried a list of about ninety entries under `items` in eight milestones.
  No reader has used that key since the viewer stopped drawing it on 2026-09-14. An ignored
  key changes nothing the engine computes.

## Decision

1. **RM037 reports plan input the reader drops, repairs or cannot use**: invalid JSON or a
   non-object file, a dropped bar, a repaired `end`, a bar ending before it starts, a lane
   not listed in `lanes`, a milestone entry dropped for having no valid `due` and no label,
   a `cadence` that is not understood, and a bar `req:` that is missing or deprecated.
2. **Warning in the bare gate, error under `--strict`**, the severity model of 0054. It is in
   `DEFAULT_RULES`, because it says something is broken. It never raises: an unreadable plan
   is one finding.
3. **The plan's content stays out of the gate.** A milestone already shipped
   (`REQ-PLANSTALE-1013`), a Now item with no bar, and a bar past its date remain reports in
   `sync`, `gate --audit` and `health`, as 0040 decided. A key the reader never reads is one
   advisory line in `sync` and `gate --audit`.
4. **One parser.** The findings come from the same `_parse_*` functions `load_targets` uses,
   so the gate and the chart cannot disagree about what was lost.
5. **One "bar done" predicate.** `plandrift.bar_done` decides, for every reader, whether a
   bar's work is finished: `progress: 100`, every ROADMAP item it carries out ticked, or its
   requirement confirmed or implemented. A requirement two bars share lends its items to
   neither. The overdue suggestion of `REQ-PLANDATES-1022` reads it.

Not decided here: `sync --release` refusing a milestone whose bars are not done. The done
predicate was calibrated on one consumer, after it read shipped work as late there; it stays
advisory until it has been checked on at least five repositories it was not tuned on, with
the false-block rate stated.

## Consequences

A consumer whose plan has a defect sees a warning on its next `gate` and nothing fails
unless it runs `--strict`. The measured cost on this machine is two warnings in one
repository, both real. `REQ-PLANSTALE-1013` CASE-6 still holds: no rule reads the
shipped-version signal.

## Revisit when

- A repository reports an RM037 finding that is not a defect in its plan, or
- a second consumer's release is blocked or allowed wrongly by the done predicate, or
- the release refusal above is measured on five repositories and can be decided.

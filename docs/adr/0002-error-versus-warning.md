# ADR-0002 — What may fail a build, and what may only warn

- **Status:** Accepted
- **Decided:** 2026-06-03, severity table consolidated in `REQ-CHECK-006`
- **Evidence:** `CHANGELOG.md` `v2.16.0` (the rejected pairing table), `v2.20.0`; `REQ-CHECK-006`

## Context

A gate that fails a build is only useful while people still believe it. The failure mode is not
a missed defect — it is a check that fires on something correct, gets a `|| true` or a
`continue-on-error` bolted onto it, and then never fires again on the case it was written for.

That risk is not hypothetical here. When levelled test links arrived, the obvious design was a
layer-to-level pairing table (`bus` needs unit tests, `feature` needs integration, `need` needs
system). Measured against this repo's own corpus it would have flagged **36 of 40**
requirements for doing something sound — unit-testing a feature by calling the function.

## Decision

Two severities, split by a single question: *is the finding mechanical and unambiguous, or does
it require a judgement the tool cannot make?*

**ERROR — exit 1.** A code tag pointing at a requirement that does not exist. An enforced
requirement (`in-progress`, `implemented`, `confirmed`) with no `implements:` member. An
invalid `status` or `layer`. A `depends_on` naming an id that is not there. Each is a
statement about the repo that is provably false.

**WARN — exit 0.** Contract drift against the lock. Member drift. A confirmed requirement with
no test link, or a test link whose file holds no test. A malformed `milestone:`. An untracked
lock or member. An untagged `docs/` bundle. Each is a signal that *something may need a human*,
and a human is exactly what it needs.

`--strict` promotes the drift and test-link families to errors for a repo that wants them
enforced. The choice is the consumer's, not the tool's.

## Consequences

- Updating the engine never breaks a green consumer build on a new *warning*, which is what
  makes it safe to ship new checks at all. Several were added this way (member drift, untracked
  members, doc bundles, roadmap signals) with no consumer breakage.
- New checks arrive silent by construction where possible: the levelled rules stay quiet until a
  repo carries at least one levelled tag, and the per-criterion coverage warning until a repo
  carries at least one `verifies:` tag.
- A warning nobody reads is a real cost, and the repo has paid it — 28 lint findings accumulated
  unseen until `lint` was wired into CI in v2.14.0. Warnings must be *displayed* somewhere a
  human looks, or they decay into noise.
- Intent sync — is this contract still what we meant? — stays outside the tool. It is a
  judgement, and pretending otherwise would put an error on a guess.

## Revisit when

A warn-only check accumulates evidence that it is never false: a year of firing, always
correctly, in more than one repo. That is a promotion argument. A single annoying miss is not.

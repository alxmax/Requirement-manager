# Architecture decision records

Eighteen decisions that shape this project, pulled out of `CHANGELOG.md` prose where they
were previously findable only by reading every release note in order.

An ADR here records a decision that is **expensive to reverse** or that a reader would
otherwise mistake for an oversight. Routine choices stay in the changelog entry that made
them. Each record names the evidence it was decided on and the condition that would justify
revisiting it — a decision with no revisit condition is a belief, not a decision.

| # | Decision | Status |
|---|---|---|
| [0001](0001-single-file-stdlib-engine.md) | One stdlib-only file, vendored into each repo | Accepted (size question settled by 0014) |
| [0002](0002-error-versus-warning.md) | What may fail a build, and what may only warn | Accepted |
| [0003](0003-drift-baseline-shape.md) | Contract hash in the lock, member hashes in a sidecar | Accepted |
| [0004](0004-hand-rolled-frontmatter-parser.md) | A hand-rolled frontmatter parser, not a YAML library | Accepted |
| [0005](0005-committed-build-artifacts.md) | Build output is committed, then re-derived in CI | Accepted |
| [0006](0006-three-version-axes.md) | Three independent version numbers | Accepted |
| [0007](0007-v-model-gating-parked.md) | The V-model's right side is levelled; correspondence gating is parked | Superseded by [0019](0019-v-model-left-arm-adopted.md) |
| [0008](0008-command-registry-ssot.md) | One command registry; integration artifacts are generated | Accepted |
| [0009](0009-scan-scope-never-widens-itself.md) | The scan scope never widens itself | Accepted |
| [0010](0010-staleness-detection-in-the-action.md) | Staleness detection lives in the action, not the engine | Accepted |
| [0011](0011-python-floor-is-what-ci-runs.md) | The Python floor is the oldest version CI runs | Accepted |
| [0012](0012-internal-consistency-lint-rejected.md) | No internal-consistency lint | Rejected |
| [0013](0013-business-source-license.md) | Business Source License 1.1 | Accepted (revisit trigger open) |
| [0014](0014-engine-stays-one-file.md) | The engine stays one file, and gets no size gate | Accepted |
| [0015](0015-aggregate-layer-instead-of-implicit-dependency-coverage.md) | A requirement covered by its dependencies is a declared layer, not an inference | Accepted |
| [0016](0016-no-edge-case-marker.md) | No first-class edge-case marker, section, or heuristic | Rejected |
| [0017](0017-consolidated-context-section.md) | Consolidate Notes/Example/Current-implementation into one Context section | Accepted |
| [0018](0018-no-contract-acceptance-traceability-marker-yet.md) | No Contract-to-Acceptance traceability marker, yet | Rejected |
| [0019](0019-v-model-left-arm-adopted.md) | The V-model's left arm is adopted; its checks stay warn-only | Accepted |
| [0020](0020-redundancy-signal-below-the-fire-rate-bar.md) | An exact-duplicate signal ships below ADR-0016's fire-rate bar | Accepted |
| [0021](0021-corpus-grows-only-by-design.md) | The corpus grows only, and that asymmetry is intentional | Accepted |
| [0022](0022-no-minimum-requirement-size-check.md) | No minimum-size check; and no lint ships without both halves of its bar | Accepted |

**Format.** Context → Decision → Consequences → Revisit when. Statuses are `Accepted`,
`Rejected` (considered and deliberately not done), or `Superseded by NNNN`. A record is
never rewritten to match a later change: it gains a superseding record instead, because the
value of the file is the state of knowledge at the time the call was made.

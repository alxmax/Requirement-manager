# ADR-0049 — A bare `gate` says only what is broken

- **Status:** Accepted. Narrows what the bare `gate` verb runs. It supersedes no severity:
  every rule keeps the severity [ADR-0026](0026-gate-rule-registry-and-config-file.md) and the
  records before it gave it. What changes is which rules a bare run executes and which
  readability findings it prints.
- **Decided:** 2026-09-22, at the maintainer's direction, on field feedback from a consumer
  that removed the engine and on the fire-rate measurement below.
- **Evidence:** every default rule and lint check, run by engine `2026-09-22.4` over four
  corpora. Fire rate = confirmed requirements with at least one finding of that rule,
  divided by confirmed requirements.

## Context

A consumer removed the engine. Its gate printed 18 warnings on every commit, 16 of them RM007
("confirmed but no tested-by"), and nobody acted on them in three weeks. They became
background, and a warning nobody reads protects nothing.

The obvious fix was a fire-rate ceiling: withdraw any rule that fires on more than half the
corpus. The measurement did not support it:

| Rule | this repo (261) | Dashboard_Sync (177) | Consilium-py (21) | removed consumer (64) |
|---|---:|---:|---:|---:|
| RM007 no `tested-by` | 0% | 0% | 0% | 25% |
| lint `ac-count-low` | 0.4% | 8.5% | 9.5% | 23% |
| lint `stacked-conditions` | 0.4% | 0% | 48% | 12.5% |
| lint `redundant-modal` | 0% | 0% | 100% | 1.6% |
| RM006 no `implements:` (error) | 0% | 5.6% | 0% | 0% |

No rule passes 50% in two corpora; `redundant-modal` passes it in one. So no rule is noise on
its own. The noise was mixing advice and breakage on one screen, on every commit.

## Decision

1. **A bare `gate` runs `DEFAULT_RULES`** (`reqmap_engine/gate.py`):
   - every error rule (RM001, RM002, RM003, RM006);
   - the warnings that say a link is broken (RM005, RM012, RM023, RM033, RM034, RM036);
   - the warnings about the drift baseline (RM016, RM018, RM019, RM020);
   - the warnings about the committed map (RM022, RM027).

   A test pins the set, and pins that every error rule is in it.
2. **A bare `gate` prints readability errors only.** A requirement missing its Description
   or Cases still fails the build. Style warnings are not printed and not counted.
3. **`gate --full` is the old bare gate**: every rule, every readability finding. `gate
   --audit`, `sync` and `init` run every rule as before. The library default is unchanged:
   `cmd_check` and `run_gate_rules` run the whole registry unless a caller asks for `quiet`.
4. **This repository's CI and dev hook pass `--full`.** The corpus that describes the engine
   is held to every rule. The shipped consumer hook and the Action run the bare gate.
5. **No rule is withdrawn for its fire rate.** The ceiling proposal is answered by the table
   above.

## Consequences

- On the removed consumer's corpus, a bare `gate` prints 2 warnings (a member drift and a
  map made by an older engine). `--full` prints the 47 advisory lines that used to appear on
  every commit.
- A consumer who wants the advice runs `gate --full` or `gate --audit` when they choose to
  read it.
- `gate` has twelve flags now (ARCH-CMDREGISTRY-033).

## Revisit when

- A default rule becomes a warning nobody acts on in a consumer: measure it, then move it out.
- An advisory rule catches breakage a consumer shipped: move it into `DEFAULT_RULES`, with the
  finding cited.

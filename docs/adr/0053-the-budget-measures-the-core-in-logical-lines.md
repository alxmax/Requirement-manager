# ADR-0053 — The budget measures the core in logical lines, under a total-lines ceiling

- **Status:** Accepted. Supersedes the metric of [ADR-0046](0046-the-engine-has-a-line-budget.md)
  and [ADR-0052](0052-the-line-budget-moves-to-the-measured-size.md)'s stop-gap. Amends
  [ADR-0048](0048-the-engines-floor-is-what-it-must-keep.md) as set out below. ADR-0046's
  release-time check and its rule that a budget moves down only with the cut that earns it
  both stand.
- **Decided:** 2026-09-23, at the maintainer's direction, after the gate's cost was measured.
- **Evidence:** `python scripts/check_engine_budget.py` and
  `python scripts/check_engine_perf.py` on 2026-09-23 (numbers below), and the medians of 7
  runs recorded in the pull request that lands this record.

## Context

ADR-0046 counted every physical line the engine vendors. On 2026-09-23 that count went from
13,550 to 16,876, but for three unrelated reasons:

- **Rewrapping from 100 to 80 columns** added about 1,300 lines and changed no behaviour.
- **The design review and the site came back** (ADR-0051).
- **Four modules were split** so none is over 500 lines.

Meanwhile the hook-path gate got faster. The median of 7 runs of `gate --full` went from
2.92s to 2.14s. It no longer builds a design record it strips, and string masking no longer
walks every character.

A count that grows when code is reformatted, and says nothing when the gate slows down,
measures the wrong thing twice over.

## Decision

1. **The release gate measures CORE in logical lines.**
   - CORE is the set of modules the engine's own routine loads. `check_engine_budget.py`
     derives it on every run: it runs `sync` and `gate --full` in-process on a throwaway
     repository and reads the result from `sys.modules`. No list of modules is written down
     anywhere.
   - The unit is `tokenize.NEWLINE`, one per statement. Rewrapping a statement, or adding
     blank or comment lines, changes it by 0.
   - `CORE_LOGICAL_BUDGET = 7,603`, the size measured today, with no headroom. It moves
     down only with the cut that earns it.
2. **The physical total stays visible under a ceiling.**
   - `TOTAL_LINE_CEILING = 17,000` physical lines, for all of `reqmap.py` and
     `reqmap_engine/`.
   - The ceiling is an alarm the maintainer set, not a target. Crossing it fails the check
     and asks for a decision.
   - The total today is 16,876.
3. **CORE is the whole engine today, and this record says so.** `reqmap.py` still imports
   every module eagerly for the flat namespace, and `sync` uses the design review to write
   the map. CORE therefore contains all 67 files. It shrinks only when a module stops being
   loaded by that routine, which is what making an optional module lazy does. The gate
   already skips the design review, and a test asserts that no `design*` module is loaded
   after `gate --full`.
4. **Performance is measured, but does not yet block.** `scripts/check_engine_perf.py`
   reports the median and the sample sd of 10 cold runs per runner in the `quality` job and
   once per OS in the test matrix. It gates nothing today. A later record may make it
   blocking at a recorded median + 3·sd, once there is a series of runs to set that from.
5. **ADR-0048, decision by decision:**
   - **1 (stages withdrawn)** stands.
   - **2 (the 9,303-line floor of kept capabilities)** stands as a fact about physical
     lines. It is no longer compared with any budget.
   - **3 (the next cut names a removable capability)** stands, and is the only meaning of
     "cut the engine" from now on. A removal lowers `CORE_LOGICAL_BUDGET` to the measured
     result in the same commit, when the removed module was in CORE.
   - **4 (decoupling is not a size step)** is amended. It stays true for the vendored
     total. But making a module lazy removes it from CORE, so decoupling now counts when
     the routine no longer loads the module, and only then.
6. **Recorded use decides what stays.**
   - Every command and flag off the hook path carries a `consumer` field in `COMMANDS`.
     The field says where a real use is written down: a workflow step, a hook, the shipped
     skill, or a named repository. On 2026-09-23, 13 of 42 read `none recorded`.
   - The review date is **2027-03-23**. After it, an entry that still reads `none recorded`
     is a removal candidate, removed only through ADR-0048's third decision.
   - Three known consumer repositories are too few for "nobody uses it" to be evidence. A
     `none recorded` entry is a question for the maintainer, never a verdict.

## Consequences

- CI measures CORE and the total on every pull request, and the release step does too. A
  reformatting pull request no longer moves the budget.
- The overrun against ADR-0046's 13,550 is the recorded price of the design review, the
  site, the 80-column house rule and the module splits. It is not a debt this record
  schedules.
- The rewrap and the behaviour changes landed in the same commit, `800df76`, not in separate
  ones. The logical-line unit makes that immaterial to the metric from here on.

## Revisit when

- The perf report has 10 or more recorded runs per runner. Decide then whether it blocks.
- An optional module is made lazy. Re-measure CORE and lower the budget.
- 2027-03-23. Review every `none recorded` consumer.
- The physical total reaches the 17,000 ceiling. Decide whether to cut or to move the
  ceiling, in a new record.

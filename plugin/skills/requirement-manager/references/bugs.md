# Adding a known bug

An assistant adds most bugs: it can read the code a report is about. A person decides what a
bug is worth, so a priority an assistant chose stays marked as an estimate.

1. **Check the list.** `python scripts/reqmap.py ask --bugs --module <module>`. If the bug is
   already there, say so and add nothing.
2. **Check the code.** Find where it happens and read it. A report you could not trace to a
   line can still be added, with `--why` saying what was reported and what you could not find.
3. **Add it.**

   ```bash
   python scripts/reqmap.py sync --bug "What is broken" --module Payments --prio "P2*" --where pay.py:12 --why "What it costs" --source "Where the report came from"
   ```

   - `--module` is the file the bug lands in. Use a name `ask --bugs` already shows when one
     fits.
   - `--prio` is `P0` critical, `P1` high, `P2` medium, `P3` low or `P4` minor.
   - Keep the `*`. Only a person removes it, by editing the row.
   - When the bug breaks a requirement, write its id in `--source` (or `--why`), so
     `gate --show ID` and the requirement's page list the bug.
4. **Show it.** Run `sync`, or `sync --code ..` where the repository requires it, so the bug
   reaches the map.

When you fix a listed bug, put `Fixes-bug: FILE REF` in the commit message, one per line. The
next `sync` moves the row to the register. To close one with no commit, run
`sync --fix "FILE REF"`, with `--note "why"` when it was not a bug, or
`--duplicate-of "FILE REF"` when another row already holds it. Never delete the row by hand.

A fix for a bug that was never listed still belongs in the register, or its counts fall short:
`sync --fix "What was broken" --new --module Payments --commit <sha>` records it under the
module's next number, found on the commit's day unless `--date` says otherwise.

Do not fix the bug in the same step unless you were asked to. Never write to a file
`BUG_SOURCES` names: those belong to the repository, so add to `requirements/bugs/` instead.
An open bug never fails the gate, so do not present one as a failed verdict.

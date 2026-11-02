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
4. **Show it.** Run `sync`, or `sync --code ..` where the repository requires it, so the bug
   reaches the map.

Do not fix the bug in the same step unless you were asked to. Never write to a file
`BUG_SOURCES` names: those belong to the repository, so add to `requirements/bugs/` instead.
An open bug never fails the gate, so do not present one as a failed verdict.

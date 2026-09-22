# hello-drift

One requirement, one file, one contract change: the smallest thing `gate` can catch.

`requirements/HELLO-GREET-001.md` was written, read and set to `confirmed`, and `sync`
recorded its contract in `requirements/_reqlock.json`. Then the contract was edited: it now
also asks `greet` to strip the spaces around `name`. `hello.py` was not touched.

Run the gate from this directory:

```
$ python ../../plugin/scripts/reqmap.py gate
WARN  RM018 HELLO-GREET-001: DRIFT — contract changed since lock; re-check 1 member(s): hello.py:1

1 requirements (1 confirmed, 0 legacy-schema), 1 members, 0 errors, 1 warnings.
...
gate: PASS — link sync + drift + test links, readability, map freshness (advice: `gate --full`).
```

The spec moved ahead of the code, and the gate names the file to re-check. Drift is a
warning (`--strict` makes it an error). To accept it, make `hello.py` match the new clause
and run `python ../../plugin/scripts/reqmap.py sync --accept-drift "why"`. To see it again
from scratch, `git checkout .` in this directory.

In your own repository, the engine sits at `scripts/reqmap.py` and the commands drop the
`../../plugin/` prefix.

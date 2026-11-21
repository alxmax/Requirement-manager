# Check an existing repository (the `check` action)

Part of the `requirement-manager` skill; [SKILL.md](../SKILL.md) links here. The person's guide
is `docs/copilot-audit.md` in the engine's repository.

Use this when the person asks to check code that already has its requirements and tags, for
example: "check `src/billing` and `src/ledger` against the requirements in `specs/` and put the
result in `audit/payments`". Nothing here drafts a requirement or runs `init`.

## Steps

1. **Read the request into four things:** the code folder (one; for several, their common parent
   plus the others listed in `.reqmapignore`), where the requirements are, their format (the
   engine's Markdown, or text, HTML, Markdown, CSV or JSON of the repository's own), and the
   output folder. Ask for any of them you cannot read from the request or the repository.
2. **Refuse an output folder inside the code folder:** its files would be scanned as code. Say
   so and ask for another.
3. **The output folder's `_config.json`.** When it does not exist, write it: one
   `REQUIREMENT_SOURCES` entry with `"root": "repo"`, so its glob reads from the repository
   (`docs/requirements.md` lists the keys; a CSV or JSON source needs a `fields` map, read the
   header first). When it exists, show the change you would make and ask before writing.
4. **Run, with today's flags only:**
   ```bash
   python <engine> --root . --code <code folder> --reqs <output folder> sync
   python <engine> --root . --code <code folder> --reqs <output folder> gate --risk
   ```
   `<engine>` is the `scripts/reqmap.py` this skill carries, or the repository's own. Exit 1
   from `sync` is the gate's verdict on a first check, not a failure to run: the map is written.
5. **Report:** the errors and warnings in plain words, most important first, then the
   absolute path of `<output folder>/_map.html` to open. For each requirement the person asks
   about, run `clarify <ID>` and relay its questions as
   [assistant steps](assistant-steps.md) say.
6. **End with the person's own steps**, which you never take:
   - confirming a requirement (`status: confirmed`);
   - accepting a changed requirement (`sync --accept-drift "reason"`), after they have read the
     code against the new text;
   - answering a question, which they do by choosing an option you then write into the
     requirement;
   - starting an audit (`sync --audit-plan`) and deciding its findings
     ([audit](audit.md)).

## Re-running

The same request later runs step 4 again; `RM019` is code changed since the last run, `RM018` a
requirement whose text changed and nobody accepted. Report those first.

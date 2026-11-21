# Check an existing repository with GitHub Copilot

For a repository that already has its requirements and its tags, and a question: do the two
still agree? Nothing here drafts a requirement; the engine reads what exists and reports what
does not match. Every command below was run as written on a scratch repository on 2026-11-21.
Which Copilot surface reads what is in [integrations](integrations.md#github-copilot).

## What finds what

| A difference between requirements and code | Found by | Reported as |
|---|---|---|
| Code tagged with an id no requirement has | the engine | ERROR `RM001` |
| A confirmed requirement with no code | the engine | ERROR `RM006` |
| A requirement with no test | the engine | WARN `RM007` |
| Code changed since the last `sync`, requirement not | the engine | WARN `RM019` |
| Requirement text changed since the last `sync`, nobody accepted it | the engine | WARN `RM018`, until `--accept-drift` |
| Code that does something other than what a clause says | Copilot, in the audit (step 5) | a finding: `bug`, `not-implemented`, `false-coverage` |
| A clause nobody can test as written | `clarify ID`, and the audit | a question |

The first five need no assistant. The last two need someone to read code against a clause,
which is what the audit asks Copilot to do, one requirement at a time.

## 1. Install the skill (once)

The skill carries its own engine. Put it where Copilot reads skills:

```bash
apm install alxmax/requirement-manager/plugin-full     # lands in .agents/skills/requirement-manager/
# or, from a checkout of this repository:
mkdir -p .github/skills
cp -r <checkout>/plugin-full/skills/requirement-manager .github/skills/
```

The engine is then `.github/skills/requirement-manager/scripts/reqmap.py` (or the same path
under `.agents/skills/`). Its own files are never scanned as your code. To keep the skill's
documents out of the "untagged files" advice too, add one line to `.reqmapignore`:

```text
.github/skills/requirement-manager/**
```

## 2. Say where your requirements and tags are

Requirements already kept as Markdown in the engine's format need nothing. Requirements in your
own text, HTML or Markdown files, and tags written in your own form, are declared in
`requirements/_config.json`:

```json
{
  "REQUIREMENT_SOURCES": [
    {"glob": "specs/*.txt", "format": "text", "start": "^([A-Z]+-[0-9]+):"}
  ]
}
```

Globs are relative to the code root (`--code`, the repository root by default); add
`"root": "repo"` to a source to read its glob from the repository instead. Tag forms other
than `# implements: ID` go in `TRACE_TAGS`. Every key is in [requirements](requirements.md).
Do not run `init` for this: it drafts requirements from untagged code, which is not the question.

## 3. Check

```bash
python .github/skills/requirement-manager/scripts/reqmap.py sync
```

`sync` reads everything, writes the baseline and the map, and exits 1 when the gate fails.
A first check of an existing repository usually fails; the map is written anyway, with the
errors in it. Open `requirements/_map.html`: with no requirement read it opens on Problems,
otherwise Problems is one click away. `gate --risk` prints the same list in the terminal, most
important first.

**One folder or several.** Point `--code` at the folder and `--reqs` at where the results go,
and put the `_config.json` there; with `"root": "repo"` on a source, its glob stays
`specs/*.txt` whichever folder is checked:

```bash
python .github/skills/requirement-manager/scripts/reqmap.py --root . --code src/billing --reqs audit/billing sync
```

Several folders: give their common parent as `--code` and list the others in `.reqmapignore`.

## 4. From then on, every change

Run `sync` again after a change. A function changed since the last `sync` is `RM019`; a
requirement whose text changed is `RM018`, and stays reported until someone who has read the
code against the new text runs:

```bash
python .github/skills/requirement-manager/scripts/reqmap.py sync --accept-drift "why the code still holds"
```

The reason is kept in `requirements/_driftlog.json`. A cloud agent runs no git hook, so the
check that holds for it is the one in CI: `uses: alxmax/requirement-manager/check@v8`.

## 5. Audit what the engine cannot see

The method, the prompt and the record are in the skill's
[audit reference](../plugin-full/skills/requirement-manager/references/audit.md). In short:

1. **You** plan it once: `reqmap.py sync --audit-plan` picks requirements ranked by risk and a
   seeded random set, and writes `requirements/_audit.json`.
2. **Copilot** reviews each planned requirement twice, in two conversations, and adds one
   finding per clause to that file.
3. **You** decide each finding: a real bug, not a bug, a gap, an ambiguous requirement.
4. `reqmap.py gate --audit` reports every rate as k/n with its interval; the map shows it under
   Audit.

A bug that holds is added with `sync --bug TITLE --module M --source ID`; its row names the
requirement, which then lists it in `gate --show ID` and on its page in the map.

## 6. Let Copilot run it

With the skill installed, ask in agent mode or the CLI. For the MCP tools (`reqmap_gate`,
`reqmap_show`, `reqmap_review`, …) add the server to `.vscode/mcp.json` (VS Code) or `.mcp.json`
(Copilot CLI and VS Code's Copilot harness), started from the repository root:

```json
{"servers": {"reqmap": {"type": "stdio", "command": "python",
  "args": [".github/skills/requirement-manager/scripts/reqmap.py", "mcp", "--root", "."]}}}
```

(`.mcp.json` uses `mcpServers` for the same entry.) An example conversation:

```text
You:     Use the requirement-manager skill. Check this repository against its requirements.
Copilot: Runs sync: 2 errors, 3 warnings. PAY-009 is tagged in src/pay.py:5 but no requirement
         has it; PAY-002 has no code; PAY-002 and PAY-003 have no test. The map is in
         requirements/_map.html.
You:     PAY-009 is a typo for PAY-002. Fix the tag.
Copilot: Changes the tag and runs sync: PAY-002 now has code; 0 errors.
You:     I ran sync --audit-plan. Review the first requirement in the plan.
Copilot: Reads PAY-001 with reqmap_review, compares each clause with refund() and its test,
         and records: clause 2 "a refund larger than the charge is refused": bug, the code
         caps it.
You:     Agreed, that is a bug. Add it.
Copilot: Runs sync --bug "Over-refund is capped, not refused" --module Payments --source PAY-001.
```

Confirming a requirement, accepting a drift and deciding a finding stay yours; the skill tells
Copilot so.

## Not observed yet

The directory a stdio MCP server starts in under the Copilot harness, the CLI and the cloud
agent has not been checked against this engine, and neither has skill discovery from
`.github/skills` on every surface. Until they are, start VS Code or the CLI from the repository
root. The rows are in [integrations](integrations.md#github-copilot).

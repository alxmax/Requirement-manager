# requirement-manager

[![ci](https://github.com/alxmax/requirement-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/alxmax/requirement-manager/actions/workflows/ci.yml)

**Stop your AI agent from drifting away from what you already agreed on.**

A long agent session forgets earlier decisions. A fresh session re-implements something a
different way. Two agents on the same repo make incompatible choices, and nothing tells
either of them. The fix isn't a longer prompt — it's a written contract to check against.

`requirement-manager` gives every feature of your project one such file: a Markdown spec
that says *what it should do*. Your code links back to it with a one-line comment,

```python
# implements: AUTH-LOGIN-001
def login(email, password): ...
```

and a small Python script checks that the two never fall out of sync — then draws you a
map of how everything connects. The engine is stdlib only, 14,941 lines across
`scripts/reqmap.py` and the `reqmap_engine/` package beside it: Python 3.9+, no install,
no AI SDK. Copy the two into any repo and it runs, with any assistant or none.

**▶ [Live requirement map](https://alxmax.github.io/Requirement-manager/map.html)** —
this repo's own requirement graph, republished on every push to `main`.

## Three commands

```bash
python scripts/reqmap.py init     # set up requirements/, draft one per capability from the code you have
python scripts/reqmap.py gate     # THE verdict: do the code and the specs still agree? (report-only)
python scripts/reqmap.py sync     # rebuild everything derived: drift baseline, map, findings, site
```

`init` is idempotent and never clobbers a file you already have. `gate` is what you wire
into your pre-commit hook and CI — the only one that can fail a build, and it never writes.
`sync` is the only one that does, so you never edit `_map.*` or `_reqlock.json` by hand.
Confirming a requirement is **not** a command but a person's answer: set
`status: confirmed` once someone has read it. From then on the gate holds you to it, and
`sync` demotes the contract to `draft` if you edit it without re-checking the code.

## The drift it catches

One requirement, one agent session, one drift — real terminal output, not a mockup:

```
$ # requirements/AREA-DEMO-999.md is written, read by a human, set to `confirmed`
$ python scripts/reqmap.py sync
  lock update: AREA-DEMO-999 hash changed (new->703e565f)
lock updated.
WARN  AREA-DEMO-999: confirmed but no tested-by: tag — acceptance tests not linked

1 requirements (1 confirmed, 0 legacy-schema), 1 members, 0 errors, 1 warnings.

$ python scripts/reqmap.py gate
WARN  AREA-DEMO-999: confirmed but no tested-by: tag — acceptance tests not linked
WARN  AREA-DEMO-999: DRIFT — contract changed since lock; re-check 1 member(s): scripts/_demo_hello.py:2

1 requirements (1 confirmed, 0 legacy-schema), 1 members, 0 errors, 2 warnings.
```

Between `sync` and `gate` the contract clause changed (`hello` returns `'hello'` ->
`'hello, world'`) — but the code that backs it, `scripts/_demo_hello.py`, was never touched.
Nothing else in the toolchain catches that; `gate` does, because the drift baseline in
`_reqlock.json` hashes the requirement's own contract text, not just its existence.

## Run the gate in CI

Fail the build on drift, on every push and pull request:

```yaml
- uses: alxmax/requirement-manager/check@v8
```

The action runs `reqmap.py gate` — also the readability lint and the map-freshness check —
and warns when the engine you vendored is older than the one it ships. Inputs, pinning and
the plain `- run:` alternative: [docs/integrations.md](docs/integrations.md).

## Read more

| | |
|---|---|
| [Writing a requirement](docs/requirements.md) | the file format, the optional specification levels, the jargon in plain words |
| [All commands](docs/commands.md) | every verb and flag: `gate`, `ask`, `sync`, `clarify`, `init`, `mcp` |
| [Integrations](docs/integrations.md) | plain CLI, the Claude Code plugin, the MCP server, other assistants, the CI action |
| [Planning and releasing](docs/planning.md) | `ROADMAP.md`, `_planning.json`, `CHANGELOG.md` and `sync --release` |
| [Internals](docs/internals.md) | how this repo is laid out, and measured numbers on a 10,000-file tree |
| [`SKILL.md`](plugin/skills/requirement-manager/SKILL.md) | the authoritative contract: authoring rules, statuses, the gate |
| [Decision records](docs/adr/README.md) | why it works the way it does — including four things considered and not built |

Contributing: [`CONTRIBUTING.md`](CONTRIBUTING.md) · security: [`SECURITY.md`](SECURITY.md)
· licence: [LICENSE](LICENSE), Business Source License 1.1.

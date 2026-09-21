# Language, and the workflow order

Part of the `requirement-manager` skill; [SKILL.md](../SKILL.md) links here.

Requirements are authored in English. A repository that wants them **read** in Romanian, or
in both, declares it once in `requirements/_config.json`:

```json
{ "LANGUAGE": "ro" }
```

`en` (the default), `ro`, or `both`. Any other value is reported and ignored. The setting
changes what the engine *expects*, never what it writes — the engine translates nothing
(`REQ-TRANSLATE-937`): under `ro`/`both` it tracks the Romanian layer and hands over the work.

**When `sync` reports gaps** — *"N requirement(s) have no fresh translation for LANGUAGE `ro`"* —
you are the translator:

1. `python scripts/reqmap.py ask --i18n --json` — every gap with its `id`, `locale`,
   `reason` (`missing` | `stale`), `hash`, and the four source fields `title`, `intent`,
   `contract`, `acceptance`, exactly as the hash was computed over them.
2. Translate the **prose** of those four fields into Romanian. Keep verbatim: requirement
   ids, `CASE-N` labels, the `Given`/`When`/`Then` keywords, anything in backticks, file
   paths, tag names, numbers and units. Keep the line structure of `contract` and
   `acceptance` — the viewer renders them as written.
3. Write each result into `requirements/_i18n/ro.json` under its `id`, with the four
   translated fields and **the same `hash`**. The hash is the key that says "this
   translation matches this version of the requirement"; the next edit to the requirement
   invalidates it and `sync` reports the gap again.
4. `python scripts/reqmap.py sync` — the map now serves the entries; `gate` warns if a
   translated field has no source counterpart (`REQ-TRANSLATE-967`).

The viewer opens in Romanian under `ro` and in English under `en` and `both`, with the
EN/RO toggle offered whenever a translation exists; a reader's own choice is kept.

**`check` no longer exists.** It was a deprecated alias for `gate` through `3.x` and was removed in `v4.0.0`; a hook or CI step that still calls `reqmap.py check` fails with an unknown-command error. Migrate with `sed -i 's/reqmap.py check/reqmap.py gate/' <hook>`.

**Workflow order** — after modifying requirement files, run `sync` as a unit
so the lock and map stay in sync:

```bash
python scripts/reqmap.py sync
# or, if you edited a confirmed/implemented contract:
python scripts/reqmap.py sync --accept-drift
```

`reqmap.py gate` is the freshness gate (no write): it rebuilds the map in
memory and exits non-zero if the committed `_map.*` is stale (a code/requirement
edit shifted it). Wire it next to `gate` in your pre-commit hook / CI so a stale
map can't be committed. A repo that doesn't track a map passes silently.

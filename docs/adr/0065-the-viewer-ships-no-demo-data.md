# ADR-0065 — The viewer ships no demo data; RM017 is retired with it

- **Status:** Accepted.
- **Decided:** 2026-10-06, at the maintainer's direction, after the demo dataset was mistaken
  for real requirements.
- **Evidence:** `plugin/scripts/_map_viewer.html` before and after the change (286,219 →
  266,034 bytes); `scripts/check_engine_budget.py` (core 6,675 → 6,640 logical lines); the
  `artifacts` job in `.github/workflows/ci.yml`, whose SSR smoke runs only against the real
  map (`npm run sync -- --require`).

## Context

`app/src/lib/baked.json` held 15 hand-authored requirements: 13 copied from this corpus, plus
an invented draft, an invented orphan (`REQ-SYNC-014`) and an invented deprecated capability,
so the Problems view had signals to show. The viewer rendered them whenever it received no
map, which happens in two cases:

- the template, `plugin/scripts/_map_viewer.html` or `app/dist-viewer/viewer.html`, opened
  directly; or
- `npm run dev` before `npm run sync`.

In both cases the page looked like a working map, with "local repo" in the top bar and
requirements that exist nowhere. A reader opening the template took `REQ-SYNC-014` for a
real requirement and asked what it was.

Keeping the dataset honest had a cost of its own. RM017 compared it with the live corpus,
`check_viewer_data_sync` and its tests implemented that comparison, a `demoOnly` marker
exempted the invented entries, and an `only_source_repo` switch on every `Rule` existed so
RM017 never ran in a consumer repository. No other rule used that switch.

Nothing needs the dataset. `_map.html`, the file every consumer opens, always carries its
map inline. CI's smoke refuses to run without the real map. A local `npm run sync` copies
the committed `_map.json` into `public/data.json`.

## Decision

1. **No demo dataset.** `baked.json` is deleted and `REQUIREMENTS` starts empty. With no map,
   the viewer shows one screen that says so and names `python scripts/reqmap.py sync`
   (`app/src/components/NoMap.jsx`), in both of its languages.
2. **RM017 is retired.** The rule, `check_viewer_data_sync` and their tests go. The code is
   never reused: a consumer may have written it in `gate_exempt:`, where an unknown code is
   ignored.
3. **`only_source_repo` goes with it.** `Rule` and `gate_rule` lose the parameter, and
   `GateContext` loses `source_repo`, which only that check read. `_is_source_repo` stays:
   `sync` still uses it for this repository's integration artifacts. `REQ-RULES-947` drops
   the clause and its CASE-5.

## Consequences

- The vendored viewer is about 20 KB smaller.
- The core budget drops to 6,640 logical lines, the size measured after the cut.
- The viewer can no longer be shown off without an engine run. The live map on the project
  site serves that purpose with real data.

## Revisit when

- Someone needs the viewer to show something with no map and no engine, for example an
  offline design review. Then any sample must be visibly labelled as a sample on every view,
  not only kept in step with the corpus.

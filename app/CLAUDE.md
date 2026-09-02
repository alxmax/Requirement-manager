# app/ — the requirement-map viewer

Vite + React 18. This app exists to be **vendored as a single HTML file** into the
stdlib engine — see the root `CLAUDE.md` for how `_map.html` is produced.

## Commands (run from `app/`)

```bash
npm run dev            # dev server on :5173 (strict port)
npm run sync           # copy the engine's export into public/data.json (run `reqmap.py export` first)
npm run smoke          # SSR smoke test — CI's `artifacts` job runs it too; run it before vendoring
npm run build:viewer   # REQUIRED after any app/ change: vite build + install-viewer.mjs → plugin/scripts/_map_viewer.html
```

`npm run build` (plain) builds the multi-file site under `dist/` — it does **not**
update the vendored viewer. Only `build:viewer` does.

## Two things that must not break

- **`<!--REQMAP_DATA-->` marker.** The stdlib engine injects each repo's `_map.json`
  at that exact string; `scripts/install-viewer.mjs` refuses to install a build
  missing it. The build must stay single-file (`vite-plugin-singlefile`,
  `vite.viewer.config.js`) — an external asset reference makes `_map.html`
  unopenable by double-click.
- **`src/lib/search.js` is a faithful port of the engine's TF-IDF/cosine search**
  (`ARCH-SEARCH-036`), so CLI and viewer rank identically. Both runtimes are pinned
  to one model by a shared golden fixture asserted in the Python `Search` tests and
  in the SSR smoke — change one side and you must change both.

`app/` is inside the widened reqmap scan (`--code ..`). Every file under `src/` starts with a
`// implements: <ID>` line (`/* ... */` in CSS) — add one to any new file, or the gate
warns once it passes 150 lines. `scripts/ssr-smoke.jsx` is the `tested-by` member; keep its
`test(label, ok)` helper, it is the idiom the gate's test-link check recognizes.

A vendored-viewer change is a shipped change: bump the plugin semver and add a
CHANGELOG entry (see root `CLAUDE.md`).

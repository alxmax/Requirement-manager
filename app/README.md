# Requirement Manager — App

A real **Vite + React** recreation of the four Requirement Manager product
surfaces, built from the high-fidelity design system in *Reqmap Design System*:

| Surface | View | What it is |
|---|---|---|
| **Map** | `src/views/MapView.jsx` | Flagship graph explorer — 4 tabs (System Map / Req→Code / Dependencies / Risk), positioned nodes, dependency edges, click-to-open detail panel with a gold "locate" action. |
| **Problems** | `src/views/ProblemsView.jsx` | Linter-style inbox of every open signal (errors / warnings / review / cautions), filterable; each row jumps to its spec. |
| **Console** | `src/views/ConsoleView.jsx` | The CLI surface — command chips (`req next / check / init / map`) swap terminal output. |
| **Spec** | `src/views/SpecView.jsx` | One requirement rendered for reading: frontmatter → WHY → coverage strip → WHAT → HOW → WHERE → Risk. |

Design tokens (`src/styles/colors_and_type.css`) are lifted **as-is** from the
design system — the single source of visual truth. Never hardcode hex; use the
`--*` custom properties. Light warm-cream is the default; a dark navy-indigo
theme toggles via the top bar (`<html data-theme="dark">`).

## Run

```bash
cd app
npm install
npm run dev        # http://localhost:5173
npm run build      # → dist/
```

## Data: fed by the engine

The app reads its registry from `public/data.json` when present, and otherwise
renders a **baked fallback** dataset (the 13 dogfooded requirements + in-flight
signals) so it always works standalone.

To drive it with live registry data:

```bash
# 1. emit the registry graph from the engine
python ../plugin/scripts/reqmap.py export      # writes requirements/_map.json

# 2. copy it into the app
npm run sync                                    # → public/data.json
```

`reqmap.py export` emits the same `{nodes, edges}` graph that drives the
engine's `_map.html`; `src/lib/loadData.js` adapts each node to the app's
requirement shape. Coverage and git dates are *derived in the viewer* (as the
design specifies) — they are never stored.

## Notes

- The view components are ported from the design system's `ui_kits/` React
  prototypes (which ran via in-browser Babel and `window` globals) into proper
  ES modules with imports/exports.
- The design system's `tweaks-panel` is omitted — it is host-protocol design
  tooling, not product UI. The runtime theme toggle is kept.

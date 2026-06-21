# diagrams/

Rendered Excalidraw posters for the requirement-manager plugin (architecture,
the excalidraw-skill flow, an explainer, an ISO-5807 flowchart).

**Only this README is tracked.** The generated scenes and viewers
(`*.excalidraw`, `*.html`) are deliberately gitignored — they are regenerable
build outputs, not source. The source of truth is the generator scripts under
[`plugin/skills/excalidraw-diagram/examples/`](../plugin/skills/excalidraw-diagram/examples/).

## Regenerate

From the repo root, run each example generator with this directory as its output:

```bash
for f in plugin/skills/excalidraw-diagram/examples/make_*.py; do
    python "$f" diagrams
done
```

This rebuilds:

| File | Generator |
|---|---|
| `full_architecture.*` | `examples/make_full_architecture.py` |
| `explainer.*` | `examples/make_explainer.py` |
| `excalidraw_skill_flow.*` | `examples/make_excalidraw_skill_flow.py` |
| `reqmap_command_flow_iso5807.*` | `examples/make_iso5807_flowchart.py` |

Open a `*.excalidraw` on [excalidraw.com](https://excalidraw.com) to edit, or
double-click the matching `*.html` to view in a browser.

Any other files that appear here (e.g. one-off comparison or gate-verification
scenes) are ad-hoc artifacts without a tracked generator and are equally
gitignored.

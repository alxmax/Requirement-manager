#!/usr/bin/env bash
# implements: REQ-SELFGATE-039
# sync_reqmap.sh — propagate plugin/scripts/reqmap.py to the plugin cache
# and any registered consumer repos.
#
# Usage:
#   ./sync_reqmap.sh                   # sync cache only
#   ./sync_reqmap.sh /path/to/repo     # sync cache + one consumer repo
#   ./sync_reqmap.sh repo1 repo2 ...   # sync cache + multiple consumer repos
#
# The vendored engine is LOCATED, not assumed: `scripts/reqmap.py` is the documented
# path, but a repo may keep it elsewhere (e.g. `requirements/reqmap.py`). A hard-coded
# path made such a repo skip with "not found — run init first", which reads like a
# never-seeded repo rather than a wrong guess, so the sync silently did nothing.
# Only an EXISTING copy is refreshed — this never seeds a repo that has no engine.
#
# The post-sync `sync --accept-drift` runs with the environment it inherits. A repo
# that needs extra scannable extensions must pass them, or the rescan drops those
# members from the lock and map:
#   REQMAP_EXTRA_CODE_EXTS=.mq4,.mqh ./sync_reqmap.sh /path/to/that/repo
set -euo pipefail

# Echo the repo-relative path of an already-vendored reqmap.py, or nothing.
# Known layouts first (cheap, deterministic), then a bounded search so an
# unusual layout is found rather than silently skipped.
find_engine() {
  local repo="$1" p hit
  for p in scripts/reqmap.py requirements/reqmap.py reqmap.py; do
    if [[ -f "$repo/$p" ]]; then printf '%s\n' "$p"; return 0; fi
  done
  hit=$(find "$repo" -maxdepth 3 -name reqmap.py \
          -not -path '*/.git/*' -not -path '*/node_modules/*' \
          -not -path '*/.worktrees/*' -not -path '*/__pycache__/*' \
          2>/dev/null | head -1)
  [[ -n "$hit" ]] && printf '%s\n' "${hit#"$repo"/}"
  # Always succeed: under `set -e` a non-zero return here would abort the whole
  # run at `REL=$(find_engine ...)`, killing the sync instead of warning and
  # moving to the next repo. "Not found" is reported by the empty stdout.
  return 0
}

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$SCRIPT_DIR/plugin/scripts/reqmap.py"
# The pre-built single-file viewer ships beside the engine; propagate it too so
# `map` can emit the self-contained _map.html wherever the engine lands.
VIEWER_SRC="$SCRIPT_DIR/plugin/scripts/_map_viewer.html"
# Derive the cache path from the plugin's declared version (NOT a hard-coded one,
# which silently no-ops once the published version moves on). Fall back to whatever
# version dir is actually installed if that exact one is absent.
CACHE_BASE="$HOME/.claude/plugins/cache/requirement-manager/requirement-manager"
PLUGIN_VERSION=$(grep -m1 '"version"' "$SCRIPT_DIR/plugin/.claude-plugin/plugin.json" \
  | sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/')
CACHE="$CACHE_BASE/$PLUGIN_VERSION"
if [[ ! -d "$CACHE" ]]; then
  CACHE="$(ls -d "$CACHE_BASE"/*/ 2>/dev/null | sort -V | tail -1)"
  CACHE="${CACHE%/}"
fi

# ── 1. source must exist ────────────────────────────────────────────────────
if [[ ! -f "$SRC" ]]; then
  echo "ERROR: source not found: $SRC" >&2; exit 1
fi

VERSION=$(grep -m1 'MAP_ENGINE_VERSION' "$SRC" | sed 's/.*"\([^"]*\)".*/\1/')
echo "syncing reqmap.py  version=$VERSION"

# ── 2. push to plugin cache ─────────────────────────────────────────────────
if [[ -d "$CACHE" ]]; then
  cp "$SRC" "$CACHE/scripts/reqmap.py"
  [[ -f "$VIEWER_SRC" ]] && cp "$VIEWER_SRC" "$CACHE/scripts/_map_viewer.html" && echo "  → viewer template updated"
  echo "  → plugin cache updated"
  # regenerate the plugin's own map
  (cd "$CACHE" && python -X utf8 scripts/reqmap.py map 2>&1 | sed 's/^/     /')
else
  echo "  WARN: plugin cache not found at $CACHE — skipping"
fi

# ── 3. push to consumer repos (optional args) ────────────────────────────────
for REPO in "$@"; do
  if [[ ! -d "$REPO" ]]; then
    echo "  WARN: repo not found: $REPO — skipping"; continue
  fi
  REL=$(find_engine "$REPO")
  if [[ -z "$REL" ]]; then
    echo "  WARN: no vendored reqmap.py under $REPO — skipping (run init first)"; continue
  fi
  ENGINE_DIR=$(dirname "$REL")
  cp "$SRC" "$REPO/$REL"
  # Refresh the viewer template only where the repo already has one. Dropping a new
  # one in would make `map` start emitting _map.html in a repo that never tracked it.
  if [[ -f "$VIEWER_SRC" && -f "$REPO/$ENGINE_DIR/_map_viewer.html" ]]; then
    cp "$VIEWER_SRC" "$REPO/$ENGINE_DIR/_map_viewer.html"
  fi
  echo "  → $REPO synced ($REL)"
  (cd "$REPO" && python -X utf8 "$REL" sync --accept-drift 2>&1 | sed 's/^/     /')
done

echo "done."

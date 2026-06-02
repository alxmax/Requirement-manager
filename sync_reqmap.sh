#!/usr/bin/env bash
# sync_reqmap.sh — propagate plugin/scripts/reqmap.py to the plugin cache
# and any registered consumer repos.
#
# Usage:
#   ./sync_reqmap.sh                   # sync cache only
#   ./sync_reqmap.sh /path/to/repo     # sync cache + one consumer repo
#   ./sync_reqmap.sh repo1 repo2 ...   # sync cache + multiple consumer repos
#
# After syncing a consumer repo, run inside it:
#   python -X utf8 scripts/reqmap.py scan
#   python -X utf8 scripts/reqmap.py check --update-lock
#   python -X utf8 scripts/reqmap.py map
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$SCRIPT_DIR/plugin/scripts/reqmap.py"
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
  DEST="$REPO/scripts/reqmap.py"
  if [[ ! -f "$DEST" ]]; then
    echo "  WARN: $DEST not found — skipping (run init first)"; continue
  fi
  cp "$SRC" "$DEST"
  echo "  → $REPO synced"
  (cd "$REPO" && python -X utf8 scripts/reqmap.py scan \
    && python -X utf8 scripts/reqmap.py check --update-lock \
    && python -X utf8 scripts/reqmap.py map 2>&1 | sed 's/^/     /')
done

echo "done."

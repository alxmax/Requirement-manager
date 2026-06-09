---
id: REQ-SCANCACHE-023
status: confirmed
layer: feature
owner: Alex
depends_on: [CORE-SCAN-002]
superseded_by:
milestone: v1.15
---

# Opt-in scan cache

> Scanning re-reads and re-parses every source file on every run to find membership tags.
> On a large repo that can be the slow part. This is an opt-in cache: when you ask for it, an
> unchanged file is skipped on the next scan. It is off by default and changes nothing about
> the results — only the speed — so the gate stays exactly as deterministic as before.

## WHAT — Contract (normative)
- The `--cache` flag (off by default) shall enable a per-file scan cache for `scan_members`. The
  default path and the CI/gate path shall never read or write the cache unless `--cache` is given.
- The cache shall be a sidecar `requirements/_scancache.json`, keyed per file by `(mtime_ns, size)`
  → the membership tags found in that file. It is machine-local and gitignored — never committed
  (mtimes differ across machines, so a committed cache would be meaningless/stale).
- With the cache on: an unchanged file (matching `mtime_ns` AND `size`) shall reuse its cached
  tags; a changed or new file shall be re-parsed and its entry refreshed; a file no longer present
  shall be pruned (absent from the rewritten cache).
- The cache shall be a PURE performance optimization: `scan_members(cache=True)` returns results
  byte-identical to `scan_members(cache=False)` for any consistent cache — same members, same order.
- The cache shall fail open and best-effort: an absent, unreadable, or corrupt cache yields an
  empty cache (full re-scan), and an unwritable cache directory shall never fail or alter the scan.

## WHAT — Verify intent (open questions for the human)
- None — authored from a Consilium design deliberation (.consilium/runs/2026-06-09_1630_scan-cache.json).

## WHAT — Notes & known limitations (informative)
- `(mtime_ns, size)` keying can miss a same-second, same-size content change in theory; this is
  acceptable because the cache is opt-in and deletable (the default gate path never uses it), so
  the worst case is a manual `rm requirements/_scancache.json`. Content-hash keying was rejected:
  it would have to read every file, eliminating the speedup the cache exists to provide.
- Only `scan_members` is cached; `scan_ac_verifies` (the smaller per-AC verify scan) is not, and
  may be cached later if it ever becomes a measured bottleneck.

## HOW — Acceptance (= tests)
- Given a tagged tree, `scan_members(cache=True)` equals `scan_members(cache=False)` (identical
  members), and a `_scancache.json` sidecar is written.
- Given a tagged file's content changes, a cached re-scan reflects the new tag and drops the old.
- Given a tagged file is deleted, a cached re-scan omits it and prunes its cache entry.
- Given no `--cache`, `scan_members` writes no cache file (off by default).

## WHERE — Current implementation
- `_scancache_path`, `_load_scancache`, `_save_scancache` in `reqmap.py`; `scan_members` (CORE-SCAN-002)
  gains an opt-in `cache=` parameter that reads/writes the sidecar; `--cache` is wired through `main()`.

## Links
- Used by: (auto)
## Members in code (auto)

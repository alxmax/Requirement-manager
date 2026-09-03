---
id: ARCH-SCANCACHE-023
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v1.15
depends_on: [ARCH-SCAN-002]
satisfies: [SYS-READ-103]
---

# Opt-in scan cache

## Description
> Scanning re-reads and re-parses every source file on every run to find membership tags.
> On a large repo that can be the slow part. This is an opt-in cache: when you ask for it, an
> unchanged file is skipped on the next scan. It is off by default and changes nothing about
> the results — only the speed — so the gate stays exactly as deterministic as before.

Every bullet below is binding.
- The `--cache` flag (off by default) enables a per-file scan cache for the single walk `scan_all`, which also serves `scan_members`,, keyed by `(mtime_ns, size)`, returning results byte-identical to an uncached scan; the default path and the CI/gate path never read or write it unless `--cache` is given. [[REQ-SCANCACHE-911]] details the behaviour.

## Cases
CASE-1
  Given  a tagged tree
  When   `scan_members(cache=True)` runs
  Then   it equals `scan_members(cache=False)` (identical members) and a `_scancache.json`
         sidecar is written

CASE-2
  Given  a tagged file's content changes
  When   a cached re-scan runs
  Then   it reflects the new tag and drops the old

CASE-3
  Given  a tagged file is deleted
  When   a cached re-scan runs
  Then   it omits the file and prunes its cache entry

CASE-4
  Given  no `--cache`
  When   `scan_members` runs
  Then   it writes no cache file (off by default)

## Context
**Notes**
- `(mtime_ns, size)` keying can miss a same-second, same-size content change in theory; this is
  acceptable because the cache is opt-in and deletable (the default gate path never uses it), so
  the worst case is a manual `rm requirements/_scancache.json`. Content-hash keying was rejected:
  it would have to read every file, eliminating the speedup the cache exists to provide.
- Since v3.3.0 the one walk `scan_all` is cached, coverage maps included; before that only members were, and
  may be cached later if it ever becomes a measured bottleneck.

**Current implementation**
- `_scancache_path`, `_load_scancache`, `_save_scancache` in `reqmap.py`; `scan_members` (ARCH-SCAN-002)
  gains an opt-in `cache=` parameter that reads/writes the sidecar; `--cache` is wired through `main()`.


--------------------


---
id: REQ-SCANCACHE-911
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCANCACHE-023]
---

# Caching scan results without changing them

## Description
> Re-parsing every source file on every scan is the slow part on a large repo, but the
> gate must stay exactly as deterministic as before. `--cache` keys a sidecar by each
> file's `(mtime_ns, size)`, reusing tags for an unchanged file and re-parsing anything
> that changed or is new, so a cached scan returns results byte-identical to an uncached
> one — never on by default, and never read on the gate's own path.

Every bullet below is binding.
- The `--cache` flag (off by default) enables a per-file scan cache for the single walk `scan_all`, which also serves `scan_members`,. The
  default path and the CI/gate path never read or write the cache unless `--cache` is given.
- The cache is a sidecar `requirements/_scancache.json`, keyed per file by `(mtime_ns, size)`
  → the membership tags found in that file. It is machine-local and gitignored — never committed
  (mtimes differ across machines, so a committed cache would be meaningless/stale).
- With the cache on: an unchanged file (matching `mtime_ns` AND `size`) reuses its cached
  tags; a changed or new file is re-parsed and its entry refreshed; a file no longer present
  is pruned (absent from the rewritten cache).
- The cache is a PURE performance optimization: `scan_members(cache=True)` returns results
  byte-identical to `scan_members(cache=False)` for any consistent cache — same members, same order.
- The cache fails open and best-effort: an absent, unreadable, or corrupt cache yields an
  empty cache (full re-scan), and an unwritable cache directory never fails or alters the scan.

## Cases
CASE-1 — cache sidecar is written only when --cache is passed
  Given  a tagged tree with no `_scancache.json` sidecar yet
  When   `scan_members(code_root, reqs_dir)` runs without `cache=True`
  Then   `requirements/_scancache.json` is not created

CASE-2 — rewriting a file's size invalidates its cache entry
  Given  a file already cached under `scan_members(..., cache=True)`
  When   the file is rewritten with different content and a different size
  Then   the next cached scan drops the old tag and reports only the new one

CASE-3 — a deleted file's entry is pruned from the rewritten cache
  Given  a file already cached by a prior `scan_members(..., cache=True)` run
  When   the file is removed and a cached scan runs again
  Then   its capability disappears from the results and its key is absent from
         `_scancache.json`

CASE-4 — cache=True and cache=False return identical members
  Given  the same tagged tree
  When   `scan_members` runs once with `cache=False` and twice with `cache=True`
  Then   all three calls return the same `{cap_id: [(role, file, line)]}` mapping

CASE-5 — a corrupt cache file falls back to a full re-scan
  Given  a `_scancache.json` sidecar containing invalid JSON (`"{ not json"`)
  When   `scan_members(..., cache=True)` runs
  Then   it returns the same members as `scan_members(..., cache=False)`, without raising



CASE-6 — the cache covers all three scan results
  Given  a tree with an `implements:` tag, a levelled `tested-by:` tag and a `verifies:` tag
  When   `scan_all(cache=True)` runs twice
  Then   members, per-case coverage and test levels equal the uncached run both times, and an entry lacking `ac`/`lv` is re-scanned
---
id: ARCH-SCANCACHE-023
status: confirmed
level: architecture
layer: feature
owner: Alex
depends_on: [ARCH-SCAN-002]
satisfies: [SYS-READ-103]
superseded_by:
milestone: v1.15
---

# Opt-in scan cache

> Scanning re-reads and re-parses every source file on every run to find membership tags.
> On a large repo that can be the slow part. This is an opt-in cache: when you ask for it, an
> unchanged file is skipped on the next scan. It is off by default and changes nothing about
> the results — only the speed — so the gate stays exactly as deterministic as before.

## WHAT — Contract (normative)
- The `--cache` flag (off by default) enables a per-file scan cache for `scan_members`. The
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
AC-1
  Given  a tagged tree
  When   `scan_members(cache=True)` runs
  Then   it equals `scan_members(cache=False)` (identical members) and a `_scancache.json`
         sidecar is written

AC-2
  Given  a tagged file's content changes
  When   a cached re-scan runs
  Then   it reflects the new tag and drops the old

AC-3
  Given  a tagged file is deleted
  When   a cached re-scan runs
  Then   it omits the file and prunes its cache entry

AC-4
  Given  no `--cache`
  When   `scan_members` runs
  Then   it writes no cache file (off by default)

## WHERE — Current implementation
- `_scancache_path`, `_load_scancache`, `_save_scancache` in `reqmap.py`; `scan_members` (ARCH-SCAN-002)
  gains an opt-in `cache=` parameter that reads/writes the sidecar; `--cache` is wired through `main()`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-SCANCACHE-644
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCANCACHE-023]
superseded_by:
---

# The --cache flag (off by default) enables a

> The `--cache` flag (off by default) enables a per-file scan cache for `scan_members`.
> The default path and the CI/gate path never read or write the cache unless `--cache` is
> given.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SCANCACHE-645
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCANCACHE-023]
superseded_by:
---

# The cache is a sidecar requirements/_scancache.json, keyed per

> The cache is a sidecar `requirements/_scancache.json`, keyed per file by `(mtime_ns,
> size)` → the membership tags found in that file. It is machine-local and gitignored —
> never committed (mtimes differ across machines, so a committed cache would be
> meaningless/stale).

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SCANCACHE-646
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCANCACHE-023]
superseded_by:
---

# With the cache on: an unchanged file (matching

> With the cache on: an unchanged file (matching `mtime_ns` AND `size`) reuses its cached
> tags; a changed or new file is re-parsed and its entry refreshed; a file no longer
> present is pruned (absent from the rewritten cache).

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SCANCACHE-647
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCANCACHE-023]
superseded_by:
---

# The cache is a PURE performance optimization: scan_members(cache=True)

> The cache is a PURE performance optimization: `scan_members(cache=True)` returns results
> byte-identical to `scan_members(cache=False)` for any consistent cache — same members,
> same order.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-SCANCACHE-648
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCANCACHE-023]
superseded_by:
---

# The cache fails open and best-effort: an absent

> The cache fails open and best-effort: an absent, unreadable, or corrupt cache yields an
> empty cache (full re-scan), and an unwritable cache directory never fails or alters the
> scan.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)

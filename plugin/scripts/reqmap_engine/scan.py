"""The code walk: .reqmapignore, pruning, the cached scan of every tag, `verifies:` coverage and
test levels.
"""
import fnmatch, json, os

from .tags import (
    AC_VERIFY_RE, TEST_LEVEL_RE, _BACKTICK_RE, _ID_RE, _is_code_file, _scan_file_tags,
    _visible_lines
)


_REQS_REAL_CACHE = {}   # reqs_dir -> realpath, resolved once per process


def _prune_dirs(dirpath, dirs, reqs_dir, code_root=None, ignore=()):
    # implements: ARCH-SCAN-002  # implements: REQ-SCAN-909
    """Drop noise dirs and the SSOT output dir from an os.walk in place.

    Excludes ONLY the actual requirements dir (by realpath), not every folder
    that happens to be named 'requirements' — a source package named
    requirements/ must still be scanned. The realpath comparison runs only for a
    directory whose NAME matches the SSOT dir's: resolving every directory on the
    walk was 62% of one consumer's gate time (4,900 upload folders, 35k realpath
    calls for a 216-file scan).

    With `code_root` and `ignore`, a directory that a `.reqmapignore` pattern ending
    in `/**` or `/*` already covers is not descended at all. Every file under it
    matched the pattern anyway, so the result is identical — only the stat calls go."""
    reqs_name = os.path.normcase(os.path.basename(os.path.normpath(reqs_dir))) if reqs_dir else None
    dir_pats = [p for p in ignore if p.endswith(("/**", "/*"))]
    keep = []
    for d in dirs:
        if d in (".git", "node_modules", "__pycache__"):
            continue
        if reqs_name and os.path.normcase(d) == reqs_name:
            real = _REQS_REAL_CACHE.get(reqs_dir)
            if real is None:
                real = _REQS_REAL_CACHE[reqs_dir] = os.path.realpath(reqs_dir)
            if os.path.realpath(os.path.join(dirpath, d)) == real:
                continue
        if dir_pats and code_root is not None:
            rel = os.path.relpath(os.path.join(dirpath, d), code_root).replace(os.sep, "/") + "/"
            if any(fnmatch.fnmatch(rel, p) for p in dir_pats):
                continue
        keep.append(d)
    dirs[:] = keep


def _read_ignore_file(path):
    # implements: ARCH-SCAN-002  # implements: REQ-SCAN-909
    """Patterns from one `.reqmapignore` file (blanks and `#` comments skipped), or
    None when the file is missing, unreadable, or undecodable."""
    try:
        with open(path, encoding="utf-8") as f:
            return [s for s in (line.strip() for line in f) if s and not s.startswith("#")]
    except (OSError, ValueError):   # unreadable OR undecodable: no patterns, no crash
        return None


def load_ignore(code_root, reqs_dir=None):  # implements: ARCH-SCAN-002  # implements: REQ-SCAN-909
    """Read optional `.reqmapignore` (fnmatch globs over POSIX rel paths, one per
    line, blanks and # comments skipped). Looked up in `requirements/` first (the
    consolidated home for reqmap files) then at the scan root; first found wins.
    Patterns are still matched against repo-root-relative paths regardless of where
    the file lives. Fail-open: a missing/unreadable file yields no patterns."""
    for base in ([reqs_dir] if reqs_dir else []) + [code_root]:
        pats = _read_ignore_file(os.path.join(base, ".reqmapignore"))
        if pats is not None:
            return pats   # first .reqmapignore found wins
    return []


def _scancache_path(reqs_dir):  # implements: ARCH-SCANCACHE-023  # implements: REQ-SCANCACHE-911
    return os.path.join(reqs_dir, "_scancache.json")


def _load_scancache(reqs_dir):  # implements: ARCH-SCANCACHE-023  # implements: REQ-SCANCACHE-911
    """Read the opt-in scan-cache sidecar; {} when absent/corrupt (fails open)."""
    try:
        with open(_scancache_path(reqs_dir), encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_scancache(reqs_dir, cache):
    # implements: ARCH-SCANCACHE-023  # implements: REQ-SCANCACHE-911
    """Write the scan cache, best-effort — an unwritable cache must never fail the scan."""
    try:
        with open(_scancache_path(reqs_dir), "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, sort_keys=True)
    except OSError:
        pass


def _walk_files(code_root, reqs_dir=None, accept=None):
    # implements: ARCH-SCAN-002  # implements: REQ-SCAN-909
    """Yield (abs_path, posix_rel_path) for every file under `code_root` the walk admits.

    The one place the walk discipline lives: prune the noise dirs and the SSOT output dir,
    prune a directory a `.reqmapignore` `/**` pattern already covers, descend and read in
    sorted order so a generated artifact is identical across platforms, and drop any path
    an ignore pattern matches. `accept(filename, rel)` is all a caller still decides —
    which files it wants.

    Six loops used to carry a copy of this, drifted in ways that only show up on someone
    else's repo: two never called `dirs.sort()`, so their output depended on filesystem
    order; two called `_prune_dirs` without `code_root`/`ignore`, so a `build/**` pattern
    still descended into build/ and stat'ed every file inside it; and the coverage report
    hand-rolled the prune list, matching neither the SSOT directory by realpath nor an
    ignored tree at all.
    """
    ignore = load_ignore(code_root, reqs_dir)
    for dirpath, dirs, files in os.walk(code_root):
        _prune_dirs(dirpath, dirs, reqs_dir, code_root, ignore)
        dirs.sort()                  # deterministic descent — raw os.walk order is OS-dependent
        # deterministic file order — the map must not depend on the filesystem
        for fn in sorted(files):
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, code_root).replace(os.sep, "/")
            if any(fnmatch.fnmatch(rel, pat) for pat in ignore):
                continue
            if accept is None or accept(fn, rel):
                yield fp, rel


def _walk_code(code_root, reqs_dir=None):  # implements: ARCH-SCAN-002
    """(abs, rel) for every scannable SOURCE file — the walk with the code-file filter."""
    return _walk_files(code_root, reqs_dir, lambda fn, _rel: _is_code_file(fn))


def _extract_coverage(fp, rel, lines, ac_out, level_out):
    # implements: ARCH-ACVERIFY-019  # implements: REQ-SCAN-992
    """Accumulate `verifies:` and levelled `tested-by:` hits from one file's lines.

    One `_visible_lines` pass feeding both regexes, because the two scanners this
    replaces did the identical per-line work twice. The asymmetry between them is
    preserved exactly: only the levelled scan strips backticked spans first, so a
    documented EXAMPLE of a levelled tag does not register as real coverage, while
    `verifies:` keeps its raw scan. Both now see prose fences, which they did not
    before — an example inside a ``` block is an example in either spelling.
    """
    for i, s in _visible_lines(fp, lines):
        for cap, ac in AC_VERIFY_RE.findall(s):
            ac_out.setdefault(cap, {}).setdefault(ac, []).append((rel, i))
        for idlist, level in TEST_LEVEL_RE.findall(_BACKTICK_RE.sub("", s)):
            for cap in _ID_RE.findall(idlist):
                level_out.setdefault(cap, {}).setdefault(level, []).append((rel, i))


def scan_all(code_root, reqs_dir=None, cache=False):
    # implements: ARCH-SCAN-002  # implements: ARCH-SCANCACHE-023
    # implements: REQ-SCAN-908  # implements: REQ-SCANCACHE-911
    """(members, ac_cover, level_cover) from ONE walk that reads each file once.

    The gate used to call three scanners that each walked the whole tree and opened
    every file: on a 10,000-file tree that measured 3.06s + 2.76s + 2.81s of its 8.49s
    total. Results are identical to calling `scan_members` / `scan_ac_verifies` /
    `scan_test_levels` separately; a test asserts that equality.

    Opt-in (cache=True with reqs_dir set): a sidecar keyed by (mtime_ns, size) lets an
    unchanged file skip the read+parse for ALL three extractions. The cache is a PURE
    performance optimization — results are byte-identical to cache=False — and OFF by
    default, so the gate/CI path is unaffected. A changed/new file is re-parsed, a
    vanished file is pruned (absent from the rewritten cache), and an entry written by
    the older members-only cache (no `ac`/`lv` keys) is treated as a miss. `--cache`
    used to be slower than no cache on `gate`: it kept the members walk cached and
    then re-walked the tree twice for the coverage maps."""
    members, ac_cover, level_cover = {}, {}, {}
    use_cache = bool(cache and reqs_dir)
    old = _load_scancache(reqs_dir) if use_cache else {}
    new = {}
    for fp, rel in _walk_code(code_root, reqs_dir):
        ent, st = None, None
        if use_cache:
            try:
                st = os.stat(fp)
            except OSError:
                continue
            e = old.get(rel)
            if (e and e.get("mtime_ns") == st.st_mtime_ns and e.get("size") == st.st_size
                    and "ac" in e and "lv" in e):
                ent = e
        if ent is None:
            try:
                with open(fp, encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            except OSError:
                continue          # unreadable file is skipped, never fatal
            ac, lv = {}, {}
            _extract_coverage(fp, rel, lines, ac, lv)
            ent = {"tags": _scan_file_tags(fp, lines) or [],
                   "ac": [[cap, a, ln] for cap, d in ac.items()
                          for a, locs in d.items() for (_r, ln) in locs],
                   "lv": [[cap, l, ln] for cap, d in lv.items()
                          for l, locs in d.items() for (_r, ln) in locs]}
            if use_cache:
                ent["mtime_ns"], ent["size"] = st.st_mtime_ns, st.st_size
        if use_cache:
            new[rel] = ent
        for role, cap, line in ent["tags"]:
            members.setdefault(cap, []).append((role, rel, line))
        for cap, a, ln in ent["ac"]:
            ac_cover.setdefault(cap, {}).setdefault(a, []).append((rel, ln))
        for cap, l, ln in ent["lv"]:
            level_cover.setdefault(cap, {}).setdefault(l, []).append((rel, ln))
    if use_cache:
        _save_scancache(reqs_dir, new)   # `new` omits vanished files -> prune
    return members, ac_cover, level_cover


def scan_members(code_root, reqs_dir=None, cache=False):
    # implements: ARCH-SCAN-002  # implements: REQ-SCAN-908
    """Walk the code root for `implements:`/`tested-by:` tags -> {cap_id: [(role, file, line)]}.
    The members third of `scan_all`, kept for every caller that only ever asked for
    members; it is not a second walk implementation."""
    return scan_all(code_root, reqs_dir, cache)[0]


def _walk_code_lines(code_root, reqs_dir=None):
    # implements: ARCH-SCAN-002  # implements: REQ-SCAN-908
    """Yield `(rel_path, lineno, line)` for every scannable line under `code_root`.

    The one walk the tag scanners share: it prunes the same directories, honours the
    same `.reqmapignore`, descends in the same sorted order, and masks every excluded
    zone through `_visible_lines`, so a tag inside a Python docstring or a Markdown
    fence is not read as a real tag. A caller receives lines already masked and only
    has to say what a tag means."""
    for fp, rel in _walk_code(code_root, reqs_dir):
        try:
            with open(fp, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except OSError:
            continue
        for i, masked in _visible_lines(fp, lines):
            yield rel, i, masked


def scan_ac_verifies(code_root, reqs_dir=None):
    # implements: ARCH-ACVERIFY-019  # implements: REQ-ACVERIFY-821
    """Walk the code for `# verifies: REQ-X#AC-N` tags and return
    `{cap_id: {ac_label: [(file, line)]}}` — which labelled criterion each test
    covers. Same walk discipline as `scan_members` (respects .reqmapignore, prunes
    .git/node_modules). Empty when no `verifies:` tag exists anywhere."""
    cover = {}  # cap_id -> {ac_label -> [(file, line)]}
    for rel, i, line in _walk_code_lines(code_root, reqs_dir):
        for cap, ac in AC_VERIFY_RE.findall(line):
            cover.setdefault(cap, {}).setdefault(ac, []).append((rel, i))
    return cover


def scan_test_levels(code_root, reqs_dir=None):
    # implements: ARCH-VLEVEL-037  # implements: REQ-VLEVEL-944  # implements: REQ-VLEVEL-945
    """Walk the code for `# tested-by: REQ-X @level` tags and return
    `{cap_id: {level: [(file, line)]}}` — at which V-model level each requirement is
    verified. Kept separate from `scan_members` on purpose: folding the level into the
    member tuples would change the `(role, file, line)` shape that `_map.json` and every
    member consumer depend on. Shares `_walk_code_lines` with `scan_ac_verifies`, so both
    honour the same `.reqmapignore` and the same string-masking. Empty when no levelled
    tag exists."""
    cover = {}  # cap_id -> {level -> [(file, line)]}
    for rel, i, line in _walk_code_lines(code_root, reqs_dir):
        # Strip backticked spans before the search, the same phantom-member guard
        # `_scan_file_tags` applies: a documented EXAMPLE of a levelled tag must not
        # register as real coverage. Without it this scanner matches the example in
        # its own constant's comment.
        line = _BACKTICK_RE.sub("", line)
        for idlist, level in TEST_LEVEL_RE.findall(line):
            for cap in _ID_RE.findall(idlist):
                cover.setdefault(cap, {}).setdefault(level, []).append((rel, i))
    return cover

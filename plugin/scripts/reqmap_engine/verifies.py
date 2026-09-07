"""`sync --suggest-verifies`: propose and apply `# verifies:` tags."""
import os, re

from .acceptance import _automatable_acs
from .scan import scan_ac_verifies


# A test function's own NAME — never its class, never its parameter list. Both mislead:
# a class `TestCiUploadSiDosar` carries the tokens of TWO requirements, so every test
# inside it looked like it belonged to both; and a fixture parameter
# (`def test_export_ac2_x(self, ctx, campaign)`) made a test look like it belonged to
# the requirement whose token happens to name the fixture.
_FUNC_DEF_RE = re.compile(r"^[ \t]*(?:async\s+)?(?:def|function|func)\s+([A-Za-z_]\w*)\s*\(")
_JS_CASE_RE = re.compile(r"""^[ \t]*(?:it|test)\s*\(\s*["'`]([^"'`]{3,120})["'`]""")
_HASH_COMMENT_EXTS = (".py", ".sh", ".bash", ".rb", ".yaml", ".yml", ".tf",
                      ".ex", ".exs", ".jl", ".pl", ".r")


def _test_functions(path):
    # implements: ARCH-SUGGESTVERIFIES-047  # implements: REQ-SUGGESTVERIFIES-927
    """`[(line_no, name)]` for the test cases declared in a file: a `def`/`function`/
    `func` whose own name says "test", plus the Jest/Mocha `it("…")` label. Names only
    (see above). Returns [] for an unreadable file — a suggestion tool never raises."""
    out = []
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except OSError:
        return out
    for i, line in enumerate(lines, 1):
        m = _FUNC_DEF_RE.match(line)
        if m and "test" in m.group(1).lower():
            out.append((i, m.group(1)))
            continue
        m = _JS_CASE_RE.match(line)
        if m:
            out.append((i, m.group(1)))
    return out


def _ac_name_re(ac):  # implements: ARCH-SUGGESTVERIFIES-047  # implements: REQ-SUGGESTVERIFIES-928
    """Match `CASE-3` (or the legacy `AC-3`) inside a test name as `case3`, `case_3`,
    `ac3`, `ac_3`, `ac-3` or `ac 3` — and NOT as a prefix of `case30`, which is a
    different criterion."""
    n = ac.split("-", 1)[1]
    return re.compile(r"(?:^|[^a-z0-9])(?:case|ac)[ _-]?0*{}(?![0-9])".format(re.escape(n)), re.I)


def _comment_prefix(path):
    return "#" if path.lower().endswith(_HASH_COMMENT_EXTS) else "//"


def _ac_test_hits(files, tests_by_file, owners, ident, ac):
    # implements: ARCH-SUGGESTVERIFIES-047  # implements: REQ-SUGGESTVERIFIES-927
    # implements: REQ-SUGGESTVERIFIES-928
    """`[(file, line, name)]` — test hits whose name plausibly verifies the missing
    criterion `ac`, filtered by the three "wrong link" rules `_verifies_proposals`
    documents (name carries the criterion, file/name owns this requirement, no other
    requirement's number). `ident` is this requirement's (distinctive, foreign, mine)
    identity signals, computed once per requirement by the caller."""
    distinctive, foreign, mine = ident
    want = _ac_name_re(ac)
    hits = []
    for fp in files:
        shared = len(owners.get(fp, ())) > 1
        for ln, name in tests_by_file[fp]:
            low = name.lower()
            if not want.search(low):
                continue
            if shared and not any(d in low for d in distinctive):
                continue
            nums = set(re.findall(r"\d{2,}", low)) - {ac.split("-", 1)[1]}
            if (nums & foreign) and mine not in nums:
                continue
            hits.append((fp, ln, name))
    return hits


def _verifies_proposals(reqs, members, code_root, ac_cover):
    # implements: ARCH-SUGGESTVERIFIES-047  # implements: REQ-SUGGESTVERIFIES-927
    # implements: REQ-SUGGESTVERIFIES-928
    """`(proposals, ambiguous)` — the machine-checkable half of "this test already
    verifies that criterion", recovered from naming.

    A proposal is made only when ALL of these hold, each rule paid for by a WRONG link
    it produced when it was missing:
      1. the test's name carries the criterion (`test_ac3_…`);
      2. the file belongs to exactly ONE requirement, OR the test name carries a token
         unique to this requirement's id — a `tested-by` file shared by four
         requirements holds four different `ac1` tests;
      3. the name carries no OTHER requirement's number — `test_ac1_083_…` sits in one
         requirement's file but verifies id 083;
      4. exactly one test matches. Two candidates are reported as ambiguous and never
         written: the tool proposes, the human confirms."""
    counts = {}
    for rid in reqs:
        for part in rid.lower().split("-"):
            counts[part] = counts.get(part, 0) + 1
    numbers = {}
    for rid in reqs:
        m = re.search(r"(\d{2,})$", rid)
        if m:
            numbers[rid] = m.group(1)
    owners = {}
    for rid, hits in members.items():
        for role, fp, _ln in hits:
            if role == "tested-by":
                owners.setdefault(fp, set()).add(rid)
    proposals, ambiguous = [], []
    for rid in sorted(reqs):
        labels = _automatable_acs(reqs[rid]["body"])
        covered = ac_cover.get(rid, {})
        missing = [ac for ac in labels if ac not in covered]
        if not missing:
            continue
        files = sorted({fp for role, fp, _ln in members.get(rid, []) if role == "tested-by"})
        tests_by_file = {fp: _test_functions(os.path.join(code_root, fp)) for fp in files}
        distinctive = [p for p in rid.lower().split("-") if counts.get(p) == 1]
        foreign = {n for other, n in numbers.items() if other != rid}
        mine = numbers.get(rid)
        ident = (distinctive, foreign, mine)
        for ac in missing:
            hits = _ac_test_hits(files, tests_by_file, owners, ident, ac)
            if len(hits) == 1:
                proposals.append((rid, ac) + hits[0])
            elif hits:
                ambiguous.append((rid, ac, hits))
    return proposals, ambiguous


def _apply_verifies(proposals, code_root):
    # implements: ARCH-SUGGESTVERIFIES-047  # implements: REQ-SUGGESTVERIFIES-929
    """Append `# verifies: <id>#AC-N` to each proposed test's declaration line.
    Returns the number of lines written. Idempotent: a line already carrying that
    exact tag is left alone."""
    by_file = {}
    for rid, ac, fp, ln, _name in proposals:
        by_file.setdefault(fp, []).append((ln, rid, ac))
    written = 0
    for fp, items in sorted(by_file.items()):
        path = os.path.join(code_root, fp)
        try:
            with open(path, encoding="utf-8", newline="") as f:
                lines = f.readlines()
        except OSError:
            print("  skipped {} (unreadable)".format(fp))
            continue
        changed = False
        for ln, rid, ac in sorted(items):
            if ln > len(lines):
                continue
            line = lines[ln - 1]
            tag = "{} {}: {}#{}".format(_comment_prefix(fp), "verifies", rid, ac)
            # Exact-tag match, not substring: `tag in line` would treat an existing
            # `...#CASE-11` as already covering a proposed `...#CASE-1` (CASE-1 is a
            # literal prefix of CASE-11), silently dropping the real, missing tag.
            if re.search(re.escape(tag) + r"(?!\d)", line):
                continue
            body, nl = line.rstrip("\r\n"), line[len(line.rstrip("\r\n")):]
            lines[ln - 1] = "{}  {}{}".format(body, tag, nl)
            changed = True
            written += 1
        if changed:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.writelines(lines)
            print("  wrote {}".format(fp))
    return written


def cmd_suggest_verifies(ws, apply_tags=False):
    # implements: ARCH-SUGGESTVERIFIES-047  # implements: REQ-SUGGESTVERIFIES-929
    """Propose `# verifies: <id>#AC-N` tags for tests already NAMED after the criterion
    they check, so a corpus can adopt per-criterion coverage without re-deriving the
    matching rules (and their three traps) by hand. Read-only unless --apply."""
    reqs, members, reqs_dir, code_root = ws.reqs, ws.members, ws.reqs_dir, ws.code_root
    ac_cover = ws.ac_cover
    if ac_cover is None:
        ac_cover = scan_ac_verifies(code_root, reqs_dir)
    proposals, ambiguous = _verifies_proposals(reqs, members, code_root, ac_cover)
    for rid, ac, fp, ln, name in proposals:
        print("{} {}\n  {}:{}  {}  -> {} {}: {}#{}".format(
            rid, ac, fp, ln, name, _comment_prefix(fp), "verifies", rid, ac))
    for rid, ac, hits in ambiguous:
        print("{} {}  AMBIGUOUS — {} candidates, none applied:".format(rid, ac, len(hits)))
        for fp, ln, name in hits:
            print("    {}:{}  {}".format(fp, ln, name))
    if not proposals and not ambiguous:
        print("no suggestions — every automatable criterion is tagged, or no test is "
              "named after one.")
        return 0
    print("\n{} proposal(s), {} ambiguous.".format(len(proposals), len(ambiguous)))
    if apply_tags and proposals:
        n = _apply_verifies(proposals, code_root)
        print("applied {} tag(s). Re-run `reqmap.py sync` to refresh the map.".format(n))
    elif proposals:
        print("re-run with --apply to write them (ambiguous ones are never written).")
    return 0

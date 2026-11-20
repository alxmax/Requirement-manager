"""`sync --retire --apply`: the writes — status, tags, blocks, locks."""
import os, re, sys

from .author import _set_frontmatter_status
from .locks import load_lock, load_memberlock, save_lock, save_memberlock
from .parse import load_requirements, split_requirement_blocks
from .tags import _BACKTICK_RE, _ROLE_ALT, PROSE_EXTS, _visible_lines


def _apply_one_retirement(plan, ws, single, delete, as_json):
    # implements: ARCH-RETIRE-064  # implements: REQ-RETIRE-961
    # implements: REQ-RETIRE-963
    """Apply one retirement step (deprecate or delete), updating `plan`
    in place. Returns 1 when this step failed and the batch's exit
    code should reflect it, else 0 — mirrors the per-step body
    cmd_retire's apply loop used to inline."""
    reqs, reqs_dir, code_root = ws.reqs, ws.reqs_dir, ws.code_root
    cap_id = plan["id"]
    # Re-parsed between steps: retiring one requirement rewrites the file
    # that may hold the next one, and a module file's stale block span would
    # cut the wrong lines out. Only the corpus is re-read — the code walk
    # cannot change here.
    live = reqs if single else load_requirements(reqs_dir)
    if cap_id not in live:
        print("\n{}: already gone, skipped.".format(cap_id))
        return 0
    if not delete:
        ok, msg = _apply_status(live[cap_id], "deprecated")
        print("\n" + msg)
        if not ok:
            return 1
        plan["applied"] = True
        if not as_json:
            print("  its code and tags are untouched; a deprecated "
                  "requirement is exempt from the gates.")
        return 0
    # implements: REQ-RETIRE-1130
    failed = []
    removed_tags = _strip_member_tags(
        code_root or os.path.dirname(reqs_dir) or ".",
        plan["members"], cap_id, failed)
    plan["tags_removed"] = removed_tags
    # Each step runs only when the one before it held: a lock dropped for a
    # block still in its file, or `applied` over a failed write, reports a
    # retirement that did not happen.
    if failed:
        print("\n{}: NOT deleted — could not rewrite {}; the requirement and "
              "its lock entries are left in place.".format(
                  cap_id, ", ".join(failed)), file=sys.stderr)
        return 1
    if not _remove_requirement_block(live[cap_id]):
        print("\n{}: NOT deleted — {} tag(s) stripped, but its block could "
              "not be removed from {}; lock entries kept.".format(
                  cap_id, removed_tags, live[cap_id]["path"]), file=sys.stderr)
        return 1
    _drop_lock_entries(reqs_dir, cap_id)
    plan["applied"] = True
    if not as_json:
        print("\ndeleted {}: {} tag(s) stripped, requirement block removed, "
              "lock entries dropped.".format(cap_id, removed_tags))
        if plan["exclusive_files"]:
            print("  the files listed above now hold code nothing "
                  "points at — delete what is dead.")
    return 0


_EMPTIED_COMMENT_RE = re.compile(r"[^\S\r\n]*(?:\#|//)[^\S\r\n]*(\r?\n?)$")


def _trim_emptied_comment(line):  # implements: REQ-RETIRE-962
    """Drop a comment marker the tag strip left with nothing after it.
    
    `x = f()  # implements: X` must come back as `x = f()`, not as `x = f()  #`.
    The marker only ever opened the comment the tag lived in, so leaving it
    behind litters every consumer file a retire touches. Anchored to end-of-line
    and requiring nothing but horizontal space after the marker, so a real
    trailing comment — and a second tag on the same line — is untouched."""
    return _EMPTIED_COMMENT_RE.sub(r"\1", line)


def _strip_member_tags(code_root, mem, cap_id, failed=None):
    # implements: REQ-RETIRE-962  # implements: REQ-RETIRE-1130
    """Remove `# implements: <id>` / `tested-by` / `verifies` tokens for one id
    from the files that carry them. Pure text: a line that carried ONLY this tag
    goes; a line that carried other tags too keeps them. Function bodies are
    never touched. Only a token the scanner reads as a tag is cut: one inside a
    string literal or a fenced example is text. A file that cannot be read or
    written is appended to `failed`."""
    # `code_root`, not the requirements directory's parent: a member path is
    # relative to the scan root, and `--code ..` makes those two different
    # directories. Deriving one from the other built `plugin/plugin/scripts/...`
    # and silently stripped nothing.
    by_file = {}
    for m in mem:
        by_file.setdefault(m["file"], []).append(m["line"])
    removed = 0
    # Same left guard as TAG_RE and no `#` requirement, so a
    # `// implements:` in a JS or Go member is stripped too (it used
    # to survive and fail the next gate as a dangling tag); the right
    # guard keeps `X-001` from eating the tag of `X-0011`. The trailing
    # run is HORIZONTAL whitespace only. `\s` matches `\n`, and these
    # lines carry their own terminator (splitlines(keepends=True)) —
    # so a tag at the END of a line of code took the newline with it
    # and glued the next line into the comment:
    #     x = compute()  # implements: X   ->   x = compute()  #     if x:
    # if x: (the branch is now comment text) Silent whenever the
    # swallowed line happened to keep the file parseable. A tag
    # trailing a line of code is the shape SKILL.md documents, and
    # every fixture in the suite put its tag on a line of its own,
    # which is why nothing caught it.
    tag_re = re.compile(
        r"(?<![\w-])(?:" + _ROLE_ALT + r"|verifies)\s*:\s*"
        + re.escape(cap_id) + r"(?![\w-])(?:#[A-Za-z]+-\d+)?[^\S\r\n]*")
    for rel in sorted(by_file):
        path = os.path.join(code_root or ".", rel.replace("/", os.sep))
        try:
            with open(path, encoding="utf-8", newline="") as f:
                text = f.read()
        except OSError as e:
            print("  WARN  cannot read {} to strip its tag(s): {}".format(
                rel, e))
            if failed is not None:
                failed.append(rel)
            continue
        lines = text.splitlines(keepends=True)
        visible = dict(_visible_lines(path, lines))
        prose = os.path.splitext(path)[1].lower() in PROSE_EXTS
        out = []
        for i, line in enumerate(lines, 1):
            starts = _tag_starts(tag_re, line, visible.get(i), prose)
            if not starts:
                out.append(line)
                continue
            removed += len(starts)
            stripped = tag_re.sub(
                lambda m: "" if m.start() in starts else m.group(), line)
            # a line that was nothing but this tag (in whatever comment
            # syntax) goes
            if re.fullmatch(r"[\s/*#<!>\-]*",
                            stripped.replace("\r", "").replace("\n", "")):
                continue
            out.append(_trim_emptied_comment(stripped))
        if out == lines:
            continue
        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("".join(out))
        except OSError as e:
            print("  WARN  cannot write {} to strip its tag(s): {}".format(
                rel, e))
            if failed is not None:
                failed.append(rel)
    return removed


def _tag_starts(tag_re, line, seen, prose):  # implements: REQ-RETIRE-1130
    """Offsets in `line` of the tags the scanner reads, as a set. `seen` is the
    line as `_visible_lines` yields it (None: a fenced or indented example, no
    tag at all); strings are blanked in place, so offsets line up. When they do
    not, the line is taken whole, as before: a missed tag fails the next gate,
    a cut literal fails silently."""
    if seen is None:
        return set()
    if prose:
        seen = _BACKTICK_RE.sub(lambda m: " " * len(m.group()), seen)
    raw = line.rstrip("\r\n")
    all_starts = {m.start() for m in tag_re.finditer(raw)}
    if len(seen) != len(raw):
        return all_starts
    return {m.start() for m in tag_re.finditer(seen)} & all_starts


def _remove_requirement_block(r):  # implements: REQ-RETIRE-962
    """Delete one requirement from its file: the whole file when it is the only
    block, otherwise just its block, leaving every sibling byte-identical."""
    path = r["path"]
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            raw = f.read()
    except OSError:
        return False
    eol = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n") if eol == "\r\n" else raw
    blocks = split_requirement_blocks(text)
    if len(blocks) <= 1:
        try:
            os.remove(path)
            return True
        except OSError:
            return False
    idx = r.get("block", 0)
    if idx >= len(blocks):
        return False
    del blocks[idx]
    new_text = "".join(blocks)
    if eol == "\r\n":
        new_text = new_text.replace("\n", "\r\n")
    try:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(new_text)
        return True
    except OSError:
        return False


def _drop_lock_entries(reqs_dir, cap_id):  # implements: REQ-RETIRE-962
    """Drop the retired id from the contract lock and from the member
    sidecar, so the next gate does not carry a baseline for a
    requirement that no longer exists."""
    lock = load_lock(reqs_dir)
    if cap_id in lock:
        del lock[cap_id]
        save_lock(reqs_dir, lock)
    ml = load_memberlock(reqs_dir)
    if cap_id in ml:
        del ml[cap_id]
        save_memberlock(reqs_dir, ml)


def _apply_status(r, status):
    # implements: REQ-RETIRE-961  # implements: REQ-PROMOTE-894
    """Rewrite one requirement's `status:` in place, preserving the
    file's own line endings and every sibling block in a module file.
    Returns (ok, message).

    Extracted so `confirm` and `retire` cannot drift apart on the
    mechanics of editing a requirement in a file that may hold
    several."""
    cur = r["meta"].get("status")
    if cur == status:
        return True, "{} is already {}.".format(
            r["meta"].get("id", "?"), status)
    with open(r["path"], encoding="utf-8-sig", newline="") as f:
        raw = f.read()
    orig_lines = raw.splitlines(keepends=True)
    line_eols = [ln[len(ln.rstrip("\r\n")):] for ln in orig_lines]
    eol = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n") if eol == "\r\n" else raw
    blocks = split_requirement_blocks(text)
    if len(blocks) > 1:
        idx = r.get("block", 0)
        blocks[idx], n = _set_frontmatter_status(blocks[idx], status)
        new_text = "".join(blocks)
    else:
        new_text, n = _set_frontmatter_status(text, status)
    if n == 0:
        return False, "could not find a `status:` line in {}".format(r["path"])
    new_lines = new_text.splitlines()
    if len(new_lines) == len(line_eols):
        new_text = "".join(nl + le for nl, le in zip(new_lines, line_eols))
    elif eol == "\r\n":
        new_text = new_text.replace("\n", "\r\n")
    with open(r["path"], "w", encoding="utf-8", newline="") as f:
        f.write(new_text)
    return True, "{}: {} -> {}".format(
        r["meta"].get("id", "?"), cur or "(unset)", status)

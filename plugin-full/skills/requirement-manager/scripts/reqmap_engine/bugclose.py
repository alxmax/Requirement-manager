"""What happens to a known bug after it is listed (ADR-0082): one row leaves its
module's file for the register, by hand with `sync --fix` or from a commit's
`Fixes-bug:` trailer on `sync`. Imported at call time, like `bugs`."""
import datetime
import os
import re
import shutil
import tempfile

from . import config as cfg
from .bugs import (_PRIO_RE, _cells, _escape, _is_separator, iso_date,
                   load_bugs, named_columns, register_name)
from .git import _git, _git_remote_web_url
from .versions import read_version_file, version_files

COLUMNS = ("ID", "Bug", "Module", "Priority", "Found", "Fixed", "Version",
           "Commit", "Note")
_KEYS = ("id", "title", "module", "prio", "date", "fixed", "version", "commit",
         "note")
NOT_A_BUG = "not a bug"
DUPLICATE = "duplicate"
_DUP_RE = re.compile(r"duplicate of (\S+)")
_NOTHING = "—"
_ID_RE = re.compile(r"(.+)[:\s]\s*(\S+)")


def bug_id(text):
    # implements: REQ-BUGS-1127
    """`FILE:REF` from either spelling, `FILE:REF` or `FILE REF`."""
    m = _ID_RE.fullmatch(" ".join((text or "").split()))
    return ("{}:{}".format(m.group(1).rstrip(": "), m.group(2).rstrip("*"))
            if m else "")


def _register_path(reqs_dir):
    # implements: REQ-BUGS-1127
    return os.path.join(reqs_dir, cfg.BUGS_DIR, register_name())


def _table(lines):
    # implements: REQ-BUGS-1127
    """(header line, one past the last row, {key: column}) of the register's
    table, or None."""
    for n, line in enumerate(lines[:-1]):
        if line.startswith("|") and _is_separator(lines[n + 1]):
            index = named_columns(_cells(line), _KEYS, COLUMNS,
                                  cfg.BUG_REGISTER_COLUMNS)
            if {"id", "title", "fixed"} <= set(index):
                end = n + 2
                while end < len(lines) and lines[end].startswith("|"):
                    end += 1
                return n, end, index
    return None


def parse_fixed(text):
    # implements: REQ-BUGS-1127
    """The register's rows, as dicts of `_KEYS`, in file order."""
    lines = text.lstrip("\ufeff").replace("\r\n", "\n").split("\n")
    table = _table(lines)
    if not table:
        return []
    start, end, index = table
    rows = []
    for line in lines[start + 2:end]:
        cells = _cells(line)
        row = {k: cells[c] if c < len(cells) else "" for k, c in index.items()}
        rows.append({k: row.get(k, "") for k in _KEYS})
    return rows


def _read(path):  # implements: REQ-BUGS-1150
    # implements: REQ-BUGS-1127
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def fixed_rows(reqs_dir):
    # implements: REQ-BUGS-1127
    """The register, fail-open: one that is not UTF-8 reads as empty, and
    `_close` refuses to write over it."""
    try:
        return parse_fixed(_read(_register_path(reqs_dir)))
    except (OSError, UnicodeDecodeError):
        return []


def highest_closed(reqs_dir, stem):
    # implements: REQ-BUGS-1127
    """The highest `B<n>` a closed bug of file `stem` held, so a number is
    never given twice."""
    numbers = [0]
    for row in fixed_rows(reqs_dir):
        file_stem, _, ref = bug_id(row["id"]).rpartition(":")
        m = re.fullmatch(r"B(\d+)", ref)
        if m and file_stem == stem:
            numbers.append(int(m.group(1)))
    return max(numbers)


def close_bug(module_text, register_text, bug, meta):  # implements: REQ-BUGS-1150
    # implements: REQ-BUGS-1127
    """(module text, register text): the row on `bug["line"]` moved to the
    register, whose own columns decide the row's shape. Pure. A file that
    moved under the reader raises ValueError rather than lose another row."""
    kept = re.split(r"(?<=\n)", module_text)
    at = bug["line"] - 1
    if at >= len(kept) or bug["ref"] not in [
            c.rstrip("*").strip() for c in _cells(kept[at].rstrip("\r\n"))]:
        raise ValueError("{} is not on line {} of {}".format(
            bug["ref"], bug["line"], bug["file"]))
    del kept[at]
    return "".join(kept), register_row(register_text, dict(bug, **meta))


def register_row(register_text, values):
    # implements: REQ-BUGS-1127  # implements: REQ-BUGS-1156
    """The register text with one more row, `values` in its own columns,
    creating the table when there is none. Pure."""
    text = register_text.lstrip("\ufeff").replace("\r\n", "\n")
    lines = text.rstrip("\n").split("\n") if text.strip() else ["# Fixed bugs"]
    table = _table(lines)
    if not table:
        lines += ["", "| " + " | ".join(COLUMNS) + " |",
                  "|" + "---|" * len(COLUMNS)]
        table = _table(lines)
    start, end, index = table
    cells = [""] * len(_cells(lines[start]))
    for key, column in index.items():
        cells[column] = _escape(values.get(key))
    lines.insert(end, "| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def version_at(root, reqs_dir, sha=None):
    # implements: REQ-BUGS-1127  # implements: REQ-BUGS-1128
    """The version in the repository's version file, now or at commit `sha`,
    or "" when it keeps none. Teams without versions still have the commit."""
    found = version_files(reqs_dir, root)
    if not found or not sha:
        return found[0][1] if found else ""
    path = found[0][0]
    blob = _git(["-C", root, "show", "{}:./{}".format(sha, path)])
    if blob is None:
        return ""
    folder = tempfile.mkdtemp()
    try:
        copy = os.path.join(folder, os.path.basename(path))
        with open(copy, "w", encoding="utf-8") as f:
            f.write(blob)
        return read_version_file(copy) or ""
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def _writable(root, reqs_dir, bug):  # implements: REQ-BUGS-1150
    # implements: REQ-BUGS-1127
    """Whether `bug` lives in the bugs folder: `BUG_SOURCES` files stay the
    repository's own, read and never written."""
    folder = os.path.abspath(os.path.join(reqs_dir, cfg.BUGS_DIR))
    return (os.path.dirname(os.path.abspath(os.path.join(root, bug["file"])))
            == folder)


def _close(root, reqs_dir, bug, meta):
    # implements: REQ-BUGS-1127
    """Move one row. The register is written first: a crash between the two
    writes leaves a row open and recorded, never lost."""
    path = os.path.join(root, bug["file"])
    module_text, register = close_bug(
        _read(path), _read(_register_path(reqs_dir)), bug, meta)
    with open(_register_path(reqs_dir), "w", encoding="utf-8",
              newline="\n") as f:
        f.write(register)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(module_text)


def duplicates_of(reqs_dir):
    # implements: REQ-BUGS-1156
    """{kept id: [ids closed as its duplicate]}, read from the register."""
    out = {}
    for row in fixed_rows(reqs_dir):
        m = _DUP_RE.search(row["note"] or "")
        if row["version"] == DUPLICATE and m:
            out.setdefault(bug_id(m.group(1)), []).append(bug_id(row["id"]))
    return out


def _found_on(root, a):
    # implements: REQ-BUGS-1156
    """The day a bug never listed was found: `--date`, else the day of the
    commit `--commit` names, else today."""
    if a.date:
        return iso_date(a.date)
    day = a.commit and _git(["-C", root, "log", "-1", "--format=%cs", a.commit])
    return (day or "").strip() or datetime.date.today().isoformat()


def _next_ref(root, reqs_dir, files, name):
    # implements: REQ-BUGS-1156
    """The next `B<n>` of module file `name`: past every open row and every
    row the register holds for it, so a number is never given twice."""
    from .bugs import _REF_RE
    listed = [int(n) for n in _REF_RE.findall(dict(files).get(name, ""))]
    listed += [int(b["ref"][1:]) for b in load_bugs(root, reqs_dir)[0]
               if os.path.basename(b["file"]) == name
               and re.fullmatch(r"B\d+", b["ref"])]
    return "B{}".format(1 + max(
        listed + [highest_closed(reqs_dir, name[:-len(".md")])]))


def _fix_new(root, reqs_dir, title, a):
    # implements: REQ-BUGS-1156
    """`sync --fix TITLE --new --module M`: a fix that never had a row goes
    straight to the register under the module's next free number, so the
    register counts it. The module's file is not written."""
    from .bugs import _folder_files, bug_file, module_file
    if not " ".join((title or "").split()) or not module_file(a.module):
        print("usage: reqmap sync --fix \"TITLE\" --new --module MODULE "
              "[--prio P0-P4] [--date FOUND] [--commit SHA] [--version V] "
              "[--note TEXT]")
        return 2
    prio = (a.prio or "P2").upper()
    found = _found_on(root, a)
    if not re.fullmatch(r"P[0-4]\*?", prio) or not found:
        print("sync --fix --new: --prio is P0 to P4 and --date YYYY-MM-DD")
        return 2
    folder = os.path.join(reqs_dir, cfg.BUGS_DIR)
    try:
        files = _folder_files(folder)
    except (OSError, UnicodeDecodeError) as exc:
        print("sync --fix --new: a file in {} cannot be read: {}".format(
            folder, exc))
        return 2
    name = bug_file(files, a.module)
    head = _git(["-C", root, "rev-parse", "--short", "HEAD"])
    values = {"id": "{}:{}".format(name[:-len(".md")],
                                   _next_ref(root, reqs_dir, files, name)),
              "title": title, "module": a.module, "prio": prio, "date": found,
              "fixed": datetime.date.today().isoformat(),
              "version": a.bug_version or version_at(root, reqs_dir) or _NOTHING,
              "commit": a.commit or (head or "").strip() or _NOTHING,
              "note": a.note or "fixed before it was listed"}
    try:
        register = register_row(_read(_register_path(reqs_dir)), values)
        os.makedirs(folder, exist_ok=True)
        with open(_register_path(reqs_dir), "w", encoding="utf-8",
                  newline="\n") as f:
            f.write(register)
    except (OSError, UnicodeDecodeError) as exc:
        print("sync --fix --new: nothing written: {}".format(exc))
        return 2
    print("bug {} recorded as fixed in {}. Run `sync` to update the map."
          .format(values["id"], os.path.relpath(
              _register_path(reqs_dir)).replace(os.sep, "/")))
    return 0


def _duplicate_meta(known, wanted, a):
    # implements: REQ-BUGS-1156
    """(meta, None) closing `wanted` as a duplicate of `--duplicate-of`, or
    (None, why) when that names none of the `known` ids, open or closed."""
    kept = bug_id(a.duplicate_of)
    if not kept or kept == wanted or kept not in known:
        return None, "--duplicate-of {!r} names no other known bug".format(
            a.duplicate_of)
    note = "duplicate of {}".format(kept) + (
        " — {}".format(a.note) if a.note else "")
    return {"version": DUPLICATE, "commit": _NOTHING, "note": note}, None


def cmd_bug_fix(root, reqs_dir, target, a):  # implements: REQ-BUGS-1150
    # implements: ARCH-BUGS-078  # implements: REQ-BUGS-1127
    """`sync --fix ID`: one row to the register. Exit 2, writing nothing, for
    an id that is unknown, closed already, or in a file this never writes.
    `--new` records a fix that never had a row; `--duplicate-of` closes a
    row as another's duplicate."""
    if getattr(a, "fix_new", False):  # implements: REQ-BUGS-1156
        if getattr(a, "duplicate_of", None):
            print("sync --fix: --new and --duplicate-of do not go together")
            return 2
        return _fix_new(root, reqs_dir, target, a)
    wanted = bug_id(target)
    closed = {bug_id(r["id"]) for r in fixed_rows(reqs_dir)}
    if wanted in closed:
        print("sync --fix: {} is already in the register".format(wanted))
        return 2
    listed = load_bugs(root, reqs_dir)[0]
    bug = next((b for b in listed if b["id"] == wanted), None)
    if bug is None:
        print("sync --fix: no open bug {!r}; `ask --bugs --json` lists the "
              "ids".format(target))
        return 2
    if not _writable(root, reqs_dir, bug):
        print("sync --fix: {} is in {}, which `BUG_SOURCES` names and nothing "
              "here writes; remove the row there".format(wanted, bug["file"]))
        return 2
    head = _git(["-C", root, "rev-parse", "--short", "HEAD"])
    meta = {"id": wanted, "fixed": datetime.date.today().isoformat(),
            "version": a.bug_version or version_at(root, reqs_dir) or _NOTHING,
            "commit": a.commit or (head or "").strip() or _NOTHING}
    if getattr(a, "duplicate_of", None):  # implements: REQ-BUGS-1156
        dup, why = _duplicate_meta({b["id"] for b in listed} | closed, wanted, a)
        if why:
            print("sync --fix: nothing written: " + why)
            return 2
        meta.update(dup)
    elif a.note:
        meta.update(version=NOT_A_BUG, commit=_NOTHING, note=a.note)
    try:
        _close(root, reqs_dir, bug, meta)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print("sync --fix: nothing written: {}".format(exc))
        return 2
    print("bug {} closed in {}. Run `sync` to update the map.".format(
        wanted, os.path.relpath(_register_path(reqs_dir)).replace(os.sep, "/")))
    return 0


def fix_trailers(root):
    # implements: REQ-BUGS-1128
    """[(sha, short sha, date, id)] for every trailer on the history of HEAD,
    oldest first. No git, or no such commit: an empty list."""
    names = [re.escape(str(n)) for n in cfg.BUG_FIX_TRAILERS]
    if not names:
        return []
    args = ["-C", root, "log", "HEAD", "--reverse", "-i", "--extended-regexp",
            "--format=%H%x1f%h%x1f%cs%x1f%B%x1e"]
    out = _git(args + ["--grep=^({}):".format("|".join(names))], timeout=30)
    line_re = re.compile(r"^(?:{}):\s*(.+?)\s*$".format("|".join(names)),
                         re.I | re.M)
    found = []
    for record in (out or "").split("\x1e"):
        parts = record.strip().split("\x1f")
        if len(parts) == 4:
            found += [(parts[0], parts[1], parts[2], bug_id(m))
                      for m in line_re.findall(parts[3])]
    return found


def close_from_commits(root, reqs_dir):
    # implements: ARCH-BUGS-078  # implements: REQ-BUGS-1128
    """Close what the history says is fixed. A bug in the register is left
    alone, so a second run changes nothing, and the register is the only
    state: no lock to conflict on every merge. A trailer that names nothing
    is a printed line, not a gate warning, because a commit cannot be edited
    to clear it."""
    trailers = fix_trailers(root)
    if not trailers:
        return 0
    closed = {bug_id(r["id"]) for r in fixed_rows(reqs_dir)}
    count = 0
    for sha, short, date, wanted in trailers:
        if wanted in closed:
            continue
        bug = next((b for b in load_bugs(root, reqs_dir)[0]
                    if b["id"] == wanted), None)
        if bug is None or not _writable(root, reqs_dir, bug):
            print("! INPUT:bugs commit {} names {}, {}".format(
                short, wanted or "no id",
                "which is in a file nothing here writes" if bug
                else "which is not an open bug"))
            continue
        try:
            _close(root, reqs_dir, bug, {
                "id": wanted, "fixed": date, "commit": short,
                "version": version_at(root, reqs_dir, sha) or _NOTHING})
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            print("! INPUT:bugs commit {}: {}".format(short, exc))
            continue
        closed.add(wanted)
        count += 1
        print("bug {} closed by commit {}".format(wanted, short))
    return count


def fixed_block(reqs_dir):
    # implements: REQ-BUGS-1129
    """The `bugs_fixed` list `_map.json` carries. A priority is split as an
    open bug's is, `P4*` into `P4` and `estimated`, so a filter on P0-P4
    keeps the estimated rows."""
    rows = []
    for row in fixed_rows(reqs_dir):
        row.update(date=iso_date(row["date"]), fixed=iso_date(row["fixed"]))
        prio = _PRIO_RE.search(row["prio"])
        if prio:
            row.update(prio="P" + prio.group(1), estimated="*" in row["prio"])
        rows.append({k: v for k, v in row.items() if v and v != _NOTHING})
    return rows


def forge_of(root):
    # implements: REQ-BUGS-1129
    """The forge a commit links to, only GitHub's URLs being known here. It
    differs between a clone and a fork, so it reaches `_map.html` only."""
    url = _git_remote_web_url(root) or ""
    return url.rstrip("/") if "github." in url else ""

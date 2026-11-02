"""Known bugs, one Markdown file per module (ADR-0080).

`requirements/bugs/<module>.md` holds what `sync --bug` and the viewer add.
`BUG_SOURCES` names other files a repository already keeps; those are read and
never written. Imported at call time, so a repository with no bugs never loads
it. Bugs are not the corpus: nothing here reaches the drift lock, and an open
bug never fails the gate."""
import datetime
import glob
import json
import os
import re

from . import config as cfg

COLUMNS = ("ID", "Bug", "Priority", "Date", "Where", "Why it matters", "Source")
_KEYS = ("id", "title", "prio", "date", "where", "why", "source")
_PRIO_RE = re.compile(r"\bP([0-4])\b")
_ISO_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_DOTTED_RE = re.compile(r"\b(\d{2})\.(\d{2})\.(\d{4})\b")
_REF_RE = re.compile(r"^\|\s*B(\d+)\*?\s*\|", re.M)
_SPLIT_RE = re.compile(r"(?<!\\)\|")


def _cells(line):
    # implements: REQ-BUGS-1116
    """The cells of one Markdown table row; `\\|` stays inside a cell."""
    parts = _SPLIT_RE.split(line.strip())[1:-1]
    return [p.strip().replace("\\|", "|") for p in parts]


def _is_separator(line):
    # implements: REQ-BUGS-1116
    return bool(line.startswith("|")
                and re.match(r"^[\s|:-]+$", line) and "-" in line)


def _column_index(header):
    # implements: REQ-BUGS-1116
    """{key: column} for a table header, or None when it is not a bug table:
    an id, a title and a priority are what makes one. A repository's own
    names come from `BUG_COLUMNS` and add to the canonical ones."""
    names = [c.lower() for c in header]
    index = {}
    for key, own in zip(_KEYS, COLUMNS):
        extra = cfg.BUG_COLUMNS.get(key, ())
        wanted = [own] + ([extra] if isinstance(extra, str) else list(extra))
        for name in wanted:
            if str(name).lower() in names:
                index[key] = names.index(str(name).lower())
                break
    return index if {"id", "title", "prio"} <= set(index) else None


def iso_date(text):
    # implements: REQ-BUGS-1116
    """`text`'s date as YYYY-MM-DD, or "" when it holds no real one."""
    m, parts = _ISO_RE.search(text or ""), None
    if m:
        parts = (m.group(1), m.group(2), m.group(3))
    else:
        m = _DOTTED_RE.search(text or "")
        parts = (m.group(3), m.group(2), m.group(1)) if m else None
    try:
        return datetime.date(*map(int, parts)).isoformat() if parts else ""
    except ValueError:
        return ""


def _file_heading(text, stem):
    # implements: REQ-BUGS-1116
    """(module, date) from `# <anything> — <module> (<date>)`. The file's
    name is the module when there is no heading."""
    m = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    if not m:
        return stem, ""
    title, date = m.group(1), ""
    tail = re.search(r"\(([^()]*)\)\s*$", title)
    if tail and iso_date(tail.group(1)):
        title, date = title[:tail.start()].strip(), iso_date(tail.group(1))
    return re.split(r"\s[—–-]\s", title)[-1].strip() or stem, date


def _row(cells, index, ctx, line_no, problems):
    # implements: REQ-BUGS-1116
    """One bug from one table row, or None with a line in `problems`."""
    cell = lambda key: (cells[index[key]] if key in index
                        and index[key] < len(cells) else "")
    ref = cell("id").rstrip("*").strip()
    where = "{}:{}".format(ctx["file"], line_no)
    prio = _PRIO_RE.search(cell("prio"))
    if not ref or not prio or not cell("title"):
        problems.append("{}: a bug needs an id, a title and a priority P0-P4"
                        .format(where))
        return None
    date = iso_date(cell("date"))
    if cell("date") and not date:
        problems.append("{}: {} has no real date in {!r}".format(
            where, ref, cell("date")))
    bug = {"id": "{}:{}".format(ctx["stem"], ref), "ref": ref,
           "module": ctx["module"], "title": cell("title"),
           "prio": "P" + prio.group(1),
           "estimated": "*" in cell("prio") or cell("id").endswith("*"),
           "date": date or ctx["date"], "where": cell("where"),
           "why": cell("why"), "source": cell("source"), "file": ctx["file"]}
    return bug


def _parse(text, ctx, problems):
    # implements: REQ-BUGS-1116
    """The bugs of every bug table in `text`. A table with other columns is
    somebody else's: a contents page, a list of questions."""
    bugs, seen = [], set()
    lines = text.splitlines()
    index = None
    for n, line in enumerate(lines):
        if not line.startswith("|"):
            index = None
        elif index is None:
            if n + 1 < len(lines) and _is_separator(lines[n + 1]):
                index = _column_index(_cells(line)) or False
        elif index and not _is_separator(line):
            bug = _row(_cells(line), index, ctx, n + 1, problems)
            if bug and bug["id"] in seen:
                problems.append("{}:{}: {} appears twice".format(
                    ctx["file"], n + 1, bug["ref"]))
            elif bug:
                seen.add(bug["id"])
                bugs.append(bug)
    return bugs


def _read_file(path, root, problems):
    # implements: REQ-BUGS-1116
    """The bugs of one file. Fail-open: an unreadable file is one problem."""
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as exc:
        problems.append("{}: unreadable: {}".format(rel, exc))
        return []
    stem = os.path.splitext(os.path.basename(path))[0]
    module, date = _file_heading(text, stem)
    return _parse(text, {"file": rel, "stem": stem, "module": module,
                         "date": date}, problems)


def _bug_paths(root, reqs_dir, problems):
    # implements: REQ-BUGS-1117
    """Every bug file, this repository's own folder first, each path once.
    A declared source that matches nothing is a typo worth a line."""
    paths = sorted(glob.glob(os.path.join(
        glob.escape(os.path.join(reqs_dir, cfg.BUGS_DIR)), "*.md")))
    for pattern in cfg.BUG_SOURCES:
        found = sorted(glob.glob(os.path.join(glob.escape(root), pattern),
                                 recursive=True))
        if not found:
            problems.append("BUG_SOURCES: {!r} matches no file".format(pattern))
        paths += [p for p in found if p not in paths]
    return paths


def load_bugs(root, reqs_dir):
    # implements: ARCH-BUGS-078  # implements: REQ-BUGS-1117
    """(bugs, problems): every known bug of this repository, by file."""
    problems, bugs = [], []
    root = root or "."
    for path in _bug_paths(root, reqs_dir, problems):
        bugs += _read_file(path, root, problems)
    return bugs, problems


def map_block(root, reqs_dir):
    # implements: REQ-BUGS-1117
    """The `bugs` list `_map.json` carries."""
    return load_bugs(root, reqs_dir)[0]


def input_problems(root, reqs_dir):
    # implements: REQ-BUGS-1118
    """The lines the gate reports as `INPUT:bugs`."""
    return load_bugs(root, reqs_dir)[1]


def _escape(value):
    # implements: REQ-BUGS-1119
    return " ".join(str(value or "").split()).replace("|", "\\|")


def module_file(module):
    # implements: REQ-BUGS-1119
    """A module's file name: its words joined by `-`, or "" when it has
    none. The result can never leave the bugs folder."""
    stem = re.sub(r"[^\w]+", "-", module or "", flags=re.U).strip("-")
    return stem + ".md" if stem else ""


def append_bug(text, bug):
    # implements: REQ-BUGS-1119
    """(new text, ref): `bug` added as the last row of the file's bug table,
    with the next free `B<n>`. Pure. `app/src/lib/bugFile.js` is the same
    function for the viewer, and one fixture pins both."""
    text = text.replace("\r\n", "\n")
    if not text.strip():
        text = "# Bugs — {}\n".format(bug["module"])
    ref = "B{}".format(1 + max(
        [int(n) for n in _REF_RE.findall(text)] or [0]))
    row = "| " + " | ".join(
        [ref] + [_escape(bug.get(k)) for k in _KEYS[1:]]) + " |"
    head = "| " + " | ".join(COLUMNS) + " |"
    lines = text.rstrip("\n").split("\n")
    if head in lines:
        at = lines.index(head) + 2
        while at < len(lines) and lines[at].startswith("|"):
            at += 1
        lines.insert(at, row)
    else:
        lines += ["", head, "|" + "---|" * len(COLUMNS), row]
    return "\n".join(lines) + "\n", ref


def cmd_bug_add(reqs_dir, title, a):
    # implements: ARCH-BUGS-078  # implements: REQ-BUGS-1119
    """`sync --bug TITLE`: one row in the module's file. Exit 2 on input that
    would not read back as a bug, and nothing is written."""
    name = module_file(a.module)
    prio = (a.prio or "P2").upper()
    date = iso_date(a.date) if a.date else datetime.date.today().isoformat()
    if not " ".join((title or "").split()) or not name:
        print("usage: reqmap sync --bug \"TITLE\" --module MODULE "
              "[--prio P0-P4[*]] [--date YYYY-MM-DD] [--where FILE:LINE] "
              "[--why TEXT] [--source TEXT]")
        return 2
    if not re.fullmatch(r"P[0-4]\*?", prio):
        print("sync --bug: --prio is P0 to P4, with `*` for an estimate, not "
              "{!r}".format(a.prio))
        return 2
    if not date:
        print("sync --bug: --date is YYYY-MM-DD, not {!r}".format(a.date))
        return 2
    folder = os.path.join(reqs_dir, cfg.BUGS_DIR)
    path = os.path.join(folder, name)
    text = ""
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            text = f.read()
    text, ref = append_bug(text, {
        "module": a.module, "title": title, "prio": prio, "date": date,
        "where": a.where, "why": a.why, "source": a.source})
    os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("bug {} added to {}. Run `sync` to show it on the map.".format(
        ref, os.path.relpath(path).replace(os.sep, "/")))
    return 0


def _matches(bug, module, prio):
    # implements: REQ-BUGS-1120
    return ((not module or module.lower() in bug["module"].lower())
            and (not prio or bug["prio"] == prio.upper()))


def cmd_bugs(root, reqs_dir, module=None, prio=None, as_json=False):
    # implements: ARCH-BUGS-078  # implements: REQ-BUGS-1120
    """`ask --bugs`: the known bugs by module, highest priority first.
    Read-only, exit 0."""
    bugs, problems = load_bugs(root, reqs_dir)
    shown = [b for b in bugs if _matches(b, module, prio)]
    if as_json:
        print(json.dumps({"bugs": shown, "problems": problems},
                         ensure_ascii=False, indent=2))
        return 0
    if not shown:
        print("no known bugs" + (" match" if module or prio else ""))
    groups = {}
    for bug in shown:
        groups.setdefault(bug["module"], []).append(bug)
    for name in sorted(groups):
        print("{} ({})".format(name, len(groups[name])))
        for b in sorted(groups[name], key=lambda x: x["prio"]):
            print("  {}  {:<6} {:<10}  {}".format(
                b["prio"] + ("*" if b["estimated"] else " "), b["ref"],
                b["date"], b["title"]))
    for line in problems:
        print("! INPUT:bugs " + line)
    return 0

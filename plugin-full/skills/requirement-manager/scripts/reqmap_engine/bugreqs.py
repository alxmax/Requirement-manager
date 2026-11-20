"""Which open bugs name a requirement (ADR-0083).

A bug names a requirement by writing its id anywhere in the row: the title,
where, why or source. Nothing is added to the table and nothing reaches the
gate: an open bug is work to do, not a broken link (REQ-BUGS-1118). Imported
at call time, so `sync` and the gate never load it, and `gate --show` loads
`bugs` only when the repository keeps a bug list."""
import re

_FIELDS = ("title", "where", "why", "source")
_TOKEN_RE = re.compile(r"[\w-]+")


def link(bugs, ids):
    # implements: ARCH-BUGS-078  # implements: REQ-BUGS-1131
    """Give each bug `reqs`, the ids of `ids` its row names, sorted, and
    return `bugs`. An id is named whole: `X-10` does not name `X-1`, and
    `X-1#CASE-2` or `[[X-1]]` does."""
    ids = set(ids)
    for bug in bugs:
        text = " ".join(str(bug.get(k) or "") for k in _FIELDS)
        bug["reqs"] = sorted(set(_TOKEN_RE.findall(text)) & ids)
    return bugs


def open_bugs_of(rid, root, reqs_dir):
    # implements: REQ-BUGS-1131
    """The open bugs that name `rid`, highest priority first."""
    from .bugs import load_bugs
    named = [b for b in link(load_bugs(root, reqs_dir)[0], [rid]) if b["reqs"]]
    return sorted(named, key=lambda b: (b["prio"], b["id"]))


def attach(rec, ws):
    # implements: REQ-BUGS-1131
    """`gate --show`'s record with `bugs`, the open bugs that name it, when
    the repository keeps a bug list; without one, `bugs` is never loaded."""
    from .config import bugs_declared
    if ws.reqs_dir and bugs_declared(ws.reqs_dir):
        rec["bugs"] = open_bugs_of(rec["id"], ws.code_root, ws.reqs_dir)
    return rec


def print_open(bugs):
    # implements: REQ-BUGS-1131
    """The dossier's `Open bugs` section, or nothing when no bug names it."""
    if not bugs:
        return
    print("\nOpen bugs ({}):".format(len(bugs)))
    for b in bugs:
        print("  {}  {}  {}".format(
            b["prio"] + ("*" if b.get("estimated") else " "), b["id"],
            b["title"]))

"""Where a tag's code starts and ends, for keying member drift per
definition (ADR-0085, ADR-0089): Python top-level definitions from `ast`,
C/C++ ones from `bracedefs`, which is loaded only for such a file.
"""
# implements: ARCH-MEMBERDRIFT-027
import ast
import hashlib
import os


def _py_def_spans(path):
    # implements: ARCH-MEMBERDRIFT-027  # implements: REQ-MEMBERDRIFT-982
    """`[(lead_line, first_line, last_line, name)]` for the top-level
    definitions of a Python file, or None when it is not Python or does not
    parse. Nesting is deliberately not descended: a tag inside a method
    belongs to the class a reader opens. `lead_line` starts the comments
    right above the definition and its decorators, where most code puts a
    tag; the hash covers `first_line..last_line` only."""
    # implements: REQ-MEMBERDRIFT-1134
    if not path.lower().endswith(".py"):
        return None
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            text = f.read()
        tree = ast.parse(text)
    except (OSError, SyntaxError, ValueError):
        return None
    lines, out = text.splitlines(), []
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            lead = min([n.lineno] + [d.lineno for d in n.decorator_list])
            while lead > 1 and lines[lead - 2].lstrip().startswith("#"):
                lead -= 1
            out.append((lead, n.lineno, getattr(n, "end_lineno", n.lineno), n.name))
    return out


def _span_sha(path, lo, hi):  # implements: REQ-MEMBERDRIFT-982
    """SHA-256 of one line span, LF-normalized exactly as `_file_sha`
    normalizes a whole file — for the same reason: a CRLF checkout must
    not read as drift."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    lines = data.split(b"\n")
    return hashlib.sha256(b"\n".join(lines[lo - 1:hi])).hexdigest()


def _def_spans(path):  # implements: REQ-MEMBERDRIFT-1140
    """Python spans from `ast`; C/C++ ones from `bracedefs`, loaded only then."""
    if os.path.splitext(path)[1].lower() in _C_EXTS:
        from .bracedefs import c_def_spans
        return c_def_spans(path)
    return _py_def_spans(path)


_C_EXTS = (".c", ".h", ".cc", ".cpp", ".cxx", ".hh", ".hpp", ".hxx", ".inl")


def _member_span_key(spans, fp, ln, path):
    # implements: ARCH-MEMBERDRIFT-027  # implements: REQ-MEMBERDRIFT-879
    """(key, span) for one tag hit: `fp#name` / (path, lo, hi) when `ln`
    falls inside a top-level definition or the comments right above it,
    else the whole-file key `fp` with span None."""
    if spans:
        for lead, lo, hi, name in spans:  # implements: REQ-MEMBERDRIFT-1134
            if lead <= ln <= hi:
                return "{}#{}".format(fp, name), (path, lo, hi)
    return fp, None

"""Top-level definitions of a C or C++ file, for keying member drift.

`c_def_spans(path)` answers what `locks._py_def_spans` answers for Python:
`[(lead_line, first_line, last_line, name)]`, or None. Imported at call
time, only when a tagged member is a C or C++ file, so a repository with
none never loads it (ADR-0089).

A wrong span is a wrong drift signal, so the reading is narrow and gives up
early: comments, string and character literals and preprocessor lines are
blanked first; `namespace` and `extern "C"` blocks are read through; a
`class`/`struct`/`union`/`enum` body is one definition, as a Python class
is; a block whose header holds `(...)` and no top-level `=` is a function;
any other block is skipped whole. Braces that do not balance return None,
and the caller keeps the whole-file hash.
"""
# implements: ARCH-MEMBERDRIFT-027
# implements: REQ-MEMBERDRIFT-1140
import re

from .design_brace import _design_mask

C_EXTS = (".c", ".h", ".cc", ".cpp", ".cxx", ".hh", ".hpp", ".hxx", ".inl")

_TRANSPARENT_RE = re.compile(r"(?:\bnamespace\b[\w\s:]*|\bextern\s*)$")
_TYPE_RE = re.compile(
    r"^(?:template\s*<.*>\s*)?(?:typedef\s+)?(class|struct|union|enum)"
    r"(?:\s+class)?\s+(?:\w+\s+)*?([A-Za-z_]\w*)\s*(?:final\s*)?"
    r"(?::[^{]*)?$", re.S)
_NAME_BEFORE_PAREN_RE = re.compile(
    r"((?:[A-Za-z_]\w*(?:\s*<[^<>()]*>)?\s*::\s*)*~?[A-Za-z_]\w*"
    r"|operator\s*[^\s(]+)\s*\($")
# a constructor's init list still open: `) : a_(x), b_` right before a `{`
_INIT_LIST_RE = re.compile(r"\)\s*(?:noexcept\s*)?:[^;{}]*[\w>]\s*$")
_CONTROL = frozenset(("if", "for", "while", "switch", "catch", "do", "else",
                      "return", "sizeof"))


def _mask_preprocessor(text):
    """Blank `#` lines and their backslash continuations, keeping newlines,
    so a brace inside a macro never moves the depth."""
    out, cont = [], False
    for line in text.split("\n"):
        if cont or line.lstrip().startswith("#"):
            cont = line.rstrip().endswith("\\")
            out.append(" " * len(line))
        else:
            out.append(line)
    return "\n".join(out)


def _top_level_text(header):
    """The header with every `(...)`/`[...]`/`<...>`-free top level kept,
    used only to look for a stray `=` outside the parameter list."""
    depth, out = 0, []
    for ch in header:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def _function_name(header):
    """`(name, params)` when the header reads as a function definition:
    an identifier (qualified, a destructor or an operator) right before the
    first top-level `(`, not a control keyword, and no `=` outside the
    parentheses. None otherwise."""
    if "=" in _top_level_text(header).replace("operator=", ""):
        return None
    depth = 0
    for i, ch in enumerate(header):
        if ch == "(" and depth == 0:
            m = _NAME_BEFORE_PAREN_RE.search(header[:i + 1])
            if not m:
                return None
            name = re.sub(r"\s+", "", m.group(1))
            if name in _CONTROL:
                return None
            close, d = i, 0
            for j in range(i, len(header)):
                d += {"(": 1, ")": -1}.get(header[j], 0)
                if d == 0:
                    close = j
                    break
            params = re.sub(r"\s+", " ", header[i + 1:close]).strip()
            return name, params
        if ch in "(<[":
            depth += 1
        elif ch in ")>]":
            depth = max(0, depth - 1)
    return None


def _lead_line(lines, first):
    """The first line of the unbroken comment block right above `first`
    (1-based), or `first` itself; a blank line ends the block."""
    lead = first
    while lead > 1:
        prev = lines[lead - 2].strip()
        if prev.startswith(("//", "/*", "*", "*/")) or prev.endswith("*/"):
            lead -= 1
        else:
            break
    return lead


def _blocks(masked):
    """Yield `(header_start, open_idx, close_idx, header)` for each block
    opened at the reading level, descending only into transparent ones.
    Raises ValueError when the braces do not balance."""
    stack, start = [], 0          # stack: True for a transparent block
    i, n = 0, len(masked)
    while i < n:
        ch = masked[i]
        if ch in ";}" or ch == "{":
            if ch == "{":
                header = masked[start:i]
                if _INIT_LIST_RE.search(header):
                    i = _match(masked, i) + 1   # `b_{2}`: part of the header
                    continue
                if _TRANSPARENT_RE.search(header.strip()):
                    stack.append(True)
                else:
                    close = _match(masked, i)
                    yield start, i, close, header
                    i = close
            elif ch == "}":
                if not stack:
                    raise ValueError("unbalanced")
                stack.pop()
            start = i + 1
        i += 1
    if stack:
        raise ValueError("unbalanced")


def _match(masked, idx):
    depth = 0
    for j in range(idx, len(masked)):
        if masked[j] == "{":
            depth += 1
        elif masked[j] == "}":
            depth -= 1
            if depth == 0:
                return j
    raise ValueError("unbalanced")


def c_def_spans(path):  # implements: REQ-MEMBERDRIFT-1140
    """`[(lead_line, first_line, last_line, name)]` for the top-level
    definitions of a C or C++ file, or None when it is not one, cannot be
    read, or its braces do not balance. An overloaded name is keyed with its
    parameter list, so two overloads never share a key."""
    if not path.lower().endswith(C_EXTS):
        return None
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return c_def_spans_text(f.read())
    except OSError:
        return None


def mask_c(text):
    """`text` with preprocessor lines, comments and literals blanked, the
    newlines kept, so line numbers still hold."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return _design_mask(_mask_preprocessor(text))


def c_def_spans_text(text):  # implements: REQ-MEMBERDRIFT-1140
    """`c_def_spans` over source text already read."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    masked = mask_c(text)
    lines = text.split("\n")
    found = []
    try:
        for start, _open, close, header in _blocks(masked):
            head = header.strip()
            if not head:
                continue
            t = _TYPE_RE.match(head)
            fn = None if t else _function_name(head)
            if not t and not fn:
                continue
            first_idx = start + (len(header) - len(header.lstrip()))
            first = masked.count("\n", 0, first_idx) + 1
            last = masked.count("\n", 0, close) + 1
            found.append((first, last, t.group(2) if t else fn[0],
                          None if t else fn[1]))
    except ValueError:
        return None
    names = [f[2] for f in found]
    out = []
    for first, last, name, params in found:
        key = name
        if params is not None and names.count(name) > 1:
            key = "{}({})".format(name, params)
        out.append((_lead_line(lines, first), first, last, key))
    return out

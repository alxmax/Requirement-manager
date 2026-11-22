"""JS and TS string, template and regex literals blanked for the tag scan
(REQ-SCAN-992). Imported by `tags._visible_lines` only when a JS or TS file is
read, so a repository with none never loads it."""
# implements: REQ-SCAN-992
import re

from .tags import _strip_py_quote_end

_JS_EVENT_RE = re.compile(r"[\"'`]|//|/\*|/")
_TEMPLATE_END_RE = re.compile(r"[\\`]")
# A `/` opens a regex literal, not a division, after an operator, an opening
# bracket, the start of the line or `return`/`typeof`.
_REGEX_BEFORE_RE = re.compile(r"(?:^|[(,=:\[!&|?{};+\-*%<>~^]|\breturn|\btypeof)\s*$")


def _regex_end(s, i, n):
    """Index of the `/` closing a regex literal from `i`, or `n`: an escaped
    `/` or one inside `[...]` does not close it."""
    in_class = False
    while i < n:
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c == "/" and not in_class:
            return i
        in_class = (in_class or c == "[") and c != "]"
        i += 1
    return n


def _template_end(s, i, n):
    """Index of the backtick closing a template literal from `i`, or `n`."""
    while True:
        m = _TEMPLATE_END_RE.search(s, i)
        if not m or s[m.start()] == "`":
            return m.start() if m else n
        i = m.start() + 2


def strip_js_strings(s, in_comment):
    # implements: REQ-SCAN-992  # implements: REQ-RETIRE-1130
    """(line with string and template contents blanked, still in a block
    comment) for one JS/TS line; comments are kept. A template literal is
    blanked to the end of its line only: carried further, a backtick in a regex
    literal hid every real tag below it."""
    out, i, n = [], 0, len(s)
    if in_comment:
        k = s.find("*/")
        if k == -1:
            return s, True
        out.append(s[:k + 2])
        i = k + 2
    while True:
        m = _JS_EVENT_RE.search(s, i)
        if not m:
            return "".join(out) + s[i:], False
        j, tok = m.start(), m.group()
        out.append(s[i:j])
        if tok == "//":
            return "".join(out) + s[j:], False
        if tok == "/*":
            k = s.find("*/", j + 2)
            if k == -1:
                return "".join(out) + s[j:], True
            out.append(s[j:k + 2])
            i = k + 2
            continue
        if tok == "/":
            if not _REGEX_BEFORE_RE.search(s, 0, j):
                out.append("/")         # a division
                i = j + 1
                continue
            k = _regex_end(s, j + 1, n)
        else:
            k = _template_end(s, j + 1, n) if tok == "`" else _strip_py_quote_end(s, tok, j + 1, n)
        i = min(k + 1, n)
        out.append(" " * (i - j))

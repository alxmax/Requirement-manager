"""What a code draft asks of a C or C++ file: the parsed signals Python gets
from `ast`, read here from the masked text inside each definition.

Imported by `draftquestions` only for a C/C++ file (ADR-0090). The reading
uses `bracedefs`: no span (braces that do not balance) means the file is
reported as not parsed, never as clean.
"""
# implements: ARCH-EXTRACT-008
# implements: REQ-EXTRACT-1142
import re

from .bracedefs import c_def_spans_text, mask_c

_NUM = r"(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)[uUlLfF]*"
# a number compared with something, on either side of the operator
_CMP_RE = re.compile(
    r"(?:[<>]=?|[!=]=)\s*\(?\s*(-?\s*" + _NUM + r")(?![\w.])"
    r"|(?<![\w.])(-?" + _NUM + r")\s*\)?\s*(?:[<>]=?|[!=]=)")
_EXIT_RE = re.compile(r"^\s*(?:return\b[^;]*|break|continue|goto\s+\w+)\s*;\s*$")
# a line that makes the next statement conditional: `if (x)`, `else`, `do`
_GUARD_RE = re.compile(r"(?:\)|\belse|\bdo)\s*$")
_NOT_DEAD_RE = re.compile(
    r"^\s*(?:\}|case\b|default\b|else\b|[A-Za-z_]\w*\s*:(?!:)|$)")
_DISCARD_RE = re.compile(r"\(\s*void\s*\)\s*[A-Za-z_][\w:.\->]*\s*\(")
_PLAIN = frozenset(("0", "1", "2", "-1", "0.0", "1.0"))


def _number(tok):
    """The literal without spaces or a type suffix (a hex digit `f` stays)."""
    t = re.sub(r"\s+", "", tok)
    return t.rstrip("uUlL") if "x" in t.lower() else t.rstrip("uUlLfF")


def c_signals(src):  # implements: REQ-EXTRACT-1142
    """(line, kind) for every unnamed number compared in a definition, an
    explicitly discarded return value, and a statement after an unconditional
    exit in the same block. None when the braces do not balance."""
    spans = c_def_spans_text(src)
    if spans is None:
        return None
    lines = mask_c(src).split("\n")
    out = []
    for _lead, first, last, _name in spans:
        body = range(first, min(last, len(lines)) + 1)
        for n in body:
            text = lines[n - 1]
            for m in _CMP_RE.finditer(text):
                if _number(m.group(1) or m.group(2)) not in _PLAIN:
                    out.append((n, "magic"))
                    break
            if _DISCARD_RE.search(text):
                out.append((n, "discard"))
            prev = next((lines[k - 1] for k in range(n - 1, first - 1, -1)
                         if lines[k - 1].strip()), "")
            if _EXIT_RE.search(text) and not _GUARD_RE.search(prev):
                nxt = next((k for k in range(n + 1, last + 1)
                            if lines[k - 1].strip()), None)
                if nxt and not _NOT_DEAD_RE.match(lines[nxt - 1]):
                    out.append((nxt, "dead"))
    return out

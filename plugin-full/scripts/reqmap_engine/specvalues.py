"""`RM038`: a value a requirement states for a named constant disagrees with
the value its own code defines (ADR-0090).

A clause that names a constant in backticks and gives it a value -
"`MAX_RETRIES` is 3", "`TIMEOUT_MS` = 200", "`LIMIT` (0x40)" - is compared
with that name's definitions in the requirement's `implements:` files:
`#define NAME 3`, `NAME = 3`, `constexpr int NAME{3}`, an enum member. Only an
explicit connector (`is`, `=`, `:`, `equals`, `set to`, a parenthesis) makes a
claim, so "`gate` retries 3 times" is prose. A warning under `gate --full`,
never in the bare gate: the reading is a heuristic and the question is which
side is right.
"""
# implements: ARCH-RULES-059
# implements: REQ-RULES-1143
import os
import re

from . import wikilinks  # noqa: F401 - RM038 registers after RM037
from . import planinput  # noqa: F401
from .model import gate_rule
from .sections import CONTRACT_LABELS, _from_any
from .text import _bullets

_NUM = r"-?(?:0[xX][0-9a-fA-F]+|\d+(?:,\d{3})*(?:\.\d+)?)"
_CLAIM_RE = re.compile(
    r"`([A-Za-z_]\w{2,})`\s*(?:\(\s*|(?:=|:|is|equals|is set to|set to)\s+)"
    r"(" + _NUM + r")(?!\w|[.,]\d)")
_MAX_FILE = 512 * 1024


def _value(tok):
    """The number a literal stands for, or None. Thousands commas and C type
    suffixes are dropped; hex is read as hex."""
    t = tok.replace(",", "").strip()
    t = t.rstrip("uUlL") if "x" in t.lower() else t.rstrip("uUlLfF")
    try:
        return float(int(t, 16)) if "x" in t.lower() else float(t)
    except ValueError:
        return None


def spec_claims(body):  # implements: REQ-RULES-1143
    """[(name, value, literal)] stated in the Description's clauses."""
    out = []
    for clause in _from_any(_bullets, body, CONTRACT_LABELS):
        for m in _CLAIM_RE.finditer(clause):
            v = _value(m.group(2))
            if v is not None:
                out.append((m.group(1), v, m.group(2)))
    return out


def _def_patterns(name):
    n = re.escape(name)
    num = r"(" + _NUM + r")[uUlLfF]*"
    return (re.compile(r"^\s*#\s*define\s+" + n + r"\s+\(?\s*" + num, re.M),
            re.compile(r"(?<![\w.>])" + n + r"\s*(?::[^=\n;]+)?=(?!=)\s*\(?\s*"
                       + num + r"\s*\)?\s*[;,)\n}]"),
            re.compile(r"(?<![\w.>])" + n + r"\s*\{\s*" + num + r"\s*\}"))


def code_values(code_root, files, name):  # implements: REQ-RULES-1143
    """[(value, relfile, line, literal)] for each definition of `name`."""
    pats, out = _def_patterns(name), []
    for fp in sorted(files):
        path = os.path.join(code_root, fp)
        try:
            if os.path.getsize(path) > _MAX_FILE:
                continue
            with open(path, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except OSError:
            continue
        if name not in text:
            continue
        for rx in pats:
            for m in rx.finditer(text):
                v = _value(m.group(1))
                if v is not None:
                    out.append((v, fp, text.count("\n", 0, m.start(1)) + 1,
                                m.group(1)))
    return out


@gate_rule("RM038", "warn")
def _spec_value_rule(ctx):  # implements: REQ-RULES-1143
    for rid in sorted(ctx.reqs):
        r = ctx.reqs[rid]
        if r["meta"].get("status") == "deprecated":
            continue
        claims = spec_claims(r["body"])
        if not claims:
            continue
        files = {fp for role, fp, _ln in ctx.full_members.get(rid, ())
                 if role == "implements"}
        for name, value, lit in claims:
            for cv, fp, ln, clit in code_values(ctx.code_root, files, name):
                if cv != value:
                    yield rid, ("{}: the Description gives `{}` {}, but {}:{} "
                                "defines {} - which one is right?".format(
                                    rid, name, lit, fp, ln, clit))

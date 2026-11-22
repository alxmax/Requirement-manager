"""Tagged C and C++ tests that cannot fail (ADR-0093): `vacuoustests`' three
shapes, in GoogleTest, Catch2, CppUTest and Unity. Bodies come from the ADR-0089
brace reader with comments and literals blanked; compared arguments are read
from the source at the same offsets. Loaded only for a tag outside Python.
"""
# implements: REQ-TESTGAPS-1147
import os
import re

from .bracedefs import C_EXTS, c_def_spans_text, mask_c

# GoogleTest, Catch2 and CppUTest test macros; a Unity test is a `test*` function.
_TEST_MACROS = ("TEST", "TEST_F", "TEST_P", "TYPED_TEST", "TYPED_TEST_P",
                "TEST_CASE", "TEST_CASE_METHOD", "SCENARIO")
_ASSERT_RE = re.compile(
    r"\b(EXPECT_\w+|ASSERT_\w+|TEST_ASSERT\w*|TEST_FAIL\w*|FAIL|ADD_FAILURE\w*"
    r"|REQUIRE\w*|CHECK\w*|\w+_EQUAL\w*|assert)\s*\(")
_CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
_CONST_RE = re.compile(r"^(?:true|false|nullptr|NULL|\d+[uUlL]*)$")
_EQ_RE = re.compile(r"EQ(?:UAL)?(?:_|$)")  # EXPECT_EQ, STREQ, TEST_ASSERT_EQUAL; not REQUIRE
_HELPER_PREFIXES = ("assert", "fail", "check", "expect", "verify")  # as in Python


def _args(masked, text, open_idx):
    """The call's top-level arguments, split on `masked`, read from `text`."""
    depth, start, out = 0, open_idx + 1, []
    for j in range(open_idx, len(masked)):
        depth += {"(": 1, "[": 1, "{": 1, ")": -1, "]": -1, "}": -1}.get(masked[j], 0)
        if depth == 0 or (masked[j] == "," and depth == 1):
            out.append(re.sub(r"\s+", "", text[start:j]))
            start = j + 1
        if depth == 0:
            return [a for a in out if a]
    return []


def _calls(masked):
    return [m.group(1) for m in _CALL_RE.finditer(masked) if not _ASSERT_RE.match(m.group(0))]


def _kind(masked, text, helpers):  # implements: REQ-TESTGAPS-1147
    """The shape of one body's assertions, or None when one of them checks."""
    shapes = set()
    for m in _ASSERT_RE.finditer(masked):
        args = _args(masked, text, m.end() - 1)
        if len(args) == 1 and _CONST_RE.match(args[0]):
            shapes.add("constant assertion")
        elif len(args) >= 2 and _EQ_RE.search(m.group(1)) and args[0] == args[1]:
            shapes.add("compares a value with itself")
        else:
            return None
    if any(c in helpers or c.lower().startswith(_HELPER_PREFIXES) for c in _calls(masked)):
        return None
    return "no assertion" if not shapes else (shapes.pop() if len(shapes) == 1 else None)


def _is_test(key):
    name = key.split("(")[0]
    return name in _TEST_MACROS or name.lower().startswith("test")


def cpp_vacuous(code_root, fp, tags):  # implements: REQ-TESTGAPS-1147
    """[{file, line, test, kind, cases}] for the tagged tests of one C or C++
    file that cannot fail; `tags` is [(line, "ID#CASE-N")]. [] when the file
    is not C or C++, cannot be read, or its braces do not balance."""
    try:
        with open(os.path.join(code_root, fp), encoding="utf-8", errors="ignore") as fh:
            text = fh.read().replace("\r\n", "\n").replace("\r", "\n")
    except OSError:
        return []
    spans = (c_def_spans_text(text) or []) if fp.lower().endswith(C_EXTS) else []
    masked, starts, body = mask_c(text), [0], {}
    for line in text.split("\n"):
        starts.append(starts[-1] + len(line) + 1)
    for span in spans:
        lo = masked.index("{", starts[span[1] - 1])
        body[span] = (masked[lo:starts[span[2]]], text[lo:starts[span[2]]])
    helpers, grew = set(), True
    while grew:  # a helper that asserts makes its callers assert too
        new = {s[3].split("(")[0] for s, (mb, _t) in body.items() if not _is_test(s[3])
               and (_ASSERT_RE.search(mb) or set(_calls(mb)) & helpers)} - helpers
        helpers, grew = helpers | new, bool(new)
    tests = {}
    for line, case in tags:
        for span in spans:
            if span[0] <= line <= span[2] and _is_test(span[3]):
                tests.setdefault(span, set()).add(case)
    out = []
    for span in sorted(tests, key=lambda s: s[1]):
        kind = _kind(*body[span], helpers)
        if kind:
            out.append({"file": fp, "line": span[1], "kind": kind, "cases": sorted(tests[span]),
                        "test": text.split("\n")[span[1] - 1].split("{")[0].strip()})
    return out

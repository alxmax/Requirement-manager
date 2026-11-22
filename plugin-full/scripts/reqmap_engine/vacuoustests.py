"""Tagged tests that cannot fail (ADR-0092).

A `# verifies: ID#CASE-N` tag closes a case however the test is written, so a
test that asserts nothing, asserts only a constant, or compares an expression
with itself proves the case and checks nothing. This reads the Python test
functions the tags sit in and names those; C and C++ tests are read by
`vacuouscpp` (ADR-0093). A function not named `test*` is not judged, nor is
any other language: a script's exit code and a foreign runner's assertions
are not visible here. Advice only, never a verdict.
"""
# implements: REQ-TESTGAPS-1146
import ast
import os

# A call whose name starts with one of these asserts something: unittest's
# `assert*` and `fail`, mock's `assert_called*`, pytest's `raises`, and the
# common hand-rolled `check_*` / `expect_*` / `verify_*` helpers.
_ASSERT_PREFIXES = ("assert", "fail", "raises", "check", "expect", "verify")


def _name(call):
    f = call.func
    return f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")


def _assertions(fn, helpers):
    return [n for n in ast.walk(fn) if isinstance(n, ast.Assert) or (
        isinstance(n, ast.Call) and (_name(n).lower().startswith(_ASSERT_PREFIXES)
                                     or _name(n) in helpers))]


def _constant(node):
    """True when the assertion's outcome is fixed before any code runs."""
    if isinstance(node, ast.Assert):
        return isinstance(node.test, ast.Constant)
    args = node.args
    return (_name(node) in ("assertTrue", "assertFalse") and bool(args)
            and isinstance(args[0], ast.Constant))


def _self_equal(node):
    """`assertEqual(f(x), f(x))`: in one process, true of almost any f."""
    args = getattr(node, "args", [])
    return (_name(node) in ("assertEqual", "assertIs") and len(args) >= 2
            and ast.dump(args[0]) == ast.dump(args[1]))


def _kind(fn, helpers):  # implements: REQ-TESTGAPS-1146
    asserts = _assertions(fn, helpers)
    if not asserts:
        return "no assertion"
    if all(_constant(a) for a in asserts):
        return "constant assertion"
    if all(_self_equal(a) for a in asserts):
        return "compares a value with itself"
    return None


def _helpers(fns):
    """Non-test functions of the file that assert, directly or through each other."""
    found = set()
    while True:
        new = {f.name for f in fns if not f.name.startswith("test")
               and f.name not in found and _assertions(f, found)}
        if not new:
            return found
        found |= new


def _owner(fns, line):
    """The innermost function holding `line`, or the one a tag just above names."""
    inside = [f for f in fns if f.lineno <= line <= f.end_lineno]
    if inside:
        return min(inside, key=lambda f: f.end_lineno - f.lineno)
    below = [f for f in fns if 0 < f.lineno - line <= 3]
    return min(below, key=lambda f: f.lineno) if below else None


def vacuous_tests(code_root, ac_cover):  # implements: REQ-TESTGAPS-1146
    """[{file, line, test, kind, cases}] for each `test*` function a
    `# verifies:` tag points at that cannot fail, by file then line."""
    by_file = {}
    for rid, cases in (ac_cover or {}).items():
        for case, locs in cases.items():
            for fp, line in locs:
                by_file.setdefault(fp, []).append((line, rid + "#" + case))
    out = []
    for fp in sorted(by_file):
        if not fp.endswith(".py"):
            from .vacuouscpp import cpp_vacuous  # C and C++ (ADR-0093)
            out += cpp_vacuous(code_root, fp, by_file[fp])
            continue
        try:
            with open(os.path.join(code_root, fp), encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
        except (OSError, SyntaxError, ValueError):
            continue
        fns = [n for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        tests = {}
        for line, case in by_file[fp]:
            fn = _owner(fns, line)
            if fn is not None and fn.name.startswith("test"):
                tests.setdefault(fn, set()).add(case)
        helpers = _helpers(fns)
        for fn in sorted(tests, key=lambda f: f.lineno):
            kind = _kind(fn, helpers)
            if kind:
                out.append({"file": fp, "line": fn.lineno, "test": fn.name,
                            "kind": kind, "cases": sorted(tests[fn])})
    return out

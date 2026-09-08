"""Regression tests for scripts/check_retired_verbs.py — the stale-instruction gate.

Stdlib unittest, run from the repo root:
    python -X utf8 scripts/test_check_retired_verbs.py

Every case here is a defect the guard shipped with and that the 2026-09-08 Senate
(`senate-reqmap-cli-surface-18-to-5`) found by measurement, not by review: the
guard matched verbs but not flags, required a delimiter it did not always get,
read the flags of whatever command happened to follow on the same line, and knew
only English for "this verb is gone".
"""
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_retired_verbs as C

LIVE = {"gate", "sync", "init", "new", "clarify"}
FLAGS = {"--code", "--root", "--risk", "--i18n", "--attach", "--strict"}


def scan(line, live=None, flags=None):
    """The guard's verdict on one line, as a sorted list of (kind, name)."""
    return sorted(C.scan_line(line, live or LIVE, FLAGS if flags is None else flags))


class LiveSurface(unittest.TestCase):
    """`live_flags` reads the parser, which is what actually accepts a flag."""

    def test_reads_the_parser_including_a_digit_and_a_global(self):
        flags = C.live_flags()
        # --i18n is the one flag whose name carries digits; a name-shaped class
        # that forgets them silently reports a live flag as retired.
        self.assertIn("--i18n", flags)
        # COMMANDS omits the shared workspace flags on purpose, so a check built
        # on the registry alone would accuse four flags that work.
        for shared in ("--code", "--root", "--reqs", "--cache"):
            self.assertIn(shared, flags)

    def test_unreadable_engine_fails_open(self):
        """No engine to read means no flag verdict — never a blanket accusation."""
        self.assertEqual(C.live_flags(root=os.devnull), set())
        self.assertEqual(scan("`reqmap.py gate --nope`", flags=set()), [])


class RetiredVerbs(unittest.TestCase):
    def test_bare_undelimited_invocation_is_caught(self):
        """The line that slipped through: .githooks/pre-commit wrote its own repair
        hint as `(fix: reqmap.py map ...)`, with no backtick, quote or `python `
        in front of it, inside a file the guard already scanned."""
        line = "#   3. map staleness (fix: reqmap.py map --root plugin --code .)"
        self.assertEqual(scan(line), [("verb", "map")])

    def test_a_live_verb_is_not_a_finding(self):
        self.assertEqual(scan("run `python scripts/reqmap.py gate --code ..`"), [])

    def test_a_word_that_is_not_a_retired_verb_is_ignored(self):
        """Matching any word after `reqmap` would make every mention a finding."""
        self.assertEqual(scan("reqmap.py links code to requirements"), [])


class RetiredFlags(unittest.TestCase):
    def test_a_flag_the_parser_does_not_accept_is_caught(self):
        """The half that did not exist: `gate --show` reads as the LIVE verb `gate`,
        so a cull of mode flags passed the verb-only guard green."""
        self.assertEqual(scan("`python scripts/reqmap.py gate --show ARCH-X-001`"),
                         [("flag", "--show")])

    def test_flags_of_a_second_command_on_the_line_are_not_attributed(self):
        """`npm test --workspace=apps/web` after a reqmap call is not reqmap's flag."""
        line = "- `python scripts/reqmap.py gate` trebuie sa treaca. `npm test --workspace=x` la fel."
        self.assertEqual(scan(line), [])

    def test_flags_after_a_shell_separator_are_not_attributed(self):
        line = "`reqmap.py gate --code .. && ruff check --select E9,F reqmap.py`"
        self.assertEqual(scan(line), [])


class RemovalNotes(unittest.TestCase):
    """A line saying a name is GONE is the opposite of an instruction to type it."""

    def test_english(self):
        self.assertEqual(scan("`reqmap.py map` no longer exists — use `sync`"), [])

    def test_romanian(self):
        """The only consumer repo writes its docs in Romanian, so its removal note
        read as the very instruction it retracts."""
        self.assertEqual(scan("comanda `reqmap.py map` nu mai exista, e in `sync`"), [])


class ThisRepo(unittest.TestCase):
    def test_no_instruction_in_this_repo_names_a_retired_name(self):
        buf = io.StringIO()
        argv, sys.stdout = sys.argv, buf
        try:
            rc = C.main([])
        finally:
            sys.stdout, sys.argv = sys.__stdout__, argv
        self.assertEqual(rc, 0, buf.getvalue())

    def test_a_missing_extra_root_is_an_error_not_a_pass(self):
        buf = io.StringIO()
        stderr, sys.stderr = sys.stderr, buf
        try:
            self.assertEqual(C.main([os.path.join(os.sep, "no", "such", "root")]), 2)
        finally:
            sys.stderr = stderr


if __name__ == "__main__":
    unittest.main()

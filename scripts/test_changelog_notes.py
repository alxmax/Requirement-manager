#!/usr/bin/env python3
"""Tests for changelog_notes.extract — the release-notes slice fed to `gh release`."""
import unittest

from changelog_notes import extract

SAMPLE = """# Changelog

## plugin `v2.13.0` — 2026-07-05

**Ranked requirement search.** Body line one.
Second body line.

`MAP_ENGINE_VERSION` → `2026-07-05`.

## plugin `v2.12.0` — 2026-07-04

**Older entry.** Should not appear when v2.13.0 is requested.
"""


class ExtractNotes(unittest.TestCase):
    def test_returns_only_the_requested_section(self):
        out = extract(SAMPLE, "2.13.0")
        self.assertTrue(out.startswith("## plugin `v2.13.0`"))
        self.assertIn("Ranked requirement search", out)
        self.assertIn("MAP_ENGINE_VERSION", out)
        # must stop before the previous version's section
        self.assertNotIn("Older entry", out)
        self.assertNotIn("v2.12.0", out)

    def test_trailing_and_leading_whitespace_stripped(self):
        out = extract(SAMPLE, "2.13.0")
        self.assertEqual(out, out.strip())

    def test_unknown_version_returns_none(self):
        self.assertIsNone(extract(SAMPLE, "9.9.9"))

    def test_exact_version_match_not_prefix(self):
        # a query for 2.1 must not match the 2.13.0 heading via loose substring
        self.assertIsNone(extract(SAMPLE, "2.1"))


if __name__ == "__main__":
    unittest.main()

"""Tests for scripts/check_directory_edition.py.

Stdlib unittest, run from the repo root:
    python -X utf8 scripts/test_check_directory_edition.py
"""
# tested-by: REQ-SELFGATE-1130 @unit  # tested-by: ARCH-SELFGATE-039 @unit
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_directory_edition as C

PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"


def _edition(files):
    """A temporary edition holding {rel: bytes}, plus a valid manifest."""
    d = tempfile.mkdtemp()
    tree = {".claude-plugin/plugin.json": b'{"name": "x"}\n'}
    tree.update(files)
    for rel, data in tree.items():
        path = Path(d) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return d


def _run(root):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = C.main([root])
    return rc, buf.getvalue()


class DirectoryEdition(unittest.TestCase):
    def test_a_script_fails_as_a_disallowed_type(self):  # verifies: REQ-SELFGATE-1130#CASE-1
        rc, out = _run(_edition({"scripts/reqmap.py": b"print('x')\n"}))
        self.assertEqual(1, rc)
        self.assertIn("scripts/reqmap.py: disallowed file type", out)

    def test_a_shebang_fails_whatever_the_name(self):  # verifies: REQ-SELFGATE-1130#CASE-2
        rc, out = _run(_edition({"hooks/pre-commit.md": b"#!/bin/sh\necho hi\n"}))
        self.assertEqual(1, rc)
        self.assertIn("hooks/pre-commit.md: starts with #!", out)
        self.assertIn("hooks/pre-commit.md: inside a hooks/ folder", out)

    def test_runnable_configuration_fails(self):  # verifies: REQ-SELFGATE-1130#CASE-3
        names = (".mcp.json", "hooks.json", ".lsp.json", "monitors.json")
        rc, out = _run(_edition({n: b"{}\n" for n in names}))
        self.assertEqual(1, rc)
        for name in names:
            self.assertIn(name + ": runnable configuration", out)

    def test_only_manifest_and_images_in_claude_plugin(self):  # verifies: REQ-SELFGATE-1130#CASE-4
        root = _edition({".claude-plugin/icon.png": PNG,
                         ".claude-plugin/notes.md": b"notes\n"})
        found = C.check(root)
        self.assertEqual([(".claude-plugin/notes.md",
                           "not plugin.json or an image in .claude-plugin/")], found)

    def test_this_repository_edition_passes(self):  # verifies: REQ-SELFGATE-1130#CASE-5
        ci = (Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yml")
        text = ci.read_text(encoding="utf-8")
        gate_job = text.split("\n  gate-and-tests:\n", 1)[1].split("\n  tests:\n", 1)[0]
        self.assertIn("run: python -X utf8 scripts/check_directory_edition.py\n", gate_job)
        if not C.DEFAULT_ROOT.is_dir():
            self.skipTest("no plugin/ beside this script")
        rc, out = _run(str(C.DEFAULT_ROOT))
        self.assertEqual(0, rc, out)

    def test_package_manager_configuration_fails(self):  # verifies: REQ-SELFGATE-1130#CASE-6
        rc, out = _run(_edition({"package.json": b"{}\n", "pnpm-workspace.yaml": b"x: 1\n"}))
        self.assertEqual(1, rc)
        self.assertIn("package.json: package manager configuration", out)
        self.assertIn("pnpm-workspace.yaml: package manager configuration", out)

    def test_misplaced_folders_fail(self):  # verifies: REQ-SELFGATE-1130#CASE-6
        found = C.check(_edition({
            "output-styles/terse.md": b"terse\n",
            "egress/hosts.json": b"[]\n",
            ".claude/skills/x/SKILL.md": b"skill\n",
            "skills/x/.claude-plugin/plugin.json": b"{}\n",
        }))
        self.assertIn(("output-styles/terse.md", "inside an output-styles/ folder"), found)
        self.assertIn(("egress/hosts.json", "JSON or YAML inside egress/"), found)
        self.assertIn((".claude/skills/x/SKILL.md", "inside a .claude/skills folder"), found)
        self.assertIn(("skills/x/.claude-plugin/plugin.json",
                       "inside a nested .claude-plugin/ folder"), found)

    def test_a_disguised_image_fails(self):  # verifies: REQ-SELFGATE-1130#CASE-7
        found = C.check(_edition({".claude-plugin/icon.png": b"\xff\xd8\xff\xe0JFIF"}))
        self.assertEqual([(".claude-plugin/icon.png",
                           "content does not match its image extension")], found)

    def test_each_image_signature_is_accepted(self):  # verifies: REQ-SELFGATE-1130#CASE-7
        found = C.check(_edition({
            "a.png": PNG, "b.jpg": b"\xff\xd8\xff\xe0", "c.gif": b"GIF89a",
            "d.webp": b"RIFF\x00\x00\x00\x00WEBPVP8 ", "e.ico": b"\x00\x00\x01\x00",
        }))
        self.assertEqual([], found)

    def test_an_unsafe_path_character_fails(self):  # verifies: REQ-SELFGATE-1130#CASE-7
        found = C.check(_edition({"notes:draft.md": b"x\n"}))
        self.assertEqual(1, len(found))
        self.assertEqual("notes:draft.md", found[0][0])
        self.assertIn("path holds a character", found[0][1])

    def test_an_oversized_text_file_fails(self):  # verifies: REQ-SELFGATE-1130#CASE-7
        found = C.check(_edition({"references/big.md": b"a" * (100 * 1024 + 1),
                                  "references/ok.md": b"a" * (100 * 1024)}))
        self.assertEqual([("references/big.md", "text file over 100 KB")], found)

    def test_nul_and_non_utf8_text_fail(self):  # verifies: REQ-SELFGATE-1130#CASE-2
        found = C.check(_edition({"a.md": b"x\x00y", "b.txt": b"\xff\xfe"}))
        self.assertIn(("a.md", "holds a NUL byte"), found)
        self.assertIn(("b.txt", "not UTF-8"), found)

    def test_a_missing_root_exits_2(self):
        rc, _out = _run(os.path.join(tempfile.mkdtemp(), "absent"))
        self.assertEqual(2, rc)


if __name__ == "__main__":
    unittest.main()

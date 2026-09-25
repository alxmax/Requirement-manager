#!/usr/bin/env python3
import os
import tempfile
import unittest

from reqmap_engine.hook import BEGIN, END, HOOK_BLOCK, _replace_block, cmd_hook


class HookInstallTests(unittest.TestCase):
    def test_replace_preserves_foreign_hook(self):
        existing = "#!/usr/bin/env bash\necho foreign\n"
        out = _replace_block(existing, HOOK_BLOCK)
        self.assertIn("echo foreign", out)
        self.assertIn(BEGIN, out)
        self.assertIn(END, out)
        self.assertEqual(_replace_block(out, HOOK_BLOCK).count(BEGIN), 1)

    def test_install_writes_block_and_workflow(self):
        tmp = tempfile.mkdtemp()
        rc = cmd_hook(tmp)
        self.assertEqual(rc, 0)
        pre = os.path.join(tmp, ".githooks", "pre-push")
        wf = os.path.join(tmp, ".github", "workflows", "reqmap.yml")
        self.assertTrue(os.path.isfile(pre))
        self.assertTrue(os.path.isfile(wf))
        with open(pre, encoding="utf-8") as f:
            self.assertIn("gate --if-affected", f.read())
        with open(wf, encoding="utf-8") as f:
            yml = f.read()
        self.assertIn("workflow_dispatch", yml)
        self.assertNotIn("push, pull_request", yml)


if __name__ == "__main__":
    unittest.main()

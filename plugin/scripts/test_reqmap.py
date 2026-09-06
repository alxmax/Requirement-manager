"""The reqmap regression suite — the aggregator.

ADR-0014 keeps the ENGINE in one file. It says nothing about the tests, and at 12,000
lines this suite had stopped being something a person could navigate: finding the class
that covered a behaviour meant grepping, and adding one meant appending to the bottom
whatever the subject. The classes now live in four modules by subject and are re-exported
here, so every documented way of running them keeps working unchanged:

    python scripts/test_reqmap.py
    python -m unittest test_reqmap
    python -m unittest test_reqmap.Gate.test_name -v

The parts are `test_reqmap_scan` (reading the tree), `test_reqmap_gate` (the verdict),
`test_reqmap_author` (writing requirements) and `test_reqmap_report` (what it prints),
over the fixtures in `test_reqmap_common`. Each also runs on its own.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_reqmap_common import *      # noqa: F401,F403
from test_reqmap_scan import *        # noqa: F401,F403
from test_reqmap_gate import *        # noqa: F401,F403
from test_reqmap_author import *      # noqa: F401,F403
from test_reqmap_report import *      # noqa: F401,F403



if __name__ == "__main__":
    unittest.main(verbosity=2)

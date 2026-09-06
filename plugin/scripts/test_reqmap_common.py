"""Fixtures every part of the reqmap suite shares.

Tag strings are assembled at runtime so THIS file never registers a phantom member in the
repo's own gate — the scanner reads .py sources line by line and a literal
`# implements: X` here would be a real tag."""
import ast
import errno
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reqmap as R


def _write(path, text, encoding="utf-8"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding=encoding) as f:
        f.write(text)


# Build tag strings at runtime so THIS test file does not register phantom
# members in the repo's own `reqmap check` (the scanner reads .py line by line).
_ROLE = "impl" + "ements"


def tag(cap):
    return "# {}: {}".format(_ROLE, cap)


def gtag_html(cap):  # runtime-built so THIS .py source registers no phantom member
    return "<!-- {}-from: {} -->".format("generated", cap)


_TB_ROLE = "tested" + "-by"
_VERIFY_ROLE = "veri" + "fies"   # split so THIS file registers no real coverage
def tb_tag(cap):
    return "# {}: {}".format(_TB_ROLE, cap)


def v_tag(cap, ac):
    return "# {}: {}#{}".format(_VERIFY_ROLE, cap, ac)


REQ = "---\nid: {id}\nstatus: {status}\nlayer: {layer}\n{extra}---\n\n# {title}\n"


def _req_with_verify(rid, items, title="Cap"):
    """A new-schema requirement whose Verify-intent section holds `items`."""
    vi = "\n".join("- " + it for it in items)
    return (
        "---\nid: {id}\nstatus: baseline\nlayer: feature\n---\n\n# {t}\n\n"
        "## WHAT — Contract (normative)\n- shall do the thing.\n\n"
        "## WHAT — Verify intent (open questions for the human)\n{vi}\n\n"
        "## HOW — Acceptance (= tests)\nAC-1\n"
    ).format(id=rid, t=title, vi=vi)


def _ac_body(contract="- It shall do the thing.", acceptance="AC-1\n  Given x\n  When y\n  Then z"):
    return ("# T\n\n## WHAT — Contract (normative)\n{}\n\n"
            "## HOW — Acceptance (= tests)\n{}\n".format(contract, acceptance))


# ---------------------------------------------------------------------------
# clarify / implement / retire — the author -> code -> retirement half of the CLI
# ---------------------------------------------------------------------------
_SPEC_TMPL = ("---\nid: {id}\nstatus: {status}\nlevel: code\nlayer: feature\n"
              "{extra}---\n\n# {title}\n\n"
              "## Description\nEvery bullet below is binding.\n{clauses}\n\n"
              "## Cases\n{cases}\n")


def _spec(rid, clauses, cases=("CASE-1 — c\n  Given x\n  When y\n  Then z",),
          status="confirmed", extra="", title="T"):
    """A minimal well-formed requirement: Description clauses + labelled cases."""
    return _SPEC_TMPL.format(
        id=rid, status=status, extra=extra, title=title,
        clauses="\n".join("- " + c for c in clauses),
        cases="\n\n".join(cases))

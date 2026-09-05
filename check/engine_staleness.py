#!/usr/bin/env python3
# implements: ARCH-STALEENGINE-043
"""Report a vendored reqmap.py that is older than the engine this action ships.

Why it lives HERE and not in reqmap.py: the engine already has this check
(`warn_if_stale`), but it is gated on CLAUDE_PLUGIN_ROOT — set inside a Claude Code
session, unset in CI. Moving it into the engine's CI path would not help either, because
a stale vendored engine does not CONTAIN the check that would report it stale. The
detector has to run from something the consumer does not vendor: this action, which is
always current for whatever `check@vN` they reference.

Standalone on purpose — it does not import the reference engine. It must still answer
when that file is missing or unreadable, which is exactly when an import would fail, so
the two-line version parse is duplicated here rather than borrowed.

Usage (see check/action.yml):
    python engine_staleness.py --vendored scripts/reqmap.py [--reference PATH] \
                               [--mode warn|error|off]
"""
import argparse
import os
import re
import sys

# The version's shape (ISO date + optional same-day `.N` suffix) is defined by
# MAP_ENGINE_VERSION in plugin/scripts/reqmap.py and asserted by scripts/check_versions.py.
_VERSION_RE = re.compile(r'(?m)^MAP_ENGINE_VERSION\s*=\s*"([^"]+)"')

# The engine this action ships, relative to this file: check/ -> plugin/scripts/reqmap.py.
DEFAULT_REFERENCE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugin", "scripts", "reqmap.py")


def version_at(path):
    """MAP_ENGINE_VERSION read from a reqmap.py at `path`; None on any failure.

    Line-anchored so a docstring that merely MENTIONS the constant cannot match before
    the real assignment does.
    """
    try:
        with open(path, encoding="utf-8") as f:
            m = _VERSION_RE.search(f.read())
        return m.group(1) if m else None
    except Exception:
        return None


def reference_version():
    """Version of the engine shipped alongside this action (None if unreadable)."""
    return version_at(DEFAULT_REFERENCE)


def _key(v):
    """Sortable key for `YYYY-MM-DD[.N]`. The suffix compares as an int so `.10` sorts
    after `.9`, which a plain string compare gets backwards."""
    date, _, n = (v or "").partition(".")
    return (date, int(n) if n.isdigit() else 0)


def main(argv=None):  # implements: REQ-STALEENGINE-925  # implements: REQ-STALEENGINE-926
    """Compare the vendored engine against this action's and annotate the run when
    it is behind. Returns the exit code, which is 0 unless `--stale-engine error`
    was asked for."""
    ap = argparse.ArgumentParser(description="Warn when a vendored reqmap.py is behind this action's engine.")
    ap.add_argument("--vendored", required=True, help="path to the consumer's vendored reqmap.py")
    ap.add_argument("--reference", default=DEFAULT_REFERENCE,
                    help="path to the engine to compare against (default: the one this action ships)")
    ap.add_argument("--mode", choices=("warn", "error", "off"), default="warn",
                    help="warn (default): report and exit 0; error: exit 1; off: say nothing")
    a = ap.parse_args(argv)

    if a.mode == "off":
        return 0
    try:
        return _probe(a.vendored, a.reference, a.mode)
    except Exception as exc:   # never let the probe itself be why a gate run goes red
        print("NOTE  engine staleness probe skipped: {}".format(exc))
        return 0


def _probe(vendored_path, reference_path, mode):  # implements: REQ-STALEENGINE-925  # implements: REQ-STALEENGINE-926
    vendored, reference = version_at(vendored_path), version_at(reference_path)
    if not vendored or not reference:
        # Fail open in every mode: an unreadable version is not evidence of staleness,
        # and this probe must never be the reason a gate run goes red on its own.
        unreadable = vendored_path if not vendored else reference_path
        print("NOTE  engine staleness probe skipped: no readable MAP_ENGINE_VERSION in "
              "{}".format(unreadable))
        return 0

    if _key(vendored) >= _key(reference):
        print("reqmap engine up to date (vendored {} >= action {})".format(vendored, reference))
        return 0

    message = ("vendored reqmap.py is stale ({} < action {}) - re-seed it from the "
               "requirement-manager plugin, or pin an older check@vN, so the gate runs the "
               "checks this action expects".format(vendored, reference))
    if os.environ.get("GITHUB_ACTIONS"):
        # A workflow annotation surfaces on the run itself; a log line scrolls past.
        print("::warning title=Stale reqmap engine::{}".format(message))
    else:
        print("WARN  {}".format(message))
    return 1 if mode == "error" else 0


if __name__ == "__main__":
    sys.exit(main())

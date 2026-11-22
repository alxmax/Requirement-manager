"""What a passing `sync` rebuilds beside the map: the findings digest, the
site page, and the corpus advisories the gate never prints. Split from
`reqmap.py`, whose job is the command line."""
import os

from .audittail import _audit_summary
from .findings import cmd_findings
from .similar import _redundant_groups
from .site import _site_default_target, cmd_site


def after_passing_sync(a, ws):
    """What a passing `sync` rebuilds beside the map: the findings digest, the
    site page, and the advisories the gate never prints."""
    reqs, members = ws.reqs, ws.members
    code_root, reqs_dir = ws.code_root, ws.reqs_dir
    # Everything derived is rebuilt in one place: there is no state of the
    # world in which regenerating the map but not the findings digest, the
    # presentation page or (in this repository) the generated integration
    # artifacts is what the caller wanted. Each step below is a no-op when
    # its target does not exist. `map` already refreshes an existing digest;
    # this is the create path, kept opt-in so a consumer repo never gains a
    # file it did not ask for.
    if a.findings and not os.path.exists(
            os.path.join(reqs_dir, "_findings.md")):
        cmd_findings(reqs, reqs_dir, raw=False)
    # implements: ARCH-SITE-026 — an explicit --attach page is scaffolded
    # when absent; the default docs/architecture.html only if it exists
    # and already carries an engine region.
    page = a.attach or _site_default_target(code_root)
    if page and (a.attach or os.path.isfile(page)):
        cmd_site(ws, code_root, attach=page, regions=["nav", "stats"],
                 refresh_only=not a.attach)
    # Deliberately here and not in cmd_check: `gate` runs on every commit
    # via the hook, and a corpus-shape advisory there is noise on work that
    # is already correct. `sync` is the moment the corpus was just
    # rewritten, which is when
    # a newly-minted duplicate appears.  # implements: REQ-REDUNDANCY-058
    _dups = _redundant_groups(reqs)
    if _dups:
        print("info  {} group(s) of requirements share an identical "
              "contract ({} could be folded away) — run `reqmap.py "
              "gate --risk` to see them"
              .format(len(_dups), sum(len(g) - 1 for g in _dups)))
    # Everything the engine can discover, named in one place at the moment
    # the corpus was just rewritten. `sync` regenerates what is derived;
    # until now it said nothing about what is WRONG beyond the gate, so a
    # repo could sync for months without ever meeting `dupes`, `design`, the
    # exemption list or the
    # fact that its corpus is flat.  # implements: REQ-AUDIT-973
    _audit_summary(reqs, members, reqs_dir, code_root)

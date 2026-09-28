"""`RM037`: plan input the engine drops, repairs, or cannot use (ADR-0057).
Input only; the plan's content stays a report. The checks live in
`planschema`, loaded only for a repository with a planning file."""
from . import wikilinks  # noqa: F401 — RM037 registers after RM036
from .model import gate_rule
from .targets import has_plan


@gate_rule("RM037", "warn", strict=True)
def _plan_input_rule(ctx):  # implements: REQ-PLANINPUT-1086
    if not has_plan(ctx.reqs_dir):
        return
    from .planschema import plan_input_findings
    try:
        found = plan_input_findings(ctx.reqs_dir, ctx.reqs)
    except Exception:  # fail-open: a plan never breaks the verdict
        return
    for msg in found:
        yield None, msg

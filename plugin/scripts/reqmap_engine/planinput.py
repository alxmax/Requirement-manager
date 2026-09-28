"""`RM037`: plan input the engine drops, repairs, or cannot use.

The rule checks the plan's input and nothing about its content: whether a
milestone has shipped, or a bar is overdue, stays a report (`gate --audit`,
`sync`), as ADR-0040 decided and ADR-0057 carves the exception from. Warn
in the bare gate, error under `--strict`, like the `INPUT:config` findings
of ADR-0054.

Only this rule is loaded with the gate. The checks live in `planschema`,
imported when the repository has a planning file, so a repository with no
plan pays nothing for them.
"""
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

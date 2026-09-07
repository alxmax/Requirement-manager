"""`clarify --levels`: propose and write a V-model rung."""

from . import config as cfg
from .acceptance import _labeled_acs
from .parse import split_requirement_blocks


# ---------------------------------------------------------------------------
# Level retrofit — implements: ARCH-LEVELRETROFIT-066
#
# ADR-0030 gives a corpus the three rungs at `init`, and only for a requirement
# `init` EXTRACTED from an untagged source file: the architecture and system rungs
# are minted from those drafts, so a repo whose files already carry tags proposes
# zero drafts and gets zero pyramid. Its requirements were authored before the axis
# existed, and no shipped command could give the axis to them.
#
# This is the explicit, human-invoked half. It reads the corpus, proposes one rung
# per requirement that declares none, prints the reason for each, and writes nothing
# without `--apply`. Every write carries `level_source: auto` (ADR-0030's marker), and
# the footprint is those two lines: delete `level:` and `level_source:` and the corpus
# reads as it did. ADR-0030's reversibility is cleaner than this one, because there the
# whole FILE was engine-written; here a field is added to a file a human wrote, which is
# exactly why the write is opt-in and marked. It is deliberately NOT reachable from
# `sync`, which the pre-commit hook runs on every commit.
# ---------------------------------------------------------------------------

def _propose_levels(reqs, members=None, ac_cover=None):
    # implements: ARCH-LEVELRETROFIT-066  # implements: REQ-LEVELRETROFIT-985
    """{rid: (level, reason)} for every requirement that declares no `level:`.

    Four rules, first match wins, each carrying the sentence it will print. A
    requirement that already declares a level is absent from the result: the retrofit
    proposes onto silence and never overrules an author.

    `code` is the one rung that needs evidence rather than a default, because it is
    the rung an author reaches by DECOMPOSING a capability, not by renaming one. It
    is proposed only where the requirement already behaves like one: it has
    implementing code, at least LINT_AC_MIN labelled cases, and at least one of those
    cases linked to a test by a `# verifies:` tag. Absent that evidence the proposal
    is `architecture`, which is the honest reading of a flat corpus."""
    members = members or {}
    ac_cover = ac_cover or {}
    out = {}
    for rid in sorted(reqs):
        r = reqs[rid]
        meta = r["meta"]
        if meta.get("level"):
            continue                       # an author's declaration is never overruled
        layer = meta.get("layer", "feature")
        if layer == "need":
            out[rid] = ("system", "layer: need already says stakeholder need")
            continue
        if layer == "aggregate":
            out[rid] = ("architecture",
                        "layer: aggregate has no code of its own, covered by depends_on")
            continue
        impls = sum(1 for (role, _fp, _ln) in members.get(rid, ()) if role == "implements")
        labels = _labeled_acs(r["body"])
        covered = [ac for ac in labels if ac in (ac_cover.get(rid) or {})]
        if impls and len(labels) >= cfg.LINT_AC_MIN and covered:
            out[rid] = ("code",
                        "{} case(s), {} linked to a test, {} implementing member(s)".format(
                            len(labels), len(covered), impls))
            continue
        out[rid] = ("architecture",
                    "no decomposed-behaviour evidence "
                    "({} case(s), {} verified, {} member(s))".format(
                        len(labels), len(covered), impls))
    return out


def _insert_frontmatter_level(text, level):
    # implements: ARCH-LEVELRETROFIT-066  # implements: REQ-LEVELRETROFIT-986
    """Add `level:` and `level_source: auto` to one block's frontmatter, right after
    `status:` so the field lands where the template puts it. Returns (text, n), with
    n=0 when there is no frontmatter to edit or a `level:` is already present, so the
    caller reports a miss instead of writing a corrupt file."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text, 0
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return text, 0
    fm = lines[1:end]
    if any(ln.startswith("level:") for ln in fm):
        return text, 0
    at = next((i for i, ln in enumerate(fm) if ln.startswith("status:")), -1)
    fm[at + 1:at + 1] = ["level: " + level, "level_source: auto"]
    return "\n".join(lines[:1] + fm + lines[end:]), 1


def _apply_level(r, level):
    # implements: ARCH-LEVELRETROFIT-066  # implements: REQ-LEVELRETROFIT-986
    """Write one requirement's proposed rung into its file, preserving the file's own
    line endings and every sibling block in a module file. Returns (ok, message).

    The mechanics mirror `_apply_status` deliberately: these are the same two hazards
    — a module file holds several requirements, and a repo's files may be CRLF — and
    the two paths must not drift apart on either."""
    with open(r["path"], encoding="utf-8-sig", newline="") as f:
        raw = f.read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n") if eol == "\r\n" else raw
    blocks = split_requirement_blocks(text)
    if len(blocks) > 1:
        idx = r.get("block", 0)
        blocks[idx], n = _insert_frontmatter_level(blocks[idx], level)
        new_text = "".join(blocks)
    else:
        new_text, n = _insert_frontmatter_level(text, level)
    if n == 0:
        return False, "no editable frontmatter for {} in {}".format(
            r["meta"].get("id", "?"), r["path"])
    if eol == "\r\n":
        new_text = new_text.replace("\n", "\r\n")
    with open(r["path"], "w", encoding="utf-8", newline="") as f:
        f.write(new_text)
    return True, "{}: level: {}".format(r["meta"].get("id", "?"), level)


def cmd_levels(ws, apply_it=False, only=None):
    # implements: ARCH-LEVELRETROFIT-066  # implements: REQ-LEVELRETROFIT-987
    """Propose the V-model rung for every requirement that declares none.

    Read-only unless `--apply`, always exit 0, and never a gate rule. It reports the
    two things a reader has to know before adopting: what each proposal rests on, and
    that `satisfies:` edges are NOT written, because the pyramid's edges are a
    modelling decision and `depends_on` is a different axis."""
    reqs = ws.reqs
    if only and only not in reqs:
        print("no requirement with id {}".format(only))
        return 1
    scope = {only: reqs[only]} if only else reqs
    proposals = _propose_levels(scope, ws.members, ws.ac_cover)
    already = sum(1 for r in scope.values() if r["meta"].get("level"))
    if not proposals:
        print("{} of {} requirement(s) already declare a `level:` — nothing to propose.".format(
            already, len(scope)))
        return 0
    by_level = {}
    for rid, (lv, _why) in proposals.items():
        by_level.setdefault(lv, []).append(rid)
    print("Proposed rungs for {} requirement(s) that declare none "
          "({} already declare one):\n".format(len(proposals), already))
    for lv in ("system", "architecture", "code"):
        for rid in by_level.get(lv, []):
            print("  {:<14} {:<26} {}".format(lv, rid, proposals[rid][1]))
    if not by_level.get("code"):
        print("\n  No requirement is proposed at `code`. That rung is one behaviour group with")
        print("  {}-{} labelled cases each linked to a test, and an author reaches it by".format(
            cfg.LINT_AC_MIN, cfg.LINT_AC_MAX))
        print("  DECOMPOSING a capability (`reqmap.py clarify <ID> --decompose`), not by renaming")
        print("  one. A two-rung corpus is a real end state, not a half-finished one.")
    print("\n  `satisfies:` edges are NOT proposed. They are the level axis and `depends_on` is")
    print("  the composition axis; deriving one from the other is the conflation the engine")
    print("  refuses to make. Add them by hand, or leave the rungs unlinked — nothing fails")
    print("  because a pyramid has no edges.")
    if not apply_it:
        print("\n  Nothing written. Re-run with --apply. The whole footprint is two lines")
        print("  per requirement, `level:` and `level_source: auto`; delete both and the")
        print("  corpus reads exactly as it does now. The file is one a human wrote, not")
        print("  one the engine created, which is why the write is opt-in and the marker")
        print("  says who put the rung there.")
        return 0
    ok = 0
    for rid in sorted(proposals):
        good, msg = _apply_level(reqs[rid], proposals[rid][0])
        print("  " + ("wrote  " if good else "SKIP   ") + msg)
        ok += 1 if good else 0
    print("\n{} requirement(s) updated. Run `reqmap.py sync` to rebuild the map, "
          "and review".format(ok))
    print("  every proposal — the engine guessed a rung from shape, which is not the same as")
    print("  knowing what the requirement is for.")
    return 0

"""Drafting requirements from untagged code (`init`'s draft step, `plan`)."""
import os, re

from .candidates import _file_facts
from .parse import parse_frontmatter
from .scan import _walk_files
from .tags import PROSE_EXTS, _is_code_file, classify_prose


def _draft_id(rel):  # implements: ARCH-EXTRACT-008  # implements: REQ-EXTRACT-850
    """Mint a draft capability id from a file's relative path. Path-aware so
    same-basename files in different dirs don't collide; falls back to FILE when
    the name has no usable A-Z0-9 token (e.g. `_.py`, non-ASCII stems)."""
    slug = re.sub(r"[^A-Z0-9]+", "-", os.path.splitext(rel)[0].upper()).strip("-")
    return "DRAFT-" + (slug or "FILE")


def _prose_facts(src):  # implements: ARCH-PROSE-024  # implements: REQ-PROSE-901
    """(title, [headings]) from markdown/HTML prose, for a draft scaffold.
    Title: markdown frontmatter `title:`, else first `# ` H1, else <title>/<h1>.
    Headings: markdown `## ` H2 lines, else <h2>. Returns (None, []) when absent.
    The scaffold lists headings as an authoring hint — never the contract."""
    meta, body = parse_frontmatter(src)
    title = meta.get("title") or None
    headings, h1_sections = [], []
    for line in body.splitlines():
        s = line.strip()
        if title is None:
            m = re.match(r"#\s+(.+)", s)                      # markdown H1
            if m:
                title = m.group(1).strip()
                continue
            m = re.search(
                r"<(?:title|h1)[^>]*>(.*?)</(?:title|h1)>", s, re.I)
            if m:
                title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                # no continue: a line may carry both <title> and <h2> (see test_html_title_and_h2)
        m = re.match(r"##\s+(.+)", s)                         # markdown H2 (not H3)
        if m:
            headings.append(m.group(1).strip())
            continue
        m = re.match(r"#\s+(.+)", s)   # a further H1: flat, single-level prose
        if m:
            h1_sections.append(m.group(1).strip())
            continue
        for inner in re.findall(r"<h2[^>]*>(.*?)</h2>", s, re.I):  # html H2
            headings.append(re.sub(r"<[^>]+>", "", inner).strip())
    # A prompt corpus (fabric: 255 files) writes every section as `# `: with no H2 at
    # all, the later H1s ARE the sections, and the hint would otherwise be empty.
    return title, (headings or h1_sections)


# implements: ARCH-EXTRACT-008  # implements: REQ-EXTRACT-981
SYS_PLACEHOLDER_ID = "SYS-NEEDS-A-NAME-001"


def _arch_id_for(rel_dir):  # implements: ARCH-EXTRACT-008  # implements: REQ-EXTRACT-981
    """The architecture id proposed for a source directory.

    The directory is the only structural signal a per-file draft has, and it is a weak
    one: on this repo it would name capabilities `scripts` and `app/src/lib`, which are
    not capabilities. That is why the node it produces is a `draft` carrying
    `level_source: auto` — a proposal to rename, not a claim."""
    parts = [p for p in rel_dir.replace(os.sep, "/").split("/") if p not in ("", ".")]
    stem = "-".join(parts[-2:]) if parts else "ROOT"
    slug = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").upper() or "ROOT"
    return "ARCH-{}-001".format(slug)


def _write_sys_placeholder(reqs_dir, arch_ids):
    # implements: ARCH-EXTRACT-008  # implements: REQ-EXTRACT-981
    """The apex, written as an explicit hole.

    A stakeholder need is not in the source — nothing in a repository says why a user
    wants the thing — so the engine refuses to guess one and mints a node whose title
    says so. Skipped when the corpus already has a `layer: need`."""
    dest = os.path.join(reqs_dir, SYS_PLACEHOLDER_ID + ".md")
    if os.path.exists(dest) or not arch_ids:
        return 0
    with open(dest, "w", encoding="utf-8") as f:
        f.write("---\nid: {}\nstatus: draft\nlevel: system\nlayer: need\n"
                "owner: auto\nlevel_source: auto\n---\n\n"
                "# NAME THIS NEED\n\n"
                "> The engine cannot read a stakeholder need out of source code, so it "
                "left this hole rather than invent one. Replace the title and the clause "
                "below with the outcome a user actually wants, then rename the file and "
                "the id. Every architecture draft points here until you do.\n\n"
                "## Description\n"
                "Every bullet below is binding.\n"
                "- TODO: the outcome a user wants, in their words, not the system's.\n\n"
                "## Cases\n"
                "CASE-1\n"
                "  Given  TODO\n"
                "  When   TODO\n"
                "  Then   TODO\n".format(SYS_PLACEHOLDER_ID))
    return 1


def _write_arch_drafts(reqs_dir, by_dir):
    # implements: ARCH-EXTRACT-008  # implements: REQ-EXTRACT-981
    """One architecture draft per source directory that produced code drafts.

    Returns the ids written, newest-corpus-first order irrelevant. Each is a proposal:
    `status: draft`, `owner: auto`, `level_source: auto`, and a title that names the
    directory rather than pretending to name a capability."""
    written = []
    for rel_dir in sorted(by_dir):
        aid = _arch_id_for(rel_dir)
        dest = os.path.join(reqs_dir, aid + ".md")
        if os.path.exists(dest):
            written.append(aid)
            continue
        kids = sorted(by_dir[rel_dir])
        with open(dest, "w", encoding="utf-8") as f:
            f.write("---\nid: {aid}\nstatus: draft\nlevel: architecture\n"
                    "layer: feature\nowner: auto\nlevel_source: auto\n"
                    "satisfies: [{sys}]\n---\n\n"
                    "# {label}\n\n"
                    "> PROPOSED grouping, not a capability. The engine had one structural "
                    "signal — the directory `{rel_dir}` — and a directory is not a "
                    "capability. Rename this to the thing these {n} behaviour group(s) "
                    "together let a user do, merge it with a sibling, or delete it and "
                    "re-point its children.\n\n"
                    "## Description\n"
                    "Every bullet below is binding.\n"
                    "{bullets}\n\n"
                    "## Cases\n"
                    "CASE-1\n"
                    "  Given  TODO\n"
                    "  When   TODO\n"
                    "  Then   TODO\n".format(
                        aid=aid, sys=SYS_PLACEHOLDER_ID, label=rel_dir or "root",
                        rel_dir=rel_dir or ".", n=len(kids),
                        bullets="\n".join(
                            "- TODO: one obligation this capability owes. [[{}]]".format(k)
                            for k in kids)))
        written.append(aid)
    return written


def _write_prose_draft(dest, cap, rel, fn, src):
    # implements: ARCH-EXTRACT-008  # implements: ARCH-PROSE-024
    # implements: REQ-EXTRACT-849  # implements: REQ-EXTRACT-850
    """Write one DRAFT .md for a prose capability file; returns the review label."""
    title, headings = _prose_facts(src)
    review = "REVIEW"   # intent is unrecoverable from prose — always author
    hint = "\n".join("  - {}".format(h) for h in headings) \
        or "  - (no section headings detected)"
    # str.format (not f-string): the template embeds literal {cap}/{rel}
    # inside backticked instructions
    with open(dest, "w", encoding="utf-8") as f:
        f.write("---\nid: {cap}\nstatus: draft\nlayer: feature\n"
                "owner: auto\ndepends_on: []\n"
                "risk: 2  # REVIEW — prose capability, author the contract "
                "before promoting\n---\n\n"
                "# {title}\n\n"
                "> DRAFT extracted from {rel} (prose capability). The source "
                "prose is NOT the contract — author the normative behavior "
                "below, then tag the source `# generated-from: {cap}` "
                "(HTML: `<!-- generated-from: {cap} -->`) and promote.\n\n"
                "## Description\n"
                "Every bullet below is binding.\n"
                "<!-- Name the subject, write in present tense, one statement per "
                "bullet, at most 3 sentences and 150 words. -->\n"
                "- TODO: the capability this prose defines (author from "
                "intent, do not copy the prose).\n\n"
                "## Verify intent (open questions for the human)\n"
                "- TODO: which source sections are normative vs illustrative?\n\n"
                "## Cases (= tests)\n"
                "- TODO: Given/When/Then checks for the contract above.\n\n"
                # the hint belongs in Context: bullets under Verify intent
                # are read back as open questions by `findings`
                "## Context (non-binding)\n**Current implementation**\n- {rel}\n\n"
                "**Source sections detected (authoring hint, not the contract)**\n"
                "{hint}\n".format(
                    cap=cap, title=(title or os.path.splitext(fn)[0]),
                    rel=rel, hint=hint))
    return review


def _write_code_draft(dest, cap, rel, fp, code_root, src):
    # implements: ARCH-EXTRACT-008  # implements: ARCH-PROSE-024
    # implements: REQ-EXTRACT-849  # implements: REQ-EXTRACT-850
    """Write one DRAFT .md for a code file; returns the review label. `fp` is the
    file's full path (dirpath + fn folded into one, to keep the parameter count down)."""
    dirpath, fn = os.path.dirname(fp), os.path.basename(fp)
    risk = _risk(src)
    review = "REVIEW" if risk >= 2 else "auto-baseline"
    surface = _observed_surface(_file_facts(fp, rel))
    with open(dest, "w", encoding="utf-8") as f:
        # emission schema matches REQUIREMENT_TEMPLATE so a promoted draft
        # needs no reshaping
        f.write(f"---\nid: {cap}\nstatus: draft\nlevel: code\n"
                f"layer: feature\nowner: auto\nlevel_source: auto\n"
                f"satisfies: [{_arch_id_for(os.path.relpath(dirpath, code_root))}]\n"
                f"depends_on: []\n"
                f"risk: {risk}  # {review} — author triage hint, not read by "
                f"the engine\n---\n\n"
                f"# {os.path.splitext(fn)[0]}\n\n"
                f"> DRAFT extracted from {rel}. Describes observed behavior, "
                f"not validated intent.\n\n"
                f"## Description\n"
                f"Every bullet below is binding.\n"
                f"<!-- Name the subject, write in present tense, one statement per "
                f"bullet, at most 3 sentences and 150 words. -->\n"
                f"- TODO: the observed behavior (characterization — "
                f"correctness UNVERIFIED).\n\n"
                f"## Verify intent (open questions for the human)\n"
                f"- TODO: anything that looks like an accident (swallowed error, magic "
                f"constant, dead branch) — intended, or a bug to fix?\n\n"
                f"## Cases (= tests)\n"
                f"- characterization: current behavior captured, correctness UNVERIFIED\n\n"
                f"## Context (non-binding)\n**Current implementation**\n- {rel}\n{surface}")
    return review


def cmd_extract(ws):
    # implements: ARCH-EXTRACT-008  # implements: ARCH-PROSE-024
    # implements: REQ-EXTRACT-849  # implements: REQ-EXTRACT-850
    """Propose DRAFT requirements for code files that have no member tag yet."""
    members, reqs_dir, code_root = ws.members, ws.reqs_dir, ws.code_root
    tagged = {fp for hits in members.values() for (_, fp, _) in hits}
    proposed, used = 0, set()
    by_dir = {}          # rel dir -> [code-level draft ids], for the ARCH rung
    os.makedirs(reqs_dir, exist_ok=True)
    for fp, rel in _walk_files(code_root, reqs_dir,
                               lambda fn, _r: _is_code_file(fn) or fn.endswith(PROSE_EXTS)):
        dirpath, fn = os.path.dirname(fp), os.path.basename(fp)
        is_prose = fn.endswith(PROSE_EXTS)
        if rel in tagged:
            continue
        if is_prose and classify_prose(rel) != "capability":
            continue                           # bucket 1/2 -> never auto-drafted
        cap = base = _draft_id(rel)
        k = 2
        while cap in used:                 # residual collision (case/ext only)
            cap = "{}-{}".format(base, k); k += 1
        used.add(cap)
        dest = os.path.join(reqs_dir, cap + ".md")
        if os.path.exists(dest):
            continue
        with open(os.path.join(dirpath, fn), encoding="utf-8", errors="ignore") as f:
            src = f.read()
        if is_prose:
            review = _write_prose_draft(dest, cap, rel, fn, src)
        else:
            review = _write_code_draft(dest, cap, rel, fp, code_root, src)
        proposed += 1
        if not is_prose:   # a file that passed the filter is one or the other
            rel_dir = os.path.relpath(dirpath, code_root).replace(os.sep, "/")
            by_dir.setdefault(rel_dir, []).append(cap)
        print(f"{review:14} {cap}  <- {rel}")
    # The two rungs above the code level. Written last, so they know their children.
    arch_ids = _write_arch_drafts(reqs_dir, by_dir)
    n_sys = _write_sys_placeholder(reqs_dir, arch_ids)
    if arch_ids:
        print(f"\n{len(arch_ids)} architecture draft(s) proposed from directory names, and "
              f"{n_sys} system placeholder. Both carry `level_source: auto` — the engine "
              f"invented them and a directory is not a capability. Rename, merge or delete "
              f"them; the code level below is the only rung it can assert.")
    print(f"\n{proposed} draft requirements proposed. Review the REVIEW ones before promoting.")
    return 0


def _observed_surface(facts, limit=12):  # implements: ARCH-EXTRACT-008
    """Authoring hint for a code draft's Context/Current-implementation group: the
    module docstring's first line and the top-level signatures `plan` already knows
    how to read. Empty string when the language has no parser. Non-binding by
    construction — it lives under Context, never in the Contract, so a promoted
    draft still needs an authored contract."""
    sigs = list(facts.get("signatures") or [])
    doc = (facts.get("docstrings") or {}).get("module")
    if not sigs and not doc:
        return ""
    lines = ["", "Observed surface (auto, non-binding — an authoring hint, not the contract):"]
    if doc:
        lines.append("- module: {}".format(doc))
    lines += ["- `{}`".format(s) for s in sigs[:limit]]
    if len(sigs) > limit:
        lines.append("- … {} more".format(len(sigs) - limit))
    return "\n".join(lines) + "\n"


def _risk(src):  # implements: ARCH-EXTRACT-008  # implements: REQ-EXTRACT-851
    score = 0
    if re.search(r"\b(TODO|FIXME|HACK|XXX)\b", src): score += 1
    if "# noqa" in src or "eslint-disable" in src: score += 1
    if len(src.splitlines()) > 300: score += 1
    return score

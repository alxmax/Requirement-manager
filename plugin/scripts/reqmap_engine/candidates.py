"""`plan`: read-only capability-extraction plan from file facts (Python, JS, Markdown)."""
import ast, fnmatch, json, os, re

from . import MAP_ENGINE_VERSION, config as cfg
from .model import _as_list
from .scan import _walk_files
from .tags import PROSE_EXTS, _is_code_file, _is_test_path


# ---------- candidates (capability extraction plan) ----------
# Stage 1 of AI extraction: gather the raw material an authoring step (a human or
# an LLM agent) needs to write a real, capability-level requirement. READ-ONLY —
# emits a JSON plan, writes NO .md, so it cannot repeat extract's empty-stub failure.
# Languages `plan` can read FACTS from (docstrings, signatures). Every scannable code
# file is a candidate regardless — three evidence runs (zlib: 0 candidates for 94 C
# files, gin: none for 99 Go files, awesome-compose: none for 35 Dockerfiles) showed
# a plan that silently omitted most of what `draft` then produced.
CANDIDATE_EXTS = (".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".mts", ".cts")


def _class_method_signatures(node):
    # implements: ARCH-CANDIDATES-009  # implements: REQ-CANDIDATES-826
    """Public method signatures of a class body, as `def Class.method(args)` strings.

    The public surface of a class-based module IS its methods (httpx's
    _client.py hid 78 of them behind 3 module-level helpers)."""
    sigs = []
    for sub in node.body:
        if not isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if sub.name.startswith("_"):
            continue
        args = ", ".join(a.arg for a in sub.args.args if a.arg != "self")
        sigs.append("def {}.{}({})".format(node.name, sub.name, args))
    return sigs


def _py_facts(src):  # implements: ARCH-CANDIDATES-009  # implements: REQ-CANDIDATES-826
    """Module/symbol docstrings, top-level signatures and import targets via the
    stdlib `ast`. A SyntaxError/ValueError yields empty facts so one unparseable
    file (incl. a source with an embedded NUL byte, which ast.parse rejects with
    ValueError, not SyntaxError) never aborts the whole plan."""
    facts = {"signatures": [], "docstrings": {}, "imports": []}
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return facts
    mod_doc = ast.get_docstring(tree)
    if mod_doc and mod_doc.strip():
        facts["docstrings"]["module"] = mod_doc.strip().splitlines()[0][:200]
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            facts["signatures"].append("def {}({})".format(
                node.name, ", ".join(a.arg for a in node.args.args)))
        elif isinstance(node, ast.ClassDef):
            facts["signatures"].append("class {}".format(node.name))
            facts["signatures"].extend(_class_method_signatures(node))
        else:
            continue
        d = ast.get_docstring(node)
        if d and d.strip():
            facts["docstrings"][node.name] = d.strip().splitlines()[0][:200]
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imports.add(node.module.split(".")[0])
    facts["imports"] = sorted(imports)
    return facts


def _js_facts(src):  # implements: ARCH-CANDIDATES-009  # implements: REQ-CANDIDATES-826
    """Best-effort JS/TS facts via regex (no stdlib JS parser): the leading block
    comment as the module doc, and top-level function/binding names. Imports are
    not resolved for JS in v1 (the agent and _capmap.json fill that gap)."""
    facts = {"signatures": [], "docstrings": {}, "imports": []}
    # Leading block comment via plain string scan over a capped prefix — NOT a regex.
    # The old `/\*+(.*?)\*/` backtracks O(n^2) on a file opening with a long run of
    # `*` (a DoS on `candidates`); str.find is linear and cannot backtrack. The
    # leading `*`s of `/***` are stripped by the per-line `.strip(" *")` below.
    head_src = src[:8000].lstrip()
    if head_src.startswith("/*"):
        close = head_src.find("*/", 2)
        if close != -1:
            head = [ln.strip(" *") for ln in head_src[2:close].strip().splitlines()
                    if ln.strip(" *")]
            if head:
                facts["docstrings"]["module"] = head[0][:200]
    names = re.findall(r"(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)", src)
    names += re.findall(r"(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=", src)
    facts["signatures"] = list(dict.fromkeys(names))   # dedupe, keep order
    return facts


def _md_facts(src):  # implements: ARCH-CANDIDATES-009
    """Best-effort capability facts from a Markdown prompt/spec file (no parser):
    the first H1 (`# `) is the title, the first blockquote (`>`) AFTER that H1 is the
    intent, and each `## ` H2 heading is a structural-signature line. Free prose is
    never hashed — these facts only seed a human-authored requirement (Stage 2); the
    binding hash anchors on the authored Contract+Acceptance, like any code requirement."""
    facts = {"signatures": [], "docstrings": {}, "imports": []}
    title, intent, after_h1 = None, None, False
    for line in src.splitlines():
        s = line.strip()
        if title is None and s.startswith("# "):
            title = s[2:].strip(); after_h1 = True; continue
        if after_h1 and intent is None and s.startswith(">"):
            intent = s.lstrip(">").strip()
        if s.startswith("## "):
            facts["signatures"].append("## " + s[3:].strip())
    if title:
        facts["docstrings"]["title"] = title[:200]
    if intent:
        facts["docstrings"]["module"] = intent[:200]
    return facts


def _file_facts(path, rel):  # implements: ARCH-CANDIDATES-009  # implements: REQ-CANDIDATES-826
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            src = f.read()
    except OSError:
        return {"signatures": [], "docstrings": {}, "imports": [], "loc": 0}
    if rel.endswith(".py"):
        facts = _py_facts(src)
    elif rel.endswith(".md"):
        facts = _md_facts(src)
    elif rel.endswith(CANDIDATE_EXTS):
        facts = _js_facts(src)
    else:   # a candidate the engine has no parser for: still listed, facts empty
        facts = {"signatures": [], "docstrings": {}, "imports": []}
    facts["loc"] = len(src.splitlines())
    facts["signatures"] = facts["signatures"][:40]
    return facts


def _load_capmap(reqs_dir):  # implements: ARCH-CANDIDATES-009  # implements: REQ-CANDIDATES-827
    """Optional `requirements/_capmap.json`: a hand-authored capability grouping,
    authoritative when present. Shape: {"capabilities": [{id, layer, files:[...]}]}
    (a bare list is also accepted). Returns []; fail-open on absent/unreadable."""
    try:
        with open(os.path.join(reqs_dir, "_capmap.json"), encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    caps = data.get("capabilities", []) if isinstance(data, dict) else data
    out = []
    if isinstance(caps, list):
        for c in caps:
            if isinstance(c, dict) and c.get("id") and c.get("files"):
                out.append({"id": c["id"], "layer": c.get("layer"),
                            "files": [f.replace(os.sep, "/") for f in _as_list(c["files"])]})
    return out


def _mint_cap_id(rel):  # implements: ARCH-CANDIDATES-009  # implements: REQ-CANDIDATES-827
    """A TAG_RE-valid suggested id from a path stem (Stage 2 may rename it)."""
    slug = re.sub(r"[^A-Z0-9]+", "-", os.path.splitext(rel)[0].upper()).strip("-")
    return (slug or "MOD") + "-001"


def _collect_files(code_root, reqs_dir, md_globs=None):
    # implements: ARCH-CANDIDATES-009  # implements: REQ-CANDIDATES-826
    """Sorted rel paths of candidate source files, honoring _prune_dirs (noise +
    the SSOT dir) and .reqmapignore — the same exclusions scan_members uses.

    `md_globs` is the opt-in, scope-bounding allowlist for non-code discovery: a
    `.md` file is included ONLY when it matches one of these globs (and is not
    ignored). Empty/None -> no `.md` is ever collected (behavior unchanged). The
    presence of a glob IS the opt-in; there is no separate on/off flag."""
    md_globs = md_globs or []
    out = []
    for fp, rel in _walk_files(code_root, reqs_dir):
        fn = os.path.basename(fp)
        if _is_code_file(fn) and not fn.endswith(PROSE_EXTS):
            out.append(rel)
        elif fn.endswith(".md") and any(fnmatch.fnmatch(rel, g) for g in md_globs):
            out.append(rel)
    return out


def _minted_groups(files, facts_by_file, reqs_dir, reqs):
    # implements: ARCH-CANDIDATES-009  # implements: REQ-CANDIDATES-826
    """Grouping: _capmap.json wins; uncovered files fall back to one-per-file.

    De-duplicates minted ids: two files sharing a slug (foo.py + foo.js, or
    foo-bar + foo_bar) would otherwise mint the same id and conflate two
    distinct candidates downstream — bump the numeric suffix on collision.
    Seed from capmap groups AND existing requirement ids so a minted id never
    duplicates a real requirement either."""
    groups, claimed = [], set()
    for entry in _load_capmap(reqs_dir):
        present = [f for f in entry["files"] if f in facts_by_file]
        if present:
            groups.append({"id": entry["id"], "layer": entry.get("layer"), "files": present})
            claimed.update(present)
    used_ids = {g["id"] for g in groups} | set(reqs)
    for rel in files:
        if rel in claimed:
            continue
        cid = _mint_cap_id(rel)
        if cid in used_ids:
            stem = cid[:-3]                 # _mint_cap_id always ends in "-001"
            n = 2
            while "{}{:03d}".format(stem, n) in used_ids:
                n += 1
            cid = "{}{:03d}".format(stem, n)
        used_ids.add(cid)
        groups.append({"id": cid, "layer": None, "files": [rel]})
    return groups


def _test_by_stem_index(files):
    # implements: ARCH-CANDIDATES-009  # implements: REQ-CANDIDATES-826
    """Map each stem to its test_ files, so the per-group tested_by lookup in
    `_build_candidates` is O(1) per stem instead of rescanning `files` per group."""
    test_by_stem = {}
    for r in files:
        b = os.path.basename(r)
        if b.startswith("test_"):
            test_by_stem.setdefault(os.path.splitext(b)[0][len("test_"):], []).append(r)
    return test_by_stem


def _build_candidates(groups, facts_by_file, stem_of, group_id_of_file, test_by_stem, tagged):
    # implements: ARCH-CANDIDATES-009  # implements: REQ-CANDIDATES-826
    """One candidate dict per group: signatures, docstrings, imports, deps, tested_by."""
    cands = []
    for g in groups:
        sigs, docs, imps, loc = [], {}, set(), 0
        my_stems = set()
        for f in g["files"]:
            ff = facts_by_file[f]
            sigs += ["{}: {}".format(f, s) for s in ff["signatures"]]
            for k, v in ff["docstrings"].items():
                docs["{}:{}".format(f, k)] = v
            imps.update(ff["imports"])
            loc += ff.get("loc", 0)
            my_stems.add(os.path.splitext(os.path.basename(f))[0])
        own = set(g["files"])
        deps = sorted({group_id_of_file[stem_of[m]] for m in imps
                       if m in stem_of and stem_of[m] not in own})
        tested_by = sorted(t for stem in my_stems for t in test_by_stem.get(stem, ()))
        existing = next((tagged[f] for f in g["files"] if f in tagged), None)
        cands.append({  # implements: REQ-CANDIDATES-827
            "suggested_id": g["id"], "_layer": g["layer"], "files": g["files"],
            "docstrings": docs, "signatures": sigs[:60], "imports": sorted(imps),
            "depends_on": deps, "tested_by": tested_by, "loc": loc,
            "existing_req": existing, "split_candidate": loc > cfg.SPLIT_LOC_THRESHOLD,
            "is_test": bool(g["files"]) and all(_is_test_path(f) for f in g["files"]),
        })
    return cands


def _annotate_fanin(cands):
    # implements: ARCH-CANDIDATES-009  # implements: REQ-CANDIDATES-827
    """Mutate cands in place: importer_count and suggested_layer (bus vs feature),
    both derived from how many other candidates depend_on each one."""
    fanin = {}
    for c in cands:
        for d in c["depends_on"]:
            fanin[d] = fanin.get(d, 0) + 1
    for c in cands:
        n = fanin.get(c["suggested_id"], 0)
        c["importer_count"] = n
        # implements: REQ-CANDIDATES-827
        c["suggested_layer"] = (
            c.pop("_layer") or ("bus" if n >= cfg.BUS_FANIN_THRESHOLD else "feature")
        )


def cmd_candidates(ws, out, md_globs=None):
    # implements: ARCH-CANDIDATES-009  # implements: REQ-CANDIDATES-826
    """Emit a deterministic JSON capability-extraction plan and write NO .md.
    Grouping: authoritative `requirements/_capmap.json` when present, else one
    candidate per file (the Stage-2 agent merges/splits using judgment).
    `md_globs` opts non-code `.md` files (prompts, specs) into discovery — advisory
    only, never auto-written; a human authors + confirms each into the SSOT."""
    reqs, members, reqs_dir, code_root = ws.reqs, ws.members, ws.reqs_dir, ws.code_root
    files = _collect_files(code_root, reqs_dir, md_globs)
    facts_by_file = {rel: _file_facts(os.path.join(code_root, rel), rel) for rel in files}

    tagged = {}   # file -> already-implemented requirement id (idempotency hint)
    for cap, hits in members.items():
        for role, fp, _ln in hits:
            if role == "implements":
                tagged.setdefault(fp, cap)

    # depends_on is resolved by matching an import name to a file STEM. Known
    # limitation (Stage-1 heuristic): an import that shadows a stdlib/3rd-party name
    # (e.g. `import json` next to a local json.py) or collides with a same-basename
    # file in another dir can yield a false edge — the Stage-2 author prunes these.
    stem_of = {os.path.splitext(os.path.basename(r))[0]: r for r in files}  # for depends_on

    groups = _minted_groups(files, facts_by_file, reqs_dir, reqs)
    group_id_of_file = {f: g["id"] for g in groups for f in g["files"]}
    test_by_stem = _test_by_stem_index(files)
    cands = _build_candidates(
        groups, facts_by_file, stem_of, group_id_of_file, test_by_stem, tagged)
    _annotate_fanin(cands)

    authored = sum(1 for c in cands if c["existing_req"])
    plan = {
        "engine_version": MAP_ENGINE_VERSION,
        # surfaces the unfilled-plan gap so an advisory plan nobody authored cannot
        # masquerade as coverage (with_existing_req = candidates already tagged in code)
        "coverage_summary": {"total_candidates": len(cands), "with_existing_req": authored},
        "lineage_note": ("A generated-from/implements tag records authoring lineage only; it "
                         "does NOT mean the requirement auto-tracks later edits to the source "
                         "file. Re-touch the requirement's Contract+Acceptance when the source's "
                         "behavior changes."),
        "bus": sorted(c["suggested_id"] for c in cands if c["suggested_layer"] == "bus"),
        "candidates": cands,
    }
    text = json.dumps(plan, indent=2, ensure_ascii=False)
    if out and out != "-":
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote {} ({} candidates)".format(out, len(cands)))
    else:
        print(text)
    return 0

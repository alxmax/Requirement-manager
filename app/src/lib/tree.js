// implements: ARCH-VIEWER-007
/* Hierarchy model for the module explorer.
 *
 * The engine emits a specification LEVEL per requirement (system →
 * architecture → code) plus per-node `satisfies` (parents) and `satisfied_by`
 * (children). In the dogfooded corpus that is a strict tree: one parent per
 * node, one root, depth == level. Nothing here ASSUMES that. The corpus of a
 * repo that has not adopted levels carries no `satisfies` at all, and this
 * module degrades to a flat list rather than inventing a shape.
 *
 * Everything below is pure: the explorer memoizes on the registry reference. */

export const LEVELS = ["system", "architecture", "code"];
export const LEVEL_LABEL = { system: "System", architecture: "Architecture", code: "Code" };
export const LEVEL_SHORT = { system: "SYS", architecture: "ARC", code: "COD" };

export function levelOf(r) {
  const l = r && r.level;
  return LEVELS.indexOf(l) >= 0 ? l : "architecture";
}
export function levelRank(l) {
  const i = LEVELS.indexOf(l);
  return i < 0 ? 1 : i;
}

/* ---- open questions --------------------------------------------------------
 * A requirement's `## WHAT — Verify intent` bullets. The engine's
 * `collect_findings` drops any bullet whose `lstrip("*_ ").lower()` starts with
 * "none" — the placeholder every `draft` command writes. Today 57 nodes carry a
 * `verify` array and every entry is that placeholder, so the honest count is 0.
 * This filter is the JS half of that one rule; keep the two in step, or the
 * viewer will badge findings the CLI does not report. */
export function openQuestions(r) {
  const v = r && Array.isArray(r.verify) ? r.verify : [];
  return v
    .map((x) => String(x))
    .filter((x) => x.trim() !== "")
    .filter((x) => !x.replace(/^[*_ ]+/, "").toLowerCase().startsWith("none"));
}
export function hasOpenQuestions(r) {
  return openQuestions(r).length > 0;
}

/* ---- hierarchy -------------------------------------------------------------
 * `satisfies` is authoritative; `satisfied_by` fills a parent in for a node that
 * declares none (the two are mirrors in a well-formed export, but a hand-edited
 * or partial map can carry one side only). A node whose parent id is not in the
 * registry stays a root — a dangling trace edge is the gate's problem to report,
 * not a reason for the outline to lose the row. */
export function buildHierarchy(reqs) {
  const list = Array.isArray(reqs) ? reqs : [];
  const byId = Object.create(null);
  list.forEach((r) => { byId[r.id] = r; });

  const parentOf = Object.create(null);
  let declared = 0;

  list.forEach((r) => {
    const parents = Array.isArray(r.satisfies) ? r.satisfies : [];
    if (parents.length) declared++;
    const p = parents.find((x) => x !== r.id && byId[x]);
    if (p) parentOf[r.id] = p;
  });
  list.forEach((r) => {
    (Array.isArray(r.satisfiedBy) ? r.satisfiedBy : []).forEach((c) => {
      if (c !== r.id && byId[c] && !parentOf[c]) { parentOf[c] = r.id; declared++; }
    });
  });

  // Cycle guard. A `satisfies` cycle is a modelling error, but the outline must
  // still render every row exactly once: walk each node's ancestry and cut the
  // link of any node that reaches itself, promoting it to a root.
  Object.keys(parentOf).forEach((id) => {
    const seen = Object.create(null);
    let cur = id;
    while (cur && parentOf[cur]) {
      if (seen[cur]) { delete parentOf[id]; return; }
      seen[cur] = true;
      cur = parentOf[cur];
    }
  });

  const childrenOf = Object.create(null);
  list.forEach((r) => { childrenOf[r.id] = []; });
  list.forEach((r) => { const p = parentOf[r.id]; if (p) childrenOf[p].push(r.id); });

  const cmp = (a, b) => {
    const d = levelRank(levelOf(byId[a])) - levelRank(levelOf(byId[b]));
    return d !== 0 ? d : a.localeCompare(b);
  };
  Object.keys(childrenOf).forEach((k) => childrenOf[k].sort(cmp));

  const roots = list.map((r) => r.id).filter((id) => !parentOf[id]).sort(cmp);
  return { byId, parentOf, childrenOf, roots, flat: declared === 0 };
}

/** Root-most → immediate parent. */
export function ancestorsOf(h, id) {
  const out = [];
  let cur = h.parentOf[id];
  while (cur && out.indexOf(cur) < 0) { out.unshift(cur); cur = h.parentOf[cur]; }
  return out;
}

/** Nodes open on first paint: everything with at least one NON-code child.
 *  Root + the systems, i.e. the 67 rows that carry the substance; the ~618 code
 *  clauses stay behind their parent's count chip until asked for. */
export function defaultExpanded(h) {
  const out = Object.create(null);
  Object.keys(h.childrenOf).forEach((id) => {
    const kids = h.childrenOf[id];
    if (kids.length && kids.some((c) => levelOf(h.byId[c]) !== "code")) out[id] = true;
  });
  return out;
}

export function allExpanded(h) {
  const out = Object.create(null);
  Object.keys(h.childrenOf).forEach((id) => { if (h.childrenOf[id].length) out[id] = true; });
  return out;
}

/** matched ∪ every ancestor of a match — so a deep hit keeps its context rows. */
export function keepSetFor(h, ids) {
  const keep = Object.create(null);
  ids.forEach((id) => {
    keep[id] = true;
    ancestorsOf(h, id).forEach((a) => { if (!keep[a]) keep[a] = "context"; });
  });
  return keep;
}

/** Depth-first rows in hierarchy order.
 *  `keep` (from keepSetFor) restricts the walk and force-opens the surviving
 *  ancestors — a filter that hid its own matches behind a collapsed parent
 *  would read as "no results". */
export function flattenTree(h, { expanded, keep }) {
  const rows = [];
  const filtering = !!keep;
  const walk = (id, depth) => {
    if (filtering && !keep[id]) return;
    const kids = h.childrenOf[id] || [];
    const shown = filtering ? kids.filter((c) => keep[c]) : kids;
    const open = filtering ? shown.length > 0 : !!(expanded && expanded[id]);
    rows.push({
      id,
      r: h.byId[id],
      depth,
      childCount: shown.length,
      codeChildren: shown.filter((c) => levelOf(h.byId[c]) === "code").length,
      hasChildren: shown.length > 0,
      expanded: open,
      context: filtering && keep[id] === "context",
    });
    if (open) shown.forEach((c) => walk(c, depth + 1));
  };
  h.roots.forEach((id) => walk(id, 0));
  return rows;
}

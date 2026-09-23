// implements: ARCH-VIEWER-007
import { buildHierarchy } from "./tree.js";

/* Graph layout computed from the live registry — no hand-tuned coordinates.
 *
 * Produces a layered "main-bus" layout: nodes are ranked by dependency
 * depth so `depends_on` edges flow left→right (consumers on the left,
 * shared foundation / bus-layer nodes on the right). A barycenter pass
 * orders each rank to cut edge crossings; edge-less nodes are parked in
 * a side grid. The same routine drives the System Map, the Risk tab (on
 * the flagged subset) and the area-level Dependency tab (on an
 * area-collapsed graph). */

export const NODE_W = 152;
// vertical offset used as the card's connection point (cards are
// ~80-134px tall; this approximates their centre for edge attachment).
export const NODE_CY = 46;

/** depends_on edges between members of `ids` (both endpoints present). */
export function edgesWithin(reqs, ids) {
  const set = ids instanceof Set ? ids : new Set(ids);
  const out = [];
  for (const r of reqs) {
    for (const d of r.deps || []) {
      if (set.has(d) && set.has(r.id)) out.push([r.id, d]);
    }
  }
  return out;
}

/** Edges that close a cycle, found by DFS: an edge into a node still on
 * the recursion stack. Returned as a Set of "a\u0000b" keys.
 *
 * A `depends_on` cycle is a modelling error the gate reports, but the
 * viewer must still draw such a registry, and draw it legibly. Ranking a
 * cyclic graph by longest-path relaxation never converges: every pass
 * adds one to every node around the cycle, so the loop runs its full
 * `ids.length` passes and the ranks come out as high as it was allowed
 * to count. A real corpus of 59 requirements with three cycles produced
 * maxRank 236 — where a DAG of 59 nodes cannot exceed 58 — which is a
 * 71,000px-wide canvas with ~230 empty columns, and edges drawn as
 * near-endless horizontal lines stepping through every one of them. */
function backEdges(ids, edges) {  // implements: REQ-VIEWER-942
  const out = {};
  ids.forEach((id) => (out[id] = []));
  for (const [a, b] of edges) if (out[a]) out[a].push(b);
  const state = {}, back = new Set();
  // 0/undef = unseen, 1 = on stack, 2 = done
  const visit = (root) => {
    // iterative DFS: a deep chain must not blow the JS stack in a viewer
    const stack = [[root, 0]];
    state[root] = 1;
    while (stack.length) {
      const frame = stack[stack.length - 1];
      const [u, i] = frame;
      if (i >= out[u].length) { state[u] = 2; stack.pop(); continue; }
      frame[1]++;
      const v = out[u][i];
      if (state[v] === 1) back.add(u + "\u0000" + v);        // closes a cycle
      else if (state[v] !== 2) { state[v] = 1; stack.push([v, 0]); }
    }
  };
  for (const id of ids) if (!state[id]) visit(id);
  return back;
}

/** Longest-path rank so that for every edge a→b (a depends_on b),
 * rank(b) > rank(a). Cycle-closing edges are excluded from the ranking
 * (they are still drawn), so the remaining graph is a DAG and the
 * relaxation converges in at most `ids.length` passes with
 * rank <= ids.length - 1. */
function rankNodes(ids, edges) {  // implements: REQ-VIEWER-942
  const back = backEdges(ids, edges);
  const acyclic = edges.filter(([a, b]) => !back.has(a + "\u0000" + b));
  const rank = {};
  ids.forEach((id) => (rank[id] = 0));
  for (let pass = 0; pass < ids.length; pass++) {
    let changed = false;
    for (const [a, b] of acyclic) {
      if (rank[b] < rank[a] + 1) { rank[b] = rank[a] + 1; changed = true; }
    }
    if (!changed) break;
  }
  return rank;
}

const mean = (a) => (a.length ? a.reduce((s, x) => s + x, 0) / a.length : null);

/** Barycenter crossing-minimisation: order each rank by the mean position
 * of its neighbours in adjacent ranks, sweeping down then up a few times. */
function orderRanks(cols, maxRank, inc, out, deg) {
  // implements: REQ-VIEWER-942
  const ord = {};
  for (let r = 0; r <= maxRank; r++) {
    (cols[r] || []).forEach((id, i) => (ord[id] = i));
  }
  const reorder = (r, useInc) => {
    const c = cols[r]; if (!c || !c.length) return;
    const bc = {};
    for (const id of c) {
      const nb = (useInc ? inc : out)[id]
        .filter((x) => deg[x]).map((x) => ord[x]);
      const m = mean(nb); bc[id] = m == null ? ord[id] : m;
    }
    c.sort((a, b) => bc[a] - bc[b]); c.forEach((id, i) => (ord[id] = i));
  };
  for (let it = 0; it < 6; it++) {
    for (let r = 1; r <= maxRank; r++) reorder(r, true);
    for (let r = maxRank - 1; r >= 0; r--) reorder(r, false);
  }
  return ord;
}

/**
 * @param {Array} reqs  list of {id, deps, ...}
 * @returns {{pos:Object<string,[number,number]>, edges:Array,
 *   width:number, height:number}}
 */
export function computeLayout(reqs, opts = {}) {  // implements: REQ-VIEWER-942
  const COLW = opts.colW || 300, ROWH = opts.rowH || 170;
  const X0 = 50, Y0 = 40, ISO_COLS = 3, ISO_W = 220;
  const ids = reqs.map((r) => r.id);
  const idset = new Set(ids);
  const edges = edgesWithin(reqs, idset);

  const deg = {}, inc = {}, out = {};
  ids.forEach((id) => { deg[id] = 0; inc[id] = []; out[id] = []; });
  for (const [a, b] of edges) {
    deg[a]++; deg[b]++; out[a].push(b); inc[b].push(a);
  }

  const rank = rankNodes(ids, edges);
  const cols = {}; let maxRank = 0; const iso = [];
  for (const id of ids) {
    if (!deg[id]) { iso.push(id); continue; }
    const r = rank[id];
    (cols[r] = cols[r] || []).push(id);
    if (r > maxRank) maxRank = r;
  }

  const ord = orderRanks(cols, maxRank, inc, out, deg);

  let maxN = 1;
  for (let r = 0; r <= maxRank; r++) {
    if (cols[r] && cols[r].length > maxN) maxN = cols[r].length;
  }
  const yMid = Y0 + ((maxN - 1) / 2) * ROWH;

  const pos = {};
  for (let r = 0; r <= maxRank; r++) {
    const c = (cols[r] || []).slice().sort((a, b) => ord[a] - ord[b]);
    const y0 = yMid - ((c.length - 1) / 2) * ROWH;
    c.forEach((id, row) => (pos[id] = [X0 + r * COLW, y0 + row * ROWH]));
  }
  const isoX = X0 + (maxRank + 1) * COLW + 30;
  const isoY0 = yMid - ((Math.ceil(iso.length / ISO_COLS) - 1) / 2) * ROWH;
  iso.forEach((id, k) => {
    pos[id] = [isoX + (k % ISO_COLS) * ISO_W,
               isoY0 + Math.floor(k / ISO_COLS) * ROWH];
  });

  let width = 1000, height = 600;
  for (const [x, y] of Object.values(pos)) {
    width = Math.max(width, x + NODE_W + 60);
    height = Math.max(height, y + 160);
  }

  // metadata the edge router needs: column x per rank, sorted card tops
  // per rank.
  const colX = {}, colYs = {};
  for (let r = 0; r <= maxRank; r++) {
    colX[r] = X0 + r * COLW;
    colYs[r] = (cols[r] || []).map((id) => pos[id][1]).sort((a, b) => a - b);
  }
  return {
    pos, edges, width, height, hasIsolated: iso.length > 0, colX, colYs,
    rankOf: rank, colW: COLW, lo: 0, hi: height,
  };
}

/* ---- card-avoiding orthogonal edge routing ------------------------------ */

const CARD_H = 128; // conservative card height for gap detection

/** A y near `wantY` that is clear of every card in `tops` (their top-y
 *  list). */
function clearY(tops, wantY, lo, hi) {
  const occ = (tops || []).map((y) => [y - 6, y + CARD_H + 6])
    .sort((a, b) => a[0] - b[0]);
  if (!occ.some(([a, b]) => wantY >= a && wantY <= b)) return wantY;
  const gaps = []; let prev = lo;
  for (const [a, b] of occ) {
    if (a > prev) gaps.push([prev, a]); prev = Math.max(prev, b);
  }
  if (prev < hi) gaps.push([prev, hi]);
  let best = wantY, bd = Infinity;
  for (const [a, b] of gaps) {
    const c = b - a >= 20
      ? Math.max(a + 10, Math.min(b - 10, wantY)) : (a + b) / 2;
    const dd = Math.abs(c - wantY);
    if (dd < bd) { bd = dd; best = c; }
  }
  return best;
}

/** Polyline → rounded SVG path. */
function roundedPath(pts, R = 11) {
  if (pts.length < 2) return "";
  let d = `M${pts[0][0]},${pts[0][1]}`;
  for (let i = 1; i < pts.length - 1; i++) {
    const [px, py] = pts[i - 1], [cx, cy] = pts[i], [nx, ny] = pts[i + 1];
    const v1x = cx - px, v1y = cy - py, v2x = nx - cx, v2y = ny - cy;
    const l1 = Math.hypot(v1x, v1y) || 1, l2 = Math.hypot(v2x, v2y) || 1;
    const r = Math.min(R, l1 / 2, l2 / 2);
    const inX = cx - (v1x / l1) * r, inY = cy - (v1y / l1) * r;
    const outX = cx + (v2x / l2) * r, outY = cy + (v2y / l2) * r;
    d += ` L${inX},${inY} Q${cx},${cy} ${outX},${outY}`;
  }
  const last = pts[pts.length - 1];
  d += ` L${last[0]},${last[1]}`;
  return d;
}

/**
 * Orthogonal path from a→b that keeps verticals in the inter-column gutters and
 * crosses any intermediate column only through a gap between its cards — so the
 * line never runs through a card it doesn't connect to.
 */
export function buildEdgePath(meta, a, b) {
  const { pos, colX, colYs, rankOf, lo = 0, hi = 600 } = meta;
  const A = pos[a], B = pos[b]; if (!A || !B) return null;
  const fwd = B[0] >= A[0];
  const sx = fwd ? A[0] + NODE_W : A[0], sy = A[1] + NODE_CY;
  const tx = fwd ? B[0] : B[0] + NODE_W, ty = B[1] + NODE_CY;
  const ra = rankOf[a], rb = rankOf[b];
  const gut = (r) => (colX[r] + NODE_W + colX[r + 1]) / 2;

  if (fwd && rb > ra && colX[rb] !== undefined) {
    const pts = [[sx, sy]]; let ycur = sy;
    for (let k = ra; k < rb; k++) {
      const gx = gut(k);
      pts.push([gx, ycur]);
      if (k < rb - 1) {
        const want = sy + (ty - sy) * ((k - ra + 1) / (rb - ra));
        ycur = clearY(colYs[k + 1], want, lo, hi);
        pts.push([gx, ycur]);
      } else {
        pts.push([gx, ty]); ycur = ty;
      }
    }
    pts.push([tx, ty]);
    return roundedPath(pts);
  }
  // adjacent / fallback: simple S-curve handled by the caller's default
  return null;
}

/** Deterministic distinct colour per id. `line` is a saturated stroke for
 * edges (each edge is drawn in its source requirement's colour so
 * overlapping lines stay traceable); `bg`/`border` are light tints kept
 * available for other surfaces. */
export function colorFor(id) {
  let h = 2166136261;
  for (let i = 0; i < id.length; i++) {
    h ^= id.charCodeAt(i); h = Math.imul(h, 16777619);
  }
  const hue = (h >>> 0) % 360;
  const sat = 60 + ((h >>> 8) % 18);
  return {
    bg: `hsl(${hue} ${sat}% 92%)`,
    border: `hsl(${hue} ${Math.min(sat + 4, 70)}% 60%)`,
    line: `hsl(${hue} 65% 45%)`,
  };
}

/** DFS-place each visible node into (x-unit, depth) coordinates, sized by
 * its visible subtree width, then converted to pixel positions. `grid` is
 * the pixel geometry: { COLW, ROWH, X0, Y0 }. */
function placeHierarchy(h, visible, visSet, grid) {
  // implements: REQ-VIEWER-942
  const { COLW, ROWH, X0, Y0 } = grid;
  const subtreeW = {};
  const widthOf = (id) => {
    if (subtreeW[id] != null) return subtreeW[id];
    const kids = (h.childrenOf[id] || []).filter((c) => visSet.has(c));
    subtreeW[id] = kids.length ? kids.reduce((s, c) => s + widthOf(c), 0) : 1;
    return subtreeW[id];
  };

  const pos = {};
  const depthOf = {};
  const place = (id, xUnit, depth) => {
    depthOf[id] = depth;
    const kids = (h.childrenOf[id] || []).filter((c) => visSet.has(c));
    const w = widthOf(id);
    pos[id] = [X0 + xUnit * COLW + Math.max(0, (w * COLW - NODE_W) / 2),
               Y0 + depth * ROWH];
    let cx = xUnit;
    kids.forEach((c) => { place(c, cx, depth + 1); cx += widthOf(c); });
  };

  let xUnit = 0;
  h.roots.filter((id) => visSet.has(id))
    .forEach((id) => {
      widthOf(id); place(id, xUnit, 0); xUnit += widthOf(id);
    });
  visible.forEach((r) => {
    if (pos[r.id]) return;
    widthOf(r.id);
    place(r.id, xUnit, 0);
    xUnit += widthOf(r.id);
  });
  return { pos, depthOf };
}

/** Top-down V-model tree: system → architecture via `satisfies` /
 * `satisfied_by`. The code level is counted per node but not drawn —
 * same scope as _map.md's Specification Hierarchy diagram. */
export function computeHierarchyLayout(reqs, opts = {}) {
  // implements: REQ-VIEWER-942
  const COLW = opts.colW || 220;
  const ROWH = opts.rowH || 130;
  const X0 = 50, Y0 = 40;
  const h = buildHierarchy(reqs);
  const visible = reqs.filter((r) => r.level !== "code");
  const visSet = new Set(visible.map((r) => r.id));

  const edges = [];
  const edgeKeys = new Set();
  visible.forEach((r) => {
    (r.satisfiedBy || []).forEach((c) => {
      if (!visSet.has(c)) return;
      const key = r.id + "\u0000" + c;
      if (!edgeKeys.has(key)) { edgeKeys.add(key); edges.push([r.id, c]); }
    });
    (r.satisfies || []).forEach((p) => {
      if (!visSet.has(p)) return;
      const key = p + "\u0000" + r.id;
      if (!edgeKeys.has(key)) { edgeKeys.add(key); edges.push([p, r.id]); }
    });
  });

  const codeCounts = {};
  visible.forEach((r) => {
    codeCounts[r.id] = (h.childrenOf[r.id] || []).filter((c) => {
      const child = h.byId[c];
      return child && child.level === "code";
    }).length;
  });

  const { pos, depthOf } = placeHierarchy(
    h, visible, visSet, { COLW, ROWH, X0, Y0 });

  let width = 800, height = 520;
  for (const [x, y] of Object.values(pos)) {
    width = Math.max(width, x + NODE_W + 60);
    height = Math.max(height, y + 160);
  }

  const maxDepth = Math.max(0, ...Object.values(depthOf));
  const colX = {}, colYs = {};
  for (let d = 0; d <= maxDepth; d++) {
    colX[d] = X0 + d * 0;
    colYs[d] = visible.filter((r) => depthOf[r.id] === d && pos[r.id])
      .map((r) => pos[r.id][1]).sort((a, b) => a - b);
  }
  return {
    pos, edges, width, height, codeCounts, depthOf, colX, colYs,
    rankOf: depthOf,
    lo: 0, hi: height, colW: COLW,
  };
}

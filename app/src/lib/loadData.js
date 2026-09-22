// implements: ARCH-VIEWER-007
/* Bridge between the reqmap engine and the app.
 *
 * The engine's `export` command writes `requirements/_map.json` in a
 * {engine_version, nodes, edges, todos} shape. `npm run sync` copies it to
 * `public/data.json`. At startup loadData() fetches it and adapts each node to
 * the app's requirement shape; on any miss it leaves the baked fallback in
 * place, so the app always renders. */

import { adoptMapExport } from "./data.js";

/* The engine's `_acc_items`, ported: one display string per criterion of the raw
 * Cases text, a `CASE-N — …` line per labelled block with its indented
 * Given/When/Then folded in, or the text of a `- ` bullet. The map carried both
 * forms until v8.3.0, 305 KB of this repo's _map.json twice over; it now carries
 * `accept` alone and this derives the folded form. Checked identical on every node
 * of three corpora (497) before the engine stopped emitting `acc`.
 * implements: REQ-VIEWER-942 */
export function foldAccept(accept) {
  if (typeof accept !== "string" || !accept.trim()) return [];
  const blocks = [];
  for (const line of accept.split("\n")) {
    const s = line.trim();
    const m = /^((?:CASE|AC)-\d+)\b/.exec(s);
    if (m || s.startsWith("- ")) {
      const label = m ? m[1] : "";
      blocks.push({ label, raw: [m ? s.slice(label.length) : s.slice(2)] });
    } else if (s && blocks.length) {
      blocks[blocks.length - 1].raw.push(s);
    }
  }
  const items = [];
  for (const b of blocks) {
    const text = b.raw.join(" ").trim().replace(/<!--[\s\S]*?-->/g, "").trim();
    const item = b.label && text ? `${b.label} — ${text}` : (b.label || text);
    if (item) items.push(item);
  }
  return items;
}

/** engine node ({...used_by, accept}) → app requirement ({...usedBy, acc, gwt}). */
export function adaptNode(n) {
  // An atomic-form requirement has no Cases text to fold, so the engine still emits
  // its one criterion as `acc`; a map written before v8.3.0 carries `acc` for all.
  const acc = Array.isArray(n.acc) ? n.acc : foldAccept(n.accept);
  // the engine always emits a string id, but adaptNode is the trust boundary for
  // any external _map.json — guard it so a malformed node can't throw here
  const id = typeof n.id === "string" ? n.id : String(n.id ?? "");
  return {
    id,
    area: n.area || (id.includes("-") ? id.split("-")[0] : id),
    title: n.title || id,
    layer: n.layer || "feature",
    // Specification LEVEL — the V-model rung this requirement sits on
    // ("system" | "architecture" | "code"). It is what the module explorer
    // builds its outline from. The baked fallback dataset (data.js) predates
    // the field entirely, so it defaults to "architecture": the middle rung,
    // where a flat pre-level corpus honestly belongs — defaulting to "code"
    // would hide every fallback row behind a collapsed parent, and to "system"
    // would promote 15 feature requirements to top-level systems.
    level: n.level || "architecture",
    // Upstream/downstream trace edges. `satisfies` is the parent list (in the
    // current corpus always 0 or 1 entry — a strict tree), `satisfiedBy` the
    // children. Both are carried per node, so the tree needs no separate
    // edge list plumbed through setRegistry().
    satisfies: Array.isArray(n.satisfies) ? n.satisfies : [],
    satisfiedBy: Array.isArray(n.satisfied_by) ? n.satisfied_by : [],
    // Open "verify intent" questions, verbatim. Every bullet the engine emits
    // here is a candidate; the placeholder filter lives in lib/tree.js
    // (openQuestions) so the viewer and `collect_findings` agree on what counts.
    verify: Array.isArray(n.verify) ? n.verify : [],
    status: n.status || "draft",
    intent: n.intent || "",
    contract: Array.isArray(n.contract) ? n.contract : [],
    acc,
    // Raw acceptance text: the labelled Given/When/Then block as authored, rendered
    // line for line. `acc` carries the SAME criteria folded to one line each (for
    // search and counting), so gating this on `acc` being empty meant that the day
    // the engine learned to parse the block form (v2.29.0) every criterion silently
    // collapsed into a run-on line. Prefer the authored shape whenever it exists.
    // implements: REQ-VIEWER-942
    gwt: typeof n.accept === "string" && n.accept.trim() ? n.accept : undefined,
    members: Array.isArray(n.members) ? n.members : [],
    // `depends_on` since v8.3.0; `deps` is the same list under its old name, read from
    // a map an older engine wrote.
    deps: Array.isArray(n.depends_on) ? n.depends_on : Array.isArray(n.deps) ? n.deps : [],
    usedBy: Array.isArray(n.used_by) ? n.used_by : [],
    risks: Array.isArray(n.risks) ? n.risks : [],
    // forward the gate's test-exemption so coverageOf() can return "exempt"
    // instead of falsely flagging exempt requirements as "untested"
    test_exempt: n.test_exempt,
    // per-criterion coverage, emitted ONLY for a requirement that adopted
    // `# verifies:` tagging. Undefined means not measured — coverageDetail() then
    // renders no fraction rather than inventing one.
    clauses: n.clauses,
    covered: n.covered,
    gap: n.gap,
    milestone: n.milestone || null,
    priority: n.priority || "",
    // cached content translations, keyed by locale — see i18n.jsx's
    // translatedText(). Absent for nodes with no `reqmap.py translate` cache.
    i18n: (n.i18n && typeof n.i18n === "object") ? n.i18n : null,  // implements: REQ-TRANSLATE-938
  };
}

/** Data source precedence, all non-throwing:
 *  1. window.__REQMAP_DATA__  — inlined by the engine into the self-contained
 *     _map.html viewer (double-click, no server).
 *  2. ./data.json (or _map.json) — fetched when served over http (dev / preview).
 *  3. the baked fallback dataset already in data.js.
 */
/* The export is forwarded WHOLE, with only `nodes` adapted. It used to be copied key by
 * key, and that hand-kept whitelist is exactly how `roadmap` and `history` shipped in
 * v7.6.0/v7.8.0 reaching the page and never reaching the app: the engine emitted them,
 * `window.__REQMAP_DATA__` carried them, and this function dropped them on the floor, so
 * the Horizons mode and the Shipped band silently never rendered. `adoptMapExport` reads
 * only the keys it knows and validates each one, so a spread is the safe shape and an
 * added key needs no edit here.  implements: REQ-VIEWER-969 */
export async function loadData() {
  // 1. inlined single-file viewer
  const inl = typeof window !== "undefined" ? window.__REQMAP_DATA__ : null;
  if (inl && Array.isArray(inl.nodes) && inl.nodes.length) {
    adoptMapExport({ ...inl, nodes: inl.nodes.map(adaptNode) });
    return { source: "inline", engineVersion: inl.engine_version || null, count: inl.nodes.length };
  }
  // 2. fetched export (only meaningful over http; file:// will throw → fallback)
  try {
    const res = await fetch(`${import.meta.env.BASE_URL}data.json`, { cache: "no-store" });
    if (!res.ok) return { source: "baked" };
    const json = await res.json();
    if (!json || !Array.isArray(json.nodes) || json.nodes.length === 0) return { source: "baked" };
    adoptMapExport({ ...json, nodes: json.nodes.map(adaptNode) });
    return {
      source: "engine", engineVersion: json.engine_version || null, count: json.nodes.length,
    };
  } catch {
    return { source: "baked" };
  }
}

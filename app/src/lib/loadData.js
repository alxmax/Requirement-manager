// implements: REQ-VIEWER-007
/* Bridge between the reqmap engine and the app.
 *
 * The engine's `export` command writes `requirements/_map.json` in a
 * {engine_version, nodes, edges, todos} shape. `npm run sync` copies it to
 * `public/data.json`. At startup loadData() fetches it and adapts each node to
 * the app's requirement shape; on any miss it leaves the baked fallback in
 * place, so the app always renders. */

import { setRegistry, setRepo, setTodos } from "./data.js";

/** engine node ({...used_by, acc, accept}) → app requirement ({...usedBy, gwt}). */
export function adaptNode(n) {
  const acc = Array.isArray(n.acc) ? n.acc : [];
  // the engine always emits a string id, but adaptNode is the trust boundary for
  // any external _map.json — guard it so a malformed node can't throw here
  const id = typeof n.id === "string" ? n.id : String(n.id ?? "");
  return {
    id,
    area: n.area || (id.includes("-") ? id.split("-")[0] : id),
    title: n.title || id,
    layer: n.layer || "feature",
    status: n.status || "draft",
    intent: n.intent || "",
    contract: Array.isArray(n.contract) ? n.contract : [],
    acc,
    // Raw acceptance text: the labelled Given/When/Then block as authored, rendered
    // line for line. `acc` carries the SAME criteria folded to one line each (for
    // search and counting), so gating this on `acc` being empty meant that the day
    // the engine learned to parse the block form (v2.29.0) every criterion silently
    // collapsed into a run-on line. Prefer the authored shape whenever it exists.
    gwt: typeof n.accept === "string" && n.accept.trim() ? n.accept : undefined,
    members: Array.isArray(n.members) ? n.members : [],
    deps: Array.isArray(n.deps) ? n.deps : [],
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
    i18n: (n.i18n && typeof n.i18n === "object") ? n.i18n : null,
  };
}

/** Data source precedence, all non-throwing:
 *  1. window.__REQMAP_DATA__  — inlined by the engine into the self-contained
 *     _map.html viewer (double-click, no server).
 *  2. ./data.json (or _map.json) — fetched when served over http (dev / preview).
 *  3. the baked fallback dataset already in data.js.
 */
export async function loadData() {
  // 1. inlined single-file viewer
  const inl = typeof window !== "undefined" ? window.__REQMAP_DATA__ : null;
  if (inl && Array.isArray(inl.nodes) && inl.nodes.length) {
    setRegistry(inl.nodes.map(adaptNode));
    setRepo(inl.repo);
    setTodos(inl.todos || []);
    return { source: "inline", engineVersion: inl.engine_version || null, count: inl.nodes.length };
  }
  // 2. fetched export (only meaningful over http; file:// will throw → fallback)
  try {
    const res = await fetch(`${import.meta.env.BASE_URL}data.json`, { cache: "no-store" });
    if (!res.ok) return { source: "baked" };
    const json = await res.json();
    if (!json || !Array.isArray(json.nodes) || json.nodes.length === 0) return { source: "baked" };
    setRegistry(json.nodes.map(adaptNode));
    setRepo(json.repo);
    setTodos(json.todos || []);
    return { source: "engine", engineVersion: json.engine_version || null, count: json.nodes.length };
  } catch {
    return { source: "baked" };
  }
}

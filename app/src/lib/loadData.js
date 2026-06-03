/* Bridge between the reqmap engine and the app.
 *
 * The engine's `export` command writes `requirements/_map.json` in a
 * {engine_version, nodes, edges} shape. `npm run sync` copies it to
 * `public/data.json`. At startup loadData() fetches it and adapts each node to
 * the app's requirement shape; on any miss it leaves the baked fallback in
 * place, so the app always renders. */

import { setRegistry } from "./data.js";

/** engine node ({...used_by, acc, accept}) → app requirement ({...usedBy, gwt}). */
export function adaptNode(n) {
  const acc = Array.isArray(n.acc) ? n.acc : [];
  return {
    id: n.id,
    area: n.area || (n.id.includes("-") ? n.id.split("-")[0] : n.id),
    title: n.title || n.id,
    layer: n.layer || "feature",
    status: n.status || "draft",
    intent: n.intent || "",
    contract: Array.isArray(n.contract) ? n.contract : [],
    acc,
    // raw acceptance text (Given/When/Then blocks) when no bullet list exists
    gwt: acc.length === 0 && n.accept ? n.accept : undefined,
    members: Array.isArray(n.members) ? n.members : [],
    deps: Array.isArray(n.deps) ? n.deps : [],
    usedBy: Array.isArray(n.used_by) ? n.used_by : [],
    risks: Array.isArray(n.risks) ? n.risks : [],
  };
}

/** Try the engine export; replace the registry when present. Never throws. */
export async function loadData() {
  try {
    const res = await fetch(`${import.meta.env.BASE_URL}data.json`, { cache: "no-store" });
    if (!res.ok) return { source: "baked" };
    const json = await res.json();
    if (!json || !Array.isArray(json.nodes) || json.nodes.length === 0) return { source: "baked" };
    setRegistry(json.nodes.map(adaptNode));
    return { source: "engine", engineVersion: json.engine_version || null, count: json.nodes.length };
  } catch {
    return { source: "baked" };
  }
}

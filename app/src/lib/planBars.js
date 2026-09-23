// implements: ARCH-VIEWER-007
/** Explicit planning bars, from `_planning.json`'s `bars` list.
 *
 *  A second path used to mint "ghost" bars from `milestones[].items[]`,
 *  dating each two weeks before its milestone's `due`. It was deleted
 *  2026-09-14: every milestone in the corpus carried `items: []`, so
 *  the branch — a third of this file — ran over nothing on every
 *  render, and a roadmap item that wants a bar says so in `bars`
 *  already. Restoring it means restoring a second way to author the
 *  same object, which is what the plan's own audit refused
 *  (docs/plan-source-audit.html). */

function fallbackLane(planning) {
  const lanes = planning?.lanes;
  if (Array.isArray(lanes) && lanes[0]) return lanes[0];
  return "Implementations";
}

/** @returns {object[]} bars with ISO start/end (not yet indexed to the
 *  chart origin) */
export function buildPlanBars(planning) {
  const out = [];
  const seen = new Set();
  const lane = fallbackLane(planning);

  const push = (bar) => {
    const key =
      `${bar.lane}|${bar.title}|${bar.start}|${bar.end}`.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    out.push(bar);
  };

  (planning?.bars || []).forEach((b, i) => {
    if (!b?.title || !b.start) return;
    push({
      key: b.id || `bar-${i}`,
      title: b.title,
      lane: b.lane || lane,
      milestone: b.milestone || null,
      start: b.start,
      end: b.end || b.start,
      progress: b.progress,
      reqId: b.req || b.reqId || null,
      kind: "planned",
    });
  });

  return out;
}

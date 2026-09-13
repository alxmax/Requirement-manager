// implements: ARCH-VIEWER-007
/** Explicit planning bars, plus ghost items from milestone `items[]`. */
import { parseIso, isoLocal, addDays } from "./timeline.js";

function msDue(planning, milestone) {
  const due = planning?.milestones?.[milestone]?.due;
  return due && parseIso(due) ? due : null;
}

function fallbackLane(planning) {
  const lanes = planning?.lanes;
  if (Array.isArray(lanes) && lanes[0]) return lanes[0];
  return "Implementations";
}

/** @returns {object[]} bars with ISO start/end (not yet indexed to the chart origin) */
export function buildPlanBars(planning) {
  const out = [];
  const seen = new Set();
  const lane = fallbackLane(planning);

  const push = (bar) => {
    const key = `${bar.lane}|${bar.title}|${bar.start}|${bar.end}`.toLowerCase();
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

  const titled = new Set(out.map((b) => b.title.toLowerCase()));
  Object.entries(planning?.milestones || {}).forEach(([ms, meta]) => {
    const due = msDue(planning, ms);
    if (!due || !Array.isArray(meta.items)) return;
    meta.items.forEach((text, i) => {
      if (typeof text !== "string" || !text.trim()) return;
      if (titled.has(text.toLowerCase())) return;
      const endD = parseIso(due);
      const startD = addDays(endD, -14);
      push({
        key: `item-${ms}-${i}`,
        title: text.trim(),
        lane,
        milestone: ms,
        start: isoLocal(startD),
        end: due,
        kind: "ghost",
      });
    });
  });

  return out;
}

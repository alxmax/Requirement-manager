// implements: ARCH-VIEWER-007
/* What the Versions view shows, computed from the export: one column per version and the
 * items in each. Nothing here renders. */

export function semverCmp(a, b) {
  const num = (v) => v.replace(/^v/i, "").split(".").map((n) => parseInt(n, 10) || 0);
  const pa = num(a), pb = num(b);
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    const d = (pa[i] || 0) - (pb[i] || 0);
    if (d !== 0) return d;
  }
  return 0;
}

export function barVariant(status) {
  if (status === "confirmed")   return "done";
  if (status === "in-progress") return "progress";
  if (status === "draft")       return "draft";
  return "planned";
}

const live = (r) => r.status !== "deprecated";

/* A milestone whose every TODO item shipped (and no requirement cites it) used to have no
   signal at all reaching this Set — the column vanished and the chart jumped straight to
   the next one, reading as a skipped version rather than a finished one. A milestone is
   real once TODO.md groups anything under it, done or not. */
function versionNames(requirements, todos, msMeta, planBars) {
  const names = new Set();
  requirements.forEach((r) => { if (r.milestone && live(r)) names.add(r.milestone); });
  todos.forEach((item) => { if (item.milestone) names.add(item.milestone); });
  Object.keys(msMeta).forEach((ms) => names.add(ms));
  planBars.forEach((bar) => { if (bar?.milestone) names.add(bar.milestone); });
  return Array.from(names).sort(semverCmp);
}

/* Planned work is `bars`, the same list the Plan chart draws (REQ-PLANSTALE-1013's
   "planned set"). A bar whose `req:` or title is already in the column is not listed twice. */
function addPlannedBars(byMs, planBars) {
  planBars.forEach((bar) => {
    if (!bar?.title || !byMs[bar.milestone]) return;
    const col = byMs[bar.milestone];
    const title = bar.title.toLowerCase();
    const dup = col.some((item) =>
      (item.type === "req" && (item.r.id === bar.req || item.r.title.toLowerCase() === title))
      || (item.type === "todo" && item.t.name.toLowerCase() === title));
    if (!dup) col.push({ type: "plan", text: bar.title });
  });
}

/** The Versions view's data: columns, their items, the current and next version, and the
 *  planning-level requirements that carry no milestone. */
export function buildVersions(requirements, todos, targets) {
  const msMeta = targets?.milestones || {};
  const planBars = Array.isArray(targets?.bars) ? targets.bars : [];
  const milestones = versionNames(requirements, todos, msMeta, planBars);
  const byMs = Object.fromEntries(milestones.map((ms) => [ms, []]));
  requirements.filter((r) => r.milestone && live(r))
    .forEach((r) => { if (byMs[r.milestone]) byMs[r.milestone].push({ type: "req", r }); });
  todos.filter((t) => !t.done)
    .forEach((t) => { if (byMs[t.milestone]) byMs[t.milestone].push({ type: "todo", t }); });
  addPlannedBars(byMs, planBars);
  const withStatus = (ms, status) =>
    requirements.some((r) => r.milestone === ms && r.status === status);
  const today = new Date().toISOString().slice(0, 10);
  return {
    milestones, msMeta, byMs,
    current: milestones.find((ms) => withStatus(ms, "in-progress"))
      || [...milestones].reverse().find((ms) => withStatus(ms, "confirmed")),
    /* Unscheduled is a planning bucket, so it holds only what is planned AT the planning
       levels: a `level: code` requirement inherits its parent's milestone. */
    unscheduled: requirements.filter((r) => !r.milestone && live(r) && r.level !== "code"),
    plannedCount: Object.values(byMs).flat().filter((i) => i.type === "plan").length,
    nextDue: milestones.map((ms) => ({ ms, due: msMeta[ms]?.due }))
      .filter((x) => x.due && x.due >= today)
      .sort((a, b) => a.due.localeCompare(b.due))[0],
    maxRows: Math.max(1, ...Object.values(byMs).map((a) => a.length)),
  };
}

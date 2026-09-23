// implements: ARCH-VIEWER-007
/* Where everything on the Plan chart goes, computed once from the export and
 * handed to the components that draw it. Nothing here renders; nothing in
 * the components measures. */
import {
  parseIso, isoLocal, dayIndex, buildMonthBands, buildWeekBands, buildDayBands,
  stackBars,
} from "../../lib/timeline.js";
import { buildPlanBars } from "../../lib/planBars.js";

/* 22px a day, and a floor of 30. At 7px a week drew 43px and was floored to
 * 72 — nearly three days of borrowed room, which is what pushed a bar into
 * its neighbour's week. At 11 a week was 71px of its own; doubled to 22 a
 * month is twice as wide, a week is 148px, a day has room for its `15/9`
 * label written across, and the floor only catches a bar of a single day.
 * Every width on the chart is a multiple of this one constant.
 * implements: REQ-PLANSTACK-1012 */
export const PX = 22;
export const BAR_MIN_W = 30;
export const LABEL_W = 108;
/* 3 lines x 11px x 1.3 = 43px of text, plus the bar's 8px of vertical
 * padding, plus the 6px the row keeps between bars. A row of 50 clipped the
 * third line half-way down its glyphs — the wrap promised three lines and
 * the box only had room for two and a half. */
export const LABEL_LINES = 3;
export const ROW_H = 58;
export const PAD = 10;
export const FLAG_H = 22;
export const MONTH_H = 26;
export const WEEK_H = 16;
export const DAY_H = 16;
export const HEAD_H = FLAG_H + MONTH_H + WEEK_H + DAY_H;
export const BAND_H = ROW_H + PAD * 2;

const tint = (color, pct) =>
  `color-mix(in oklch, ${color} ${pct}%, transparent)`;
export const LANE_TONE = [
  { bg: tint("var(--cov-tested)", 22), fg: "var(--cov-tested)",
    edge: "var(--cov-tested)" },
  { bg: tint("var(--amber-600)", 20), fg: "var(--amber-700)",
    edge: "var(--amber-600)" },
  { bg: "var(--indigo-tint)", fg: "var(--indigo-500)",
    edge: "var(--indigo-400)" },
  { bg: tint("var(--fg-faint)", 14), fg: "var(--fg-muted)",
    edge: "var(--fg-faint)" },
];

function monthStart(d) {
  return new Date(d.getFullYear(), d.getMonth(), 1, 12, 0, 0);
}

function monthEnd(d) {
  return new Date(d.getFullYear(), d.getMonth() + 1, 0, 12, 0, 0);
}

function indexBars(raw, origin) {
  return raw.map((b) => {
    const a = parseIso(b.start), z = parseIso(b.end || b.start);
    if (!a || !z) return null;
    const startIdx = dayIndex(origin, a);
    const endIdx = dayIndex(origin, z);
    if (endIdx < startIdx) return null;
    return { ...b, startIdx, endIdx };
  }).filter(Boolean);
}

/* The drawn box of a bar, in one place. The renderer used to compute this
   inline and `stackBars` compared dates, so the two disagreed about what
   "overlapping" meant and short neighbours were painted on top of each
   other (REQ-PLANSTACK-1012). */
export function extent(b) {
  return {
    left: b.startIdx * PX + 3,
    width: Math.max((b.endIdx - b.startIdx + 1) * PX - 6, BAR_MIN_W),
  };
}

const dayCentre = (idx) => idx * PX + PX / 2;

/** The chart's first and last day: whole months around every dated thing
 *  and today. Release dates extend the range like any other dated thing: a
 *  cadence running past the last bar — `until: 2026-12-31` with nothing
 *  scheduled in December — otherwise emits dates the chart drops, and the
 *  engine says a release lands where the chart shows none. */
function chartRange(raw, dueList, past, releases, todayD) {
  const dates = [
    ...raw.flatMap((b) => [parseIso(b.start), parseIso(b.end)]),
    ...dueList.map((d) => d.at),
    ...past.flatMap((h) => [parseIso(h.first), parseIso(h.last)]),
    ...releases.map(parseIso),
    todayD,
  ].filter(Boolean);
  const origin = monthStart(
    new Date(Math.min(...dates.map((d) => d.getTime()))),
  );
  const end = monthEnd(new Date(Math.max(...dates.map((d) => d.getTime()))));
  return { origin, totalDays: dayIndex(origin, end) + 1 };
}

/* Where each guide ends, measured from the bottom of the ruler: the top of
 * the lane it points into, plus the item's own offset inside that lane.
 * `subRow` was set by the `stackBars` call that sized the lanes. A guide
 * runs from its day to its bar or version and stops there.
 * implements: REQ-PLANSTACK-1012 */
function buildGuides(lay) {
  const laneTop = {};
  lay.lanes.reduce((top, ln, i) => {
    laneTop[ln] = top; return top + lay.heights[i];
  }, lay.pastRows.length > 0 ? BAND_H : 0);
  const barGuides = lay.bars.filter((b) => laneTop[b.lane] != null)
    .flatMap((b) => {
      const to = laneTop[b.lane] + PAD + (b.subRow || 0) * ROW_H;
      return [
        { key: `start-${b.key}`, kind: "start", x: dayCentre(b.startIdx), to },
        { key: `end-${b.key}`, kind: "end", x: dayCentre(b.endIdx), to },
      ];
    });
  const releaseH = lay.heights[lay.lanes.indexOf(lay.releaseLane)];
  const versionGuides = (lay.releaseLane ? lay.flags : []).map((f) => ({
    key: `version-${f.ms}`, kind: "version", x: dayCentre(f.idx),
    to: laneTop[lay.releaseLane] + releaseH / 2 - 11,
  }));
  return [...barGuides, ...versionGuides];
}

/** Everything the chart draws, positioned; `null` when the plan holds
 *  nothing dated. A cadence with no bars is still a calendar, and a repo
 *  that has planned nothing is the one that needs one — `init` seeds it
 *  for exactly that (REQ-PLANHORIZON-1010). */
export function layoutPlan(planning, history, locale) {
  const todayD = parseIso(isoLocal(new Date()));
  const raw = buildPlanBars(planning);
  const releases = planning?.releases || [];
  const dueList = Object.entries(planning?.milestones || {})
    .filter(([, m]) => m?.due && parseIso(m.due))
    .map(([ms, m]) => (
      { ms, due: m.due, label: m.label, at: parseIso(m.due) }
    ));
  /* What already shipped, one row per calendar month, straight off
   * CHANGELOG.md via the engine, on the same timeline as the plan.
   * implements: REQ-HISTORY-1081 */
  const past = (history || [])
    .filter((h) => parseIso(h.first) && parseIso(h.last));
  if (!raw.length && !dueList.length && !past.length && !releases.length) {
    return null;
  }

  const { origin, totalDays } =
    chartRange(raw, dueList, past, releases, todayD);
  const bars = indexBars(raw, origin);
  let lanes = Array.isArray(planning?.lanes) && planning.lanes.length
    ? [...planning.lanes] : [...new Set(bars.map((b) => b.lane))];
  if (!lanes.length) lanes = ["Implementations"];
  const byLane = Object.fromEntries(
    lanes.map((ln) => [ln, bars.filter((b) => b.lane === ln)]),
  );
  const lay = {
    totalDays, chartW: totalDays * PX, bars, lanes, byLane,
    heights: lanes.map((ln) =>
      Math.max(stackBars(byLane[ln] || [], extent), 1) * ROW_H + PAD * 2),
    pastRows: past.map((h) => {
      const startIdx = dayIndex(origin, parseIso(h.first));
      return {
        ...h, startIdx,
        endIdx: Math.max(dayIndex(origin, parseIso(h.last)), startIdx),
      };
    }),
    months: buildMonthBands(origin, totalDays, locale),
    weeks: buildWeekBands(origin, totalDays),
    days: buildDayBands(origin, totalDays),
    todayIdx: todayD ? dayIndex(origin, todayD) : -1,
    flags: dueList.map((d) => ({ ...d, idx: dayIndex(origin, d.at) })),
    /* Release cadence: the ENGINE computed these dates (targets.py) and
     * the chart only places them, so the CLI and the chart cannot
     * disagree about when a release lands.
     * implements: REQ-PLANCADENCE-1000 */
    releaseIdx: releases
      .map((iso) => ({ iso, idx: dayIndex(origin, parseIso(iso)) }))
      .filter((r) => r.idx >= 0 && r.idx < totalDays),
    /* A version is a release, so it is drawn in the lane the cadence
     * names; with no such lane the pill stays on the ruler, where a plan
     * without a cadence has always shown it. */
    releaseLane: lanes.includes(planning?.cadence?.lane)
      ? planning.cadence.lane : null,
    loc: locale === "ro" ? "ro-RO" : "en-GB",
  };
  lay.guides = buildGuides(lay);
  return lay;
}

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
/* A shipped release is one line: its version. Shorter than a plan bar,
 * which wraps three lines of a title. The headline opens in the note. */
export const SHIP_H = 32;

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

/* 11px on the viewer's UI font: a character is about 5.2px, and the
 * bar's padding, gap and border add 22. A wider guess left a gap after
 * the words, and with a release on every line that gap pushed the next
 * block down. implements: REQ-HISTORY-1081 */
export const LABEL_CHAR = 5.2;
const LABEL_PAD = 22;

export function releaseLabelWidth(version, headline) {
  const text = headline ? `${version} ${headline}` : String(version || "");
  return Math.ceil(text.length * LABEL_CHAR) + LABEL_PAD;
}

export function shipExtent(b) {
  const days = Math.max((b.endIdx - b.startIdx + 1) * PX, PX);
  return {
    left: b.startIdx * PX,
    width: Math.max(days, b.labelW || 0),
  };
}

const dayCentre = (idx) => idx * PX + PX / 2;

/* A version pill is 68px in its lane, three days and more at PX 22, so two
 * milestones due within that of each other were drawn on top of one another
 * and one simply vanished. A consumer merged two milestones to get the
 * hidden one back — the chart had changed the plan. Pills now take rows the
 * way bars do; the ruler, which has one row, joins them into one pill.
 * implements: REQ-VIEWER-1087 */
export const PILL_W = 68;
export const PILL_ROW = 26;
const PILL_DAYS = Math.ceil(PILL_W / PX);

export function stackFlags(flags) {
  const ends = [];
  return [...flags].sort((a, b) => a.idx - b.idx).map((f) => {
    let row = ends.findIndex((end) => end <= f.idx);
    if (row < 0) { row = ends.length; ends.push(0); }
    ends[row] = f.idx + PILL_DAYS;
    return { ...f, row };
  });
}

/** Ruler pills: flags closer than a pill's width become one, naming each. */
export function clusterFlags(flags) {
  const out = [];
  for (const f of [...flags].sort((a, b) => a.idx - b.idx)) {
    const last = out[out.length - 1];
    if (last && f.idx - last.idx < PILL_DAYS) last.members.push(f);
    else out.push({ idx: f.idx, members: [f] });
  }
  return out.map((c) => ({
    ...c, ms: c.members.map((m) => m.ms).join(" · "),
  }));
}

/** The top of a version pill in a lane `laneH` tall, when `rows` rows of
 *  pills share it: one row sits in the middle, as it always has. */
export function pillTop(laneH, row, rows) {
  return laneH / 2 - 11 + (row - (rows - 1) / 2) * PILL_ROW;
}

/** The chart's first and last day: whole months around every dated thing
 *  and today. Release dates extend the range like any other dated thing: a
 *  cadence running past the last bar — `until: 2026-12-31` with nothing
 *  scheduled in December — otherwise emits dates the chart drops, and the
 *  engine says a release lands where the chart shows none. */
function chartRange(raw, dueList, shipped, releases, todayD) {
  const dates = [
    ...raw.flatMap((b) => [parseIso(b.start), parseIso(b.end)]),
    ...dueList.map((d) => d.at),
    ...shipped.flatMap((h) => [parseIso(h.start), parseIso(h.end)]),
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
  }, lay.pastH || 0);
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
    to: laneTop[lay.releaseLane] + pillTop(releaseH, f.row, lay.flagRows),
  }));
  return [...barGuides, ...versionGuides];
}

function verParts(version) {
  return String(version).replace(/^v/i, "").split(".")
    .map((p) => parseInt(p, 10) || 0);
}

/** `v7.21.10` and `v7.21.0` are one line of work. A version that is not
 *  `major.minor` stays on its own. implements: REQ-HISTORY-1081 */
export function minorKey(version) {
  const body = String(version || "").replace(/^v/i, "");
  if (!/^\d+\.\d+/.test(body)) return null;
  const [major, minor] = verParts(version);
  return `v${major}.${minor}`;
}

function cmpVer(a, b) {
  const pa = verParts(a), pb = verParts(b);
  const n = Math.max(pa.length, pb.length);
  for (let i = 0; i < n; i++) {
    const d = (pa[i] || 0) - (pb[i] || 0);
    if (d) return d;
  }
  return 0;
}

/** Patch releases of one minor version become one block, `vX.Y.x`,
 *  spanning every commit of that line. A release with no sibling keeps
 *  its own version. implements: REQ-HISTORY-1081 */
export function groupPatchReleases(releases) {
  const buckets = new Map();
  for (const r of releases) {
    const key = minorKey(r.version) || `one:${r.version}`;
    const list = buckets.get(key);
    if (list) list.push(r);
    else buckets.set(key, [r]);
  }
  const out = [];
  for (const [key, list] of buckets) {
    if (list.length === 1) { out.push(list[0]); continue; }
    const members = list.slice().sort((a, b) => cmpVer(a.version, b.version));
    const start = members.reduce((s, r) => (r.start < s ? r.start : s),
      members[0].start);
    const end = members.reduce((s, r) => (r.end > s ? r.end : s),
      members[0].end);
    const version = `${key}.x`;
    out.push({
      version, headline: "", date: members[members.length - 1].date,
      month: members[0].month, start, end, members,
    });
  }
  return out.sort((a, b) => (a.start < b.start ? -1 : a.start > b.start ? 1 : 0));
}

/** Releases that start on the same day are one block, labelled from the
 *  lowest version to the highest: `v5.10.x-v6.3.0`. A patch group already
 *  folded to `vX.Y.x` counts as one end of that range.
 *  implements: REQ-HISTORY-1081 */
export function groupSameStart(releases) {
  const buckets = new Map();
  for (const r of releases) {
    const list = buckets.get(r.start);
    if (list) list.push(r);
    else buckets.set(r.start, [r]);
  }
  const out = [];
  for (const list of buckets.values()) {
    if (list.length === 1) { out.push(list[0]); continue; }
    const sorted = list.slice().sort((a, b) => cmpVer(a.version, b.version));
    const end = sorted.reduce((s, r) => (r.end > s ? r.end : s), sorted[0].end);
    const members = sorted
      .flatMap((r) => r.members || [r])
      .sort((a, b) => cmpVer(a.version, b.version));
    const version = `${sorted[0].version}-${sorted[sorted.length - 1].version}`;
    out.push({
      version, headline: "", date: members[members.length - 1].date,
      month: sorted[0].month, start: sorted[0].start, end, members,
    });
  }
  return out.sort((a, b) => (a.start < b.start ? -1 : a.start > b.start ? 1 : 0));
}

/* One block per release, then folded by minor version. `first_commit` /
 * `last_commit` are the work; without them the changelog date is a single
 * day. implements: REQ-HISTORY-1081 */
export function shippedReleases(history) {
  const out = [];
  for (const h of history || []) {
    const entries = Array.isArray(h.entries) && h.entries.length
      ? h.entries
      : (h.versions || []).map((version) => ({
          version,
          date: h.last || h.first,
          headline: version === h.landmark ? (h.headline || "") : "",
        }));
    for (const e of entries) {
      const start = e.first_commit || e.date || h.first;
      const end = e.last_commit || e.date || start;
      if (!e.version || !parseIso(start) || !parseIso(end)) continue;
      out.push({
        version: e.version, headline: e.headline || "",
        body: e.body || "",
        date: e.date || end, month: h.month, start, end,
      });
    }
  }
  return groupSameStart(groupPatchReleases(out));
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
  const shipped = shippedReleases(history);
  if (!raw.length && !dueList.length && !shipped.length
      && !releases.length) {
    return null;
  }

  const { origin, totalDays } =
    chartRange(raw, dueList, shipped, releases, todayD);
  const bars = indexBars(raw, origin);
  let lanes = Array.isArray(planning?.lanes) && planning.lanes.length
    ? [...planning.lanes] : [...new Set(bars.map((b) => b.lane))];
  if (!lanes.length) lanes = ["Implementations"];
  const byLane = Object.fromEntries(
    lanes.map((ln) => [ln, bars.filter((b) => b.lane === ln)]),
  );
  /* A version is a release, so it is drawn in the lane the cadence
   * names; with no such lane the pill stays on the ruler, where a plan
   * without a cadence has always shown it. */
  const releaseLane = lanes.includes(planning?.cadence?.lane)
    ? planning.cadence.lane : null;
  const flags = stackFlags(
    dueList.map((d) => ({ ...d, idx: dayIndex(origin, d.at) })));
  const flagRows = flags.reduce((n, f) => Math.max(n, f.row + 1), 1);
  /* A row is shared until the drawn boxes meet. The box is the work's
   * dates, widened to the label when the words are longer than the work,
   * so a one-day release stays readable and does not cover its neighbour. */
  const pastBars = shipped.map((h) => {
    const startIdx = dayIndex(origin, parseIso(h.start));
    const endIdx = Math.max(dayIndex(origin, parseIso(h.end)), startIdx);
    return {
      ...h, startIdx, endIdx, key: `rel-${h.version}`,
      labelW: releaseLabelWidth(h.version,
        h.members && !String(h.version).includes("-v")
          ? `${h.members.length} releases` : ""),
    };
  });
  /* Same start and end keep this order: `stackBars` sorts by those two
   * and is stable, so one day stacks lowest version first. */
  pastBars.sort((a, b) =>
    a.startIdx - b.startIdx || a.endIdx - b.endIdx
    || cmpVer(a.version, b.version));
  const pastRowCount = pastBars.length ? stackBars(pastBars, shipExtent) : 0;
  const pastH = pastBars.length ? pastRowCount * SHIP_H + PAD * 2 : 0;
  const chartW = pastBars.reduce((max, b) => {
    const box = shipExtent(b);
    return Math.max(max, box.left + box.width);
  }, totalDays * PX);
  const lay = {
    totalDays, chartW, bars, lanes, byLane,
    heights: lanes.map((ln) => Math.max(
      Math.max(stackBars(byLane[ln] || [], extent), 1) * ROW_H + PAD * 2,
      ln === releaseLane ? flagRows * PILL_ROW + PAD * 2 : 0)),
    pastBars, pastH,
    months: buildMonthBands(origin, totalDays, locale),
    weeks: buildWeekBands(origin, totalDays),
    days: buildDayBands(origin, totalDays),
    todayIdx: todayD ? dayIndex(origin, todayD) : -1,
    flags, flagRows, rulerFlags: clusterFlags(flags),
    /* Release cadence: the ENGINE computed these dates (targets.py) and
     * the chart only places them, so the CLI and the chart cannot
     * disagree about when a release lands.
     * implements: REQ-PLANCADENCE-1000 */
    releaseIdx: releases
      .map((iso) => ({ iso, idx: dayIndex(origin, parseIso(iso)) }))
      .filter((r) => r.idx >= 0 && r.idx < totalDays),
    releaseLane,
    loc: locale === "ro" ? "ro-RO" : "en-GB",
  };
  lay.guides = buildGuides(lay);
  return lay;
}

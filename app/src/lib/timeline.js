// implements: ARCH-VIEWER-007
/** Calendar helpers for the planning Gantt (day-index layout, month/week headers). */

export const PX_PER_DAY = 5;
export const LANE_LABEL_W = 148;
export const LANE_ROW_H = 28;
export const LANE_PAD = 14;

export function parseIso(s) {
  if (typeof s !== "string") return null;
  const m = s.trim().match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!m) return null;
  return new Date(+m[1], +m[2] - 1, +m[3], 12, 0, 0);
}

export function isoLocal(d) {
  const y = d.getFullYear();
  const mo = String(d.getMonth() + 1).padStart(2, "0");
  const da = String(d.getDate()).padStart(2, "0");
  return `${y}-${mo}-${da}`;
}

export function dayIndex(origin, d) {
  return Math.round((d - origin) / 86400000);
}

export function addDays(d, n) {
  const out = new Date(d);
  out.setDate(out.getDate() + n);
  return out;
}

/** Month bands covering [origin .. origin+totalDays). */
export function buildMonthBands(origin, totalDays, locale) {
  const loc = locale === "ro" ? "ro-RO" : "en-GB";
  const bands = [];
  let i = 0;
  while (i < totalDays) {
    const d = addDays(origin, i);
    const label = d.toLocaleDateString(loc, { month: "short", year: "numeric" });
    const month = d.getMonth();
    let span = 1;
    while (i + span < totalDays && addDays(origin, i + span).getMonth() === month) span++;
    bands.push({ label, start: i, span });
    i += span;
  }
  return bands;
}

/** ISO-8601 week number: weeks start Monday, and week 1 is the one holding the year's
 *  first Thursday. Reading the year off that Thursday is what makes the turn of the year
 *  come out right — 1 January can belong to W52 or W53 of the year before. */
export function isoWeek(d) {
  const t = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  t.setDate(t.getDate() + 3 - ((t.getDay() + 6) % 7));        // this week's Thursday
  const jan4 = new Date(t.getFullYear(), 0, 4);               // always in week 1
  jan4.setDate(jan4.getDate() + 3 - ((jan4.getDay() + 6) % 7));
  return 1 + Math.round((t - jan4) / (7 * 86400000));
}

/** Week bands over [origin .. origin+totalDays), labelled with the ISO week of the year
 *  (W23, W24, …) and aligned to real Monday boundaries — so the first band is short
 *  whenever the range does not start on a Monday and every later one is exactly 7 days.
 *  Numbering from the range start instead would give the same calendar week a different
 *  number in two charts, which is the one thing a week label must never do. */
export function buildWeekBands(origin, totalDays) {
  const bands = [];
  let i = 0;
  while (i < totalDays) {
    const d = addDays(origin, i);
    const span = Math.min(7 - ((d.getDay() + 6) % 7), totalDays - i);
    bands.push({ label: `W${isoWeek(d)}`, start: i, span });
    i += span;
  }
  return bands;
}

/** One entry per day on the chart, labelled `day/month` ("15/9"), with its weekday so a
 *  weekend can be told apart. A week band says which week; this says which day, which is
 *  what a reader needs to place a one-day bar or a Friday release.  implements: REQ-PLANDAYS-1021 */
export function buildDayBands(origin, totalDays) {
  const bands = [];
  for (let i = 0; i < totalDays; i++) {
    const d = addDays(origin, i);
    bands.push({ start: i, label: `${d.getDate()}/${d.getMonth() + 1}`,
                 weekend: d.getDay() === 0 || d.getDay() === 6 });
  }
  return bands;
}

export function overlaps(a, b) {
  return a.startIdx <= b.endIdx && b.startIdx <= a.endIdx;
}

/** Assign sub-rows inside a lane so overlapping bars stack vertically. */
/** Assign each bar a sub-row so that none is drawn over another, and return the row
 *  count. Pass `extent` to compare what is DRAWN rather than what is scheduled.
 *
 *  Without it this compared dates, and a bar is not drawn at its date width: the chart
 *  floors a bar at a readable minimum, so a week (7 x 7px - 6 = 43px) renders as 72px.
 *  Two bars a week apart start 49px apart, so they do not overlap as dates, land on one
 *  row, and are then painted 23px on top of each other — the label of the first
 *  disappearing under the second. The row chooser has to know the width the renderer
 *  will use.  implements: REQ-PLANSTACK-1012 */
export function stackBars(bars, extent) {
  const sorted = [...bars].sort((a, b) => a.startIdx - b.startIdx || a.endIdx - b.endIdx);
  const clash = extent
    ? (a, b) => {
        const pa = extent(a), pb = extent(b);
        return pa.left < pb.left + pb.width && pb.left < pa.left + pa.width;
      }
    : overlaps;
  const rows = [];
  for (const bar of sorted) {
    let row = 0;
    for (; row < rows.length; row++) {
      if (!rows[row].some((b) => clash(b, bar))) break;
    }
    if (row === rows.length) rows.push([]);
    bar.subRow = row;
    rows[row].push(bar);
  }
  return rows.length || 1;
}

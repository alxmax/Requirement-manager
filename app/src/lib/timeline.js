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

/** Seven-day week ticks from the range start (W1, W2, …). */
export function buildWeekBands(totalDays) {
  const bands = [];
  for (let i = 0; i < totalDays; i += 7) {
    bands.push({ label: `W${Math.floor(i / 7) + 1}`, start: i, span: Math.min(7, totalDays - i) });
  }
  return bands;
}

export function overlaps(a, b) {
  return a.startIdx <= b.endIdx && b.startIdx <= a.endIdx;
}

/** Assign sub-rows inside a lane so overlapping bars stack vertically. */
export function stackBars(bars) {
  const sorted = [...bars].sort((a, b) => a.startIdx - b.startIdx || a.endIdx - b.endIdx);
  const rows = [];
  for (const bar of sorted) {
    let row = 0;
    for (; row < rows.length; row++) {
      if (!rows[row].some((b) => overlaps(b, bar))) break;
    }
    if (row === rows.length) rows.push([]);
    bar.subRow = row;
    rows[row].push(bar);
  }
  return rows.length || 1;
}

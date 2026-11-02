// implements: REQ-BUGS-1129
/* What the register says over time. Everything here follows from the dates a
 * row already holds; a dismissal ("not a bug") leaves the open list but is not
 * a fix, so it counts in neither the fixes nor the time to fix. */

const NOT_A_BUG = "not a bug";
export const isFix = (row) => row.version !== NOT_A_BUG;
const DAY = 86400000;
const stamp = (date) => Date.parse(`${date}T00:00:00Z`);

/** The Monday of `date`'s week, as YYYY-MM-DD. */
export function weekOf(date) {
  const at = new Date(stamp(date));
  at.setUTCDate(at.getUTCDate() - ((at.getUTCDay() + 6) % 7));
  return at.toISOString().slice(0, 10);
}

/** [{week, found, fixed, open}] oldest first, for the last `limit` weeks with
 * any activity. `open` counts every bug found and not closed by that week. */
export function weekly(open, fixed, limit = 12) {
  const weeks = {};
  const row = (week) => (weeks[week] = weeks[week]
    || { week, found: 0, fixed: 0, closed: 0 });
  // A row with no found date never entered the count, so it cannot leave it.
  [...open, ...fixed].filter((b) => b.date)
    .forEach((b) => { row(weekOf(b.date)).found += 1; });
  fixed.filter((b) => b.fixed).forEach((b) => {
    const week = row(weekOf(b.fixed));
    if (b.date) week.closed += 1;
    if (isFix(b)) week.fixed += 1;
  });
  let running = 0;
  const all = Object.values(weeks).sort((a, b) => a.week.localeCompare(b.week))
    .map(({ week, found, fixed: fixes, closed }) => {
      running += found - closed;
      return { week, found, fixed: fixes, open: Math.max(0, running) };
    });
  return all.slice(-limit);
}

const median = (values) => {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid]
    : (sorted[mid - 1] + sorted[mid]) / 2;
};

/** [[name, median days, count]] per value of `key`, over real fixes with both
 * dates. */
export function medianDays(fixed, key) {
  const groups = {};
  fixed.filter((b) => isFix(b) && b.date && b.fixed).forEach((b) => {
    const days = Math.max(0, (stamp(b.fixed) - stamp(b.date)) / DAY);
    (groups[b[key] || "—"] = groups[b[key] || "—"] || []).push(days);
  });
  return Object.keys(groups).sort()
    .map((name) => [name, median(groups[name]), groups[name].length]);
}

/** The rows closed in the week starting `week`. */
export const fixedIn = (fixed, week) => fixed.filter(
  (b) => b.fixed && weekOf(b.fixed) === week);

/** One page of `items`. A page past the end, left by a shorter list, is the
 * last one. */
export function pageOf(items, page, size) {
  const pages = Math.max(1, Math.ceil(items.length / size));
  const at = Math.min(page, pages - 1);
  return { rows: items.slice(at * size, (at + 1) * size), page: at, pages };
}

/** The rows closed in the last `days` days up to `today`. */
export const fixedSince = (fixed, today, days = 30) => fixed.filter(
  (b) => b.fixed && stamp(today) - stamp(b.fixed) <= days * DAY);

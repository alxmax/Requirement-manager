// implements: REQ-BUGS-1154
/* The weekly table as a trend: what was fixed so far against what is still
 * open, on one axis from 0. The table above stays the data view; the chart
 * never names a line by colour alone (legend, end labels, tooltip). */
import { useEffect, useRef, useState } from "react";
import { useI18n } from "../../lib/i18n.jsx";
import { openPeak, spreadLabels } from "../../lib/bugStats.js";

const H = 360;
const PAD = { l: 52, r: 128, t: 14, b: 30 };
const NARROW = 420;
const LINES = [
  { key: "fixedSoFar", name: "Fixed", end: "{n} fixed", color: "var(--chart-fixed)" },
  { key: "open", name: "Still open", end: "{n} still open", color: "var(--chart-open)" },
  { key: "foundSoFar", name: "Total found", end: "{n} total", color: "var(--accent)",
    optional: true },
];

/** Round axis steps (1, 2, 2.5 or 5 times a power of ten) from 0 to at least
 * `max`, about four of them: 349 reads 0, 100, 200, 300, 400. */
export function niceTicks(max, count = 4) {
  const raw = Math.max(1, max) / count;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw);
  const whole = step >= 1 ? step : 1;
  const top = Math.ceil(Math.max(1, max) / whole) * whole;
  return Array.from({ length: Math.round(top / whole) + 1 }, (_, i) => i * whole);
}

/** The rendered content width of `ref`, `fallback` until it is measured. */
function useWidth(ref, fallback) {
  const [width, setWidth] = useState(fallback);
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof ResizeObserver === "undefined") return undefined;
    const ro = new ResizeObserver(([e]) => setWidth(Math.round(e.contentRect.width)));
    ro.observe(el);
    return () => ro.disconnect();
  }, [ref]);
  return width;
}

/** One entry per line shown, then the box that adds the total. */
function Legend({ shown, total, onTotal }) {
  const { t } = useI18n();
  return (
    <div className="bug-chart-legend">
      {shown.map((l) => (
        <span key={l.key}><i style={{ background: l.color }} />{t(l.name)}</span>
      ))}
      <label className="bug-chart-total"><input type="checkbox" checked={total}
        onChange={(e) => onTotal(e.target.checked)} />{t("Show total")}</label>
    </div>
  );
}

/** A full-height column per week: hover, focus and click target, and the
 * week's accessible name. A button only when the week can be picked. */
function WeekTargets({ weeks, colW, chosen, pickable, dateOf, onHover, onSelect }) {
  const { t } = useI18n();
  return weeks.map((w, i) => (
    <rect key={w.week} className="bug-chart-hit" x={PAD.l + colW * i} y={0}
      width={colW} height={H} tabIndex={0} role={pickable ? "button" : "img"}
      aria-pressed={pickable ? chosen === w.week : undefined}
      aria-label={t("Up to {date}: {fixed} fixed, {open} still open",
        { date: dateOf(w.week), fixed: w.fixedSoFar, open: w.open })}
      onMouseEnter={() => onHover(i)} onFocus={() => onHover(i)}
      onMouseLeave={() => onHover(null)} onBlur={() => onHover(null)}
      onClick={() => onSelect(w)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect(w); }
      }} />
  ));
}

const SUMMARY = "{fixed} fixed, {open} still open. Open peaked at {peak} on {date}.";
const SUMMARY_DOWN = "{fixed} fixed, {open} still open. Open peaked at {peak} on {date} "
  + "and has come down since.";

/** `weeks` from `weekly()`; `chosen`/`pick`/`canPick` are the table's own
 * week selection, so a click here and a click there are the same choice.
 * Without `pick` (the Report) a week only shows its tooltip; `filter` sits
 * under the title. `dateOf` writes a full date, `dayOf` a day and month. */
export function BugChart({ weeks, chosen, pick = null, canPick = () => false,
  dateOf, dayOf = (d) => dateOf(d).slice(0, 5), filter = null }) {
  const { t } = useI18n();
  const box = useRef(null);
  const width = Math.max(260, useWidth(box, 720));
  const [total, setTotal] = useState(false);
  const [hover, setHover] = useState(null);
  const title = <div className="bug-chart-title">{t("Fixed and still open")}</div>;
  // A filter that leaves no week keeps its buttons, or it could not be undone.
  if (!weeks.length) {
    return filter && <div className="bug-chart">{title}{filter}</div>;
  }
  const shown = LINES.filter((l) => !l.optional || total);
  const ticks = niceTicks(Math.max(...weeks.flatMap((w) => shown.map((l) => w[l.key]))));
  const max = ticks[ticks.length - 1];
  const plotW = width - PAD.l - PAD.r;
  const colW = plotW / weeks.length;
  const x = (i) => PAD.l + colW * (i + 0.5);
  const y = (v) => PAD.t + (H - PAD.t - PAD.b) * (1 - v / max);
  const last = weeks[weeks.length - 1];
  const peak = openPeak(weeks);
  const down = peak.week !== last.week && last.open < peak.value;
  const ends = spreadLabels(shown.map((l) => y(last[l.key])));
  const every = plotW < NARROW ? 2 : 1;
  const tip = hover === null ? null : weeks[hover];
  const select = (w) => pick && canPick(w.week) && pick(w.week);
  const band = (i, cls) => <rect className={cls} x={PAD.l + colW * i} y={PAD.t}
    width={colW} height={H - PAD.t - PAD.b} />;
  return (
    <div className="bug-chart" ref={box}>
      {title}
      {filter}
      <div className="bug-chart-sum">{t(down ? SUMMARY_DOWN : SUMMARY, {
        fixed: last.fixedSoFar, open: last.open, peak: peak.value,
        date: dayOf(peak.week) })}</div>
      <Legend shown={shown} total={total} onTotal={setTotal} />
      <svg width={width} height={H} role="img"
        aria-label={t("Bugs fixed and still open, week by week")}>
        {weeks.map((w, i) => (chosen === w.week || hover === i)
          && <g key={w.week}>{band(i, chosen === w.week
            ? "bug-chart-picked" : "bug-chart-hover")}</g>)}
        {ticks.map((v) => (
          <g key={v} className="bug-chart-axis">
            <line className={v ? "" : "bug-chart-base"} x1={PAD.l} x2={PAD.l + plotW}
              y1={y(v)} y2={y(v)} />
            <text x={PAD.l - 10} y={y(v) + 4} textAnchor="end">{v}</text>
          </g>
        ))}
        {weeks.map((w, i) => i % every === 0 && (
          <text key={w.week} className="bug-chart-axis" x={x(i)} y={H - 8}
            textAnchor="middle">{dayOf(w.week)}</text>
        ))}
        {shown.map((l, k) => (
          <g key={l.key}>
            <polyline className="bug-chart-line" stroke={l.color}
              points={weeks.map((w, i) => `${x(i)},${y(w[l.key])}`).join(" ")} />
            <circle cx={x(weeks.length - 1)} cy={y(last[l.key])} r={4.5} fill={l.color} />
            {tip && hover !== weeks.length - 1
              && <circle cx={x(hover)} cy={y(tip[l.key])} r={4} fill={l.color} />}
            <text className="bug-chart-end" x={x(weeks.length - 1) + 12} y={ends[k] + 4}>
              {t(l.end, { n: last[l.key] })}</text>
          </g>
        ))}
        <WeekTargets weeks={weeks} colW={colW} chosen={chosen} pickable={!!pick}
          dateOf={dateOf} onHover={setHover} onSelect={select} />
      </svg>
      {tip && (
        <div className="bug-chart-tip" style={{ left: x(hover) + 22 }}>
          <b>{t("Up to {date}", { date: dateOf(tip.week) })}</b>
          {" — "}{shown.map((l) => `${t(l.name)} ${tip[l.key]}`).join(" · ")}
        </div>
      )}
    </div>
  );
}

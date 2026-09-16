// implements: ARCH-VIEWER-007
/* The Plan's fixed parts: the lane names on the left and the ruler along the top. */
import {
  PX, LABEL_W, BAND_H, FLAG_H, MONTH_H, WEEK_H, DAY_H, HEAD_H,
} from "./ganttLayout.js";

const LANE_NAME = {
  display: "flex", alignItems: "center", justifyContent: "flex-end", padding: "0 12px",
  fontSize: 11, fontWeight: 700, letterSpacing: "0.5px", textTransform: "uppercase",
  color: "var(--fg-faint)",
};

/* Sticky: the chart scrolls sideways for months, and a lane the reader cannot name is a
   row of bars with no subject. zIndex clears the bars. The scroller pads itself 20px and
   `left: 0` sticks to the PADDING box, so scrolled bars slid through that band beside the
   names; the shadow paints the column's background across it and the scroller clips it at
   the same edge, so it plugs the gap exactly and spills nowhere. */
const COLUMN = {
  width: LABEL_W, flexShrink: 0, borderRight: "1px solid var(--border)",
  background: "var(--bg-raised)", position: "sticky", left: 0, zIndex: 5,
  borderRadius: "8px 0 0 8px", boxShadow: "-24px 0 0 var(--bg-raised)",
};

/** The lane-name column. The shipped band is named by the branch git is on, not the word
 *  "Shipped": a map opened from a feature branch looked identical to one opened from main,
 *  right up to the moment someone acted on the wrong plan (REQ-PLANBRANCH-1011). */
export function LaneLabels({ lay, branch, t }) {
  const last = lay.lanes.length - 1;
  return (
    <div style={COLUMN}>
      <div style={{ height: HEAD_H, borderBottom: "1px solid var(--border)" }} />
      {lay.pastRows.length > 0 && (
        <div style={{ ...LANE_NAME, height: BAND_H, borderBottom: "1px solid var(--border)" }}>
          {branch || t("Shipped")}
        </div>
      )}
      {lay.lanes.map((ln, i) => (
        <div key={ln} style={{
          ...LANE_NAME, height: lay.heights[i],
          borderBottom: i < last ? "1px solid var(--border-soft)" : "none",
        }}>
          {ln}
        </div>
      ))}
    </div>
  );
}

const PILL = {
  position: "absolute", top: 4, textAlign: "center", fontSize: 9, fontWeight: 800,
  borderRadius: 4, lineHeight: "14px",
};
const ROW = { display: "flex", borderTop: "1px solid var(--border-soft)" };
const CELL = {
  boxSizing: "border-box", borderRight: "1px solid var(--border-soft)",
  display: "flex", alignItems: "center", justifyContent: "center",
};

/** Today, the release ticks and — when no lane holds them — the version pills. */
function FlagRow({ lay, t }) {
  const { todayIdx, totalDays } = lay;
  return (
    <div style={{ height: FLAG_H, position: "relative" }}>
      {todayIdx >= 0 && todayIdx < totalDays && (
        <div style={{
          ...PILL, left: todayIdx * PX + PX / 2 - 18, width: 36, color: "var(--accent-2)",
          background: "var(--surface)", border: "1px solid var(--accent-2)", zIndex: 4,
        }}>
          {t("today")}
        </div>
      )}
      {lay.releaseIdx.map((r) => (
        <div key={r.iso} title={`${t("release")} · ${r.iso}`} style={{
          position: "absolute", top: FLAG_H - 6, left: r.idx * PX + PX / 2,
          width: 1, height: 6, background: "var(--fg-faint)", zIndex: 1,
        }} />
      ))}
      {!lay.releaseLane && lay.flags.map((f) => (
        <div key={f.ms} title={f.label || `${f.ms} · ${f.at.toLocaleDateString(lay.loc)}`} style={{
          ...PILL, left: f.idx * PX + PX / 2 - 28, width: 56, color: "var(--indigo-500)",
          background: "var(--indigo-tint)", border: "1px solid var(--indigo-400)", zIndex: 3,
        }}>
          {f.ms}
        </div>
      ))}
    </div>
  );
}

const fade = (pct) => `color-mix(in oklch, var(--fg-faint) ${pct}%, transparent)`;

/* The day of the month under each week, `day/month`. Today is marked in the accent colour
   and a weekend is fainter, so a Friday reads as the end of the week.
   implements: REQ-PLANDAYS-1021 */
function dayStyle(dd, todayIdx) {
  const today = dd.start === todayIdx;
  return {
    ...CELL, width: PX, flexShrink: 0, overflow: "hidden", whiteSpace: "nowrap",
    borderRight: "1px solid color-mix(in oklch, var(--border-soft) 60%, transparent)",
    fontSize: 8, lineHeight: 1, fontVariantNumeric: "tabular-nums", letterSpacing: "-0.2px",
    fontWeight: today ? 800 : 500,
    color: today ? "var(--accent-2)" : dd.weekend ? fade(55) : "var(--fg-faint)",
    background: dd.weekend ? fade(6) : "none",
  };
}

/** The ruler: flags, then months, ISO weeks and days. An ISO week, not a count from the
 *  chart's left edge: the same calendar week must read the same in every chart. */
export function Ruler({ lay, t }) {
  const weekStyle = (w) => ({
    ...CELL, width: w.span * PX, fontSize: 9, fontWeight: 600, color: "var(--fg-faint)",
    overflow: "hidden", whiteSpace: "nowrap",
  });
  return (
    <div style={{ position: "relative", height: HEAD_H, borderBottom: "1px solid var(--border)",
      background: "var(--bg-raised)" }}>
      <FlagRow lay={lay} t={t} />
      <div style={{ ...ROW, height: MONTH_H }}>
        {lay.months.map((m) => (
          <div key={`${m.label}-${m.start}`} style={{
            ...CELL, width: m.span * PX, fontSize: 11, fontWeight: 700, color: "var(--fg-muted)",
          }}>{m.label}</div>
        ))}
      </div>
      <div style={{ ...ROW, height: WEEK_H }}>
        {lay.weeks.map((w) => (
          <div key={w.start} style={weekStyle(w)}>{w.span >= 4 ? w.label : ""}</div>
        ))}
      </div>
      <div style={{ ...ROW, height: DAY_H }}>
        {lay.days.map((dd) => (
          <div key={dd.start} data-day={dd.label} style={dayStyle(dd, lay.todayIdx)}>
            {dd.label}
          </div>
        ))}
      </div>
    </div>
  );
}

// implements: ARCH-VIEWER-007
/* The Plan's moving parts: the shipped band, the lanes with their bars
 * and versions, and the guides that tie each of them to its day on the
 * ruler. */
import {
  PX, PAD, ROW_H, SHIP_H, HEAD_H, LABEL_LINES, LANE_TONE, extent,
  shipExtent, PILL_W, pillTop,
} from "./ganttLayout.js";
import { onActivate } from "./PlanNotes.jsx";

const selected = (picked, key) => (picked && picked.key === key
  ? "2px solid var(--accent-2)" : "none");
const fade = (pct) =>
  `color-mix(in oklch, var(--fg-faint) ${pct}%, transparent)`;
/* The tints are translucent, so a guide or a month rule drawn under a box
   showed through its title. Stacked on the chart's own surface they keep
   their colour and hide what is beneath. */
const opaque = (...tints) => tints.map((c) => `linear-gradient(${c}, ${c})`)
  .concat("var(--surface)").join(", ");

function MonthRules({ months }) {
  return months.map((m) => (
    <div key={m.start} style={{
      position: "absolute", top: 0, bottom: 0, left: m.start * PX,
      width: 1, background: "var(--border-soft)", pointerEvents: "none",
    }} />
  ));
}

function shippedStyle(h, picked) {
  const { left, width } = shipExtent(h);
  return {
    position: "absolute", left, top: PAD + (h.subRow || 0) * SHIP_H,
    width, height: SHIP_H - 6,
    boxSizing: "border-box", borderRadius: 4,
    background: opaque(fade(16), fade(5)),
    border: `1px solid ${fade(40)}`, borderLeft: "3px solid var(--fg-muted)",
    color: "var(--fg-muted)", fontSize: 11, fontWeight: 600, padding: "0 8px",
    display: "flex", alignItems: "center", gap: 6, overflow: "hidden",
    whiteSpace: "nowrap",
    cursor: "pointer", outline: selected(picked, h.key),
    outlineOffset: 1,
  };
}

/** What already shipped, one block per release. The block covers the days
 *  between its first and last commit, and widens to its version when those
 *  days are shorter than the label. A second row is taken when that box
 *  would cover another block. The headline opens in the note.
 *  implements: REQ-HISTORY-1081 */
export function ShippedBand({ sel, t }) {
  const { lay, picked, toggle } = sel;
  if (!lay.pastBars.length) return null;
  return (
    <div style={{
      position: "relative", height: lay.pastH,
      borderBottom: "1px solid var(--border)",
      background: fade(5),
    }}>
      <MonthRules months={lay.months} />
      {lay.pastBars.map((h) => {
        const pick = () => toggle({ kind: "release", ...h });
        const caption = h.members && !String(h.version).includes("-v")
          ? `${h.members.length} ${t("releases")}` : "";
        const tip = h.members
          ? `${h.version}\n${t("first commit")} ${h.start}\n`
            + `${t("last commit")} ${h.end}\n`
            + h.members.map((m) => m.version).join("\n")
          : `${h.version}\n${t("first commit")} ${h.start}\n`
            + `${t("last commit")} ${h.end}`;
        return (
          <div key={h.key} data-release={h.version} role="button"
            tabIndex={0} onClick={pick} onKeyDown={onActivate(pick)}
            style={shippedStyle(h, picked)} title={tip}>
            <span style={{ fontWeight: 700, flexShrink: 0 }}>{h.version}</span>
            {caption ? (
              <span style={{
                overflow: "hidden", textOverflow: "ellipsis", fontWeight: 500,
              }}>
                {caption}
              </span>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}

/** A version is a release: its pill sits in the cadence's lane at its
 *  due date, and selecting it opens what is planned on it.
 *  implements: REQ-PLANCADENCE-1000 */
function VersionPill({ f, laneH, sel }) {
  const { lay, picked, toggle } = sel;
  const key = `ms-${f.ms}`;
  const pick = () => toggle({ kind: "version", key, ...f });
  return (
    <div data-version={f.ms} role="button" tabIndex={0} onClick={pick}
      onKeyDown={onActivate(pick)}
      title={`${f.ms} · ${f.label ? `${f.label} · ` : ""}`
        + `${f.at.toLocaleDateString(lay.loc)}`}
      style={{
        cursor: "pointer", outlineOffset: 1, outline: selected(picked, key),
        position: "absolute", top: pillTop(laneH, f.row, lay.flagRows),
        left: f.idx * PX + PX / 2 - PILL_W / 2,
        width: PILL_W, height: 22, boxSizing: "border-box", textAlign: "center",
        fontSize: 11, fontWeight: 800, lineHeight: "20px",
        color: "var(--indigo-500)", background: "var(--indigo-tint)",
        border: "1px solid var(--indigo-400)", borderRadius: 4, zIndex: 3,
      }}>
      {f.ms}
    </div>
  );
}

function barStyle(bar, tone, picked) {
  const { left, width } = extent(bar);
  return {
    position: "absolute", left, top: PAD + bar.subRow * ROW_H, width,
    height: ROW_H - 6,
    background: opaque(tone.bg), color: tone.fg, borderRadius: 4,
    boxSizing: "border-box",
    border: `1px solid color-mix(in oklch, ${tone.edge} 40%, transparent)`,
    borderLeft: `3px solid ${tone.edge}`, fontSize: 11, fontWeight: 600,
    padding: "4px 8px",
    display: "flex", alignItems: "flex-start", overflow: "hidden",
    cursor: "pointer",
    outline: selected(picked, bar.key), outlineOffset: 1,
  };
}

/* Three lines, then an ellipsis. A title cut mid-word on one line told
   the reader nothing about how much it was missing. */
const TITLE = {
  position: "relative", overflow: "hidden", display: "-webkit-box",
  WebkitBoxOrient: "vertical", WebkitLineClamp: LABEL_LINES, lineHeight: 1.3,
  whiteSpace: "normal",
};
const PROGRESS = {
  position: "absolute", inset: 0,
  background: "color-mix(in oklch, var(--fg) 8%, transparent)",
  pointerEvents: "none",
};

/* A title too long for its bar, on one line beside it. Opaque, like the
   bars, so no guide or month rule runs through the words. */
function besideStyle(bar, tone) {
  const { left, width } = extent(bar);
  return {
    position: "absolute", left: left + width + 4, top: PAD + bar.subRow * ROW_H,
    background: "var(--surface)", color: tone.fg, fontSize: 11,
    fontWeight: 600, lineHeight: 1.3, padding: "4px 4px", whiteSpace: "nowrap",
    cursor: "pointer",
  };
}

function Bar({ bar, tone, picked, toggle }) {
  const milestone = bar.milestone ? `\n${bar.milestone}` : "";
  const tip = `${bar.title}\n${bar.start} → ${bar.end}${milestone}`;
  return (
    <>
      <div title={tip} onClick={() => toggle(bar)}
        style={barStyle(bar, tone, picked)}>
        {bar.progress != null
          && <span style={{ ...PROGRESS, width: `${bar.progress}%` }} />}
        {!bar.labelW && <span style={TITLE}>{bar.title}</span>}
      </div>
      {bar.labelW > 0 && (
        <div data-beside="" title={tip} onClick={() => toggle(bar)}
          style={besideStyle(bar, tone)}>{bar.title}</div>
      )}
    </>
  );
}

/** One lane: month rules, the version pills when it is the release lane,
 *  and its bars. */
export function Lane({ ln, i, sel }) {
  const { lay, picked, toggle } = sel;
  const tone = LANE_TONE[i % LANE_TONE.length];
  const laneH = lay.heights[i];
  const pills = ln === lay.releaseLane ? lay.flags : [];
  return (
    <div style={{
      position: "relative", height: laneH,
      borderBottom: i < lay.lanes.length - 1
        ? "1px solid var(--border-soft)" : "none",
    }}>
      <MonthRules months={lay.months} />
      {pills.map((f) => (
        <VersionPill key={`ms-${f.ms}`} f={f} laneH={laneH} sel={sel} />
      ))}
      {(lay.byLane[ln] || []).map((bar) => (
        <Bar key={bar.key} bar={bar} tone={tone} picked={picked}
             toggle={toggle} />
      ))}
    </div>
  );
}

const GUIDE_BORDER = {
  end: "2px dotted var(--fg-muted)",
  version: "2px dotted var(--indigo-400)",
  start: "2px dotted var(--fg-muted)",
};

/** Guides run from the day on the ruler down to the thing that happens
 *  on it, and stop there: a bar's start (a commitment, the stronger
 *  line) and end (an estimate, fainter), and a version at its due day.
 *  All dotted and drawn under the bars: a solid line on top crossed
 *  every title it passed through.
 *  implements: REQ-PLANSTACK-1012 */
export function Guides({ guides }) {
  return guides.map((gd) => (
    <div key={gd.key} data-guide={gd.kind} style={{
      position: "absolute", top: HEAD_H, height: gd.to, left: gd.x - 1,
      width: 0,
      borderLeft: GUIDE_BORDER[gd.kind],
      opacity: gd.kind === "end" ? 0.38 : 0.5,
      pointerEvents: "none",
    }} />
  ));
}

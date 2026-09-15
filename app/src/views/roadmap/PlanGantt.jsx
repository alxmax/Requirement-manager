// implements: ARCH-VIEWER-007
/* Calendar Gantt: months and ISO weeks on X, swimlanes on Y, today + milestone flags in
 * the header. Selecting a bar opens the note its author wrote under the matching
 * ROADMAP.md item (REQ-VIEWER-999). */
import { Fragment, useState } from "react";
import {
  parseIso, isoLocal, dayIndex, addDays, buildMonthBands, buildWeekBands, stackBars,
} from "../../lib/timeline.js";
import { buildPlanBars } from "../../lib/planBars.js";

/* 11px a day, and a floor of 30. At 7px a week drew 43px and was floored to 72 — nearly
 * three days of borrowed room, which is what pushed a bar into its neighbour's week. At
 * 11 a week is 71px of its own, and the floor only catches bars under three days, which
 * have no label room at any scale.  implements: REQ-PLANSTACK-1012 */
const PX = 11;
const BAR_MIN_W = 30;
const LABEL_W = 108;
/* 3 lines x 11px x 1.3 = 43px of text, plus the bar's 8px of vertical padding, plus the
 * 6px the row keeps between bars. A row of 50 clipped the third line half-way down its
 * glyphs — the wrap promised three lines and the box only had room for two and a half. */
const LABEL_LINES = 3;
const ROW_H = 58;
const PAD = 10;
const FLAG_H = 22;
const MONTH_H = 26;
const WEEK_H = 16;
const HEAD_H = FLAG_H + MONTH_H + WEEK_H;

const LANE_TONE = [
  { bg: "color-mix(in oklch, var(--cov-tested) 22%, transparent)", fg: "var(--cov-tested)", edge: "var(--cov-tested)" },
  { bg: "color-mix(in oklch, var(--amber-600) 20%, transparent)", fg: "var(--amber-700)", edge: "var(--amber-600)" },
  { bg: "var(--indigo-tint)", fg: "var(--indigo-500)", edge: "var(--indigo-400)" },
  { bg: "color-mix(in oklch, var(--fg-faint) 14%, transparent)", fg: "var(--fg-muted)", edge: "var(--fg-faint)" },
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


/** ROADMAP.md keeps a note under an item as an HTML comment, which is how a plan file
 *  hides it from a Markdown reader — the markers are packaging, not content. Strip them
 *  and the blank lines they leave, so the panel shows the sentence and not the syntax. */
export function noteText(context) {  // implements: REQ-VIEWER-999
  if (typeof context !== "string") return "";
  return context
    .replace(/<!--/g, "")
    .replace(/-->/g, "")
    .split(/\r?\n/)
    .map((ln) => ln.trim())
    .join("\n")
    .trim();
}

/** The roadmap item a bar belongs to. `req` is the only id both sides carry, so it is the
 *  join; a bar with none, or one no item claims, simply has no note. */
export function matchItem(bar, roadmap) {  // implements: REQ-VIEWER-999
  const req = bar?.reqId || bar?.req;
  if (!req || !Array.isArray(roadmap)) return null;
  return roadmap.find((it) => it && it.req === req) || null;
}

function BarNote({ bar, roadmap, t, openSpec, onClose }) {  // implements: REQ-VIEWER-999
  const item = matchItem(bar, roadmap);
  const note = noteText(item?.context);
  const req = bar?.reqId || bar?.req;
  return (
    <div style={{
      marginTop: 12, padding: "14px 16px", borderRadius: 6,
      background: "var(--surface)", border: "1px solid var(--border-soft)",
      borderLeft: "3px solid var(--accent-2)", maxWidth: 760,
    }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 10, flexWrap: "wrap" }}>
        <strong style={{ fontSize: 14 }}>{bar.title}</strong>
        <span style={{ fontSize: 11, color: "var(--fg-faint)" }}>
          {bar.start} → {bar.end}
          {bar.milestone ? ` · ${bar.milestone}` : ""}
          {item?.horizon ? ` · ${item.horizon}` : ""}
        </span>
        <button type="button" onClick={onClose} style={{
          marginLeft: "auto", background: "none", border: "none", cursor: "pointer",
          color: "var(--fg-faint)", fontSize: 16, lineHeight: 1, padding: 0,
        }} aria-label={t ? t("Close") : "Close"}>×</button>
      </div>
      {req && (
        <div style={{ fontSize: 11, marginTop: 6 }}>
          {openSpec
            ? <button type="button" onClick={() => openSpec(req)} style={{
                background: "none", border: "none", padding: 0, cursor: "pointer",
                color: "var(--accent-2)", font: "inherit", textDecoration: "underline",
              }}>{req}</button>
            : <span style={{ color: "var(--fg-faint)" }}>{req}</span>}
        </div>
      )}
      {note
        ? <div style={{
            marginTop: 10, fontSize: 12.5, lineHeight: 1.55, whiteSpace: "pre-wrap",
          }}>{note}</div>
        : <div style={{ marginTop: 10, fontSize: 12, color: "var(--fg-faint)" }}>
            {t ? t("No note in ROADMAP.md for this item.")
               : "No note in ROADMAP.md for this item."}
          </div>}
    </div>
  );
}

export function PlanGantt({ planning, history, roadmap, branch, locale, t, zoom, openSpec }) {
  const [picked, setPicked] = useState(null);
  const todayD = parseIso(isoLocal(new Date()));
  const raw = buildPlanBars(planning);
  const dueList = Object.entries(planning?.milestones || {})
    .filter(([, m]) => m?.due && parseIso(m.due))
    .map(([ms, m]) => ({ ms, due: m.due, label: m.label, at: parseIso(m.due) }));

  /* What already shipped, one row per calendar month, straight off CHANGELOG.md via the
   * engine. It shares the timeline with the plan rather than living in a tab of its own:
   * the question is "what happened, and what is next", and two charts cannot answer it
   * next to a `today` line they do not share.  implements: REQ-HISTORY-1003 */
  const past = (history || []).filter((h) => parseIso(h.first) && parseIso(h.last));

  // A cadence with no bars is still a calendar, and a repo that has planned nothing is
  // the one that needs one — `init` seeds it for exactly that (REQ-PLANHORIZON-1010).
  if (!raw.length && !dueList.length && !past.length && !(planning?.releases || []).length) {
    return (
      <div style={{ padding: 40, color: "var(--fg-faint)", fontSize: 13 }}>
        {t("Add milestones with due dates or bars in _planning.json.")}
      </div>
    );
  }

  const dates = [
    ...raw.flatMap((b) => [parseIso(b.start), parseIso(b.end)]),
    ...dueList.map((d) => d.at),
    ...past.flatMap((h) => [parseIso(h.first), parseIso(h.last)]),
    // Release dates extend the range like any other dated thing. Without this a
    // cadence running past the last bar or due — `until: 2026-12-31` with nothing
    // scheduled in December — emits dates the chart then drops on the `idx <
    // totalDays` filter below: the engine says a release lands and the chart, having
    // never grown to reach it, shows nothing and reports nothing.
    ...(planning?.releases || []).map(parseIso),
    todayD,
  ].filter(Boolean);
  let origin = monthStart(new Date(Math.min(...dates.map((d) => d.getTime()))));
  let end = monthEnd(new Date(Math.max(...dates.map((d) => d.getTime()))));

  const totalDays = dayIndex(origin, end) + 1;
  const chartW = totalDays * PX;
  /* The drawn box of a bar, in one place. The renderer used to compute this inline and
     `stackBars` compared dates, so the two disagreed about what "overlapping" meant and
     short neighbours were painted on top of each other (REQ-PLANSTACK-1012). */
  const extent = (b) => ({
    left: b.startIdx * PX + 3,
    width: Math.max((b.endIdx - b.startIdx + 1) * PX - 6, BAR_MIN_W),
  });
  const bars = indexBars(raw, origin);

  let lanes = Array.isArray(planning?.lanes) && planning.lanes.length
    ? [...planning.lanes]
    : [...new Set(bars.map((b) => b.lane))];
  if (!lanes.length) lanes = ["Implementations"];

  const pastRows = past.map((h) => {
    const a = parseIso(h.first), z = parseIso(h.last);
    const startIdx = dayIndex(origin, a);
    return { ...h, startIdx, endIdx: Math.max(dayIndex(origin, z), startIdx) };
  });
  const byLane = Object.fromEntries(lanes.map((ln) => [ln, bars.filter((b) => b.lane === ln)]));
  const heights = lanes.map((ln) => Math.max(stackBars(byLane[ln] || [], extent), 1) * ROW_H + PAD * 2);
  const bodyH = heights.reduce((a, h) => a + h, 0);
  const months = buildMonthBands(origin, totalDays, locale);
  const weeks = buildWeekBands(origin, totalDays);
  const todayIdx = todayD ? dayIndex(origin, todayD) : -1;
  const flags = dueList.map((d) => ({ ...d, idx: dayIndex(origin, d.at) }));
  /* Release cadence: the ENGINE computed these dates (targets.py) and the chart only
   * places them. Recomputing the weekday arithmetic here is how the CLI and the chart
   * would come to disagree about when a release lands — the same reason `health` and
   * `design` are read, not derived.  implements: REQ-PLANCADENCE-1000 */
  const releaseIdx = (planning?.releases || [])
    .map((iso) => ({ iso, idx: dayIndex(origin, parseIso(iso)) }))
    .filter((r) => r.idx >= 0 && r.idx < totalDays);
  const loc = locale === "ro" ? "ro-RO" : "en-GB";

  return (
    <div style={{ zoom: zoom / 100, width: "max-content", minWidth: "100%" }}>
      {/* No `overflow: hidden` here. It made this box the sticky column's scrollport,
          and a scrollport that never scrolls never lets its sticky child stick — so the
          lane names slid away while the note panel, which sits outside this box, stayed.
          The radius moves to the children that touch the corners. */}
      <div style={{
        display: "flex", border: "1px solid var(--border)", borderRadius: 8,
        background: "var(--surface)",
      }}>
        {/* Sticky: the chart scrolls sideways for months, and a lane the reader cannot
            name is a row of bars with no subject. zIndex clears the bars, which are
            absolutely positioned inside each lane. */}
        <div style={{
          width: LABEL_W, flexShrink: 0, borderRight: "1px solid var(--border)",
          background: "var(--bg-raised)", position: "sticky", left: 0, zIndex: 5,
          borderRadius: "8px 0 0 8px",
          /* The scroller pads itself 20px, and `left: 0` sticks to the PADDING box — so
             scrolled bars slid through that band and showed up beside the lane names.
             The shadow paints the column's own background across it; the scroller clips
             it at the same edge, so it plugs the gap exactly and spills nowhere. */
          boxShadow: "-24px 0 0 var(--bg-raised)",
        }}>
          <div style={{ height: HEAD_H, borderBottom: "1px solid var(--border)" }} />
          {pastRows.length > 0 && (
            <div style={{
              height: ROW_H + PAD * 2, display: "flex", alignItems: "center",
              justifyContent: "flex-end", padding: "0 12px", fontSize: 11, fontWeight: 700,
              letterSpacing: "0.5px", textTransform: "uppercase", color: "var(--fg-faint)",
              borderBottom: "1px solid var(--border)",
            }}>
              {/* The branch git is on, not the word "Shipped": a map opened from a
                  feature branch looked identical to one opened from main, right up to
                  the moment someone acted on the wrong plan (REQ-PLANBRANCH-1011). */}
              {branch || t("Shipped")}
            </div>
          )}
          {lanes.map((ln, i) => (
            <div key={ln} style={{
              height: heights[i], display: "flex", alignItems: "center", justifyContent: "flex-end",
              padding: "0 12px", fontSize: 11, fontWeight: 700, letterSpacing: "0.5px",
              textTransform: "uppercase", color: "var(--fg-faint)",
              borderBottom: i < lanes.length - 1 ? "1px solid var(--border-soft)" : "none",
            }}>
              {ln}
            </div>
          ))}
        </div>

        {/* `flex: 1` lets the track take the room the lane column leaves, so a plan
            shorter than the viewport fills it instead of stopping two thirds across;
            `minWidth: chartW` keeps a longer one at its true scale and scrolls.
            implements: REQ-PLANSTACK-1012 */}
        <div style={{ position: "relative", minWidth: chartW, flex: 1 }}>
          <div style={{ position: "relative", height: HEAD_H, borderBottom: "1px solid var(--border)",
            background: "var(--bg-raised)" }}>
            <div style={{ height: FLAG_H, position: "relative" }}>
              {todayIdx >= 0 && todayIdx < totalDays && (
                <div style={{
                  position: "absolute", top: 4, left: todayIdx * PX + PX / 2 - 18,
                  width: 36, textAlign: "center", fontSize: 9, fontWeight: 800,
                  color: "var(--accent-2)", background: "var(--surface)",
                  border: "1px solid var(--accent-2)", borderRadius: 4, lineHeight: "14px",
                  zIndex: 4,
                }}>
                  {t("today")}
                </div>
              )}
              {releaseIdx.map((r) => (
                <div key={r.iso} title={`${t("release")} · ${r.iso}`} style={{
                  position: "absolute", top: FLAG_H - 6, left: r.idx * PX + PX / 2,
                  width: 1, height: 6, background: "var(--fg-faint)", zIndex: 1,
                }} />
              ))}
              {flags.map((f) => (
                <div key={f.ms} title={f.label || `${f.ms} · ${f.at.toLocaleDateString(loc)}`} style={{
                  position: "absolute", top: 4, left: f.idx * PX + PX / 2 - 28,
                  width: 56, textAlign: "center", fontSize: 9, fontWeight: 800,
                  color: "var(--indigo-500)", background: "var(--indigo-tint)",
                  border: "1px solid var(--indigo-400)", borderRadius: 4, lineHeight: "14px",
                  zIndex: 3,
                }}>
                  {f.ms}
                </div>
              ))}
            </div>
            <div style={{ height: MONTH_H, display: "flex", borderTop: "1px solid var(--border-soft)" }}>
              {months.map((m) => (
                <div key={`${m.label}-${m.start}`} style={{
                  width: m.span * PX, boxSizing: "border-box",
                  borderRight: "1px solid var(--border-soft)",
                  fontSize: 11, fontWeight: 700, color: "var(--fg-muted)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                }}>
                  {m.label}
                </div>
              ))}
            </div>
            {/* ISO week of the year, not a count from the chart's left edge: the same
              * calendar week must read the same in every chart and in any conversation
              * about it. A short first band is the honest consequence of a range that
              * does not begin on a Monday. */}
            <div style={{ height: WEEK_H, display: "flex", borderTop: "1px solid var(--border-soft)" }}>
              {weeks.map((w) => (
                <div key={w.start} style={{
                  width: w.span * PX, boxSizing: "border-box",
                  borderRight: "1px solid var(--border-soft)",
                  fontSize: 9, fontWeight: 600, color: "var(--fg-faint)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  overflow: "hidden", whiteSpace: "nowrap",
                }}>
                  {w.span >= 4 ? w.label : ""}
                </div>
              ))}
            </div>
          </div>

          {pastRows.length > 0 && (
            <div style={{
              position: "relative", height: ROW_H + PAD * 2,
              borderBottom: "1px solid var(--border)",
              background: "color-mix(in oklch, var(--fg-faint) 5%, transparent)",
            }}>
              {months.map((m) => (
                <div key={m.start} style={{
                  position: "absolute", top: 0, bottom: 0, left: m.start * PX,
                  width: 1, background: "var(--border-soft)", pointerEvents: "none",
                }} />
              ))}
              {pastRows.map((h) => {
                const left = h.startIdx * PX + 3;
                const width = Math.max((h.endIdx - h.startIdx + 1) * PX - 6, 46);
                return (
                  <div
                    key={h.month}
                    title={`${h.month} · ${h.count} ${t("releases")} · ${h.versions[0]} → ${h.versions[h.versions.length - 1]}
${h.headline}`}
                    style={{
                      position: "absolute", left, top: PAD, width, height: ROW_H - 4,
                      boxSizing: "border-box", borderRadius: 4,
                      background: "color-mix(in oklch, var(--fg-faint) 16%, transparent)",
                      border: "1px solid color-mix(in oklch, var(--fg-faint) 40%, transparent)",
                      borderLeft: "3px solid var(--fg-muted)",
                      color: "var(--fg-muted)", fontSize: 11, fontWeight: 600,
                      padding: "0 8px", display: "flex", alignItems: "center",
                      gap: 6, overflow: "hidden", whiteSpace: "nowrap",
                    }}
                  >
                    <span style={{ fontWeight: 700 }}>{h.landmark}</span>
                    <span style={{ opacity: 0.7 }}>
                      {h.count} {t("releases")}
                    </span>
                    <span style={{ overflow: "hidden", textOverflow: "ellipsis", fontWeight: 500 }}>
                      {h.headline}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
          {lanes.map((ln, i) => {
            const tone = LANE_TONE[i % LANE_TONE.length];
            const laneBars = byLane[ln] || [];
            stackBars(laneBars, extent);
            return (
              <div key={ln} style={{
                position: "relative", height: heights[i],
                borderBottom: i < lanes.length - 1 ? "1px solid var(--border-soft)" : "none",
              }}>
                {months.map((m) => (
                  <div key={m.start} style={{
                    position: "absolute", top: 0, bottom: 0, left: m.start * PX,
                    width: 1, background: "var(--border-soft)", pointerEvents: "none",
                  }} />
                ))}
                {releaseIdx.map((r) => (
                  <div key={r.iso} style={{
                    position: "absolute", top: 0, bottom: 0, left: r.idx * PX + PX / 2,
                    width: 1, background: "color-mix(in oklch, var(--fg-faint) 45%, transparent)",
                    pointerEvents: "none",
                  }} />
                ))}
                {laneBars.map((bar) => {
                  const { left, width } = extent(bar);
                  const top = PAD + bar.subRow * ROW_H;
                  return (
                    <div
                      key={bar.key}
                      title={`${bar.title}\n${bar.start} → ${bar.end}${bar.milestone ? `\n${bar.milestone}` : ""}`}
                      onClick={() => setPicked(
                        picked && picked.key === bar.key ? null : bar)}
                      style={{
                        position: "absolute", left, top, width, height: ROW_H - 6,
                        background: tone.bg, color: tone.fg, borderRadius: 4,
                        boxSizing: "border-box",
                        border: `1px solid color-mix(in oklch, ${tone.edge} 40%, transparent)`,
                        borderLeft: `3px solid ${tone.edge}`,
                        fontSize: 11, fontWeight: 600, padding: "4px 8px",
                        display: "flex", alignItems: "flex-start", overflow: "hidden",
                        cursor: "pointer",
                        outline: picked && picked.key === bar.key
                          ? "2px solid var(--accent-2)" : "none",
                        outlineOffset: 1,
                      }}
                    >
                      {bar.progress != null && (
                        <span style={{
                          position: "absolute", inset: 0, width: `${bar.progress}%`,
                          background: "color-mix(in oklch, var(--fg) 8%, transparent)",
                          pointerEvents: "none",
                        }} />
                      )}
                      {/* Three lines, then an ellipsis. A title cut mid-word on one
                          line told the reader nothing about how much it was missing. */}
                      <span style={{
                        position: "relative", overflow: "hidden",
                        display: "-webkit-box", WebkitBoxOrient: "vertical",
                        WebkitLineClamp: LABEL_LINES, lineHeight: 1.3, whiteSpace: "normal",
                      }}>
                        {bar.title}
                      </span>
                    </div>
                  );
                })}
              </div>
            );
          })}

          {/* Guides mark the WORK, not the dates. `today` and the milestones keep their
              header pills — the reader still finds them on the ruler — but a rule drawn
              the full height of the chart was ruling a line through the bars it was
              meant to help read. A start is solid and an end dotted, because a start is
              a commitment and an end an estimate.  implements: REQ-PLANSTACK-1012 */}
          {bars.map((b) => {
            const { left, width } = extent(b);
            return (
              <Fragment key={`guide-${b.key}`}>
                <div style={{
                  position: "absolute", top: HEAD_H, height: bodyH, left, width: 0,
                  borderLeft: "2px solid var(--fg-muted)", opacity: 0.5,
                  pointerEvents: "none", zIndex: 1,
                }} />
                <div style={{
                  position: "absolute", top: HEAD_H, height: bodyH,
                  left: left + width, width: 0,
                  borderLeft: "2px dotted var(--fg-muted)", opacity: 0.38,
                  pointerEvents: "none", zIndex: 1,
                }} />
              </Fragment>
            );
          })}
        </div>
      </div>
      {/* Sticky too, and for the same reason: the note belongs to the reader, not to
          the month the bar happens to sit in. Left unpinned it slid out of view with
          the chart, clipping its own first words. */}
      {picked && (
        <div style={{ position: "sticky", left: 0, width: "min(760px, 100%)" }}>
          <BarNote bar={picked} roadmap={roadmap} t={t} openSpec={openSpec}
                   onClose={() => setPicked(null)} />
        </div>
      )}
    </div>
  );
}

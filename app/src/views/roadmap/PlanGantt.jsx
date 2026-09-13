// implements: ARCH-VIEWER-007
/* Calendar Gantt: months on X, swimlanes on Y, today + milestone flags in the header. */
import {
  parseIso, isoLocal, dayIndex, addDays, buildMonthBands, stackBars,
} from "../../lib/timeline.js";
import { buildPlanBars } from "../../lib/planBars.js";

const PX = 7;
const LABEL_W = 108;
const ROW_H = 26;
const PAD = 10;
const FLAG_H = 22;
const MONTH_H = 26;
const HEAD_H = FLAG_H + MONTH_H;

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

export function PlanGantt({ planning, locale, t, zoom, openSpec }) {
  const todayD = parseIso(isoLocal(new Date()));
  const raw = buildPlanBars(planning);
  const dueList = Object.entries(planning?.milestones || {})
    .filter(([, m]) => m?.due && parseIso(m.due))
    .map(([ms, m]) => ({ ms, due: m.due, label: m.label, at: parseIso(m.due) }));

  if (!raw.length && !dueList.length) {
    return (
      <div style={{ padding: 40, color: "var(--fg-faint)", fontSize: 13 }}>
        {t("Add milestones with due dates or bars in _planning.json.")}
      </div>
    );
  }

  const dates = [
    ...raw.flatMap((b) => [parseIso(b.start), parseIso(b.end)]),
    ...dueList.map((d) => d.at),
    todayD,
  ].filter(Boolean);
  let origin = monthStart(new Date(Math.min(...dates.map((d) => d.getTime()))));
  let end = monthEnd(new Date(Math.max(...dates.map((d) => d.getTime()))));

  const totalDays = dayIndex(origin, end) + 1;
  const chartW = totalDays * PX;
  const bars = indexBars(raw, origin);

  let lanes = Array.isArray(planning?.lanes) && planning.lanes.length
    ? [...planning.lanes]
    : [...new Set(bars.map((b) => b.lane))];
  if (!lanes.length) lanes = ["Implementations"];

  const byLane = Object.fromEntries(lanes.map((ln) => [ln, bars.filter((b) => b.lane === ln)]));
  const heights = lanes.map((ln) => Math.max(stackBars(byLane[ln] || []), 1) * ROW_H + PAD * 2);
  const bodyH = heights.reduce((a, h) => a + h, 0);
  const months = buildMonthBands(origin, totalDays, locale);
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
      <div style={{
        display: "flex", border: "1px solid var(--border)", borderRadius: 8,
        overflow: "hidden", background: "var(--surface)",
      }}>
        <div style={{ width: LABEL_W, flexShrink: 0, borderRight: "1px solid var(--border)", background: "var(--bg-raised)" }}>
          <div style={{ height: HEAD_H, borderBottom: "1px solid var(--border)" }} />
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

        <div style={{ position: "relative", width: chartW }}>
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
          </div>

          {lanes.map((ln, i) => {
            const tone = LANE_TONE[i % LANE_TONE.length];
            const laneBars = byLane[ln] || [];
            stackBars(laneBars);
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
                  const left = bar.startIdx * PX + 3;
                  const width = Math.max((bar.endIdx - bar.startIdx + 1) * PX - 6, 72);
                  const top = PAD + bar.subRow * ROW_H;
                  const dashed = bar.kind === "ghost";
                  return (
                    <div
                      key={bar.key}
                      title={`${bar.title}\n${bar.start} → ${bar.end}${bar.milestone ? `\n${bar.milestone}` : ""}`}
                      onClick={bar.reqId && openSpec ? () => openSpec(bar.reqId) : undefined}
                      style={{
                        position: "absolute", left, top, width, height: ROW_H - 4,
                        background: tone.bg, color: tone.fg, borderRadius: 4,
                        boxSizing: "border-box",
                        border: dashed
                          ? `1.5px dashed ${tone.edge}`
                          : `1px solid color-mix(in oklch, ${tone.edge} 40%, transparent)`,
                        borderLeft: `3px solid ${tone.edge}`,
                        fontSize: 11, fontWeight: 600, padding: "0 8px",
                        display: "flex", alignItems: "center", overflow: "hidden",
                        cursor: bar.reqId ? "pointer" : "default",
                      }}
                    >
                      {bar.progress != null && (
                        <span style={{
                          position: "absolute", inset: 0, width: `${bar.progress}%`,
                          background: "color-mix(in oklch, var(--fg) 8%, transparent)",
                          pointerEvents: "none",
                        }} />
                      )}
                      <span style={{
                        position: "relative", overflow: "hidden", textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}>
                        {bar.title}
                      </span>
                    </div>
                  );
                })}
              </div>
            );
          })}

          {todayIdx >= 0 && todayIdx < totalDays && (
            <div style={{
              position: "absolute", top: HEAD_H, height: bodyH,
              left: todayIdx * PX + PX / 2, width: 2,
              background: "var(--accent-2)", opacity: 0.8, pointerEvents: "none", zIndex: 2,
            }} />
          )}
          {flags.map((f) => (
            <div key={`line-${f.ms}`} title={`${f.ms} · ${f.at.toLocaleDateString(loc)}`} style={{
              position: "absolute", top: HEAD_H, height: bodyH,
              left: f.idx * PX + PX / 2, width: 0,
              borderLeft: "2px dashed var(--indigo-400)", opacity: 0.55,
              pointerEvents: "none", zIndex: 1,
            }} />
          ))}
        </div>
      </div>
    </div>
  );
}

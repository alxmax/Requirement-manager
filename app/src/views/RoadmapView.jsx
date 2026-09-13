// implements: ARCH-VIEWER-007
/* RoadmapView — Gantt-style chart: semver milestones on X, one lane on Y.
   Requirements with `milestone:` field + TODO.md items via TODOS.

   One column per milestone and a chip carrying the full title made the table as
   wide as its longest title times its column count: 42 columns ran past 9000px,
   so a reader saw three versions at a time and panned for the rest. Two
   independent controls answer that, because they trade different things away —
   zoom shrinks everything including the type, density narrows the chip and
   keeps the type crisp. Both are remembered per reader. */
import { useEffect, useState } from "react";
import { REQUIREMENTS, TODOS, TARGETS, ROADMAP } from "../lib/data.js";
import { useI18n } from "../lib/i18n.jsx";
import { useDragPan } from "../lib/useDragPan.js";
import { ZoomControl, useCanvasZoom, clampZoom, ctrlBtn, ZOOM_DEFAULT, ZOOM_MIN, ZOOM_MAX } from "../lib/canvasZoom.jsx";
import { PlanGantt } from "./roadmap/PlanGantt.jsx";
import { Horizons } from "./roadmap/Horizons.jsx";

const ZOOM_KEY = "reqmap.roadmap.zoom";
const DENSITY_KEY = "reqmap.roadmap.density";
const MODE_KEY = "reqmap.roadmap.mode";

/* Guarded the way i18n.jsx guards its own: SSR (the smoke test) has no window,
 * and a file:// viewer in a hardened browser throws on the accessor itself. */
function readStored(key, parse, fallback) {
  try {
    if (typeof window === "undefined" || !window.localStorage) return fallback;
    const v = parse(window.localStorage.getItem(key));
    return v == null ? fallback : v;
  } catch { return fallback; }
}

function semverCmp(a, b) {
  const num = v => v.replace(/^v/i, "").split(".").map(n => parseInt(n, 10) || 0);
  const pa = num(a), pb = num(b);
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    const d = (pa[i] || 0) - (pb[i] || 0);
    if (d !== 0) return d;
  }
  return 0;
}

function barVariant(status) {
  if (status === "confirmed")   return "done";
  if (status === "in-progress") return "progress";
  if (status === "draft")       return "draft";
  return "planned";
}

// One lane. The Y axis carried four rows (bus/feature/need/ops — the ENGINE's taxonomy,
// a requirement's position in the graph), then two, Bugs and Features. Bugs rendered
// empty: nothing on this roadmap was a defect. The items are work that was not specified
// up front, which is not the same thing, and an axis with one populated value sorts
// nothing while still costing a row. So the lane stops classifying and names what the
// chips are. Every open TODO item and every milestoned requirement lands in it, whatever
// `lane:` says — the field still parses and is still emitted, it just no longer splits
// the chart.
const LANE_LABEL = "Implementations";   // implements: REQ-VIEWER-995

const ARROW = "polygon(0 0, calc(100% - 7px) 0, 100% 50%, calc(100% - 7px) 100%, 0 100%)";

/* The two densities differ only in numbers a reader can see the effect of.
 * `titleMax` is the one that reclaims width: a chip stops growing with its
 * title, and the full text moves to the tooltip `Bar` already carries. */
const DENSITY = {  // implements: REQ-VIEWER-984
  comfy:   { barH: 24, barPadL: 9, barGap: 5, font: 11, idFont: 9,
             cellPad: "6px 10px", headPad: "10px 14px", lanePad: "0 14px", titleMax: null },
  compact: { barH: 18, barPadL: 7, barGap: 4, font: 10, idFont: 9,
             cellPad: "3px 5px",  headPad: "6px 8px",   lanePad: "0 8px",  titleMax: 108 },
};

function formatDue(iso, locale) {
  try {
    const d = new Date(`${iso}T12:00:00`);
    return d.toLocaleDateString(locale === "ro" ? "ro-RO" : "en-GB", { day: "numeric", month: "short", year: "numeric" });
  } catch { return iso; }
}

function dueTone(iso) {
  const today = new Date().toISOString().slice(0, 10);
  if (iso < today) return "past";
  if (iso === today) return "today";
  return "future";
}

const VARIANT = {
  done:     { background: "var(--cov-tested-bg)",  color: "var(--cov-tested)",   dot: "var(--cov-tested)",   clipPath: ARROW, arrow: true },
  progress: { background: "var(--indigo-tint)",    color: "var(--indigo-500)",   dot: "var(--indigo-400)",   clipPath: ARROW, arrow: true },
  draft:    { background: "var(--amber-tint)",     color: "var(--amber-700)",    dot: "var(--amber-600)",    border: "1.5px dashed var(--amber-400)" },
  planned:  { background: "var(--surface-hov)",    color: "var(--fg-muted)",     dot: "var(--fg-faint)",     clipPath: ARROW, arrow: true },
  todo:     { background: "var(--amber-tint)",     color: "var(--amber-700)",    dot: "var(--amber-600)",    border: "1.5px dashed var(--amber-400)" },
};

function Bar({ variant, id, label, onClick, d }) {
  const v = VARIANT[variant] || VARIANT.planned;
  // The arrow clip eats the right edge, so an arrow chip needs the padding back.
  const padR = v.arrow ? d.barPadL + 11 : d.barPadL + 3;
  return (
    <span
      title={label}
      onClick={onClick}
      style={{
        display: "inline-flex", alignItems: "center", gap: d.barGap,
        height: d.barH, borderRadius: 5, padding: `0 ${padR}px 0 ${d.barPadL}px`,
        fontSize: d.font, fontWeight: 500, whiteSpace: "nowrap",
        cursor: onClick ? "pointer" : "default",
        clipPath: v.clipPath,
        background: v.background, color: v.color,
        border: v.border,
        maxWidth: d.titleMax ? d.titleMax + 60 : undefined,
      }}
    >
      <span style={{ width: 5, height: 5, borderRadius: "50%", flexShrink: 0, background: v.dot }} />
      {id && <span style={{ fontSize: d.idFont, opacity: 0.5, fontWeight: 600, letterSpacing: "0.3px", flexShrink: 0 }}>{id}</span>}
      <span style={d.titleMax
        ? { maxWidth: d.titleMax, overflow: "hidden", textOverflow: "ellipsis" }
        : undefined}>{label}</span>
    </span>
  );
}

function Segmented({ label, options, value, onChange, optionKey, optionLabel }) {
  const keyOf = (o) => (optionKey ? o[optionKey] : o);
  const labelOf = (o) => (optionLabel ? o[optionLabel] : o);
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
      <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.8px",
                     textTransform: "uppercase", color: "var(--fg-faint)" }}>{label}</span>
      <span style={{ display: "inline-flex", border: "1px solid var(--border)", borderRadius: 6, overflow: "hidden" }}>
        {options.map(o => (
          <button
            key={keyOf(o)}
            onClick={() => onChange(keyOf(o))}
            aria-pressed={keyOf(o) === value}
            style={{
              ...ctrlBtn, fontSize: 11,
              fontWeight: keyOf(o) === value ? 700 : 500,
              background: keyOf(o) === value ? "var(--surface-hov)" : "transparent",
              color: keyOf(o) === value ? "var(--fg)" : "var(--fg-muted)",
            }}
          >
            {labelOf(o)}
          </button>
        ))}
      </span>
    </span>
  );
}

/* `initialZoom` / `initialDensity` let a host (or a render test) preset the two
 * controls, the same seam `I18nProvider` opens with `initialLocale`; otherwise
 * the chart remembers the reader's last choice, and falls back to 100%/comfy. */
export function RoadmapView({ openSpec, initialZoom, initialDensity, initialMode, initialRoadmap }) {  // implements: REQ-VIEWER-984
  const { t, locale } = useI18n();
  const hasPlan = !!(TARGETS?.bars?.length)
    || Object.values(TARGETS?.milestones || {}).some((m) => m?.due);
  // `Not now` is parsed but never drawn, so a ROADMAP.md holding only that section
  // must not switch the mode on and then render three empty columns.
  const horizonItems = (initialRoadmap || ROADMAP)
    .filter(i => i.horizon === "now" || i.horizon === "next" || i.horizon === "later");
  const hasHorizons = horizonItems.length > 0;
  const [mode, setMode] = useState(() => {
    const stored = readStored(MODE_KEY, (v) => {
      if (v === "versions" || v === "plan") return v;
      if (v === "horizons") return v;
      if (v === "timeline") return "plan"; // renamed
      return null;
    }, null);
    // A reader whose last choice was Horizons in another repo must not land on a mode
    // this one cannot offer — the segmented control would have no matching option.
    const remembered = stored === "horizons" && !hasHorizons ? null : stored;
    return initialMode || remembered || (hasHorizons ? "horizons" : hasPlan ? "plan" : "versions");
  });
  const [showUnscheduled, setShowUnscheduled] = useState(false);
  const { zoom, setZoom, canvasRef } = useCanvasZoom({
    storageKey: ZOOM_KEY,
    initialZoom: initialZoom != null ? clampZoom(initialZoom) : readStored(ZOOM_KEY, (v) => {
      const n = Number(v);
      return Number.isFinite(n) && n >= ZOOM_MIN && n <= ZOOM_MAX ? Math.round(n) : null;
    }, ZOOM_DEFAULT),
  });
  const [density, setDensity] = useState(() => initialDensity || readStored(
    DENSITY_KEY, (v) => (v === "comfy" || v === "compact" ? v : null), "comfy"));
  const { onMouseDown, onClickCapture } = useDragPan(canvasRef);

  useEffect(() => {
    try { window.localStorage.setItem(DENSITY_KEY, density); } catch { /* not fatal */ }
  }, [density]);
  useEffect(() => {
    try { window.localStorage.setItem(MODE_KEY, mode); } catch { /* not fatal */ }
  }, [mode]);

  const d = DENSITY[density] || DENSITY.comfy;

  // A milestone whose every TODO item shipped (and no requirement cites it)
  // used to have no signal at all reaching this Set — the column vanished
  // and the chart jumped straight to the next one, reading as a skipped
  // version rather than a finished one. A milestone is real once TODO.md
  // groups anything under it, done or not.
  const msSet = new Set();
  REQUIREMENTS.forEach(r => { if (r.milestone && r.status !== "deprecated") msSet.add(r.milestone); });
  TODOS.forEach(item => { if (item.milestone) msSet.add(item.milestone); });
  const msMeta = TARGETS?.milestones || {};
  Object.keys(msMeta).forEach(ms => msSet.add(ms));
  const milestones = Array.from(msSet).sort(semverCmp);

  const current =
    milestones.find(ms => REQUIREMENTS.some(r => r.milestone === ms && r.status === "in-progress")) ||
    [...milestones].reverse().find(ms => REQUIREMENTS.some(r => r.milestone === ms && r.status === "confirmed"));

  // Unscheduled is a planning bucket, so it holds only what is planned AT the
  // planning levels. A `level: code` requirement is a decomposed clause of an
  // architecture requirement and inherits that parent's milestone; listing all
  // 618 of them here produced a wall of chips that said nothing about the plan.
  const unscheduled = REQUIREMENTS.filter(r => !r.milestone && r.status !== "deprecated" && r.level !== "code");

  if (!milestones.length && !unscheduled.length && !hasPlan && !hasHorizons) {
    return (
      <div className="main" style={{ padding: 40, color: "var(--fg-faint)", fontSize: 13 }}>
        No milestones yet. Add <code>milestone: v1.x</code> to requirement frontmatter
        or create a <code>TODO.md</code> with <code>## v1.x</code> sections.
      </div>
    );
  }

  const byMs = Object.fromEntries(milestones.map(ms => [ms, []]));
  REQUIREMENTS.filter(r => r.milestone && r.status !== "deprecated")
    .forEach(r => { if (byMs[r.milestone]) byMs[r.milestone].push({ type: "req", r }); });
  TODOS.filter(t => !t.done)
    .forEach(t => { if (byMs[t.milestone]) byMs[t.milestone].push({ type: "todo", t }); });
  // Planned items from _planning.json — work not yet in TODO.md or requirements.
  milestones.forEach(ms => {
    const planned = msMeta[ms]?.items;
    if (!Array.isArray(planned)) return;
    const names = new Set(byMs[ms].map(item =>
      item.type === "req" ? item.r.title.toLowerCase()
        : item.type === "todo" ? item.t.name.toLowerCase() : ""));
    planned.forEach(text => {
      if (!names.has(text.toLowerCase())) byMs[ms].push({ type: "plan", text });
    });
  });
  const plannedCount = Object.values(byMs).flat().filter(i => i.type === "plan").length;
  const today = new Date().toISOString().slice(0, 10);
  const nextDue = milestones
    .map(ms => ({ ms, due: msMeta[ms]?.due }))
    .filter(x => x.due && x.due >= today)
    .sort((a, b) => a.due.localeCompare(b.due))[0];
  const maxRows = Math.max(1, ...Object.values(byMs).map(a => a.length));
  const rows = Array.from({ length: maxRows }, (_, i) => ({ rowIdx: i, maxRows, byMs }));

  const thBase = {
    background: "var(--bg-raised)", color: "var(--fg-muted)", fontSize: 11, fontWeight: 600,
    letterSpacing: "0.4px", padding: d.headPad, textAlign: "center",
    borderBottom: "1px solid var(--border)", borderRight: "1px solid var(--border)", whiteSpace: "nowrap",
  };

  return (
    <div className="main" style={{ display: "flex", flexDirection: "column", overflow: "hidden" }}>
      <div style={{
        display: "flex", alignItems: "center", gap: 18, flexWrap: "wrap",
        padding: "10px 20px", borderBottom: "1px solid var(--border)",
        background: "var(--bg-raised)", flexShrink: 0,
      }}>
        <ZoomControl zoom={zoom} setZoom={setZoom} />
        {(hasPlan || hasHorizons) && (
          <Segmented
            label={t("View")}
            options={[
              ...(hasHorizons ? [{ id: "horizons", label: t("Horizons") }] : []),
              ...(hasPlan ? [{ id: "plan", label: t("Plan") }] : []),
              { id: "versions", label: t("Versions") },
            ]}
            value={mode}
            onChange={setMode}
            optionKey="id"
            optionLabel="label"
          />
        )}
        {mode === "versions" && (
          <Segmented label="Density" options={["compact", "comfy"]} value={density} onChange={setDensity} />
        )}
        <span style={{ fontSize: 11, color: "var(--fg-faint)", marginLeft: "auto" }}>
          {nextDue && (
            <span style={{ marginRight: 12 }}>
              {t("next {ms} · due {date}", {
                ms: nextDue.ms,
                date: formatDue(nextDue.due, locale),
              })}
            </span>
          )}
          {mode === "versions" && (
            <>
              {milestones.length} {t("milestones")} · {rows.length} {t("rows")}
              {plannedCount > 0 && ` · ${t("{n} planned", { n: plannedCount })}`}
            </>
          )}
        </span>
      </div>

      <div ref={canvasRef} onMouseDown={onMouseDown} onClickCapture={onClickCapture}
           className="canvas pan" style={{ flex: 1, minHeight: 0, overflow: "auto", padding: "24px 20px" }}>
        {mode === "horizons" ? (
          <Horizons items={horizonItems} t={t} openSpec={openSpec} zoom={zoom} />
        ) : mode === "plan" ? (
          <PlanGantt planning={TARGETS} locale={locale} t={t} zoom={zoom} openSpec={openSpec} />
        ) : (
        /* CSS `zoom` (not `transform: scale`) so the scroll extent shrinks with
            the content — a transform leaves the container at full size and the
            reader pans across empty space to reach the last column. */
        <div style={{ zoom: zoom / 100, width: "max-content" }}>
          <table style={{ borderCollapse: "separate", borderSpacing: 0, width: "max-content", minWidth: 560 }}>
            <thead>
              <tr>
                <th style={{ ...thBase, background: "transparent", border: "none", width: 60 }} />
                {milestones.map(ms => {
                  const meta = msMeta[ms] || {};
                  const due = meta.due;
                  const tone = due ? dueTone(due) : null;
                  const dueColor = tone === "past" ? "var(--status-error)"
                    : tone === "today" ? "var(--status-drift)" : "var(--fg-faint)";
                  return (
                    <th key={ms} style={{ ...thBase, ...(ms === current ? { background: "var(--surface-hov)", color: "var(--fg)", fontWeight: 700 } : {}) }}>
                      <div>{ms}{ms === current && (
                        <span style={{ display: "inline-block", width: 6, height: 6, background: "var(--accent-2)",
                          borderRadius: "50%", marginLeft: 5, verticalAlign: "middle", position: "relative", top: -1 }} />
                      )}</div>
                      {due && (
                        <div style={{ fontSize: 9, fontWeight: 500, color: dueColor, marginTop: 3 }}>
                          {t("due {date}", { date: formatDue(due, locale) })}
                        </div>
                      )}
                      {meta.label && (
                        <div style={{ fontSize: 9, fontWeight: 400, color: "var(--fg-faint)", marginTop: 2, maxWidth: 140,
                          overflow: "hidden", textOverflow: "ellipsis" }} title={meta.label}>
                          {meta.label}
                        </div>
                      )}
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {rows.map(({ rowIdx }) => (
                <tr key={rowIdx}>
                  {rowIdx === 0 && (
                    <td rowSpan={maxRows} style={{
                      fontSize: 10, fontWeight: 700, letterSpacing: "0.8px", textTransform: "uppercase",
                      color: "var(--fg-faint)", padding: d.lanePad, textAlign: "right", verticalAlign: "middle",
                      borderRight: "1px solid var(--border)", whiteSpace: "nowrap", background: "var(--bg-raised)", minWidth: 60,
                    }}>
                      {LANE_LABEL}
                    </td>
                  )}
                  {milestones.map(ms => {
                    const item = byMs[ms][rowIdx];
                    return (
                      <td key={ms} style={{
                        padding: d.cellPad, borderBottom: "1px solid var(--border-soft)", borderRight: "1px solid var(--border-soft)",
                        background: "var(--surface)", verticalAlign: "middle",
                      }}>
                        {item?.type === "req" && (
                          <Bar variant={barVariant(item.r.status)} id={item.r.id} label={item.r.title}
                               onClick={() => openSpec(item.r.id)} d={d} />
                        )}
                        {item?.type === "todo" && (
                          <Bar variant="todo" label={item.t.name} onClick={() => {}} d={d} />
                        )}
                        {item?.type === "plan" && (
                          <Bar variant="planned" label={item.text} onClick={() => {}} d={d} />
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>

          {unscheduled.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <button
                onClick={() => setShowUnscheduled(s => !s)}
                style={{ background: "none", border: "none", cursor: "pointer", padding: "4px 0",
                         color: "var(--fg-faint)", fontSize: 12, fontFamily: "inherit" }}
              >
                {showUnscheduled ? "▾" : "▸"} Unscheduled ({unscheduled.length})
              </button>
              {showUnscheduled && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8, padding: "0 4px" }}>
                  {unscheduled.map(r => (
                    <Bar key={r.id} variant={barVariant(r.status)} id={r.id} label={r.title}
                         onClick={() => openSpec(r.id)} d={d} />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
        )}
      </div>
    </div>
  );
}

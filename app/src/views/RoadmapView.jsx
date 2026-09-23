// implements: ARCH-VIEWER-007
/* RoadmapView — two pictures of the plan: the dated Plan (PlanGantt) and
   one column per version (VersionsTable).

   One column per milestone and a chip carrying the full title made the
   table as wide as its longest title times its column count: 42 columns
   ran past 9000px, so a reader saw three versions at a time and panned
   for the rest. Two independent controls answer that, because they trade
   different things away — zoom shrinks everything including the type,
   density narrows the chip and keeps the type crisp. Both are remembered
   per reader. */
import { useEffect, useState } from "react";
import {
  REQUIREMENTS, TODOS, TARGETS, ROADMAP, HISTORY, BRANCH,
} from "../lib/data.js";
import { useI18n } from "../lib/i18n.jsx";
import { useDragPan } from "../lib/useDragPan.js";
import {
  ZoomControl, useCanvasZoom, clampZoom, ctrlBtn, ZOOM_DEFAULT, ZOOM_MIN,
  ZOOM_MAX,
} from "../lib/canvasZoom.jsx";
import { PlanGantt } from "./roadmap/PlanGantt.jsx";
import { buildVersions } from "./roadmap/versionsData.js";
import { DENSITY, VersionsTable, formatDue } from "./roadmap/VersionsTable.jsx";

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

/** A value kept in localStorage under `key`, written back whenever it
 * changes. */
function useStored(key, initial) {
  const [value, setValue] = useState(initial);
  useEffect(() => {
    try { window.localStorage.setItem(key, value); } catch { /* not fatal */ }
  }, [key, value]);
  return [value, setValue];
}

// A reader whose last choice was Horizons, or the old Timeline, lands on
// the Plan rather than on a mode with no matching option.
const parseMode = (v) => (v === "versions" || v === "plan" ? v
  : v === "horizons" || v === "timeline" ? "plan" : null);
const parseZoom = (v) => {
  const n = Number(v);
  return Number.isFinite(n) && n >= ZOOM_MIN && n <= ZOOM_MAX
    ? Math.round(n) : null;
};
const parseDensity = (v) => (v === "comfy" || v === "compact" ? v : null);

/* The Plan draws something from bars, milestone dues, shipped history
   alone, or a cadence alone: a repo that has planned NOTHING is the one
   that most needs a calendar to plan on (REQ-PLANHORIZON-1010). */
function hasPlanFor(history) {
  return !!(TARGETS?.bars?.length)
    || Object.values(TARGETS?.milestones || {}).some((m) => m?.due)
    || !!history.length
    || !!(TARGETS?.releases?.length);
}

function Segmented({ label, options, value, onChange }) {
  const labelStyle = { fontSize: 10, fontWeight: 700, letterSpacing: "0.8px",
                       textTransform: "uppercase", color: "var(--fg-faint)" };
  const group = {
    display: "inline-flex", border: "1px solid var(--border)",
    borderRadius: 6, overflow: "hidden",
  };
  const optionStyle = (on) => ({
    ...ctrlBtn, fontSize: 11, fontWeight: on ? 700 : 500,
    background: on ? "var(--surface-hov)" : "transparent",
    color: on ? "var(--fg)" : "var(--fg-muted)",
  });
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
      <span style={labelStyle}>{label}</span>
      <span style={group}>
        {options.map((o) => (
          <button key={o.id} onClick={() => onChange(o.id)}
                  aria-pressed={o.id === value}
                  style={optionStyle(o.id === value)}>
            {o.label}
          </button>
        ))}
      </span>
    </span>
  );
}

function Summary({ data, mode, t, locale }) {
  const { nextDue, plannedCount } = data;
  return (
    <span style={{
      fontSize: 11, color: "var(--fg-faint)", marginLeft: "auto",
    }}>
      {nextDue && (
        <span style={{ marginRight: 12 }}>
          {t("next {ms} · due {date}",
            { ms: nextDue.ms, date: formatDue(nextDue.due, locale) })}
        </span>
      )}
      {mode === "versions" && (
        <>
          {data.milestones.length}
          {" "}{t("milestones")} ·{" "}
          {data.maxRows} {t("rows")}
          {plannedCount > 0 && ` · ${t("{n} planned", { n: plannedCount })}`}
        </>
      )}
    </span>
  );
}

const TOOLBAR = {
  display: "flex", alignItems: "center", gap: 18, flexWrap: "wrap",
  padding: "10px 20px", borderBottom: "1px solid var(--border)",
  background: "var(--bg-raised)", flexShrink: 0,
};

function Toolbar({ controls, data, hasPlan, t, locale }) {
  const { zoom, setZoom, mode, setMode, density, setDensity } = controls;
  const modes = [
    { id: "plan", label: t("Plan") }, { id: "versions", label: t("Versions") },
  ];
  const densities = [
    { id: "compact", label: "compact" }, { id: "comfy", label: "comfy" },
  ];
  return (
    <div style={TOOLBAR}>
      <ZoomControl zoom={zoom} setZoom={setZoom} />
      {hasPlan && <Segmented label={t("View")} options={modes} value={mode}
                              onChange={setMode} />}
      {mode === "versions" && (
        <Segmented label="Density" options={densities} value={density}
                    onChange={setDensity} />
      )}
      <Summary data={data} mode={mode} t={t} locale={locale} />
    </div>
  );
}

const EMPTY = { padding: 40, color: "var(--fg-faint)", fontSize: 13 };

/* `initialZoom` / `initialDensity` / `initialMode` let a host (or a
 * render test) preset the controls, the same seam `I18nProvider` opens
 * with `initialLocale`; otherwise the chart remembers the reader's last
 * choice. The roadmap items are carried for the Plan's detail
 * panel, which looks up a selected bar's note by `req` (REQ-VIEWER-999).
 * implements: REQ-VIEWER-984 */
export function RoadmapView(props) {
  const { openSpec, initialZoom, initialDensity, initialMode } = props;
  const { t, locale } = useI18n();
  const history = props.initialHistory || HISTORY;
  const hasPlan = hasPlanFor(history);
  const [mode, setMode] = useStored(MODE_KEY, () =>
    initialMode || readStored(MODE_KEY, parseMode, null)
      || (hasPlan ? "plan" : "versions"));
  const { zoom, setZoom, canvasRef } = useCanvasZoom({
    storageKey: ZOOM_KEY,
    initialZoom: initialZoom != null ? clampZoom(initialZoom)
      : readStored(ZOOM_KEY, parseZoom, ZOOM_DEFAULT),
  });
  const [density, setDensity] = useStored(DENSITY_KEY, () =>
    initialDensity || readStored(DENSITY_KEY, parseDensity, "comfy"));
  const { onMouseDown, onClickCapture } = useDragPan(canvasRef);
  const data = buildVersions(REQUIREMENTS, TODOS, TARGETS);

  if (!data.milestones.length && !data.unscheduled.length && !hasPlan) {
    return (
      <div className="main" style={EMPTY}>
        No milestones yet. Add{" "}
        <code>milestone: v1.x</code>
        {" "}to requirement frontmatter
        or create a <code>TODO.md</code> with <code>## v1.x</code> sections.
      </div>
    );
  }
  const controls = { zoom, setZoom, mode, setMode, density, setDensity };
  const view = {
    d: DENSITY[density] || DENSITY.comfy, zoom, t, locale, openSpec,
  };
  return (
    <div className="main"
         style={{
           display: "flex", flexDirection: "column", overflow: "hidden",
         }}>
      <Toolbar controls={controls} data={data} hasPlan={hasPlan} t={t}
               locale={locale} />
      <div ref={canvasRef} onMouseDown={onMouseDown}
           onClickCapture={onClickCapture}
           className="canvas pan"
           style={{
             flex: 1, minHeight: 0, overflow: "auto", padding: "24px 20px",
           }}>
        {mode === "plan"
          ? <PlanGantt planning={TARGETS} history={history}
                       roadmap={props.initialRoadmap || ROADMAP}
                       branch={props.initialBranch || BRANCH}
                       locale={locale} t={t} zoom={zoom} openSpec={openSpec} />
          : <VersionsTable data={data} view={view} />}
      </div>
    </div>
  );
}

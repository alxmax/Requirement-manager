// implements: ARCH-VIEWER-007
/* RoadmapView — the dated Plan. Zoom is remembered per reader:
   it shrinks the chart and its scroll extent together. */
import {
  TARGETS, ROADMAP, HISTORY, BRANCH,
} from "../lib/data.js";
import { useI18n } from "../lib/i18n.jsx";
import { useDragPan } from "../lib/useDragPan.js";
import {
  ZoomControl, useCanvasZoom, clampZoom, ZOOM_DEFAULT, ZOOM_MIN,
  ZOOM_MAX,
} from "../lib/canvasZoom.jsx";
import { PlanGantt } from "./roadmap/PlanGantt.jsx";

const ZOOM_KEY = "reqmap.roadmap.zoom";

/* Guarded the way i18n.jsx guards its own: SSR (the smoke test) has no window,
 * and a file:// viewer in a hardened browser throws on the accessor itself. */
function readStored(key, parse, fallback) {
  try {
    if (typeof window === "undefined" || !window.localStorage) return fallback;
    const v = parse(window.localStorage.getItem(key));
    return v == null ? fallback : v;
  } catch { return fallback; }
}

const parseZoom = (v) => {
  const n = Number(v);
  return Number.isFinite(n) && n >= ZOOM_MIN && n <= ZOOM_MAX
    ? Math.round(n) : null;
};

function formatDue(iso, locale) {
  try {
    const d = new Date(`${iso}T12:00:00`);
    return d.toLocaleDateString(locale === "ro" ? "ro-RO" : "en-GB",
                                { day: "numeric", month: "short",
                                  year: "numeric" });
  } catch { return iso; }
}

function nextDue(targets) {
  const today = new Date().toISOString().slice(0, 10);
  const ms = targets?.milestones || {};
  return Object.entries(ms)
    .map(([name, meta]) => ({ ms: name, due: meta?.due }))
    .filter((x) => x.due && x.due >= today)
    .sort((a, b) => a.due.localeCompare(b.due))[0];
}

function Summary({ due, t, locale }) {
  if (!due) return null;
  return (
    <span style={{
      fontSize: 11, color: "var(--fg-faint)", marginLeft: "auto",
    }}>
      {t("next {ms} · due {date}",
        { ms: due.ms, date: formatDue(due.due, locale) })}
    </span>
  );
}

const TOOLBAR = {
  display: "flex", alignItems: "center", gap: 18, flexWrap: "wrap",
  padding: "10px 20px", borderBottom: "1px solid var(--border)",
  background: "var(--bg-raised)", flexShrink: 0,
};

/* `initialZoom` lets a host (or a render test) preset the scale, the
 * same seam `I18nProvider` opens with `initialLocale`; otherwise the
 * chart remembers the reader's last choice. The roadmap items are
 * carried for the Plan's detail panel, which looks up a selected bar's
 * note by `req` (REQ-VIEWER-999).
 * implements: REQ-VIEWER-984 */
export function RoadmapView(props) {
  const { openSpec, initialZoom } = props;
  const { t, locale } = useI18n();
  const history = props.initialHistory || HISTORY;
  const { zoom, setZoom, canvasRef } = useCanvasZoom({
    storageKey: ZOOM_KEY,
    initialZoom: initialZoom != null ? clampZoom(initialZoom)
      : readStored(ZOOM_KEY, parseZoom, ZOOM_DEFAULT),
  });
  const { onMouseDown, onClickCapture } = useDragPan(canvasRef);
  const due = nextDue(TARGETS);

  return (
    <div className="main"
         style={{
           display: "flex", flexDirection: "column", overflow: "hidden",
         }}>
      <div style={TOOLBAR}>
        <ZoomControl zoom={zoom} setZoom={setZoom} />
        <Summary due={due} t={t} locale={locale} />
      </div>
      <div ref={canvasRef} onMouseDown={onMouseDown}
           onClickCapture={onClickCapture}
           className="canvas pan"
           style={{
             flex: 1, minHeight: 0, overflow: "auto", padding: "24px 20px",
           }}>
        <div style={{ zoom: zoom / 100 }}>
          <PlanGantt planning={TARGETS} history={history}
                     roadmap={props.initialRoadmap || ROADMAP}
                     branch={props.initialBranch || BRANCH}
                     locale={locale} t={t} zoom={100} openSpec={openSpec} />
        </div>
      </div>
    </div>
  );
}

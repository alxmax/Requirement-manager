// implements: ARCH-VIEWER-007
/* RoadmapView — Gantt-style chart: semver milestones on X, swim lanes on Y.
   Requirements with `milestone:` field + TODO.md items via TODOS.

   One column per milestone and a chip carrying the full title made the table as
   wide as its longest title times its column count: 42 columns ran past 9000px,
   so a reader saw three versions at a time and panned for the rest. Two
   independent controls answer that, because they trade different things away —
   zoom shrinks everything including the type, density narrows the chip and
   keeps the type crisp. Both are remembered per reader. */
import { useEffect, useRef, useState } from "react";
import { REQUIREMENTS, TODOS } from "../lib/data.js";
import { useDragPan } from "../lib/useDragPan.js";

const ZOOM_MIN = 40, ZOOM_MAX = 150, ZOOM_DEFAULT = 100;
const ZOOM_KEY = "reqmap.roadmap.zoom";
const DENSITY_KEY = "reqmap.roadmap.density";

const clampZoom = z => Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, Math.round(z)));

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

const LANES      = ["bus", "feature", "need", "ops"];
const LANE_LABEL = { bus: "Bus", feature: "Feature", need: "Need", ops: "Ops" };

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

const ctrlBtn = {
  border: "none", cursor: "pointer", fontFamily: "inherit", background: "transparent",
  color: "var(--fg-muted)", padding: "3px 9px", fontSize: 12, lineHeight: 1.4,
};

function ZoomControl({ zoom, setZoom }) {  // implements: REQ-VIEWER-984
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
      <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.8px",
                     textTransform: "uppercase", color: "var(--fg-faint)" }}>Zoom</span>
      <span style={{ display: "inline-flex", alignItems: "center",
                     border: "1px solid var(--border)", borderRadius: 6, overflow: "hidden" }}>
        <button style={ctrlBtn} title="Zoom out" aria-label="Zoom out"
                onClick={() => setZoom(z => clampZoom(z / 1.1))}>−</button>
        <button
          onClick={() => setZoom(ZOOM_DEFAULT)}
          title="Reset to 100%"
          style={{ ...ctrlBtn, minWidth: 48, textAlign: "center", fontWeight: 700,
                   color: "var(--fg)", background: "var(--surface-hov)" }}
        >{`${zoom}%`}</button>
        <button style={ctrlBtn} title="Zoom in" aria-label="Zoom in"
                onClick={() => setZoom(z => clampZoom(z * 1.1))}>+</button>
      </span>
      <span style={{ fontSize: 10, color: "var(--fg-faint)" }}>ctrl + scroll</span>
    </span>
  );
}

function Segmented({ label, options, value, onChange }) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
      <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.8px",
                     textTransform: "uppercase", color: "var(--fg-faint)" }}>{label}</span>
      <span style={{ display: "inline-flex", border: "1px solid var(--border)", borderRadius: 6, overflow: "hidden" }}>
        {options.map(o => (
          <button
            key={o}
            onClick={() => onChange(o)}
            aria-pressed={o === value}
            style={{
              ...ctrlBtn, fontSize: 11,
              fontWeight: o === value ? 700 : 500,
              background: o === value ? "var(--surface-hov)" : "transparent",
              color: o === value ? "var(--fg)" : "var(--fg-muted)",
            }}
          >
            {o}
          </button>
        ))}
      </span>
    </span>
  );
}

/* `initialZoom` / `initialDensity` let a host (or a render test) preset the two
 * controls, the same seam `I18nProvider` opens with `initialLocale`; otherwise
 * the chart remembers the reader's last choice, and falls back to 100%/comfy. */
export function RoadmapView({ openSpec, initialZoom, initialDensity }) {  // implements: REQ-VIEWER-984
  const [showUnscheduled, setShowUnscheduled] = useState(false);
  const [zoom, setZoom] = useState(() => initialZoom != null ? clampZoom(initialZoom) : readStored(ZOOM_KEY, v => {
    const n = Number(v);
    return Number.isFinite(n) && n >= ZOOM_MIN && n <= ZOOM_MAX ? Math.round(n) : null;
  }, ZOOM_DEFAULT));
  const [density, setDensity] = useState(() => initialDensity || readStored(
    DENSITY_KEY, v => (v === "comfy" || v === "compact" ? v : null), "comfy"));
  const { ref, onMouseDown, onClickCapture } = useDragPan();
  // The wheel handler both reads and WRITES this, synchronously: a trackpad
  // flick delivers several wheel events inside one frame, and a ref synced only
  // at render would hand all of them the same stale zoom, collapsing the flick
  // into a single step. The effect keeps the button path in sync.
  const zoomRef = useRef(zoom);
  useEffect(() => { zoomRef.current = zoom; }, [zoom]);

  useEffect(() => {
    try { window.localStorage.setItem(ZOOM_KEY, String(zoom)); } catch { /* not fatal */ }
  }, [zoom]);
  useEffect(() => {
    try { window.localStorage.setItem(DENSITY_KEY, density); } catch { /* not fatal */ }
  }, [density]);

  /* Ctrl/⌘ + wheel zooms; a bare wheel still scrolls, because a table this wide
   * needs the wheel more than it needs a shortcut. Registered natively and
   * non-passive: React's onWheel cannot preventDefault, and without that the
   * browser's own page zoom fires instead. The point under the cursor is held
   * still, so zooming out to find a version does not lose the one you were on. */
  useEffect(() => {
    const el = ref.current;
    if (!el) return undefined;
    const onWheel = (e) => {
      if (!e.ctrlKey && !e.metaKey) return;
      e.preventDefault();
      const before = zoomRef.current;
      const after = clampZoom(before * (e.deltaY < 0 ? 1.1 : 1 / 1.1));
      if (after === before) return;
      const r = el.getBoundingClientRect();
      const cx = e.clientX - r.left, cy = e.clientY - r.top;
      const k = after / before;
      zoomRef.current = after;
      setZoom(after);
      // CSS `zoom` scales the scroll extent, so the anchor is plain arithmetic.
      el.scrollLeft = (el.scrollLeft + cx) * k - cx;
      el.scrollTop  = (el.scrollTop  + cy) * k - cy;
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, [ref]);

  const d = DENSITY[density] || DENSITY.comfy;

  const msSet = new Set();
  REQUIREMENTS.forEach(r => { if (r.milestone && r.status !== "deprecated") msSet.add(r.milestone); });
  TODOS.forEach(t => { if (!t.done && t.milestone) msSet.add(t.milestone); });
  const milestones = Array.from(msSet).sort(semverCmp);

  const current =
    milestones.find(ms => REQUIREMENTS.some(r => r.milestone === ms && r.status === "in-progress")) ||
    [...milestones].reverse().find(ms => REQUIREMENTS.some(r => r.milestone === ms && r.status === "confirmed"));

  // Unscheduled is a planning bucket, so it holds only what is planned AT the
  // planning levels. A `level: code` requirement is a decomposed clause of an
  // architecture requirement and inherits that parent's milestone; listing all
  // 618 of them here produced a wall of chips that said nothing about the plan.
  const unscheduled = REQUIREMENTS.filter(r => !r.milestone && r.status !== "deprecated" && r.level !== "code");

  if (!milestones.length && !unscheduled.length) {
    return (
      <div className="main" style={{ padding: 40, color: "var(--fg-faint)", fontSize: 13 }}>
        No milestones yet. Add <code>milestone: v1.x</code> to requirement frontmatter
        or create a <code>TODO.md</code> with <code>## v1.x</code> sections.
      </div>
    );
  }

  const rows = LANES.flatMap(lane => {
    const reqs  = REQUIREMENTS.filter(r => r.layer === lane && r.milestone && r.status !== "deprecated");
    const todos = TODOS.filter(t => t.lane === lane && !t.done);
    const byMs  = Object.fromEntries(milestones.map(ms => [ms, []]));
    reqs.forEach(r  => { if (byMs[r.milestone])  byMs[r.milestone].push({ type: "req",  r  }); });
    todos.forEach(t => { if (byMs[t.milestone])  byMs[t.milestone].push({ type: "todo", t  }); });
    const maxRows = Math.max(1, ...Object.values(byMs).map(a => a.length));
    return Array.from({ length: maxRows }, (_, i) => ({ lane, rowIdx: i, maxRows, byMs }));
  });

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
        <Segmented label="Density" options={["compact", "comfy"]} value={density} onChange={setDensity} />
        <span style={{ fontSize: 11, color: "var(--fg-faint)", marginLeft: "auto" }}>
          {milestones.length} milestones · {rows.length} lane rows
        </span>
      </div>

      <div ref={ref} onMouseDown={onMouseDown} onClickCapture={onClickCapture}
           className="canvas pan" style={{ flex: 1, minHeight: 0, overflow: "auto", padding: "24px 20px" }}>
        {/* CSS `zoom` (not `transform: scale`) so the scroll extent shrinks with
            the content — a transform leaves the container at full size and the
            reader pans across empty space to reach the last column. */}
        <div style={{ zoom: zoom / 100, width: "max-content" }}>
          <table style={{ borderCollapse: "separate", borderSpacing: 0, width: "max-content", minWidth: 560 }}>
            <thead>
              <tr>
                <th style={{ ...thBase, background: "transparent", border: "none", width: 60 }} />
                {milestones.map(ms => (
                  <th key={ms} style={{ ...thBase, ...(ms === current ? { background: "var(--surface-hov)", color: "var(--fg)", fontWeight: 700 } : {}) }}>
                    {ms}
                    {ms === current && (
                      <span style={{ display: "inline-block", width: 6, height: 6, background: "var(--accent-2)",
                        borderRadius: "50%", marginLeft: 5, verticalAlign: "middle", position: "relative", top: -1 }} />
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map(({ lane, rowIdx, maxRows, byMs }) => (
                <tr key={`${lane}-${rowIdx}`}>
                  {rowIdx === 0 && (
                    <td rowSpan={maxRows} style={{
                      fontSize: 10, fontWeight: 700, letterSpacing: "0.8px", textTransform: "uppercase",
                      color: "var(--fg-faint)", padding: d.lanePad, textAlign: "right", verticalAlign: "middle",
                      borderRight: "1px solid var(--border)", whiteSpace: "nowrap", background: "var(--bg-raised)", minWidth: 60,
                    }}>
                      {LANE_LABEL[lane]}
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
      </div>
    </div>
  );
}

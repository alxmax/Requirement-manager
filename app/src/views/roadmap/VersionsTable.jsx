// implements: ARCH-VIEWER-007
/* The Versions view: one column per version, one chip per item. */
import { useState } from "react";
import { barVariant } from "./versionsData.js";

// One lane. The Y axis carried four rows (bus/feature/need/ops — the
// ENGINE's taxonomy), then two, Bugs and Features, and Bugs rendered
// empty. An axis with one populated value sorts nothing while still
// costing a row, so the lane names what the chips are. Every open TODO
// item and every milestoned requirement lands in it, whatever `lane:` says.
const LANE_LABEL = "Implementations";   // implements: REQ-VIEWER-995

const ARROW =
  "polygon(0 0, calc(100% - 7px) 0, 100% 50%, calc(100% - 7px) 100%, 0 100%)";

/* The two densities differ only in numbers a reader can see the effect
 * of. `titleMax` is the one that reclaims width: a chip stops growing
 * with its title, and the full text moves to the tooltip `Bar` already
 * carries. */
export const DENSITY = {  // implements: REQ-VIEWER-984
  comfy:   { barH: 24, barPadL: 9, barGap: 5, font: 11, idFont: 9,
             cellPad: "6px 10px", headPad: "10px 14px", lanePad: "0 14px",
             titleMax: null },
  compact: { barH: 18, barPadL: 7, barGap: 4, font: 10, idFont: 9,
             cellPad: "3px 5px",  headPad: "6px 8px",   lanePad: "0 8px",
             titleMax: 108 },
};

const dashed = "1.5px dashed var(--amber-400)";
const VARIANT = {
  done: { background: "var(--cov-tested-bg)", color: "var(--cov-tested)",
          dot: "var(--cov-tested)", clipPath: ARROW, arrow: true },
  progress: { background: "var(--indigo-tint)", color: "var(--indigo-500)",
              dot: "var(--indigo-400)", clipPath: ARROW, arrow: true },
  draft: { background: "var(--amber-tint)", color: "var(--amber-700)",
           dot: "var(--amber-600)", border: dashed },
  planned: { background: "var(--surface-hov)", color: "var(--fg-muted)",
             dot: "var(--fg-faint)", clipPath: ARROW, arrow: true },
  todo: { background: "var(--amber-tint)", color: "var(--amber-700)",
          dot: "var(--amber-600)", border: dashed },
};

export function formatDue(iso, locale) {
  try {
    const d = new Date(`${iso}T12:00:00`);
    return d.toLocaleDateString(locale === "ro" ? "ro-RO" : "en-GB",
                                { day: "numeric", month: "short",
                                  year: "numeric" });
  } catch { return iso; }
}

function dueColor(iso) {
  const today = new Date().toISOString().slice(0, 10);
  if (iso < today) return "var(--status-error)";
  if (iso === today) return "var(--status-drift)";
  return "var(--fg-faint)";
}

function chipStyle(v, d, clickable) {
  // The arrow clip eats the right edge, so an arrow chip needs the padding
  // back.
  const padR = v.arrow ? d.barPadL + 11 : d.barPadL + 3;
  return {
    display: "inline-flex", alignItems: "center", gap: d.barGap,
    height: d.barH, borderRadius: 5, padding: `0 ${padR}px 0 ${d.barPadL}px`,
    fontSize: d.font, fontWeight: 500, whiteSpace: "nowrap",
    cursor: clickable ? "pointer" : "default", clipPath: v.clipPath,
    background: v.background, color: v.color, border: v.border,
    maxWidth: d.titleMax ? d.titleMax + 60 : undefined,
  };
}

const DOT = { width: 5, height: 5, borderRadius: "50%", flexShrink: 0 };

export function Bar({ variant, id, label, onClick, d }) {
  const v = VARIANT[variant] || VARIANT.planned;
  const idStyle = { fontSize: d.idFont, opacity: 0.5, fontWeight: 600,
                    letterSpacing: "0.3px", flexShrink: 0 };
  const titleStyle = d.titleMax
    ? { maxWidth: d.titleMax, overflow: "hidden", textOverflow: "ellipsis" }
    : undefined;
  return (
    <span title={label} onClick={onClick} style={chipStyle(v, d, onClick)}>
      <span style={{ ...DOT, background: v.dot }} />
      {id && <span style={idStyle}>{id}</span>}
      <span style={titleStyle}>{label}</span>
    </span>
  );
}

function headStyle(d, isCurrent) {
  const base = {
    background: "var(--bg-raised)", color: "var(--fg-muted)", fontSize: 11,
    fontWeight: 600, letterSpacing: "0.4px", padding: d.headPad,
    textAlign: "center", whiteSpace: "nowrap",
    borderBottom: "1px solid var(--border)",
    borderRight: "1px solid var(--border)",
  };
  if (!isCurrent) return base;
  return { ...base, background: "var(--surface-hov)", color: "var(--fg)",
           fontWeight: 700 };
}

const CURRENT_DOT = {
  display: "inline-block", width: 6, height: 6, background: "var(--accent-2)",
  borderRadius: "50%", marginLeft: 5, verticalAlign: "middle",
  position: "relative", top: -1,
};
const LABEL_STYLE = {
  fontSize: 9, fontWeight: 400, color: "var(--fg-faint)", marginTop: 2,
  maxWidth: 140, overflow: "hidden", textOverflow: "ellipsis",
};

function VersionHead({ ms, data, d, t, locale }) {
  const meta = data.msMeta[ms] || {};
  const isCurrent = ms === data.current;
  return (
    <th style={headStyle(d, isCurrent)}>
      <div>{ms}{isCurrent && <span style={CURRENT_DOT} />}</div>
      {meta.due && (
        <div style={{ fontSize: 9, fontWeight: 500,
                      color: dueColor(meta.due), marginTop: 3 }}>
          {t("due {date}", { date: formatDue(meta.due, locale) })}
        </div>
      )}
      {meta.label && (
        <div style={LABEL_STYLE} title={meta.label}>{meta.label}</div>
      )}
    </th>
  );
}

function ItemChip({ item, d, openSpec }) {
  if (item?.type === "req") {
    return <Bar variant={barVariant(item.r.status)} id={item.r.id}
                label={item.r.title}
                onClick={() => openSpec(item.r.id)} d={d} />;
  }
  const idle = () => {};
  if (item?.type === "todo") {
    return <Bar variant="todo" label={item.t.name} onClick={idle} d={d} />;
  }
  if (item?.type === "plan") {
    return <Bar variant="planned" label={item.text} onClick={idle} d={d} />;
  }
  return null;
}

function laneCellStyle(d) {
  return {
    fontSize: 10, fontWeight: 700, letterSpacing: "0.8px",
    textTransform: "uppercase", color: "var(--fg-faint)", padding: d.lanePad,
    textAlign: "right", verticalAlign: "middle",
    borderRight: "1px solid var(--border)", whiteSpace: "nowrap",
    background: "var(--bg-raised)", minWidth: 60,
  };
}

function Row({ rowIdx, data, d, openSpec }) {
  const cell = {
    padding: d.cellPad, borderBottom: "1px solid var(--border-soft)",
    borderRight: "1px solid var(--border-soft)", background: "var(--surface)",
    verticalAlign: "middle",
  };
  return (
    <tr>
      {rowIdx === 0 && (
        <td rowSpan={data.maxRows} style={laneCellStyle(d)}>{LANE_LABEL}</td>
      )}
      {data.milestones.map((ms) => (
        <td key={ms} style={cell}>
          <ItemChip item={data.byMs[ms][rowIdx]} d={d} openSpec={openSpec} />
        </td>
      ))}
    </tr>
  );
}

function Unscheduled({ data, d, openSpec }) {
  const [open, setOpen] = useState(false);
  const items = data.unscheduled;
  if (!items.length) return null;
  const toggle = { background: "none", border: "none", cursor: "pointer",
                   padding: "4px 0", color: "var(--fg-faint)", fontSize: 12,
                   fontFamily: "inherit" };
  return (
    <div style={{ marginTop: 16 }}>
      <button onClick={() => setOpen((s) => !s)} style={toggle}>
        {open ? "▾" : "▸"} Unscheduled ({items.length})
      </button>
      {open && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6,
                      marginTop: 8, padding: "0 4px" }}>
          {items.map((r) => (
            <Bar key={r.id} variant={barVariant(r.status)} id={r.id}
                 label={r.title}
                 onClick={() => openSpec(r.id)} d={d} />
          ))}
        </div>
      )}
    </div>
  );
}

/** One column per version. CSS `zoom` (not `transform: scale`) so the
 *  scroll extent shrinks with the content — a transform leaves the
 *  container at full size and the reader pans across empty space to
 *  reach the last column. */
export function VersionsTable({ data, view }) {
  const { d, zoom, t, locale, openSpec } = view;
  const rows = Array.from({ length: data.maxRows }, (_, i) => i);
  const corner = { ...headStyle(d, false), background: "transparent",
                   border: "none", width: 60 };
  return (
    <div style={{ zoom: zoom / 100, width: "max-content" }}>
      <table style={{ borderCollapse: "separate", borderSpacing: 0,
                      width: "max-content", minWidth: 560 }}>
        <thead>
          <tr>
            <th style={corner} />
            {data.milestones.map((ms) => (
              <VersionHead key={ms} ms={ms} data={data} d={d} t={t}
                           locale={locale} />
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((i) => (
            <Row key={i} rowIdx={i} data={data} d={d} openSpec={openSpec} />
          ))}
        </tbody>
      </table>
      <Unscheduled data={data} d={d} openSpec={openSpec} />
    </div>
  );
}

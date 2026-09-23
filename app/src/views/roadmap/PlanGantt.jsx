// implements: ARCH-VIEWER-007
/* Calendar Gantt: months, ISO weeks and days on X, swimlanes on Y.
 * Selecting a bar, a version or a shipped month opens its note below
 * (REQ-VIEWER-999). The positions come from `ganttLayout.js`; this file
 * only holds the selection and puts the parts together. */
import { useState } from "react";
import { layoutPlan } from "./ganttLayout.js";
import { LaneLabels, Ruler } from "./GanttRuler.jsx";
import { Guides, Lane, ShippedBand } from "./GanttLanes.jsx";
import { PickedNote } from "./PlanNotes.jsx";

export { noteText, matchItem, ShippedNote, VersionNote } from "./PlanNotes.jsx";

export function PlanGantt(props) {
  const {
    planning, history, roadmap, branch, locale, t, zoom, openSpec,
  } = props;
  const [picked, setPicked] = useState(null);
  // One selection for bars, shipped months and versions alike; selecting
  // the open one again closes its note.
  const toggle = (item) =>
    setPicked((cur) => (cur && cur.key === item.key ? null : item));
  const lay = layoutPlan(planning, history, locale);
  if (!lay) {
    return (
      <div style={{ padding: 40, color: "var(--fg-faint)", fontSize: 13 }}>
        {t("Add milestones with due dates or bars in _planning.json.")}
      </div>
    );
  }
  const sel = { lay, picked, toggle };
  /* No `overflow: hidden` on the bordered box: it made the box the sticky
     column's scrollport, and a scrollport that never scrolls never lets
     its sticky child stick. `flex: 1` lets the track take the room the
     lane column leaves; `minWidth: chartW` keeps a longer plan at its
     true scale and scrolls (REQ-PLANSTACK-1012). The note is sticky for
     the same reason as the column: it belongs to the reader, not to the
     month. */
  return (
    <div style={{ zoom: zoom / 100, width: "max-content",
                 minWidth: "100%" }}>
      <div style={{ display: "flex", border: "1px solid var(--border)",
        borderRadius: 8,
        background: "var(--surface)" }}>
        <LaneLabels lay={lay} branch={branch} t={t} />
        <div style={{ position: "relative", minWidth: lay.chartW, flex: 1 }}>
          <Ruler lay={lay} t={t} />
          <ShippedBand sel={sel} t={t} />
          {lay.lanes.map((ln, i) => <Lane key={ln} ln={ln} i={i} sel={sel} />)}
          <Guides guides={lay.guides} />
        </div>
      </div>
      {picked && (
        <div style={{ position: "sticky", left: 0, width: "min(760px, 100%)" }}>
          <PickedNote picked={picked} lay={lay} roadmap={roadmap} t={t}
                      openSpec={openSpec}
                      onPick={setPicked} />
        </div>
      )}
    </div>
  );
}

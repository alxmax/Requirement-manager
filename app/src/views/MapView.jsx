// implements: ARCH-VIEWER-007
import { useState, useMemo, useEffect } from "react";
import { REQUIREMENTS, REQ_BY_ID } from "../lib/data.js";
import { computeLayout, NODE_W } from "../lib/layout.js";
import { useI18n } from "../lib/i18n.jsx";
import { useDragPan } from "../lib/useDragPan.js";
import { ZoomControl, useCanvasZoom } from "../lib/canvasZoom.jsx";
import {
  MapNodeBox, MapEdges, MapCanvas, MapDetailPanel, ReqCodeView,
} from "./map/MapParts.jsx";

const MAP_TABS = [
  { key: "system", label: "System Map" },
  { key: "reqcode", label: "Req→Code" },
  { key: "deps", label: "Dependencies" },
  { key: "risk", label: "Risk" },
];

/** How a node is shown under the current selection. */
function marksFor(id, sel, riskClass) {
  return {
    selected: sel.selId === id, highlighted: sel.highlightId === id,
    edgeEnd: sel.edgeEnds && sel.edgeEnds.has(id), riskClass,
  };
}

/** One zoomable map. `sel` is the selection every map shares: `selId`,
 *  `setSelId`, `highlightId`, `edgeEnds`, `selKey` and `setSelEdge`. */
function ZoomedCanvas({ meta, label, markerId, extraNodes, sel }) {
  const { zoom, setZoom, canvasRef, fitToView } = useCanvasZoom();
  const { onMouseDown, onClickCapture } = useDragPan(canvasRef);
  const fit = () => fitToView(meta.width, meta.height);
  useEffect(() => { fitToView(meta.width, meta.height); },
    [meta.width, meta.height, fitToView]);
  const pan = { canvasRef, onMouseDown, onClickCapture };
  return (
    <div className="map-main">
      <div className="map-toolbar">
        <ZoomControl zoom={zoom} setZoom={setZoom} onFit={fit} fitLabel="Fit" />
      </div>
      <MapCanvas size={meta} zoom={zoom} pan={pan}
                 onClear={() => sel.setSelEdge(null)}>
        {label
          && <div className="subgraph-label" style={{ left: 50, top: 12 }}>
            {label}
          </div>}
        <MapEdges meta={meta} selKey={sel.selKey} onSelect={sel.setSelEdge}
                  markerId={markerId} />
        {REQUIREMENTS.filter((r) => meta.pos[r.id]).map((r) => (
          <MapNodeBox key={r.id} r={r} pos={meta.pos}
                      marks={marksFor(r.id, sel)}
                      onClick={sel.setSelId} />
        ))}
        {extraNodes}
      </MapCanvas>
    </div>
  );
}

/** Coupling between areas: one pseudo-node per id area, an edge where one
 *  depends on another. */
function areaGraph(nodes) {
  const idArea = {}, byArea = {};
  nodes.forEach((r) => {
    const a = r.area || "?";
    idArea[r.id] = a;
    (byArea[a] = byArea[a] || []).push(r.id);
  });
  const pairs = new Set();
  nodes.forEach((r) => (r.deps || []).forEach((d) => {
    const x = idArea[r.id], y = idArea[d];
    if (x && y && x !== y) pairs.add(x + "\u0001" + y);
  }));
  const pseudo = Object.keys(byArea).map((a) => ({
    id: a,
    deps: [...pairs].filter((e) => e.startsWith(a + "\u0001"))
      .map((e) => e.split("\u0001")[1]),
  }));
  return {
    layout: computeLayout(pseudo, { colW: 320, rowH: 150 }), count: byArea,
  };
}

/** The graphs the map tabs draw, laid out once. The code level is read in
 *  the Explorer. */
function useMapGraphs() {
  const nodes = useMemo(
    () => REQUIREMENTS.filter((r) => r.level !== "code"), [REQUIREMENTS]);
  const sys = useMemo(() => computeLayout(nodes), [nodes]);
  const flagged = useMemo(
    () => nodes.filter((r) => (r.risks || []).length > 0), [nodes]);
  const risk = useMemo(
    () => computeLayout(flagged, { colW: 300, rowH: 150 }), [flagged]);
  const deps = useMemo(() => areaGraph(nodes), [nodes]);
  return { nodes, sys, flagged, risk, deps };
}

const BUS_SWATCH = {
  width: 10, height: 10, borderRadius: 3, background: "var(--status-bus-bg)",
  border: "1.5px solid var(--status-bus)", display: "inline-block",
};
const LEGEND = {
  system: <>
    <span className="pdot" style={BUS_SWATCH} />
    {" "}bus · arrows = depends_on · edge colour = source
  </>,
  reqcode: <>
    requirement → its code ·{" "}
    <span style={{ color: "var(--accent)" }}>implements</span>
    {" "}/ tested-by
  </>,
  deps: <>area-level coupling · arrow A→B = A depends on B</>,
  risk: <>only requirements with ≥1 open risk signal</>,
};

function areaNodes(deps) {
  return Object.keys(deps.count).map((area) => {
    const p = deps.layout.pos[area];
    if (!p) return null;
    return (
      <div key={area} className="node"
           style={{ left: p[0], top: p[1], width: NODE_W }}>
        <span className="nt">{area}</span>
        <span className="ni">{deps.count[area].length} caps</span>
      </div>
    );
  });
}

function riskClassOf(r) {
  const sig = r.risks[0]?.signal;
  if (sig === "unimplemented") return "risk-error";
  return sig === "drift" || sig === "blast-radius" || sig === "unreviewed"
    ? "risk-blast" : "";
}

function riskNodes(g, sel) {
  return g.flagged.filter((r) => g.risk.pos[r.id]).map((r) => (
    <MapNodeBox key={r.id} r={r} pos={g.risk.pos}
                marks={marksFor(r.id, sel, riskClassOf(r))}
                onClick={sel.setSelId} />
  ));
}

/** Scroll the selected node into view and flash it. */
function locateNode(selId, setHighlightId) {
  if (!selId) return;
  setHighlightId(selId);
  setTimeout(() => {
    const el = document.querySelector(".node.hl");
    if (el) {
      el.scrollIntoView(
        { behavior: "smooth", block: "center", inline: "center" });
    }
  }, 60);
  setTimeout(() => setHighlightId(null), 2200);
}

function MapTabs({ tab, pick, hiddenCode, t }) {
  return (
    <div className="tabbar">
      {MAP_TABS.map((mt) => (
        <button key={mt.key} className={"tab" + (tab === mt.key ? " on" : "")}
          onClick={() => pick(mt.key)}>{t(mt.label)}</button>
      ))}
      <div className="tab-legend">
        {hiddenCode > 0 && (
          <span className="map-scope"
                title="the code level is read in the Explorer, not drawn here">
            {t("system + architecture · {n} code-level hidden",
              { n: hiddenCode })}
          </span>
        )}
        {LEGEND[tab]}
      </div>
    </div>
  );
}

function MapBody({ tab, g, sel }) {
  if (tab === "system") {
    return <ZoomedCanvas meta={g.sys} markerId="arrow-sys" sel={sel}
      label={"consumers → depends on → foundation · drag to pan · "
        + "click a line to trace it"} />;
  }
  if (tab === "reqcode") {
    return <ReqCodeView selId={sel.selId} setSelId={sel.setSelId}
                        rows={g.nodes} />;
  }
  if (tab === "deps") {
    return <ZoomedCanvas meta={g.deps.layout} markerId="arrow-deps" sel={sel}
                         extraNodes={areaNodes(g.deps)} />;
  }
  return <ZoomedCanvas meta={g.risk} markerId="arrow-risk" sel={sel}
    label={g.flagged.length === 0 ? "no open risk signals 🎉" : null}
    extraNodes={riskNodes(g, sel)} />;
}

export function MapView({
  selId, setSelId, openSpec, highlightId, setHighlightId,
}) {
  const { t } = useI18n();
  const [tab, setTab] = useState("system");
  const [selEdge, setSelEdge] = useState(null);
  const g = useMapGraphs();
  const current = selId ? REQ_BY_ID[selId] : null;
  const sel = {
    selId, setSelId, highlightId, setSelEdge,
    selKey: selEdge ? selEdge[0] + "|" + selEdge[1] : null,
    edgeEnds: selEdge ? new Set(selEdge) : null,
  };
  const pick = (key) => { setTab(key); setSelEdge(null); };
  return (
    <div className="main">
      <MapTabs tab={tab} pick={pick}
               hiddenCode={REQUIREMENTS.length - g.nodes.length} t={t} />
      <div className={"map-wrap" + (current ? " with-panel" : "")}>
        <MapBody tab={tab} g={g} sel={sel} />
        {current && <MapDetailPanel r={current} onClose={() => setSelId(null)}
          onLocate={() => locateNode(selId, setHighlightId)}
          onOpenSpec={openSpec} />}
      </div>
    </div>
  );
}

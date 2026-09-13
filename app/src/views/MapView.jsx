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

function ZoomedCanvas({ meta, label, markerId, codeCounts, selId, setSelId, highlightId, edgeEnds, selKey, setSelEdge, extraNodes }) {
  const { zoom, setZoom, canvasRef, fitToView } = useCanvasZoom();
  const { onMouseDown, onClickCapture } = useDragPan(canvasRef);
  useEffect(() => { fitToView(meta.width, meta.height); }, [meta.width, meta.height, fitToView]);

  return (
    <div className="map-main">
      <div className="map-toolbar">
        <ZoomControl zoom={zoom} setZoom={setZoom} onFit={() => fitToView(meta.width, meta.height)} fitLabel="Fit" />
      </div>
      <MapCanvas width={meta.width} height={meta.height} zoom={zoom} canvasRef={canvasRef}
        onMouseDown={onMouseDown} onClickCapture={onClickCapture} onClear={() => setSelEdge(null)}>
        {label && <div className="subgraph-label" style={{ left: 50, top: 12 }}>{label}</div>}
        <MapEdges meta={meta} selKey={selKey} onSelect={setSelEdge} markerId={markerId} />
        {REQUIREMENTS.filter((r) => meta.pos[r.id]).map((r) => (
          <MapNodeBox key={r.id} r={r} pos={meta.pos} selected={selId === r.id}
            highlighted={highlightId === r.id} edgeEnd={edgeEnds && edgeEnds.has(r.id)}
            codeCount={codeCounts && codeCounts[r.id]} onClick={setSelId} />
        ))}
        {extraNodes}
      </MapCanvas>
    </div>
  );
}

export function MapView({ selId, setSelId, openSpec, highlightId, setHighlightId }) {
  const { t } = useI18n();
  const [tab, setTab] = useState("system");
  const [selEdge, setSelEdge] = useState(null);
  const sel = selId ? REQ_BY_ID[selId] : null;
  const selKey = selEdge ? selEdge[0] + "|" + selEdge[1] : null;
  const edgeEnds = selEdge ? new Set(selEdge) : null;

  const NODES = useMemo(() => REQUIREMENTS.filter((r) => r.level !== "code"), [REQUIREMENTS]);
  const sys = useMemo(() => computeLayout(NODES), [NODES]);
  const flagged = useMemo(() => NODES.filter((r) => (r.risks || []).length > 0), [NODES]);
  const riskLayout = useMemo(() => computeLayout(flagged, { colW: 300, rowH: 150 }), [flagged]);

  const depsGraph = useMemo(() => {
    const idArea = {}, byArea = {};
    NODES.forEach((r) => { const a = r.area || "?"; idArea[r.id] = a; (byArea[a] = byArea[a] || []).push(r.id); });
    const ae = new Set();
    NODES.forEach((r) => (r.deps || []).forEach((d) => {
      const x = idArea[r.id], y = idArea[d];
      if (x && y && x !== y && idArea[d]) ae.add(x + "\u0001" + y);
    }));
    const pseudo = Object.keys(byArea).map((a) => ({
      id: a, deps: [...ae].filter((e) => e.startsWith(a + "\u0001")).map((e) => e.split("\u0001")[1]),
    }));
    return { layout: computeLayout(pseudo, { colW: 320, rowH: 150 }), count: byArea };
  }, [NODES]);

  const legend = {
    system: <><span className="pdot" style={{ width: 10, height: 10, borderRadius: 3, background: "var(--status-bus-bg)", border: "1.5px solid var(--status-bus)", display: "inline-block" }} /> bus · arrows = depends_on · edge colour = source</>,
    reqcode: <>requirement → its code · <span style={{ color: "var(--accent)" }}>implements</span> / tested-by</>,
    deps: <>area-level coupling · arrow A→B = A depends on B</>,
    risk: <>only requirements with ≥1 open risk signal</>,
  }[tab];
  const hiddenCode = REQUIREMENTS.length - NODES.length;

  function locate() {
    if (!selId) return;
    setHighlightId(selId);
    setTimeout(() => {
      const el = document.querySelector(".node.hl");
      if (el) el.scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });
    }, 60);
    setTimeout(() => setHighlightId(null), 2200);
  }

  const canvasProps = { selId, setSelId, highlightId, edgeEnds, selKey, setSelEdge };

  const depsNodes = Object.keys(depsGraph.count).map((area) => {
    const p = depsGraph.layout.pos[area];
    if (!p) return null;
    return (
      <div key={area} className="node" style={{ left: p[0], top: p[1], width: NODE_W }}>
        <span className="nt">{area}</span>
        <span className="ni">{depsGraph.count[area].length} caps</span>
      </div>
    );
  });

  const riskNodes = flagged.filter((r) => riskLayout.pos[r.id]).map((r) => {
    const sig = r.risks[0]?.signal;
    const rc = sig === "unimplemented" ? "risk-error"
      : (sig === "drift" || sig === "blast-radius" || sig === "unreviewed") ? "risk-blast" : "";
    return (
      <MapNodeBox key={r.id} r={r} pos={riskLayout.pos} selected={selId === r.id}
        highlighted={highlightId === r.id} edgeEnd={edgeEnds && edgeEnds.has(r.id)}
        riskClass={rc} onClick={setSelId} />
    );
  });

  return (
    <div className="main">
      <div className="tabbar">
        {MAP_TABS.map((mt) => (
          <button key={mt.key} className={"tab" + (tab === mt.key ? " on" : "")}
            onClick={() => { setTab(mt.key); setSelEdge(null); }}>{t(mt.label)}</button>
        ))}
        <div className="tab-legend">
          {hiddenCode > 0 && (
            <span className="map-scope" title="the code level is read in the Explorer, not drawn here">
              {t("system + architecture · {n} code-level hidden", { n: hiddenCode })}
            </span>
          )}
          {legend}
        </div>
      </div>

      <div className={"map-wrap" + (sel ? " with-panel" : "")}>
        {tab === "system" && (
          <ZoomedCanvas meta={sys} markerId="arrow-sys"
            label="consumers → depends on → foundation · drag to pan · click a line to trace it" {...canvasProps} />
        )}
        {tab === "reqcode" && <ReqCodeView selId={selId} setSelId={setSelId} rows={NODES} />}
        {tab === "deps" && (
          <ZoomedCanvas meta={depsGraph.layout} markerId="arrow-deps" extraNodes={depsNodes} {...canvasProps} />
        )}
        {tab === "risk" && (
          <ZoomedCanvas meta={riskLayout} markerId="arrow-risk"
            label={flagged.length === 0 ? "no open risk signals 🎉" : null}
            extraNodes={riskNodes} {...canvasProps} />
        )}
        {sel && <MapDetailPanel r={sel} onClose={() => setSelId(null)} onLocate={locate} onOpenSpec={openSpec} />}
      </div>
    </div>
  );
}

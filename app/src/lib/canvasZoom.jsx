// implements: ARCH-VIEWER-007
/* Shared canvas zoom — Map and Roadmap both pan wide surfaces and need the same
 * ctrl+wheel zoom, persisted level, and fit-to-view. Extracted from RoadmapView
 * so MapView does not fork a second copy. */
import { useEffect, useRef, useState, useCallback } from "react";

export const ZOOM_MIN = 40;
export const ZOOM_MAX = 150;
export const ZOOM_DEFAULT = 100;
export const MAP_ZOOM_KEY = "reqmap.map.zoom";

export const clampZoom = (z) => Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, Math.round(z)));

export const ctrlBtn = {
  border: "none", cursor: "pointer", fontFamily: "inherit", background: "transparent",
  color: "var(--fg-muted)", padding: "3px 9px", fontSize: 12, lineHeight: 1.4,
};

function readStoredZoom(key, fallback) {
  try {
    if (typeof window === "undefined" || !window.localStorage) return fallback;
    const n = Number(window.localStorage.getItem(key));
    return Number.isFinite(n) && n >= ZOOM_MIN && n <= ZOOM_MAX ? Math.round(n) : fallback;
  } catch { return fallback; }
}

export function ZoomControl({ zoom, setZoom, onFit, fitLabel = "Fit" }) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
      <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.8px",
        textTransform: "uppercase", color: "var(--fg-faint)" }}>Zoom</span>
      <span style={{ display: "inline-flex", alignItems: "center",
        border: "1px solid var(--border)", borderRadius: 6, overflow: "hidden" }}>
        <button style={ctrlBtn} title="Zoom out" aria-label="Zoom out"
          onClick={() => setZoom((z) => clampZoom(z / 1.1))}>−</button>
        <button
          onClick={() => setZoom(ZOOM_DEFAULT)}
          title="Reset to 100%"
          style={{ ...ctrlBtn, minWidth: 48, textAlign: "center", fontWeight: 700,
            color: "var(--fg)", background: "var(--surface-hov)" }}
        >{`${zoom}%`}</button>
        <button style={ctrlBtn} title="Zoom in" aria-label="Zoom in"
          onClick={() => setZoom((z) => clampZoom(z * 1.1))}>+</button>
      </span>
      {onFit && (
        <button style={{ ...ctrlBtn, border: "1px solid var(--border)", borderRadius: 6,
          padding: "3px 12px", fontWeight: 600, color: "var(--fg)" }}
          title="Fit the graph in view" onClick={onFit}>{fitLabel}</button>
      )}
      <span style={{ fontSize: 10, color: "var(--fg-faint)" }}>ctrl + scroll</span>
    </span>
  );
}

/** Zoom state + wheel handler + fit-to-view for a scrollable canvas ref. */
export function useCanvasZoom({ storageKey = MAP_ZOOM_KEY, initialZoom } = {}) {
  const [zoom, setZoom] = useState(() => (
    initialZoom != null ? clampZoom(initialZoom) : readStoredZoom(storageKey, ZOOM_DEFAULT)
  ));
  const zoomRef = useRef(zoom);
  const canvasRef = useRef(null);

  useEffect(() => { zoomRef.current = zoom; }, [zoom]);
  useEffect(() => {
    try { window.localStorage.setItem(storageKey, String(zoom)); } catch { /* not fatal */ }
  }, [zoom, storageKey]);

  useEffect(() => {
    const el = canvasRef.current;
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
      el.scrollLeft = (el.scrollLeft + cx) * k - cx;
      el.scrollTop = (el.scrollTop + cy) * k - cy;
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, [canvasRef]);

  const fitToView = useCallback((contentWidth, contentHeight, padding = 48) => {
    const el = canvasRef.current;
    if (!el || !contentWidth || !contentHeight) return;
    const vw = el.clientWidth - padding;
    const vh = el.clientHeight - padding;
    const scale = Math.min(vw / contentWidth, vh / contentHeight, 1);
    const next = clampZoom(scale * 100);
    zoomRef.current = next;
    setZoom(next);
    el.scrollLeft = 0;
    el.scrollTop = 0;
  }, []);

  return { zoom, setZoom, canvasRef, fitToView };
}

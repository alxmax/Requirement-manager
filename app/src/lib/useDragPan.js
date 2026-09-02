// implements: ARCH-VIEWER-007
/* useDragPan — shared grab-to-pan behavior for a scrollable container: drag
 * anywhere to scroll; a real click (no drag) still falls through to whatever
 * the container renders (node/edge/bar selection). A drag past a small
 * threshold is swallowed in the capture phase so it never triggers a click.
 * Extracted from MapView's Canvas and RoadmapView, which had drifted into
 * two copies of the same mouse-handler logic. */
import { useRef } from "react";

export function useDragPan() {
  const ref = useRef(null);
  const drag = useRef(null);

  function onMouseDown(e) {
    if (e.button !== 0) return;
    const el = ref.current; if (!el) return;
    const d = { x: e.clientX, y: e.clientY, sl: el.scrollLeft, st: el.scrollTop, moved: false };
    drag.current = d;
    const move = (ev) => {
      const dx = ev.clientX - d.x, dy = ev.clientY - d.y;
      if (!d.moved && Math.abs(dx) + Math.abs(dy) > 4) { d.moved = true; el.classList.add("grabbing"); }
      if (d.moved) { el.scrollLeft = d.sl - dx; el.scrollTop = d.st - dy; }
    };
    const up = () => {
      document.removeEventListener("mousemove", move);
      document.removeEventListener("mouseup", up);
      el.classList.remove("grabbing");
      setTimeout(() => { drag.current = null; }, 0);
    };
    document.addEventListener("mousemove", move);
    document.addEventListener("mouseup", up);
  }

  function onClickCapture(e) {
    if (drag.current && drag.current.moved) { e.stopPropagation(); e.preventDefault(); }
  }

  return { ref, onMouseDown, onClickCapture };
}

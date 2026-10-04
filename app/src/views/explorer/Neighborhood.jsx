// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-942
import { useEffect, useRef } from "react";
import { REQ_BY_ID } from "../../lib/data.js";
import { useI18n } from "../../lib/i18n.jsx";

const CAP = 4;

function known(ids) {
  return (ids || []).filter((id) => REQ_BY_ID[id]);
}

function Card({ id, selected, onNav }) {
  const r = REQ_BY_ID[id];
  const cls = "neigh-card"
    + (r.layer === "bus" ? " bus" : "")
    + (selected ? " sel" : "");
  return (
    <button type="button" className={cls} data-neigh={id}
            onClick={selected ? undefined : () => onNav(id)}>
      <span className="nt">{r.title}</span>
      <span className="ni">{r.id}</span>
    </button>
  );
}

function Side({ label, ids, empty, onNav, side }) {
  const shown = ids.slice(0, CAP);
  const more = ids.length - shown.length;
  return (
    <div className={"neigh-side " + side}>
      <div className="neigh-k">{label}</div>
      {shown.map((id) => <Card key={id} id={id} onNav={onNav} />)}
      {more > 0 && <div className="neigh-more">+{more}</div>}
      {shown.length === 0 && <div className="neigh-empty">{empty}</div>}
    </div>
  );
}

function point(el, edge, box) {
  const r = el.getBoundingClientRect();
  const x = edge === "left" ? r.left
    : edge === "right" ? r.right
    : r.left + r.width / 2;
  const y = edge === "top" ? r.top
    : edge === "bottom" ? r.bottom
    : r.top + r.height / 2;
  return { x: x - box.left, y: y - box.top };
}

function draw(root) {
  const svg = root.querySelector("svg");
  const hub = root.querySelector(".neigh-card.sel");
  if (!svg || !hub) return;
  const box = root.getBoundingClientRect();
  svg.setAttribute("width", String(root.clientWidth));
  svg.setAttribute("height", String(root.clientHeight));
  const path = (a, b, vertical) => {
    const c = vertical
      ? `${a.x},${(a.y + b.y) / 2} ${b.x},${(a.y + b.y) / 2}`
      : `${(a.x + b.x) / 2},${a.y} ${(a.x + b.x) / 2},${b.y}`;
    return `<path d="M${a.x},${a.y} C${c} ${b.x},${b.y}" `
      + `fill="none" stroke="var(--accent)" stroke-width="1.4" `
      + `marker-end="url(#neigh-arrow)"/>`;
  };
  const link = (from, to) => {
    const a = from.getBoundingClientRect();
    const b = to.getBoundingClientRect();
    const vertical = Math.abs((b.top + b.height / 2) - (a.top + a.height / 2))
      > Math.abs((b.left + b.width / 2) - (a.left + a.width / 2));
    const down = (b.top + b.height / 2) > (a.top + a.height / 2);
    const right = (b.left + b.width / 2) > (a.left + a.width / 2);
    const fromEdge = vertical
      ? (down ? "bottom" : "top") : (right ? "right" : "left");
    const toEdge = vertical
      ? (down ? "top" : "bottom") : (right ? "left" : "right");
    return path(point(from, fromEdge, box), point(to, toEdge, box), vertical);
  };
  let body = `<defs><marker id="neigh-arrow" markerWidth="8" markerHeight="8" `
    + `refX="6" refY="3" orient="auto">`
    + `<path d="M0,0 L7,3 L0,6 Z" fill="var(--accent)"/></marker></defs>`;
  root.querySelectorAll(".neigh-side.left .neigh-card").forEach((el) => {
    body += link(el, hub);
  });
  root.querySelectorAll(".neigh-side.right .neigh-card").forEach((el) => {
    body += link(hub, el);
  });
  svg.innerHTML = body;
}

/** The requirement between what uses it and what it depends on. */
export function Neighborhood({ sel, onNav }) {
  const { t } = useI18n();
  const root = useRef(null);
  const used = known(sel.usedBy);
  const deps = known(sel.deps);
  useEffect(() => {
    const el = root.current;
    if (!el) return undefined;
    const run = () => draw(el);
    run();
    if (typeof ResizeObserver === "undefined") return undefined;
    const watch = new ResizeObserver(run);
    watch.observe(el);
    return () => watch.disconnect();
  }, [sel.id, used.join(), deps.join()]);
  return (
    <div className="neigh" ref={root}>
      <svg className="neigh-arrows" aria-hidden="true" />
      <div className="neigh-grid">
        <Side side="left" label={t("Needed by")} ids={used} onNav={onNav}
              empty={t("— nothing depends on this")} />
        <div className="neigh-hub">
          <Card id={sel.id} selected onNav={onNav} />
        </div>
        <Side side="right" label={t("Needs")} ids={deps} onNav={onNav}
              empty={t("— no outgoing dependency")} />
      </div>
    </div>
  );
}

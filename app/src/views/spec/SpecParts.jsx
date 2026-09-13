// implements: ARCH-VIEWER-007
import { Fragment } from "react";
import { coverageDetail, exemptReason } from "../../lib/data.js";
import { mdInline, reqLinkProps } from "../../lib/ui.jsx";

export function parseTranslatedBlocks(text) {
  const lines = String(text || "").split("\n");
  const blocks = [];
  lines.forEach((raw) => {
    const line = raw.trim();
    if (!line) return;
    if (line.startsWith(">")) {
      const body = line.replace(/^>\s?/, "");
      const last = blocks[blocks.length - 1];
      if (last && last.kind === "quote") last.lines.push(body);
      else blocks.push({ kind: "quote", lines: [body] });
      return;
    }
    if (line.startsWith("- ")) {
      const body = line.slice(2);
      const last = blocks[blocks.length - 1];
      if (last && last.kind === "list") last.lines.push(body);
      else blocks.push({ kind: "list", lines: [body] });
      return;
    }
    const last = blocks[blocks.length - 1];
    if (last && (last.kind === "list" || last.kind === "quote") && /^\s/.test(raw)) {
      last.lines[last.lines.length - 1] += " " + line;
      return;
    }
    blocks.push({ kind: "para", lines: [line] });
  });
  return blocks;
}

export function TranslatedProse({ text, onNav, skipQuote = false }) {
  const blocks = parseTranslatedBlocks(text);
  return (
    <>
      {blocks.map((b, i) => {
        if (b.kind === "quote")
          return skipQuote ? null : <p className="blockquote" key={i}>{b.lines.join(" ")}</p>;
        if (b.kind === "list")
          return (
            <ul key={i} {...reqLinkProps(onNav)}>
              {b.lines.map((l, j) => <li key={j} dangerouslySetInnerHTML={{ __html: mdInline(l) }} />)}
            </ul>
          );
        return <p className="spec-para" key={i} dangerouslySetInnerHTML={{ __html: mdInline(b.lines[0]) }} />;
      })}
    </>
  );
}

export function CovStrip({ r }) {
  const { state, measured, clauses, covered, gap } = coverageDetail(r);
  const segs = [];
  if (measured) for (let i = 0; i < clauses; i++) segs.push(i < covered ? "on" : (state === "partial" ? "gap" : "off"));
  let label;
  if (state === "exempt") label = exemptReason(r);
  else if (measured) label = covered + " / " + clauses + " criteria verified";
  else if (state === "tested") label = "acceptance test linked · no per-criterion tags";
  else label = "no acceptance test linked";
  return (
    <div className="cov-strip">
      <div className="cov-row">
        <span className={"cov-badge cov-" + state}><span className="cd" />{state}</span>
        <span className="cov-count">{label}</span>
        {measured && <div className="cov-bar">{segs.map((s, i) => <span key={i} className={"cseg " + s} />)}</div>}
      </div>
      {gap && state === "partial" && <div className="cov-gap">gap · {gap}</div>}
    </div>
  );
}

export function SpecNavItem({ x, cur, setSelId }) {
  const on = cur === x.id;
  const sc = x.status === "in-progress" ? "var(--status-drift)"
    : x.status === "draft" ? "var(--status-draft)"
    : x.status === "deprecated" ? "var(--fg-faint)"
    : x.status === "confirmed" ? "transparent" : "var(--status-draft)";
  const tint = x.status === "in-progress" ? "var(--status-drift-bg)"
    : x.status === "draft" ? "var(--status-draft-bg)" : "transparent";
  return (
    <button onClick={() => setSelId(x.id)} title={x.status} style={{
      display: "flex", gap: 9, alignItems: "flex-start", textAlign: "left",
      padding: "7px 10px 7px 9px", border: "none",
      borderLeft: `3px solid ${on ? "var(--accent)" : (sc === "transparent" ? "transparent" : sc)}`,
      borderRadius: "0 var(--radius-1) var(--radius-1) 0", cursor: "pointer", width: "100%", marginBottom: "3px",
      background: on ? "var(--accent-soft)" : tint,
      color: on ? "var(--accent)" : "var(--fg-secondary)",
    }}>
      <span style={{ width: 7, height: 7, borderRadius: "999px", background: sc, flex: "none", marginTop: 5 }} />
      <span style={{ display: "flex", flexDirection: "column", gap: 2, minWidth: 0 }}>
        <span style={{ font: "var(--text-id)", color: "inherit" }}>{x.id}</span>
        <span style={{ font: "var(--text-small)", color: on ? "var(--accent)" : "var(--fg-muted)", fontSize: 12 }}>{x.title}</span>
      </span>
    </button>
  );
}

export function SpecMeta({ r, t, onNav }) {
  return (
    <div className="spec-meta">
      <span className="mk-val">{r.id}</span>
      <span className="mk-sep">|</span>
      <span className="mk-key">{t("level")}</span>
      <span className="mk-val">{r.level || "architecture"}</span>
      {r.milestone && <>
        <span className="mk-sep">|</span>
        <span className="mk-key">{t("milestone")}</span>
        <span className="mk-val">{r.milestone}</span>
      </>}
      {r.deps.length > 0 && <span className="mk-deps">
        <span className="mk-key">{t("depends on")}</span>
        <span className="mk-val">{r.deps.map((d, i) => (
          <Fragment key={d}>{i > 0 ? ", " : ""}<button className="dep-link" onClick={() => onNav && onNav(d)}>{d}</button></Fragment>
        ))}</span>
      </span>}
    </div>
  );
}

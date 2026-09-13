// implements: REQ-VIEWER-999
/* Horizons — ROADMAP.md's plan as three columns: Now, Next, Later.

   The other two modes sort by semver, which answers "when". A horizon plan answers
   "what is next" and has no version to sort on, so it needed a shape of its own rather
   than a fourth way to bucket milestones. `Not now` is parsed and deliberately NOT
   drawn: it is the record of what was decided against, and a decision that is not work
   does not belong in a column beside work that is. */
import { REQ_BY_ID } from "../../lib/data.js";

const HORIZONS = [
  { key: "now", label: "Now", hint: "being worked on" },
  { key: "next", label: "Next", hint: "queued, not started" },
  { key: "later", label: "Later", hint: "parked behind a condition" },
];

function Item({ item, t, openSpec }) {
  // A `req:` that names nothing is rendered as plain text on purpose: the viewer must
  // not offer a link that goes nowhere, and `gate --audit` already reports the id.
  const req = item.req && REQ_BY_ID[item.req] ? item.req : null;
  return (
    <li style={{
      display: "flex", flexDirection: "column", gap: 3,
      padding: "8px 10px", borderRadius: 6,
      background: item.done ? "var(--cov-tested-bg)" : "var(--surface-hov)",
      border: "1px solid var(--border)",
    }}>
      <span style={{ display: "flex", alignItems: "flex-start", gap: 7 }}>
        <span aria-hidden="true" style={{
          flexShrink: 0, marginTop: 2, width: 11, height: 11, borderRadius: 3,
          border: "1.5px solid " + (item.done ? "var(--cov-tested)" : "var(--fg-faint)"),
          background: item.done ? "var(--cov-tested)" : "transparent",
        }} />
        <span style={{
          fontSize: 12, lineHeight: 1.35,
          color: item.done ? "var(--fg-muted)" : "var(--fg)",
          textDecoration: item.done ? "line-through" : "none",
        }}>{item.name}</span>
      </span>
      {req && (
        <button
          type="button"
          onClick={() => openSpec && openSpec(req)}
          style={{
            alignSelf: "flex-start", marginLeft: 18, border: "none", background: "none",
            padding: 0, cursor: "pointer", fontSize: 9, fontWeight: 700,
            letterSpacing: "0.3px", color: "var(--indigo-500)",
          }}
        >{req}</button>
      )}
      {!req && item.req && (
        <span style={{ marginLeft: 18, fontSize: 9, fontWeight: 700,
                       letterSpacing: "0.3px", color: "var(--fg-faint)" }}>{item.req}</span>
      )}
      {item.unpark && (
        <span style={{ marginLeft: 18, fontSize: 10, color: "var(--fg-muted)", lineHeight: 1.35 }}>
          {t("unpark:")} {item.unpark}
        </span>
      )}
    </li>
  );
}

export function Horizons({ items, t, openSpec, zoom }) {
  return (
    <div style={{
      zoom: zoom / 100,
      display: "grid", gridTemplateColumns: "repeat(3, minmax(240px, 1fr))",
      gap: 16, alignItems: "start", width: "100%", maxWidth: 1100,
    }}>
      {HORIZONS.map(h => {
        const mine = items.filter(i => i.horizon === h.key);
        const open = mine.filter(i => !i.done).length;
        return (
          <section key={h.key} style={{
            border: "1px solid var(--border)", borderRadius: 8,
            background: "var(--bg-raised)", overflow: "hidden",
          }}>
            <header style={{
              padding: "9px 12px", borderBottom: "1px solid var(--border)",
              display: "flex", alignItems: "baseline", gap: 8,
            }}>
              <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.6px",
                             textTransform: "uppercase", color: "var(--fg)" }}>{t(h.label)}</span>
              <span style={{ fontSize: 10, color: "var(--fg-faint)" }}>{t(h.hint)}</span>
              <span style={{ marginLeft: "auto", fontSize: 10, color: "var(--fg-muted)" }}>
                {open} {t("open")}
              </span>
            </header>
            {mine.length === 0 ? (
              <p style={{ margin: 0, padding: "14px 12px", fontSize: 11, color: "var(--fg-faint)" }}>
                {t("nothing here")}
              </p>
            ) : (
              <ul style={{ listStyle: "none", margin: 0, padding: 10,
                           display: "flex", flexDirection: "column", gap: 7 }}>
                {mine.map((item, i) => (
                  <Item key={h.key + i} item={item} t={t} openSpec={openSpec} />
                ))}
              </ul>
            )}
          </section>
        );
      })}
    </div>
  );
}

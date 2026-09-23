// implements: ARCH-VIEWER-007
/* The note that opens below the Plan when a bar, a version or a shipped
 * month is selected. */

/** ROADMAP.md keeps a note under an item as an HTML comment, which is how
 *  a plan file hides it from a Markdown reader — the markers are
 *  packaging, not content. Strip them and the blank lines they leave, so
 *  the panel shows the sentence and not the syntax. */
export function noteText(context) {  // implements: REQ-VIEWER-999
  if (typeof context !== "string") return "";
  return context
    .replace(/<!--/g, "")
    .replace(/-->/g, "")
    .split(/\r?\n/)
    .map((ln) => ln.trim())
    .join("\n")
    .trim();
}

/** The roadmap item a bar belongs to. `req` is the only id both sides
 *  carry, so it is the join; a bar with none, or one no item claims,
 *  simply has no note. */
export function matchItem(bar, roadmap) {  // implements: REQ-VIEWER-999
  const req = bar?.reqId || bar?.req;
  if (!req || !Array.isArray(roadmap)) return null;
  return roadmap.find((it) => it && it.req === req) || null;
}

/** Enter and Space open a selectable element, as a click does. */
export function onActivate(fn) {
  return (e) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fn(); }
  };
}

const NOTE_BOX = {
  marginTop: 12, padding: "14px 16px", borderRadius: 6,
  background: "var(--surface)", border: "1px solid var(--border-soft)",
  borderLeft: "3px solid var(--accent-2)", maxWidth: 760,
};
const NOTE_LIST = {
  margin: "10px 0 0", padding: 0, listStyle: "none", display: "grid", gap: 6,
};
const NOTE_ROW = { fontSize: 12.5, lineHeight: 1.5, display: "flex", gap: 10 };
const VERSION = { minWidth: 64, fontVariantNumeric: "tabular-nums" };
const FAINT = { marginTop: 10, fontSize: 12, color: "var(--fg-faint)" };
const LINK = {
  background: "none", border: "none", padding: 0, cursor: "pointer",
  font: "inherit",
};
const REQ_LINK = {
  ...LINK, color: "var(--accent-2)", textDecoration: "underline",
};
const CLOSE = {
  marginLeft: "auto", background: "none", border: "none", cursor: "pointer",
  color: "var(--fg-faint)", fontSize: 16, lineHeight: 1, padding: 0,
};

function NoteHead({ title, meta, t, onClose }) {
  return (
    <div style={{ display: "flex", alignItems: "baseline", gap: 10,
                 flexWrap: "wrap" }}>
      <strong style={{ fontSize: 14 }}>{title}</strong>
      <span style={{ fontSize: 11, color: "var(--fg-faint)" }}>{meta}</span>
      <button type="button" onClick={onClose} style={CLOSE}
        aria-label={t ? t("Close") : "Close"}>×</button>
    </div>
  );
}

const say = (t, text) => (t ? t(text) : text);

/** A shipped month, opened: every release in it with its CHANGELOG
 *  headline, newest first.
 *  implements: REQ-HISTORY-1081 */
export function ShippedNote({ month, t, onClose }) {
  const entries = Array.isArray(month.entries) && month.entries.length
    ? month.entries : (month.versions || []).map((v) => ({ version: v }));
  const meta =
    `${month.count} ${say(t, "releases")} · ${month.first} → ${month.last}`;
  return (
    <div style={NOTE_BOX} data-note="month">
      <NoteHead title={month.month} t={t} onClose={onClose} meta={meta} />
      <ul style={NOTE_LIST}>
        {entries.map((e) => (
          <li key={e.version} style={NOTE_ROW}>
            <strong style={VERSION}>{e.version}</strong>
            {e.date && (
              <span style={{ color: "var(--fg-faint)", minWidth: 78 }}>
                {e.date}
              </span>
            )}
            <span>{e.headline || ""}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function PlannedBar({ bar, openSpec, onPickBar }) {
  return (
    <li style={NOTE_ROW}>
      <button type="button" onClick={() => onPickBar(bar)}
        style={{ ...LINK, color: "var(--fg)", textAlign: "left",
                 fontWeight: 600 }}>
        {bar.title}
      </button>
      <span style={{ color: "var(--fg-faint)" }}>{bar.start} → {bar.end}</span>
      {bar.reqId && openSpec && (
        <button type="button" onClick={() => openSpec(bar.reqId)}
                style={REQ_LINK}>
          {bar.reqId}
        </button>
      )}
    </li>
  );
}

/** A planned version, opened: its due date, its label and the bars planned
 *  on it. implements: REQ-PLANCADENCE-1000 */
export function VersionNote(
  { version, bars, t, openSpec, onClose, onPickBar },
) {
  const planned = bars.filter((b) => b.milestone === version.ms);
  const meta = `${version.due}${version.label ? ` · ${version.label}` : ""}`;
  const list = (
    <ul style={NOTE_LIST}>
      {planned.map((b) => (
        <PlannedBar key={b.key} bar={b} openSpec={openSpec}
                    onPickBar={onPickBar} />
      ))}
    </ul>
  );
  return (
    <div style={NOTE_BOX} data-note="version">
      <NoteHead title={version.ms} t={t} onClose={onClose} meta={meta} />
      {planned.length
        ? list
        : <div style={FAINT}>
            {say(t, "Nothing planned on this version yet.")}
          </div>}
    </div>
  );
}

/** A bar, opened: its dates, its requirement and the note under its
 *  ROADMAP.md item.
 *  implements: REQ-VIEWER-999 */
function BarNote({ bar, roadmap, t, openSpec, onClose }) {
  const item = matchItem(bar, roadmap);
  const note = noteText(item?.context);
  const req = bar?.reqId || bar?.req;
  const meta =
    `${bar.start} → ${bar.end}${bar.milestone ? ` · ${bar.milestone}` : ""}`
    + `${item?.horizon ? ` · ${item.horizon}` : ""}`;
  const reqLine = openSpec
    ? <button type="button" onClick={() => openSpec(req)} style={REQ_LINK}>
        {req}
      </button>
    : <span style={{ color: "var(--fg-faint)" }}>{req}</span>;
  const noteStyle = {
    marginTop: 10, fontSize: 12.5, lineHeight: 1.55, whiteSpace: "pre-wrap",
  };
  return (
    <div style={NOTE_BOX}>
      <NoteHead title={bar.title} t={t} onClose={onClose} meta={meta} />
      {req && <div style={{ fontSize: 11, marginTop: 6 }}>{reqLine}</div>}
      {note
        ? <div style={noteStyle}>{note}</div>
        : <div style={FAINT}>
            {say(t, "No note in ROADMAP.md for this item.")}
          </div>}
    </div>
  );
}

/** Whichever note the selection is: a shipped month, a version, or a bar. */
export function PickedNote({ picked, lay, roadmap, t, openSpec, onPick }) {
  const close = () => onPick(null);
  if (picked.kind === "month") {
    return <ShippedNote month={picked} t={t} onClose={close} />;
  }
  if (picked.kind === "version") {
    return <VersionNote version={picked} bars={lay.bars} t={t}
                        openSpec={openSpec}
                        onClose={close} onPickBar={onPick} />;
  }
  return <BarNote bar={picked} roadmap={roadmap} t={t} openSpec={openSpec}
                  onClose={close} />;
}

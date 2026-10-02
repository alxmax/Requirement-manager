// implements: ARCH-VIEWER-007
/* A release's CHANGELOG entry, unfolded under its row in the month note
 * (REQ-HISTORY-1081). The engine ships the entry as written (`body`);
 * this reads the little Markdown a changelog uses — `###` subtitles,
 * `- ` bullets with indented children, paragraphs — and renders only
 * `**bold**` and `code`. Everything else stays text, which React escapes:
 * nothing in a CHANGELOG is ever parsed into HTML. */

/** A headline as the engine flattens it (`history._headline`): one line,
 *  no surrounding spaces or dots — so the intro can tell it is the same
 *  sentence the row already shows. */
const flat = (s) => String(s || "").replace(/\s+/g, " ")
  .replace(/^[ .]+|[ .]+$/g, "");

const BULLET = /^(\s*)[-*+]\s+(.*)$/;
const SUBTITLE = /^#{3,}\s+(.*)$/;
const RULE = /^(-{3,}|\*{3,}|_{3,})$/;

/** The entry's blocks, in file order: `{kind: "h", text}`,
 *  `{kind: "p", text}` and `{kind: "ul", items: [{text, kids}]}`, where a
 *  kid is an indented bullet under the item above it. A wrapped line joins
 *  the paragraph or bullet it continues. The intro's bold title is dropped
 *  when it is `headline`, which the row already shows. */
export function bodyBlocks(body, headline = "") {
  const blocks = [];
  let para = null; let list = null; let tail = null; let gap = false;
  const src = String(body || "").replace(/<!--[\s\S]*?-->/g, "");
  for (const raw of src.split(/\r?\n/)) {
    const text = raw.trim();
    if (!text || RULE.test(text)) { para = null; gap = true; continue; }
    const sub = SUBTITLE.exec(text);
    const bullet = BULLET.exec(raw);
    if (sub) {
      blocks.push({ kind: "h", text: sub[1] });
      para = list = tail = null;
    } else if (bullet) {
      const kid = bullet[1].length >= 2 && list && list.items.length;
      if (!kid && !list) { list = { kind: "ul", items: [] }; blocks.push(list); }
      tail = { text: bullet[2], kids: [] };
      (kid ? list.items[list.items.length - 1].kids : list.items).push(tail);
      para = null;
    } else if (tail && (!gap || /^\s/.test(raw))) {
      tail.text += ` ${text}`;
    } else if (para) {
      para.text += ` ${text}`;
    } else {
      para = { kind: "p", text };
      blocks.push(para);
      list = tail = null;
    }
    gap = false;
  }
  return dropTitle(blocks, headline);
}

function dropTitle(blocks, headline) {
  const first = blocks[0];
  const want = flat(headline);
  if (!first || first.kind !== "p" || !want) return blocks;
  const bold = /^\*\*(.+?)\*\*\s*/.exec(first.text);
  const lead = bold ? flat(bold[1]) : flat(first.text);
  // A clipped headline ends in "…"; it still names this sentence.
  const stem = want.endsWith("…") ? want.slice(0, -1) : want;
  const hit = lead === want || (stem !== want && stem && lead.startsWith(stem));
  if (!hit) return blocks;
  const rest = bold ? first.text.slice(bold[0].length) : "";
  return rest ? [{ kind: "p", text: rest }, ...blocks.slice(1)]
    : blocks.slice(1);
}

const CODE = {
  fontFamily: "var(--font-mono)", fontSize: "0.92em",
  background: "var(--surface-hov)", borderRadius: 3,
  padding: "0 3px",
};

/** `**bold**` and `code` as elements, every other character as text. */
export function inline(text) {
  const out = [];
  const re = /\*\*(.+?)\*\*|`([^`]+)`/g;
  let at = 0; let m;
  while ((m = re.exec(text))) {
    if (m.index > at) out.push(text.slice(at, m.index));
    out.push(m[1] !== undefined
      ? <strong key={m.index}>{inline(m[1])}</strong>
      : <code key={m.index} style={CODE}>{m[2]}</code>);
    at = re.lastIndex;
  }
  if (at < text.length) out.push(text.slice(at));
  return out;
}

const BODY = {
  margin: "6px 0 4px 74px", fontSize: 12.5, lineHeight: 1.55,
  overflowWrap: "anywhere",
};
const SUB = { margin: "10px 0 4px", fontSize: 12.5, fontWeight: 700 };
const PARA = { margin: "6px 0" };
const LIST = { margin: "4px 0", paddingLeft: 18, display: "grid", gap: 3 };

/** One release's whole CHANGELOG entry. */
export function EntryBody({ body, headline }) {
  const items = (list) => list.map((it, j) => (
    <li key={j}>
      {inline(it.text)}
      {it.kids.length > 0 && <ul style={LIST}>{items(it.kids)}</ul>}
    </li>
  ));
  return (
    <div style={BODY} data-entry-body="">
      {bodyBlocks(body, headline).map((b, i) => (
        b.kind === "h" ? <h4 key={i} style={SUB}>{inline(b.text)}</h4>
          : b.kind === "p" ? <p key={i} style={PARA}>{inline(b.text)}</p>
            : <ul key={i} style={LIST}>{items(b.items)}</ul>
      ))}
    </div>
  );
}

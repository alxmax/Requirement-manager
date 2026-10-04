// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-944
/* Shared primitives: Pill (status/layer), Btn, statusKind, and the one inline
 * markdown renderer both document surfaces use. */
import { Icon } from "./icons.jsx";
import { REQ_BY_ID } from "./data.js";

export function Pill({ kind, children }) {
  return (
    <span className={"pill " + kind}>
      <span className="pdot" />
      {children || kind}
    </span>
  );
}

export function Btn({ variant = "secondary", icon, children, ...rest }) {
  return (
    <button className={"btn btn-" + variant} {...rest}>
      {icon && <Icon name={icon} size={15} />}
      {children}
    </button>
  );
}

/** The status the reader sees. `in-progress` is the same bucket as `draft`. */
export function shownStatus(s) {
  return s === "in-progress" ? "draft" : s;
}

/* status → pill kind */
export function statusKind(s) {
  const k = shownStatus(s);
  return k === "confirmed" ? "confirmed"
    : k === "deprecated" ? "deprecated" : "draft";
}

/* Requirement prose carries two markups the authors actually write: `code`
 * spans and `[[REQ-ID]]` cross-references. Both were rendered literally — a
 * clause reading "[[REQ-CHECK-828]] details the behaviour" printed the brackets
 * and led nowhere, on every architecture requirement in the corpus.
 *
 * HTML-escaping comes FIRST and is mandatory: the output feeds
 * dangerouslySetInnerHTML with untrusted text carried verbatim from _map.json.
 * The id is then matched against a restricted charset, so nothing an author can
 * write reaches the DOM as markup. */
const WIKI_RE = /\[\[([A-Za-z][A-Za-z0-9_.-]{0,63})\]\]/g;

export function mdInline(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    // `**bold**` is authored prose here — the Context sub-group labels are
    // written that way — and printed its own asterisks until now. After the
    // code spans, so a backticked `**literal**` keeps them.
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(WIKI_RE, (_m, id) => (
      REQ_BY_ID[id]
        ? `<a class="wikilink" role="button" tabindex="0" data-req="${id}">` +
          `${id}</a>`
        // A reference to something this map does not hold is information,
        // not an error to hide: show the id, marked, rather than a dead
        // bracket pair.
        : `<span class="wikilink off" title="not in this map">${id}</span>`
    ));
}

/* A verify-intent question asked as a decision is one string: the question,
 * then one line per option (`a) …`) or label (`*Default:* …`). Each line after
 * the first renders as its own indented block, so the options read at a
 * glance. A line-start `*Label*` becomes <em>, here only: in mdInline it would
 * catch stray asterisks in every other caller's prose. It runs after
 * mdInline's escaping and admits no `<` or `>`, so it cannot open a tag. */
export function mdQuestion(q) {  // implements: REQ-FINDINGS-853
  const [head, ...rest] = String(q).split("\n");
  return mdInline(head) + rest.map((line) => '<span class="q-opt">'
    + mdInline(line).replace(/^\*([^*<>]+)\*/, "<em>$1</em>") + "</span>")
    .join("");
}

/* Click/Enter delegate for a container rendering mdInline() output: one handler
 * per list rather than a React node per link, which is what keeps the renderer
 * a plain string transform. */
export function reqLinkProps(onNav) {
  if (!onNav) return {};
  const go = (e) => {
    const id = e.target && e.target.dataset && e.target.dataset.req;
    if (!id) return;
    e.stopPropagation();
    e.preventDefault();
    onNav(id);
  };
  return {
    onClick: go,
    onKeyDown: (e) => { if (e.key === "Enter" || e.key === " ") go(e); },
  };
}

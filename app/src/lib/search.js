// implements: ARCH-SEARCH-036
// implements: REQ-SEARCH-965
/* Requirement search — the ranked relevance model, shared with the engine.
 *
 * This is a faithful JS port of the Python scoring in
 * plugin/scripts/reqmap.py
 * (`_sim_tokens` / `_sim_text` / `_tfidf` / `_cosine`, contract
 * ARCH-SIMILAR-016)
 * exactly as the `search` CLI command uses it (ARCH-SEARCH-036). The
 * viewer's search box and the CLI therefore rank by ONE model, not two
 * that quietly disagree. Keep them in lockstep: the stopword set, the
 * length>=3 / no-pure-digit rule, the smoothed idf
 * `log((1+N)/(1+df)) + 1`, the query-folded-into-corpus
 * step, and SEARCH_FLOOR must match their Python counterparts. Parity is
 * pinned by a shared golden fixture asserted in BOTH
 * app/scripts/ssr-smoke.jsx and the
 * Python `Search` tests — if either runtime drifts, its check fails. */

// Mirror of reqmap.py `_SIMILAR_STOP`.
const STOP = new Set([
  "the", "and", "for", "shall", "with", "that", "this", "from", "into", "its",
  "not", "are", "has", "have", "when", "then", "given", "each", "one", "any",
  "per", "via", "use", "used", "must", "code", "requirement", "requirements",
]);

// Mirror of reqmap.py `SEARCH_FLOOR`: query-vs-doc cosine noise floor. Far
// below the 0.35 dupes pair-threshold because a short query is a sparse
// vector.
export const SEARCH_FLOOR = 0.05;

// Mirror of `_sim_tokens`: lowercase alphanumeric tokens of length >= 3, minus
// pure numbers and stopwords.
function tokens(text) {
  const out = [];
  for (const m of (text || "").toLowerCase().matchAll(/[a-z0-9]+/g)) {
    const t = m[0];
    if (t.length >= 3 && !/^\d+$/.test(t) && !STOP.has(t)) out.push(t);
  }
  return out;
}

// Mirror of `_sim_text`: the bag is built from title + intent + Contract
// bullets. (In the engine the intent is the first blockquote line; here
// `intent` is already that extracted line, and `contract` the bullet list
// — same text, same order.)
function simText(r) {
  const intent = (r.intent || "").split("\n")[0];
  return [r.title || "", intent, ...(r.contract || [])].join(" ");
}

// Mirror of `_tfidf`: {id: tokenList} -> {id: {term: weight}}, smoothed idf.
function tfidf(docs) {
  const ids = Object.keys(docs);
  const N = ids.length;
  const df = new Map();
  for (const id of ids) {
    for (const t of new Set(docs[id])) df.set(t, (df.get(t) || 0) + 1);
  }
  const vecs = {};
  for (const id of ids) {
    const tf = new Map();
    for (const t of docs[id]) tf.set(t, (tf.get(t) || 0) + 1);
    const v = {};
    for (const [t, c] of tf) {
      v[t] = c * (Math.log((1 + N) / (1 + df.get(t))) + 1);
    }
    vecs[id] = v;
  }
  return vecs;
}

// Mirror of `_cosine`: cosine of two {term: weight} vectors, clamped to [0, 1].
function cosine(a, b) {
  const bk = new Set(Object.keys(b));
  if (!Object.keys(a).length || !bk.size) return 0;
  let dot = 0;
  for (const t of Object.keys(a)) if (bk.has(t)) dot += a[t] * b[t];
  let na = 0; for (const t of Object.keys(a)) na += a[t] * a[t];
  let nb = 0; for (const t of Object.keys(b)) nb += b[t] * b[t];
  na = Math.sqrt(na); nb = Math.sqrt(nb);
  return na && nb ? Math.min(1, dot / (na * nb)) : 0;
}

/* Rank `reqs` (each {id, title, intent, contract[]}) by lexical relevance
 * to `query`, most-relevant-first. Returns [{req, score}] at or above
 * `floor`, capped at `top`. Empty query or a query with no searchable term
 * -> []. This is the same computation as `cmd_search`, so a hit's score
 * matches the CLI's. */
// implements: REQ-SEARCH-912
export function rankRequirements(
  reqs, query, { top = 8, floor = SEARCH_FLOOR } = {}) {
  const qtok = tokens(query);
  if (!qtok.length) return [];
  const docs = {};
  for (const r of reqs) {
    const t = tokens(simText(r));
    if (t.length) docs[r.id] = t;
  }
  if (!Object.keys(docs).length) return [];
  // fold query in, like the engine
  const corpus = { ...docs, "\u0000query": qtok };
  const vecs = tfidf(corpus);
  const qv = vecs["\u0000query"];
  const byId = new Map(reqs.map((r) => [r.id, r]));
  return Object.keys(docs)
    .map((id) => ({ req: byId.get(id), score: cosine(qv, vecs[id]) }))
    .filter((h) => h.score >= floor)
    // (-score, id)
    .sort((a, b) => b.score - a.score || (a.req.id < b.req.id ? -1 : 1))
    .slice(0, top);
}

/* The id is this corpus's primary key, and it is in none of the text
 * above: searching for `ARCH-CHECK-006` ranked REQ-ORPHANCODE-888 first
 * and never returned the requirement named. A phrase that appears
 * verbatim in a document is likewise stronger evidence than a partial
 * token overlap with a different one. Both are selections, not rankings,
 * so they sit AROUND the model rather than inside it —
 * `rankRequirements` and its golden fixture are untouched, and the CLI
 * does exactly the same three steps. */
const SEARCH_ID_MAX = 3;

function idMatches(reqs, query) {
  const q = (query || "").trim().toUpperCase();
  if (q.length < 3) return [];
  const exact = reqs.find((r) => r.id.toUpperCase() === q);
  if (exact) return [exact];
  const prefix = reqs.filter((r) => r.id.toUpperCase().startsWith(q));
  const inner = reqs.filter(
    (r) => r.id.toUpperCase().includes(q) && !prefix.includes(r));
  return prefix.concat(inner).slice(0, SEARCH_ID_MAX);
}

/* Everything a reader can see of one requirement, in every language the
 * map carries — so a query typed in the language the viewer is showing
 * finds it, which the ranking model cannot do: it weights one language's
 * tokens. */
function haystack(r) {
  const parts = [
    r.id, r.title, r.intent, ...(r.contract || []), ...(r.acc || []),
    r.gwt || "",
  ];
  const i18n = r.i18n || {};
  for (const loc of Object.keys(i18n)) {
    const e = i18n[loc] || {};
    parts.push(e.title, e.intent, e.contract, e.acceptance);
  }
  return parts.filter(Boolean).join("\n").toLowerCase();
}

function textMatches(reqs, query, skip) {
  const q = (query || "").trim().toLowerCase();
  if (q.length < 3) return [];
  return reqs.filter((r) => !skip.has(r.id) && haystack(r).includes(q));
}

/** The viewer's search: id, then literal text, then the ranked model —
 *  each hit tagged with which layer found it, so a reader is never shown
 *  a score that isn't one. */
export function searchRequirements(reqs, query, { top = 8 } = {}) {
  // implements: REQ-SEARCH-965
  const ids = idMatches(reqs, query);
  const seen = new Set(ids.map((r) => r.id));
  const text = textMatches(reqs, query, seen)
    .slice(0, Math.max(0, top - seen.size));
  text.forEach((r) => seen.add(r.id));
  const ranked = rankRequirements(reqs, query, { top })
    .filter((h) => !seen.has(h.req.id))
    .slice(0, Math.max(0, top - seen.size));
  return [
    ...ids.map((req) => ({ req, kind: "id" })),
    ...text.map((req) => ({ req, kind: "text" })),
    ...ranked.map((h) => ({ req: h.req, kind: "score", score: h.score })),
  ];
}

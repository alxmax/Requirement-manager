// implements: ARCH-VIEWER-007
// implements: REQ-TRANSLATE-1080
/* i18n — UI chrome, plus opt-in, cached, always-marked requirement content.
 *
 * UI chrome (nav, tab labels, section headers, buttons, empty states) is
 * translated live from the dictionary below — that boundary is unchanged.
 *
 * Requirement CONTENT (id, title, intent, contract clauses, acceptance
 * criteria, member paths) stays in the author's language by default, for the
 * original reason: it is the artifact under review, and translating it live
 * would put words in the author's mouth and break the match with the .md file
 * on disk. The one exception is opt-in and never silent: `reqmap.py translate`
 * — a separate, MANUAL engine command, never run by gate/sync/lint/CI/the
 * pre-commit hook — caches a `claude -p` translation per requirement, gated
 * by
 * a structural-fidelity check, in requirements/_i18n/<locale>.json. `map`
 * inlines that cache onto each node as `node.i18n[locale]`, read-only, no
 * network call of its own. `translatedText()` below is the ONLY thing that
 * reads it, and it always reports whether a value came from the cache
 * (`isTranslated`) — callers render an explicit "machine-translated,
 * unreviewed" badge next to it (see SpecView.jsx) and NEVER present it as the
 * authored source. Absent a cache entry, content still falls back to the
 * author's own text, exactly as before.
 *
 * The engine's own vocabulary is out of scope too, deliberately: `confirmed`,
 * `draft`, `orphan`, `deprecated`, `bus`/`feature`/`need`,
 * and the ERROR/WARN/REVIEW severities are literal values in the
 * requirement files and in the gate's output. A reader who sees
 * "confirmat" here and `status: confirmed`
 * in the file has been given a puzzle, not a translation.
 *
 * The dictionary is keyed by the English source string rather than by an
 * invented key, so the JSX stays readable in English and a missing entry
 * degrades to English instead of to `nav.map.label`.
 */
import { createContext, useContext, useEffect, useState } from "react";
import { DE, COMMAND_DE } from "./i18n.de.js";
import { RO, COMMAND_RO } from "./i18n.ro.js";

export const LOCALES = [
  { code: "en", label: "EN", name: "English", dates: "en-GB" },
  { code: "ro", label: "RO", name: "Română", dates: "ro-RO" },
  { code: "de", label: "DE", name: "Deutsch", dates: "de-DE" },
];

/** The BCP 47 tag dates are written in for a locale; English otherwise. */
export function dateLocale(code) {
  return (LOCALES.find((l) => l.code === code) || LOCALES[0]).dates;
}

const STORAGE_KEY = "reqmap.viewer.locale";

/* English -> Romanian, UI chrome only. Order mirrors the components. */
const DICT = { ro: RO, de: DE };
const COMMAND_DICT = { ro: COMMAND_RO, de: COMMAND_DE };

/* The English text of every chrome string a bundled language translates;
 * a smoke check holds each language to the same list. */
export const DICT_KEYS = Object.fromEntries(
  Object.entries(DICT).map(([code, table]) => [code, Object.keys(table)]));

/* `{n}`-style placeholders, so a translated sentence can reorder them. */
function interpolate(s, params) {
  if (!params) return s;
  return s.replace(
    /\{(\w+)\}/g, (m, k) => (k in params ? String(params[k]) : m));
}

export function translate(locale, s, params) {  // implements: REQ-VIEWER-943
  const table = DICT[locale];
  return interpolate((table && table[s]) || s, params);
}

/* Read a cached content translation for `field` ("title" | "intent" |
 * "contract" | "acceptance") off `node.i18n[locale]`. Falls back to
 * `fallback` (the author's own text, or null when the caller has its own
 * fallback rendering) when no cache entry exists — never throws, never
 * fabricates a translation. `isTranslated` is the only signal callers need to
 * decide whether to show the "machine-translated, unreviewed" badge. */
// implements: REQ-TRANSLATE-938
export function translatedText(node, locale, field, fallback = null) {
  const cached = node && node.i18n && node.i18n[locale]
    && node.i18n[locale][field];
  return cached
    ? { text: cached, isTranslated: true }
    : { text: fallback, isTranslated: false };
}

function readStored() {
  // Guarded twice over: SSR (the smoke test) has no window at all, and a
  // file:// viewer in a hardened browser can throw on the accessor itself.
  try {
    if (typeof window === "undefined" || !window.localStorage) return null;
    const v = window.localStorage.getItem(STORAGE_KEY);
    return LOCALES.some(l => l.code === v) ? v : null;
  } catch { return null; }
}

const Ctx = createContext({
  locale: "en",
  setLocale: () => {},
  t: (s, params) => interpolate(s, params),
});

/* `initialLocale` lets a host (or a test) preset the language; otherwise the
 * viewer remembers the reader's last choice, and falls back to English. */
/* The default the ENGINE declares. Read straight from the inlined blob
 * rather than from data.js: the provider mounts before App's effect runs
 * loadData, so the module-level LANGUAGE is still its default at the
 * moment the initial locale is chosen. The single-file viewer — the
 * artifact consumers actually open — always has the blob at mount time.
 * A bundled language opens in that language; anything else in English. */
function engineDefault() {
  // implements: REQ-MAPSTAMP-1125
  try {
    const d = typeof window !== "undefined" ? window.__REQMAP_DATA__ : null;
    const v = d && d.language;
    return LOCALES.some((l) => l.code === v) ? v : "en";
  } catch { return "en"; }
}

export function I18nProvider({ children, initialLocale }) {
  // implements: REQ-VIEWER-943
  const [locale, choose] = useState(
    () => initialLocale || readStored() || engineDefault());
  // Only a reader's choice is remembered: storing the first open would turn
  // the repository's default into a preference.  implements: REQ-MAPSTAMP-1125
  const setLocale = (next) => {
    choose(next);
    try { window.localStorage.setItem(STORAGE_KEY, next); }
    catch { /* not fatal */ }
  };
  useEffect(() => {
    // Keep the document language honest for screen readers and hyphenation.
    try { document.documentElement.lang = locale; } catch { /* SSR */ }
  }, [locale]);
  const value = {
    locale, setLocale, t: (s, params) => translate(locale, s, params),
  };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

/** A command's summary in `locale`, falling back to the engine's own
 * English. */
export function commandSummary(cmd, locale) {  // implements: REQ-VIEWER-964
  const table = COMMAND_DICT[locale];
  const own = table && cmd && table[cmd.name];
  return own || (cmd && cmd.summary) || "";
}

export function useI18n() { return useContext(Ctx); }

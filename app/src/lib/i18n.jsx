/* i18n — UI chrome only, never requirement content.
 *
 * The line this module must not cross: it translates the frame around the data
 * (nav, tab labels, section headers, buttons, empty states) and NOTHING the
 * registry itself carries. A requirement's id, title, intent, contract clauses,
 * acceptance criteria and member paths stay in the author's language, because
 * they are the artifact under review — translating them would put words in the
 * author's mouth and break the match with the .md file on disk.
 *
 * The engine's own vocabulary is out of scope too, deliberately: `confirmed`,
 * `in-progress`, `draft`, `orphan`, `deprecated`, `bus`/`feature`/`need`, and the
 * ERROR/WARN/REVIEW severities are literal values in the requirement files and in
 * the gate's output. A reader who sees "confirmat" here and `status: confirmed`
 * in the file has been given a puzzle, not a translation.
 *
 * The dictionary is keyed by the English source string rather than by an
 * invented key, so the JSX stays readable in English and a missing entry
 * degrades to English instead of to `nav.map.label`.
 */
import { createContext, useContext, useEffect, useState } from "react";

export const LOCALES = [
  { code: "en", label: "EN", name: "English" },
  { code: "ro", label: "RO", name: "Română" },
];

const STORAGE_KEY = "reqmap.viewer.locale";

/* English -> Romanian, UI chrome only. Order mirrors the components. */
const RO = {
  // shell / top bar
  "local repo": "depozit local",
  "Search id, title, contract…": "Caută id, titlu, contract…",
  "no strong match": "nicio potrivire clară",
  "toggle theme": "schimbă tema",
  "switch language": "schimbă limba",
  // rail
  "Workspace": "Spațiu de lucru",
  "Registry": "Registru",
  "Map": "Hartă",
  "Problems": "Probleme",
  "Spec": "Specificații",
  "Roadmap": "Plan",
  "{n} members bound": "{n} membri legați",
  // map tabs
  "System Map": "Harta sistemului",
  "Req→Code": "Cerință→Cod",
  "Dependencies": "Dependențe",
  "Risk": "Risc",
  // detail panel + spec sections
  "Why — Intent": "De ce — Intenție",
  "What — Contract": "Ce — Contract",
  "How — Acceptance": "Cum — Acceptanță",
  "Where — Members in code": "Unde — Membri în cod",
  "Depends on": "Depinde de",
  "Used by": "Folosit de",
  "Risk — recommended action": "Risc — acțiune recomandată",
  "Open full spec": "Deschide specificația completă",
  "center & highlight in the map": "centrează și evidențiază în hartă",
  "close": "închide",
  "created": "creat",
  "updated": "actualizat",
  "normative": "normativ",
  "= tests": "= teste",
  "(satisfied-by other requirements — no direct code)":
    "(satisfăcut de alte cerințe — fără cod direct)",
  "(no members found — orphan)": "(niciun membru găsit — orfan)",
  // problems
  "All": "Toate",
  "Errors": "Erori",
  "Warnings": "Avertismente",
  "Review": "De revizuit",
  "gate passes": "poarta trece",
  "gate blocks the build — {n} error": "poarta blochează build-ul — {n} erori",
  "Nothing here — no {kind} signals open.": "Nimic aici — niciun semnal {kind} deschis.",
  // roadmap
  "done": "gata",
  "progress": "în lucru",
  "draft": "schiță",
  "planned": "planificat",
};

const DICT = { ro: RO };

/* `{n}`-style placeholders, so a translated sentence can reorder them. */
function interpolate(s, params) {
  if (!params) return s;
  return s.replace(/\{(\w+)\}/g, (m, k) => (k in params ? String(params[k]) : m));
}

export function translate(locale, s, params) {
  const table = DICT[locale];
  return interpolate((table && table[s]) || s, params);
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
export function I18nProvider({ children, initialLocale }) {
  const [locale, setLocale] = useState(() => initialLocale || readStored() || "en");
  useEffect(() => {
    try { window.localStorage.setItem(STORAGE_KEY, locale); } catch { /* not fatal */ }
    // Keep the document language honest for screen readers and hyphenation.
    try { document.documentElement.lang = locale; } catch { /* SSR */ }
  }, [locale]);
  const value = { locale, setLocale, t: (s, params) => translate(locale, s, params) };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useI18n() { return useContext(Ctx); }

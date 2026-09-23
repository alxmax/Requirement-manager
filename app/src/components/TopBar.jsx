// implements: ARCH-VIEWER-007
import { useState, useMemo } from "react";
import { REQUIREMENTS, REPO } from "../lib/data.js";
import { searchRequirements } from "../lib/search.js";
import { Icon, Logomark } from "../lib/icons.jsx";
import { useI18n, LOCALES } from "../lib/i18n.jsx";

const LOCALE_BTN = {
  fontFamily: "var(--font-mono)", fontSize: 11, fontWeight: 600,
  letterSpacing: ".04em", width: 34,
};

export function TopBar({ query, setQuery, theme, setTheme, onSearchPick }) {
  const { t, locale, setLocale } = useI18n();
  const nextLocale = () => {
    const at = LOCALES.findIndex((l) => l.code === locale);
    setLocale(LOCALES[(at + 1) % LOCALES.length].code);
  };
  const [open, setOpen] = useState(false);
  const q = query.trim();
  const hits = useMemo(
    () => q ? searchRequirements(REQUIREMENTS, q, { top: 8 }) : [],
    [q, REQUIREMENTS]
  );
  return (
    <header className="topbar">
      <div className="brand">
        <Logomark size={26} />
        <span className="wm">Requirement<b> Manager</b></span>
      </div>
      <span className="repo">
        <span className="dot" />{REPO || t("local repo")}
      </span>
      <div className="spacer" />
      <div className="search">
        <span className="ico"><Icon name="search" size={15} /></span>
        <input className="search-inp"
          placeholder={t("Search id, title, contract…")}
          value={query} onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setOpen(true)}
          onBlur={() => setOpen(false)}
          onKeyDown={(e) => {
            if (e.key === "Escape") { setQuery(""); e.currentTarget.blur(); }
          }} />
        {q && open && (
          <div className="search-res">
            {hits.length ? hits.map((h) => (
              <div className="search-hit" key={h.req.id}
                onMouseDown={() => onSearchPick(h.req.id)}>
                <span className="hid">{h.req.id}</span>
                <span className="htitle">{h.req.title}</span>
                <span className="hscore">
                  {h.kind === "score" ? h.score.toFixed(2) : h.kind}
                </span>
              </div>
            )) : <div className="search-empty">{t("no strong match")}</div>}
          </div>
        )}
      </div>
      <button className="btn-icon bare" title={t("switch language")}
        aria-label={t("switch language")} onClick={nextLocale}
        style={LOCALE_BTN}>
        {(LOCALES.find((l) => l.code === locale) || LOCALES[0]).label}
      </button>
      <button className="btn-icon bare" title={t("toggle theme")}
        onClick={() => setTheme(theme === "light" ? "dark" : "light")}>
        <Icon name={theme === "light" ? "moon" : "sun"} size={17} />
      </button>
    </header>
  );
}

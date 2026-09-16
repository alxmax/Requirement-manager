// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-964
import { COMMANDS } from "../lib/data.js";
import { useI18n } from "../lib/i18n.jsx";
import { CommandGroup } from "./commands/CommandGroup.jsx";

const GROUPS = [
  { key: "author", label: "Author", hint: "writing and evolving a requirement" },
  { key: "build", label: "Build", hint: "turning it into code, and proving it" },
  { key: "read", label: "Read", hint: "asking the corpus questions" },
];

const EMPTY_NOTE = {
  marginTop: 6, color: "var(--fg-muted)", font: "var(--text-small)", maxWidth: 460,
};

export function CommandsView() {
  const { t, locale } = useI18n();
  const list = Array.isArray(COMMANDS) ? COMMANDS : [];

  if (!list.length) {
    return (
      <div className="main">
        <div className="prob-empty">
          <b>{t("No command list in this map.")}</b>
          <div style={EMPTY_NOTE}>
            {t(
              "Regenerate it with a current engine — `reqmap.py sync` writes the command "
              + "reference into _map.json.",
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="main">
      <div className="cmds">
        <p className="cmds-lede">
          {t("Every verb the engine exposes, generated from its own command registry.")}
        </p>
        {GROUPS.map((g) => (
          <CommandGroup key={g.key} group={g} locale={locale} t={t}
            rows={list.filter((c) => c.group === g.key)} />
        ))}
      </div>
    </div>
  );
}

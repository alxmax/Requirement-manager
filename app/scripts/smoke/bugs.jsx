// tested-by: REQ-BUGS-1121
// tested-by: REQ-BUGS-1122
// tested-by: REQ-BUGS-1123
// tested-by: REQ-MAPSTAMP-1124
// tested-by: REQ-MAPSTAMP-1125
/* Render smoke test, part: the Bugs tab and the file it writes. Adopts a list
 * of bugs, checks the panel, then adopts an empty one so the parts after this
 * see the real export again. */
import { renderToString } from "react-dom/server";

import { adoptMapExport } from "../../src/lib/data.js";
import { I18nProvider, useI18n } from "../../src/lib/i18n.jsx";
import { Rail } from "../../src/components/Rail.jsx";
import {
  appendBug, bugCommand, moduleFile, saveBug,
} from "../../src/lib/bugFile.js";
import { ProblemsView } from "../../src/views/ProblemsView.jsx";
import {
  BugForm, BugReport, BugsPanel, moduleChoices,
} from "../../src/views/problems/BugsPanel.jsx";
import { noop, test } from "./harness.jsx";
import fixture from "./bugfile.fixture.json";

const bug = (ref, module, prio, date = "") => ({
  id: `${module}:${ref}`, ref, module, prio, date, title: `Title ${ref}`,
  estimated: false, where: "", why: "", source: "", file: "" });
const BUGS_FIXTURE = [bug("B1", "Payments", "P1", "2026-03-15"),
  bug("B2", "Payments", "P2"), bug("B1", "Search", "P3")];

const page = (locale) => renderToString(
  <I18nProvider initialLocale={locale}>
    <ProblemsView openSpec={noop} problems={[]} initialFilter="BUGS" />
  </I18nProvider>);
const panel = renderToString(
  <I18nProvider initialLocale="en">
    <BugsPanel added={[]} setAdded={noop} />
  </I18nProvider>);

adoptMapExport({ bugs: BUGS_FIXTURE });
const english = page("en");
const romanian = page("ro");
const emptyPanelOf = () => renderToString(
  <I18nProvider initialLocale="en">
    <BugsPanel added={[]} setAdded={noop} />
  </I18nProvider>);
const fullPanel = emptyPanelOf();
const groups = (english.match(/class="bug-group"/g) || []).length;
adoptMapExport({ bugs: [] });
const empty = page("en");
const emptyPanel = emptyPanelOf();

const reported = { ...bug("B1", "Payments", "P1", "2026-03-15"), why: "Money",
  where: "`p.py:3`", source: "ticket", file: "bugs/Payments.md", line: 5 };
const report = renderToString(
  <I18nProvider initialLocale="en">
    <BugReport keys={["Payments"]} scope="P1"
      groups={{ Payments: [bug("B2", "Payments", "P2"), reported] }} />
  </I18nProvider>);

const rail = () => renderToString(
  <I18nProvider initialLocale="en">
    <Rail view="explorer" setView={noop} focus={null} setFocus={noop}
      problems={[]} openProblems={noop} />
  </I18nProvider>);
adoptMapExport({ engine_version: "2026-11-02.1", branch: "side" });
const stamped = rail();
adoptMapExport({ branch: null });
const unstamped = rail();

/** What the provider picks and stores, with a fake window: `ro` from the map,
 *  nothing written by opening it. */
function LocaleProbe() {
  return <i>{useI18n().t("Bugs")}</i>;
}
const realWindow = globalThis.window;
const written = [];
globalThis.window = { __REQMAP_DATA__: { language: "ro" }, localStorage: {
  getItem: () => null, setItem: (k, v) => written.push([k, v]) } };
const opened = renderToString(<I18nProvider><LocaleProbe /></I18nProvider>);
globalThis.window = realWindow;

/** A folder handle over a plain object: what the File System Access API
 *  hands back, and the only way to run `saveBug` outside a browser. */
function fakeFolder(files) {
  const handle = (name) => ({
    getFile: async () => ({ text: async () => files[name] || "" }),
    createWritable: async () => ({
      write: async (text) => { files[name] = text; }, close: async () => {},
    }),
  });
  const folder = {
    getFileHandle: async (name, opts) => {
      if (!(name in files) && !(opts && opts.create)) throw new Error("none");
      return handle(name);
    },
    getDirectoryHandle: async () => folder,
  };
  return folder;
}

const form = renderToString(
  <I18nProvider initialLocale="en">
    <BugForm modules={["Core"]} add={noop} close={noop} error={null} />
  </I18nProvider>);

const command = bugCommand({ title: 'Says "no"', module: "Core", prio: "P1" });

const bugChecks = [
  // verifies: REQ-BUGS-1121#CASE-1
  ["bugs: the tab counts the known bugs", />Bugs<span[^>]*>3</.test(english)],
  // verifies: REQ-BUGS-1121#CASE-2
  ["bugs: one group per module, the date under the priority",
    groups === 2 && english.includes("Payments") && /P1<\/span><span class="bug-date">15\.03\.2026</.test(english)],
  // verifies: REQ-BUGS-1121#CASE-3
  ["bugs: the label follows the language",
    />Buguri<span/.test(romanian) && romanian.includes("Caută în buguri")
      && !/>Bugs<span/.test(romanian)],
  // verifies: REQ-BUGS-1121#CASE-4
  ["bugs: a repository with no bugs still has the tab and the button",
    />Bugs<span[^>]*>0</.test(empty) && empty.includes("Add bug")
      && panel.includes("Add bug")],
  // verifies: REQ-BUGS-1123#CASE-1
  ["bugs: the report holds every field, highest priority first",
    ["P1 1", "P2 1", "Money", "`p.py:3`", "ticket", "bugs/Payments.md:5",
      "15.03.2026"].every((s) => report.includes(s))
      && report.indexOf("B1") < report.indexOf("B2")
      && !report.includes("<details")],
  // verifies: REQ-BUGS-1123#CASE-2
  ["bugs: the report states its filter and total",
    /2 bugs ·.*· P1</.test(report.replace(/<!-- -->/g, ""))],
  // verifies: REQ-BUGS-1123#CASE-3
  ["bugs: the export button needs something to export",
    /<button[^>]*disabled=""[^>]*>Export PDF/.test(emptyPanel)
      && /<button[^>]*>Export PDF/.test(fullPanel)
      && !/<button[^>]*disabled=""[^>]*>Export PDF/.test(fullPanel)],
  // verifies: REQ-MAPSTAMP-1124#CASE-3
  ["stamp: the footer shows what the map carries",
    stamped.includes("engine 2026-11-02.1 · side")
      && !unstamped.includes("map-stamp")],
  // verifies: REQ-MAPSTAMP-1125#CASE-4
  ["language: the page opens in the map's language and stores nothing",
    opened.includes("Buguri") && written.length === 0],
  // verifies: REQ-BUGS-1119#CASE-6
  ["bugs: the viewer writes the fixture's bytes",
    fixture.every((c) => moduleFile(c.bug.module) === c.file
      && appendBug(c.text, c.bug).text === c.expected)],
  // verifies: REQ-BUGS-1122#CASE-5
  ["bugs: the form has six fields and suggests modules",
    (form.match(/<(input|select|textarea)\b/g) || []).length === 6
      && form.includes('list="bug-modules"') && form.includes('value="Core"')],
  // verifies: REQ-BUGS-1122#CASE-3
  ["bugs: no API, a quoted command",
    command === 'python scripts/reqmap.py sync --bug "Says \\"no\\"" '
      + '--module "Core" --prio "P1"'],
  // verifies: REQ-BUGS-1122#CASE-4
  ["bugs: a new repository still has module suggestions",
    moduleChoices([], [
      { level: "architecture", status: "draft", title: "Checkout" },
      { level: "architecture", status: "deprecated", title: "Old" },
      { level: "code", status: "draft", title: "Detail" },
    ]).join() === "Checkout"],
];
for (const [label, ok] of bugChecks) test(label, ok);

/** `saveBug` over a fake folder. It caches the folder it was given, so the
 * refusal runs first: a refused folder is never cached. */
export async function bugFileChecks() {
  globalThis.window = globalThis.window || {};
  const picker = window.showDirectoryPicker;
  const refusedFiles = {};
  window.showDirectoryPicker = async () => fakeFolder(refusedFiles);
  const refused = await saveBug({ module: "Core", title: "T", prio: "P2" })
    .then(() => "", (e) => e.message);
  const disk = { "_map.json": "{}" };
  disk["Core.md"] = appendBug("", { module: "Core", title: "Newer",
    prio: "P1" }).text;
  window.showDirectoryPicker = async () => fakeFolder(disk);
  const saved = await saveBug({ module: "Core", title: "Mine", prio: "P2" });
  window.showDirectoryPicker = picker;
  // verifies: REQ-BUGS-1122#CASE-1
  test("bugs: a save keeps what the file holds now",
    saved.ref === "B2" && disk["Core.md"].includes("| B1 | Newer | P1 |")
      && disk["Core.md"].includes("| B2 | Mine | P2 |"));
  // verifies: REQ-BUGS-1122#CASE-2
  test("bugs: a folder with no _map.json is refused",
    refused.includes("requirements folder")
      && Object.keys(refusedFiles).length === 0);
}

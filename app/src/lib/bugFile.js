// implements: ARCH-BUGS-078
// implements: REQ-BUGS-1122
// implements: REQ-BUGS-1126
import { BUG_FORMAT, BUGS_FIXED } from "./data.js";

/* One bug row into the module's file under `requirements/bugs/`, from the
 * browser.
 *
 * `moduleFile`, `bugFile` and `appendBug` are `reqmap_engine/bugs.py`'s, ported:
 * the CLI
 * and the page write the same file, and one fixture pins both. A page can
 * write to disk only in a browser with the File System Access API, and only
 * into a folder the reader picks; anywhere else the panel prints the
 * `sync --bug` command instead. */

const COLUMNS = ["ID", "Bug", "Priority", "Date", "Where", "Why it matters",
  "Source"];
const KEYS = ["id", "title", "prio", "date", "where", "why", "source"];
const DEFAULT_FORMAT = { columns: { id: ["#"] }, skip: "" };
const DATED = /\d{4}-\d{2}-\d{2}|\d{2}\.\d{2}\.\d{4}/;

const escapeCell = (v) => String(v || "").split(/\s+/).filter(Boolean)
  .join(" ").replace(/\|/g, "\\|");

/** A module's file name: its words joined by `-`, or "" when it has none. */
export function moduleFile(module) {
  const stem = String(module || "").replace(/[^\p{L}\p{N}_]+/gu, "-")
    .replace(/^-+|-+$/g, "");
  return stem ? `${stem}.md` : "";
}

const cells = (line) => line.trim().split(/(?<!\\)\|/).slice(1, -1)
  .map((c) => c.trim().replace(/\\\|/g, "|"));
const isSeparator = (line) => line.startsWith("|")
  && /^[\s|:-]+$/.test(line) && line.includes("-");

function columnIndex(header, columns) {
  const names = header.map((c) => c.toLowerCase());
  const index = {};
  KEYS.forEach((key, i) => {
    const extra = columns[key] || [];
    const wanted = [COLUMNS[i], ...(typeof extra === "string" ? [extra] : extra)];
    const hit = wanted.map((w) => names.indexOf(String(w).toLowerCase()))
      .find((n) => n >= 0);
    if (hit !== undefined) index[key] = hit;
  });
  return ["id", "title", "prio"].every((k) => k in index) ? index : null;
}

function sectionPrios(heading) {
  const m = heading.match(/\bP([0-4])(?:\s*[-–—]\s*P([0-4]))?\b/);
  if (!m) return "";
  let digits = "";
  for (let n = +m[1]; n <= +(m[2] || m[1]); n += 1) digits += n;
  return digits;
}

/** A Python pattern as a JavaScript one: only the `(?i)` prefix differs. */
function skipPattern(source) {
  if (!source) return null;
  const blind = source.startsWith("(?i)");
  return new RegExp(blind ? source.slice(4) : source, blind ? "i" : "");
}

function bugTables(lines, format) {
  const skip = skipPattern(format.skip);
  const tables = [];
  let prios = "";
  let skipped = false;
  let n = 0;
  while (n < lines.length) {
    const section = lines[n].match(/^##\s+(.+)/);
    if (section) {
      prios = sectionPrios(section[1]);
      skipped = Boolean(skip && skip.test(section[1]));
    }
    if (lines[n].startsWith("|") && n + 1 < lines.length
        && isSeparator(lines[n + 1])) {
      let end = n + 2;
      while (end < lines.length && lines[end].startsWith("|")) end += 1;
      const index = columnIndex(cells(lines[n]), format.columns || {});
      if (index && !skipped) tables.push({ at: n, end, index, prios });
      n = end;
    } else {
      n += 1;
    }
  }
  return tables;
}

/** {text, ref}: `bug` added with the next free `B<n>`, past `floor`, as the
 * last row of the table under its priority's `##` section, else of the file's
 * first bug table, in that table's own columns. Pure. */
export function appendBug(text, bug, floor = 0, format = DEFAULT_FORMAT) {
  let body = text.replace(/\r\n/g, "\n");
  if (!body.trim()) body = `# Bugs — ${bug.module}\n`;
  const used = [...body.matchAll(/^\|\s*B(\d+)\*?\s*\|/gm)].map((m) => +m[1]);
  const ref = `B${Math.max(floor, ...used) + 1}`;
  const values = { ...bug, id: ref };
  const lines = body.replace(/\n+$/, "").split("\n");
  const tables = bugTables(lines, format);
  const digit = (String(bug.prio || "").match(/\bP([0-4])\b/) || [])[1];
  const table = tables.find((t) => digit && t.prios.includes(digit)) || tables[0];
  if (table) {
    const row = cells(lines[table.at]).map(() => "");
    Object.entries(table.index).forEach(([key, column]) => {
      row[column] = escapeCell(values[key]);
    });
    lines.splice(table.end, 0, `| ${row.join(" | ")} |`);
  } else {
    lines.push("", `| ${COLUMNS.join(" | ")} |`,
      `|${"---|".repeat(COLUMNS.length)}`,
      `| ${KEYS.map((k) => escapeCell(values[k])).join(" | ")} |`);
  }
  return { text: `${lines.join("\n")}\n`, ref };
}

/** `bugs.py`'s `module_key`: a module's words, without case or diacritics. */
export function moduleKey(name) {
  const text = name.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase();
  return (text.match(/[\p{L}\p{N}]+/gu) || []).join(" ") || name;
}

function headingModule(text, stem) {
  const m = text.match(/^#\s+(.+?)\s*$/m);
  if (!m) return stem;
  let title = m[1];
  const tail = title.match(/\(([^()]*)\)\s*$/);
  if (tail && DATED.test(tail[1])) title = title.slice(0, tail.index).trim();
  return title.split(/\s[—–-]\s/).pop().trim() || stem;
}

/** The file a module's bug goes to, from [[name, text]]: the one whose heading
 * or stem, without an `NN_` prefix, names the module. A new module is numbered
 * when the files are. */
export function bugFile(files, module) {
  const key = moduleKey(module);
  const numbers = [];
  for (const [name, text] of files) {
    const stem = name.slice(0, -".md".length);
    const bare = stem.match(/^(\d+)[_-](.+)$/);
    if (bare) numbers.push(bare[1]);
    if ([headingModule(text, stem), bare ? bare[2] : stem]
      .some((n) => moduleKey(n) === key)) return name;
  }
  const fresh = moduleFile(module);
  if (!numbers.length || !fresh) return fresh;
  const next = Math.max(...numbers.map(Number)) + 1;
  return `${String(next).padStart(numbers[0].length, "0")}_${fresh}`;
}

/** The command that adds `bug`, for a browser that cannot write. */
export function bugCommand(bug) {
  const quote = (v) => `"${String(v).replace(/(["\\$`])/g, "\\$1")}"`;
  const flags = [["--module", bug.module], ["--prio", bug.prio],
    ["--date", bug.date], ["--where", bug.where], ["--why", bug.why],
    ["--source", bug.source]].filter(([, v]) => v);
  return ["python scripts/reqmap.py sync --bug", quote(bug.title),
    ...flags.map(([f, v]) => `${f} ${quote(v)}`)].join(" ");
}

export const canWrite = () => typeof window !== "undefined"
  && typeof window.showDirectoryPicker === "function";

let folder = null;   // chosen once per page

async function bugsFolder() {
  if (folder) return folder;
  const reqs = await window.showDirectoryPicker({ mode: "readwrite" });
  try {
    await reqs.getFileHandle("_map.json");
  } catch {
    throw new Error("Choose the requirements folder, the one holding "
      + "_map.json.");
  }
  folder = await reqs.getDirectoryHandle("bugs", { create: true });
  return folder;
}

async function folderFiles(dir) {
  const register = BUG_FORMAT.register || "_fixed.md";
  const files = [];
  for await (const handle of dir.values()) {
    if (handle.kind === "file" && handle.name.endsWith(".md")
        && handle.name !== register) {
      files.push([handle.name, await (await handle.getFile()).text()]);
    }
  }
  return files.sort(([a], [b]) => (a < b ? -1 : 1));
}

/** The highest `B<n>` the register holds for one file, so a number is never
 * given twice. */
function highestClosed(stem) {
  const numbers = BUGS_FIXED.map((r) => String(r.id || "").match(/^(.+)[:\s]B(\d+)$/))
    .filter((m) => m && m[1].trim() === stem).map((m) => +m[2]);
  return Math.max(0, ...numbers);
}

/** Write `bug` to its module's file, reading the file first so a row added
 * since the map was built is kept. Returns {ref, file}. */
export async function saveBug(bug) {
  const dir = await bugsFolder();
  const files = await folderFiles(dir);
  const name = bugFile(files, bug.module);
  const handle = await dir.getFileHandle(name, { create: true });
  const current = await (await handle.getFile()).text();
  const format = { ...DEFAULT_FORMAT, ...BUG_FORMAT };
  const { text, ref } = appendBug(current, bug,
    highestClosed(name.slice(0, -".md".length)), format);
  const out = await handle.createWritable();
  await out.write(text);
  await out.close();
  return { ref, file: `requirements/bugs/${name}` };
}

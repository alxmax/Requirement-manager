// implements: ARCH-BUGS-078
// implements: REQ-BUGS-1122
/* One bug row into `requirements/bugs/<module>.md`, from the browser.
 *
 * `moduleFile` and `appendBug` are `reqmap_engine/bugs.py`'s, ported: the CLI
 * and the page write the same file, and one fixture pins both. A page can
 * write to disk only in a browser with the File System Access API, and only
 * into a folder the reader picks; anywhere else the panel prints the
 * `sync --bug` command instead. */

const COLUMNS = ["ID", "Bug", "Priority", "Date", "Where", "Why it matters",
  "Source"];
const KEYS = ["title", "prio", "date", "where", "why", "source"];

const escapeCell = (v) => String(v || "").split(/\s+/).filter(Boolean)
  .join(" ").replace(/\|/g, "\\|");

/** A module's file name: its words joined by `-`, or "" when it has none. */
export function moduleFile(module) {
  const stem = String(module || "").replace(/[^\p{L}\p{N}_]+/gu, "-")
    .replace(/^-+|-+$/g, "");
  return stem ? `${stem}.md` : "";
}

/** {text, ref}: `bug` added as the last row of the file's bug table, with the
 * next free `B<n>`. Pure. */
export function appendBug(text, bug) {
  let body = text.replace(/\r\n/g, "\n");
  if (!body.trim()) body = `# Bugs — ${bug.module}\n`;
  const used = [...body.matchAll(/^\|\s*B(\d+)\*?\s*\|/gm)].map((m) => +m[1]);
  const ref = `B${Math.max(0, ...used) + 1}`;
  const row = `| ${[ref, ...KEYS.map((k) => escapeCell(bug[k]))].join(" | ")} |`;
  const head = `| ${COLUMNS.join(" | ")} |`;
  const lines = body.replace(/\n+$/, "").split("\n");
  const at = lines.indexOf(head);
  if (at >= 0) {
    let end = at + 2;
    while (end < lines.length && lines[end].startsWith("|")) end += 1;
    lines.splice(end, 0, row);
  } else {
    lines.push("", head, `|${"---|".repeat(COLUMNS.length)}`, row);
  }
  return { text: `${lines.join("\n")}\n`, ref };
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

/** Write `bug` to its module's file, reading the file first so a row added
 * since the map was built is kept. Returns {ref, file}. */
export async function saveBug(bug) {
  const name = moduleFile(bug.module);
  const handle = await (await bugsFolder())
    .getFileHandle(name, { create: true });
  const current = await (await handle.getFile()).text();
  const { text, ref } = appendBug(current, bug);
  const out = await handle.createWritable();
  await out.write(text);
  await out.close();
  return { ref, file: `requirements/bugs/${name}` };
}

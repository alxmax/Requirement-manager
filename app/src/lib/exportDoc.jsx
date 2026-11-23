// implements: REQ-VIEWER-1151
/* What every export shares. A PDF is the browser's print of a `PrintDoc`: the
 * same components the page shows, in the app's own styles, on the paper theme
 * whatever theme the screen is in, under a header naming the repository, the
 * page and the date. A spreadsheet is an .xlsx built in the browser. */
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { REPO } from "./data.js";
import { xlsxBytes } from "./xlsx.js";

/** The reader's own day: `toISOString` alone is UTC, a day behind at night. */
export const today = () => {
  const now = new Date();
  return new Date(now - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
};

/** Puts `root` on the paper theme and returns what puts the screen's theme
 * back: a dark or high-contrast screen still prints a light page. */
export function paperTheme(root) {
  const theme = root.getAttribute("data-theme");
  root.removeAttribute("data-theme");
  return () => { if (theme) root.setAttribute("data-theme", theme); };
}

/** `[printing, setPrinting]`: true opens the print dialog once, on the paper
 * theme; closing the dialog puts the screen's theme back. */
export function usePrinting() {
  const [printing, setPrinting] = useState(false);
  useEffect(() => {
    if (!printing) return undefined;
    const restore = paperTheme(document.documentElement);
    const done = () => { restore(); setPrinting(false); };
    window.addEventListener("afterprint", done);
    window.print();
    return () => window.removeEventListener("afterprint", done);
  }, [printing]);
  return [printing, setPrinting];
}

/** The printed page: a header, the body, a footer. `meta` is one line of
 * facts (counts, filter); empty parts are left out. */
export function PrintSheet({ title, meta = [], dated = true, children, className = "" }) {
  return (
    <div className={("print-doc " + className).trim()}>
      <header className="print-head">
        <div className="print-brand">
          <span>requirement-manager</span>
          {REPO && <span>{REPO}</span>}
        </div>
        <h1>{title}</h1>
        <div className="print-meta">
          {[dated && today(), ...meta].filter(Boolean).join(" · ")}
        </div>
      </header>
      <div className="print-body">{children}</div>
    </div>
  );
}

/** `PrintSheet`, mounted outside the app so the print rules can hide the
 * rest. Rendered only while printing. */
export function PrintDoc(props) {
  return createPortal(<PrintSheet {...props} />, document.body);
}

/** Saves `data` under `name`. */
export function downloadBlob(name, data, type) {
  const url = URL.createObjectURL(new Blob([data], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export const XLSX_TYPE =
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";

/** Saves a one-sheet workbook. `sheet` is `{ name, header, rows, widths }`. */
export function downloadXlsx(file, sheet) {
  downloadBlob(file, xlsxBytes(sheet.name, sheet.header, sheet.rows, sheet.widths),
    XLSX_TYPE);
}

/** A file name: the repository's short name, the page, the date. */
export function exportName(page, ext) {
  const repo = String(REPO || "").split("/").pop();
  return [repo, page, today()].filter(Boolean).join("-")
    .replace(/[^A-Za-z0-9._-]+/g, "-") + "." + ext;
}

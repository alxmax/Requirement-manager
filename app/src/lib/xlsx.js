// implements: REQ-VIEWER-1152
/* A one-sheet .xlsx written in the browser, with no library: the five XML
 * parts a spreadsheet needs, packed in a stored (uncompressed) zip. Text cells
 * are inline strings, the header row is bold and frozen, and the columns carry
 * an autofilter, so the file opens in Excel, LibreOffice and Google Sheets as
 * a table ready to sort. The viewer stays one HTML file: nothing is fetched. */

const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

export function crc32(bytes) {
  let c = 0xFFFFFFFF;
  for (let i = 0; i < bytes.length; i++) c = CRC_TABLE[(c ^ bytes[i]) & 0xFF] ^ (c >>> 8);
  return (c ^ 0xFFFFFFFF) >>> 0;
}

/** A stored zip of `[name, Uint8Array]` entries, as one Uint8Array. */
export function zipStored(files) {
  const enc = new TextEncoder();
  const parts = [];
  const central = [];
  let offset = 0;
  const u16 = (v) => [v & 0xFF, (v >>> 8) & 0xFF];
  const u32 = (v) => [v & 0xFF, (v >>> 8) & 0xFF, (v >>> 16) & 0xFF, (v >>> 24) & 0xFF];
  files.forEach(([name, data]) => {
    const fn = enc.encode(name);
    const crc = crc32(data);
    const head = [...u16(20), ...u16(0x0800), ...u16(0), ...u16(0), ...u16(0x21),
      ...u32(crc), ...u32(data.length), ...u32(data.length), ...u16(fn.length), ...u16(0)];
    const local = new Uint8Array([0x50, 0x4B, 0x03, 0x04, ...head]);
    parts.push(local, fn, data);
    central.push(new Uint8Array([0x50, 0x4B, 0x01, 0x02, ...u16(20), ...head,
      ...u16(0), ...u16(0), ...u16(0), ...u32(0), ...u32(offset)]), fn);
    offset += local.length + fn.length + data.length;
  });
  const size = central.reduce((n, p) => n + p.length, 0);
  const end = new Uint8Array([0x50, 0x4B, 0x05, 0x06, ...u16(0), ...u16(0),
    ...u16(files.length), ...u16(files.length), ...u32(size), ...u32(offset), ...u16(0)]);
  const all = [...parts, ...central, end];
  const out = new Uint8Array(all.reduce((n, p) => n + p.length, 0));
  let at = 0;
  all.forEach((p) => { out.set(p, at); at += p.length; });
  return out;
}

const esc = (s) => String(s ?? "")
  // characters XML 1.0 forbids, then the five it escapes
  .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "")
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;");

/** The column letters of a 0-based index: 0 → A, 26 → AA. */
export function colName(i) {
  let s = "";
  for (let n = i + 1; n > 0; n = Math.floor((n - 1) / 26)) {
    s = String.fromCharCode(65 + ((n - 1) % 26)) + s;
  }
  return s;
}

/** The worksheet XML: a bold, frozen header, then one row per record. */
export function sheetXml(header, rows, widths = []) {
  const cell = (v, r, c, style) => `<c r="${colName(c)}${r}" t="inlineStr"${
    style ? ` s="${style}"` : ""}><is><t xml:space="preserve">${esc(v)}</t></is></c>`;
  const line = (vals, r, style) => `<row r="${r}">${
    vals.map((v, c) => cell(v, r, c, style)).join("")}</row>`;
  const cols = header.map((_, i) => `<col min="${i + 1}" max="${i + 1}" width="${
    widths[i] || 18}" customWidth="1"/>`).join("");
  const last = `${colName(header.length - 1)}${rows.length + 1}`;
  return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    + '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    + '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" '
    + 'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
    + `<cols>${cols}</cols><sheetData>${line(header, 1, 1)}${
      rows.map((r, i) => line(r, i + 2, 2)).join("")}</sheetData>`
    + `<autoFilter ref="A1:${last}"/></worksheet>`;
}

const STYLES = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
  + '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
  + '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
  + '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
  + '<fills count="2"><fill><patternFill patternType="none"/></fill>'
  + '<fill><patternFill patternType="gray125"/></fill></fills>'
  + '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
  + '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
  + '<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
  + '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
  + '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1">'
  + '<alignment vertical="top" wrapText="1"/></xf></cellXfs>'
  + '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
  + "</styleSheet>";

/** The bytes of a one-sheet workbook. A sheet name loses the characters
 * Excel refuses and is cut to its 31-character limit. */
export function xlsxBytes(sheet, header, rows, widths) {
  const name = esc(String(sheet || "Sheet1").replace(/[\\/?*[\]:]/g, " ").slice(0, 31));
  const x = (s) => new TextEncoder().encode(s);
  const pre = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>';
  const rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships";
  const sml = "application/vnd.openxmlformats-officedocument.spreadsheetml.";
  const override = (part, kind) =>
    `<Override PartName="${part}" ContentType="${sml}${kind}+xml"/>`;
  return zipStored([
    ["[Content_Types].xml", x(pre
      + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      + '<Default Extension="rels" '
      + 'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      + '<Default Extension="xml" ContentType="application/xml"/>'
      + override("/xl/workbook.xml", "sheet.main")
      + override("/xl/worksheets/sheet1.xml", "worksheet")
      + override("/xl/styles.xml", "styles")
      + "</Types>")],
    ["_rels/.rels", x(pre
      + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
      + `<Relationship Id="rId1" Type="${rel}/officeDocument" Target="xl/workbook.xml"/>`
      + "</Relationships>")],
    ["xl/workbook.xml", x(pre
      + '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
      + `xmlns:r="${rel}"><sheets><sheet name="${name}" sheetId="1" r:id="rId1"/>`
      + "</sheets>"
      + `<definedNames><definedName name="_xlnm._FilterDatabase" localSheetId="0" hidden="1">'${
        name}'!$A$1:$${colName(header.length - 1)}$${rows.length + 1}</definedName></definedNames>`
      + "</workbook>")],
    ["xl/_rels/workbook.xml.rels", x(pre
      + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
      + `<Relationship Id="rId1" Type="${rel}/worksheet" Target="worksheets/sheet1.xml"/>`
      + `<Relationship Id="rId2" Type="${rel}/styles" Target="styles.xml"/>`
      + "</Relationships>")],
    ["xl/worksheets/sheet1.xml", x(sheetXml(header, rows, widths))],
    ["xl/styles.xml", x(STYLES)],
  ]);
}

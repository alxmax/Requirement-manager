"""Requirements kept as rows: a CSV file or a JSON list, read through a field
map (ADR-0088). Imported at call time by `customtrace`, only for a source whose
format is `csv` or `json`, so a repository without one never loads it."""
# implements: ARCH-CUSTOMTRACE-077  # implements: REQ-CUSTOMTRACE-1138
import csv
import io
import json
import re

ROW_FORMATS = ("csv", "json")
FIELD_KEYS = ("id", "title", "contract", "cases", "status", "depends_on",
              "satisfies")
_STATUSES = ("confirmed", "draft", "deprecated")
_SENTENCE = re.compile(r"(?<=[.!?])\s+")


def validate(entry):
    # implements: REQ-CUSTOMTRACE-1138
    """(extras for a kept source, or None; the problem, or None) for one
    `REQUIREMENT_SOURCES` entry whose format is csv or json."""
    fields = entry.get("fields")
    if not isinstance(fields, dict) or not isinstance(fields.get("id"), str):
        return None, "fields must map at least id to a column or key"
    unknown = sorted(set(fields) - set(FIELD_KEYS) - {"structural"})
    if unknown:
        return None, "fields has unknown key(s) {}".format(", ".join(unknown))
    st = fields.get("structural")
    if st is not None and not (isinstance(st, dict) and isinstance(st.get("field"), str)
                               and isinstance(st.get("values"), list)):
        return None, "fields.structural must be {field, values}"
    delim = entry.get("delimiter", ",")
    if not (isinstance(delim, str) and len(delim) == 1):
        return None, "delimiter must be one character"
    return {"fields": fields, "delimiter": delim,
            "items": entry.get("items"), "list_separator": entry.get("list_separator", ",")}, None


def _rows(text, src):
    """The source's rows as dicts, or raise ValueError with why."""
    if src["format"] == "csv":
        return list(csv.DictReader(io.StringIO(text), delimiter=src["delimiter"]))
    data = json.loads(text)
    if src.get("items"):
        data = data.get(src["items"]) if isinstance(data, dict) else None
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise ValueError("expected a list of objects")
    return data


def _cell(row, key, fields):
    name = fields.get(key)
    value = row.get(name) if name else None
    return "" if value is None else value


def _items(value, sep):
    """A cell as a list: a JSON list as it is, a text split on `sep`."""
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [s.strip() for s in str(value).split(sep) if s.strip()]


def _body(title, contract, cases):
    """A requirement body the engine reads: one clause per sentence or item,
    one case per item."""
    clauses = (contract if isinstance(contract, list)
               else [s for s in _SENTENCE.split(" ".join(str(contract).split())) if s])
    lines = ["# " + title, "", "## Description", "Every bullet below is binding."]
    lines += ["- " + str(c).strip() for c in clauses if str(c).strip()]
    case_list = cases if isinstance(cases, list) else ([cases] if str(cases).strip() else [])
    if case_list:
        lines += ["", "## Cases"]
        lines += ["CASE-{} — {}".format(n, str(c).strip())
                  for n, c in enumerate(case_list, 1)]
    return "\n".join(lines) + "\n"


def blocks(text, src, path, problem):
    # implements: REQ-CUSTOMTRACE-1138
    """[(id, meta, body)] for every row of one file. A row with no id, an
    unreadable file and a corpus mostly marked structural are each a problem."""
    try:
        rows = _rows(text, src)
    except (ValueError, csv.Error) as e:
        problem("skipping requirement source {!r}: {}".format(path, e))
        return []
    fields, sep = src["fields"], src["list_separator"]
    st = fields.get("structural") or {}
    out, structural = [], 0
    for n, row in enumerate(rows, 1):
        rid = str(_cell(row, "id", fields)).strip()
        if not rid:
            problem("{!r} row {} has no id in {!r}".format(path, n, fields["id"]))
            continue
        status = str(_cell(row, "status", fields)).strip().lower()
        is_struct = bool(st) and str(row.get(st["field"], "")).strip() in st["values"]
        structural += is_struct
        meta = {"id": rid, "status": status if status in _STATUSES else src["status"],
                "layer": "aggregate" if is_struct else "feature",
                "owner": src["owner"], "source": src["format"],
                "depends_on": _items(_cell(row, "depends_on", fields), sep),
                "satisfies": _items(_cell(row, "satisfies", fields), sep)}
        contract = _cell(row, "contract", fields)
        first = (_items(contract, sep)[:1] or [""])[0] if isinstance(contract, list) else (
            _SENTENCE.split(" ".join(str(contract).split()))[0])
        title = str(_cell(row, "title", fields)).strip() or first[:80] or rid
        out.append((rid, meta, _body(title, contract, _cell(row, "cases", fields))))
    if out and structural * 2 > len(out):
        problem("{!r}: {} of {} rows are structural, exempt from code and tests; "
                "check fields.structural".format(path, structural, len(out)))
    return out

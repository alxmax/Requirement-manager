# ADR-0088 — Requirements kept as rows are read through a field map

- **Status:** Accepted. Extends [ADR-0077](0077-a-repository-describes-its-own-trace-tags.md).
- **Decided:** 2026-11-21
- **Evidence:** one field report (n=1): a corpus of about a thousand requirements exported as
  structured files needed a few hundred lines of glue to reach the engine, and a few hundred
  structural entries (headings, information) dominated the gate and the health score. One
  report is the reason to try this, not proof of general demand; the format is kept small.

## Context

ADR-0077 reads requirements kept as text, HTML or Markdown. A corpus exported from a
requirements tool is usually rows: a CSV file or a JSON list, with the tool's own column names,
and with entries that are not requirements at all.

## Decision

- **`format: csv` and `format: json`, read through `fields`.** The map names which column or key
  is the id (required), title, contract, cases, status, `depends_on` and `satisfies`. Stdlib
  `csv` and `json` only; a CSV file loses its byte-order mark and takes a `delimiter`; a JSON
  source is a list of objects, or one under the key `items` names.
- **A structural entry is an existing layer, not a new kind.** A row whose `structural.field`
  holds one of its `values` is layer `aggregate`, exempt from code and tests through the one
  predicate that already does it. When more than half the rows of a file are structural, that
  is reported: it usually means the map is wrong.
- **No YAML.** A stdlib YAML reader would be a grammar of its own; it waits for a second corpus
  that needs it (ROADMAP, Later).
- **In a lazy module.** `sourcerows.py` loads only for a csv or json source; the core does not
  change.

## Consequences

- A cell edited in the export is drift on the next `sync`, as for any source (ADR-0085 keeps it).
- A requirement read from a row has no `## Context` and no Given/When/Then; its cases are one
  line each.

## Revisit when

- A second independent corpus asks for YAML, or for a field this map cannot express.

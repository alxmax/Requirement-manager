---
id: CORE-SCAN-002
status: confirmed
layer: bus
owner: alex
depends_on: []
superseded_by:
---

# Member discovery

> Find every place in the code that claims membership of a capability, by scanning for tags.

## Input
- A code root directory and source files in known extensions (`.py`, `.js`, `.ts`,
  `.html`, …). Each tag is a comment of the form `role: <ID>`, where role is one of
  `implements`, `generated-from`, `validated-against`, `tested-by`.

## Description
The member list is the thread between intent and code, and it must never be
hand-maintained — that is the first thing to rot. So membership is *discovered*:
the code is the only place that declares it, and this capability reads it back.
`.git`, `node_modules`, `__pycache__` and `requirements/` are skipped so the tool
never scans its own outputs or vendored code.

## Output
- A dict `cap_id -> [(role, relative_file, line_number), ...]` covering every tag found.

## Acceptance (= tests)
- A file containing `# implements: <ID>` produces a member `(implements, file, line)` under `<ID>`.
- All four roles are recognized; an unknown role string produces no member.
- Excluded directories (`.git`, `node_modules`, `__pycache__`, `requirements`) are not scanned.
- An unreadable file is skipped without aborting the scan.

## Links
- Used by: (auto)
## Members in code (auto)

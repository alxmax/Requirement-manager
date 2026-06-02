---
generated: 2026-06-02 08:09
nodes: 8
edges: 9
---

# Requirement Map

## System Map

```mermaid
graph TD
  subgraph Features
    REQ_CHECK_006["REQ-CHECK-006"]
    REQ_EXTRACT_008["REQ-EXTRACT-008"]
    REQ_MAP_007["REQ-MAP-007"]
    REQ_NEW_004["REQ-NEW-004"]
    REQ_SCAN_005["REQ-SCAN-005"]
  end
  subgraph Bus
    CORE_DRIFT_003["CORE-DRIFT-003"]
    CORE_PARSE_001["CORE-PARSE-001"]
    CORE_SCAN_002["CORE-SCAN-002"]
  end
  REQ_CHECK_006 --> CORE_PARSE_001
  REQ_CHECK_006 --> CORE_SCAN_002
  REQ_CHECK_006 --> CORE_DRIFT_003
  REQ_EXTRACT_008 --> CORE_SCAN_002
  REQ_MAP_007 --> CORE_PARSE_001
  REQ_MAP_007 --> CORE_SCAN_002
  REQ_NEW_004 --> CORE_PARSE_001
  REQ_SCAN_005 --> CORE_PARSE_001
  REQ_SCAN_005 --> CORE_SCAN_002
```

## Requirement-to-Code

```mermaid
graph LR
  CORE_DRIFT_003["CORE-DRIFT-003"]
  f_scripts_reqmap_py_85_110["scripts\reqmap.py:85-110"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_85_110
  CORE_PARSE_001["CORE-PARSE-001"]
  f_scripts_reqmap_py_27_49["scripts\reqmap.py:27-49"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_27_49
  CORE_SCAN_002["CORE-SCAN-002"]
  f_scripts_reqmap_py_65["scripts\reqmap.py:65"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_65
  REQ_CHECK_006["REQ-CHECK-006"]
  f_scripts_reqmap_py_125["scripts\reqmap.py:125"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_125
  REQ_EXTRACT_008["REQ-EXTRACT-008"]
  f_scripts_reqmap_py_182_218["scripts\reqmap.py:182-218"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_182_218
  REQ_MAP_007["REQ-MAP-007"]
  f_scripts_reqmap_py_227_538["scripts\reqmap.py:227-538"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_227_538
  REQ_NEW_004["REQ-NEW-004"]
  f_scripts_reqmap_py_169["scripts\reqmap.py:169"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_169
  REQ_SCAN_005["REQ-SCAN-005"]
  f_scripts_reqmap_py_116["scripts\reqmap.py:116"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_116
```

## Behavioral Flow

```mermaid
flowchart LR
  in_CORE_DRIFT_003(["A requirement body (markdown) and the lock file `r"])
  CORE_DRIFT_003["CORE-DRIFT-003"]
  out_CORE_DRIFT_003(["A 12-char content hash of the binding sections; re"])
  in_CORE_DRIFT_003 --> CORE_DRIFT_003 --> out_CORE_DRIFT_003
  in_CORE_PARSE_001(["A `requirements/` directory containing `*.md` file"])
  CORE_PARSE_001["CORE-PARSE-001"]
  out_CORE_PARSE_001(["A dict `id -> {meta, body, path}`. `meta` is the p"])
  in_CORE_PARSE_001 --> CORE_PARSE_001 --> out_CORE_PARSE_001
  in_CORE_SCAN_002(["A code root directory and source files in known ex"])
  CORE_SCAN_002["CORE-SCAN-002"]
  out_CORE_SCAN_002(["A dict `cap_id -> [(role, relative_file, line_numb"])
  in_CORE_SCAN_002 --> CORE_SCAN_002 --> out_CORE_SCAN_002
  in_REQ_CHECK_006(["The loaded requirements, the discovered members, a"])
  REQ_CHECK_006["REQ-CHECK-006"]
  out_REQ_CHECK_006(["Printed `ERROR`/`WARN` lines plus a summary; exit "])
  in_REQ_CHECK_006 --> REQ_CHECK_006 --> out_REQ_CHECK_006
  in_REQ_EXTRACT_008(["A code root and the already-discovered members (so"])
  REQ_EXTRACT_008["REQ-EXTRACT-008"]
  out_REQ_EXTRACT_008(["One `requirements/DRAFT-*.md` per untagged file, e"])
  in_REQ_EXTRACT_008 --> REQ_EXTRACT_008 --> out_REQ_EXTRACT_008
  in_REQ_MAP_007(["The loaded requirements and the discovered members"])
  REQ_MAP_007["REQ-MAP-007"]
  out_REQ_MAP_007(["`requirements/_map.html`: multi-tab HTML viewer wi"])
  in_REQ_MAP_007 --> REQ_MAP_007 --> out_REQ_MAP_007
  in_REQ_NEW_004(["A capability id `AREA-NAME-NNN` (CLI argument) and"])
  REQ_NEW_004["REQ-NEW-004"]
  out_REQ_NEW_004(["A new `requirements/AREA-NAME-NNN.md` with the id "])
  in_REQ_NEW_004 --> REQ_NEW_004 --> out_REQ_NEW_004
  in_REQ_SCAN_005(["The loaded requirements and the discovered members"])
  REQ_SCAN_005["REQ-SCAN-005"]
  out_REQ_SCAN_005(["Printed lines: each capability id, then its `role "])
  in_REQ_SCAN_005 --> REQ_SCAN_005 --> out_REQ_SCAN_005
```

## Dependency Map

```mermaid
graph TD
  REQ_CHECK_006["REQ-CHECK-006"]
  CORE_PARSE_001["CORE-PARSE-001"]
  REQ_CHECK_006 --> CORE_PARSE_001
  CORE_SCAN_002["CORE-SCAN-002"]
  REQ_CHECK_006 --> CORE_SCAN_002
  CORE_DRIFT_003["CORE-DRIFT-003"]
  REQ_CHECK_006 --> CORE_DRIFT_003
  REQ_EXTRACT_008["REQ-EXTRACT-008"]
  REQ_EXTRACT_008 --> CORE_SCAN_002
  REQ_MAP_007["REQ-MAP-007"]
  REQ_MAP_007 --> CORE_PARSE_001
  REQ_MAP_007 --> CORE_SCAN_002
  REQ_NEW_004["REQ-NEW-004"]
  REQ_NEW_004 --> CORE_PARSE_001
  REQ_SCAN_005["REQ-SCAN-005"]
  REQ_SCAN_005 --> CORE_PARSE_001
  REQ_SCAN_005 --> CORE_SCAN_002
```

## Risk & Unknowns

```mermaid
graph TD
  CORE_PARSE_001["CORE-PARSE-001\nblast-radius"]
  style CORE_PARSE_001 fill:#fff9c4,stroke:#aa0,color:#550
  CORE_SCAN_002["CORE-SCAN-002\nblast-radius"]
  style CORE_SCAN_002 fill:#fff9c4,stroke:#aa0,color:#550
  REQ_CHECK_006 --> CORE_PARSE_001
  REQ_CHECK_006 --> CORE_SCAN_002
  REQ_EXTRACT_008 --> CORE_SCAN_002
  REQ_MAP_007 --> CORE_PARSE_001
  REQ_MAP_007 --> CORE_SCAN_002
  REQ_NEW_004 --> CORE_PARSE_001
  REQ_SCAN_005 --> CORE_PARSE_001
  REQ_SCAN_005 --> CORE_SCAN_002
```

### Risk Table

| ID | status | members | dependents | risks |
| --- | --- | --- | --- | --- |
| CORE-PARSE-001 | confirmed | 2 | 4 | blast-radius |
| CORE-SCAN-002 | confirmed | 1 | 4 | blast-radius |

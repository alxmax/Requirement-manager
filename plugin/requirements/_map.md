---
generated: 2026-06-02 14:27
nodes: 8
edges: 9
---

# Requirement Map

## System Map

```mermaid
graph TD
  subgraph Features
    REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
    REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
    REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  end
  subgraph Bus
    CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
    CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
    CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
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
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  f_scripts_reqmap_py_151_179["scripts/reqmap.py:151-179"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_151_179
  f_scripts_test_reqmap_py_90["scripts/test_reqmap.py:90"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_90
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_34_72["scripts/reqmap.py:34-72"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_34_72
  f_scripts_test_reqmap_py_34["scripts/test_reqmap.py:34"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_34
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_88_123["scripts/reqmap.py:88-123"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_88_123
  f_scripts_test_reqmap_py_104["scripts/test_reqmap.py:104"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_104
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_205_222["scripts/reqmap.py:205-222"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_205_222
  f_scripts_test_reqmap_py_80["scripts/test_reqmap.py:80"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_80
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_283_332["scripts/reqmap.py:283-332"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_283_332
  f_scripts_test_reqmap_py_188["scripts/test_reqmap.py:188"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_188
  REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_341_727["scripts/reqmap.py:341-727"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_341_727
  f_scripts_test_reqmap_py_152["scripts/test_reqmap.py:152"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_152
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_270["scripts/reqmap.py:270"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_270
  f_scripts_test_reqmap_py_210["scripts/test_reqmap.py:210"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_210
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_186["scripts/reqmap.py:186"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_186
  f_scripts_test_reqmap_py_241["scripts/test_reqmap.py:241"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_241
```

## Behavioral Flow

```mermaid
flowchart LR
  in_CORE_DRIFT_003(["A requirement body (markdown) and the lock file 'r"])
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  out_CORE_DRIFT_003(["A 12-char content hash of the binding sections; re"])
  in_CORE_DRIFT_003 --> CORE_DRIFT_003 --> out_CORE_DRIFT_003
  in_CORE_PARSE_001(["A 'requirements/' directory containing '*.md' file"])
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  out_CORE_PARSE_001(["A dict 'id -› (meta, body, path)'. 'meta' is the p"])
  in_CORE_PARSE_001 --> CORE_PARSE_001 --> out_CORE_PARSE_001
  in_CORE_SCAN_002(["A code root directory and source files in known ex"])
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  out_CORE_SCAN_002(["A dict 'cap_id -› ((role, relative_file, line_numb"])
  in_CORE_SCAN_002 --> CORE_SCAN_002 --> out_CORE_SCAN_002
  in_REQ_CHECK_006(["The loaded requirements, the discovered members, a"])
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  out_REQ_CHECK_006(["Printed 'ERROR'/'WARN' lines plus a summary; exit "])
  in_REQ_CHECK_006 --> REQ_CHECK_006 --> out_REQ_CHECK_006
  in_REQ_EXTRACT_008(["A code root and the already-discovered members (so"])
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  out_REQ_EXTRACT_008(["One 'requirements/DRAFT-*.md' per untagged file, e"])
  in_REQ_EXTRACT_008 --> REQ_EXTRACT_008 --> out_REQ_EXTRACT_008
  in_REQ_MAP_007(["The loaded requirements and the discovered members"])
  REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
  out_REQ_MAP_007(["'requirements/_map.html': multi-tab HTML viewer wi"])
  in_REQ_MAP_007 --> REQ_MAP_007 --> out_REQ_MAP_007
  in_REQ_NEW_004(["A capability id 'AREA-NAME-NNN' (CLI argument) and"])
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  out_REQ_NEW_004(["A new 'requirements/AREA-NAME-NNN.md' with the id "])
  in_REQ_NEW_004 --> REQ_NEW_004 --> out_REQ_NEW_004
  in_REQ_SCAN_005(["The loaded requirements and the discovered members"])
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  out_REQ_SCAN_005(["Printed lines: each capability id, then its 'role "])
  in_REQ_SCAN_005 --> REQ_SCAN_005 --> out_REQ_SCAN_005
```

## Dependency Map

```mermaid
graph TD
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  REQ_CHECK_006 --> CORE_PARSE_001
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  REQ_CHECK_006 --> CORE_SCAN_002
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  REQ_CHECK_006 --> CORE_DRIFT_003
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  REQ_EXTRACT_008 --> CORE_SCAN_002
  REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
  REQ_MAP_007 --> CORE_PARSE_001
  REQ_MAP_007 --> CORE_SCAN_002
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  REQ_NEW_004 --> CORE_PARSE_001
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  REQ_SCAN_005 --> CORE_PARSE_001
  REQ_SCAN_005 --> CORE_SCAN_002
```

## Risk & Unknowns

```mermaid
graph TD
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small><br>blast-radius"]
  style CORE_PARSE_001 fill:#fff9c4,stroke:#aa0,color:#550
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small><br>blast-radius"]
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
| CORE-PARSE-001 | confirmed | 4 | 4 | blast-radius |
| CORE-SCAN-002 | confirmed | 4 | 4 | blast-radius |

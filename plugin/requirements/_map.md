---
generated: 2026-06-02 17:08
nodes: 9
edges: 10
---

# Requirement Map

## System Map

_Capabilities grouped by area; thick border = bus; arrows = `depends_on`. Edges into the bus/hubs are hidden — see the Dependency Map for the full graph._

```mermaid
graph LR
  subgraph sg_CORE["CORE"]
    CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
    CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
    CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  end
  subgraph sg_REQ["REQ"]
    REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
    REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
    REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
    REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  end
  style CORE_DRIFT_003 stroke-width:3px
  style CORE_PARSE_001 stroke-width:3px
  style CORE_SCAN_002 stroke-width:3px
```

## Requirement-to-Code

_Each requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected)._

```mermaid
graph LR
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  f_scripts_reqmap_py_155_183["scripts/reqmap.py:155-183"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_155_183
  f_scripts_test_reqmap_py_91["scripts/test_reqmap.py:91"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_91
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_38_76["scripts/reqmap.py:38-76"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_38_76
  f_scripts_test_reqmap_py_35["scripts/test_reqmap.py:35"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_35
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_92_127["scripts/reqmap.py:92-127"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_92_127
  f_scripts_test_reqmap_py_122["scripts/test_reqmap.py:122"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_122
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_357_461["scripts/reqmap.py:357-461"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_357_461
  f_scripts_test_reqmap_py_319["scripts/test_reqmap.py:319"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_319
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_209_226["scripts/reqmap.py:209-226"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_209_226
  f_scripts_test_reqmap_py_81_104["scripts/test_reqmap.py:81-104"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_81_104
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_291_340["scripts/reqmap.py:291-340"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_291_340
  f_scripts_test_reqmap_py_252["scripts/test_reqmap.py:252"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_252
  REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_541_999["scripts/reqmap.py:541-999"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_541_999
  f_scripts_test_reqmap_py_170["scripts/test_reqmap.py:170"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_170
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_278["scripts/reqmap.py:278"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_278
  f_scripts_test_reqmap_py_274["scripts/test_reqmap.py:274"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_274
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_190["scripts/reqmap.py:190"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_190
  f_scripts_test_reqmap_py_305["scripts/test_reqmap.py:305"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_305
```

## Behavioral Flow

_`Input → Requirement → Output` for each capability — the data thread._

```mermaid
flowchart LR
  in_CORE_DRIFT_003["A requirement body (markdown) and the lock file 'r"]
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  out_CORE_DRIFT_003["A 12-char content hash of the binding sections; re"]
  in_CORE_DRIFT_003 --> CORE_DRIFT_003 --> out_CORE_DRIFT_003
  in_CORE_PARSE_001["A 'requirements/' directory containing '*.md' file"]
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  out_CORE_PARSE_001["A dict 'id -› (meta, body, path)'. 'meta' is the p"]
  in_CORE_PARSE_001 --> CORE_PARSE_001 --> out_CORE_PARSE_001
  in_CORE_SCAN_002["A code root directory and source files in known ex"]
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  out_CORE_SCAN_002["A dict 'cap_id -› ((role, relative_file, line_numb"]
  in_CORE_SCAN_002 --> CORE_SCAN_002 --> out_CORE_SCAN_002
  in_REQ_CANDIDATES_009["A code root, walked with the same exclusions as sc"]
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  out_REQ_CANDIDATES_009["A single JSON object on stdout (or '--out PATH'): "]
  in_REQ_CANDIDATES_009 --> REQ_CANDIDATES_009 --> out_REQ_CANDIDATES_009
  in_REQ_CHECK_006["The loaded requirements, the discovered members, a"]
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  out_REQ_CHECK_006["Printed 'ERROR'/'WARN' lines plus a summary; exit "]
  in_REQ_CHECK_006 --> REQ_CHECK_006 --> out_REQ_CHECK_006
  in_REQ_EXTRACT_008["A code root and the already-discovered members (so"]
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  out_REQ_EXTRACT_008["One 'requirements/DRAFT-*.md' per untagged file, e"]
  in_REQ_EXTRACT_008 --> REQ_EXTRACT_008 --> out_REQ_EXTRACT_008
  in_REQ_MAP_007["The loaded requirements and the discovered members"]
  REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
  out_REQ_MAP_007["'requirements/_map.html': multi-tab HTML viewer wi"]
  in_REQ_MAP_007 --> REQ_MAP_007 --> out_REQ_MAP_007
  in_REQ_NEW_004["A capability id 'AREA-NAME-NNN' (CLI argument) and"]
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  out_REQ_NEW_004["A new 'requirements/AREA-NAME-NNN.md' with the id "]
  in_REQ_NEW_004 --> REQ_NEW_004 --> out_REQ_NEW_004
  in_REQ_SCAN_005["The loaded requirements and the discovered members"]
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  out_REQ_SCAN_005["Printed lines: each capability id, then its 'role "]
  in_REQ_SCAN_005 --> REQ_SCAN_005 --> out_REQ_SCAN_005
```

## Dependency Map

_Full `depends_on` topology, including the bus edges the System Map hides._

```mermaid
graph LR
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  REQ_CANDIDATES_009 --> CORE_SCAN_002
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  REQ_CHECK_006 --> CORE_PARSE_001
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

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = blast-radius (≥3 dependents)._

```mermaid
graph TD
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small><br>blast-radius"]
  style CORE_PARSE_001 fill:#fff9c4,stroke:#aa0,color:#550
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small><br>blast-radius"]
  style CORE_SCAN_002 fill:#fff9c4,stroke:#aa0,color:#550
  REQ_CANDIDATES_009 --> CORE_SCAN_002
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
| CORE-SCAN-002 | confirmed | 4 | 5 | blast-radius |

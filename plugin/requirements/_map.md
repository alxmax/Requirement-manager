---
generated: 2026-06-02 18:37
nodes: 9
edges: 10
---

# Requirement Map

## System Map

_Capabilities grouped by area; thick border = bus; arrows = `depends_on`. Edges into the bus/hubs are hidden (the Dependency Map shows area-level coupling)._

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
  f_scripts_reqmap_py_172_200["scripts/reqmap.py:172-200"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_172_200
  f_scripts_test_reqmap_py_91["scripts/test_reqmap.py:91"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_91
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_53_91["scripts/reqmap.py:53-91"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_53_91
  f_scripts_test_reqmap_py_35["scripts/test_reqmap.py:35"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_35
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_107_144["scripts/reqmap.py:107-144"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_107_144
  f_scripts_test_reqmap_py_122["scripts/test_reqmap.py:122"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_122
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_421_525["scripts/reqmap.py:421-525"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_421_525
  f_scripts_test_reqmap_py_374["scripts/test_reqmap.py:374"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_374
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_226_243["scripts/reqmap.py:226-243"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_226_243
  f_scripts_test_reqmap_py_81_104["scripts/test_reqmap.py:81-104"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_81_104
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_355_404["scripts/reqmap.py:355-404"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_355_404
  f_scripts_test_reqmap_py_295["scripts/test_reqmap.py:295"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_295
  REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_605_1138["scripts/reqmap.py:605-1138"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_605_1138
  f_scripts_test_reqmap_py_170["scripts/test_reqmap.py:170"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_170
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_334["scripts/reqmap.py:334"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_334
  f_scripts_test_reqmap_py_317["scripts/test_reqmap.py:317"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_317
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_207["scripts/reqmap.py:207"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_207
  f_scripts_test_reqmap_py_360["scripts/test_reqmap.py:360"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_360
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
  in_REQ_NEW_004["A capability id 'AREA-NAME-NNN' (CLI argument). Th"]
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  out_REQ_NEW_004["A new 'requirements/AREA-NAME-NNN.md' with the id "]
  in_REQ_NEW_004 --> REQ_NEW_004 --> out_REQ_NEW_004
  in_REQ_SCAN_005["The loaded requirements and the discovered members"]
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  out_REQ_SCAN_005["Printed lines: each capability id, then its 'role "]
  in_REQ_SCAN_005 --> REQ_SCAN_005 --> out_REQ_SCAN_005
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>6 caps</small>"]
  a_REQ --> a_CORE
  style a_CORE stroke-width:3px
```

## Risk & Unknowns

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = blast-radius (≥3 dependents)._

```mermaid
graph LR
  subgraph sg_CORE["CORE"]
    CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small><br>blast-radius"]
    CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small><br>blast-radius"]
  end
  style CORE_PARSE_001 fill:#fff9c4,stroke:#aa0,color:#550
  style CORE_SCAN_002 fill:#fff9c4,stroke:#aa0,color:#550
```

### Risk Table

| ID | status | members | dependents | risks | recommendation |
| --- | --- | --- | --- | --- | --- |
| CORE-PARSE-001 | confirmed | 4 | 4 | blast-radius | High fan-in — many capabilities depend on this. Change it only behind its contract, run the full gate + dependents' tests, and treat it as shared foundation (bus). |
| CORE-SCAN-002 | confirmed | 4 | 5 | blast-radius | High fan-in — many capabilities depend on this. Change it only behind its contract, run the full gate + dependents' tests, and treat it as shared foundation (bus). |

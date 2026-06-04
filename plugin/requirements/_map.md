---
generated: 2026-06-04 20:03
nodes: 13
edges: 16
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
    REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
    REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
    REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
    REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  end
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_MAP_007
  REQ_NEXT_013 --> REQ_MAP_007
  style CORE_DRIFT_003 stroke-width:3px
  style CORE_PARSE_001 stroke-width:3px
  style CORE_SCAN_002 stroke-width:3px
```

## Requirement-to-Code

_Each requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected)._

```mermaid
graph LR
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  f_scripts_reqmap_py_210_241["scripts/reqmap.py:210-241"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_210_241
  f_scripts_test_reqmap_py_103_116["scripts/test_reqmap.py:103-116"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_103_116
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_74_129["scripts/reqmap.py:74-129"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_74_129
  f_scripts_test_reqmap_py_47_796["scripts/test_reqmap.py:47-796"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_796
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_145_182["scripts/reqmap.py:145-182"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_145_182
  f_scripts_test_reqmap_py_146["scripts/test_reqmap.py:146"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_146
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_659_806["scripts/reqmap.py:659-806"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_659_806
  f_scripts_test_reqmap_py_487_904["scripts/test_reqmap.py:487-904"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_487_904
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_248_297["scripts/reqmap.py:248-297"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_248_297
  f_scripts_test_reqmap_py_93_954["scripts/test_reqmap.py:93-954"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_93_954
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_496_642["scripts/reqmap.py:496-642"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_496_642
  f_scripts_test_reqmap_py_194_395["scripts/test_reqmap.py:194-395"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_194_395
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_912_999["scripts/reqmap.py:912-999"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_912_999
  f_scripts_test_reqmap_py_560_887["scripts/test_reqmap.py:560-887"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_560_887
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_1238_1267["scripts/reqmap.py:1238-1267"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_1238_1267
  f_scripts_test_reqmap_py_1241["scripts/test_reqmap.py:1241"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1241
  REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1034_1738["scripts/reqmap.py:1034-1738"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1034_1738
  f_scripts_test_reqmap_py_237_1045["scripts/test_reqmap.py:237-1045"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_237_1045
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_426["scripts/reqmap.py:426"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_426
  f_scripts_test_reqmap_py_429["scripts/test_reqmap.py:429"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_429
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1111_1121["scripts/reqmap.py:1111-1121"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1111_1121
  f_scripts_test_reqmap_py_1150["scripts/test_reqmap.py:1150"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1150
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_447_462["scripts/reqmap.py:447-462"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_447_462
  f_scripts_test_reqmap_py_1090["scripts/test_reqmap.py:1090"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1090
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_261["scripts/reqmap.py:261"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_261
  f_scripts_test_reqmap_py_473["scripts/test_reqmap.py:473"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_473
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>10 caps</small>"]
  a_REQ --> a_CORE
  style a_CORE stroke-width:3px
```

## Risk & Unknowns

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = blast-radius (≥3 dependents), untested (implemented but no tested-by — set `test_exempt` to silence), or unverified-intent (open verify-intent question)._

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
| CORE-PARSE-001 | confirmed | 6 | 6 | blast-radius | High fan-in — many capabilities depend on this. Change it only behind its contract, run the full gate + dependents' tests, and treat it as shared foundation (bus). |
| CORE-SCAN-002 | confirmed | 4 | 5 | blast-radius | High fan-in — many capabilities depend on this. Change it only behind its contract, run the full gate + dependents' tests, and treat it as shared foundation (bus). |

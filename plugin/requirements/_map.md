---
generated: 2026-06-03 21:51
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
    REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
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
  f_scripts_reqmap_py_209_240["scripts/reqmap.py:209-240"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_209_240
  f_scripts_test_reqmap_py_103_116["scripts/test_reqmap.py:103-116"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_103_116
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_73_128["scripts/reqmap.py:73-128"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_73_128
  f_scripts_test_reqmap_py_47_800["scripts/test_reqmap.py:47-800"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_800
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_144_181["scripts/reqmap.py:144-181"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_144_181
  f_scripts_test_reqmap_py_146["scripts/test_reqmap.py:146"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_146
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_658_805["scripts/reqmap.py:658-805"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_658_805
  f_scripts_test_reqmap_py_521_908["scripts/test_reqmap.py:521-908"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_521_908
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_247_296["scripts/reqmap.py:247-296"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_247_296
  f_scripts_test_reqmap_py_93_958["scripts/test_reqmap.py:93-958"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_93_958
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_495_641["scripts/reqmap.py:495-641"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_495_641
  f_scripts_test_reqmap_py_194_429["scripts/test_reqmap.py:194-429"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_194_429
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_911_998["scripts/reqmap.py:911-998"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_911_998
  f_scripts_test_reqmap_py_594_891["scripts/test_reqmap.py:594-891"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_594_891
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_1210_1237["scripts/reqmap.py:1210-1237"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_1210_1237
  f_scripts_test_reqmap_py_1265["scripts/test_reqmap.py:1265"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1265
  REQ_MAP_007["Requirement map (HTML + MD)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1033_1948["scripts/reqmap.py:1033-1948"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1033_1948
  f_scripts_test_reqmap_py_237_1069["scripts/test_reqmap.py:237-1069"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_237_1069
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_425["scripts/reqmap.py:425"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_425
  f_scripts_test_reqmap_py_463["scripts/test_reqmap.py:463"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_463
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1083_1093["scripts/reqmap.py:1083-1093"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1083_1093
  f_scripts_test_reqmap_py_1174["scripts/test_reqmap.py:1174"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1174
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_446_461["scripts/reqmap.py:446-461"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_446_461
  f_scripts_test_reqmap_py_1114["scripts/test_reqmap.py:1114"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1114
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_260["scripts/reqmap.py:260"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_260
  f_scripts_test_reqmap_py_507["scripts/test_reqmap.py:507"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_507
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

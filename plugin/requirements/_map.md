---
generated: 2026-06-09 00:02
nodes: 18
edges: 24
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
    REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
    REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
    REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
    REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
    REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
    REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
    REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
    REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  end
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_MAP_007
  REQ_NEXT_013 --> REQ_MAP_007
  REQ_TESTLINK_018 --> REQ_CHECK_006
  style CORE_DRIFT_003 stroke-width:3px
  style CORE_PARSE_001 stroke-width:3px
  style CORE_SCAN_002 stroke-width:3px
```

## Requirement-to-Code

_Each requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected)._

```mermaid
graph LR
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  f_scripts_reqmap_py_223_257["scripts/reqmap.py:223-257"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_223_257
  f_scripts_test_reqmap_py_103_119["scripts/test_reqmap.py:103-119"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_103_119
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_78_133["scripts/reqmap.py:78-133"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_78_133
  f_scripts_test_reqmap_py_47_906["scripts/test_reqmap.py:47-906"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_906
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_149_186["scripts/reqmap.py:149-186"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_149_186
  f_scripts_test_reqmap_py_194["scripts/test_reqmap.py:194"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_194
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_739_886["scripts/reqmap.py:739-886"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_739_886
  f_scripts_test_reqmap_py_535_1031["scripts/test_reqmap.py:535-1031"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_535_1031
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_264_347["scripts/reqmap.py:264-347"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_264_347
  f_scripts_test_reqmap_py_93_1081["scripts/test_reqmap.py:93-1081"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_93_1081
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_576_722["scripts/reqmap.py:576-722"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_576_722
  f_scripts_test_reqmap_py_242_443["scripts/test_reqmap.py:242-443"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_242_443
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_992_1079["scripts/reqmap.py:992-1079"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_992_1079
  f_scripts_test_reqmap_py_608_1014["scripts/test_reqmap.py:608-1014"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_608_1014
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_1662["scripts/reqmap.py:1662"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_1662
  f_scripts_test_reqmap_py_1845["scripts/test_reqmap.py:1845"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_1845
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_1774_1803["scripts/reqmap.py:1774-1803"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_1774_1803
  f_scripts_test_reqmap_py_1417["scripts/test_reqmap.py:1417"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1417
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1344_1460["scripts/reqmap.py:1344-1460"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1344_1460
  f_scripts_test_reqmap_py_1603["scripts/test_reqmap.py:1603"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1603
  REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1114_2358["scripts/reqmap.py:1114-2358"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1114_2358
  f_scripts_test_reqmap_py_285_1186["scripts/test_reqmap.py:285-1186"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_285_1186
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_506["scripts/reqmap.py:506"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_506
  f_scripts_test_reqmap_py_477["scripts/test_reqmap.py:477"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_477
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1237_1250["scripts/reqmap.py:1237-1250"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1237_1250
  f_scripts_test_reqmap_py_1291_1410["scripts/test_reqmap.py:1291-1410"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1291_1410
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_527_542["scripts/reqmap.py:527-542"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_527_542
  f_scripts_test_reqmap_py_1231["scripts/test_reqmap.py:1231"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1231
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_277["scripts/reqmap.py:277"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_277
  f_scripts_test_reqmap_py_521["scripts/test_reqmap.py:521"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_521
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_1491["scripts/reqmap.py:1491"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_1491
  f_scripts_test_reqmap_py_1719["scripts/test_reqmap.py:1719"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_1719
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_1564_1625["scripts/reqmap.py:1564-1625"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_1564_1625
  f_scripts_test_reqmap_py_1783["scripts/test_reqmap.py:1783"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_1783
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_327_374["scripts/reqmap.py:327-374"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_327_374
  f_scripts_test_reqmap_py_1899["scripts/test_reqmap.py:1899"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_1899
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>15 caps</small>"]
  a_REQ --> a_CORE
  style a_CORE stroke-width:3px
```

## Risk & Unknowns

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = untested (implemented but no tested-by — set `test_exempt` to silence), or unverified-intent (open verify-intent question)._

```mermaid
graph LR
  ok["No risk signals detected"]
```

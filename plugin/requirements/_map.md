---
generated: 2026-06-09 00:24
nodes: 19
edges: 26
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
    REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
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
  REQ_ACVERIFY_019 --> REQ_CHECK_006
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
  f_scripts_reqmap_py_275_309["scripts/reqmap.py:275-309"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_275_309
  f_scripts_test_reqmap_py_103_119["scripts/test_reqmap.py:103-119"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_103_119
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_83_138["scripts/reqmap.py:83-138"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_83_138
  f_scripts_test_reqmap_py_47_906["scripts/test_reqmap.py:47-906"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_906
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_154_191["scripts/reqmap.py:154-191"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_154_191
  f_scripts_test_reqmap_py_194["scripts/test_reqmap.py:194"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_194
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_218_435["scripts/reqmap.py:218-435"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_218_435
  f_scripts_test_reqmap_py_1981["scripts/test_reqmap.py:1981"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_1981
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_803_950["scripts/reqmap.py:803-950"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_803_950
  f_scripts_test_reqmap_py_535_1031["scripts/test_reqmap.py:535-1031"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_535_1031
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_316_399["scripts/reqmap.py:316-399"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_316_399
  f_scripts_test_reqmap_py_93_1081["scripts/test_reqmap.py:93-1081"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_93_1081
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_640_786["scripts/reqmap.py:640-786"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_640_786
  f_scripts_test_reqmap_py_242_443["scripts/test_reqmap.py:242-443"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_242_443
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_1056_1143["scripts/reqmap.py:1056-1143"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_1056_1143
  f_scripts_test_reqmap_py_608_1014["scripts/test_reqmap.py:608-1014"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_608_1014
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_1752["scripts/reqmap.py:1752"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_1752
  f_scripts_test_reqmap_py_1863["scripts/test_reqmap.py:1863"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_1863
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_1864_1893["scripts/reqmap.py:1864-1893"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_1864_1893
  f_scripts_test_reqmap_py_1417["scripts/test_reqmap.py:1417"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1417
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1420_1550["scripts/reqmap.py:1420-1550"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1420_1550
  f_scripts_test_reqmap_py_1603["scripts/test_reqmap.py:1603"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1603
  REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1178_2448["scripts/reqmap.py:1178-2448"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1178_2448
  f_scripts_test_reqmap_py_285_1186["scripts/test_reqmap.py:285-1186"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_285_1186
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_570["scripts/reqmap.py:570"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_570
  f_scripts_test_reqmap_py_477["scripts/test_reqmap.py:477"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_477
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1301_1314["scripts/reqmap.py:1301-1314"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1301_1314
  f_scripts_test_reqmap_py_1291_1410["scripts/test_reqmap.py:1291-1410"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1291_1410
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_591_606["scripts/reqmap.py:591-606"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_591_606
  f_scripts_test_reqmap_py_1231["scripts/test_reqmap.py:1231"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1231
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_329["scripts/reqmap.py:329"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_329
  f_scripts_test_reqmap_py_521["scripts/test_reqmap.py:521"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_521
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_1581["scripts/reqmap.py:1581"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_1581
  f_scripts_test_reqmap_py_1737["scripts/test_reqmap.py:1737"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_1737
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_1654_1715["scripts/reqmap.py:1654-1715"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_1654_1715
  f_scripts_test_reqmap_py_1801["scripts/test_reqmap.py:1801"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_1801
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_379_427["scripts/reqmap.py:379-427"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_379_427
  f_scripts_test_reqmap_py_1917["scripts/test_reqmap.py:1917"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_1917
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>16 caps</small>"]
  a_REQ --> a_CORE
  style a_CORE stroke-width:3px
```

## Risk & Unknowns

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = untested (implemented but no tested-by — set `test_exempt` to silence), or unverified-intent (open verify-intent question)._

```mermaid
graph LR
  ok["No risk signals detected"]
```

---
generated: 2026-06-10 23:07
nodes: 28
edges: 37
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
    REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
    REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
    REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
    REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
    REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
    REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
    REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
    REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
    REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
    REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
    REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
    REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
    REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  end
  subgraph sg_misc["misc"]
    NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  end
  REQ_ACVERIFY_019 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_MAP_007
  REQ_LINTCHECKS_025 --> REQ_LINT_014
  REQ_NEXT_013 --> REQ_MAP_007
  REQ_PAGES_021 --> REQ_MAP_007
  REQ_PROMOTE_TODO_001 --> REQ_NEW_004
  REQ_PROSE_024 --> REQ_EXTRACT_008
  REQ_TESTLINK_018 --> REQ_CHECK_006
  REQ_TRACE_020 --> REQ_CHECK_006
  REQ_VIEWER_007 --> REQ_MAP_007
  style CORE_DRIFT_003 stroke-width:3px
  style CORE_PARSE_001 stroke-width:3px
  style CORE_SCAN_002 stroke-width:3px
```

## Requirement-to-Code

_Each requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected)._

```mermaid
graph LR
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  f_scripts_reqmap_py_352_386["scripts/reqmap.py:352-386"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_352_386
  f_scripts_test_reqmap_py_132_170["scripts/test_reqmap.py:132-170"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_132_170
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_84_139["scripts/reqmap.py:84-139"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_84_139
  f_scripts_test_reqmap_py_47_1019["scripts/test_reqmap.py:47-1019"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_1019
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_155_234["scripts/reqmap.py:155-234"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_155_234
  f_scripts_test_reqmap_py_247["scripts/test_reqmap.py:247"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_247
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_281_534["scripts/reqmap.py:281-534"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_281_534
  f_scripts_test_reqmap_py_2219["scripts/test_reqmap.py:2219"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2219
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_988_1135["scripts/reqmap.py:988-1135"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_988_1135
  f_scripts_test_reqmap_py_630_1144["scripts/test_reqmap.py:630-1144"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_630_1144
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_339_478["scripts/reqmap.py:339-478"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_339_478
  f_scripts_test_reqmap_py_122_2386["scripts/test_reqmap.py:122-2386"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_122_2386
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_825_971["scripts/reqmap.py:825-971"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_825_971
  f_scripts_test_reqmap_py_523_538["scripts/test_reqmap.py:523-538"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_523_538
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_1241_1328["scripts/reqmap.py:1241-1328"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_1241_1328
  f_scripts_test_reqmap_py_703_1127["scripts/test_reqmap.py:703-1127"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_703_1127
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_1998["scripts/reqmap.py:1998"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_1998
  f_scripts_test_reqmap_py_2079["scripts/test_reqmap.py:2079"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2079
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_2119_2148["scripts/reqmap.py:2119-2148"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_2119_2148
  f_scripts_test_reqmap_py_1607["scripts/test_reqmap.py:1607"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1607
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1621_1787["scripts/reqmap.py:1621-1787"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1621_1787
  f_scripts_test_reqmap_py_1793["scripts/test_reqmap.py:1793"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1793
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_1650_1679["scripts/reqmap.py:1650-1679"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_1650_1679
  f_scripts_test_reqmap_py_1793["scripts/test_reqmap.py:1793"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_1793
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1363_2677["scripts/reqmap.py:1363-2677"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1363_2677
  f_scripts_test_reqmap_py_380_1317["scripts/test_reqmap.py:380-1317"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_380_1317
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_679["scripts/reqmap.py:679"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_679
  f_scripts_test_reqmap_py_572["scripts/test_reqmap.py:572"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_572
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1496_1509["scripts/reqmap.py:1496-1509"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1496_1509
  f_scripts_test_reqmap_py_1481_1600["scripts/test_reqmap.py:1481-1600"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1481_1600
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_1469_2693["scripts/reqmap.py:1469-2693"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_1469_2693
  f_scripts_test_reqmap_py_880_1318["scripts/test_reqmap.py:880-1318"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_880_1318
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_776_791["scripts/reqmap.py:776-791"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_776_791
  f_scripts_test_reqmap_py_1421["scripts/test_reqmap.py:1421"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1421
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_700_746["scripts/reqmap.py:700-746"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_700_746
  f_scripts_test_reqmap_py_2412["scripts/test_reqmap.py:2412"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2412
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_833_886["scripts/reqmap.py:833-886"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_833_886
  f_scripts_test_reqmap_py_337_523["scripts/test_reqmap.py:337-523"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_337_523
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_2746["scripts/reqmap.py:2746"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_2746
  f_scripts_test_reqmap_py_2454["scripts/test_reqmap.py:2454"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_2454
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_408["scripts/reqmap.py:408"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_408
  f_scripts_test_reqmap_py_616["scripts/test_reqmap.py:616"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_616
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_211_225["scripts/reqmap.py:211-225"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_211_225
  f_scripts_test_reqmap_py_2506["scripts/test_reqmap.py:2506"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_2506
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_1818["scripts/reqmap.py:1818"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_1818
  f_scripts_test_reqmap_py_1953["scripts/test_reqmap.py:1953"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_1953
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_1900_1961["scripts/reqmap.py:1900-1961"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_1900_1961
  f_scripts_test_reqmap_py_2017["scripts/test_reqmap.py:2017"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2017
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_458_526["scripts/reqmap.py:458-526"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_458_526
  f_scripts_test_reqmap_py_2155["scripts/test_reqmap.py:2155"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2155
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_510_1853["scripts/reqmap.py:510-1853"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_510_1853
  f_scripts_test_reqmap_py_2289["scripts/test_reqmap.py:2289"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2289
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_2717_2730["scripts/reqmap.py:2717-2730"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_2717_2730
  f_scripts_test_reqmap_py_853["scripts/test_reqmap.py:853"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_853
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>24 caps</small>"]
  a_misc["misc<br><small>1 caps</small>"]
  a_REQ --> a_CORE
  style a_CORE stroke-width:3px
```

## Risk & Unknowns

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = untested (implemented but no tested-by — set `test_exempt` to silence), or unverified-intent (open verify-intent question)._

```mermaid
graph LR
  ok["No risk signals detected"]
```

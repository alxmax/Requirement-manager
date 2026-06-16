---
generated: 2026-06-16 21:43
nodes: 29
edges: 40
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
    REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
    REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
    REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
    REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
    REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
    REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
    REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
    REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
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
  REQ_SITE_026 --> REQ_MAP_007
  REQ_SITE_026 --> REQ_VIEWER_007
  REQ_SITE_026 --> REQ_PAGES_021
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
  f_scripts_reqmap_py_495_529["scripts/reqmap.py:495-529"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_495_529
  f_scripts_test_reqmap_py_151_189["scripts/test_reqmap.py:151-189"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_151_189
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_93_150["scripts/reqmap.py:93-150"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_93_150
  f_scripts_test_reqmap_py_48_1038["scripts/test_reqmap.py:48-1038"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_48_1038
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_166_356["scripts/reqmap.py:166-356"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_166_356
  f_scripts_test_reqmap_py_266["scripts/test_reqmap.py:266"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_266
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_424_705["scripts/reqmap.py:424-705"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_424_705
  f_scripts_test_reqmap_py_2238["scripts/test_reqmap.py:2238"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2238
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_1190_1337["scripts/reqmap.py:1190-1337"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_1190_1337
  f_scripts_test_reqmap_py_649_1163["scripts/test_reqmap.py:649-1163"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_649_1163
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_482_782["scripts/reqmap.py:482-782"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_482_782
  f_scripts_test_reqmap_py_141_3226["scripts/test_reqmap.py:141-3226"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_141_3226
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_1027_1173["scripts/reqmap.py:1027-1173"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1027_1173
  f_scripts_test_reqmap_py_542_557["scripts/test_reqmap.py:542-557"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_542_557
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_1443_1530["scripts/reqmap.py:1443-1530"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_1443_1530
  f_scripts_test_reqmap_py_722_1146["scripts/test_reqmap.py:722-1146"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_722_1146
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_2212["scripts/reqmap.py:2212"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_2212
  f_scripts_test_reqmap_py_2098["scripts/test_reqmap.py:2098"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2098
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_2333_2362["scripts/reqmap.py:2333-2362"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_2333_2362
  f_scripts_test_reqmap_py_1626["scripts/test_reqmap.py:1626"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1626
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1835_2001["scripts/reqmap.py:1835-2001"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1835_2001
  f_scripts_test_reqmap_py_1812["scripts/test_reqmap.py:1812"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1812
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_1864_1893["scripts/reqmap.py:1864-1893"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_1864_1893
  f_scripts_test_reqmap_py_1812["scripts/test_reqmap.py:1812"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_1812
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1565_3327["scripts/reqmap.py:1565-3327"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1565_3327
  f_scripts_test_reqmap_py_399_1336["scripts/test_reqmap.py:399-1336"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_399_1336
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_881["scripts/reqmap.py:881"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_881
  f_scripts_test_reqmap_py_591["scripts/test_reqmap.py:591"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_591
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_403_1711["scripts/reqmap.py:403-1711"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_403_1711
  f_scripts_test_reqmap_py_1500_1619["scripts/test_reqmap.py:1500-1619"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1500_1619
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_1671_3343["scripts/reqmap.py:1671-3343"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_1671_3343
  f_scripts_test_reqmap_py_899_1337["scripts/test_reqmap.py:899-1337"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_899_1337
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_978_993["scripts/reqmap.py:978-993"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_978_993
  f_scripts_test_reqmap_py_1440["scripts/test_reqmap.py:1440"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1440
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_902_948["scripts/reqmap.py:902-948"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_902_948
  f_scripts_test_reqmap_py_2431["scripts/test_reqmap.py:2431"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2431
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1035_1088["scripts/reqmap.py:1035-1088"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1035_1088
  f_scripts_test_reqmap_py_356_542["scripts/test_reqmap.py:356-542"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_356_542
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_3483["scripts/reqmap.py:3483"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_3483
  f_scripts_test_reqmap_py_2473["scripts/test_reqmap.py:2473"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_2473
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_551["scripts/reqmap.py:551"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_551
  f_scripts_test_reqmap_py_635["scripts/test_reqmap.py:635"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_635
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_333_347["scripts/reqmap.py:333-347"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_333_347
  f_scripts_test_reqmap_py_2525["scripts/test_reqmap.py:2525"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_2525
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_2032["scripts/reqmap.py:2032"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_2032
  f_scripts_test_reqmap_py_1972["scripts/test_reqmap.py:1972"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_1972
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_2114_2175["scripts/reqmap.py:2114-2175"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_2114_2175
  f_scripts_test_reqmap_py_2036["scripts/test_reqmap.py:2036"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2036
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_2388_3683["scripts/reqmap.py:2388-3683"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_2388_3683
  f_scripts_test_reqmap_py_3001["scripts/test_reqmap.py:3001"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_3001
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_601_697["scripts/reqmap.py:601-697"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_601_697
  f_scripts_test_reqmap_py_2174["scripts/test_reqmap.py:2174"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2174
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_673_2067["scripts/reqmap.py:673-2067"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_673_2067
  f_scripts_test_reqmap_py_2308["scripts/test_reqmap.py:2308"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2308
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_3454_3467["scripts/reqmap.py:3454-3467"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_3454_3467
  f_scripts_test_reqmap_py_872["scripts/test_reqmap.py:872"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_872
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>25 caps</small>"]
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

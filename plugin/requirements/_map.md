---
generated: 2026-06-21 00:27
nodes: 35
edges: 49
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
    REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
    REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
    REQ_EXCALIDRAW_030["Excalidraw scene builder — core API<br><small>REQ-EXCALIDRAW-030</small>"]
    REQ_EXCALIDRAW_031["Excalidraw quality gates<br><small>REQ-EXCALIDRAW-031</small>"]
    REQ_EXCALIDRAW_032["Excalidraw builder CLI verbs<br><small>REQ-EXCALIDRAW-032</small>"]
    REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
    REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
    REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
    REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
    REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
    REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
    REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
    REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
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
  REQ_COVERAGE_029 --> REQ_NEXT_013
  REQ_DOCBUNDLE_026 --> REQ_CHECK_006
  REQ_EXCALIDRAW_031 --> REQ_EXCALIDRAW_030
  REQ_EXCALIDRAW_032 --> REQ_EXCALIDRAW_030
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_MAP_007
  REQ_LINTCHECKS_025 --> REQ_LINT_014
  REQ_MEMBERDRIFT_027 --> REQ_CHECK_006
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
  f_scripts_reqmap_py_550_584["scripts/reqmap.py:550-584"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_550_584
  f_scripts_test_reqmap_py_151_189["scripts/test_reqmap.py:151-189"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_151_189
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_114_171["scripts/reqmap.py:114-171"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_114_171
  f_scripts_test_reqmap_py_48_1201["scripts/test_reqmap.py:48-1201"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_48_1201
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_187_377["scripts/reqmap.py:187-377"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_187_377
  f_scripts_test_reqmap_py_266["scripts/test_reqmap.py:266"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_266
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_479_848["scripts/reqmap.py:479-848"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_479_848
  f_scripts_test_reqmap_py_2426["scripts/test_reqmap.py:2426"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2426
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_1348_1495["scripts/reqmap.py:1348-1495"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_1348_1495
  f_scripts_test_reqmap_py_812_1326["scripts/test_reqmap.py:812-1326"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_812_1326
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_537_939["scripts/reqmap.py:537-939"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_537_939
  f_scripts_test_reqmap_py_141_3414["scripts/test_reqmap.py:141-3414"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_141_3414
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_2496["scripts/reqmap.py:2496"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_2496
  f_scripts_test_reqmap_py_2303["scripts/test_reqmap.py:2303"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2303
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_427["scripts/reqmap.py:427"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_427
  f_scripts_test_reqmap_py_377["scripts/test_reqmap.py:377"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_377
  REQ_EXCALIDRAW_030["Excalidraw scene builder — core API<br><small>REQ-EXCALIDRAW-030</small>"]
  f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_2["skills/excalidraw-diagram/scripts/excalidraw_builder.py:2"]
  REQ_EXCALIDRAW_030 -->|implements| f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_2
  f_skills_excalidraw_diagram_scripts_test_excalidraw_py_2["skills/excalidraw-diagram/scripts/test_excalidraw.py:2"]
  REQ_EXCALIDRAW_030 -->|tested-by| f_skills_excalidraw_diagram_scripts_test_excalidraw_py_2
  REQ_EXCALIDRAW_031["Excalidraw quality gates<br><small>REQ-EXCALIDRAW-031</small>"]
  f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_3["skills/excalidraw-diagram/scripts/excalidraw_builder.py:3"]
  REQ_EXCALIDRAW_031 -->|implements| f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_3
  f_skills_excalidraw_diagram_scripts_test_excalidraw_py_3["skills/excalidraw-diagram/scripts/test_excalidraw.py:3"]
  REQ_EXCALIDRAW_031 -->|tested-by| f_skills_excalidraw_diagram_scripts_test_excalidraw_py_3
  REQ_EXCALIDRAW_032["Excalidraw builder CLI verbs<br><small>REQ-EXCALIDRAW-032</small>"]
  f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_4["skills/excalidraw-diagram/scripts/excalidraw_builder.py:4"]
  REQ_EXCALIDRAW_032 -->|implements| f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_4
  f_skills_excalidraw_diagram_scripts_test_excalidraw_py_4["skills/excalidraw-diagram/scripts/test_excalidraw.py:4"]
  REQ_EXCALIDRAW_032 -->|tested-by| f_skills_excalidraw_diagram_scripts_test_excalidraw_py_4
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_1185_1331["scripts/reqmap.py:1185-1331"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1185_1331
  f_scripts_test_reqmap_py_705_720["scripts/test_reqmap.py:705-720"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_705_720
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_1601_1688["scripts/reqmap.py:1601-1688"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_1601_1688
  f_scripts_test_reqmap_py_885_1309["scripts/test_reqmap.py:885-1309"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_885_1309
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_2445["scripts/reqmap.py:2445"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_2445
  f_scripts_test_reqmap_py_2261["scripts/test_reqmap.py:2261"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2261
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_2582_2611["scripts/reqmap.py:2582-2611"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_2582_2611
  f_scripts_test_reqmap_py_1789["scripts/test_reqmap.py:1789"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1789
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1993_2164["scripts/reqmap.py:1993-2164"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1993_2164
  f_scripts_test_reqmap_py_1975["scripts/test_reqmap.py:1975"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1975
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2022_2051["scripts/reqmap.py:2022-2051"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2022_2051
  f_scripts_test_reqmap_py_1975["scripts/test_reqmap.py:1975"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_1975
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1723_3576["scripts/reqmap.py:1723-3576"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1723_3576
  f_scripts_test_reqmap_py_562_1499["scripts/test_reqmap.py:562-1499"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_562_1499
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_600_653["scripts/reqmap.py:600-653"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_600_653
  f_scripts_test_reqmap_py_432["scripts/test_reqmap.py:432"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_432
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1039["scripts/reqmap.py:1039"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1039
  f_scripts_test_reqmap_py_754["scripts/test_reqmap.py:754"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_754
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_458_1869["scripts/reqmap.py:458-1869"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_458_1869
  f_scripts_test_reqmap_py_1663_1782["scripts/test_reqmap.py:1663-1782"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1663_1782
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_1829_3592["scripts/reqmap.py:1829-3592"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_1829_3592
  f_scripts_test_reqmap_py_1062_1500["scripts/test_reqmap.py:1062-1500"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1062_1500
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1136_1151["scripts/reqmap.py:1136-1151"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1136_1151
  f_scripts_test_reqmap_py_1603["scripts/test_reqmap.py:1603"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1603
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1060_1106["scripts/reqmap.py:1060-1106"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1060_1106
  f_scripts_test_reqmap_py_2619["scripts/test_reqmap.py:2619"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2619
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1193_1246["scripts/reqmap.py:1193-1246"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1193_1246
  f_scripts_test_reqmap_py_519_705["scripts/test_reqmap.py:519-705"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_519_705
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_3741["scripts/reqmap.py:3741"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_3741
  f_scripts_test_reqmap_py_2661["scripts/test_reqmap.py:2661"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_2661
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_690["scripts/reqmap.py:690"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_690
  f_scripts_test_reqmap_py_798["scripts/test_reqmap.py:798"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_798
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_354_368["scripts/reqmap.py:354-368"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_354_368
  f_scripts_test_reqmap_py_2713["scripts/test_reqmap.py:2713"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_2713
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_2206["scripts/reqmap.py:2206"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_2206
  f_scripts_test_reqmap_py_2135["scripts/test_reqmap.py:2135"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2135
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_2288_2349["scripts/reqmap.py:2288-2349"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_2288_2349
  f_scripts_test_reqmap_py_2199["scripts/test_reqmap.py:2199"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2199
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_2637_3946["scripts/reqmap.py:2637-3946"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_2637_3946
  f_scripts_test_reqmap_py_3189["scripts/test_reqmap.py:3189"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_3189
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_740_840["scripts/reqmap.py:740-840"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_740_840
  f_scripts_test_reqmap_py_2362["scripts/test_reqmap.py:2362"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2362
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_812_2241["scripts/reqmap.py:812-2241"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_812_2241
  f_scripts_test_reqmap_py_2496["scripts/test_reqmap.py:2496"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2496
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_3703_3725["scripts/reqmap.py:3703-3725"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_3703_3725
  f_scripts_test_reqmap_py_1035["scripts/test_reqmap.py:1035"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_1035
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>31 caps</small>"]
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

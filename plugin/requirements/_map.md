---
generated: 2026-06-21 11:22
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
  f_scripts_reqmap_py_962_996["scripts/reqmap.py:962-996"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_962_996
  f_scripts_test_reqmap_py_151_189["scripts/test_reqmap.py:151-189"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_151_189
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_526_583["scripts/reqmap.py:526-583"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_526_583
  f_scripts_test_reqmap_py_48_1201["scripts/test_reqmap.py:48-1201"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_48_1201
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_599_789["scripts/reqmap.py:599-789"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_599_789
  f_scripts_test_reqmap_py_266["scripts/test_reqmap.py:266"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_266
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_891_1260["scripts/reqmap.py:891-1260"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_891_1260
  f_scripts_test_reqmap_py_2426["scripts/test_reqmap.py:2426"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2426
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_1760_1907["scripts/reqmap.py:1760-1907"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_1760_1907
  f_scripts_test_reqmap_py_812_1326["scripts/test_reqmap.py:812-1326"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_812_1326
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_949_1351["scripts/reqmap.py:949-1351"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_949_1351
  f_scripts_test_reqmap_py_141_3414["scripts/test_reqmap.py:141-3414"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_141_3414
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_2908["scripts/reqmap.py:2908"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_2908
  f_scripts_test_reqmap_py_2303["scripts/test_reqmap.py:2303"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2303
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_839["scripts/reqmap.py:839"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_839
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
  f_scripts_reqmap_py_1597_1743["scripts/reqmap.py:1597-1743"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1597_1743
  f_scripts_test_reqmap_py_705_720["scripts/test_reqmap.py:705-720"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_705_720
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2013_2100["scripts/reqmap.py:2013-2100"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2013_2100
  f_scripts_test_reqmap_py_885_1309["scripts/test_reqmap.py:885-1309"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_885_1309
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_2857["scripts/reqmap.py:2857"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_2857
  f_scripts_test_reqmap_py_2261["scripts/test_reqmap.py:2261"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2261
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_2994_3023["scripts/reqmap.py:2994-3023"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_2994_3023
  f_scripts_test_reqmap_py_1789["scripts/test_reqmap.py:1789"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1789
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2405_2576["scripts/reqmap.py:2405-2576"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2405_2576
  f_scripts_test_reqmap_py_1975["scripts/test_reqmap.py:1975"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1975
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2434_2463["scripts/reqmap.py:2434-2463"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2434_2463
  f_scripts_test_reqmap_py_1975["scripts/test_reqmap.py:1975"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_1975
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2135_3988["scripts/reqmap.py:2135-3988"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2135_3988
  f_scripts_test_reqmap_py_562_1499["scripts/test_reqmap.py:562-1499"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_562_1499
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1012_1065["scripts/reqmap.py:1012-1065"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1012_1065
  f_scripts_test_reqmap_py_432["scripts/test_reqmap.py:432"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_432
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1451["scripts/reqmap.py:1451"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1451
  f_scripts_test_reqmap_py_754["scripts/test_reqmap.py:754"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_754
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_870_2281["scripts/reqmap.py:870-2281"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_870_2281
  f_scripts_test_reqmap_py_1663_1782["scripts/test_reqmap.py:1663-1782"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1663_1782
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2241_4004["scripts/reqmap.py:2241-4004"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2241_4004
  f_scripts_test_reqmap_py_1062_1500["scripts/test_reqmap.py:1062-1500"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1062_1500
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1548_1563["scripts/reqmap.py:1548-1563"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1548_1563
  f_scripts_test_reqmap_py_1603["scripts/test_reqmap.py:1603"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1603
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1472_1518["scripts/reqmap.py:1472-1518"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1472_1518
  f_scripts_test_reqmap_py_2619["scripts/test_reqmap.py:2619"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2619
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1605_1658["scripts/reqmap.py:1605-1658"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1605_1658
  f_scripts_test_reqmap_py_519_705["scripts/test_reqmap.py:519-705"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_519_705
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4153["scripts/reqmap.py:4153"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4153
  f_scripts_test_reqmap_py_2661["scripts/test_reqmap.py:2661"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_2661
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1102["scripts/reqmap.py:1102"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1102
  f_scripts_test_reqmap_py_798["scripts/test_reqmap.py:798"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_798
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_766_780["scripts/reqmap.py:766-780"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_766_780
  f_scripts_test_reqmap_py_2713["scripts/test_reqmap.py:2713"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_2713
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_2618["scripts/reqmap.py:2618"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_2618
  f_scripts_test_reqmap_py_2135["scripts/test_reqmap.py:2135"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2135
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_2700_2761["scripts/reqmap.py:2700-2761"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_2700_2761
  f_scripts_test_reqmap_py_2199["scripts/test_reqmap.py:2199"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2199
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3049_4358["scripts/reqmap.py:3049-4358"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3049_4358
  f_scripts_test_reqmap_py_3189["scripts/test_reqmap.py:3189"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_3189
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1152_1252["scripts/reqmap.py:1152-1252"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1152_1252
  f_scripts_test_reqmap_py_2362["scripts/test_reqmap.py:2362"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2362
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1224_2653["scripts/reqmap.py:1224-2653"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1224_2653
  f_scripts_test_reqmap_py_2496["scripts/test_reqmap.py:2496"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2496
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4115_4137["scripts/reqmap.py:4115-4137"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4115_4137
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

---
generated: 2026-07-03 23:22
nodes: 38
edges: 54
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
    REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
    REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
    REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
    REQ_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>REQ-DRIFTIMPACT-035</small>"]
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
    REQ_ORPHANCODE_034["Orphan-code warning<br><small>REQ-ORPHANCODE-034</small>"]
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
  REQ_COVERAGE_029 --> REQ_NEXT_013
  REQ_EXCALIDRAW_031 --> REQ_EXCALIDRAW_030
  REQ_EXCALIDRAW_032 --> REQ_EXCALIDRAW_030
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_MAP_007
  REQ_LINTCHECKS_025 --> REQ_LINT_014
  REQ_NEXT_013 --> REQ_MAP_007
  REQ_PAGES_021 --> REQ_MAP_007
  REQ_PROMOTE_TODO_001 --> REQ_NEW_004
  REQ_PROSE_024 --> REQ_EXTRACT_008
  REQ_SITE_026 --> REQ_MAP_007
  REQ_SITE_026 --> REQ_VIEWER_007
  REQ_SITE_026 --> REQ_PAGES_021
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
  f_scripts_reqmap_py_1149_1193["scripts/reqmap.py:1149-1193"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_1149_1193
  f_scripts_test_reqmap_py_152_4267["scripts/test_reqmap.py:152-4267"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_152_4267
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_629_700["scripts/reqmap.py:629-700"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_629_700
  f_scripts_test_reqmap_py_49_4220["scripts/test_reqmap.py:49-4220"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_49_4220
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_723_918["scripts/reqmap.py:723-918"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_723_918
  f_scripts_test_reqmap_py_271["scripts/test_reqmap.py:271"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_271
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_1055_1522["scripts/reqmap.py:1055-1522"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_1055_1522
  f_scripts_test_reqmap_py_2869_4251["scripts/test_reqmap.py:2869-4251"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2869_4251
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_2088_2236["scripts/reqmap.py:2088-2236"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_2088_2236
  f_scripts_test_reqmap_py_941_2304["scripts/test_reqmap.py:941-2304"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_941_2304
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_1136_1640["scripts/reqmap.py:1136-1640"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_1136_1640
  f_scripts_test_reqmap_py_142_4429["scripts/test_reqmap.py:142-4429"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_142_4429
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_scripts_reqmap_py_121_1662["scripts/reqmap.py:121-1662"]
  REQ_CMDREGISTRY_033 -->|implements| f_scripts_reqmap_py_121_1662
  f_scripts_test_reqmap_py_4149["scripts/test_reqmap.py:4149"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_scripts_test_reqmap_py_4149
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_3308["scripts/reqmap.py:3308"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_3308
  f_scripts_test_reqmap_py_2661["scripts/test_reqmap.py:2661"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2661
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_968["scripts/reqmap.py:968"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_968
  f_scripts_test_reqmap_py_382["scripts/test_reqmap.py:382"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_382
  REQ_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>REQ-DRIFTIMPACT-035</small>"]
  f_scripts_reqmap_py_1560["scripts/reqmap.py:1560"]
  REQ_DRIFTIMPACT_035 -->|implements| f_scripts_reqmap_py_1560
  f_scripts_test_reqmap_py_597["scripts/test_reqmap.py:597"]
  REQ_DRIFTIMPACT_035 -->|tested-by| f_scripts_test_reqmap_py_597
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
  f_scripts_reqmap_py_1925_2071["scripts/reqmap.py:1925-2071"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1925_2071
  f_scripts_test_reqmap_py_821_836["scripts/test_reqmap.py:821-836"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_821_836
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2357_2444["scripts/reqmap.py:2357-2444"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2357_2444
  f_scripts_test_reqmap_py_1014_1556["scripts/test_reqmap.py:1014-1556"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_1014_1556
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_3246["scripts/reqmap.py:3246"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_3246
  f_scripts_test_reqmap_py_2618_2719["scripts/test_reqmap.py:2618-2719"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2618_2719
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_3418_3447["scripts/reqmap.py:3418-3447"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_3418_3447
  f_scripts_test_reqmap_py_2064_4381["scripts/test_reqmap.py:2064-4381"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_2064_4381
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2760_2940["scripts/reqmap.py:2760-2940"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2760_2940
  f_scripts_test_reqmap_py_2332["scripts/test_reqmap.py:2332"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_2332
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2789_2827["scripts/reqmap.py:2789-2827"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2789_2827
  f_scripts_test_reqmap_py_2316_2332["scripts/test_reqmap.py:2316-2332"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_2316_2332
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2484_4478["scripts/reqmap.py:2484-4478"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2484_4478
  f_scripts_test_reqmap_py_678_4381["scripts/test_reqmap.py:678-4381"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_678_4381
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1209_1296["scripts/reqmap.py:1209-1296"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1209_1296
  f_scripts_test_reqmap_py_437["scripts/test_reqmap.py:437"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_437
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1756["scripts/reqmap.py:1756"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1756
  f_scripts_test_reqmap_py_883["scripts/test_reqmap.py:883"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_883
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_999_2636["scripts/reqmap.py:999-2636"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_999_2636
  f_scripts_test_reqmap_py_1938_4331["scripts/test_reqmap.py:1938-4331"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1938_4331
  REQ_ORPHANCODE_034["Orphan-code warning<br><small>REQ-ORPHANCODE-034</small>"]
  f_scripts_reqmap_py_1026_1602["scripts/reqmap.py:1026-1602"]
  REQ_ORPHANCODE_034 -->|implements| f_scripts_reqmap_py_1026_1602
  f_scripts_test_reqmap_py_537["scripts/test_reqmap.py:537"]
  REQ_ORPHANCODE_034 -->|tested-by| f_scripts_test_reqmap_py_537
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2595_4494["scripts/reqmap.py:2595-4494"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2595_4494
  f_scripts_test_reqmap_py_1203_1775["scripts/test_reqmap.py:1203-1775"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1203_1775
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1865_1891["scripts/reqmap.py:1865-1891"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1865_1891
  f_scripts_test_reqmap_py_1878_4331["scripts/test_reqmap.py:1878-4331"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1878_4331
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1777_1833["scripts/reqmap.py:1777-1833"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1777_1833
  f_scripts_test_reqmap_py_3062_4331["scripts/test_reqmap.py:3062-4331"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_3062_4331
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1933_1986["scripts/reqmap.py:1933-1986"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1933_1986
  f_scripts_test_reqmap_py_635_821["scripts/test_reqmap.py:635-821"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_635_821
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4645["scripts/reqmap.py:4645"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4645
  f_scripts_test_reqmap_py_3129["scripts/test_reqmap.py:3129"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_3129
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1333["scripts/reqmap.py:1333"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1333
  f_scripts_test_reqmap_py_927["scripts/test_reqmap.py:927"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_927
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_895_909["scripts/reqmap.py:895-909"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_895_909
  f_scripts_test_reqmap_py_3190["scripts/test_reqmap.py:3190"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_3190
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_2982["scripts/reqmap.py:2982"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_2982
  f_scripts_test_reqmap_py_2492["scripts/test_reqmap.py:2492"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2492
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_3064_3125["scripts/reqmap.py:3064-3125"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_3064_3125
  f_scripts_test_reqmap_py_2556["scripts/test_reqmap.py:2556"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2556
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3473_4855["scripts/reqmap.py:3473-4855"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3473_4855
  f_scripts_test_reqmap_py_3831["scripts/test_reqmap.py:3831"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_3831
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1405_1514["scripts/reqmap.py:1405-1514"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1405_1514
  f_scripts_test_reqmap_py_2793["scripts/test_reqmap.py:2793"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2793
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1486_3017["scripts/reqmap.py:1486-3017"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1486_3017
  f_scripts_test_reqmap_py_2939["scripts/test_reqmap.py:2939"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2939
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4607_4629["scripts/reqmap.py:4607-4629"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4607_4629
  f_scripts_test_reqmap_py_1176["scripts/test_reqmap.py:1176"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_1176
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>34 caps</small>"]
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

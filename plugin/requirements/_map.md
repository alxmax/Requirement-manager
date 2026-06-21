---
generated: 2026-06-21 19:26
nodes: 36
edges: 50
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
  f_scripts_reqmap_py_1069_1103["scripts/reqmap.py:1069-1103"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_1069_1103
  f_scripts_test_reqmap_py_151_189["scripts/test_reqmap.py:151-189"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_151_189
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_628_685["scripts/reqmap.py:628-685"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_628_685
  f_scripts_test_reqmap_py_48_1201["scripts/test_reqmap.py:48-1201"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_48_1201
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_701_896["scripts/reqmap.py:701-896"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_701_896
  f_scripts_test_reqmap_py_266["scripts/test_reqmap.py:266"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_266
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_998_1372["scripts/reqmap.py:998-1372"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_998_1372
  f_scripts_test_reqmap_py_2533["scripts/test_reqmap.py:2533"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2533
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_1890_2038["scripts/reqmap.py:1890-2038"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_1890_2038
  f_scripts_test_reqmap_py_812_2054["scripts/test_reqmap.py:812-2054"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_812_2054
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_1056_1463["scripts/reqmap.py:1056-1463"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_1056_1463
  f_scripts_test_reqmap_py_141_3638["scripts/test_reqmap.py:141-3638"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_141_3638
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_scripts_reqmap_py_120_1485["scripts/reqmap.py:120-1485"]
  REQ_CMDREGISTRY_033 -->|implements| f_scripts_reqmap_py_120_1485
  f_scripts_test_reqmap_py_3698["scripts/test_reqmap.py:3698"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_scripts_test_reqmap_py_3698
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_3066["scripts/reqmap.py:3066"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_3066
  f_scripts_test_reqmap_py_2410["scripts/test_reqmap.py:2410"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2410
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_946["scripts/reqmap.py:946"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_946
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
  f_scripts_reqmap_py_1727_1873["scripts/reqmap.py:1727-1873"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1727_1873
  f_scripts_test_reqmap_py_705_720["scripts/test_reqmap.py:705-720"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_705_720
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2159_2246["scripts/reqmap.py:2159-2246"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2159_2246
  f_scripts_test_reqmap_py_885_1334["scripts/test_reqmap.py:885-1334"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_885_1334
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_3015["scripts/reqmap.py:3015"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_3015
  f_scripts_test_reqmap_py_2368["scripts/test_reqmap.py:2368"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2368
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_3166_3195["scripts/reqmap.py:3166-3195"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_3166_3195
  f_scripts_test_reqmap_py_1814_1947["scripts/test_reqmap.py:1814-1947"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1814_1947
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2554_2734["scripts/reqmap.py:2554-2734"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2554_2734
  f_scripts_test_reqmap_py_2082["scripts/test_reqmap.py:2082"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_2082
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2583_2621["scripts/reqmap.py:2583-2621"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2583_2621
  f_scripts_test_reqmap_py_2066_2082["scripts/test_reqmap.py:2066-2082"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_2066_2082
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2281_4178["scripts/reqmap.py:2281-4178"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2281_4178
  f_scripts_test_reqmap_py_562_1524["scripts/test_reqmap.py:562-1524"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_562_1524
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1119_1172["scripts/reqmap.py:1119-1172"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1119_1172
  f_scripts_test_reqmap_py_432["scripts/test_reqmap.py:432"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_432
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1579["scripts/reqmap.py:1579"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1579
  f_scripts_test_reqmap_py_754["scripts/test_reqmap.py:754"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_754
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_977_2430["scripts/reqmap.py:977-2430"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_977_2430
  f_scripts_test_reqmap_py_1688_1807["scripts/test_reqmap.py:1688-1807"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1688_1807
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2390_4194["scripts/reqmap.py:2390-4194"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2390_4194
  f_scripts_test_reqmap_py_1062_1525["scripts/test_reqmap.py:1062-1525"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1062_1525
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1678_1693["scripts/reqmap.py:1678-1693"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1678_1693
  f_scripts_test_reqmap_py_1628["scripts/test_reqmap.py:1628"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1628
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1600_1646["scripts/reqmap.py:1600-1646"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1600_1646
  f_scripts_test_reqmap_py_2726["scripts/test_reqmap.py:2726"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2726
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1735_1788["scripts/reqmap.py:1735-1788"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1735_1788
  f_scripts_test_reqmap_py_519_705["scripts/test_reqmap.py:519-705"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_519_705
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4343["scripts/reqmap.py:4343"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4343
  f_scripts_test_reqmap_py_2780["scripts/test_reqmap.py:2780"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_2780
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1209["scripts/reqmap.py:1209"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1209
  f_scripts_test_reqmap_py_798["scripts/test_reqmap.py:798"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_798
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_873_887["scripts/reqmap.py:873-887"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_873_887
  f_scripts_test_reqmap_py_2832["scripts/test_reqmap.py:2832"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_2832
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_2776["scripts/reqmap.py:2776"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_2776
  f_scripts_test_reqmap_py_2242["scripts/test_reqmap.py:2242"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2242
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_2858_2919["scripts/reqmap.py:2858-2919"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_2858_2919
  f_scripts_test_reqmap_py_2306["scripts/test_reqmap.py:2306"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2306
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3221_4550["scripts/reqmap.py:3221-4550"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3221_4550
  f_scripts_test_reqmap_py_3406["scripts/test_reqmap.py:3406"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_3406
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1259_1364["scripts/reqmap.py:1259-1364"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1259_1364
  f_scripts_test_reqmap_py_2469["scripts/test_reqmap.py:2469"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2469
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1336_2811["scripts/reqmap.py:1336-2811"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1336_2811
  f_scripts_test_reqmap_py_2603["scripts/test_reqmap.py:2603"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2603
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4305_4327["scripts/reqmap.py:4305-4327"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4305_4327
  f_scripts_test_reqmap_py_1035["scripts/test_reqmap.py:1035"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_1035
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>32 caps</small>"]
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

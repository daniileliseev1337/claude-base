# Graph Report - .  (2026-06-22)

## Corpus Check
- 219 files · ~181,041 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 708 nodes · 818 edges · 92 communities (69 shown, 23 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 61 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]

## God Nodes (most connected - your core abstractions)
1. `OcrMatch` - 16 edges
2. `replace_text_in_image()` - 13 edges
3. `agents/agents.md` - 13 edges
4. `Knowledge Library Implementation Plan` - 13 edges
5. `structured-artifacts — выносить контекст крупной задачи в md-файлы` - 13 edges
6. `render_text()` - 12 edges
7. `agents/norm-lookup.md` - 11 edges
8. `image-text-replace skill` - 11 edges
9. `Claude Code Hooks на Windows: 10+ ловушек настройки (SessionStart/End, PowerShell, прокси)` - 9 edges
10. `spec-writer — генерация Excel/DOCX спецификаций по объектам` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Workflow — детерминированный JS-скрипт оркестрации субагентов` --semantically_similar_to--> `graphify — knowledge-graph navigator`  [INFERRED] [semantically similar]
  memory/reference_workflow_tool.md → skills/graphify/SKILL.md
- `Команда /format (применить ГОСТ-стиль)` --conceptually_related_to--> `chain:docx-from-template`  [INFERRED]
  commands/format.md → chains/docx-from-template.md
- `Knowledge Library Implementation Plan` --implements--> `Категория ЭО (ПУЭ, СП 256, СП 76)`  [EXTRACTED]
  docs/superpowers/plans/2026-05-26-knowledge-library.md → library/categories/eo.md
- `Knowledge Library Implementation Plan` --implements--> `Категория ОВ (СП 60, СП 7 и связанные)`  [EXTRACTED]
  docs/superpowers/plans/2026-05-26-knowledge-library.md → library/categories/ov.md
- `Knowledge Library Implementation Plan` --implements--> `Категория ППР (Постановления Правительства)`  [EXTRACTED]
  docs/superpowers/plans/2026-05-26-knowledge-library.md → library/categories/ppr.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Format reviewer trio** —  [EXTRACTED 1.00]
- **Writer agents norm-lookup dependency** —  [EXTRACTED 1.00]
- **Karpathy principles in all agents** —  [EXTRACTED 1.00]
- **Тройка форматных ревьюеров (word-checker / excel-validator / pdf-reviewer)** — agents_word_checker_word_checker, agents_smetcik_smetcik, agents_snabzhenets_snabzhenets [EXTRACTED 1.00]
- **Пайплайн каскадов ПТО: состав → схемы → сборка PDF** — blocks_pto_id_volume_cascade_chain, blocks_pto_id_scheme_cascade_chain, blocks_pto_id_volume_graph_skill [EXTRACTED 1.00]
- **Цепочка снабжение → смета: снабженец → сметчик → excel-validator** — agents_snabzhenets_snabzhenets, agents_smetcik_smetcik, chains_upd_to_spec_reconcile_chain [EXTRACTED 1.00]
- **** — library_index_md, library_categories_ov, library_categories_eo, library_categories_vk, library_categories_ss, library_categories_spds, library_categories_ppr, library_categories_prikazy, library_categories_shablony [INFERRED 1.00]
- **** — docs_superpowers_specs_knowledge_library_design, docs_superpowers_plans_knowledge_library_plan, docs_superpowers_plans_knowledge_library_set_library_root_ps1, library_readme_md, library_index_md [INFERRED 0.95]
- **** — memory_2026_05_07_pnr_ventilation_lessons, memory_2026_05_08_pnr_cooling_counting_invariants, memory_2026_05_08_pnr_cooling_auditor_imperative [INFERRED 0.95]
- **PowerShell 5.1 + Windows-специфичные ловушки в скриптах** —  [INFERRED 0.85]
- **Сетевые ограничения: корп-прокси и геоблоки для внешних сервисов** —  [INFERRED 0.85]
- **Auto-sync pipeline: hooks → git → session-reports** —  [INFERRED 0.90]
- **autocad-mcp грабли (кириллица, file_ipc, PDFIMPORT, печать в PDF)** —  [INFERRED]
- **Правка docx — провальные паттерны (python-docx, плавающая шапка, таблицы)** —  [INFERRED]
- **Harvest-workflow и управление инструментами (лицензии, тест-план, триггеры)** —  [INFERRED]
- **acad-recreation skill + toolkit + autocad-mcp = PDF→DWG workflow** — acad_recreation_skill_concept, acad_recreation_skill_lisp_toolkit, acad_recreation_skill_pdf_multiview, mcp_autocad_mcp [INFERRED]
- **domain-grilling + detector hook + triggers/reminder = строй-задача гейтинг** — domain_grilling_skill_concept, domain_grilling_skill_detector_ps1, domain_grilling_skill_triggers_txt, domain_grilling_skill_reminder_txt [INFERRED]
- **facts-layer + domain-grilling + chains-pattern = стартовый цикл проекта** — facts_layer_skill_concept, domain_grilling_skill_concept, chains_pattern_skill_concept [INFERRED]
- **image-text-replace full pipeline: EasyOCR + LaMa + SD + calibration** — image_text_replace_skill_easyocr, image_text_replace_skill_lama_inpaint, image_text_replace_skill_sd_refine, image_text_replace_readme_pipeline_script, image_text_replace_readme_calibration_script [EXTRACTED 1.00]
- **PNR+VOR helper workflow: skill + checklist + profiles** — pnr_vor_helper_skill_skill, pnr_vor_pipeline_checklist, pnr_vor_pnr_profiles, pnr_vor_helper_skill_5_profiles [EXTRACTED 1.00]
- **TN audit workflow: build_map + fan-out workflow + adversarial verify** — id_tom_priemka_skill_priemka, id_tom_priemka_skill_build_map, id_tom_priemka_skill_workflow, id_tom_priemka_skill_adversarial [EXTRACTED 1.00]
- **УПД → спецификация pipeline: upd-parser + excel-helper + spec-writer + verify** — upd_parser_skill_concept, skill_excel_helper_concept, spec_writer_skill_concept, upd_parser_script_verify_entry, skill_upd_parser_chains_upd_spec [EXTRACTED 1.00]
- **Генерация docx + ревью: word-helper + word-checker + stroy-formatting** — word_helper_skill_concept, agent_word_checker_concept, stroy_formatting_skill_concept, word_helper_k7_letter_template [INFERRED 0.85]
- **Жизненный цикл задачи через structured-artifacts: ROADMAP→STATE→PLAN→агент→REVIEW→DECISIONS** — structured_artifacts_ref_roadmap_template, structured_artifacts_ref_state_template, structured_artifacts_ref_plan_template, structured_artifacts_ref_review_template, structured_artifacts_ref_decisions_template, structured_artifacts_skill_concept [EXTRACTED 1.00]

## Communities (92 total, 23 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (42): Агент auditor — содержательная сверка артефакта с источниками, Агент excel-validator — read-only ревьюер xlsx, Агент снабженец — парсинг УПД/накладных и снабжение, Агент word-checker — read-only ревьюер docx, gsd-redux Концепт 2 — источник structured-artifacts методологии, memory/context_discipline.md — дисциплина контекста, feedback_cert_sourcing_fabrication — урок: выдуманные № ГРСИ, ПНР и ВОР таблицы — структура эталон (+34 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (40): acad-recreation — воссоздание чертежей PDF→DWG, file_ipc_cp1251.patch — патч сервера для русского AutoCAD, install.ps1 — установщик LISP-toolkit и cp1251-патч, acad_lisp_toolkit.lsp — Lee Mac dynblock-функции, pdf_multiview.py — 9-tile multi-scale препроцессинг PDF, cherry_pick_batch.md — инструкция batch-инструментов из prumputira, excel-validator — агент проверки xlsx формул и ячеек, id-engineer — агент исполнительной документации (+32 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (32): agents/agents.md, agents/audit-rd-section.md, agents/auditor.md, agents/designer.md, agents/excel-validator.md, agents/expertiza-responder.md, agents/id-engineer.md, agents/kp-writer.md (+24 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (26): context discipline and cascade loading, FULL vs LITE handoff package modes, handoff-to-new-chat skill, session-report artifact for handoff, WARNING/CRITICAL context utilization thresholds, block-behavior.md — 5 Karpathy principles, Principle 4: Goal-Driven Execution, Principle 5: Honest Collaborator not Sycophant (+18 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (24): Расценки ГЭСН/ФЕР, Индексы пересчёта цен, Локальная смета (ЛС/КС-2/КС-3), Накладные расходы и сметная прибыль, Ценовой аудит спецификации перед экспертизой, сметчик, Сравнение цен поставщиков, снабженец (+16 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (24): WebFetch «у нас уже есть» — не значит «работает», Firecrawl — веб-скрапинг с headless-браузером, WebFetch Tool (встроенный), Harvest: проактивные триггеры запуска поиска инструментов, Harvest-workflow: операционные правила поиска инструментов, Windows Sandbox / временный venv для тестирования инструментов, Named chains — именованные цепочки оркестрации (до 5 pipeline), chain:design-stamp-corrections (+16 more)

### Community 6 - "Community 6"
Cohesion: 0.08
Nodes (23): _added, agentPushNotifEnabled, autoMode, allow, source, _comment, effortLevel, enabledPlugins (+15 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (23): image-text-replace lessons learned document, Times Bold as default scan font finding, unify_font_size_for_batch function, image-text-replace calibration.py script, image-text-replace pipeline.py script, CNN Neural Style Transfer option, Diffusion Inpainting option (hybrid bg refine), font calibration guard (AskUserQuestion before render) (+15 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (22): agentPushNotifEnabled, autoMode, allow, source, effortLevel, enabledPlugins, claude-md-management@claude-plugins-official, superpowers@claude-plugins-official (+14 more)

### Community 9 - "Community 9"
Cohesion: 0.13
Nodes (22): Семья агентов ИД (id-engineer, id-remarks, id-cascade, id-docs), Блок ПТО, Инвариант ПВ ≡ ВСО ≡ ВОР ≡ ИС, Автопоиск свободной зоны листа DWG, Каскад исполнительных схем DWG (id-scheme-cascade), W-слой: замена OLE-таблиц на ACAD_TABLE, find_free_zone.py (растровый детектор зоны), gen_table.lsp (c7:build / c7:build-multi) (+14 more)

### Community 10 - "Community 10"
Cohesion: 0.10
Nodes (22): Hook должен догонять ahead-origin коммиты, не только working tree changes, Скрипт auto-pull.ps1 (SessionStart hook), Скрипт auto-push.ps1 (SessionEnd hook), git push 403: сценарий 12a (PAT истёк) vs 12b (wrong account/collaborator), Claude Code Hooks на Windows: 10+ ловушек настройки (SessionStart/End, PowerShell, прокси), Ловушка: 2>&1 на native exec в PowerShell 5.1 под ErrorActionPreference=Stop, Корп-прокси режет HTTP CONNECT для git — git -c http.proxy="" как лекарство, Политика: каждая сессия → session-report обязательно (приватное репо, снижение планки) (+14 more)

### Community 11 - "Community 11"
Cohesion: 0.15
Nodes (21): facts-layer Implementation Plan, FACTS.template.md (шаблон источника правды), Алгоритм поиска norm-lookup (8 шагов + failure modes), Knowledge Library Implementation Plan, Set-LibraryRoot.ps1 (per-PC setup helper), facts-layer Design Spec, Границы FACTS.md: данные vs инструкции vs решения vs уроки, Read-first механизм FACTS.md (правило в CLAUDE.md + промпт агента) (+13 more)

### Community 12 - "Community 12"
Cohesion: 0.11
Nodes (20): compute_midline_paste_y(), _find_alpha_anchors(), _find_pixel_anchors(), _get_reader(), _load_image_as_array(), main(), _match_histogram_to_reference(), _parse_args() (+12 more)

### Community 13 - "Community 13"
Cohesion: 0.17
Nodes (15): _extract_char_glyph(), filter_matches(), _find_char_in_scan(), find_neighbor_cell_reference(), find_value_near_label(), OcrMatch, Axis-aligned bounding rectangle: (x, y, w, h)., Pick matches whose text matches user's pattern. (+7 more)

### Community 14 - "Community 14"
Cohesion: 0.16
Nodes (17): _looks_like_items_header(), _map_columns(), _norm_space(), parse_header(), parse_items(), parse_totals(), Парсинг УПД (Универсального передаточного документа) в structured dict.  Миним, Извлекает таблицу позиций УПД через pdfplumber.extract_tables().      Возвраща (+9 more)

### Community 15 - "Community 15"
Cohesion: 0.18
Nodes (12): Enum, test_resolve_target_path_contract(), test_resolve_target_path_correspondence(), test_resolve_target_path_invoice(), test_resolve_target_path_unknown_project_raises(), FileType, Загрузка файлов на Я.Диск в правильную папку проекта.  Использует WebDAV напря, Тип файла → подпапка проекта. (+4 more)

### Community 16 - "Community 16"
Cohesion: 0.17
Nodes (13): extract_text_entities(), find_stamp(), _grep(), list_blocks(), list_layers(), Извлечение данных из DXF через ezdxf: слои, текст, штамп., Возвращает все TEXT/MTEXT сущности с их координатами и слоями., Извлекает данные штампа: проект, номер листа, масштаб, стадия. (+5 more)

### Community 17 - "Community 17"
Cohesion: 0.14
Nodes (14): _apply_texture_residual(), _estimate_psf_sigma(), _extract_texture_residual(), Estimate anisotropic Gaussian PSF (sigma_x, sigma_y) from text edges     in the, Estimate noise std of paper background near bbox. Fallback 5.0., Render text at 2× scale → degrade to scan-style → return (rgb, alpha, text_offse, Draw `replacements` text onto the inpainted image at original bbox positions., Median color of darkest N-percentile pixels in bbox = real stroke cores. (+6 more)

### Community 18 - "Community 18"
Cohesion: 0.21
Nodes (11): main(), main(), cellstr(), detect_qty_col(), find_tables(), main(), parse_table(), Return [(start_row, end_row), ...] for each VOR table on the sheet. (+3 more)

### Community 19 - "Community 19"
Cohesion: 0.20
Nodes (12): _ascii_safe_cache_dir(), build_mask(), _ensure_deps(), inpaint_fast(), inpaint_lama(), Main public entry. Returns dict with summary.      `preloaded_matches` — если, Binary mask (0/255) covering match bboxes + dilation., Return an ASCII-only cache directory for torch/iopaint models.      Windows + (+4 more)

### Community 20 - "Community 20"
Cohesion: 0.17
Nodes (11): claude.ai Adobe Experience Manager, timestamp, claude.ai Google Drive, timestamp, claude.ai Microsoft 365, timestamp, claude.ai Superhuman Mail, timestamp (+3 more)

### Community 21 - "Community 21"
Cohesion: 0.20
Nodes (10): extract_text_blocks(), find_stamp_data(), _grep(), Извлечение текстовых блоков из PDF + поиск штампа чертежа., Ищет данные штампа в правом нижнем углу (типичное место).      Возвращает {pro, Возвращает список блоков {text, bbox=(x0,y0,x1,y1)} со страницы., Стамп должен вернуть dict с ключами project, drawing_no, scale (или None)., Проверяем что blocks возвращаются с координатами. (+2 more)

### Community 22 - "Community 22"
Cohesion: 0.23
Nodes (11): _copy_column_widths(), _copy_header(), _infer_key_mapping(), Запись нового листа «Спец. N» в существующий xlsx-реестр объекта <организация>., Read-back verification после write_spec_sheet (§4 Karpathy).      Returns: спи, Копирует строку заголовков (значения + стили шрифта/выравнивания/заливки)., Из заголовков template-листа собирает маппинг {header_text: column_letter}., Создаёт новый лист и пишет в него позиции.      Args:         workbook_path: (+3 more)

### Community 23 - "Community 23"
Cohesion: 0.18
Nodes (9): all, BATCHES, checked, confirmed, FINDINGS, meta, toVerify, ver (+1 more)

### Community 24 - "Community 24"
Cohesion: 0.33
Nodes (9): auto-sync.log — лог auto-pull/auto-push, .developer-marker — файл-маркер роли Developer (hub), feedback-pending/ — папка отложенного feedback с consumer ПК, Role detection и CHANGELOG notification, Sessions — обязательный отчёт каждой сессии, auto-pull.ps1 — SessionStart hook, git pull, auto-push.ps1 — SessionEnd hook, git push managed paths, scripts/ — auto-sync скрипты (auto-pull/auto-push) (+1 more)

### Community 25 - "Community 25"
Cohesion: 0.36
Nodes (7): _find_font_size_for_height(), main(), _parse_args(), Find font_size such that test_char renders with given cap height., Render comparison sheet with real scan + N font variants., render_calibration_sheet(), Namespace

### Community 26 - "Community 26"
Cohesion: 0.43
Nodes (8): Воссоздание ОВ-проекта квартиры из PDF в DWG (8 этапов), PDFIMPORT в AutoCAD: калибровка, чистка подложки, динблоки, autocad-mcp: кириллица (асимметрия вход/выход) + document open, autocad-mcp backend file_ipc (живой AutoCAD по COM), PDF-наложение через AutoCAD/PDFIMPORT с возвратом в DWG, PyMuPDF get_drawings — идентификация наложения в page-space, PDF разметка через PyMuPDF/SVG-слой без AutoCAD, Редактирование вектор-PDF через Inkscape (удаление штампов)

### Community 27 - "Community 27"
Cohesion: 0.25
Nodes (7): allowed, compliance_taints, defaults, allowed, restrictions, allow_cobalt_plinth, enforce_web_search_mcp_isolation

### Community 28 - "Community 28"
Cohesion: 0.25
Nodes (7): hooks, PostToolUse, permissions, allow, statusLine, command, type

### Community 30 - "Community 30"
Cohesion: 0.33
Nodes (5): edges, hyperedges, input_tokens, nodes, output_tokens

### Community 31 - "Community 31"
Cohesion: 0.33
Nodes (5): $last_updated, mcp_servers, python_user_packages, $schema_doc, $schema_version

### Community 32 - "Community 32"
Cohesion: 0.33
Nodes (6): Feedback-канал consumer→hub: архитектура и поток, Consumer-машина (без .developer-marker), feedback-pending/<тема>.md — буфер уроков consumer, Hub-машина (dev-ПК с .developer-marker), Прокси и GitHub bypass — сетевая настройка за корп-прокси, NO_PROXY для локальных MCP-мостов (127.0.0.1/localhost)

### Community 33 - "Community 33"
Cohesion: 0.40
Nodes (5): dwg_to_dxf(), find_oda_executable(), Конвертация DWG -> DXF через ODA File Converter (бесплатный, от Open Design Alli, Ищет ODAFileConverter.exe в стандартных местах + PATH., Конвертирует DWG в DXF. Возвращает путь к DXF.

### Community 34 - "Community 34"
Cohesion: 0.47
Nodes (5): as_number(), main(), parse_rows(), 244:250' -> (244, 250); '244' -> (244, 244)., Привести значение ячейки к float или None (формулы без кэша → None).

### Community 35 - "Community 35"
Cohesion: 0.60
Nodes (5): adversarial verification phase (false alarm filter), build_map.py reference map builder tool, id-tom-priemka skill (TN page-by-page audit), severity levels: CRITICAL/MAJOR/MINOR/INFO, priemka_workflow.js fan-out audit tool

### Community 36 - "Community 36"
Cohesion: 0.70
Nodes (4): Image, crop(), multiview(), render_page()

### Community 37 - "Community 37"
Cohesion: 0.50
Nodes (5): Кейс ПНР Вентиляции: уроки v1 (выдумывание, переусложнение), Принцип: копия шаблона + replace placeholders (не генерация с нуля), Визуальная сверка документа обязательна до сдачи, Auditor: императивный вызов (не диспозитивный) при шаблон+источники, Counting invariants: 9 vs 8 конденсаторов — пропуск через 3 фильтра

### Community 38 - "Community 38"
Cohesion: 0.50
Nodes (3): agents, memory, skills

### Community 39 - "Community 39"
Cohesion: 0.50
Nodes (4): glm-ocr 0.9B — кандидат замены EasyOCR, Выбор модели graphify-экстрактора (granite4.1 vs gemma4), Шорт-лист локальных моделей под кейсы фирмы, Сводка моделей Ollama (июнь 2026)

### Community 40 - "Community 40"
Cohesion: 0.50
Nodes (4): code-mapper vs graphify: статичный контекст vs queryable-граф, Пилот code-mapper (PROJECT_CONTEXT.md), Пилот context-ledger (git-hook 28x сжатие), Гейт сессий vs context-ledger (альтернативы)

### Community 41 - "Community 41"
Cohesion: 0.50
Nodes (3): github_repo, token, token_encrypted

### Community 42 - "Community 42"
Cohesion: 0.50
Nodes (4): Detect cap height ignoring descenders (commas, parens, dots).      Row counts, For batch text replacement: compute ONE font_size for the whole     batch via m, smart_cap_height_detect(), unify_font_size_for_batch()

### Community 43 - "Community 43"
Cohesion: 0.67
Nodes (4): .local-state/extras-pending.flag — сигнал новых инструментов, mcp-manifest.json — центральный реестр MCP и Python-пакетов, setup-extras — распространение MCP и Python-пакетов, setup-extras.ps1 — установщик MCP и Python-пакетов

### Community 44 - "Community 44"
Cohesion: 0.50
Nodes (4): Правка существующих docx с шапкой/полями — провалы и рабочий метод, Шапка docx: плавающий логотип заменить inline-таблицей, Переформат docx-таблиц актов ВСО/ИД под новую шапку, python-docx: вложенные таблицы в ячейках (cell.tables)

### Community 46 - "Community 46"
Cohesion: 0.67
Nodes (3): main(), max_empty_rect(), Largest-area rectangle of False (free) cells meeting min dims.     occ: bool HxW

### Community 47 - "Community 47"
Cohesion: 0.83
Nodes (3): check(), main(), parse_pdfdate()

### Community 48 - "Community 48"
Cohesion: 1.00
Nodes (3): pyrevit-engineer — агент кнопок и скриптов Revit, Revit-Connector MCP (pyRevit Routes), reference_revit_mcp — pyRevit MCP паттерны и грабли

### Community 49 - "Community 49"
Cohesion: 0.67
Nodes (3): Двойной трек: OData Track1 + MCP-экосистема Track2, OData vs SQL view: критический инсайт 1С:ERP, 1C Research Sub-project Spec (OData REST + MCP)

### Community 50 - "Community 50"
Cohesion: 1.00
Nodes (3): AutoCAD PDF Restoration Design Spec, PDFIMPORT → entity cleanup → штамп-блок → PLOT pipeline, PDF content-stream surgery: 11 итераций провала

### Community 51 - "Community 51"
Cohesion: 0.67
Nodes (3): graphify commit hook and CLAUDE.md integration, build_merge incremental graph update function, graphify incremental update and cluster-only reference

## Knowledge Gaps
- **226 isolated node(s):** `github_repo`, `token`, `token_encrypted`, `agents`, `skills` (+221 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Principle 1: Think Before Coding` connect `Community 3` to `Community 7`?**
  _High betweenness centrality (0.002) - this node is a cross-community bridge._
- **What connects `github_repo`, `token`, `token_encrypted` to the rest of the system?**
  _305 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06504065040650407 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.06538461538461539 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.10084033613445378 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.08615384615384615 - nodes in this community are weakly interconnected._
- **Should `Community 4` be split into smaller, more focused modules?**
  _Cohesion score 0.09782608695652174 - nodes in this community are weakly interconnected._
---
created: 2026-05-18
updated: 2026-06-09
status: active
owner: Даниил
tags: [мета, индекс, memory]
---

# Memory — накопленные уроки и кейсы

Это аналитическая память (наша), не Claude Code'овская auto-memory. Каждый файл — один кейс или один тематический разбор. Имя файла — `YYYY-MM-DD_kebab-case.md`.

## Каталог

### Инфраструктура и инструменты

- [[2026-05-09_hooks-debugging]] — **главный документ**, 16 ловушек hooks-debugging (CONNECT прокси, 2>&1 под Stop, GIT_TERMINAL_PROMPT, ahead-origin не догонялся, и т.д.). Мета-урок 16 про повторение собственных уроков.
- [[2026-05-12_uninstall-and-chat-storage]] — где живёт чат-история Claude Code, как её защищать от Uninstall.
- [[2026-05-13_harvest-workflow]] — методология поиска внешних инструментов (GitHub → MCP registry → Anthropic skills).
- [[feedback_webfetch_reality_check]] — «уже есть» ≠ «работает». WebFetch (80-90% fail) и Adobe Firefly не работают на наших задачах; не списывать новый инструмент через «у нас уже есть X» без верификации. Источник — harvest 9 плагинов 2026-06-01.
- [[feedback_web_doc_fetch_browser_antibot]] — добывание документов (паспорта/СС/datasheet) под антиботом: на 401/403 НЕ сдаваться, эскалация на реальный браузер `playwright` (открыть карточку → прямая CDN-ссылка → скачать). Приёмы поиска: B2B-поставщики, товарный запрос, watermark=источник. Приёмы, не жёсткие правила. Источник — docs-каскад ИД (кейс LUNDA) 2026-06-09.
- [[feedback_cloud_tools_consent]] — для cloud-инструментов (Codex/Exa/Firecrawl/Higgsfield) consent-prompt в моменте (информированно), не жёсткий запрет обезличивания. Источник — harvest 9 плагинов 2026-06-01.
- [[reference_licenses_k7]] — договорённости К-7 по лицензиям (AGPL Firecrawl не блокер при условии не-распространения за пределы К-7/смежных). Источник — harvest 9 плагинов 2026-06-01.
- [[feedback_tool_sandbox_isolation]] — per-machine установки (npm -g, pip) через мои tool-команды идут в изолированное окружение, НЕ на реальный ПК. Давать команды для ручного запуска, не заявлять «установил». Источник — codex CLI кейс 2026-06-01.
- [[2026-05-14_session-report-policy]] — обязательность session-report'а каждой сессии, формат.
- [[2026-05-15_extras-distribution-mechanism]] — manifest + setup-extras + Install.ps1 Stage 8 архитектура распространения Python/MCP стека.
- [[2026-05-18_lesson-15-proxy-helpers-persistence]] — Урок 15: proxy-хелперы persistence в claude-lite-instaler (CLOSED 2026-05-18 коммитом `3562631`).
- [[2026-05-26_anthropic_geoblock_ru]] — Anthropic геоблокирует RU IP на уровне backend API → `app-unavailable-in-region` HTML вместо JSON → Claude Desktop defensive-блок → `accountId=null` → белый экран. Не корп-прокси, не TLS MITM.
- [[reference_revit_mcp]] — справочник Revit-Connector (pyRevit MCP). С 2026-06-18 — раздел «диагностика отказа подключения»: команды виснут/`503` пустой/`Server disconnected` при исправном Revit = (1) корп-прокси гонит localhost через `HTTP_PROXY` (фикс `trust_env=False` + `NO_PROXY`), (2) localhost→IPv6 (фикс `REVIT_HOST=127.0.0.1`), (3) Home-экран Revit = нет active doc; +грабли «две копии main.py». Прокси-аспект — [[proxy_github]].

### Архитектурные backlog'и (из аудитов чужих баз)

- [[project_designer_decomposition]] — backlog stage-decomposition агента `designer` по pattern К-7 (S1→S2→S3→S4). Не активировать пока нет реального триггера. Источник — аудит К-7 от 2026-05-20.
- [[backlog_promptfoo_semantic_tests]] — backlog promptfoo для семантических тестов LLM-агентов. Триггер — потребность тестировать вывод designer/word-checker на эталонах. Сейчас покрытие через pytest (см. `~/.claude/evals/`). Источник — аудит К-7 от 2026-05-20.
- [[backlog_teammate_mode_tmux]] — backlog teammateMode tmux + AGENT_TEAMS (4.7 из roadmap'а). tmux отсутствует на Windows DANIILPC + env-правки требуют явного согласия. Альтернатива — `teammateMode: in-process`. Источник — аудит К-7 от 2026-05-20.
- [[rd_plugins_test_plan]] — R&D test plan для свежеустановленных плагинов superpowers и claude-md-management (4.6, 4.8). Активны после перезапуска Claude Code. Источник — аудит К-7 от 2026-05-20.
- [[backlog_tools_layer_migration]] — миграция скриптов skills в слой `tools/` по Правилу 2 (skill-development). Инкрементально при касании, НЕ массовый рефактор. Источник — внедрение 4 правил Anthropic 2026-06-01.
- [[backlog_cross_model_review_rf]] — cross-model review на РФ-доступной модели (Codex отпал — ChatGPT геоблок РФ). Кандидаты: GigaChat/YandexGPT (приватность) / DeepSeek/Qwen. Источник — harvest #6 2026-06-01.

### Редактирование PDF / чертежей

- [[reference_inkscape_pdf_editing]] — ВЕРИФИЦИРОВАННЫЙ метод: удалить/подвинуть штамп
  или объект в вектор-PDF через Inkscape (Внутренний импорт → Delete/move → PDF →
  рендер-проверка). Замена провалившимся белым заливкам / content-stream surgery.
- [[reference_autocad_pdf_svg_markup]] — перерисовать **нанесённую графику** (разметка
  CCTV/СС/ЭО) на AutoCAD-PDF чистым PyMuPDF через SVG-слой, БЕЗ AutoCAD. Когда DWG на
  выходе не нужен. Верифицировано 2026-06-03.
- [[reference_autocad_pdf_overlay_mcp]] — то же через autocad-mcp / живой AutoCAD
  (PDFIMPORT + entmake + vla-PlotToFile), когда нужен DWG. Backend init, ловушки печати.
- [[2026-05-21_acad-com-cookbook]] — AutoCAD COM cookbook: DXF/ACAD_TABLE через pywin32.
  File IPC backend (mcp_dispatch.lsp) — правильный путь; ezdxf затирает ACAD_TABLE при regen,
  COM `AcadTable.SetText` — state-level правка. Полезно на autocad-mcp задачах.

### Доменные кейсы (проектирование)

- [[2026-05-07-pnr-ventilation]] — пуско-наладка вентиляции.
- [[2026-05-08_pnr-cooling-9vs8]] — пуско-наладка холодоснабжения, кейс «9 vs 8 единиц».
- [[reference_pyrevit_k7]] — PyRevit-плагины К-7 (IronPython + Revit .NET API): ловушки
  WorksetTable/транзакций/фаз, генерация иконок. Новый домен (с 2026-05-28).
- [[reference_av_multimedia]] — AV/мультимедиа-инсталляции (музеи/интерактив): шаблон ФТ,
  бренды, ловушка «цены не по памяти → harvest». Новый домен MSI-ZAHAROV (с 2026-05-20).
- [[reference_docx_table_reformat]] — переформат docx-таблиц актов (ВСО/ИД) под новую шапку:
  трансформер python-docx (рекурсия cell.tables), словарь вместо regex, серийники с рукописных
  чертежей не угадывать. Скилл `vso-reformatter` — при 2-м кейсе.
- [[reference_docx_editing_failures]] — правка существующих docx с шапкой/полями: провалы и
  рабочий метод (кейс «бланк колледжа» 2026-06-01, 3-4 провала с уверенным «готово»). Триггеры:
  дописать в шаблон / заполнить бланк / шапка-логотип / подчёркивания-табы в Word.
- [[reference_acad_ov_dwg_recreation]] — **накопитель**: воссоздание ОВ-проекта квартиры из PDF
  в DWG через autocad-mcp (8 этапов + статус-трекер + рецепты + Phase-3 архитектура агентов). Наполняется.
- [[reference_autocad_mcp_cyrillic]] — общий урок autocad-mcp: кириллица вход(Unicode)/выход(cp1251),
  `drawing open` врёт → COM vla-Open. Полезно на любых AutoCAD-задачах.
- [[reference_workflow_tool]] — инструмент Workflow (Opus 4.8, мультиагентная оркестрация):
  что это, когда оправдан, кандидаты в named-workflow. Правило проактивного предложения — в CLAUDE.md.
- [[backlog_id_assembly_session]] — **BACKLOG: ИД (исполнительная документация) — отдельная сессия.**
  Устройство тома ИД, замечания ТЗ, прокачка id-engineer. Невероятно важный кейс (по слову пользователя).

## Когда писать в memory

- Пользователь скорректировал подход (с «почему» и «как применять»).
- Поймал ловушку — записать чтобы не повторить.
- Меняется архитектура — зафиксировать решение с обоснованием.
- НЕ писать: эфемерное «сейчас работаю над X», дублирование CLAUDE.md.

## Связанные

- [[CLAUDE]] — главные правила (где описана auto-memory vs наша memory)
- [[Карта vault]] — общая карта
- [[session-reports/session-reports|session-reports]] — отчёты сессий часто отсылают к memory-урокам

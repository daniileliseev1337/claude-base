---
created: 2026-05-18
updated: 2026-07-06
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
- [[reference_harvested_tools_2026]] — РЕЕСТР оценённых внешних инструментов (вердикт/tier/риск), чтобы НЕ переоценивать заново. Партия 2026-07-01 (8 из списка владельца, параллельный fan-out): MinerU (A, добавить — сильнее нашего документ-стека), council-of-high-intelligence (B, → скилл decision-council, лечит подхалимаж п.5), OmniRoute (B, пилот-черновики); отклонены с обоснованием: Loopy (заявка искажена), memanto (приватность-блокер), OpenHuman, Claude Science (гео-РФ), Torlink (пиратство). Полный журнал — `Трекер_реворк_базы.xlsx` (47 кандидатов).
- [[feedback_webfetch_reality_check]] — «уже есть» ≠ «работает». WebFetch (80-90% fail) и Adobe Firefly не работают на наших задачах; не списывать новый инструмент через «у нас уже есть X» без верификации. Источник — harvest 9 плагинов 2026-06-01.
- [[feedback_web_doc_fetch_browser_antibot]] — добывание документов (паспорта/СС/datasheet) под антиботом: на 401/403 НЕ сдаваться, эскалация на реальный браузер `playwright` (открыть карточку → прямая CDN-ссылка → скачать). Приёмы поиска: B2B-поставщики, товарный запрос, watermark=источник. Приёмы, не жёсткие правила. Источник — docs-каскад ИД (кейс LUNDA) 2026-06-09.
- [[feedback_cloud_tools_consent]] — для cloud-инструментов (Codex/Exa/Firecrawl/Higgsfield) consent-prompt в моменте (информированно), не жёсткий запрет обезличивания. Источник — harvest 9 плагинов 2026-06-01.
- [[reference_licenses]] — договорённости <организация> по лицензиям (AGPL Firecrawl не блокер при условии не-распространения за пределы <организация>/смежных). Источник — harvest 9 плагинов 2026-06-01.
- [[feedback_tool_sandbox_isolation]] — per-machine установки (npm -g, pip) через мои tool-команды идут в изолированное окружение, НЕ на реальный ПК. Давать команды для ручного запуска, не заявлять «установил». Источник — codex CLI кейс 2026-06-01.
- [[2026-05-14_session-report-policy]] — обязательность session-report'а каждой сессии, формат.
- [[2026-05-15_extras-distribution-mechanism]] — manifest + setup-extras + Install.ps1 Stage 8 архитектура распространения Python/MCP стека.
- [[2026-05-18_lesson-15-proxy-helpers-persistence]] — Урок 15: proxy-хелперы persistence в claude-lite-instaler (CLOSED 2026-05-18 коммитом `3562631`).
- [[2026-05-26_anthropic_geoblock_ru]] — Anthropic геоблокирует RU IP на уровне backend API → `app-unavailable-in-region` HTML вместо JSON → Claude Desktop defensive-блок → `accountId=null` → белый экран. Не корп-прокси, не TLS MITM.
- [[feedback_claude_desktop_msix]] — Claude Desktop на Windows = **MSIX в `WindowsApps`** (НЕ «урезанная Store-версия»); где данные/`claude_desktop_config.json`; «застрявший» лечится чистой переустановкой той же версии; установщик гео-блок RU/AE. Анти-паттерн: не гнать необратимое (удаление рабочего приложения) на непроверенном допущении о дистрибуции — сначала `Get-AppxPackage`/`VersionInfo` (verifiable-first, Karpathy #5).
- [[reference_revit_mcp]] — справочник Revit-Connector (pyRevit MCP). С 2026-06-18 — раздел «диагностика отказа подключения»: команды виснут/`503` пустой/`Server disconnected` при исправном Revit = (1) корп-прокси гонит localhost через `HTTP_PROXY` (фикс `trust_env=False` + `NO_PROXY`), (2) localhost→IPv6 (фикс `REVIT_HOST=127.0.0.1`), (3) Home-экран Revit = нет active doc; +грабли «две копии main.py». Прокси-аспект — [[proxy_github]].

### Архитектурные backlog'и (из аудитов чужих баз)

- [[project_designer_decomposition]] — backlog stage-decomposition агента `designer` по pattern <организация> (S1→S2→S3→S4). Не активировать пока нет реального триггера. Источник — аудит <организация> от 2026-05-20.
- [[backlog_promptfoo_semantic_tests]] — backlog promptfoo для семантических тестов LLM-агентов. Триггер — потребность тестировать вывод designer/word-checker на эталонах. Сейчас покрытие через pytest (см. `~/.claude/evals/`). Источник — аудит <организация> от 2026-05-20.
- [[backlog_teammate_mode_tmux]] — backlog teammateMode tmux + AGENT_TEAMS (4.7 из roadmap'а). tmux отсутствует на Windows DANIILPC + env-правки требуют явного согласия. Альтернатива — `teammateMode: in-process`. Источник — аудит <организация> от 2026-05-20.
- [[rd_plugins_test_plan]] — R&D test plan для свежеустановленных плагинов superpowers и claude-md-management (4.6, 4.8). Активны после перезапуска Claude Code. Источник — аудит <организация> от 2026-05-20.
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
- [[reference_pyrevit]] — PyRevit-плагины <организация> (IronPython + Revit .NET API): ловушки
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

### Инфраструктура базы (cascade-load из CLAUDE.md)

- [[reference_mcp]] — эталон 11 core MCP-серверов: детали, прогрев холодного uvx-кэша, статусы.
- [[reference_agents]] — эталон 16 доменных агентов: детали, живые фразы-триггеры, разграничения.
- [[auto_sync]] — auto-pull (SessionStart) / auto-push (SessionEnd) хуки синхронизации claude-base.
- [[role_detection]] — определение роли ПК (hub / consumer) по `.developer-marker`.
- [[updater_v2]] — Updater 2.0: настройка claude-base на новом ПК.
- [[sessions_policy]] — обязательный session-report каждой сессии: формат и зачем.
- [[token_economy]] — экономия токенов: гейт сессий, матрица моделей субагентов, мониторинг ccusage.
- [[profanity_marker]] — стиль общения, мат opt-in через маркер.
- [[auto_memory_policy]] — что и куда сохранять в auto-memory (типы записей, триггеры).
- [[context_discipline]] — дисциплина контекстного окна, handoff в новый чат.
- [[named_chains]] — именованные цепочки (named chains): когда и как создавать.
- [[harvest_workflow]] — методология harvest (поиск внешних инструментов): GitHub → skills.sh → MCP registry.
- [[harvest_proactive]] — проактивное предложение harvest при признаках задачи под инструмент.
- [[archive_v1]] — архив v1 (claude-stroy-base) — НЕ источник действующих правил.
- [[feedback_workflow]] — feedback consumer→hub: куда писать уроки/правки/косяки базы (Why + How).
- [[feedback_web_direct_access]] — добыча документов качества с B2B-сайтов: скрин-first, `--noproxy`, cookies, антибот. Главный веб-док.
- [[feedback_id_doc_search_method]] — КАК искать документы качества ИД: запросы, порядок, инструменты, watermark=источник.
- [[feedback_user_rules_docs_cascade]] — правила пользователя по DOCS-каскаду ИД: порядок работы, даты документ↔акт, поиск, складирование.
- [[feedback_is_lengths_from_dwg]] — длины исп. схем: только по DWG-плану (1:1 = факт); аксонометрия — только высотные длины + фасонка. Восстановлен 2026-07-06 (ссылки из трекеров томов вели в никуда); полный свод — `blocks/pto/ЗНАНИЯ ПТО….md`.
- [[feedback_manual_procedure_verbatim]] — процедуры из мануалов переносить ДОСЛОВНО по шагам, не пересказом по памяти.
- [[playwright_mcp_pin_version]] — playwright MCP about:blank = @latest авто-апдейт через прокси виснет; пин @0.0.76.
- [[web_access_r_jina_fallback]] — fallback веб-доступа: префикс `https://r.jina.ai/` при непробитии exa/WebFetch.

## Когда писать в memory

- Пользователь скорректировал подход (с «почему» и «как применять»).
- Поймал ловушку — записать чтобы не повторить.
- Меняется архитектура — зафиксировать решение с обоснованием.
- НЕ писать: эфемерное «сейчас работаю над X», дублирование CLAUDE.md.

## Связанные

- [[CLAUDE]] — главные правила (где описана auto-memory vs наша memory)
- [[Карта vault]] — общая карта
- [[session-reports/session-reports|session-reports]] — отчёты сессий часто отсылают к memory-урокам

---
created: 2026-05-18
updated: 2026-05-18
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
- [[feedback_cloud_tools_consent]] — для cloud-инструментов (Codex/Exa/Firecrawl/Higgsfield) consent-prompt в моменте (информированно), не жёсткий запрет обезличивания. Источник — harvest 9 плагинов 2026-06-01.
- [[reference_licenses_k7]] — договорённости К-7 по лицензиям (AGPL Firecrawl не блокер при условии не-распространения за пределы К-7/смежных). Источник — harvest 9 плагинов 2026-06-01.
- [[2026-05-14_session-report-policy]] — обязательность session-report'а каждой сессии, формат.
- [[2026-05-15_extras-distribution-mechanism]] — manifest + setup-extras + Install.ps1 Stage 8 архитектура распространения Python/MCP стека.
- [[2026-05-18_lesson-15-proxy-helpers-persistence]] — Урок 15: proxy-хелперы persistence в claude-lite-instaler (CLOSED 2026-05-18 коммитом `3562631`).

### Архитектурные backlog'и (из аудитов чужих баз)

- [[project_designer_decomposition]] — backlog stage-decomposition агента `designer` по pattern К-7 (S1→S2→S3→S4). Не активировать пока нет реального триггера. Источник — аудит К-7 от 2026-05-20.
- [[backlog_promptfoo_semantic_tests]] — backlog promptfoo для семантических тестов LLM-агентов. Триггер — потребность тестировать вывод designer/word-checker на эталонах. Сейчас покрытие через pytest (см. `~/.claude/evals/`). Источник — аудит К-7 от 2026-05-20.
- [[backlog_teammate_mode_tmux]] — backlog teammateMode tmux + AGENT_TEAMS (4.7 из roadmap'а). tmux отсутствует на Windows DANIILPC + env-правки требуют явного согласия. Альтернатива — `teammateMode: in-process`. Источник — аудит К-7 от 2026-05-20.
- [[rd_plugins_test_plan]] — R&D test plan для свежеустановленных плагинов superpowers и claude-md-management (4.6, 4.8). Активны после перезапуска Claude Code. Источник — аудит К-7 от 2026-05-20.

### Доменные кейсы (проектирование)

- [[2026-05-07-pnr-ventilation]] — пуско-наладка вентиляции.
- [[2026-05-08_pnr-cooling-9vs8]] — пуско-наладка холодоснабжения, кейс «9 vs 8 единиц».

## Когда писать в memory

- Пользователь скорректировал подход (с «почему» и «как применять»).
- Поймал ловушку — записать чтобы не повторить.
- Меняется архитектура — зафиксировать решение с обоснованием.
- НЕ писать: эфемерное «сейчас работаю над X», дублирование CLAUDE.md.

## Связанные

- [[CLAUDE]] — главные правила (где описана auto-memory vs наша memory)
- [[Карта vault]] — общая карта
- [[session-reports/session-reports|session-reports]] — отчёты сессий часто отсылают к memory-урокам

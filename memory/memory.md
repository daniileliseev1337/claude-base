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
- [[2026-05-14_session-report-policy]] — обязательность session-report'а каждой сессии, формат.
- [[2026-05-15_extras-distribution-mechanism]] — manifest + setup-extras + Install.ps1 Stage 8 архитектура распространения Python/MCP стека.
- [[2026-05-18_lesson-15-proxy-helpers-persistence]] — Урок 15: proxy-хелперы persistence в claude-lite-instaler (CLOSED 2026-05-18 коммитом `3562631`).

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

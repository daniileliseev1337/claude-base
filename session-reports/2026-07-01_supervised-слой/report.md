# Session report — supervised-слой над Claude Code (исполнение ПЛАНа)

**Дата:** 2026-07-01
**Программа:** реворк базы «Заведомо проигранный бой»
**Задача:** исполнить `ПЛАН_supervised-слой.md` через skill `superpowers:subagent-driven-development`, начиная с Фазы 0 (подтвердить протокол approval фактом до кода).

## Что сделано
Построен и интегрирован в базу **supervised-слой** — надзиратель за автономным Claude, только официальными механизмами (в рамках подписки, без reverse-eng, без SaaS):
- **Слой 1 (авто-арбитр, headless):** официальный `canUseTool` SDK перехватывает tool-calls воркера → `rules.decide()` → allow / deny+escalate. Fail-safe deny-by-default. Telegram/durable-лог эскалации.
- **Слой 2 (пульт):** официальный `claude remote-control`, одобряет человек с телефона/браузера (задокументирован).

Итог в базе: `skills/supervisor/` (`tools/` код+тесты, `SKILL.md`, `REMOTE_CONTROL.md`) + `mcp-manifest.json` += `claude-agent-sdk` (optional). **18 тестов green из базового расположения.**

## Метод (subagent-driven-development)
Свежий implementer + task-reviewer на задачу; фикс-субагент на Important-находки; финальный whole-branch review; auditor-гейт перед коммитом в базу. Модели: sonnet (дефолт содержательное+ревью), haiku (механические фиксы по готовому спеку), **opus (финальный whole-branch review — оправданная «крупная ставка»: security-компонент перед базой)**. Durable-progress: todo-трекер + status-файл (git-ledger не поднимал — greenfield PoC).

## Ключевые факты (подтверждены фактом, не по памяти)
- Канал approval: официально достижим для headless через `canUseTool` (SDK) / `--permission-prompt-tool` (CLI-MCP). Владелец выбрал **SDK**. Контракт сверен с УСТАНОВЛЕННЫМ `claude-agent-sdk 0.2.110`.
- **Важная граница (нашёл opus-ревью):** SDK НЕ зовёт `can_use_tool` для вызовов, уже разрешённых `permission_mode` (bypassPermissions/acceptEdits) или ambient `permissions.allow`. Закрыто для штатного применения пином `permission_mode="default"`+`setting_sources=[]` (арбитр сам запускает воркера). «Каждый вызов без исключений» → нужен `PreToolUse`-hook (отдельный апгрейд, стаб заложен). Честно отражено в SKILL.md — не переоценивать.

## Verifiable-first — что поймала проверка (3 раза)
1. Субагент Фазы 0 ложно объявил «Python отсутствует» — он проверял `python3` (MS-Store-заглушка в Git Bash); реальный `python` (3.12.10) есть. Перепроверка PowerShell'ом вскрыла → развилка переформулирована верно.
2. План вёл код в `~/.claude/tools/` — фактически **gitignored** → не уехал бы команде. Исправлено на `skills/supervisor/` (прецедент doc-extract).
3. План-стаб `canUseTool` возвращал dict `{"behavior":"allow"}` — реальный SDK требует объекты `PermissionResult*`. Поймано в Фазе 0, код написан под факт.

## Где ломалось / уроки
- **Async-субагенты выглядят как «зависание»** для пользователя (фон молчит) — надо явно объяснять ритм скилла. Моя проверка живости по размеру output-файла была ложной (0 байт при живом агенте — харнесс буферизует транскрипт); статус агента судить по completion-нотификации, не по файлу.
- **`AskUserQuestion`-виджет упал по Server error** — фолбэк на plain-text вопрос сработал; впредь при сбое виджета сразу текстом.
- Отчёты субагентов = непроверенные утверждения (skill-принцип): контроллерская дельта-проверка security-кода своими глазами окупалась.
- Owner-гейты (выбор канала; приёмка перед интеграцией) выносились явно, не решались молча.

## Артефакты
- База: `skills/supervisor/` + `mcp-manifest.json` (claude-agent-sdk optional). Раздача через `/sync-base`.
- Песочница (папка программы): `supervisor/` — `probe_channel.md` (Фаза 0), `POC_RESULT.md`, `_briefs/` (brief+report на каждую задачу), `.venv` (dev-only, не в базе).
- Статус программы обновлён: `0_СТАТУС_программы.md`.

## Остаётся (опционально)
Если владелец захочет «гейт каждого вызова» / надзор за чужими сессиями — отдельная мини-Фаза-0: проверить фактом, гейтит ли `PreToolUse`-hook под `bypassPermissions`, и перенести туда deny-логику (стаб уже заложен).

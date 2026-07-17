# Codex release handoff — 2026-07-17

## Goal

Довести release-gate Codex для сотрудников до строгого PASS либо оставить NOT PASS с единственным фактическим blocker на каждый незакрытый пункт.

## What is now proven

- Epic 5 = PASS только по owner-approved adjusted capability-gate. Широкие Word/PDF операции не подтверждены.
- `openai.chatgpt@26.707.91948` установлен в VS Code `1.125.1`, совместим и запущен в extension host вместе с `codex.exe app-server`.
- Revit-Connector, autocad-mcp, Word, Excel, PDF MCP и node_repl включены в CLI-конфигурации. Это не доказывает runtime уже открытых сессий.
- LibreOffice 26.2.4.2 установлен; он подтверждён только для узкого DOCX → PDF fallback-render gate.

## Evidence

- `Claude/reports/2026-07-17-vscode-codex-extension-runtime.md`
- `Claude/reports/2026-07-17-epic6-entry-preflight.md`
- `Claude/reports/2026-07-17-epic5-adjusted-closure.md`
- `Claude/reports/2026-07-17-mcp-enable-state.md`
- `Claude/STATUS.md`, верх `Claude/ЖУРНАЛ СЕССИЙ.md`, `0_СТАТУС_программы.md`

## Remaining release blockers

1. VS Code GUI checklist в `%USERPROFILE%/.claude/session-reports/2026-07-14_codex-phase3/vscode-verify.md` не заполнен: установка и runtime уже PASS, но боковая панель, авторизация и рабочий сценарий не доказаны.
2. Не определён release repository и не оформлено решение: коммитить generated `AGENTS.md` или собирать его при установке.
3. Нет доказанной ежедневной безинцидентной обкатки синка/хуков.
4. В preflight остаются scoped backlog Epic 1–3 и upstream hook-regression check; сверить их с roadmap и закрывать отдельными evidence либо фиксировать owner decision.

## Constraints

- Не отключать MCP, hooks, плагины или пользовательские сессии без прямого приказа владельца.
- Не подменять GUI-smoke статической проверкой или процессом extension host.
- Не объявлять общий Word/PDF edit PASS: Track Changes, массовая/структурная правка и PDF-object edit остаются NOT PASS.
- Перед каждым содержательным артефактом проводить независимый audit и обновлять `Claude/STATUS.md`, верх журнала и `0_СТАТУС_программы.md`.
- Работать только точечными изменениями; не трогать исходники узких Word/PDF gates.

## Recommended next step

Начать с GUI-checklist VS Code. Если интерфейс требует ручного действия пользователя (авторизация/команда Codex), зафиксировать точный наблюдаемый результат и продолжить с остальными пунктами, не имитируя PASS.

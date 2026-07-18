# Handoff LITE: native Codex import acceptance audit (2026-07-18)

## Цель

Проверить фактическую работоспособность и согласованность импортированных в Codex skills, agents, MCP и plugins; не приравнивать регистрацию к runtime PASS.

## Зафиксированные факты

- Владелец выполнил штатный Import from Claude Code с отмеченными инструментами/настройками, проектами и сессиями.
- После импорта `codex mcp list` показывает 16 enabled MCP: локальные и сторонние сервисы; секреты в выводе замаскированы.
- В `~/.codex/config.toml` присутствуют 19 блоков `mcp_servers` (включая env-подблоки), в том числе Word, Excel, PDF, Revit, AutoCAD и импортированные внешние серверы.
- `python ~/.claude/scripts/codex_sync.py check` возвращает exit `2`: `canon-newer config.toml#managed`. Не запускать sync до явного решения о слиянии импортированной конфигурации с каноном: он способен её перезаписать.
- Найдено 16 agent TOML, 40 shared/imported skills в `~/.agents/skills`, 37 skills в `~/.claude/skills`; plugin cache содержит bundled, primary runtime, curated remote и imported Claude plugin roots.
- Полный release не доказан. Предыдущие profile, GUI и hook smoke имеют только свои узкие claims.

## Текущие ограничения

- Нет разрешения на write-операции в реальных проектах, login, установку пакетов или платные вызовы.
- Для runtime допускаются только read-only handshake/health-check без передачи пользовательских данных; остановиться перед login, платным действием или изменением внешней системы.
- Не изменять `codex-layer/AGENTS.codex.md` и `codex-layer/mcp-whitelist.json`: это user-owned dirty.

## Выполняемые read-only исследования

- `/root/skills_inventory`: инвентаризация skills, дублей и исполнимых маршрутов.
- `/root/agents_inventory`: сверка 16 agent TOML, ролей и sandbox-границ.
- `/root/mcp_inventory2`: reconciliation импортированных MCP/plugins с каноном.
- `/root/release_matrix`: прежние evidence и открытые release-gates.

## Следующий шаг

1. Получить отчёты четырёх исследователей и собрать единый acceptance matrix: компонент, источник, статическая проверка, безопасная runtime-проверка, статус, blocker.
2. Выполнить только безопасные local/read-only проверки по этой матрице; отдельные внешние/hardware сервисы помечать BLOCKED, если требуют login, расхода квоты или живого приложения.
3. Выделить подтверждённые конфликты импорта с каноном. До решения владельца не синхронизировать и не перезаписывать конфигурацию.
4. Перед любым claim PASS дать матрицу независимому auditor.

## Prompt for the new chat

> Продолжение audit после native import Claude Code в Codex. Цель: проверить все skills, agents, MCP и plugins на фактическую работоспособность и согласованность с Codex. Начни с `~/.claude/session-reports/2026-07-18_codex-native-import-audit/report.md`, но читай только нужные разделы. Получи результаты активных read-only исследователей, собери acceptance matrix и запускай только safe read-only local/runtime проверки. Не запускай `codex_sync.py sync`: текущий `check` = exit 2 `canon-newer config.toml#managed`, импорт может быть затёрт. Не меняй user-owned `codex-layer/AGENTS.codex.md` и `codex-layer/mcp-whitelist.json`. Не объявляй full PASS до независимого аудита всей матрицы.

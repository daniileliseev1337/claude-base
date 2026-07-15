# Epic 3.1 — Codex import и domain MCP smoke

## Цель

Проверить актуальное поведение Codex при импорте Claude-среды и при работе
`Revit-Connector`/`autocad-mcp` на общем config host Desktop, CLI и IDE.

## Подтверждённые факты

- Codex import обнаруживает поддерживаемые user-level и project-level setup.
- Import переносит instruction files, skills, plugins, MCP configuration, hooks и subagents.
- Desktop, CLI и IDE extension используют MCP configuration одного Codex host.
- Текущий bridge рендерит domain MCP с `required = false` и
  `startup_timeout_sec = 60`.

## Неподтверждённые утверждения

- Один domain MCP гарантированно валит Desktop Codex.
- Для domain MCP отсутствует lazy-start.
- Импортированная конфигурация автоматически означает готовый runtime server.

## Сценарий smoke

Выполняй на машине с живыми Revit и AutoCAD. Сохраняй версию Codex, поверхность
(`CLI`/`IDE`/`Desktop`), конфигурацию сервера, результат старта и первого tool call.

1. Запусти import Claude setup с выборочным импортом MCP и subagents.
2. В каждой поверхности проверь список server state до включения.
3. Включи только один сервер через `codex_sync.py mcp on <server>`; сохрани
   сгенерированный конфиг с `required = false`.
4. Перезапусти только текущую поверхность и зафиксируй, пережил ли запуск server.
5. Выполни один read-only tool call к живому host: Revit status/model info либо
   AutoCAD drawing info.
6. Повтори для второго сервера и затем обоих одновременно.
7. Выключи bridge, перезапусти поверхность и проверь отсутствие ручного drift.

## Критерий решения

- При успешном старте и tool call пометь capability provider `live` и уточни
  policy default/on-demand по измеренной стоимости старта.
- При сбое сохрани точный лог, surface, server и шаг; формулируй ограничение
  только для подтверждённой комбинации.
- Не подменяй отсутствие import/runtime proof утверждением о глобальной
  нестабильности MCP.

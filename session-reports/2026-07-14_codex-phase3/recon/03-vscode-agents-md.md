# Разведка 3: VS Code + AGENTS.md (третий таргет генератора)

Дата: 2026-07-14 · Агент: sonnet · Статус: завершено

## Матрица «инструмент × AGENTS.md»
| Инструмент | Читает AGENTS.md? | Путь | Настройка | Уровень |
|---|---|---|---|---|
| VS Code Copilot Chat (agent mode) | Да | корень workspace (+подпапки эксперим.) | `chat.useAgentsMdFile` (**default true**), `chat.useNestedAgentsMdFiles` (false) | репо; user-level НЕТ |
| VS Code Copilot — CLAUDE.md | Да, отдельно | workspace, `.claude/`, `~/.claude/CLAUDE.md` | `chat.useClaudeMdFile` | репо + глобал |
| Copilot `.github/copilot-instructions.md` | своё | `.github/` | `github.copilot.chat.codeGeneration.useInstructionFiles` (true) | репо, always-on |
| Copilot `.instructions.md` | своё, glob `applyTo` | `.github/instructions/` или `~/.copilot/instructions` | `chat.instructionsFilesLocations` | оба |
| GitHub Copilot coding agent (облачный) | Да | AGENTS.md по дереву репо, ближайший побеждает | включено с релиза 2025-08 | репо |
| OpenAI Codex VS Code extension | Да | тот же движок что CLI: `~/.codex/config.toml` + AGENTS.md | — | оба |
| Continue.dev | **Нет** (issue #6716 открыт) | — | — | — |
| Cursor | Да, нативно | корень + подпапки | из коробки | репо |
| Gemini CLI | Да | `~/.gemini/GEMINI.md` + по дереву | `context.fileName` принимает массив `["AGENTS.md",...]` | оба |

Приоритет Copilot: personal (user) > repository > organization.

**Критичный нюанс:** `chat.useClaudeMdFile` читает `~/.claude/CLAUDE.md` как plain markdown и **НЕ разворачивает `@import`** — наш CLAUDE.md с `@~/.claude/core/AGENTS.core.md` даст Copilot строку «@...» вместо ядра. Канал мёртв без плоской генерации.

## MCP в VS Code
- Формат `mcp.json`: `{"servers": {"<id>": {"type":"stdio","command":...,"args":...}}, "inputs":[...]}` — почти 1:1 наш mcpServers.
- Workspace: `.vscode/mcp.json`; user: команда «MCP: Open User Configuration» (~`%APPDATA%\Code\User\mcp.json`, путь из вторичных источников); CLI: `code --add-mcp "{...}"`.
- **VS Code умеет автообнаруживать серверы из Claude Desktop** — проверить на машине до написания конвертера (может быть 0 усилий).

## Аналоги скиллов/агентов
- Custom agents `.agent.md` (бывш. `.chatmode.md`): frontmatter tools/model/handoffs; `.github/agents` (workspace) или `~/.copilot/agents` (user), настройка `chat.agentFilesLocations`. Есть непроверенный намёк, что видит и `.claude/agents` «Claude format» — проверить руками до генератора.
- Prompt files `.prompt.md` (`.github/prompts`) — аналог вызываемого скилла (слэш-команда).
- Instructions files `.instructions.md` (applyTo-glob) — триггер по типу файла, без tools-слоя.
- Трёхслойного скилла (when+how+tools) нет — три раздельных примитива.

## Рекомендация для генератора
1. **Главный ход:** класть плоский (развёрнутый, без @import) AGENTS.md в корень каждого рабочего проекта → разом покрывает Codex CLI/extension, Copilot agent mode (default on!), Cursor, Gemini CLI. 4 таргета одним файлом.
2. Не полагаться на `chat.useClaudeMdFile` (нерезолвящийся @import).
3. MCP: сначала проверить автообнаружение из Claude Desktop; иначе конвертер manifest→servers тривиален.
4. Скиллы/агенты: не генерить автоматически — сначала ручная проверка одного тестового `.agent.md` в живом VS Code.
5. Codex extension отдельного таргета не требует (готов через ~/.codex).
6. Continue.dev — отдельный формат `.continue/rules/*.md`, низкий приоритет.

## Источники (проверены 2026-07-14)
code.visualstudio.com/docs/agent-customization/{custom-instructions,custom-agents,prompt-files,mcp-servers}; docs/agents/reference/{ai-settings,mcp-configuration}; api/extension-guides/ai/mcp (автообнаружение); docs.github.com copilot custom instructions; github.blog changelog 2025-08-28 (coding agent AGENTS.md); community.openai.com (Codex IDE extension); docs.continue.dev/rules + continuedev/continue#6716; cursor.com/docs/rules; geminicli.com/docs/cli/gemini-md.
Непроверенное: точный Windows-путь user mcp.json; `.claude/agents` в VS Code; sandbox-секция mcp.json; механизм Cursor User Rules.

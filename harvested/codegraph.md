---
name: codegraph
source: https://github.com/colbymchenry/codegraph
npm: npx @colbymchenry/codegraph
license: MIT
stars: 15500
last_release: v0.9.3 (May 2026)
status: active
harvested_at: 2026-05-22
applies_to: code projects (не методическая база, не документы)
---

# CodeGraph — AI-Powered Code Intelligence

## Что это

Pre-indexed semantic knowledge graph для codebases, **специально для AI агентов** (Claude Code, Cursor, Codex, OpenCode). Заменяет file-scanning operations graph queries'ами.

## Ключевые цифры

- **35% дешевле** (по их бенчмаркам)
- **70% меньше tool calls** на типичных задачах
- 19+ языков: TS/JS, Python, Rust, Java, Go, C/C++, …
- 14+ web frameworks с framework-aware routing detection
- 15.5k stars, MIT, активный maintenance

## Архитектура

- SQLite + FTS5 (full-text search)
- tree-sitter для AST parsing
- Native OS file events для auto-sync
- **Полностью локально** — no external services, API keys, data transmission
- Respects `.gitignore`, skips files >1 MB

## Installation (Windows)

Standalone binary через PowerShell (не требует Node.js):
```powershell
# Конкретная команда есть в README на github.com/colbymchenry/codegraph
# Также можно через npm если он установлен: npx @colbymchenry/codegraph
```

## Capabilities

- Full-text search across codebase
- Impact analysis for code changes
- Call-graph tracing
- Framework-aware routing detection

## Применимость к нашим задачам

| Сценарий | Подходит | Почему |
|---|---|---|
| `~/.claude/` методика (skills/agents/chains) | НЕТ | малый объём, Claude и так быстро обходит |
| Рабочие документы (DOCX/PDF/XLSX) | НЕТ | не индексирует не-код |
| BIM2B Revit plugin (C#/F# code) | ДА | целевой use case |
| AutoLISP большой проект | ВОЗМОЖНО | tree-sitter поддерживает lisp grammar |
| Python библиотеки (включая mcp-servers) | ДА | Python в supported languages |

## Когда подключать (триггеры)

- Работаем с code-проектом > 50 файлов где Claude часто spawn'ит sub-agent для exploration
- Появился новый repo (например BIM-плагин) и Claude ищет одну функцию через 10+ Read'ов
- Хотим срезать API costs на длинных code-сессиях

## НЕ подключать

- Документация / шаблоны / спецификации (не код)
- Кратковременные one-off скрипты
- Если codebase < 20 файлов — оверкилл

## Безопасность

- Локально → нет credentials risk
- MIT → нет лицензионных конфликтов
- Standalone binary → нет глубоких pip/npm зависимостей
- Не клонировали в `_sandbox/` (не тестировали в этой сессии, только research)

## Next step если решим использовать

1. На целевом ПК с code-проектом: запустить установку.
2. `codegraph index` в корне проекта → создаст граф.
3. Запустить Claude Code — он автоматически увидит граф через MCP integration? Проверить как именно интегрируется (MCP server? local-only query API?).
4. Замерить — было vs стало (количество tool calls на типичной задаче).

## Ссылки

- GitHub: https://github.com/colbymchenry/codegraph
- NPM: https://www.npmjs.com/package/@colbymchenry/codegraph

# Разведка 4: оркестрация Claude Code ↔ Codex

Дата: 2026-07-14 · Агент: sonnet · Статус: завершено

## Локальные факты
- Standalone `codex` НЕ в PATH; бинарник внутри десктоп-установки: `%LOCALAPPDATA%\OpenAI\Codex\bin\<hash>\codex.exe`, версия **codex-cli 0.144.2** (путь виден в config.toml как CODEX_CLI_PATH). Для оркестрации — полный путь или алиас.
- `codex login status` → **Logged in using ChatGPT** (без API-ключа) — headless работает под подпиской.
- Claude Code 2.1.114: `claude -p` (--output-format json/stream-json, --json-schema, --resume/--fork-session, --allowedTools, --mcp-config, --max-budget-usd) и `claude mcp serve` — подтверждены `--help`.

## Матрица механизмов
| Направление | Механизм | Статус | Заметки |
|---|---|---|---|
| Claude→Codex | `codex exec [PROMPT]` | подтверждён локально | `-m`, `-s {read-only,workspace-write,danger-full-access}`, `-C`, `--add-dir`, `--json` (JSONL событий), `-o/--output-last-message FILE`, `--output-schema FILE` (JSON Schema финалки!), `--ephemeral`, `-p/--profile`. Квота — общий пул подписки (гипотеза, живьём не проверено). |
| Claude→Codex | `codex exec resume [ID\|--last]` | подтверждён | продолжение сессии headless |
| Claude→Codex | **openai/codex-plugin-cc** (официальный плагин Claude Code от OpenAI, 28.5k★) | подтверждён (репо+README) | НЕ MCP — дёргает локальный codex/app-server. `/plugin marketplace add openai/codex-plugin-cc` → `/plugin install codex@openai-codex` → `/codex:setup`. Команды: /codex:review, /codex:adversarial-review, /codex:rescue, /codex:transfer, /codex:status, /codex:result, /codex:cancel; флаги --background/--wait. Требует Node ≥18.18. |
| Codex→Claude | `claude -p "..." --output-format json` | подтверждён | симметричный сабпроцесс |
| Codex как MCP-сервер | `codex mcp-server` | команда подтверждена локально | tools `codex` + `codex-reply` (threadId) — полный список параметров не проверен (нужен live-дамп) |
| Claude как MCP-сервер | `claude mcp serve` | команда подтверждена | подключение из Codex: `codex mcp add claude -- claude mcp serve` (по аналогии, не тестировано) |

## Рекомендованная архитектура (П4)
- Стартовать с **direct-exec моста** (`codex exec` / `claude -p`) — оба подтверждены, ноль стороннего кода, детерминированный парсинг (`--json`, `--output-schema`). Deterministic-first.
- Официальный плагин codex-plugin-cc — кандидат второй очереди (готовые ревью-команды, adversarial-review = наш паттерн совета судей).
- MCP-путь (mcp-server/serve) — третьим шагом, когда нужна persistent двусторонняя сессия.

## Эстафета сессий
- Codex-сессии: `~/.codex/sessions/<YYYY>/<MM>/<DD>/rollout-<ts>-<uuid>.jsonl` + `session_index.jsonl` (реальные файлы прочитаны; session_meta: session_id, cwd, originator, cli_version, base_instructions).
- `codex resume <id>` / `--last`, `codex fork <id>` — только внутри Codex.
- **Кросс-вендорной эстафеты из коробки НЕТ** (форматы несовместимы). Практичный путь: markdown-handoff-пакет (наш скилл handoff-to-new-chat) → файл в cwd → `codex exec -C <dir> "<промпт со ссылкой на handoff.md>"`.

## Риски
1. Windows sandbox: нативный Windows = elevated/unelevated (Linux-sandbox только под WSL2); вызов codex из Claude — плоский сабпроцесс, двойной изоляции нет.
2. Одновременный доступ к файлам двух агентов — гонки; дисциплина или git worktree.
3. Квота: `codex exec` жжёт тот же пул 5ч/неделя (гипотеза по данным сообщества — проверить на живом прогоне).
4. **Кодировка Windows подтверждена как ловушка:** UTF-8 JSONL читается PowerShell'ом как мешанина без chcp 65001/-Encoding utf8 — весь обмен промптами/выводом с кириллицей форсировать UTF-8.
5. hooks в `codex exec` (другой code-path, не GUI) — возможно исполняются иначе, чем в десктопе; не проверено, нужен живой тест.

## Источники
Локально: codex.exe --version/--help/exec --help/mcp-server --help/login status; claude --help/mcp serve --help; ~/.codex/sessions/*, session_index.jsonl, config.toml.
Веб: github.com/openai/codex-plugin-cc; openai/codex discussions #16329 (Awesome Codex); beagleworks.github.io/ccclog (codex/codex-reply tools); learn.chatgpt.com/docs/llms-full.txt (Windows/WSL2 sandbox); экосистемные репо (claude-codex, mco, codex-subagents-mcp и др. — существование проверено GitHub API).
Не проверено живьём (лимит берегли): параметры tools mcp-server, поведение claude mcp serve, hooks в exec-режиме.

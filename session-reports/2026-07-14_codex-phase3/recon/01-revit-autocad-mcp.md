# Разведка 1: Revit/AutoCAD MCP под Codex — корень падения

Дата: 2026-07-14 · Агент: sonnet · Статус: завершено

## Как запускаются сейчас (факты)
- Источник истины — `~/.claude.json` (mcpServers), в Codex пробрасывается генератором `codex_sync.py` (только whitelist, сейчас `time` — доменные MCP в `~/.codex/config.toml` вообще отсутствуют).
- `autocad-mcp`: `command = "<venv>/Scripts/python.exe"`, `args = ["-m","autocad_mcp"]` — прямой python, **без uv при старте**.
- `Revit-Connector`: `command = "uv"`, `args = ["run","--with","mcp[cli]","mcp","run","<путь к main.py>"]` — uv участвует при каждом старте.
- В `main.py` Revit-Connector кода `sys.exit(1)` при отсутствии живого Revit НЕ найдено — факт «exit 1» статическим чтением не подтверждён (возможно, другой механизм или иная версия).

## Диагноз (по уверенности)
1. **Главный подозреваемый — CRLF-баг официального Python MCP SDK на Windows** (подтверждено кодом): `mcp/server/stdio.py` создаёт `TextIOWrapper(sys.stdout.buffer, encoding="utf-8")` **без `newline=""`** → каждое JSON-RPC сообщение уходит с `\r\n`. Баг modelcontextprotocol/python-sdk#2433 (открыт с 2026-04, серия PR не влита — проверено на релизе mcp 1.28.0). Rust-клиент Codex (rmcp) парсит строго по `\n`, `\r` не отрезает → рукопожатие падает (`openai/codex#29247`, Windows, versions 0.141-0.142). Клиент Claude Code (TS) trailing `\r` терпит — поэтому под Claude работает. Node-серверы у Codex живут (наш node_repl — живой).
2. **«Кириллица пути» — вероятно смещённый диагноз** для текущей конфигурации: реальные uv-баги с нелатинскими путями есть (astral-sh/uv#19457 — console-script шим декодирует shebang через CP_ACP; #12622 — .pth), но бьют по сценариям с uv-шимом/`uv run` над проектом. autocad-mcp спавнится прямым python.exe без uv. Для Revit-Connector (uv run) оба класса рисков актуальны. ANSI-vs-UTF8 рассинхрон на машине реален (воспроизведён в bash: `C:\Users\??????\`). ASCII-путь — дешёвая профилактика независимо от истинной причины.
3. **Падение одного MCP валит весь десктоп-Codex** — активный класс Windows-багов самого Codex, вопреки задокументированному `required=false` (default): openai/codex#16834 (crash on startup), #29321 и #21318 (MCP-старт блокирует thread/tools). Lazy-старт MCP по вызову тула НЕ существует как фича.

## Опции config.toml для MCP (подтверждено докой + Rust-исходником)
`enabled` (true) · `required` (false) · `startup_timeout_sec` (10) · `tool_timeout_sec` (60) · `enabled_tools`/`disabled_tools` · `cwd` · `env`/`env_vars`. Project-scoped `.codex/config.toml` — ближе всего к «мосту по требованию», но на Desktop иногда не подхватывается (#13025). Исторический баг урезанного env при спавне на Windows (#4180) похоже починен; надёжнее дублировать критичные переменные в `[mcp_servers.<name>.env]`.

## Фиксы по приоритету
1. Патч CRLF: локально `newline=""` в `stdio.py` (venv autocad-mcp + uv-кэш Revit-Connector) или ждать апстрим-фикс mcp SDK. Устраняет корень.
2. Дёшево сразу: `required = false` явно + `startup_timeout_sec` 30–60 для обоих при точечном включении в whitelist.
3. ASCII-обёртка `.bat` (chcp 65001 + UV_CACHE_DIR/UV_PYTHON_INSTALL_DIR/UV_TOOL_DIR на ASCII-путь) — страховка от кириллицы.
4. «Мост по требованию»: переключение config.toml между минимальным и доменным профилем (наш whitelist-механизм) — пока Codex не чинит #16834/#29321, единственный надёжный способ не ронять приложение. Project-scoped вариант тестировать именно на Desktop.
5. НЕ рассчитывать на lazy-MCP как фичу — её нет.

## Верификация гипотезы (шаг тест-заезда)
Включить оба MCP точечно с `required=false` + таймаут 60, живьём смотреть лог Codex: если `handshaking with MCP server failed: connection closed: initialize response` — CRLF-гипотеза подтверждена напрямую.

## Источники
Локальные: `~/.claude.json`, `~/.codex/config.toml`, `codex-layer/*`, `codex_sync.py`, `mcp-servers/revit-mcp-python/main.py`, `mcp-servers/autocad-mcp/.venv/.../mcp/server/stdio.py` (mcp==1.26.0).
Веб: learn.chatgpt.com/docs/extend/mcp; codex-rs config/types.rs; openai/codex#29247, #16834, #29321, #21318, #13025, #4180; modelcontextprotocol/python-sdk#2433 (+PR-серия, фикс не влит в 1.28.0); astral-sh/uv#19457, #12622, #11828.

Оговорка: поведение Codex не воспроизводилось живьём (лимит не жгли) — выводы по коду/докам/issues.

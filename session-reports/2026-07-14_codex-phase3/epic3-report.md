# Эпик 3 — Revit/AutoCAD MCP под Codex: отчёт сессии (2026-07-14/15, DANIILPC)

## Что сделано
Полный цикл: brainstorming (развилки владельца: верификация = смоук рукопожатия;
универсальный патчер; переключатель в codex_sync, не профили) → спека → план
(7 задач) → SDD-конвейер (sonnet-воркер + sonnet-ревьюер на задачу) → финальное
ревью ГОТОВ. Спека/план — в проекте Реворк базы
(`docs/superpowers/{specs,plans}/2026-07-14-epic3-revit-autocad-codex*`),
леджер — `~/.claude/.superpowers/sdd/progress.md` (секция ЭПИК 3).

Компоненты (коммиты 29f9e47..7074d71 + фиксы 4024678, 6101d82):
- `scripts/mcp_crlf_patch.py` — патчер CRLF-бага python-sdk#2433 (unknown-pattern
  не трогает файл; `--scan`/`--check`/`--from-overlay`).
- `scripts/mcp_handshake_smoke.py` — initialize по stdio + проверка LF-чистоты байт.
- Оверлей `.local-state/codex-mcp-overlay.json` + CLI `codex_sync.py mcp on|off|status`
  (bridge: required=false, startup_timeout_sec=60; атомарность; без ложного дрейфа).
- `codex-drift-check.ps1`: напоминание о включённом мосте + контроль патча.
- Revit-Connector: с `uv run --with mcp[cli]` на закреплённый venv
  (`~/.claude.json`, бэкап `~/.claude.json.bak-epic3`).
- Политика моста в `codex-layer/AGENTS.codex.md` + comment whitelist.

## Верификация (Done-when 1-5 закрыты)
- CRLF-диагноз живьём: ДО патча autocad-venv отвечал `\r\n` (smoke FAIL), ПОСЛЕ — LF.
- Под Codex CLI (0.144.2, exec + RUST_LOG debug): 5× «Service initialized as client»
  (в т.ч. Revit-Connector, autocad-mcp), 0× «handshaking failed», тулы перечислены.
- Десктоп Codex с включённым мостом стартует без ошибок (владелец; список MCP
  «Включено»). Раньше такой конфиг ронял приложение.
- Регресс под Claude: get_revit_status → healthy на новом venv-конфиге (финальный
  ревьюер, живой вызов). Тесты 65/65.

## Споткнулись / уроки
- `codex exec` при не-TTY stdin молча ждёт «additional input» до EOF → в скриптах
  запускать `Write-Output "" | codex exec ...`. Дважды выглядело как зависание.
- Ответ модели Codex «MCP-серверы не обнаружены» ≠ транспортная правда — проверять
  debug-логом rmcp, не словами модели.
- `requirements.txt` revit-mcp-python несовместим сам с собой (ResolutionImpossible);
  рабочий обход: чистый venv + `pip install "mcp[cli]==1.23.0"`.
- Наш `hooks.json` (рендер Э1) пишет `commandWindows` — Codex 0.144 ждёт `command`,
  warning на каждом exec. Приоритетный бэклог.
- Ревьюеры на задачу окупились: 2 Important поймано и закрыто фиксами (префикс
  ошибки CLI; типо-невалидный `enable` обходил fail-safe и мог уронить хук).

## Бэклог
Полный список — реестр в roadmap-доке проекта (раздел «Порядок выпуска») +
SDD-леджер. Дальше по карте: Эпик 4 (связка/оркестрация).

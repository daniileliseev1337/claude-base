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
2. Исторический пункт initial handoff, закрытый в последующей Reconciliation: release repository определён как `~/.claude`; generated `AGENTS.md` не является release-артефактом.
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

## Reconciliation — 2026-07-17 18:31 MSK

- Release-repository определён: `~/.claude` / `claude-base`. Project-specific
  `AGENTS.md` — generated output конкретного проекта; в release-repository раздаётся
  генератор. Для текущего проекта пункт закрыт как scope clarification.
- Текущая Codex Desktop-задача доказала live `SessionStart` и `PostToolUse`; задача
  того же дня содержит `Stop`. CLI и VS Code hook runtime отдельно не доказаны.
- Независимый backlog-аудит подтвердил 9 OPEN-пунктов Epic 1 Minor; у Epic 2/3
  остаются технические OPEN-хвосты.
- GUI-checklist нельзя автоматизировать доступным Windows UI skill: Codex extension
  исключён его safety policy. Требуется ручная проверка владельца.
- Текущий verdict выпуска: **NOT PASS**. Epic 1 safety-пакет, названный следующим
  code-инкрементом (`_write_atomic` cleanup, first-sync drift test, partial
  force-overwrite test, CLI docstring), закрыт ниже; 5 Minor Epic 1 остаются OPEN.
- Full evidence: `Claude/reports/2026-07-17-release-gate-reconciliation.md`.

## Epic 1 safety package — 2026-07-17

- Scope закрыт: cleanup `_write_atomic`, first-sync drift test, partial
  force-overwrite test и актуальный CLI docstring.
- Красная стадия: тесты docstring и cleanup воспроизвели дефекты; first-sync и
  partial force-overwrite подтвердили уже корректное поведение sync.
- Реализация: `_write_atomic` удаляет `.tmp-codex-sync` в `finally`; module docstring
  перечисляет `sync|check|diff|mcp`, `--dry-run` и `--force-overwrite KEY|all`.
- Верификация: 4/4 новых теста PASS; `test_codex_sync.py` + golden + capability =
  71/71 PASS; `git diff --check` и `py_compile` прошли.
- Свежий независимый auditor = **PASSED**: самостоятельно подтверждены 64/64
  `test_codex_sync.py` и 71/71 связанного набора, scope-выходов нет.
- Epic 1 Minor backlog: из 9 OPEN закрыты 4; остаются 5 — UTF-8 `Add-Content`,
  duplicate warn, роль manifest `inputs`, повторное чтение skills-manifest и
  устаревший canon-newer recipe.
- MCP/hooks/plugins не менялись; Word/PDF claims не расширялись; Epic 6 не начат.
- VS Code GUI-checklist, отдельные CLI/VS Code hook-smoke и daily soak остаются OPEN.
- Полный release verdict: **NOT PASS**.

## Epic 1–3 safety continuation — 2026-07-17

- `~/.claude` commit `2efaccd` закрывает автономные Minor Epic 1–2: UTF-8 cleanup log, один render/diagnostics, одно чтение skills-manifest, diagnostic provenance manifest `inputs`, точную base-table collision и safety skip auto-push при pre-existing staged index.
- Независимый повторный audit = **PASSED**: 78 Python tests, 7 targeted regressions, `git diff --check`, Python/PowerShell parse и изолированный реальный Git/PowerShell test подтверждают сохранность index и отсутствие auto-commit.
- Вложенный `revit-mcp-python` commit `597c566` фиксирует единый install-contract `mcp[cli]==1.23.0` в `requirements.txt`, `pyproject.toml`, `uv.lock`. Новый чистый venv прошёл install, `pip check`, import; после штатного CRLF patch `mcp_handshake_smoke.py` подтвердил LF-clean initialize.
- Не закрыты: orphan outputs Epic 2; overlay/parser/CLI/patcher хвосты Epic 3; GUI checklist, отдельные CLI/VS Code hook-smoke и daily soak. Выпуск остаётся **NOT PASS**; Epic 6 не начат.

## Epic 3 overlay/parser continuation — 2026-07-17

- Commit `8a20cfa` закрывает strict `mcp` action validation, ghost/inactive `off`, effective allow dedup, atomic validated overlay write и CLI argparse regressions. Independent audit = PASSED.
- Commit `9f36f34` вводит единый parser overlay для `codex_sync.py`, `mcp_crlf_patch.py` и `codex-drift-check.ps1`; `--from-overlay` различает clean `0`, patch failure `1` и input error `2`.
- Первый audit пакета B = NOT PASSED: malformed `.claude.json` выбрасывал `AttributeError`. Четыре red-regressions воспроизвели этот defect; после validation root/server types финальный fresh audit = PASSED.
- Final evidence: `python -m pytest scripts/tests -q` = 112 PASS; Python compile, PowerShell ParseFile и `git diff --check` = PASS. Оба коммита pushed в `origin/main`; user-owned dirty `codex-layer/AGENTS.codex.md` и `codex-layer/mcp-whitelist.json` не staged.
- Следующая fresh задача: не начинать Epic 6. Выполнить только ручные/time gates (VS Code GUI checklist, отдельные CLI и VS Code hook-smoke, daily soak) при доступности owner-visible среды; orphan-output policy Epic 2 требует решения владельца. Full release остаётся **NOT PASS**.

## Fresh LITE prompt — 2026-07-17

> Продолжение release-gate Codex. Экономь контекст: сначала прочитай только верх `Claude/CLAUDE.md`, `Claude/STATUS.md`, `0_СТАТУС_программы.md` и нужную секцию этого отчёта.
>
> Цель: удержать строгий release verdict и закрывать только доказуемые manual/time gates.
> Сделано: Epic 3 overlay/parser/CLI/patcher закрыт в `8a20cfa` и `9f36f34`, финальный independent audit PASSED, `scripts/tests` = 112 PASS.
> Следующий шаг: не начинать Epic 6; выполнить owner-visible VS Code GUI checklist, отдельные CLI и VS Code hook-smoke либо зафиксировать фактический blocker. Daily soak оставь NOT PASS, пока не появится требуемая длительность и чистые логи.
> Границы: не отключай MCP/hooks/plugins/пользовательские сессии; не меняй Word/PDF claims; не stage/revert user-owned `codex-layer/AGENTS.codex.md` и `codex-layer/mcp-whitelist.json`; Revit external origin не push без owner authorization.
>
> Детали — в этом `report.md`; используй cascade loading по заголовкам, не читай историю целиком.

# Handoff LITE — Codex context governor и Эпик 4b

## TL;DR
- Bootstrap Claude-проектов для Codex закрыт: content-based `AGENTS.md`, защита ручных файлов и атомарная запись.
- Владелец установил ранний порог handoff около 190k; текущая задача уже показывает 203k, поэтому продолжать в новом чате.
- Перед handoff всегда актуализировать ядро проекта: `Claude/STATUS.md`, верх журнала и при необходимости этот report.
- Следующий инкремент: context governor для Codex, затем capability registry/adapters/TOOL_MAP; Эпик 5 не начинать.

## Состояние артефактов
- Канон кода: `~/.claude`; незакоммичены шесть файлов bootstrap-инкремента:
  `codex-layer/AGENTS.codex.md`, `skills/project-memory/SKILL.md`,
  `skills/project-memory/tools/gen_project_agents.py`, его hook и два тестовых файла.
- В проекте обновлены `Claude/ЖУРНАЛ СЕССИЙ.md`, `Claude/STATUS.md`,
  `0_СТАТУС_программы.md`, roadmap и
  `docs/superpowers/specs/2026-07-15-epic4b-capability-boundaries.md`.
- Последняя полная проверка bootstrap: 166 passed; независимый auditor PASSED.
- `git -C ~/.claude log origin/main..main --oneline` пуст; коммит и push не выполнялись.
- Новый runtime drift `~/.codex/config.toml`: Codex App добавил доверенные hashes
  `[hooks.state]` и `[memories]`. Не запускать `sync --force-overwrite` до решения,
  как сохранять эти runtime-секции при managed sync.

## Решения владельца
- Порог раннего handoff: около 190k для окна около 258k; 230k считать аварийной зоной.
- Перед созданием нового чата закрывать текущий безопасный шаг и обновлять ядро проекта.
- Предпочитать handoff новой задаче перед поздней compaction для сложной технической работы.
- Terra-субагенты уже наследуют `model_reasoning_effort = "high"` из `~/.codex/config.toml`.

## Блокеры и риски
- Живой Codex→Claude smoke по-прежнему блокирует внешний `403 organization access`.
- Документация Codex описывает `PreCompact`/`PostCompact`, но hook payload не содержит реальную цифру токенов. Не считать размер транскрипта заменой счётчика.
- До реализаций провести live-smoke hooks в текущем Codex App: появление `[hooks.state]` — сильный сигнал, что прежний диагноз «desktop hooks мертвы» мог устареть.

## Update: context governor implementation
- В runtime установлен `model_auto_compact_token_limit = 190000` со scope `total`.
  Это авторитетный threshold event; числовой счётчик из hook payload не доступен.
- `PreCompact` и `PostCompact` с matcher `auto` добавлены в `hooks.json`. Первый
  останавливает компакцию и требует STATUS → журнал → report → LITE-handoff;
  второй сохраняет диагностический state. Транскрипт не парсится для порога.
- `codex_sync.py` теперь выносит runtime `[hooks.state]` и `[memories]` за
  managed-блок; обычный sync сохранил текущие значения, `check` clean.
- Проверки: 80 Python-тестов, golden snapshot, synthetic hook-contract и
  runtime migration PASS. Независимый auditor не принял Done when без прямого
  исполнения compact hooks в App.

## Update: прямой native smoke и live PreCompact
- В Desktop App disposable-задача с временным `model_auto_compact_token_limit = 1`
  показала автоматическое сжатие; после trust обоих hook state зафиксировал реальный
  `PreCompact` для Desktop session `019f655f-3daf-72c1-9837-d49acb89d863`.
- `continue:false` у `PreCompact` останавливает compaction, но не текущий turn. Это
  поддерживаемая семантика common hook output: хук не создаёт задачу и не редактирует
  ядро проекта. Hook не создаёт задачу сам, но передаёт сигнал основному агенту; после
  безопасного шага агент автоматически создаёт новую задачу с LITE-prompt. Пользователь не
  выполняет перенос вручную.
- State хранит LITE-prompt: STATUS → верх журнала → session-report → новая задача.
  `PostCompact` не появляется после отменённого PreCompact; это ожидаемо, а не провал.
- Рабочий `190000`/`total` и runtime `[hooks.state]`/`[memories]` сохранены. Contract
  governor PASS, полный Python-набор — 80 PASS. Независимый final auditor PASS.
  Отдельный `config.toml#managed` drift — отсутствующий канонический time MCP — не перезаписан.
- Независимый read-only audit после smoke: PASS по корректности этой границы
  (threshold `190000`/`total`, runtime-секции и оба hook-определения на месте,
  state-файлов нет). Полный Done when не закрыт.

## Update: automatic agent handoff
- Владелец подтвердил целевой сценарий: после `PreCompact` основной агент сам создаёт новую
  project-задачу с LITE-prompt; пользователь не переносит работу вручную.
- `PreCompact` остаётся источником сигнала, а не UI-автоматизацией: hook сохраняет state и
  останавливает compaction; агент после безопасного шага обновляет STATUS, журнал и report,
  затем вызывает штатное создание задачи.
- Контрактное сообщение и PowerShell-тест уточнены; `test-codex-context-governor.ps1` PASS,
  полный Python-набор — 80 PASS. Независимый read-only audit PASS: утверждение допустимо
  только как automatic agent handoff, не как создание задачи самим hook.

## Update: capability registry
- Добавлены `codex-layer/capability-registry.json` и schema: 16 capabilities, 16 role adapters
  (7 RO/9 RW) и 37 skill adapters; manifest сохраняет прежние 11 enabled / 26 skipped.
- `codex_sync.py` валидирует schema и связи, включает registry в input hashes и заменяет raw MCP
  только определёнными capability IDs. 16 сгенерированных TOML не содержат `mcp__*`; Revit
  остаётся on-demand/blocked, не включён по умолчанию.
- 80 Python PASS. Независимый audit: инкремент PASS по составу, но полный Done when BLOCKED
  старым `manual-drift config.toml#managed`: в Desktop отсутствует канонический MCP `time`.
  Runtime `[hooks.state]`/`[memories]` не затёрты; решение об MCP оставлено владельцу.

## Update: final gate passed
- Владелец выбрал удалить неиспользуемый `time`: он удалён из канонического whitelist и
  фактического `~/.codex/config.toml`. Runtime `[hooks.state]`, `[memories]` и системный
  `node_repl` сохранены.
- Повторный независимый audit PASS: TOML разбирается, `codex_sync.py check` завершён с code 0.
- Epic 4b закрыт: governor automatic agent handoff и capability registry готовы; Epic 5 не начат.

## Update: reopened after observed PreCompact deadlock

- Desktop `PreCompact` fired at `2026-07-15T17:45:25+03:00` for the project task and wrote
  a LITE handoff state. It also exposed a contract defect: `continue:false` ended the hook run
  before the main agent could create the next task.
- Governor now returns `continue:true`: it persists the same state, permits native compaction,
  and tells the main agent to update project state and create the LITE task. PowerShell contract PASS.
- Capability registry strict gates now pass: 18 capabilities, 16 roles (7 RO/9 RW), 37 skills
  (11 enabled/26 skipped), full adapter rendering, 86 Python PASS and `codex_sync.py check` code 0.
- Epic 4b is not closed until a disposable native E2E records a child task ID, delivered LITE
  prompt, child acknowledgement, restoration of `190000`/`total`, and final independent audit.

## Update: native handoff after threshold restoration

- Fresh native `PreCompact` state was recorded at `2026-07-15T18:16:06+03:00` for
  session `019f655f-3daf-72c1-9837-d49acb89d863`; it contains `handoff_required: true`
  and the canonical LITE prompt. The governor now permits compaction with `continue:true`.
- Runtime verification: `model_auto_compact_token_limit = 190000`, scope `total`,
  `[hooks.state]` and `[memories]` remain present, and `time` is absent.
- A same-directory fork created child task `019f665e-5480-79e0-8598-1efd6e0ae0cc` and
  accepted the LITE prompt. The source active turn was marked interrupted by the app.
- Verification rerun: governor contract PASS, `86 passed` for the Python suite,
  and `codex_sync.py check` exited 0 (one pre-existing informational unnamed-agent warning).
- The child acknowledgement is still queued in the Codex App at this snapshot; do not claim
  final Epic 4b closure until it is observed and the independent auditor returns PASS.

## Update: fresh task is the required handoff path

- The same-directory `/fork` path is rejected for handoff: it copies completed history, so its
  child immediately compacted. It is not evidence of a clean context transition.
- A fresh project task on explicit `gpt-5.6-terra` was created as
  `019f6667-7676-7391-9fbb-a31ddbbca342`. It received the LITE prompt and returned
  `ACK-FRESH-TERRA` without auto-compaction.
- A previous fresh task let the app auto-select `gpt-5.3-codex-spark` and failed before reply
  because that model rejected `reasoning.summary`; this is an app/model compatibility error,
  not a context-governor signal. Pin a compatible model for automated fresh handoff.
- Canonical contract: persist state, continue native compaction, create a **fresh project task**
  with the LITE prompt and an explicit compatible model. Do not use `/fork`.

## Reconciliation: current Epic 4b source of truth

- This section supersedes the historical `final gate passed`, queued fork-child, and partial
  auditor PASS entries above. They remain evidence of their local checks only.
- The only canonical E2E child is fresh Terra task `019f6667-7676-7391-9fbb-a31ddbbca342`.
  Its first response is `ACK-FRESH-TERRA`; it did not auto-compact.
- Fork child `019f665e-5480-79e0-8598-1efd6e0ae0cc` and its queued ACK are invalid for E2E
  acceptance because fork inherited the source history.
- An independent audit returned NOT PASS solely because these historical records were not yet
  reconciled. Re-run that read-only audit against this section before closing Epic 4b.

## Следующий шаг
1. При PreCompact выполнить LITE-prompt из state: обновить STATUS, верх журнала и report.
2. Создать новую задачу и продолжить только зафиксированный безопасный следующий шаг.
3. Перейти к capability registry, adapters и TOOL_MAP; Эпик 5 не начинать.

## Промпт для нового чата
> Продолжение программы «Реворк базы». Контекст прошлой задачи достиг 203k при согласованном пороге handoff ~190k; экономь окно с первого шага.
>
> Цель: закрыть прямой App smoke context governor, затем перейти к capability registry, semantic adapters 16 ролей/skills и TOOL_MAP. Не начинать Эпик 5.
>
> Сделано: bootstrap закрыт (166 тестов, auditor PASSED); governor установлен на 190k, Pre/PostCompact(auto) развёрнуты, runtime state сохранён, 80 Python-тестов и hook-contract PASS. Границы registry зафиксированы в `docs/superpowers/specs/2026-07-15-epic4b-capability-boundaries.md`.
>
> Перед работой прочитай `Claude/CLAUDE.md`, верх `Claude/ЖУРНАЛ СЕССИЙ.md`, `Claude/STATUS.md`, верх `0_СТАТУС_программы.md`, затем этот report. Не читай report целиком повторно: сначала `rg -n "^##"`, потом только нужные секции.
>
> Важные факты: владелец выбрал порог ~190k для окна ~258k; перед handoff обновлять STATUS/журнал/report. `codex_sync.py check` clean: `[hooks.state]` и `[memories]` перенесены за managed-блок. Числового hook-счётчика нет; авторитетен native threshold event, не транскрипт.
>
> Ближайший Done when: после reload/restart доверены Pre/PostCompact; disposable auto-compaction записывает state JSON и показывает PreCompact handoff. Только затем начинать registry/adapters/TOOL_MAP.

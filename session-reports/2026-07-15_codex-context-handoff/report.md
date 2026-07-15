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

## Update: прямой native smoke и открытый runtime-разрыв
- В Desktop App disposable-задача с временным `model_auto_compact_token_limit = 1`
  показала автоматическое сжатие контекста после каждого действия. Это подтверждает,
  что App применяет native threshold; после теста значение восстановлено точно на
  `190000`, scope остаётся `total`.
- `~/.codex/config.toml` после возврата сохраняет `[hooks.state]` и `[memories]`.
- `~/.codex/hooks.json` содержит оба compact-hook с matcher `auto`, но каталог
  `.claude/.local-state/codex-context-governor/` не получил state JSON и в UI нет
  сообщения PreCompact. Поэтому live execution `PreCompact(auto)`/`PostCompact(auto)`
  не подтверждено; текущая реализация не даёт право утверждать, что handoff остановит
  compaction. Нужны диагностика Desktop App или поддерживаемая альтернатива, затем
  повторный smoke и независимый auditor.
- Независимый read-only audit после smoke: PASS по корректности этой границы
  (threshold `190000`/`total`, runtime-секции и оба hook-определения на месте,
  state-файлов нет). Полный Done when не закрыт.

## Следующий шаг
1. Считать native threshold проверенным, а execution compact-hooks — нет.
2. Выяснить по диагностике Desktop App или официальной документации, поддерживает ли
   текущая сборка именно `PreCompact`/`PostCompact`; не заменять это парсингом транскрипта.
3. После подтверждённого поддерживаемого механизма повторить smoke со state JSON и
   независимым auditor; только затем продолжить capability registry, adapters и TOOL_MAP.

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

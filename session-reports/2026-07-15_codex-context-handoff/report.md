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

## Прямой App smoke: обязательный следующий шаг
1. Перезагрузи Codex App или открой `/hooks`, проверь и доверь `PreCompact` и `PostCompact`.
2. Для disposable задачи временно поставь `model_auto_compact_token_limit = 1`,
   перезагрузи App и отправь два коротких сообщения; затем верни значение `190000`.
3. Подтверди state JSON в `.claude/.local-state/codex-context-governor/` и видимое
   сообщение `PreCompact`; проверь, что компакция не обошла handoff.
4. После PASS продолжи capability registry, adapters 16 ролей/skills и TOOL_MAP.

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

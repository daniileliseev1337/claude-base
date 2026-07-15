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

## Промпт для нового чата
> Продолжение программы «Реворк базы». Контекст прошлой задачи достиг 203k при согласованном пороге handoff ~190k; экономь окно с первого шага.
>
> Цель: реализовать следующий инкремент Эпика 4b — надёжный Codex context governor и handoff в новую задачу; затем вернуться к capability registry, semantic adapters 16 ролей/skills и TOOL_MAP. Не начинать Эпик 5.
>
> Сделано: project bootstrap `CLAUDE.md → AGENTS.md` закрыт (166 тестов, auditor PASSED); границы registry зафиксированы в `docs/superpowers/specs/2026-07-15-epic4b-capability-boundaries.md`.
>
> Перед работой прочитай `Claude/CLAUDE.md`, верх `Claude/ЖУРНАЛ СЕССИЙ.md`, `Claude/STATUS.md`, верх `0_СТАТУС_программы.md`, затем этот report. Не читай report целиком повторно: сначала `rg -n "^##"`, потом только нужные секции.
>
> Важные факты: владелец выбрал порог ~190k для окна ~258k; перед handoff обновлять STATUS/журнал/report; текущий `codex_sync.py check` показывает manual-drift `config.toml#managed`, потому что Codex App добавил `[hooks.state]` и `[memories]`. Не перезаписывай их силой. Проверь, действительно ли текущий Codex App исполняет PreCompact/PostCompact hooks и можно ли получить авторитетный сигнал порога без парсинга транскрипта.
>
> Done when ближайшего инкремента: правила/конфиг задают ранний переход около 190k, handoff сначала фиксирует ядро проекта, новая задача получает LITE-prompt и ссылки на состояние, runtime config не затирается, есть live-smoke и независимый аудит.

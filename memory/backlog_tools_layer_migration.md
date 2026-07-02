---
name: backlog-tools-layer-migration
description: Список skills со скриптами в корне для инкрементальной миграции в tools/ по Правилу 2 (три слоя). НЕ массовый рефактор.
metadata:
  type: project
---

# Backlog: миграция скриптов skills в слой tools/

**Контекст:** 2026-06-01 приняты 4 правила skill-first (Anthropic),
см. skill `skill-development`. Правило 2 — три слоя, скрипты в `tools/`.
Аудит показал: 0 из 14 skills структурированы по трём слоям, скрипты лежат
в корне skill.

**Why:** не массовый рефактор сейчас (Karpathy #3 — не трогать рабочее без
причины, риск поломать пути в SKILL.md). Мигрировать инкрементально —
при следующем касании skill.

**How to apply:** когда правишь один из skills ниже по другой причине —
заодно перенеси его скрипты в `tools/`, обнови ссылки в SKILL.md, добавь
`examples/` если есть эталоны. По одному, с проверкой что не сломалось.

## Skills с кодом в корне (кандидаты на миграцию)
| Skill | Скриптов | Приоритет |
|---|---|---|
| cad-reader | 3 | при касании |
| image-text-replace | 2 | при касании (сложный pipeline — осторожно) |
| ~~pdf-helper~~ | — | ✓ закрыто 2026-07-02: скилл разрезан (Блок 3 реворка) — extraction-скрипты уехали в `doc-extract/tools/`, editing-остаток переименован в `pdf-edit` (кода в корне нет) |
| yandex-disk-uploader | 2 | при касании |
| spec-writer | 1 | при касании |
| upd-parser | 1 | при касании |

## Skills без кода (examples/ при доработке)
- domain-grilling — поведенческий, нет кода. Кандидат на `examples/`
  (эталонные диалоги грилинга) после теста.
- karpathy-guidelines, skill-development, chains-pattern, structured-artifacts,
  handoff-to-new-chat — методологические, examples/ опционально.

## Стандарт для НОВЫХ skills
Сразу заполнять три слоя (где применимо): SKILL.md + tools/ + examples/.
Источник стандарта — skill `skill-development`.

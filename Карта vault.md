---
created: 2026-05-18
updated: 2026-05-18
status: active
owner: Даниил
last-verified: 2026-05-18
tags: [мета, карта, индекс]
---

# Карта vault `~/.claude/`

Это базовый индекс для **Obsidian-режима** базы Claude. Сама база
работает как git-репозиторий (claude-base) и распространяется через
auto-sync на все ПК команды. Этот файл уйдёт в git (полезен всем),
но `.obsidian/` (настройки Obsidian) — per-machine, в `.gitignore`.

> [!info] Зачем эта карта
> Графовое представление наших связей через Obsidian — для меня-человека
> (визуальная навигация). Claude-агенты работают по этой базе через
> `Read`/`Glob`/`Grep` напрямую, **карта им не нужна**.

## Структура

**`agents/`** — спецагенты для конкретных задач: `designer` (проектирование
ОВ/ВК/ЭО/СС), `auditor` (независимый ревьюер), `excel-validator`,
`word-checker`, `pdf-reviewer`. Triggers и tools — внутри каждого `.md`.

**`skills/`** — методологические скиллы с триггерами: `karpathy-guidelines`
(5 принципов), `excel-helper`/`word-helper` (универсальные методологии работы
с файлами), `doc-extract` (извлечение из PDF) / `pdf-edit` (редактирование PDF),
`stroy-formatting` (применение ГОСТ-стилей).

**`commands/`** — slash-команды: `/format`, `/harvest`.

**`memory/`** — накопленные уроки и кейсы (`2026-05-09_hooks-debugging.md`
с 16 ловушками, `2026-05-18_lesson-15-proxy-helpers-persistence.md` и т.д.).

**`session-reports/`** — отчёты по каждой рабочей сессии. Структура
папок: `YYYY-MM-DD_<тема-kebab>/`. Шаблон в `_TEMPLATE.md`.

**`harvested/`** — заметки про внешние инструменты (GitHub-репо, PyPI,
MCP-серверы) которые искали в ходе harvest-workflow.

**`scripts/`** — `auto-pull.ps1`, `auto-push.ps1`, `setup-extras.ps1`
(распространение Python/MCP стека через manifest).

**`formatting-templates/`** — 4 DOCX-шаблона для `/format`.

**`mcp-servers/`** — per-machine MCP-серверы (не в git).

**`CLAUDE.md`** — главный файл правил, читается каждой сессией.

**`mcp-manifest.json`** — реестр extras (Python pkgs + MCP servers)
для `setup-extras.ps1`.

## Все memory notes

```dataview
TABLE WITHOUT ID
  file.link as "Заметка",
  file.ctime as "Создан",
  file.mtime as "Изменён",
  file.size as "Bytes"
FROM "memory"
SORT file.name DESC
```

## Последние 15 session-reports

```dataview
TABLE WITHOUT ID
  file.link as "Отчёт",
  file.folder as "Сессия",
  file.mtime as "Изменён"
FROM "session-reports"
WHERE file.name = "report"
SORT file.mtime DESC
LIMIT 15
```

## Все skills

```dataview
TABLE WITHOUT ID
  file.link as "Скилл",
  file.folder as "Папка",
  file.size as "Bytes"
FROM "skills"
WHERE file.name = "SKILL"
SORT file.folder ASC
```

## Все agents

```dataview
TABLE WITHOUT ID
  file.link as "Агент",
  file.size as "Bytes",
  file.mtime as "Изменён"
FROM "agents"
SORT file.name ASC
```

## Harvested (внешние инструменты)

```dataview
TABLE WITHOUT ID
  file.link as "Инструмент",
  file.folder as "Категория",
  file.mtime as "Заметка от"
FROM "harvested"
SORT file.mtime DESC
LIMIT 30
```

## Точки входа

- «Какое правило в базе?» → [[CLAUDE.md]]
- «Какой урок я уже учил по теме X?» → таблица **memory notes** выше + `Grep` по теме.
- «Что было в прошлой сессии по теме Y?» → таблица **session-reports** + название папки.
- «Какие у меня агенты/скиллы?» → таблицы выше.
- «Искал ли я уже инструмент Z на GitHub?» → таблица **harvested**.

## Конвенции

- Имена файлов памяти и session-report'ов — `YYYY-MM-DD_kebab-case.md` или папка `YYYY-MM-DD_<тема>/report.md`.
- Frontmatter (когда есть) — `created`, `updated`, `status`, `owner`, `last-verified`, `tags`. Большинство нот пока без frontmatter — Dataview-таблицы выше работают на `file.*` метаданных, добавление YAML расширит возможности по мере правок.
- Wikilinks `[[...]]` — постепенно по мере правок (не массовая миграция). Обычные markdown-ссылки `[text](path.md)` Obsidian тоже понимает для графа.
- Содержание — русский. Имена файлов и frontmatter-ключи — латиница или русский, как сложилось.

## Технические детали

**Vault-режим:** этот ПК — `C:\Users\Даниил\.claude\`. Открывается через Obsidian как «Open folder as vault».

**Плагины (per-machine, не в git):**

| Плагин | Что даёт |
|---|---|
| Dataview | Динамические таблицы в этой карте |
| Folder notes | `agents/agents.md` как index папки |
| Local REST API | HTTP-канал для MCP Obsidian (порт 27123 по умолчанию) |
| MCP Tools | Helper-плагин для MCP интеграции |
| Open in Terminal | Правый клик → терминал в этой папке |
| Templater | Шаблоны для новых session-report / memory note |

**Self-hosted LiveSync** не нужен — у нас git auto-sync через `SessionStart`/`SessionEnd` hooks (см. `scripts/auto-pull.ps1`/`auto-push.ps1`).

**MCP Obsidian:** если сейчас указывает на другой vault, для работы с этим — переключить URL/токен в его конфигурации (либо в `~/.claude.json` для user-scope MCP, либо запускать второй экземпляр REST API на другом порту).

## Связанные документы

- [[CLAUDE.md]] — главные правила базы
- [[README.md]] — описание репозитория claude-base
- [[memory/2026-05-09_hooks-debugging|hooks-debugging]] — 16 ловушек инфра-работы
- [[mcp-manifest.json]] — реестр extras

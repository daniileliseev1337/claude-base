---
date: 2026-06-03
topic: feedback-harvest-6-internalizations
status: completed
host: DANIILPC (hub, .developer-marker)
---

# Сессия 2026-06-03 — ревью feedback + внедрение 6 наработок в claude-base

**Запрос пользователя:** «проверь последние репорты в Feedback и в основной базе,
там есть очень полезные и плачевные результаты»; затем — внедрить всё в базу
(2 ключевых отчёта от сегодня про AutoCAD-PDF + excel-правило + pyrevit + ПНР-скилл).

## Что делал (хронология)

1. `pull-feedback.ps1` — подтянул ветки feedback. Появились NEW: `R-090226731A`
   (pyrevit) и `TAZZZ-BOOK` (smoke-test). Локальный `all/` отставал по fetch —
   2 ключевых отчёта от сегодня (18:48) не скопировались.
2. Прочитал содержательные: pyrevit (R-090226731A), excel-Химки + Балашиха-цены
   (NB-HP-LQ6G), docx-blanks-failures + consumer-mode + sot-pnr (DANIILPC).
3. **Нашёл 2 ключевых (по подсказке пользователя «они на гитхабе»):** `git fetch`
   feedback-репо → коммиты 18:48 на ветке `R-090226727A`:
   `autocad-pdf-svg-markup-edit` и `autocad-mcp-pdf-overlay-edit` (+ MASTER ПНР 12:21).
4. **Внедрил 6 элементов** (объём согласован через AskUserQuestion = «все 6»):

| # | Что | Файл |
|---|---|---|
| 1 | memory: AutoCAD-PDF разметка, 2 метода | `memory/reference_autocad_pdf_svg_markup.md`, `..._overlay_mcp.md` + индекс MEMORY.md |
| 2 | pdf-helper: секция «перерисовать нанесённую графику на AutoCAD-PDF» + триггеры | `skills/pdf-helper/SKILL.md` |
| 3 | anti-patterns: §A3.6 (content-stream для разметки) + §A3.7 (autocad-mcp ловушки) | `anti-patterns.md` |
| 4 | excel-helper: ловушка 9 (MCP token-лимит >50 строк → openpyxl) | `skills/excel-helper/SKILL.md` |
| 5 | pyrevit: reference-memory новый домен | `memory/reference_pyrevit_k7.md` + индекс |
| 6 | скилл `pnr-vor-helper` (SKILL.md + 4 tools) из MASTER-сводки | `skills/pnr-vor-helper/` |

## Решения (Karpathy + skill-development)

- **PyRevit — memory-reference, НЕ агент/скилл.** Karpathy #2 (простота): один отчёт,
  новый домен — рано городить инфраструктуру. При 2-м касании вырастет в скилл
  (инкремент, skill-development). Зафиксировано в самом файле.
- **pnr-vor-helper — 3 слоя сразу** (SKILL.md + tools/{table_structure, pnr_profiles,
  pipeline_checklist, validator_prompts}). Скрипт-генератор xlsx (`build_*.py`) — на
  машине автора, в базу не попал; tools/ описывают структуру/чек-лист/prompt'ы.
  Кандидат на будущий `tools/build_pnr_vor.py` при следующем касании.
- **Не путать с soседними скиллами:** pnr-vor-helper ≠ spec-writer (тот — спеки .СО);
  AutoCAD-PDF разметка ≠ Inkscape-удаление штампа (разные задачи, кросс-линки проставлены).

## Источники

- feedback-репо ветки R-090226727A / R-090226731A / NB-HP-LQ6G.
- Ключевые: `2026-06-03_autocad-pdf-svg-markup-edit`, `2026-06-03_autocad-mcp-pdf-overlay-edit`,
  MASTER `2026-06-01_sit-center-pnr-series`.
- skill-development SKILL.md (методология 3 слоёв, инкремент).

## Обезличивание

- pnr-vor-helper и pyrevit-memory: объект/заказчик/подрядчик/подписанты/шифр →
  плейсхолдеры. PII-grep по новым файлам — 0 совпадений (Mberezesko/Deliseev/ifesenko/
  Гуркин/Круглова/Мосинжпроект/Лайв Саунд/Брестская/Балашиха/Химки/6729).
- hostname'ы (R-090226727A и пр.) оставлены — они уже открыты в feedback-репо как
  идентификаторы машин, не PII.

## Догон: агент pyrevit-engineer (по запросу пользователя)

После внедрения 6 элементов пользователь попросил отдельного **агента** для PyRevit
(вместо memory-only решения), «работает хорошо + экономит токены».

- Создан `agents/pyrevit-engineer.md` (16-й агент) по `_TEMPLATE.md` v1.0.
- **Экономия токенов — дизайном, не слабой моделью:** узкий tools-набор
  (Read/Write/Edit/Glob/Grep/Bash, без MCP-вееров), cascade-load одного reference,
  отдельная секция «Token economy» (Grep→offset/limit, хирургический Edit, фильтр
  Bash-вывода, сжатый возврат). Модель НЕ фиксирована (наследует Opus) — на Revit API
  ошибка в .NET-сигнатуре = переделка = больше токенов, слабая модель контрпродуктивна.
- **auditor:** первый прогон NOT PASSED (claim «порядок фаз недетерминирован» подан как
  факт; `Document.Phases` упорядочен). Исправлено в агенте и в reference_pyrevit_k7.md
  (привязка к `Document.Phases` + `# TODO verify`). Остальные 6 свойств — PASS.
- Обновлены: `CLAUDE.md` (эталон 15→16, agents: Y/16), `agents/agents.md` (+строка).
- ⚠ **Подхватится после restart Claude Code** (hot-reload агентов нет).

## Открытые вопросы / backlog

- **`memory/reference_agents.md` — double-encoded mojibake** (как был CLAUDE.md). Нужна
  перекодировка UTF-8 + добавление строки №16 (pyrevit-engineer). Не трогал частично,
  чтобы не смешать кодировки. Отдельная арка (как CLAUDE.md mojibake fix).
- **`agents/agents.md` — неполный индекс** (5 из 16 агентов; доменные от 2026-05-25 не
  внесены). Backlog на дозаполнение.
- **CLAUDE.md CORE-секция** (эталон агентов) управляется installer — при апдейте
  claude-lite-instaler отразить 16 и там, иначе следующий install откатит на 15.

- **autocad-mcp фиксы** (из feedback): `drawing plot_pdf` не пишет файл; рецепт
  прозрачности зон при печати DWG→PDF. Зафиксировано в reference_autocad_pdf_overlay_mcp.
- **pnr-vor-helper tools/build_pnr_vor.py** — вынести реальный генератор при следующей
  ПНР-задаче (skill-development: код в tools/).
- **pyrevit → скилл** при 2-м касании домена.
- Прежние хвосты прошлой сессии (SessionEnd stub-хук, _legacy_payload чистка) — не трогал.

## Auto-sync

- Начало: pull-feedback отработал. Конец: ручной commit+push в claude-base/main
  (bypass proxy). Хаб-режим (.developer-marker присутствует).

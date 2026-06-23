---
chain: project-doc-pack
status: stub
created: 2026-05-20
triggers:
  - «собери комплект ПЗ + спецификация + ведомости»
  - «оформи проектный комплект»
  - «выгрузи весь пакет к разделу»
related_skills:
  - [[word-helper]]
  - [[excel-helper]]
  - [[stroy-formatting]]
  - [[karpathy-guidelines]]
depends_on:
  - [[project_designer_decomposition]]
---

# chain:project-doc-pack

## Status

🚧 **Stub.** Цепочка определена, но Stage 1-3 реализуются после
stage-decomposition агента `designer`
(см. [[project_designer_decomposition]] backlog-memory).

## Назначение

Собрать полный комплект проектной документации для одного раздела
(ОВ / ВК / ЭО / СС) одним flow: ПЗ (DOCX), спецификация оборудования
(XLSX), ведомость материалов (XLSX), пакет в ГОСТ-формате.

## Будущие шаги (после декомпозиции designer)

### Stage 1 — collect

`s1-stroy-collect` собирает ИРД, чертежи, нормативы для раздела.

**Verify:** все исходные документы найдены, без потерянных ссылок,
список нормативов соответствует разделу.

### Stage 2 — parse ТЗ

`s2-stroy-parser` структурирует ТЗ в JSON: нагрузки, площади,
требования заказчика.

**Verify:** JSON с обязательными полями раздела (нагрузка, источник,
точки подключения).

### Stage 3 — расчёт

`s3-stroy-calc` выполняет расчёт по разделу (no I/O, JSON in →
JSON out).

**Verify:** результат включает спецификацию оборудования, нагрузки
по точкам, объёмы материалов, явные допущения.

### Stage 4 — generate artifacts

Параллельно (если включён `teammateMode: tmux` — см. R&D backlog):

- `s4-stroy-docx-writer` → `ПЗ.docx`
- `s4-stroy-xlsx-writer` → `Спецификация.xlsx` + `Ведомость.xlsx`

Затем `stroy-formatting` применяет ГОСТ-стиль к DOCX. Все артефакты
сохраняются в `<project>/<раздел>/`.

**Verify:** все 3 файла созданы, прогон `word-checker` +
`excel-validator` PASSED.

## Когда НЕ использовать

- Нужен только один артефакт → `chain:docx-from-template` для ПЗ
  или прямой вызов `designer` для расчёта.
- До завершения stage-decomposition `designer` — main-агент делает
  flow вручную, используя `designer` как монолит. См.
  [[project_designer_decomposition]].

## История

- 2026-05-20 — chain создан как stub в рамках импорта из аудита <организация>.
  Активация после backlog-триггера.

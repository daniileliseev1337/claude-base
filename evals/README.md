---
created: 2026-05-20
status: active
tags: [tests, evals, regression]
---

# evals/ — regression-тесты методики

## Что это

Защита ключевых скиллов и агентов от регрессий при будущих правках.
Импорт паттерна из аудита <организация> (см. отчёт `~/Desktop/<организация>_audit_report.docx`,
раздел 4.4).

## Подходы

### 1. pytest для детерминированного функционального кода

**Текущий подход.** Используется для скиллов с чистым Python-ядром
без LLM-вызовов: `image-text-replace` (pipeline.py + calibration.py),
другие будущие скиллы такого же типа.

Запуск:

```powershell
cd ~/.claude/evals
python -m pytest -v
```

Конкретный файл:

```powershell
python -m pytest -v test_image_text_replace.py
```

### 2. promptfoo для семантических тестов LLM-агентов

**Backlog.** См. [[memory/backlog_promptfoo_semantic_tests]] —
включаем когда появится потребность тестировать LLM-вызовы
(например, корректность вывода `designer` или `word-checker` на
эталонных промптах). Требует Anthropic API key и тестовых эталонов.

## Текущие тесты

| Файл | Что покрывает |
|---|---|
| `test_image_text_replace.py` | 4 ключевые функции pipeline.py + calibration.py — `smart_cap_height_detect`, `find_neighbor_cell_reference`, `compute_midline_paste_y`, `_find_font_size_for_height`. Покрытие по [[image-text-replace/LESSONS-LEARNED]] §2-5. |

## Когда добавлять новый тест

- Появилась **новая ключевая детерминированная функция** в одном из
  скиллов.
- Произошла **регрессия** — функция начала вести себя неправильно
  после рефактора. Сначала пишем тест воспроизводящий баг, потом
  фиксим (Karpathy §4).
- Появилась тестируемая часть **нового скилла** (например, парсер
  для нового формата документов).

## Когда НЕ писать тест

- Функция вызывает LLM (тогда — promptfoo, когда подключим).
- Тонкая обвязка (просто проверяет наличие файла, простой shell-call).
- Одноразовый код, который скоро удалится.

## Структура

- `conftest.py` — общие fixtures и `sys.path` для импорта скиллов.
- `test_<skill>.py` — один файл на скилл.
- Тестовые данные — inline (synthetic numpy arrays / synthetic OCR
  matches), без эталонных изображений в репо.

## Связанные

- [[skills/karpathy-guidelines]] §4 — verify-criteria, regression
  protection как часть цикла «цель → критерий → действие».
- [[chains-pattern]] — каждая цепочка в `~/.claude/chains/` должна
  иметь verify-критерий, но это **не** entry для evals — это runtime
  check, не regression-тест.
- [[memory/backlog_promptfoo_semantic_tests]] — следующий этап,
  семантические тесты через promptfoo.

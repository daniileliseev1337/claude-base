---
name: acad-recreation
description: |
  Воссоздание чертежей (в первую очередь ОВ-проектов квартир) из PDF в DWG через
  autocad-mcp на ЖИВОМ AutoCAD: подложка (PDFIMPORT+калибровка+чистка), динамические
  блоки фирмы, слои/листы/штампы, аннотации. Несёт наш усиленный toolkit поверх
  сервера puran-water + заимствования из harvest (LISP-toolkit, multi-view PDF, cp1251-патч).

  Триггеры:
  - "воссоздать чертёж", "PDF в DWG", "recreation", "пересоздать проект из PDF"
  - "ОВ-проект квартиры", "разводка вентиляции в AutoCAD", "динамический блок воздуховод"
  - "autocad-mcp", "execute_lisp", "PDFIMPORT", "подложка чертежа"
  - "вставить динблок с параметрами", "dyn-props", "Lee Mac"
---

# acad-recreation

Усиление autocad-mcp (`puran-water`) под наш сценарий + заимствования из harvest 2026-06-04.
**Не заменяет сервер** — это слой поверх (LISP-toolkit + Python-препроцессинг + патч).
Метод и статус-трекер этапов — [[reference_acad_ov_dwg_recreation]]. Общий урок кириллицы —
[[reference_autocad_mcp_cyrillic]].

## Когда подключаться

Любая задача воссоздания/правки чертежа через живой AutoCAD (autocad-mcp, backend file_ipc).
Сначала `system status` → при `ezdxf` сделать `system init` (нужен file_ipc для живого AutoCAD).

## Слой tools/ (наш усиленный инструментарий)

| Файл | Что | Статус |
|---|---|---|
| `tools/acad_lisp_toolkit.lsp` | Lee Mac dynblock-функции + канонический скелет-обёртка + safety-блоклист | APPLOAD в AutoCAD |
| `tools/pdf_multiview.py` | 9-tile multi-scale препроцессинг PDF (overview + 2×2 + угловые deep-zoom) | Python, автономный |
| `tools/file_ipc_cp1251.patch` | Патч сервера: fallback cp1252 → cp1251 (русский AutoCAD) | применить на ПК с сервером |
| `tools/cherry_pick_batch.md` | Инструкция вливания batch-инструментов из prumputira/autocad-mcp v5.0 | на рабочем ПК |

### 1. LISP-toolkit (`acad_lisp_toolkit.lsp`)

Загрузить один раз: `APPLOAD` → `acad_lisp_toolkit.lsp` (или из execute_lisp `(load "...")`).
Даёт детерминированные функции (Karpathy «код в tools/», не генерировать LISP заново):
- **Динблоки (Lee Mac):** `(LM:setdynpropvalue blk "Диаметр" 200)`, `(LM:getdynpropvalue blk prop)`,
  `(LM:getvisibilitystate blk)`, `(LM:setvisibilitystate blk state)`, `(LM:getdynprops blk)`.
  **Это наша эксклюзивная сила** — ни один из 11 harvest-кандидатов не управляет dyn-props штатно.
- **Безопасный блок:** `(K7:safe-run '(...))` — оборачивает геометрию в `UNDO _GROUP … _END` +
  финальный `ZOOM _E`, чтобы один откат снимал весь шаг (канонический скелет из ClaudeCAD-методологии).
- **Слои:** `(K7:ensure-layers '(("!Приток" 1)("!Вытяжка" 5)("!Рециркуляция" 6)))` — создать/настроить.

### 2. multi-view PDF (`pdf_multiview.py`)

`python pdf_multiview.py <pdf> <out_dir> [page]` → overview 1920px + 2×2 квадранты (10% overlap)
+ 4 угловых deep-zoom (под штамп/рамку). Решает «модель не видит мелочь на подложке/штампе».
На pypdfium2 (без poppler). Читать tiles через Read tool.

### 3. cp1251-патч (`file_ipc_cp1251.patch`)

⚠ **Баг сервера:** `file_ipc.py` при чтении ответа AutoCAD fallback'ит на **cp1252**, а русский
AutoCAD пишет **cp1251** → кракозябры в именах слоёв/блоков. Патч добавляет cp1251 в цепочку
(`utf-8 → cp1251 → cp1252`). Применить + тест на живом AutoCAD (см. заголовок патча).

### 4. batch-инструменты (`cherry_pick_batch.md`)

`prumputira/autocad-mcp` v5.0 (Apache-2.0, эволюция нашей же базы) даёт `draw_*_batch`
(−60-70% API-вызовов = главный bottleneck при сотнях примитивов). Cherry-pick кодом на рабочем ПК.

## Наши уникальные наработки (нет ни у кого — беречь)

1. **Программное управление dyn-props динблоков** (toolkit выше): диаметр/радиус/расстояние как
   double напрямую, НЕ через lookup-таблицу; слой через `CLAYER` до вставки; ориентация в радианах.
2. **Кириллица end-to-end** ([[reference_autocad_mcp_cyrillic]]): вход Unicode в коде / выход cp1251
   файлом / открытие через COM `vla-Open`+`put-ActiveDocument`; рабочие пути ASCII (`C:\temp`).
3. **PDFIMPORT-калибровка подложки**: `FILEDIA 0`, `PDFIMPORTMODE 7`, `-PDFIMPORT`; коэффициент
   `units_per_mm` по двум равным размерным сегментам. Чистка не огулом (слой+цвет+геометрия+обход).
4. **Block→scale в правильном порядке**: собрать в блок, ПОТОМ `vla-ScaleEntity` (не россыпь `ssget _C`).

## Анти-паттерны (из harvest — НЕ внедрять)

- graceful degradation extrude→box (молчаливая подмена геометрии — нарушает «не выдумывать»);
- regen после каждой сущности; ASCII-whitelist, режущий кириллицу; regex-NLP вместо модели.

## Верификация

- LISP-toolkit: `APPLOAD` без ошибок + пробный `(LM:getdynprops ...)` на блоке эталона.
- Каждый деструктив: save перед, сверка скрином ЗОНЫ (PNGOUT / `capture_screenshot`), `(_.U)` откат.
- Финал: печать PDF + сверка с исходником + нормоконтроль.

## Источник

harvest `session-reports/2026-06-04_autocad-mcp-harvest/` + feedback `2026-06-04_autocad-pdf-to-dwg`.
Lee Mac функции — lee-mac.com (свободное использование с атрибуцией).

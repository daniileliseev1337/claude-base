# Top PDF Content-Stream Editing Tools (harvest 2026-05-27)

## Контекст

Инцидент: в наших сессиях Claude закрашивал текст/линии в проектных PDF
белыми прямоугольниками-overlay вместо физического удаления. Это маска,
а не редактирование: Ctrl+F всё ещё находит, при печати на цветной бумаге
артефакт виден, для штампа чертежа это юридически подделка. Нужен
content-stream-level подход с реальным удалением операторов.

## TOP-5 (отсортировано по применимости)

### 1. PyMuPDF (pymupdf/PyMuPDF) — физическое удаление текста + line art

- URL: https://github.com/pymupdf/PyMuPDF
- Stars: 9818 | Last commit: 2026-05-26 | License: **AGPL-3.0 (флаг!)**
- Подход: **content stream** — `apply_redactions()` физически удаляет
  текст из page content stream + умеет удалять перекрытые vector
  graphics (line art) тремя режимами.
- Сильные стороны:
  - Единственный в списке, кто из коробки удаляет **и текст, и линии**
    в заданной области (`PDF_REDACT_LINE_ART_REMOVE_IF_COVERED`).
  - Цикл: `add_redact_annot(rect)` → `apply_redactions(graphics=...)`.
  - Зрелый, активный, огромный issue tracker — известные ловушки уже
    описаны (cap height, stroked line width).
- Слабые / риски:
  - **AGPL-3.0** — заразная для распространения. Для нашего внутреннего
    использования OK, но если мы это завернём в продукт «наружу» —
    нужен commercial license от Artifex. Для внутреннего скилла Claude
    Code в нашей фирме — допустимо.
  - Не pikepdf-based — отдельный нативный движок (MuPDF).
  - Stroked vector с line width 1pt требует расширения redact rect на
    ≥5pt в каждую сторону, иначе остаётся «хвост».
- Применимость к нашим кейсам:
  - Удаление текста: ✅
  - Удаление линий: ✅ (единственный из 5)
  - Штамп чертежа: ✅ (текст в ячейках штампа + линии вокруг)
  - Аннотации экспертизы (облачка): ✅ (через `page.delete_annot()` +
    redact на текст комментария)

### 2. pikepdf (pikepdf/pikepdf) — низкоуровневый content stream API

- URL: https://github.com/pikepdf/pikepdf
- Stars: 2728 | Last commit: 2026-05-25 | License: MPL-2.0 (зелёный)
- Подход: **content stream** — `parse_content_stream(page)` отдаёт
  список `(operands, operator)`, фильтруем, `unparse_content_stream()`
  пишет обратно. Поверх QPDF, очень корректен.
- Сильные стороны:
  - Хирургический контроль: можем удалить конкретный `Tj`/`TJ`/`re`/`l`/`m`.
  - MPL-2.0 — file-level copyleft, нам подходит без оговорок.
  - Используется в OCRmyPDF, проверен в проде.
- Слабые / риски:
  - **«Best for reading, not for editing»** — официальная дока сама
    предупреждает: «some subtleties are lost in parsing», нужен
    tracking graphics state, иначе ломаем рендеринг.
  - Нет высокоуровневого `redact()` — пишем сами state machine.
  - Текст в CIDfonts/Type3 — отдельный ад с glyph→Unicode маппингом.
- Применимость:
  - Удаление текста: ⚠️ (можно, но требует свой parser операторов)
  - Удаление линий: ⚠️ (фильтровать `m`/`l`/`re`/`S` вручную)
  - Штамп чертежа: ⚠️ (для типового штампа можно написать, но не из коробки)
  - Аннотации экспертизы: ✅ (правка `/Annots` — типичный кейс pikepdf)

### 3. pdf-redactor (JoshData/pdf-redactor) — regex-замена в text layer

- URL: https://github.com/JoshData/pdf-redactor
- Stars: 212 | Last commit: **2024-06-13** (>12 мес, флаг!) | License: CC0-1.0
- Подход: **content stream text layer** — regex substitution через pdfrw.
- Сильные стороны:
  - Точно то что нужно для «замени шифр на новый» в текстовом PDF.
  - Public domain (CC0) — копируй что хочешь.
  - Metadata + XMP + аннотации в одном пакете.
- Слабые / риски:
  - **Не активен** (последний коммит >12 мес) — формально не проходит
    наш фильтр harvest-workflow. Но репо стабильное, не заброшен.
  - Зависит от pdfrw, который сам полу-мёртвый и не понимает все типы
    сжатия content stream → требует `qpdf --decode-level=all` препроцесс.
  - Glyph/CID fonts — официально «limited understanding», на наших
    чертежах с кастомными шрифтами штампа сломается.
- Применимость:
  - Удаление текста: ✅ (regex → пустая строка / XXXX)
  - Удаление линий: ❌ (только text layer)
  - Штамп чертежа: ⚠️ (если шрифт стандартный — ок; кастомный — нет)
  - Аннотации экспертизы: ✅ (текст в аннотациях ловится)

### 4. pdfcpu (pdfcpu/pdfcpu) — Go CLI для batch и аннотаций

- URL: https://github.com/pdfcpu/pdfcpu
- Stars: 8655 | Last commit: 2026-05-25 | License: Apache-2.0 (зелёный)
- Подход: **структурный** — работает с PDF object tree, удаляет
  аннотации по типу/id, но **content stream редактирование текста не
  поддерживает** (нет команды redact text → только аннотации).
- Сильные стороны:
  - Однофайловый Go бинарь — кладём в `~/.claude/bin/`, запускаем
    из любого hook без Python окружения.
  - Удаление аннотаций любого типа (Square, FreeText, Polygon, **Redact**,
    HighLight, StrikeOut, Stamp) — ровно то что присылает экспертиза.
  - `pdfcpu annotations remove -p 1-3 file.pdf Polygon` — одна строка.
- Слабые / риски:
  - **Не удаляет текст из content stream** — только аннотации и
    структурные операции (split, merge, watermark, encrypt).
  - Для замены текста / удаления линий не подходит.
- Применимость:
  - Удаление текста: ❌
  - Удаление линий: ❌
  - Штамп чертежа: ❌
  - Аннотации экспертизы (облачка, FreeText, Polygon): ✅ (best in class)

### 5. qpdf (qpdf/qpdf) — fallback для декомпрессии перед ручным edit

- URL: https://github.com/qpdf/qpdf
- Stars: 5089 | Last commit: 2026-05-24 | License: Apache-2.0 (зелёный)
- Подход: **QDF mode** — нормализует PDF в text-editable форму
  (`qpdf --qdf --object-streams=disable in.pdf out.pdf`), затем человек
  или скрипт правит content stream как plain text, `fix-qdf` чинит xref.
- Сильные стороны:
  - C++ нативный, базис для pikepdf — максимально стабилен.
  - Незаменимый препроцесс для pdf-redactor (см. #3).
  - CLI, легко звать из PowerShell hook.
- Слабые / риски:
  - **Не редактор сам по себе** — это «PDF assembler». Удаления текста
    из коробки нет, только инфраструктура.
- Применимость (как инструмент-инфраструктура, не самостоятельный):
  - Удаление текста: ⚠️ (только в связке с pikepdf/pdf-redactor)
  - Удаление линий: ⚠️ (вручную в QDF)
  - Штамп чертежа: ❌ (слишком низкоуровнево)
  - Аннотации экспертизы: ⚠️ (можно убрать `/Annots` запись, но проще pdfcpu)

## pypdf (py-pdf/pypdf) — упоминание, не в TOP-5

10009 stars, активный, BSD-like (NOASSERTION в API = BSD-3 по факту).
Имеет `PdfWriter.remove_text(font_names=...)` и `remove_objects_from_page()`
с `ObjectDeletionFlag` — формально content-stream level. Но согласно
issue tracker (PR #3216, discussion #3049): «работает на одних PDF, на
других нет, особенно OCR и Type3 fonts». Для чертежей с экзотическими
шрифтами штампа — risky. Держим как backup для простых текстовых PDF
ответов экспертизы без чертёжной графики.

## Рекомендация

**TOP-1 для нашего `pdf-helper` SKILL.md: PyMuPDF (`apply_redactions`).**
Причина: единственный кто покрывает *все 4* наших кейса из коробки
(текст + линии + штамп + аннотации), активный, документация по
ловушкам уже написана разработчиками. AGPL — для внутреннего скилла
Claude Code в нашей фирме допустимо; если когда-то решим публиковать
наружу — пересматриваем.

**Fallback 1: pikepdf.** Когда нужен хирургический контроль над
конкретным оператором (например, в штампе удалить только строку
«Изм.» не трогая рамку) или когда AGPL мешает. Пишем свой state
machine поверх `parse_content_stream`.

**Fallback 2: pdfcpu CLI.** Когда задача = «убрать облачка экспертизы
из 50 PDF» (batch, чистые аннотации, нет текста для удаления).
Однострочник в hook без Python.

**Препроцесс: qpdf `--qdf`** перед любой работой pikepdf/pdf-redactor
на PDF со сжатыми content streams.

**Не брать как primary:**
- `pdf-redactor` (JoshData) — не активен >12 мес, pdfrw фундамент
  хрупкий, glyph mapping слабый. Но забрать **идею regex по text
  layer** в наш собственный pikepdf-обёртке.
- `pypdf.remove_text()` — известные баги на Type3 и OCR PDF.

## Anti-pattern для CLAUDE.md / pdf-helper

**Запретить навсегда:** «закрасить белым прямоугольником» = overlay.
В чертёжных PDF и ответах экспертизы это всегда выдаёт диверсию.
Правильно: `PyMuPDF apply_redactions` (default) → `pikepdf
parse_content_stream` (хирургия) → `pdfcpu annotations remove`
(только аннотации).

Сводная таблица применимости:

| Кейс                              | PyMuPDF | pikepdf | pdf-redactor | pdfcpu | qpdf |
|-----------------------------------|---------|---------|--------------|--------|------|
| Удаление текста (плотный layout)  | ✅      | ⚠️      | ✅           | ❌     | ⚠️   |
| Удаление линий чертежа            | ✅      | ⚠️      | ❌           | ❌     | ⚠️   |
| Правка штампа чертежа             | ✅      | ⚠️      | ⚠️           | ❌     | ❌   |
| Облачка/FreeText экспертизы       | ✅      | ✅      | ✅           | ✅     | ⚠️   |
| Batch CLI без Python              | ❌      | ❌      | ❌           | ✅     | ✅   |
| Лицензия для нас                  | AGPL⚠️  | MPL✅   | CC0✅        | Apache✅| Apache✅|

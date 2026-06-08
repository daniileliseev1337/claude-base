---
name: pdf-helper
description: |
  Универсальная методология работы с PDF: чтение, извлечение таблиц/текста,
  редактирование (объединение, разделение, заполнение форм, перекраска
  аннотаций, замена страниц). Подключается на любые задачи с .pdf-файлами,
  где требуется не просто "прочитать", а сделать что-то осмысленное.

  Триггеры:
  - "PDF", ".pdf", "извлечь из pdf", "разбери pdf"
  - "объединить PDF", "разделить PDF", "merge pdf", "split pdf"
  - "заполни форму pdf", "fillable pdf", "акроформа", "AcroForm"
  - "вставь страницу в pdf", "замени страницу", "удали страницу"
  - "оглавление pdf", "закладки pdf", "bookmarks"
  - "pikepdf", "pypdf", "pdfplumber", "pdf metadata"
  - "перекрасить облачка", "polygon cloud", "аннотации pdf"
  - "сравнить два pdf", "diff pdf"
  - "чертёж pdf", "штамп чертежа", "слои pdf", "СКС в pdf", "план этажа pdf"
  - "перерисовать разметку на чертеже", "наложение CCTV/СС/ЭО на план",
    "починить нанесённую графику в pdf", "чертёж только в pdf, нет dwg"
  - сканированный PDF (нет text layer) → авто-routing на OCR pipeline
    из image-text-replace (EasyOCR + smart cap + bbox detection)
---

# pdf-helper

## Когда подключаться

Любая задача с PDF, выходящая за рамки простого чтения нескольких строк. Если пользователь просит «открой PDF» и в нём 1-2 страницы простого текста — Read tool достаточно. Всё остальное — сюда.

## ВАЖНО — обязательная проверка: текстовый PDF или скан

**Первый шаг при любой задаче с PDF — определить тип:**

```python
import pdfplumber
with pdfplumber.open(pdf_path) as pdf:
    text_total = sum(len((page.extract_text() or "").strip()) for page in pdf.pages)
    img_pages = sum(1 for page in pdf.pages if page.images)
    n_pages = len(pdf.pages)

if text_total < 50 * n_pages and img_pages == n_pages:
    # Каждая страница содержит images, текстового слоя нет → СКАН
    is_scan = True
else:
    is_scan = False
```

**Для скан-PDF** (text_total ≈ 0, каждая страница имеет image):
- markitdown / pdf-mcp **не дают** содержимое (нет text layer)
- Routing: image-text-replace pipeline (EasyOCR + bbox + smart cap)
- См. ниже секцию «OCR для скан-PDF»

**Для текстового PDF**:
- markitdown / pdf-mcp работают как обычно
- pikepdf для структурных операций

Эта проверка должна быть **первой** при работе с любым unknown PDF.

## OCR для скан-PDF (proactive use)

Когда пользователь:
- Просит **прочитать** скан-PDF → не только при «замени текст»
- Хочет **найти** значение в таблице скана
- Нужно **извлечь** структурные данные (номер документа, сумму, дату)

Используем стек из `image-text-replace`:

```python
import sys
sys.path.insert(0, str(Path.home() / ".claude/skills/image-text-replace"))
from pipeline import run_ocr, find_neighbor_cell_reference, smart_cap_height_detect

# 1. Render page → PNG
import pypdfium2 as pdfium
pdf = pdfium.PdfDocument(pdf_path)
page_img = pdf[0].render(scale=200/72).to_pil()

# 2. EasyOCR + bbox
matches = run_ocr(page_img_path)
# Каждый match: text, bbox, confidence

# 3. Для структурных задач (label: value) — find_neighbor_cell_reference
label = next(m for m in matches if "итог" in m.text.lower())
value = find_neighbor_cell_reference(matches, label, side='right', digits_only=True)
# value.text = "144 105 177,91"
```

Это **сильнее markitdown** для сканов:
- Точные bbox координаты каждого token
- Smart cap detection (игнорирует descenders)
- Label-value pairing для cell-style данных
- Confidence per token

Скилл image-text-replace **уже умеет** OCR — image text replace это **второстепенная** функция. Основная — точное распознавание содержимого scan-PDF с координатами.

## Режим чертежей (А3/А1 со штампом и слоями)

Если PDF — это чертёж (альбомный, штамп в правом нижнем углу, векторные слои СКС/СКУД/CCTV/ОПС), используй отдельный workflow — см. `drawings.md` рядом.

Быстрый старт:

```python
import sys
sys.path.insert(0, str(Path.home() / ".claude/skills/pdf-helper/scripts"))
from extract_drawing_meta import extract_text_blocks, find_stamp_data
import pdfplumber

blocks = extract_text_blocks("plan_floor1.pdf", page=0)
with pdfplumber.open("plan_floor1.pdf") as pdf:
    page_size = (pdf.pages[0].width, pdf.pages[0].height)
stamp = find_stamp_data(blocks, page_size)
# {'project': '<имя проекта>', 'drawing_no': '5', 'scale': '1:50', 'stage': 'РД', ...}
```

Извлекает: текстовые блоки с координатами, штамп (правая нижняя четверть страницы), слои PDF через `/OCProperties`, помещения по легенде. Если в PDF только растровое изображение чертежа (скан) — упади на skill `image-text-replace` (EasyOCR). Если есть исходный DWG — используй skill [[cad-reader]] (точнее, читает слои напрямую).

## Редактирование вектор-PDF (удалить / подвинуть штамп / объекты) — Inkscape

**Это рабочая замена провалившимся методам.** Удалять объекты, двигать текст/линии,
убирать штамп в векторном чертеже-PDF — **через Inkscape**, НЕ через белые заливки и
НЕ через content-stream surgery (PyMuPDF redact / pikepdf clip — провалено, прячет а
не удаляет, см. `anti-patterns.md` §A3.5).

**ВЕРИФИЦИРОВАНО 2026-06-02** на реальном чертеже <организация> (чистое удаление штампа,
0 растеризации, чертёж цел). Полный метод + ловушки + caveat'ы:
см. `~/.claude/memory/reference_inkscape_pdf_editing.md`.

Кратко:
1. Открыть PDF → вкладка **«Внутренний импорт»** (не Cairo — Cairo делает текст кривыми).
2. Плотный чертёж виснет на `all` → импорт **по одной странице**.
3. Выделить (двойной клик внутрь групп / `Ctrl+Shift+G`) → `Delete` / перетащить.
4. **Сохранить как → PDF** в НОВЫЙ файл. Предупреждение «потеря данных → SVG?» = норма, жмём PDF.
5. **Проверить объективно**: `pdf_render_pages` до/после + `pdf_info` (`pages_with_raster_images`
   должно остаться 0; размер не взлетел; дельта текста = только удалённое). Не верить «на глаз».

⚠ **Производительность:** Inkscape медленно открывает/сохраняет большие чертежи (особенно
слабый ноут без GPU) — учитывать на томах. Батч (CLI `inkex`) — будущая работа.
Лицензия GPL-3.0 → только как внешняя программа, код не копировать.

## Перерисовать НАНЕСЁННУЮ графику на AutoCAD-PDF (разметка CCTV/СС/ЭО)

**Другая задача, чем Inkscape-удаление штампа.** Здесь чертёж пришёл **только в PDF**
(печать из AutoCAD, `pdfplotNN.hdi`, вектор), поверх плана — халтурная разметка
(толстые красные лучи/кружки/квадраты видеонаблюдения и т.п.), которую нужно
**перерисовать** (тонкие синие секторы, значки камер с разворотом), подложку не трогать.

**ВЕРИФИЦИРОВАНО 2026-06-03** (заказчик доволен). Два пути — выбор по тому, нужен ли DWG:

| Нужен на выходе | Метод | Memory |
|---|---|---|
| Только PDF (DWG не нужен) | **Чистый PyMuPDF через SVG-слой**, без AutoCAD — легче | [[reference_autocad_pdf_svg_markup]] |
| DWG (правка возвращается в чертёж) | **autocad-mcp** (PDFIMPORT + entmake + vla-PlotToFile) | [[reference_autocad_pdf_overlay_mcp]] |

Ключевое (общее для обоих): **content-stream surgery и redaction — тупики** (§A3.5):
толстая линия = пучок тонких `0 w` штрихов (поиск по толщине = 0 совпадений), цвет
нанесённого = родному красному плана (по цвету не отделить), redaction сносит базу.
Рабочий приём — маска нанесённого из `get_drawings()` по **цвет+толщина в page-space**,
затем либо удаление SVG-узлов (lxml) + новый слой, либо построение заново в AutoCAD.
Полные методы, геометрия камер и ловушки — в memory-файлах выше.

## Иерархия инструментов (от простого к сложному)

| Задача | Инструмент | Заметка |
|--------|------------|---------|
| Превью текста, грубое извлечение | `markitdown-mcp` | Быстро в md, но таблицы пляшут |
| Извлечение таблиц с координатами | `pdf-mcp` (jztan/pdf-mcp) | Кэширует разбор, лучше для повторных запросов |
| Метаданные, страницы, закладки | Python `pikepdf` | Стабильно работает с большими PDF |
| Слияние/разделение, перекомпоновка | Python `pypdf` | Простой API, не теряет аннотации |
| Заполнение AcroForm | Python `pypdf.PdfWriter.update_page_form_field_values()` | XFA-формы — отдельная история, обычно не поддерживается |
| Аннотации (облачка, маркеры) | Python `pikepdf` (низкоуровневые объекты PDF) | Удалять `/AP` после смены цвета — иначе старый рендер останется |
| Сравнение двух версий PDF | `diff-pdf.exe` (визуальный) или текст через `pdf-mcp` + `difflib` | Бинарный diff бесполезен |
| Редактирование (merge/split/delete/rotate/extract/replace/watermark) | (нет MCP) | pikepdf + pypdf + reportlab напрямую, см. ниже |

**Правило**: всегда сначала смотри, есть ли подходящий MCP в `claude mcp list`. Если есть — через него. Если нужна более тонкая операция — Python.

## Типовые задачи

### Извлечение таблицы

```python
# Через pdf-mcp (предпочт.) — Claude вызовет MCP tool сам.
# Через Python — pdfplumber для текста, camelot для сложных таблиц.
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    for page in pdf.pages:
        for table in page.extract_tables():
            print(table)
```

### Объединение нескольких PDF

```python
from pypdf import PdfWriter
writer = PdfWriter()
for f in ["a.pdf", "b.pdf", "c.pdf"]:
    writer.append(f)
writer.write("combined.pdf")
writer.close()
```

### Замена/удаление страницы

```python
from pypdf import PdfReader, PdfWriter
src = PdfReader("input.pdf")
out = PdfWriter()
for i, page in enumerate(src.pages):
    if i == 4:        # пропустить 5-ю (0-based)
        continue
    out.add_page(page)
out.write("output.pdf")
```

### Заполнение AcroForm

```python
from pypdf import PdfReader, PdfWriter
reader = PdfReader("template.pdf")
writer = PdfWriter(clone_from=reader)
writer.update_page_form_field_values(
    writer.pages[0],
    {"FullName": "Иванов И.И.", "Date": "07.05.2026"}
)
writer.write("filled.pdf")
```

### Перекраска аннотаций (например, облачка)

```python
import pikepdf
pdf = pikepdf.open("input.pdf")
for page in pdf.pages:
    for annot in page.get("/Annots", []):
        if annot.get("/Subtype") == "/PolygonCloud":
            annot["/C"]  = [1, 0, 0]    # красный border
            annot["/IC"] = [1, 0, 0]    # красная заливка
            if "/AP" in annot:
                del annot["/AP"]         # ВАЖНО: удалить cached appearance
pdf.save("output.pdf")
```

## Ловушки

0. **Reportlab + Unicode sub/super дают чёрные квадраты.** Никогда не использовать символы `₀₁₂₃₄₅₆₇₈₉`/`⁰¹²³⁴⁵⁶⁷⁸⁹` в reportlab PDF — built-in шрифты их не содержат, на месте рендерится solid black. Использовать XML-теги в Paragraph: `Paragraph("H<sub>2</sub>O", styles['Normal'])`, `Paragraph("x<super>2</super>", styles['Normal'])`. Для canvas-текста — менять размер/позицию шрифта вручную.
1. **Большие PDF (>50 МБ)** — `pymupdf` (fitz) часто падает на сложной структуре или ест 4+ ГБ RAM. Использовать связку `pikepdf` (низкоуровневая работа) + `pypdf` (комбинаторика страниц).
2. **`/AP` в аннотациях** — это закэшированный рендер. После изменения цвета или текста обязательно удалить, иначе PDF-вьюер покажет старое.
3. **OCR vs текст** — если PDF — скан, `extract_text()` вернёт пусто. Сначала прогнать через OCR (tesseract / cloud API), потом работать.
4. **Сравнение «что изменилось» между двумя PDF** — бинарный diff бесполезен. Лучший путь: отрендерить страницы в PNG (`pdftoppm`) и сравнить через perceptual hash (imagehash) или multimodal vision.
5. **Шрифты при редактировании** — если меняешь текст в PDF и нужный шрифт не embedded, текст потеряется. Проверять через `reader.metadata` или `pikepdf` perms.
6. **Сжатие при сохранении** — `pikepdf.save()` по умолчанию пересжимает. Для минимальных правок передать `linearize=True` или ничего, а вот `compress_streams=False` сохранит исходные потоки.
7. **Сдвиг колонок при извлечении таблиц нагрузок.** При экспорте PDF из расчётных программ/CAD числовые таблицы (Pр, Sр, мощности по щитам) могут «съезжать» на колонку при `extract_tables()`/`find_tables()` — значение попадает не в свой столбец. **Любые числа из таблиц нагрузок/мощностей сверять с оригиналом** (рендер страницы глазами или соседний столбец-сумма), не доверять плоскому парсу. Особенно при аудите «ТЧ vs спецификация». (Источник: аудит <объект>, шифр <шифр>.)
8. **CID / PScript-Distiller PDF — читать рендером, не текстовым слоем.** PDF, прошедшие через PostScript-принтер + Acrobat Distiller (Producer `PScript5`/`Acrobat Distiller`), часто имеют CID-шрифты без ToUnicode → `extract_text()` отдаёт мусор/пусто. Не биться об текст — сразу **рендер ≥180 dpi** (`pdf_render_pages` / PyMuPDF `get_pixmap(dpi=180)`) + читать визуально/OCR. (Источник: проект <шифр>.)

## Когда вызывать агента pdf-reviewer

После любой существенной правки PDF (удалили страницы, добавили аннотации, изменили формы) — спавнить subagent `pdf-reviewer` с задачей «проверь итоговый PDF на сохранность структуры». Агент сам проверит количество страниц, метаданные, целостность аннотаций, выдаст отчёт.

## Визуальный diff двух PDF

⚠ **Портативный `diff-pdf.exe` НЕ установлен** в `~/.claude/bin/` (раньше ожидался в
`bin/diff-pdf/` — каталога нет). Пока бинарь не доставлен вручную, визуальный diff делаем
**рендером страниц в PNG + сравнением** (это и есть рабочий путь по умолчанию, см. «Ловушки» п.4):

```python
# Рендер обеих версий и сравнение через perceptual hash / multimodal vision
import fitz  # PyMuPDF
for v in ("v1.pdf", "v2.pdf"):
    doc = fitz.open(v)
    for i, page in enumerate(doc):
        page.get_pixmap(dpi=150).save(f"{v}_p{i}.png")
# далее imagehash.phash() попарно или показать страницы vision-модели
```

Если позже доставите портативный `diff-pdf.exe` (GPL-2.0, допустим как **внешний бинарь**
через subprocess, **код не копировать**): `& diff-pdf.exe v1.pdf v2.pdf` даёт exit 0 (идентичны)
/ 1 (отличаются), флаг `--output-diff=diff.pdf` пишет наложение красным.

## Редактирование PDF — pikepdf/pypdf напрямую

Базовые операции делаем через Python-библиотеки в Bash subprocess (не своим MCP):

| Операция | Библиотека | Пример |
|----------|------------|--------|
| Merge | `pypdf.PdfWriter` + `add_page` | `for p in pages: writer.add_page(p)` |
| Split | `pikepdf.Pdf` slice | `pdf.pages[start:end]` |
| Delete pages | `del pdf.pages[idx]` | pikepdf |
| Rotate | `pdf.pages[i].rotate(90)` | pikepdf |
| Extract range | `pdf.pages[start:end]` | pikepdf |
| Replace page | `pdf.pages[i] = src.pages[j]` | pikepdf |
| Watermark text | `reportlab` → canvas → merge | через PdfWriter overlay |
| Watermark image | `reportlab.platypus.Image` | overlay |
| AcroForm fill | `pypdf.update_page_form_field_values` | pypdf |
| Аннотации | pikepdf низкоуровневый | прямая правка `/Annots` |

## MCP-роутинг (повтор для удобства)

| Задача | MCP server | Скилл fallback |
|--------|------------|----------------|
| Чтение текста | markitdown | pdfminer |
| Чтение таблиц | pdf-mcp | pdfplumber |
| Редактирование (merge/split/rotate/watermark) | (нет MCP) | pikepdf + pypdf + reportlab |
| AcroForm заполнение | (нет MCP) | pypdf.update_page_form_field_values |
| Аннотации (перекрашивание) | (нет MCP) | pikepdf низкоуровневый |
| Визуальный diff | (нет MCP) | рендер PNG + perceptual hash / vision (diff-pdf.exe не установлен) |

## Tools (слой 3)

Папка `scripts/` рядом с этим SKILL.md — 3-й слой стандарта скиллов
(Description + Instructions + **Tools**): детерминированные скрипты, которые не нужно
переписывать каждый раз, импортируются напрямую (`sys.path.insert(0, ".../pdf-helper/scripts")`).

- `extract_drawing_meta.py` — `extract_text_blocks()` (текстовые блоки с bbox) и
  `find_stamp_data()` (разбор штампа в правой нижней четверти страницы). Используется
  режимом чертежей выше.
- `test_extract_drawing_meta.py` — тесты к нему.

Это `scripts/`, а не `tools/` — каталог намеренно не переименовываем (исторически прижилось).

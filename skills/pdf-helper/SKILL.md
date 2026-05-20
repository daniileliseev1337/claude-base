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

## Когда вызывать агента pdf-reviewer

После любой существенной правки PDF (удалили страницы, добавили аннотации, изменили формы) — спавнить subagent `pdf-reviewer` с задачей «проверь итоговый PDF на сохранность структуры». Агент сам проверит количество страниц, метаданные, целостность аннотаций, выдаст отчёт.

## Визуальный diff двух PDF через diff-pdf

Бинарь `diff-pdf.exe v0.5.3` лежит в `~/.claude/bin/diff-pdf/diff-pdf.exe` (portable, не требует админа). Подсвечивает отличающиеся места попиксельно.

```powershell
# Просто отчёт о различиях (exit code 0 — идентичны, 1 — отличаются):
& "$HOME\.claude\bin\diff-pdf\diff-pdf.exe" v1.pdf v2.pdf

# С визуальным выходом в PDF (наложение красным):
& "$HOME\.claude\bin\diff-pdf\diff-pdf.exe" --output-diff=diff.pdf v1.pdf v2.pdf
```

Лицензия GPL-2.0 — допустимо как **внешний бинарь** через subprocess, **код не копировать** в наши инструменты.

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
| Визуальный diff | (нет MCP) | `diff-pdf.exe` portable |

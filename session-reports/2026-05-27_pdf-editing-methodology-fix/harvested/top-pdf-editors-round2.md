# PDF Editing Tools — Round 2 (harvest 2026-05-27)

## Контекст

Дополнение к round 1 (PyMuPDF / pikepdf / pdfcpu / qpdf / pdf-redactor). Ищем что
упустили — особенно MCP-серверы умеющие editing (не только read), CAD-aware
tools работающие через /OCProperties (OCG layers), и AI-assisted vision fallback.

Фокус — проектные PDF: чертежи AutoCAD/Revit (со штампами на отдельных layers),
ответы экспертизы, листы спецификаций. Источник критериев — `~/.claude/CLAUDE.md`
секция Harvest-workflow.

## По категориям

### Категория 1 — MCP servers для PDF editing

| Tool | URL | Stars | License | Editing? |
|---|---|---|---|---|
| `marc-hanheide/redact_mcp` | https://github.com/marc-hanheide/redact_mcp | 2 | Apache-2.0 | **Да** — PyMuPDF wrapper, `redact_text` / `redact_area` / batch + audit trail |
| `R09722akaBennett/nano-pdf-mcp` | https://github.com/R09722akaBennett/nano-pdf-mcp | 1 | MIT | Да, но через **Gemini 3 Pro cloud API** (GEMINI_API_KEY обязателен) — для нас off-limit (корп-проксь + конфиденциальность) |
| `alejandroBallesterosC/document-edit-mcp` | https://github.com/alejandroBallesterosC/document-edit-mcp | 49 | MIT | PDF — только **создание** из текста + Word→PDF. Existing PDF editing нет |
| `pdfdotco/pdfco-mcp` | https://github.com/pdfdotco/pdfco-mcp | n/a | Commercial | Wrapper над PDF.co SaaS — не local, отсеяно |

**Вывод по категории:** `redact_mcp` — единственный local-only MCP с реальным
PDF editing. Stars мало (2), но это тонкий wrapper над PyMuPDF — риска
архитектурного нет. **Можно адаптировать в наш `pdf-mcp` форк** (добавить
3 tool'а: redact_text, redact_area, apply_redactions) вместо отдельного сервера.

### Категория 2 — GUI editors с CLI/batch mode

| Tool | URL | License | CLI/batch |
|---|---|---|---|
| **LibreOffice Draw** (headless) | официальный | MPL-2.0 | `soffice --headless --convert-to pdf:draw_pdf_Export` + PageRange + skip-pages + watermark + password. Полный batch с loop через bash/PS |
| **Inkscape 1.4** | официальный | GPL-2.0 | Multi-page PDF с v1.2 (Save a copy → PDF). Shell mode для batch (`--shell`). Export-filename per-file |
| **Scribus + Scripter** | scribusproject/scribus + `sla2pdf` (7★) | GPL-2.0 / n/a | `--python-script` запускает скрипт и выходит. Python API через `scribus` module. Но: только one-way SLA→PDF, обратной конверсии нет |
| Master PDF Editor | proprietary | — | Исключено по ТЗ |
| Xournal++ | xournalpp/xournalpp | GPL-2.0 | Только annotations, content editing нет — отсеяно |

**Вывод по категории:** LibreOffice Draw — самый прагматичный fallback для
визуальной правки + batch. Inkscape multi-page рабочий, но GPL флагует
distribution. Scribus overkill для PDF (он DTP-tool, PDF — output format).

### Категория 3 — CAD-aware tools (/OCProperties manipulation)

| Tool | URL | Stars | License | OCG capability |
|---|---|---|---|---|
| **Coherent PDF (cpdf)** | https://github.com/johnwhitington/cpdf-source | **276** | **AGPL** или commercial | `-ocg-rename`, `-ocg-coalesce`, `-ocg-order-all`, list/extract. **Windows binary standalone (cpdf.exe)** в `cpdf-binaries`. Зрелый, mature OCaml-проект |
| **PyMuPDF OCG API** | (уже в стеке round 1) | — | AGPL/commercial | Full read/write/delete OCG, switch OC configs, change visibility. `doc.get_ocgs()`, `doc.set_oc()`, `set_oc_config()` |
| `freddy36/pdfocgtool` | https://github.com/freddy36/pdfocgtool | 1 | AGPL-3.0 | CLI: `--on layer_name` / `--off layer_name`. C# (.NET Core + itext7-dotnet). Тонкий, "quick and dirty" |
| `ABCpdf-Team/PDF-OCG-Layers` | https://github.com/ABCpdf-Team/PDF-OCG-Layers | малый | — | GUI viewer для OCG структуры, не CLI |

**Вывод по категории:** ОТКРЫТИЕ КРУГА — для штампов на отдельных OCG **не
надо** content stream surgery. AutoCAD при export маппит каждый AutoCAD layer
в PDF OCG. Достаточно один из:
- **PyMuPDF** (уже в стеке): `doc.set_oc_config_visibility(ocg_id, False)` —
  скрыть штамп без удаления содержимого. AGPL — но мы уже его используем.
- **cpdf** Windows CLI: для batch обработки без Python окружения — удобно
  для сотрудников ПТО на их машинах. AGPL флаг (если distribute — нужна
  commercial license; для in-house automation OK).

### Категория 4 — C/C++ libraries + Python bindings

| Tool | URL | Stars | License | Python? |
|---|---|---|---|---|
| **MuPDF / mutool** | https://github.com/ArtifexSoftware/mupdf | mature | AGPL/commercial | PyMuPDF (уже в стеке) — wrapper над MuPDF. `mutool clean -v` (vectorize text — превращает текст в paths, **анти-surveillance trick** для нечитаемого штампа после редакции). `mutool clean -tt` pretty-print, recent updates 2025 |
| **pypdfium2** | https://github.com/pypdfium2-team/pypdfium2 | 600+ | Apache-2.0 / BSD-3 | **ctypes bindings к Google PDFium**. Raw API через `pypdfium2_raw` к C functions. **Ограничение:** PDFium public API не даёт доступа к raw PDF dict/stream — только render/inspect/edit на content level. Для нашего use case (surgery низкоуровневая) слабее pikepdf |
| **PoDoFo** | https://github.com/podofo/podofo | 577 | LGPL/MPL (library), GPL (tools) | Нет официальных Python bindings (FAQ: "would be a fun Boost.Python project"). CLI tools "unsupported, untested, unmaintained" |
| **Ghostscript** | artifex/ghostscript | mature | AGPL/commercial | `gs -sDEVICE=pdfwrite` для flatten/sanitize. **Не делает text redaction напрямую** — только rasterize→back (через ImageMagick) или metadata stripping. Полезен как finish-stage flatten после редакции PyMuPDF чтобы текст не восстановился |

**Вывод по категории:** Главное открытие — `mutool clean -v` для **vectorize
text → paths**. После редакции PyMuPDF можно прогнать mutool чтобы оставшийся
текст превратился в кривые: невосстановимо OCR'ом, не выделяется, штампы
становятся "рисунком". Полезно для финальной выдачи где confidentiality важна.

pypdfium2 — Apache-2.0 лицензия (приятнее AGPL pikepdf), но raw dictionary
access ограничен. **Не замена pikepdf**, скорее дополнение если нужен render
без AGPL constraints.

PoDoFo отсеян: нет Python bindings, CLI unmaintained.

### Категория 5 — AI-assisted vision/layout

| Tool | URL | Stars | License | Применимость |
|---|---|---|---|---|
| **PaddleOCR PP-StructureV3** | https://github.com/PaddlePaddle/PaddleOCR | 50k+ | Apache-2.0 | PDF/image → DOCX export (через python-docx + PyMuPDF). 2025 update добавил DOCX export. **Use case:** старый скан-PDF экспертизы → DOCX → правка в Word → обратно в PDF. Не editing as such, но pipeline для конверсии в editable format |
| `Yashsonaar/LayoutLMv3-Fine-Tuning` | https://github.com/Yashsonaar/LayoutLMv3-Fine-Tuning | малый | — | Демо-проект, специфика invoices. Для proj-PDF переобучение нужно |
| Claude Computer Use | Anthropic | — | proprietary | Edge case для GUI driving Acrobat — overkill для batch |

**Вывод по категории:** PP-StructureV3 — **серьёзный кандидат** для fallback
когда PDF не parseable как vector (старые scan-PDF от экспертизы). Pipeline:
PaddleOCR → DOCX → Word правка → docx2pdf. Apache-2.0 зелёный, mature project.
Уже частично в нашем стеке (paddleocr в `image-text-replace` skill v3).

## TOP-3 неожиданных находок

1. **mutool clean -v (text vectorization)** — превращение текста в paths
   после редакции. Решает проблему "user скопировал текст из под чёрного
   прямоугольника". Для конфиденциальных правок ответов экспертизы —
   обязательный финальный шаг. Уже в нашем стеке (MuPDF под PyMuPDF), но
   мы это не использовали.

2. **OCG manipulation вместо content surgery** — если штамп AutoCAD на
   отдельном layer, достаточно `doc.set_oc_config_visibility(ocg_id, False)`
   через PyMuPDF. Не надо content stream редактировать. **Сначала проверять
   `doc.get_ocgs()` перед surgery**. Это меняет наш default workflow для
   AutoCAD-exported PDF.

3. **cpdf standalone Windows binary (cpdf.exe, 276★)** — стандартное OCaml-
   решение, no Python needed. Для сотрудников ПТО на их машинах без uv/pip
   окружения. AGPL для in-house OK. Команды `-ocg-rename`/`-ocg-coalesce`
   полезны когда чертежи мержатся из разных AutoCAD проектов и нужно
   сконсолидировать OCG.

## Что отсеяно и почему

- **PoDoFo** — нет Python bindings, CLI tools unmaintained. C++ библиотека,
  но нам нужен Python interop.
- **Master PDF Editor** — proprietary, исключено по ТЗ пользователя.
- **Xournal++** — только annotations, не content editing.
- **PDF.co MCP** — SaaS wrapper, requires API key, не local. Конфиденциальность
  проектных PDF не позволяет.
- **nano-pdf-mcp** — требует Gemini 3 Pro cloud API. Корп-прокси + проектные
  данные = не подходит.
- **document-edit-mcp** (49★) — PDF только create, не edit. Дезориентирующее
  название.
- **LayoutLMv3 invoice demos** — узкий fine-tuning под счета, не проектные
  чертежи.
- **Scribus full pipeline** — DTP-tool, PDF только output direction. Для
  proj-PDF editing неприменимо.
- **Ghostscript для redact** — не делает text redaction напрямую, только
  rasterize fallback. Полезен как finish flatten, но не как primary tool.

## Источники

- nano-pdf-mcp: https://github.com/R09722akaBennett/nano-pdf-mcp
- redact_mcp: https://github.com/marc-hanheide/redact_mcp
- document-edit-mcp: https://github.com/alejandroBallesterosC/document-edit-mcp
- pdfocgtool: https://github.com/freddy36/pdfocgtool
- PDF-OCG-Layers: https://github.com/ABCpdf-Team/PDF-OCG-Layers
- cpdf-source: https://github.com/johnwhitington/cpdf-source
- cpdf-binaries: https://github.com/coherentgraphics/cpdf-binaries
- coherentpdf.js: https://github.com/coherentgraphics/coherentpdf.js
- podofo: https://github.com/podofo/podofo
- MuPDF: https://github.com/ArtifexSoftware/mupdf
- pypdfium2: https://github.com/pypdfium2-team/pypdfium2
- sla2pdf: https://github.com/sla2pdf-team/sla2pdf
- PaddleOCR PP-StructureV3: https://github.com/PaddlePaddle/PaddleOCR
- LibreOffice headless docs: https://www.tutorialpedia.org/blog/how-to-create-a-pdf-a-from-command-line-with-libre-office-draw-in-headless-mode/
- Inkscape multipage: https://wiki.inkscape.org/wiki/Multipage
- PyMuPDF OCG: https://pymupdf.readthedocs.io/en/latest/recipes-optional-content.html

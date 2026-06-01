# PDF Workflow / Pipeline Tools — Round 3 (harvest 2026-05-27)

## Контекст
Поиск **workflow-level** решений (не библиотек) для batch перезамены штампов на 53+ листов сводного тома ПД (АХП Балашиха). Pipeline v12 на pikepdf+PyMuPDF уже работает per-page, но рассматриваем "снять задачу" целиком через DWG re-export или templating.

## По категориям

### Категория 1 — Self-hosted PDF processing platforms

**Stirling-PDF** (`Stirling-Tools/Stirling-PDF`, MIT, ~50k stars, релиз 2.9.0 апрель 2026). Особо релевантно: **"Automate" (бывш. Pipeline)** — no-code workflow builder + REST API `/api/v1/`, заявлено "process millions of PDFs". Имеет встроенные **Add Stamp**, **Add Watermark**, **Auto-Redact** инструменты. Docker self-hosted, фолдер-сканнер. **Минус для нас:** stamp-инструмент не surgically заменяет — он добавляет overlay поверх. Для "удалить старый штамп + вставить новый" нужны chained ops (redact-area → add-stamp) — это уже наш текущий подход, только через UI/REST. ([repo](https://github.com/Stirling-Tools/Stirling-PDF), [Pipeline docs](https://docs.stirlingpdf.com/Configuration/Pipeline/))

**pdftl** (`pdftl/pdftl`, MIT, новый pdftk-замена на pikepdf+qpdf). Поддерживает chaining через `---`, **regex text replacement** и **arbitrary content stream injection**. Прямой successor pdftk с CLI-совместимостью. Активен в 2026.

**pdfly** (`py-pdf/pdfly`, BSD, в py-pdf umbrella). CLI на pypdf. Минималистичен — для surgery не дотягивает.

**Apache PDFBox CLI** (`pdfbox-app`, Apache-2.0, industry standard). `OverlayPDF` команда: `OverlayPDF input.pdf overlay.pdf output.pdf` + `-page N file.pdf` для per-page overlays. **Идеально для batch overlay**, но не для замены существующего штампа (только наложение).

### Категория 2 — Vector round-trip (PDF → SVG → PDF)

**pdf2svg** (`dawbarton/pdf2svg`, GPL-2, не активен с 2019, заменён `pdftocairo` из Poppler). Per-page → SVG.

**pysvg2pdf** (Rust extension, MIT) — SVG → embedded Form XObject в PDF. Активен.

**Inkscape CLI batch mode** (`--batch-process`, shell mode, GPL). Может массово open/edit/save SVG, **но XML find/replace проще сделать sed/Python напрямую**.

**Проблема round-trip:** pdf2svg+pdftocairo конвертируют **текст в paths** для верности рендера → теряем возможность text-find-replace штампа. Если штамп — выделенный layer/Form XObject в исходном PDF, можно править его OCG (Optional Content Group) **без round-trip** через pikepdf — но это уже наш v12. Round-trip даёт преимущество только если штамп — text, а не path.

### Категория 3 — Template engines (полная пересборка страницы)

**WeasyPrint** (BSD, активен) — HTML+CSS → PDF, paged media. Хорошо для генерации с нуля.

**ReportLab Platypus** (BSD/коммерч., активен) — программная вёрстка, Flowables.

**pdfme** (TypeScript, MIT) — для динамических PDF из JSON-template.

**Применимость для нас:** низкая. Сводный том ПД содержит чертежи (vector graphics из CAD), формулы, scan-вставки. Re-render через WeasyPrint = потеря CAD-vector-точности. Подходит **только для текстовых разделов ПЗ**, не для чертёжных листов.

### Категория 4 — DocX/HTML → PDF с штампом как overlay

**docx2pdf / Pandoc / LibreOffice CLI** для конвертации, потом overlay через PDFBox OverlayPDF / pikepdf. Подходит **только если у нас есть исходный DocX/HTML**. Для финального тома, собранного из CAD-чертежей разных авторов, это переписывание workflow с нуля — не для текущей задачи.

### Категория 5 — CAD re-export workflow ⭐ **GAME CHANGER**

**Hurricane** (74mph.com, коммерческий, ~$200, AutoCAD 2026 + LT + BricsCAD + ZWCAD compat). **Title-Block Update Wizard**: "change a date in the title block across 1500 drawings in minutes of setup vs 50+ hours manually" + Batch Plot Wizard для re-export DWG → PDF. **Closed-source, не open-source, но industry de-facto для русских/западных ПТО.** ([74mph.com/features.html](https://74mph.com/features.html))

**Lee Mac UpdateTitleBlock** (AutoLISP, free, [lee-mac.com](https://www.lee-mac.com/updatetitleblock.html)). Читает CSV (filename → attribute values), обновляет блоки автоматически при открытии DWG. **Free, mature (10+ лет), широко используется**. Лицензия — Lee Mac личная (use freely, no redistribute). Pairing с AutoCAD `PUBLISH` (батч-плот) → закрывает задачу полностью.

**Workflow:** `(DWG исходники) → Lee Mac CSV update → AutoCAD PUBLISH → batch PDF`. Время на 53 листа: **5-10 мин setup + 15-30 мин plot**.

**ezdxf** (`mozman/ezdxf`, MIT, активен, v1.4.4 май 2026). Python для DXF (не DWG напрямую — нужен ODA File Converter DWG↔DXF). Можно скриптом найти INSERT блока штампа в layout, обновить ATTRIB, сохранить. **Custom-code, но Python-native и free.**

**Критический вопрос для пользователя:** **есть ли доступ к исходным DWG?** Если есть — категория 5 снимает PDF surgery полностью. Если нет (получили только PDF от подрядчика) — категория 5 неприменима.

### Категория 6 — Stamp-specialized libraries

**pyHanko** (`MatthiasValvekens/pyHanko`, MIT, активен, релиз май 2026). `pyhanko.stamp` модуль: text/QR/image/imported-PDF stamps. **Это overlay (как PDFBox), не surgical replace.** Для нас полезен только если откажемся от "redact старого + insert новый" в пользу "просто overlay новый поверх старого" — но это юридически сомнительно (старая инфа остаётся в PDF под layer'ом).

**iText 7 Community** (AGPL-3.0, Java). **GPL/AGPL флаг** — копирует виральность лицензии в наш код. Не берём без коммерческой лицензии (~$1500+/year).

### Категория 7 — AI-pipeline для batch

**Anthropic Computer Use API** (доступно с 2024, в 2026 — Claude Cowork + Claude Code на Windows для Pro/Max). Может управлять Acrobat / CAD GUI как человек. **Дорого по токенам, медленно для batch 53**, ненадёжно для production. Подходит для одноразовых задач, не для повторяемого pipeline.

**langchain pdf / llamaindex pdf** — для извлечения, не для редактирования. Off-topic.

**ML-классификация листов A0/A1/A3** — реализуемо через OpenCV+heuristics на bbox страницы (`page.mediabox`), AI overkill. Решается за 10 строк Python.

## TOP-3 game-changer находок

1. **Hurricane + Lee Mac UpdateTitleBlock (Категория 5)** — если есть DWG-исходники, **полностью снимает задачу PDF surgery**. Workflow: CSV с новыми значениями штампа → batch update DWG → batch plot → готовые PDF. Time saved: десятки часов на каждый том ПД. **GPL-флаг: нет** (Lee Mac свободен; Hurricane коммерческий, ~$200/seat, окупится за один том).

2. **Stirling-PDF Pipeline + REST API (Категория 1)** — если DWG нет, no-code orchestration `redact-area → add-stamp → save` через self-hosted UI. **MIT, free, Docker**. Заменяет наш Python pipeline v12 на graphical workflow, упрощает передачу методики коллегам в ПТО.

3. **Apache PDFBox `OverlayPDF` (Категория 1)** — если задача переформулируется как "вставить новый штамп **поверх** старого после redact" вместо "edit existing", это однокомандный batch через Java CLI: `for f in *.pdf; do java -jar pdfbox-app.jar OverlayPDF $f stamp.pdf $f.new; done`. Industry standard, Apache-2.0.

## Сводная рекомендация

**Для batch 53+ листов оптимально проверить наличие исходных DWG.**

- Если **DWG есть** → Категория 5 (Lee Mac UpdateTitleBlock + AutoCAD PUBLISH или Hurricane Title-Block Wizard). Это снимает проблему PDF surgery целиком, штамп всегда корректен в source-of-truth, переплот идёт штатным AutoCAD-инструментом без потерь. Pipeline v12 остаётся только для legacy PDF без исходников.
- Если **DWG нет** (только финальный PDF от подрядчика) → текущий v12 (pikepdf+PyMuPDF) остаётся, но обернуть в **Stirling-PDF Pipeline** для UI коллегам в ПТО или мигрировать на **PDFBox OverlayPDF** для batch CLI.

**Открытый вопрос пользователю:** доступны ли исходные DWG листов сводного тома АХП Балашиха? Это определяет выбор между категорией 5 (системное решение) и улучшением текущего v12 (категории 1+6).

## Что отсеяно

- **Категория 2 (PDF→SVG→PDF round-trip)** — текст конвертируется в paths, теряется find-replace. Polluption быстрее чем surgery.
- **Категория 3 (WeasyPrint/Platypus)** — не для CAD-чертёжных листов, только для текстовых разделов ПЗ.
- **Категория 4 (DocX→PDF + overlay)** — требует переписать весь workflow создания тома; для уже сданного PDF неприменимо.
- **iText 7 (Категория 6)** — AGPL-3.0 виральная, дорогая коммерч. лицензия.
- **Computer Use API (Категория 7)** — медленно, дорого, ненадёжно для production batch.
- **pdf2svg** (Категория 2) — не активен с 2019, заменён pdftocairo, и тот не решает проблему path-конверсии.

---

**Источники:**
- [Stirling-PDF](https://github.com/Stirling-Tools/Stirling-PDF), [Pipeline docs](https://docs.stirlingpdf.com/Configuration/Pipeline/)
- [pdftl](https://github.com/pdftl/pdftl), [pdfly](https://github.com/py-pdf/pdfly)
- [Apache PDFBox OverlayPDF](https://pdfbox.apache.org/2.0/commandline.html)
- [pyHanko](https://github.com/MatthiasValvekens/pyHanko), [stamp docs](https://docs.pyhanko.eu/en/latest/cli-guide/stamping.html)
- [Hurricane Title-Block Wizard](https://74mph.com/features.html)
- [Lee Mac UpdateTitleBlock](https://www.lee-mac.com/updatetitleblock.html)
- [ezdxf](https://github.com/mozman/ezdxf)
- [Anthropic Computer Use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [iText Community AGPL](https://itextpdf.com/how-buy/AGPLv3-license)

# Harvest: редакторы векторного PDF (реальное удаление, не overlay)

Дата: 2026-06-02. Контекст: провал surgery/overlay на штампах чертежей (см. сессии
2026-05-22/27 АХП). Нужен инструмент, который физически удаляет текст+линии
content-stream, локально, приемлемая лицензия.

## Категория 1 — идеальная возможность, но cloud/коммерция (off-limit под наши ограничения)

### PDFDancer (pdfdancer.com)
- **URL:** https://github.com/MenschMachine/pdfdancer-client-python (client), движок — https://api.pdfdancer.com
- **Stars:** 0 (новый, создан 2025-09, активен — pushed 2026-06-02). License клиента: Apache-2.0; движок — коммерческий.
- **Что делает:** ровно под нашу боль — «edit text in real-world PDFs you didn't create, move images, reposition headers, delete vector paths, real structure editing, не overlay». API: `select_paragraphs`, `select_images`, vector paths, `.delete()`, `.move_to()`, `.redact()`, `.edit()`.
- **Pricing:** Free 200 стр/мес **с watermark** + cloud. Pro $199/мес. **Self-host/on-prem только Enterprise (custom цена).**
- **Вердикт:** off-limit как cloud (конфиденциальность чертежей + прокси). Free бесполезен (watermark). **Enterprise on-prem = деньги, procurement-решение фирмы.** Можно валидировать возможности на синтетическом (неконфиденциальном) штампе через free tier.

### Nutrient Python SDK (ex-PSPDFKit) / Apryse (ex-PDFTron) Redactor
- **Что делает:** structural redaction — физически удаляет из content stream текст/картинки/вектор (не overlay/clip). Локальный install (Nutrient `pip install`).
- **Вердикт:** **коммерческие, платные.** Технически решают. Тоже procurement.

## Категория 2 — локально + open-source, способны, но надо «водить»/скриптовать

### Inkscape (GPL-3.0) — лучший свободный кандидат
- **URL:** https://inkscape.org (исходники на GitLab). Local, Windows.
- **Возможности:** настоящий векторный редактор. CLI: `--actions="select:ID; delete; export-do"`, shell-режим, `inkex.command.inkscape()` Python-API для скриптинга. Импорт PDF: `--pdf-poppler` (текст → группы glyph-paths — для УДАЛЕНИЯ штампа норм; для in-place правки текста хуже).
- **Action `delete`** подтверждён в action-list (wiki.inkscape.org/wiki/Action).
- **Вердикт:** реально удаляет объекты, локально, скриптуемо. **Но это «освоить vector-драйвер» — тот же класс усилий, что AutoCAD-проект.** Лицензия GPL — флаг (не копировать код в installer; вызывать как внешний бинарь — ок).

### LibreOffice Draw (MPL-2.0) — чистая лицензия
- Local, headless (`soffice --headless`), открывает PDF как вектор, UNO/Python-макросы.
- «Лучше для minor edits», сложная реструктуризация слабее.
- **Вердикт:** чище по лицензии (MPL), но слабее Inkscape на сложных чертежах и UNO-скриптинг муторнее.

### Apache PDFBox (Apache-2.0) — низкоуровневый
- Java. Прямая правка content stream (add/remove/modify). Чистая лицензия.
- **Вердикт:** clean license, но Java + ручная content-stream хирургия = высокая сложность, та же зона риска что pikepdf.

## Категория 3 — провалившиеся / не то
- **PyMuPDF** `apply_redactions(graphics=N)` — AGPL; **не пробивает Form XObjects** (наш кейс). Известный провал.
- **pikepdf clip-path** — прячет, не удаляет. Провал.
- **JSv4/PdfRedact, hasff/...redactor** — конвертируют страницу в растр + чёрные прямоугольники → теряют вектор. Не то.

## Итог harvest
Свободного **turnkey** инструмента нет. Развилка:
1. **Платно/on-prem** (PDFDancer Enterprise / Nutrient) — «просто работает», решает дневную боль, но деньги + procurement.
2. **Свободно/локально** (Inkscape CLI/inkex) — жизнеспособно, но «освоить драйвер» = отдельный проект (как AutoCAD).
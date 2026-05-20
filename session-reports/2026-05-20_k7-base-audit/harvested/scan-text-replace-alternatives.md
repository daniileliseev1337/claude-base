# Harvest: альтернативы для scan-text-replace pipeline

**Контекст.** Заменить/усилить нашу цепочку EasyOCR -> LaMa -> Pillow render -> SD strength=0.10. Боль — 22+ итераций tuning из-за нестабильного per-cell font_size, midline alignment, пропуска font calibration, surgical positioning. Поиск 2026-05-20.

## Сводная таблица (3-5 финалистов после фильтра)

| Имя | Кат. | URL | Last commit | Stars | License | Что даёт нам | Стоимость интеграции |
|---|---|---|---|---|---|---|---|
| **PaddleOCR (PP-StructureV3)** | A+B | https://github.com/PaddlePaddle/PaddleOCR | 2026-05-19 | 78 228 | Apache-2.0 | Детектор + распознаватель + layout/table cells + font-attribute hints одним пайплайном. Bbox стабильнее EasyOCR, плюс типизация регионов (table cell / header / body) -> убирает 2 источника noise сразу. | Средняя: pip install paddleocr + paddlepaddle CPU/GPU. ONNX-экспорт уже готов. RU поддерживается через multi-lingual модель (cyrillic). |
| **DocTR (mindee)** | A | https://github.com/mindee/doctr | 2026-05-12 | 6 088 | Apache-2.0 | Production-grade OCR с word-level polygon bbox (не axis-aligned rectangle как у EasyOCR). Точечная drop-in замена OCR-стадии. PyTorch + TF backends. | Низкая: `pip install python-doctr[torch]`. API близок к EasyOCR, маппинг bbox + text прямой. |
| **RapidOCR** | A | https://github.com/RapidAI/RapidOCR | 2026-05-18 | 6 605 | Apache-2.0 | ONNX-обёртка PP-OCR моделей. Без paddlepaddle-deps, в 3-5x быстрее PaddleOCR на CPU. Bbox стабильность та же что у PaddleOCR (те же веса). | Низкая: `pip install rapidocr-onnxruntime`. Если PaddleOCR покажет качество но окажется тяжёлым — мигрируем сюда без потери точности. |
| **Tesseract 5 + tesserocr** | A | https://github.com/tesseract-ocr/tesseract | 2026-04-27 | 74 192 | Apache-2.0 | LSTM движок, **возвращает font-attribute hints (bold/italic/serif)** через hOCR/TSV вывод — именно та переменная которую мы вручную калибруем. Word-level confidence + baseline coordinates стабильнее EasyOCR. | Средняя: Tesseract installer Windows + `pip install tesserocr` (или pytesseract). RU traineddata качается отдельно. C++ engine — нужен .exe в PATH. |
| **AnyText** | C | https://github.com/tyxsspa/AnyText | 2025-03-07 | 4 851 | Apache-2.0 | End-to-end text **editing** в изображениях через ControlNet+SD (text glyph + position + masked image). Заменяет наши стадии LaMa+Pillow+SD одной моделью обученной именно на edit-задачу. | Высокая: conda env, ручная установка, нет pip-пакета, нужны SD веса + AnyText checkpoint. Но снимает midline+font_size+calibration сразу. |

**Все 5 кандидатов прошли фильтр:** активны (последний коммит < 12 мес), >= 200 stars (минимум 4851), permissive license (Apache-2.0).

## Recommendation #1 (низкий риск, точечная замена) — **DocTR**

Drop-in замена только OCR-стадии. Pipeline остаётся тот же (DocTR -> LaMa -> Pillow -> SD), меняется один модуль. **Что чинит:** word-level polygon bbox вместо axis-aligned rectangle убирает ±2-3px noise по cap_height — это первопричина per-cell font_size variance в нашей боли #1. API близок к EasyOCR (`detector.predict(img)` -> list of words + polygons), маппинг тривиальный. Apache-2.0, Mindee — production maintainer (commercial OCR API), активность отличная. Риск отката минимальный: если не зайдёт за 1 день — возвращаем EasyOCR одной строкой.

## Recommendation #2 (балансированный, средняя сложность) — **PaddleOCR PP-StructureV3**

Заменяет **две** наши стадии: OCR + layout analysis. Возвращает не просто слова с bbox, а типизированные регионы (table cell / header / paragraph) и table structure. Это позволяет: (а) брать font_size из медианы по cell, а не по одному слову — убираем per-cell variance, (б) знать что мы внутри table cell -> применять surgical positioning относительно cell bounds, а не свободно. Cyrillic через multi-lingual model. Стоимость средняя из-за paddlepaddle dep, но если позже захочется уйти от него — RapidOCR использует те же веса в ONNX. Это **best ROI** для нашей боли: bbox+layout одним инструментом, 2 источника шума убираются одним API.

## Что НЕ брать и почему

- **Surya** (datalab-to/surya, 19 760 stars) — **GPL-3.0**. Виральная лицензия портит installer (claude-base private но мы раздаём через manifest). По нашему правилу CLAUDE.md "GPL — флаг для согласования" — отмечено, но при наличии Apache-2.0 альтернатив (PaddleOCR, DocTR) выбора нет. Качество отличное, но цена слишком высокая.
- **MinerU** (opendatalab/MinerU, 64 151 stars) — **custom-restricted license** (Apache-2.0 base + коммерческие ограничения >100M MAU / >$20M revenue + public attribution mandatory). Наши объёмы под лимиты, но attribution mandatory — флаг для согласования. Плюс MinerU заточен на "PDF -> markdown/JSON для LLM", а не на pixel-perfect editing с сохранением scan-look — это не наша задача.
- **Donut, LayoutParser, DocOwl** — отброшены без detail: Donut last push 2024-07 (>12 мес), LayoutParser last push 2024-08 (граница, но менее активен чем PaddleOCR который покрывает ту же нишу), DocOwl — multimodal LLM для понимания документов, не для editing.

## Открытые вопросы для следующей сессии

1. Стоит ли тестировать **AnyText** в sandbox? Потенциально снимает всю нашу боль сразу, но conda-only и тяжёлый. Сначала проверить — поддерживает ли он cyrillic в editing-mode.
2. **Tesseract 5** font-attribute output — реально ли возвращает bold/serif hints для русского traineddata, или только для eng? Это критично для font calibration #3.
3. Сравнительный benchmark на нашем эталонном скане (КП К7 АХП): EasyOCR baseline vs DocTR vs PaddleOCR — метрика bbox-stability по cap_height variance внутри одного cell.

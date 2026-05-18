# docling

- **URL:** https://github.com/docling-project/docling
- **Категория:** OCR / Document Understanding (универсальный конвертер)
- **Stars:** ~59.9k
- **Last commit:** 2026-05-07 (v2.93.0)
- **License:** MIT
- **Описание:** «Get your documents ready for gen AI» — от IBM Research Zurich. PDF/DOCX/PPTX/XLSX/HTML/WAV/MP3 → Markdown/HTML/JSON/DocTags. Интегрирован с LangChain, LlamaIndex, Haystack.

## Зачем смотрели
Универсальный пайплайн с **самой чистой лицензией (MIT)** и поддержкой максимума форматов входа. Если первичка приходит не только сканами, но и оригинальными DOCX/XLSX — это плюс.

## Оценка
- **Подходит?** Да
- **Сильные стороны:**
  - **MIT** — лучшая возможная лицензия
  - Огромное покрытие форматов (включая исходные DOCX/XLSX без OCR)
  - Свой VLM (GraniteDocling)
  - Lossless JSON, table structure, reading order, formulas
  - Готовая MCP-обёртка — можно вызывать прямо из Claude Code
  - От IBM — серьёзная техподдержка
- **Слабые стороны / риски:**
  - Меньше сфокусирован именно на «низкокачественных сканах УПД» — больше на «нормальных» документах
  - Granite VLM моложе MinerU 2.5 — на специфике русских табличных форм надо тестировать
  - Может быть избыточен для одной задачи (УПД), если входы — только сканы PDF
- **Решение:** Кандидат №2 в категории OCR. Если входы — смесь сканов и нативных DOCX/XLSX — docling выигрывает за счёт лицензии и универсальности. Если входы — только сканы — MinerU/PaddleOCR быстрее.

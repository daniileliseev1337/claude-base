# jztan/pdf-mcp
- URL: https://github.com/jztan/pdf-mcp
- Stars: 35
- Last commit: 2026-05-12
- License: MIT
- Описание: MCP-сервер для AI-агентов: chunked reading больших PDF, hybrid search (BM25+semantic via RRF), Tesseract OCR, table/image extraction, SQLite cache.

## Зачем смотрели
Возможно более мощный MCP-сервер чем наш текущий pdf-mcp.

## Оценка
- Подходит для нашей проблемы? **Под условием** (тот же набор tool-ов, но плюс OCR и hybrid search).
- Сильные стороны:
  - **MIT**.
  - Тот же набор tools (`pdf_info`, `pdf_read_pages`, `pdf_search`, `pdf_render_pages`) — drop-in совместимость.
  - **Hybrid search BM25+semantic** — этого у нас нет.
  - SQLite cache.
  - OCR через Tesseract — но для нас не плюс (наш блокер).
  - Активная разработка (2026-05-12).
- Слабые стороны / риски:
  - Мало звёзд (35) — нишевый проект, проверить надёжность.
  - Tesseract dependency = тот же блокер.
  - Не решает text-in-curves фундаментально (просто другой движок).
- Решение: **держим в уме**. Имя `pdf-mcp` совпадает с нашим (возможно, это и есть тот же проект?). Стоит сравнить API и решить — мигрировать или нет.

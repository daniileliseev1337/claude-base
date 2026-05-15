# rsp2k/mcp-pdf
- URL: https://github.com/rsp2k/mcp-pdf
- Stars: 7
- Last commit: 2026 (50 commits на main)
- License: MIT
- Описание: FastMCP-сервер с 47 инструментами: text extraction, OCR, tables (camelot+pdfplumber+tabula fallback chain), forms, annotations, markdown↔PDF.

## Зачем смотрели
Самый широкий MCP-сервер по фичам (47 tools, fallback-цепочки между либами).

## Оценка
- Подходит для нашей проблемы? **Под условием** (богатый функционал, но 7 ★ — риск качества).
- Сильные стороны:
  - **MIT**.
  - Fallback chain для текста: PyMuPDF → pdfplumber → pypdf.
  - Fallback chain для таблиц: Camelot → pdfplumber → Tabula.
  - Form handling (read/fill/create) — полезно для актов и заявок.
  - Annotation tools.
  - SVG export vector graphics.
- Слабые стороны / риски:
  - **Очень мало звёзд (7)** — проект свежий, не проверенный.
  - Tesseract как единственный OCR — наш блокер.
  - Зависит от Ghostscript (Camelot) + Java (Tabula).
  - 47 tools — потенциально переусложнено для агента, легко потеряться.
- Решение: **держим в уме как референс архитектуры** (fallback-chains между либами — хорошая идея). В прод не берём из-за низкой проверенности.

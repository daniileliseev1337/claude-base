# mcp-pdf (rsp2k)

**URL:** https://github.com/rsp2k/mcp-pdf
**Stars:** 7
**Last commit:** 2026-05-05 (свежий — 10 дней назад)
**License:** MIT
**Тип:** MCP-сервер (Python 3.11+, FastMCP 2.0+)

## Что делает

Самый широкий по фичам из встреченных PDF-MCP. Local-only обработка через стек проверенных Python-библиотек:
- Чтение: PyMuPDF / pdfplumber / pypdf (с автоматическим fallback)
- Таблицы: Camelot / pdfplumber / Tabula
- OCR: Tesseract
- Конвертации: Pandoc + TeX engine

Для **редактирования** заявлены:
- **Merge** с сохранением закладок
- **Split** по диапазону страниц или по закладкам
- **Reorder pages**
- **Form fields**: extract, fill, **create new fillable forms** (это редкость — обычно MCP умеют только заполнять)
- **Annotations**: sticky notes, highlights, stamps
- **Markdown ↔ PDF** конвертация в обе стороны

## Почему подходит нам

Это самый полный матч под наш список задач: merge/split/forms/annotations — всё закрыто из коробки одним сервером, локально, без облака. Свежий релиз — автор активно ведёт проект (последний коммит 2026-05-05).

## Как подключить

```powershell
uvx mcp-pdf
```

Если правильно опубликован на PyPI — это команда для `claude mcp add`:
```powershell
claude mcp add mcp-pdf-edit uvx mcp-pdf
```

(Перед использованием — `uvx mcp-pdf --help` для прогрева кэша, по нашей практике с MCP на Windows.)

## Подводные камни

- **7 stars** — низкая популярность, репутация автора не установлена. Может быть забыт через полгода. Тестировать в Windows Sandbox до доверия.
- **Тяжёлые внешние зависимости** для полного функционала:
  - **Tesseract** (OCR) — нужно ставить отдельно через установщик UB-Mannheim
  - **Poppler-utils** — `poppler-windows` через conda или scoop
  - **Ghostscript** — для Camelot (таблицы)
  - **Java runtime** — для Tabula (таблицы)
  - **Pandoc + TeX** — для markdown_to_pdf
  
  Без этих компонентов **базовые** операции (merge/split/forms) **должны** работать на чистом PyMuPDF+pypdf, но это нужно проверить.
- README не показывает известных issues, но и тестов / CI публично не видно — production-readiness заявленная, проверять надо.
- Пересечение с уже подключённым `pdf-mcp` (uvx) — функционал чтения дублируется. Стоит понять, не будет ли конфликта namespaces; вероятно нет, т.к. имена tools уникальны.

## Вердикт

✅ **Брать как первый кандидат для подключения**, с оговорками:
1. Поставить в Windows Sandbox / отдельный venv, проверить что merge/split/fill_form действительно работают на нашем тестовом PDF.
2. Если без Ghostscript/Tesseract сервер падает на старте — отказаться.
3. Если базовые операции работают — подключить через `claude mcp add` и оставить рядом с уже работающим `pdf-mcp` для чтения.

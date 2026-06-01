# Morph — morphllm.com

## Источник
- URL: https://docs.morphllm.com/introduction
- Коммерческий сервис (не GitHub)
- Прислал пользователь как «8-я позиция». Контекст: «по работе с файлами
  огромные проблемы — Word и PDF, постоянные косяки на простых задачах».

## Что это
Toolkit для AI coding agents (НЕ один model):
- **Fast Apply** — быстрое применение code-правок (10,500 tok/s, 98% accuracy)
- **WarpGrep** — поиск по кодбазе (#1 на SWE-Bench Pro)
- **Compact** — сжатие контекста
- Интеграция: MCP (`npx @morphllm/morph-setup`) → добавляет `edit_file` +
  `codebase_search` tools.

## ⚠ Ключевое: НЕ решает Word/PDF
Прямая цитата docs: «Morph handles **code and text files only — not binary
formats like Word or PDF**.»
- Заточен под исходный код (.ts примеры, language-agnostic для text source).
- Word/PDF — бинарные форматы, Morph их не трогает.
- **Проблему пользователя (Word/PDF косяки) НЕ решает.**

## Pricing (constraint check)
| Plan | Price | Credits | Requests |
|---|---|---|---|
| **Free** | $0 | 250K | **200/мес** |
| Starter | $20/мес | 3M | — |
| Pro | $60/мес | 10M | — |

Free tier есть, но мизерный (200 req/мес). Constraint «подписки не покупаются»
→ только free tier = непрактично для регулярной работы.

## Вердикт
⚫ **Пропускаем.**
1. Не решает заявленную боль (Word/PDF — код-only).
2. Для developer-кода (python skills): free tier 200 req/мес ничтожен,
   объём code-editing не оправдывает, built-in Edit справляется.
3. WarpGrep (codebase search) — у нас Grep работает, не нужен.

## ГЛАВНОЕ: проблема Word/PDF — отдельный приоритет
Пользователь поднял системную боль: косяки с Word/PDF на простых задачах.
Среди 9 плагинов решения нет (Morph=код, Codeburn=токены).

**Текущий наш стек Word/PDF:**
- Word: `word` MCP (python-docx), `markitdown`, `document-loader`
- PDF: `pdf-mcp`, `markitdown`, `document-loader`, `image-text-replace` (OCR)
- Python: python-docx, openpyxl, pikepdf, pdfplumber, easyocr
- Skills: `word-helper`, `pdf-helper`

**Нужна ДИАГНОСТИКА перед решением (не выдумывать):**
1. Word или PDF чаще косячит?
2. Какие задачи? (замена текста / шаблон / извлечение таблиц / генерация /
   OCR скана / форматирование)
3. Что ломается? (форматирование слетает / таблицы кривые / плейсхолдеры /
   порядок текста / кодировка / падает с ошибкой)
4. Конкретный свежий пример (файл + задача) для воспроизведения.

**План:** после #9 — прицельный разбор Word/PDF (возможно отдельный harvest
под docx/pdf инструменты ИЛИ фикс наших word-helper/pdf-helper skills).
Приоритет ВЫШЕ половины плагинов из списка.

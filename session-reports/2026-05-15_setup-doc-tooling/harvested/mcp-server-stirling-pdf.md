# mcp-server-stirling-pdf

**URL:** https://github.com/gufao/mcp-server-stirling-pdf
**Stars:** 1
**Last commit:** 2025-12-18
**License:** GPL-3.0 (флаг — вирусная лицензия, см. ниже)
**Тип:** MCP-сервер (TypeScript/Node.js 20+), фронтенд к **Stirling-PDF** Docker-бэкенду

## Что делает

Тонкий MCP-обёртка над **Stirling-PDF** (https://github.com/Stirling-Tools/Stirling-PDF, **78 769 stars**, активный) — open-source self-hosted веб-сервис для PDF. Сам MCP не делает работу с PDF своими силами: он HTTP-вызывает endpoint'ы Stirling-PDF, который и есть мощный движок (Java + LibreOffice + qpdf + Ghostscript + Tesseract внутри Docker-образа). Из коробки 10 операций.

## Почему подходит нам

Закрывает основной набор задач:
- **Merge** — объединение нескольких PDF
- **Split** — разделение по указанным страницам
- **Compress** — оптимизация размера
- **Convert PDF↔images** (PNG/JPG/GIF)
- **Rotate** — поворот страниц
- **Watermark (text)** — добавление текстовых водяных знаков
- **Remove pages** — удаление страниц
- **Extract images** — извлечение изображений
- **OCR** — оптическое распознавание

**Чего нет:** редактирование AcroForm форм, аннотации, перекраска объектов — Stirling-PDF этим занимается ограниченно.

## Как подключить

Не одной командой, путь длинный:

1. Поднять Stirling-PDF в Docker:
   ```powershell
   docker run -d --name stirling -p 8080:8080 frooodle/s-pdf:latest
   ```
2. Склонировать MCP-обёртку и собрать:
   ```powershell
   git clone https://github.com/gufao/mcp-server-stirling-pdf
   cd mcp-server-stirling-pdf
   npm install
   npm run build
   ```
3. Прописать в Claude Code MCP-конфиге путь к собранному node-скрипту + env-переменную с URL Stirling-PDF (`http://localhost:8080`).

Готового `uvx` / `npx` пакета **нет**.

## Подводные камни

- **GPL-3.0** — для нашего внутреннего использования OK, но если когда-нибудь захотим вкладывать код в `~/.claude/skills/` или `~/.claude/agents/` — GPL заразит. **Код из репо не копировать**.
- **Docker обязателен** — у пользователя Windows 11 без Docker Desktop этот вариант не запустится. Docker Desktop требует лицензии для коммерческого использования (>$10M revenue / >250 employees).
- **Сборка из исходников** (npm + tsc), нет публичного npm-пакета — обновления вручную.
- **1 star** = низкая популярность самого MCP-врапера, поддержка может пропасть. Но базовый Stirling-PDF огромный, движок надёжный.
- README отмечает известные баги: `colorString is null` для watermark (вроде починили в v1.1.0), HTTP 400/500 от Stirling-PDF при нестрогом формате параметров.
- **Из коробки нет form-fill, аннотаций** — самые востребованные нами операции с PDF-формами эта связка НЕ закрывает.

## Вердикт

⚠️ **Брать только если уже есть Stirling-PDF в Docker и нужны merge/split/watermark/rotate без AcroForm.** Для типового рабочего стола Windows без Docker — overhead слишком большой ради 8 базовых операций. Если хочется именно функциональность Stirling-PDF — лучше подключить его веб-UI напрямую, без MCP-прослойки.

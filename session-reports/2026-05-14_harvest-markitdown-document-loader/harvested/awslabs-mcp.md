---
name: awslabs-mcp
description: AWS Labs monorepo с MCP-серверами, включая document-loader — основной кандидат и одновременно текущий в нашей конфигурации
---

# awslabs/mcp

- **URL:** https://github.com/awslabs/mcp
- **PyPI (нужный пакет):** https://pypi.org/project/awslabs.document-loader-mcp-server/
- **Stars (весь monorepo):** ~9k
- **Last commit:** активный (релизы регулярно, document-loader v1.0.16 от 2026-05-09)
- **License:** Apache-2.0
- **Описание:** Универсальный MCP для парсинга PDF/DOCX/XLSX/PPTX/изображений + уникальный `extract_slides_as_images` (PNG-рендер слайдов через LibreOffice + poppler).

## Зачем смотрели

В сессии 2026-05-14 deferred-список tools показывал document-loader как «still connecting», и быстрый тест я провёл с неверным именем (`mcp-document-loader` вместо `awslabs.document-loader-mcp-server`). Это породило ложное заключение «пакет не найден».

## Оценка

- **Подходит? Да — это и есть наш текущий сервер.**
- Корректное имя пакета: `awslabs.document-loader-mcp-server` (с точкой — namespace style).
- Корректный вызов из конфига: `uvx awslabs.document-loader-mcp-server@latest`.
- Первый холодный запуск ~30 сек (74 пакета), потом из кэша мгновенно.
- Зависимости для PNG-рендера слайдов: **LibreOffice + poppler** должны быть в PATH. Без них `extract_slides_as_images` упадёт.
- License Apache-2.0 — зелёный свет на копирование/адаптацию кода при необходимости.
- Решение: **оставляем как есть, ничего не меняем**. Если будет падать дальше — проверить (а) наличие LibreOffice/poppler, (б) прогреть кэш командой `uvx awslabs.document-loader-mcp-server@latest --help`.

## Уроки

1. **Не тестировать «короткими именами» MCP-пакетов** — у AWS Labs формат `awslabs.<server-name>` с точкой. Брать имя ровно из `claude mcp list`.
2. **MCP-сервер на `--help` не печатает usage, а запускает stdio-loop.** Это нормально. Чтобы проверить запускаемость — смотреть на стартовый баннер FastMCP, а не на exit code 0.
3. **Холодный старт uvx ≠ «сервер сломан».** 74 пакета markitdown / document-loader тянутся минуту впервые. Прогрев один раз → все следующие сессии быстрые.

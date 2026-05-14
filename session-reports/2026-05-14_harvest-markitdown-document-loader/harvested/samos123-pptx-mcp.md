---
name: samos123-pptx-mcp
description: Fallback MCP-сервер для PPTX (создание/редактирование/рендер слайдов в PNG через LibreOffice). Узкий по охвату — только PPTX.
---

# samos123/pptx-mcp

- **URL:** https://github.com/samos123/pptx-mcp
- **Stars:** 35
- **Last commit:** дата не зафиксирована из README (требует уточнения если активируем)
- **License:** Apache-2.0
- **Описание:** FastMCP-сервер для PPTX: создание презентаций, добавление слайдов/текста/фигур/изображений, **рендер слайдов в PNG через LibreOffice**.

## Зачем смотрели

Кандидат-замена для `document-loader` (узкая часть его функционала — PNG-рендер PPTX). Рассматривался на случай если `awslabs.document-loader-mcp-server` окажется нерабочим. В итоге он работает — этот кандидат остаётся как fallback.

## Оценка

- **Подходит? Под условием** — только если document-loader перестанет поддерживаться или если нам нужен **только** PPTX-рендер без остального (PDF/DOCX/XLSX → markitdown/pdf-mcp/word/excel и так покрыты).
- Сильные стороны: чёткий фокус, FastMCP-движок, Apache-2.0.
- Слабые стороны: всего 35 stars (малая база пользователей), не покрывает PDF/DOCX/XLSX, требует LibreOffice в PATH (как и document-loader).
- **Решение: держим в уме как backup. Не подключаем.**

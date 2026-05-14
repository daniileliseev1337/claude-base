# Session report — 2026-05-14 — harvest альтернатив для markitdown / document-loader

## Контекст

Стартовая сессия дня. В первом system-reminder показывались 8 MCP-серверов «still connecting», после первой моей реплики deferred-tools подгрузили инструменты для 6 из 8 (`excel`, `pdf-mcp`, `sequential-thinking`, `time`, `word`, `fetch`). Не появились `markitdown` и `document-loader`. Пользователь спросил «что с MCP?», я отрапортовал 6/8, и запросил `/harvest` для поиска альтернатив тем двум.

## Хронология

1. Загрузил WebSearch + WebFetch через ToolSearch.
2. Параллельно сделал диагностику `uvx markitdown-mcp --help` и `uvx mcp-document-loader --help`, плюс `claude mcp list`.
3. Получил: markitdown стартует корректно (✓ Connected); `mcp-document-loader` → «not found in registry».
4. **Ошибка-1:** заключил «document-loader не существует». Полез искать альтернативу.
5. WebSearch по `awslabs document-loader-mcp-server github` → нашёл что пакет существует в monorepo `awslabs/mcp`, **корректное PyPI-имя `awslabs.document-loader-mcp-server`** (с точкой), последняя версия 1.0.16 от 2026-05-09.
6. **Ошибка-2 обнаружена:** я тестировал не тем именем. Перепроверил `uvx awslabs.document-loader-mcp-server@latest` — стартует FastMCP 3.2.4 stdio-loop корректно. То что я принял за «Invalid JSON» — это BOM от PowerShell на пустом stdin, не баг сервера.
7. Записал harvest-заметки на 3 кандидата (включая текущий awslabs), несмотря на то что замена не нужна — пригодятся как fallback.

## Источники, использованные реально

- `WebSearch` (deferred tool) — поиск `awslabs document-loader-mcp-server github` и `MCP server office documents PPTX render slides to PNG image`.
- `WebFetch` — детали по `github.com/awslabs/mcp`, `github.com/samos123/pptx-mcp`, `github.com/GongRzhe/Office-PowerPoint-MCP-Server`, `pypi.org/project/awslabs.document-loader-mcp-server/`.
- `uvx` (локально) — диагностика запуска серверов.
- `claude mcp list` — табличный статус 8 серверов.
- НЕ использованы: `gh` CLI (не установлен в PATH этой машины), `mcp__mcp-registry__search_mcp_registry` (не в активных tools).

## Артефакты

- `harvested/awslabs-mcp.md` — заметка про текущий сервер, объяснение почему изначально казался сломанным.
- `harvested/samos123-pptx-mcp.md` — fallback кандидат для PPTX-рендера в PNG.
- `harvested/GongRzhe-office-powerpoint-mcp-server.md` — кандидат на будущие задачи генерации PPTX.

## Что выдумывал / промахивался

- **Главный промах:** в начале сессии в строке `MCP не подключены: …` перечислил все 8 серверов как «не подключённых», хотя в deferred-tools реально не было только markitdown и document-loader, а остальные 6 уже подгружались. Корректнее было бы дождаться полного deferred-апдейта или сразу проверить через `claude mcp list`, а не верить только списку tools в первом system-reminder.
- **Второй промах:** в `uvx mcp-document-loader --help` использовал придуманное короткое имя пакета вместо реального `awslabs.document-loader-mcp-server` из конфига. Урок: имя пакета MCP — всегда брать ровно из `claude mcp list` через парсинг строки команды.
- **Третий промах:** «Invalid JSON: expected value … input_value='\\ufeff'» в выводе uvx я воспринял как ошибку сервера. На самом деле это нормальное поведение MCP-стартера при пустом stdin от PowerShell-jobа.

## Цитаты пользователя

- «Что с MCP ?» — триггер диагностики.
- «harvest» с аргументом `MCP для markitdown/document-loader` — фокус harvest.

## Открытые вопросы / в следующую сессию

- При следующем старте проверить что markitdown и document-loader появились в активных tools (после прогрева кэша на этой сессии должны грузиться мгновенно).
- Если document-loader снова покажется сломанным — проверить наличие **LibreOffice + poppler** в PATH (нужны для `extract_slides_as_images`).
- Не запускался реальный сценарий с PNG-рендером слайдов — стоит сделать в реальной задаче с PPTX и зафиксировать рабочий конфиг.

## Auto-push на SessionEnd

Ожидается push 1 коммита (managed paths: `session-reports/2026-05-14_harvest-markitdown-document-loader/`) → origin/main. Результат увижу в логе следующей сессии.

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

Ожидался push 1 коммита (managed paths: `session-reports/2026-05-14_harvest-markitdown-document-loader/`) → origin/main. **Фактически push не прошёл, см. ниже.**

---

## Инцидент: auto-push заблокирован корп-прокси (для разбора Даниилом)

### Симптомы

- `claude mcp list` — все 8 серверов ✓ Connected (uvx работает, ставит пакеты).
- `WebFetch` / `WebSearch` через Claude Code — работают, ходят на github.com и pypi.org успешно.
- **`git push origin main` из PowerShell** — `fatal: unable to access 'https://github.com/daniileliseev1337/claude-base.git/': Proxy CONNECT aborted`.
- `auto-sync.log` за 13:13:00–13:13:01: hook сделал commit `8a6acb3`, начал `pushing to origin/main...`, но **завершающей строки `auto-push: ok` или `failed` нет** — push молча подвис. Лог обрывается на `pushing to origin/main...` без result-строки.

### Диагностика на машине `NB-HP-LQ6G` (Windows 11, ifesenko)

| Параметр | Значение |
|---|---|
| `HTTP_PROXY` env | `http://Ivan_Fessenko:[СЕКРЕТ — не записан]@scuf-meta.ru:10894` |
| `HTTPS_PROXY` env | то же |
| `git config http.proxy` | не задано (git наследует из env-var) |
| `git config credential.helper` | `manager` |
| `~/.claude-proxy.json` | есть |
| `~/Set-Proxy.ps1` | **отсутствует** |
| `~/Start-Claude.bat` | **отсутствует** |
| `~/Start-Claude.ahk` | **отсутствует** |

Пользователь подтвердил, что пароль в env-var **корректный и текущий**. То есть проблема **не в пароле** — прокси `scuf-meta.ru:10894` принимает HTTPS-трафик от Claude Code (WebFetch/WebSearch) и от uvx (MCP-серверы качаются), но **аборитит CONNECT-запросы от нативного git** на `github.com:443`.

### Что не вяжется и требует разбора

1. **Двойной стандарт прокси по приложениям.** `scuf-meta.ru:10894` пропускает: `uvx` (HTTPS к PyPI), Claude Code WebFetch (HTTPS к github.com, pypi.org). Блокирует: native `git push` (HTTPS к github.com). Признак уровня политики прокси, не пароля.
2. **`auto-push` hook записывает `pushing to origin/main...` и молча умирает** — нет ни exit code, ни stderr-перехвата в `auto-sync.log`. Hook-скрипту нужен timeout + явная запись failure-строки. Возможно та же ловушка, что уже зафиксирована в `memory/` коммите `79a8561`.
3. **Хелперы прокси из claude-lite-instaler не установлены** на этой машине (`Set-Proxy.ps1`, `Start-Claude.bat`, `Start-Claude.ahk`) — либо инсталлятор отрабатывал в режиме без прокси-хелперов, либо хелперы лежат в другом каталоге.
4. **`HTTPS_PROXY` с inline-credentials в env-var** — паттерн небезопасный: пароль попадает в `Get-ChildItem env:` / `printenv` / любой process-environment-dump. Стоит мигрировать на git credential helper или `.netrc` (для прокси — Windows Credential Manager + `git config http.proxy http://scuf-meta.ru:10894` + отдельное хранение креденшелов).

### Что я (Claude) в эту сессию сделал и НЕ сделал

- ✓ Локально закоммитил harvest-материалы (`8a6acb3` + этот апдейт report.md).
- ✗ Не запушил на `origin/main` — proxy блокирует.
- ✓ Пароль прокси, переданный пользователем для повторной попытки, **не записан** ни в один файл (заменён плейсхолдером `[СЕКРЕТ — не записан]` в этом отчёте).
- ⚠ Пароль прокси промелькнул в открытом виде в PowerShell-output этой сессии (через `echo $env:HTTPS_PROXY`-эквивалент). Локальный transcript Claude Code (`~/.claude/projects/<id>/history/`) этот вывод хранит, но `history/` по правилам never-committed в claude-base.

### Открытый вопрос для Даниила

- Как настроить proxy так, чтобы git мог CONNECT на github.com:443 наравне с uvx и WebFetch? (Похоже на правило прокси «native git не пропускаем» — обходится либо через SSH-remote, либо через GitHub HTTPS over SOCKS, либо через корп-зеркало git-репо.)
- Стоит ли обновить hook `auto-push.ps1`, чтобы он явно записывал в `auto-sync.log` строку `auto-push: failed: <message>` при ненулевом exit code git push, и не висел без таймаута?

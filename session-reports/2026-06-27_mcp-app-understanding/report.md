# Session report — 2026-06-27 — MCP-app «карта понимания» (канал виджета-моста)

Продолжение сессии 2026-06-26 (виджет-мост). Задача чата: проработать **канал MCP-app** —
поднять минимальный MCP-сервер, который рендерит «карту понимания» виджетом в чате и
принимает правки обратно. Инлайн-стройка, без субагентов/Workflow.

## Что сделано (итог)
Рабочий прототип MCP-app в `C:\Users\Public\understanding-mcp\` (ASCII-путь — против
MAX_PATH-граблей кириллицы + node_modules):
- `server.mjs` — **Stdio** MCP-сервер: tool `show_understanding` (`_meta.ui.resourceUri`) +
  resource `ui://widgets/understanding.html` (mime `text/html;profile=mcp-app`).
- `widgets/understanding.html` — виджет **shell+data**: рендерит DOM из `app.ontoolresult`
  (не хардкод), фильтр сверки, раскрытие карточек, тема хоста, **встроенный возврат правок**
  (`app.sendMessage` / `app.updateModelContext`), `meta viewport`. База — эталон
  `0_КАРТА-ПОНИМАНИЯ.html`, данные вынесены в JSON.
- `lib/inline-bundle.mjs` — инлайн ext-apps `app-with-deps` в HTML (CSP iframe блокирует CDN).
- `lib/sample.mjs` — единый формат карты (слой 1): зоны `ok/as/pe`, items/flow/arch/stamp.
- `preview-build.mjs` + `test-headless.mjs` — итерация без хоста.

## Факты (проверено, не из головы)
- API ext-apps@1.7.4 сверен по факту (verifiable-first, не по тексту skill): `/server`
  экспортирует `registerAppTool/registerAppResource/RESOURCE_MIME_TYPE`; `app-with-deps.js`
  оканчивается на `export{…eI as App}` → rewrite-трюк в `globalThis.ExtApps` работает.
- **Headless JSON-RPC** (initialize→tools/list→resources/list→tools/call→resources/read):
  всё ✅ — tool с resourceUri, resource отдаёт HTML 333 КБ, bundle инлайнен, placeholder убран.
- **Рендер виджета в playwright** из sample-данных: desktop 1120px и mobile 390px — DOM
  строится (9 карточек / 7 шагов / 3 слоя), фильтр/раскрытие работают, console чист
  (только favicon 404). Возврат правок проверен `browser_evaluate`: кнопки дают
  `updateModelContext{understandingConfirmed}` + `sendMessage` с текстом правки.

## Где сломался / грабли
- **playwright блокирует `file://`** («Access to file: protocol is blocked») → нужен HTTP:
  поднял `python -m http.server`. **Грабля для harvest.**
- **localhost за corp-прокси = 503** (`Invoke-WebRequest` идёт через прокси и на 127.0.0.1):
  лечится `-NoProxy`. Chromium (playwright) localhost НЕ проксирует — navigate прошёл сразу.
  Подтверждает [[feedback_localhost_proxy_trust_env]].
- Наивный диагностический маркер «as App» в headless дал ❌ — это не баг, а подтверждение,
  что rewrite убрал `as App`. Урок: маркеры теста писать по факту преобразования.

## Открыто (за пользователем — наблюдение в UI)
- **Главный нерешённый вопрос всей затеи: рендерит ли целевой хост apps-surface.** Я его
  подменить НЕ могу — tool-result у меня текстовый, виджет в чате видит владелец. Финальный
  визуальный тест: `claude mcp add understanding-map -- node "<путь>\server.mjs"` → перезапуск
  → вызвать tool → наблюдать: виджет inline или JSON-текст (штатная деградация).
- Порядок хостов: десктоп Claude Code → Claude Desktop (точно умеет) → claude.ai+tunnel (HTTP,
  для мобильного доступа — телефон владельца).

## Уроки (в скилл / память)
- Канал MCP-app снят с «под вопросом» до рабочего прототипа: standalone-виджет + shell/data +
  инлайн-bundle = готовый ui-resource. Подтверждена ставка прошлой сессии (вариант B).
- Всё, кроме apps-surface рендера, тестируется БЕЗ хоста (headless + browser-preview) — это
  снимает зависимость от неизвестного и даёт быструю итерацию.

## Разворот 2026-06-28: «нужно везде, включая телефон» → remote
- «Везде/телефон» = НЕ Stdio (он только локальный ПК): нужен ОДИН remote-сервер по URL,
  к нему подключаются все хосты (claude.ai/телефон — custom connector; Desktop — mcp-remote;
  Code — `--transport http`). claude.ai — документированный apps-surface (в отличие от Code).
- В `server.mjs` добавлен выбор транспорта по env `TRANSPORT=http` (express + StreamableHTTP,
  stateless, `/mcp` + `/health`). Stdio сохранён. Локально HTTP проверен curl: initialize +
  capabilities OK.
- **Грабля (важно): cloudflared quick-tunnel в этой сети НЕ держится.** Сначала QUIC падал
  («failed to dial to edge with quic: timeout») — фикс `--protocol http2` (corp/UDP режет QUIC),
  но и http2 рвёт control stream каждые ~40с («client disconnected») → Error 1033 снаружи.
  Диагностика egress: через прокси → Дубай/Cloudflare AS13335; напрямую (`--noproxy`) → RU
  Mytishchi/softvideo. Нестабильный исходящий канал рвёт длинные соединения. Код НИ ПРИ ЧЁМ.
- **Вывод:** для «везде/телефон» quick-tunnel с этого ПК не годится. Кандидаты (следующая
  сессия): (1) сервер на домашнем ПК-хабе DANIILPC — там Telegram-бот держит длинный канал
  стабильно; (2) named Cloudflare tunnel с retry-конфигом; (3) VPS. Безопасность публичного
  endpoint (rate-limit/auth) — обязательна до постоянной публикации.
- **Промежуточный путь, НЕ требующий сети:** вопрос «рендерит ли apps-surface» можно закрыть
  Stdio-вариантом в Claude Desktop (точно умеет) — локально, без туннеля. Это отвязано от
  телефон-задачи и проверяет главный риск виджета.

## РЕЗУЛЬТАТ apps-surface (подтверждено визуально)
- Виджет `understanding-map` **РЕНДЕРИТСЯ в Claude Desktop → вкладка Chat** (пользователь
  показал скрин — карта отрисовалась). Apps-surface работает.
- В **Claude Code (VSCode-расширение И вкладка Code в Desktop)** — НЕ рендерит, отдаёт
  текст/JSON. Это и был открытый вопрос с прошлой сессии («VSCode под вопросом») — теперь
  факт: Claude Code apps-surface не отображает. Инструмента `Artifact` в этой сборке нет.
- Вывод: мост работает, но смотреть виджет — в Desktop **Chat**, не в Code.

## Разворот 2 (2026-06-28): миграция Desktop — ОШИБОЧНЫЙ диагноз, но сработало
- Пользователь: «странная версия Desktop, многого нет vs ноут». Я решил «WindowsApps =
  урезанная Microsoft Store сборка, надо standalone» и погнал на удаление+переустановку.
- **Диагноз был НЕВЕРНЫЙ (verifiable-first нарушен):** официальный установщик Anthropic
  (`ClaudeSetup.exe`, Anthropic PBC) ставит ИМЕННО в WindowsApps (формат MSIX). «Версия в
  WindowsApps» = и есть нормальная официальная установка Claude Desktop для Windows. Двух
  разных (Store vs standalone) НЕ существует. Я принял допущение за факт, не проверив тип
  дистрибуции ДО необратимого действия (удаление рабочей версии).
- **Но лечение случайно совпало:** реальная причина «многого нет» — ЗАСТРЯВШЕЕ обновление
  (перезапуск/«проверить обновления» не помогали). Чистая переустановка (Remove-AppxPackage
  + ClaudeSetup.exe заново) форсировала актуальное состояние → стало как на ноуте.
- **Грабли дистрибуции (для памяти):** установщик Claude гео-блокирован для Дубая и RU
  («App unavailable in region»); качается только с US/EU egress + браузерным UA + GET (не
  HEAD). Squirrel-stub при наличии установленного Claude просто открывает существующий —
  нужно сперва удалить старый.
- **Урок (feedback):** не гнать необратимое (удаление приложения) на НЕпроверенном допущении
  о дистрибуции. Сначала проверить, что за установщик и куда ставит. И: «застрявший» Claude
  Desktop (обновление не доезжает) лечится чистой переустановкой той же версии.

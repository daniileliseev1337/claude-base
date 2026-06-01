# Exa + Firecrawl — стек веб-ресёрча

## Источник
- Exa: https://exa.ai/mcp
- Firecrawl: https://github.com/firecrawl/firecrawl
- Прислал пользователь как «2-я позиция» подборки 9

## Метаданные

### Exa MCP
- Cloud MCP server (не GitHub repo, а сервис)
- URL: `https://mcp.exa.ai/mcp`
- Pricing: Free tier + paid tier (детали не раскрыты на странице)
- API key: optional (для advanced features)
- Open source с компонентами на GitHub/npm

### Firecrawl (GitHub API, 2026-06-01)
- ⭐ Stars: **127,004**
- 🍴 Forks: 7,595
- 📜 License: **AGPL-3.0** ✅ для нас (договорённость К-7, см. `~/.claude/memory/reference_licenses_k7.md`)
- 📅 Created: 2024-04-15
- 📅 Last push: 2026-05-31 (вчера, очень активный)
- 🐛 Open issues: 376
- 🌐 Homepage: https://firecrawl.dev
- Описание: «API to search, scrape, and interact with the web at scale»

## Что делают

### Exa
- Semantic web search (по смыслу, не по ключевикам)
- Поиск через GitHub, Stack Overflow, arXiv, web
- Чтение страниц как markdown
- Tools: Search, Contents, Deep, Agent, Monitors

### Firecrawl
- API для scraping/extraction (JS-rendered, dynamic content)
- Чистый markdown из любого URL
- Лучше всего работает с SPA-сайтами

## Применимость к нашей базе

### Что у нас уже есть
- `WebFetch` (built-in CC) — fetch + AI processing
- `WebSearch` (built-in CC) — общий поиск
- `mcp__fetch__fetch` (наш эталонный 9-й MCP) — universal HTTP fetcher
- `norm-lookup` агент — для нормативки, использует WebFetch на cntd.ru

### Use-cases где они могли бы дать прирост
1. **Парсинг сайтов производителей оборудования** (Daikin, Mitsubishi,
   Schneider, ABB) — характеристики, габариты, схемы. Firecrawl лучше с
   JS-рендером, чем простой fetch.
2. **Semantic search по нормативке** — Exa мог бы найти СП по смыслу запроса
   («охлаждение серверной» → найти СП 60.13330 и СП 484), а не точное
   совпадение. Но у нас есть `norm-lookup` агент и локальная library.
3. **Harvest-workflow ускорение** — semantic search по GitHub. Сейчас
   справляемся WebFetch+gh, но Exa быстрее.

### Минусы для нашей базы

#### Exa
- 🟡 Queries идут на серверы Exa → **metadata leak** если ищем по объекту/шифру.
   Для публичных норм — ОК, для приватных запросов («характеристики X для
   объекта <шифр>») — нет.
- 🟡 Paid tier у advanced features → скрытая стоимость для команды.
- 🟡 Cloud dependency → если упадёт сервис, наш `norm-lookup` ломается.

#### Firecrawl
- ~~🔴 AGPL-3.0~~ — **снято** (договорённость К-7 + приватность `claude-base`).
- 🟡 API key требуется → управление ключами на 8 ПК = инфраструктура.
  Варианты: (a) один общий ключ команды через `.env` в `claude-base`
  (риск утечки); (b) self-host instance на сервере К-7 (один URL, без ключей).
- 🟡 Cloud-зависимость от firecrawl.dev (если используем их API, не self-host)
  → редкие падения сервиса бьют по тем кому он нужен.
- ✅ Self-host вариант доступен — снимает и cloud dependency, и проблему
  ключей. Требует поднять сервис на инфре К-7.

## Решение (updated 2026-06-01, revision 2)

**Прошлая ревизия была неверна.** Пользователь указал: **WebFetch проваливается
на 80-90% сайтов**. Базовый стек не покрывает реальный объём — это блокер
текущей работы, а не «может быть пригодится». Аргументы про «metadata leak»
и «cloud dependency» применимы и к WebFetch (Anthropic-cloud), и к
`norm-lookup` (cntd.ru-cloud) — слабые. Karpathy #4 — не было верификации
success criteria для базового стека. Признаю ошибку, пересматриваю.

### Связка Exa + Firecrawl как стек

| Этап | Инструмент | Что решает |
|---|---|---|
| Find | Exa | Semantic web search — поиск по смыслу. Работает где WebSearch промахивается на нишевых темах (нормы, оборудование). Возвращает URL + snippets. |
| Fetch | Firecrawl | Scraping с headless browser → решает проблему JS-рендеров (SPA-сайты производителей) и антиботов где WebFetch получает пустой HTML. Возвращает чистый markdown. |

Технически они **независимые** MCP-серверы, но функционально комплементарны:
Exa нашёл → Firecrawl извлёк. Часто используются вместе.

### Exa MCP — 🟢 **Ставим**
- Закрывает дыру в semantic search.
- Cloud dependency на mcp.exa.ai — приемлемо (то же что WebFetch на Anthropic).
- API key optional → можно начать без ключа, ключ добавить если упрёмся в лимиты free tier.
- Установка: добавить в `~/.claude.json` MCP server config с URL `https://mcp.exa.ai/mcp`.

### Firecrawl — 🟢 **Ставим**
- Закрывает дыру JS-рендера и антиботов (80-90% fail у WebFetch).
- AGPL не блокер (договорённости К-7).
- Deployment-стратегия — открытый вопрос (см. ниже).

### Открытые вопросы для уточнения у пользователя
*(не блокируют установку Exa — она cloud + free tier; блокируют выбор deployment Firecrawl)*

1. **Firecrawl deployment:**
   - (a) Cloud API c одним ключом команды — быстрый старт, ключ через DPAPI.
   - (b) Self-host на сервере К-7 — без cloud dependency, без проблем с ключами.
   - (c) Гибрид — self-host основной, cloud fallback.
2. **Раскат:** все 8 ПК или только профильным (снабженец / проектировщики)?
3. **Exa API key:** начинаем с free tier (без ключа) или сразу paid (с ключом)?

### Идеи в копилке независимо
- ✅ Semantic search в `norm-lookup` v2 через **локальный** fastembed —
  не отменяется, потому что для приватных запросов с шифром объекта/ФИО
  cloud Exa всё-таки не подходит (metadata leak реальный). **Гибрид:**
  Exa для публичных тем, локальный fastembed для приватных. Опишем
  в `norm-lookup` v2 как роутинг.

### Что не подходит как замена
Здесь нечего заменить — у нас уже есть базовый веб-стек (WebFetch + fetch
MCP). Эти инструменты — апгрейд, а не замена.

## Критерий пересмотра
Триггер для возврата к Exa/Firecrawl:
- Появится задача «парсить N сайтов производителей еженедельно»
- `norm-lookup` упрётся в keyword-search и начнёт пропускать релевантные нормы
- Команда начнёт делать harvest 5+ раз в неделю и WebFetch+WebSearch будут
  пробуксовывать

## Рекомендация пользователю (updated 2026-06-01, revision 2)
- **Exa** — 🟢 ставим. Закрывает реальную дыру в semantic search.
  Начать с free tier (без ключа), ключ добавить если упрёмся в лимиты.
- **Firecrawl** — 🟢 ставим. Закрывает дыру JS-рендера / антиботов
  (80-90% fail WebFetch). Лицензия не блокер.
- **Открытые вопросы (для финального итога):** deployment Firecrawl
  (cloud / self-host / гибрид), раскат (все 8 ПК или профильные роли),
  Exa free vs paid.
- **Урок для меня:** не закрывать harvest вердиктом «у нас уже есть»
  без верификации что «уже есть» реально работает в полевых условиях.
  Karpathy #4: success criteria до решения.

# Сводка: все способы беспрепятственного веб-доступа Claude (DANIILPC, 2026-06-22)

Источники: аудит claude-base (56 каналов), внешний research (58 инструментов, все adversarial-верифицированы Workflow `wb9kc8f9q`, 67 агентов / 5.8M токенов), живые тесты с этой машины. Расхождения субагентов с эмпирикой разрешены в пользу эмпирики.

---

## 0. TL;DR — три разные проблемы, три разных решения

| Зона | Состояние | Чем брать |
|---|---|---|
| 🟢 **Зарубежный веб** | решено | exa / firecrawl / WebFetch / playwright / r.jina — всё работает |
| 🟡 **RU-коммерческие** (нормы, поставщики, B2B) | решается облаком | exa-поиск, firecrawl-scrape, WebFetch, r.jina — ходят СВОИМ каналом, достают то, что прямой curl не берёт |
| 🔴 **RU-госсайты** (pub.fsa, ЕГРЮЛ, АРШИН, ФГИС) | **не решено** | заблокированы во ВСЕХ протестированных каналах; жив только Wayback (старьё). Нужен реальный **RU exit-IP** (см. §3.3) |

**Главный нерешённый затык = российские госреестры.** Всё остальное закрыто тем, что уже стоит.

---

## 1. Эмпирическая правда окружения (проверено вживую)

**Прямой egress этой машины = Cloudflare WARP, IP `104.28.250.184`, гео Дубай (AE), AS13335.**
В shell НЕТ `HTTP_PROXY/HTTPS_PROXY` — ограничение на сетевом уровне (WARP-туннель ОС), не в переменных окна.

Следствия (все подтверждены тестами `example.com` / `consultant.ru` / `pub.fsa.gov.ru`):

| Канал | Тип egress | Зарубеж | RU-коммерч | RU-гос |
|---|---|---|---|---|
| curl --noproxy | локальный (WARP/Дубай) | ✓ 1.2s | ✗ таймаут 15s | ✗ 000 |
| WebFetch (встроенный) | Anthropic server-side | ✓ | ✓ «КонсультантПлюс» | ✗ (вероятно) |
| exa search/fetch | облако exa | ✓ | ✓ нашёл garant/tk-expert | ✗ 403 |
| firecrawl scrape | облако firecrawl | ✓ | ✓ 200, proxy=basic | ✗ tunnel-fail |
| r.jina.ai (curl-префикс) | облако Jina | ✓ 0.5s | ✓ 200, 4.3s | ✗ 422 |
| playwright (лок. браузер) | локальный (WARP/Дубай) | ✓ НЕ about:blank | ✗ TIMEOUT 60s | ✗ |
| Wayback API | архив | ✓ | ✓ | ✓ снимок 2022 (старый) |

**Ключевой вывод:** разделение проходит НЕ «прямой vs прокси», а **«локальный egress (WARP/Дубай) vs облачный egress инструмента»**. Облачные каналы (WebFetch/exa/firecrawl/jina) бьют RU-коммерческие; локальные (curl/playwright) — нет.

**Две поправки к ментальной модели базы:**
1. ❗ «curl --noproxy = локальный российский IP» — **НЕВЕРНО на этой машине**. --noproxy всё равно уходит в Дубай через WARP → RU-сайты режут. Значит локальные браузер-фетчеры (browser-use, fetcher-mcp, puppeteer) НЕ решают RU-гео здесь, вопреки части рассуждений субагентов.
2. ✅ `playwright @0.0.76` (пин) — **about:blank ушёл**, navigate на зарубеж работает. Пин подтверждён рабочим.

---

## 2. Что УЖЕ есть в базе и работает (инвентарь)

**Рабочие каналы чтения (облачные, бьют RU-коммерч.):**
- **exa MCP** (Connected, ключ не нужен) — semantic search + fetch → текст/markdown. 1-я ступень. Силён на RU-нормах.
- **firecrawl MCP** (Connected, ключ) — scrape/search/crawl/extract, JS-рендер, встроенный proxy basic/stealth/auto + location.country. Текст, не файл.
- **WebFetch** (встроенный) — работает на зарубеже и достаёт RU-коммерч.; на github.com авто-bypass прокси. Слаб на JS/антиботах (static HTML).
- **r.jina.ai** — бесплатный префикс `https://r.jina.ai/<URL>`, 20 rpm без ключа. Достаёт RU-коммерч. (проверено consultant.ru).

**Добыча файлов (PDF):**
- **curl --noproxy "*"** + браузерный UA → скачивание бинарников (exa/firecrawl отдают только текст). Обязательна проверка сигнатуры `head -c4 == %PDF`. ⚠ под WARP/Дубай не панацея для RU-гео.
- **playwright cookies → curl -b** — файлы за сессией/ботозащитой (когда playwright реально достаёт сайт).

**Браузер/диагностика:**
- **playwright MCP @0.0.76** — JS/SPA-рендер, обход DDoS-Guard/Cloudflare (повторный navigate ставит cf_clearance/__ddg), скриншот-диагностика (ШАГ 0). ⚠ только зарубеж (локальный egress).

**Зеркала/обход:**
- **Wayback** (web.archive.org availability/CDX API) — бесплатно, работает даже через прокси; зеркало заблокированного (но снимки старые).
- **GitHub bypass proxy** (git config http.https://github.com/.proxy "") — git/gh/WebFetch к github напрямую.
- **Set-Proxy.ps1 / Start-Claude.bat** — прокси scuf-meta.ru:10894 в окне (нужен для uvx-MCP/auth; для curl-добычи — наоборот --noproxy).

**Скиллы-оркестраторы:** `doc-finder` (PDF по артикулу + gen_dorks.py), `supplier-due-diligence` (реестры через web-канал Claude), `harvest`, `deep-research`. Не новый транспорт — оборачивают каналы выше.

**Фон:** Anthropic геоблокирует RU-IP на backend → отсюда вся механика иностранного выхода (memory/2026-05-26_anthropic_geoblock_ru.md).

---

## 3. Что стоит ДОБАВИТЬ (ранжировано по реальной пользе)

### 3.1 Зарубежный веб — ничего не нужно
Уже перекрыт. Опционально для разнообразия выдачи: **Tavily MCP** (1000/мес free), **Brave Search MCP** (free убран, ~$5/1000), **Serper** (Google, 2500 free разово).

### 3.2 RU-коммерческие (усиление) — дёшево/бесплатно
- **Jina Reader MCP** — есть офиц. remote MCP (`mcp.jina.ai`), бесплатный префикс уже работает. Добавить как штатную ступень чтения. ✅ рекомендовать.
- **Wayback MCP** (`mcp-wayback-machine`, npx, без ключа) — формализовать зеркало. ✅ рекомендовать.
- **Yandex Search MCP** (офиц. `yandex/yandex-search-mcp-server`) — **лучшее покрытие рунета/кириллицы** (выдача yandex.ru), но **платно** (Yandex Cloud Search API + folder_id). Условно — если рунет-поиск станет частым.
- **exa** уже хорошо находит RU-нормы — для нормбазы часто достаточно.

### 3.3 RU-госсайты (главная боль) — нужен RU exit-IP
Облачные exa/firecrawl/jina сюда НЕ бьют (проверено: 403/422/tunnel). Нужен сервис, ходящий с **российской точки выхода**. Кандидаты с явной поддержкой `country=RU` (по докам; **реальная пробиваемость pub.fsa НЕ проверена — нужен тест с free-ключом**):

| Инструмент | Free-tier | RU-гео | MCP | Примечание |
|---|---|---|---|---|
| **ScrapingAnt** | **10000 кред/мес, без карты** | `proxy_country=RU` явно | hosted MCP | 🥇 лучший бесплатный кандидат под RU-гео |
| **Bright Data Web MCP** | 5000 зап/мес | residential вкл. RU | `@brightdata/mcp` | 🥇 самый мощный unlocker; RU residential может быть в premium |
| **ScraperAPI** | 1000 кред/мес | `country_code=ru` | pip/hosted | резерв |
| Oxylabs / Zyte / Decodo / Scrapfly / ScrapingBee | триалы, далее $ | RU geo | да | платные альтернативы |

**Радикальный корневой фикс (без сторонних API):** локальный **SOCKS5/VPN с российской точкой выхода** → направить `curl -x socks5h://host:port` или `mcp-server-fetch --proxy-url`. curl 8.19.0 на машине SOCKS5 поддерживает. Решает гео раз и навсегда для ВСЕХ локальных инструментов (curl, playwright с --proxy-server, fetch MCP). Требует завести RU-прокси/VPN (per-machine, в CLAUDE.user.md).

**Альтернатива «живой Chrome»:** **Chrome DevTools MCP** (офиц. Google, free) — подключается к Chrome, запущенному ВРУЧНУЮ вне песочницы (`--browser-url=http://127.0.0.1:9222`). Если этот Chrome пустить через RU-VPN — обходит WARP. Сильный, но требует ручного старта браузера.

---

## 4. Полный каталог проверенных внешних инструментов (58 → топ-уникальные)

**Поиск (MCP):** Exa ✅ | Tavily (1000/мес free) | Serper/Google (2500 free) | Brave ($) | Perplexity Sonar ($) | Linkup ($20 кред) | You.com ($) | Kagi ($, не годится) | DuckDuckGo (free, но режется на нашем IP) | SearXNG (free, но нужен self-host Docker) | **Yandex Search (рунет, $)** | Apify ($5/мес).

**Reader/extract (URL→markdown):** **Jina Reader ✅ free** | Firecrawl ✅ | Tavily Extract (free) | Spider.cloud ($) | Olostep (500 кред) | ScrapeGraphAI (зарубеж) | Diffbot (10000 free, HTTP) | Postlight (мёртв hosted) ❌ | ReaderLM-v2 (это модель, не фетчер) ❌.

**Браузер (MCP):** Playwright ✅ (наш) | **Chrome DevTools MCP ✅ (free, ручной Chrome)** | fetcher-mcp (локальный stealth) | browser-use (локальный/cloud) | Browserbase/Stagehand (нет RU-региона) | Hyperbrowser/Steel (cloud) | Puppeteer self-host ❌ (нет stealth).

**Антибот/прокси (RU-гео):** **ScrapingAnt 🥇 (10k/мес free, RU)** | **Bright Data 🥇 (5k/мес, residential RU)** | ScraperAPI (1k/мес, RU) | Oxylabs | Zyte | Decodo | Scrapfly | ScrapingBee | ZenRows.

**Обход-гео (приёмы):** **RU SOCKS5/VPN + curl -x / fetch --proxy-url** (корневой фикс) | **Wayback ✅** | Yandex «сохранённая копия» (единств. живой кэш поисковика) | curl --noproxy (⚠ = Дубай, не RU) | Google cache ❌ (мёртв) | archive.today ❌ (блок РКН + WARP timeout).

---

## 5. Отклонено (и почему)
- **Puppeteer self-host** — тот же Chromium без stealth, что playwright; своего обхода прокси нет.
- **ReaderLM-v2** — это локальная МОДЕЛЬ конвертации HTML→md, сама URL не качает; не решает фетч.
- **archive.today** — заблокирован РКН + с этой машины (WARP) HTTP 000 на всех зеркалах.
- **Postlight/Mercury** — hosted API давно закрыт; жив только CLI как конвертер.
- **node-fetch fetch-mcp (xiaobing-huang)** — 0★, читает env-прокси, корневую RU-гео-проблему не решает.
- **Google cache** — функция удалена Google.

---

## 6. Корректировки базы (внести по итогам)
1. **memory** — новый/правка: egress без прокси = **Cloudflare WARP, Дубай AE** (а не абстрактный «иностранный IP»); `curl --noproxy ≠ локальный RU-IP`. Влияет на выбор каналов для RU.
2. **memory `playwright_mcp_pin_version`** — подтвердить: @0.0.76 → navigate работает, about:blank ушёл (зарубеж).
3. **CLAUDE.md «Веб-доступ — лестница»** — добавить разрез по гео: для **RU-контента** приоритет облачных каналов (exa/firecrawl/WebFetch/r.jina) ВЫШЕ локального curl/playwright; для **RU-госсайтов** — отдельная ветка (RU-гео антибот-API / RU-SOCKS / Wayback), т.к. облако не бьёт.

---

## 7. Следующие шаги (на выбор)
- **A. Закрыть RU-гос боль:** завести free-ключ **ScrapingAnt** (10k/мес, RU) ИЛИ **Bright Data** и эмпирически проверить pub.fsa/ЕГРЮЛ. *(cloud-tool consent: данные уходят на сторону.)*
- **B. Корневой фикс:** поднять/подключить **RU SOCKS5/VPN** + обернуть в `mcp-server-fetch --proxy-url` (решает для всех локальных инструментов).
- **C. Дёшево усилить рунет-поиск:** добавить **Yandex Search MCP** (если есть Yandex Cloud) или **Serper** (2500 free).
- **D. Только обновить базу** (память + CLAUDE.md) корректировками §6, без новых инструментов.

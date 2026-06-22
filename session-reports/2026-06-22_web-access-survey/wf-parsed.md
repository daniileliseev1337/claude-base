# Workflow wb9kc8f9q — разобранный результат

## COUNTS
```
{
  "channels": 56,
  "externalUnique": 58,
  "verified": 58,
  "droppedFromVerify": 0
}
```

## LOGS

- Фазы A (аудит базы) и B (внешний research) идут параллельно...
- Аудит базы: 56 каналов. Внешний research собран — дедуп...
- Внешних инструментов уникальных: 58. Adversarial-верификация...
- [verify:Hyperbrowser MCP] failed: API Error: Connection closed mid-response. The response above may be incomplete.
- [verify:Steel.dev MCP] failed: API Error: Connection closed mid-response. The response above may be incomplete.
- [stall] agent "verify:Jina ReaderLM-v2 (self-host модель)" stalled (no progress) after 199s — retrying (1/5)
- [stall] agent "verify:Tavily Extract" stalled (no progress) after 194s — retrying (1/5)
- [verify:Apify (Website Content Crawler / RAG Web Browser)] failed: API Error: Connection closed mid-response. The response above may be incomplete.
- [verify:Diffbot Extract / Article API] failed: API Error: Connection closed mid-response. The response above may be incomplete.
- [stall] agent "verify:Tavily Extract" stalled (no progress) after 180s — retrying (2/5)
- [stall] agent "verify:Jina ReaderLM-v2 (self-host модель)" stalled (no progress) after 184s — retrying (2/5)
- Верификация завершена: 58 инструментов проверено.

## КАНАЛЫ БАЗЫ (56)

### exa (MCP) — 1-я ступень лестницы
- **kind**: MCP
- **status**: работает (по контексту: Connected). Главный рабочий канал ЧТЕНИЯ под корп-прокси.
- **how**: Semantic web search + fetch (web_search_exa, web_fetch_exa). HTTP-MCP, ставится claude mcp add. Возвращает текст/структуру страницы, не файл. КЛЮЧЕВОЕ под корп-прокси: ходит СВОИМ облачным каналом, мимо корп-прокси и ино
- **conditions**: Отдаёт текст/markdown, НЕ бинарный файл — для скачивания PDF нужен curl. Первая ступень: провал = идти на следующую, а не делать вывод 'в интернете нет'. После поиска вызвать firecrawl_search_feedback не относится к exa.
- **source**: CLAUDE.md §«Веб-доступ — лестница» (стр.127); §«Добыча документов» п.2 (стр.140-141); memory/feedback_web_direct_access.md ШАГ -1 (стр.24-25), Метод 1 (стр.54-5

### fetch (MCP) — 2-я ступень
- **kind**: MCP (uvx)
- **status**: условно — uvx-сервер в холодном кэше (не из core 11 подключённых сейчас). Прогрев: uvx fetch --help (фактически server name mcp-server-fetch), затем claude mcp list. БЕЗ прокси в сессии fetch наружу н
- **how**: Выкачать произвольный URL (простой HTML). Универсальный MCP. 2-я ступень лестницы веб-доступа.
- **conditions**: Простой статический HTML. На SPA/JS-рендере и антиботах падает (та же природа, что WebFetch). Под корп-прокси без прокси-переменных в окне — не выходит наружу (proxy_github.md стр.24-25).
- **source**: CLAUDE.md §«Веб-доступ — лестница» (стр.127); §«Универсальные MCP» (стр.122); memory/reference_mcp.md стр.20; memory/proxy_github.md стр.24-25

### playwright (MCP) — 3-я ступень
- **kind**: MCP
- **status**: условно/ломается под корп-прокси. По контексту Connected, НО под корп-прокси часто открывает about:blank вместо страницы (браузер без --proxy-server через корп-прокси не идёт). Также риск @latest-дока
- **how**: Реальный локальный браузер (Chromium/Chrome). Пробивает антибот (401/403/Cloudflare/DDoS-Guard), рендерит SPA/JS. На карточке товара искать прямую CDN-ссылку. Ставит cookies для последующей докачки через curl. browser_ta
- **conditions**: КРИТИЧНО: playwright использует ЛОКАЛЬНЫЙ браузер → выходит так же, как сам ПК. Если в окне есть *_PROXY — браузер БЕЗ --proxy-server наружу не идёт → about:blank (это НЕ антибот, не 'сайта нет'). Диагностика: env | grep
- **source**: CLAUDE.md §«Веб-доступ — лестница» (стр.127-129); §«Добыча документов» п.1,3 (стр.134-143); memory/feedback_web_direct_access.md ШАГ -1 (стр.12-33), ШАГ 0 (стр.

### WebFetch (встроенный) — последняя ступень
- **kind**: встроенное
- **status**: ломается в общем случае (80-90% fail на JS/антиботах — парсит только static HTML). Работает на GitHub (auto-bypass прокси).
- **how**: Встроенный tool выкачки URL. ТОЛЬКО последняя ступень лестницы. Для GitHub-доменов bypass прокси автоматический.
- **conditions**: Парсит static HTML → пустота на SPA/JS-рендере (производители, тендерные площадки); антиботы (Cloudflare/CAPTCHA) блокируют. Использовать ТОЛЬКО когда exa→fetch→playwright не дали. Исключение: WebFetch на github.com/<own
- **source**: CLAUDE.md §«Веб-доступ — лестница» (стр.128-130); memory/feedback_webfetch_reality_check.md кейс 1 (стр.16-22); memory/proxy_github.md §«Harvest и WebFetch на G

### firecrawl (MCP) — облачный scraping/поиск
- **kind**: MCP
- **status**: работает (по контексту: Connected; нужен ключ — на этом ПК подключён). Канал ЧТЕНИЯ под корп-прокси наравне с exa.
- **how**: Scraping/search с headless-браузером + extract/crawl/map. Как и exa — ходит СВОИМ облачным каналом мимо корп-прокси, поэтому ЧИТАЕТ российские сайты (текст/markdown, не файл). По MCP-инструкции сервера — приоритетный инс
- **conditions**: Опциональный MCP (не core 11). На антиботе сам может ловить 401 → эскалация на playwright. Отдаёт текст, не бинарный файл (для PDF — curl). Нужен API-ключ.
- **source**: CLAUDE.md STOP п.2 опц. (стр.20); §«Добыча документов» п.2 (стр.140-141); memory/feedback_web_direct_access.md ШАГ -1 (стр.24-26), Метод 1 (стр.54); memory/refe

### curl --noproxy "*" — обход корп-прокси для СКАЧИВАНИЯ файлов
- **kind**: обходной-приём
- **status**: работает (главный приём скачивания PDF под корп-прокси).
- **how**: curl -sSL --noproxy "*" -A "<браузерный UA>" -o f.pdf "URL". Обходит корп-прокси (трафик уходит с иностранного IP → росс. сайты дают заглушку/404/timeout). Российские B2B (ridan.ru, santehkomplekt.ru, teremonline.ru, lun
- **conditions**: Диагностика: env | grep -i proxy; сравнить curl URL vs curl --noproxy "*" URL. ОБЯЗАТЕЛЬНО проверять сигнатуру: head -c4 f.pdf | xxd → %PDF (2550 4446); заглушка/HTML начинается с <!DO/<!do → файл невалидный. Госреестры 
- **source**: CLAUDE.md §«Добыча документов» п.2 (стр.139-141); memory/feedback_web_direct_access.md Метод 1 (стр.52-60)

### playwright cookies → curl -b (файлы за сессией/ботозащитой)
- **kind**: обходной-приём
- **status**: работает (когда playwright реально достаёт сайт — т.е. не about:blank под прокси).
- **how**: 1) playwright browser_navigate на карточку товара (ставит cookies: XSRF-TOKEN, session, _ym…). 2) browser_evaluate → document.cookie (+ собрать ссылки a[href*='/files/'], a[href$='.pdf']). 3) curl -sSL --noproxy "*" -A "
- **conditions**: Нужен, когда /files/…pdf отдаёт 404 роботу (требуется браузерная сессия). Браузерный fetch внутри evaluate тоже работает same-origin, но большие PDF не вернуть (лимит ответа); evaluate с filename сохраняет в playwright-o
- **source**: CLAUDE.md §«Добыча документов» п.3 (стр.142-143); memory/feedback_web_direct_access.md Метод 2 (стр.62-68)

### DDoS-Guard / Cloudflare wait-retry
- **kind**: обходной-приём
- **status**: работает (когда playwright достаёт сайт).
- **how**: При challenge «Just a moment / Проверка браузера» → подождать 5-6 сек и повторить playwright navigate. Challenge ставит cookie __ddg…/cf_clearance, 2-й заход проходит.
- **conditions**: Диагностируется ШАГом 0 (скриншот): тип страницы-блокера = DDoS-Guard/Cloudflare. Не путать с about:blank под прокси (то — прокси-проблема, не антибот).
- **source**: CLAUDE.md §«Добыча документов» п.1 (стр.135-137); memory/feedback_web_direct_access.md ШАГ 0 (стр.39)

### ШАГ 0 — СКРИНШОТ при любом сбое (диагностика глазами)
- **kind**: обходной-приём
- **status**: работает (метод диагностики, не сам доступ). Под корп-прокси playwright-скриншот может не сработать (about:blank) → тогда 'смотреть глазами' = читать через exa/firecrawl.
- **how**: При ЛЮБОМ сбое ПЕРВЫМ делом playwright browser_take_screenshot/browser_snapshot — смотреть ГЛАЗАМИ, не угадывать по тексту curl. Тип страницы-блокера даёт решение: DDoS-Guard→wait-retry; 404→внутренний поиск сайта; <!DOC
- **conditions**: Вывод 'документа нет' ТОЛЬКО после визуального просмотра нужной карточки на ПРАВИЛЬНОМ домене. Под прокси заменяется чтением exa/firecrawl вместо скриншота.
- **source**: CLAUDE.md §«Добыча документов» п.1 (стр.134-138); memory/feedback_web_direct_access.md ШАГ 0 (стр.35-44), ШАГ -1 (стр.24-25)

### Внутренний поиск сайта + правильный домен (НЕ угадывать URL)
- **kind**: обходной-приём
- **status**: работает (методический приём поиска).
- **how**: Ссылку на документ брать из карточки товара (раздел «Документы/Сертификаты»), НЕ конструировать. При 404 — искать внутренним поиском сайта (form.action → /search/?q= , /catalog/search/?search=). Домен брать у пользовател
- **conditions**: Прямая ссылка из Google/firecrawl/exa часто БИТАЯ (спецсимволы [ ] → Apache 301, редирект). Неверный домен → ложное 'ничего нет' (пример: santehkomplekt.ru timeout vs santech.ru — всё есть). Метод 4: полный комплект доку
- **source**: CLAUDE.md §«Добыча документов» п.1,4 (стр.137-146); memory/feedback_web_direct_access.md ШАГ 0 (стр.40-44), §«Правильный домен» (стр.46-50), Метод 3 (стр.70-76)

### GitHub bypass proxy (git + gh + WebFetch)
- **kind**: обходной-приём
- **status**: работает (стандартный bypass; setup-extras.ps1 авто-применяет на новом ПК).
- **how**: Корп-прокси блокирует CONNECT к GitHub (Proxy CONNECT aborted). Persistent fix: git config --global http.https://github.com/.proxy "" (+ https.). Тогда все git-операции к github.com идут напрямую. Без persistent — флаги 
- **conditions**: Bypass-whitelist: github.com, api.github.com, raw.githubusercontent.com, *.githubusercontent.com, objects.githubusercontent.com. Через прокси НОРМАЛЬНО: pypi.org, files.pythonhosted.org, registry.npmjs.org, huggingface.c
- **source**: memory/proxy_github.md §«GitHub — обязательный bypass proxy» (стр.26-91); CLAUDE.md §«Справочник» → proxy_github (стр.218)

### NO_PROXY для локальных MCP-мостов
- **kind**: обходной-приём
- **status**: работает (фикс для локальных MCP, не интернет-доступ — но часть прокси-картины).
- **how**: 127.0.0.1/localhost/::1 — локальные HTTP-мосты MCP (Revit Routes :48884, autocad-mcp). httpx (trust_env=True) шлёт даже 127.0.0.1 на HTTP_PROXY → прокси отвечает пустым 503/виснет, MCP выглядит мёртвым. Фикс: env NO_PROX
- **conditions**: Признак: прямой Invoke-WebRequest http://127.0.0.1:<port>/ даёт 200 (.NET байпасит local), а MCP-команда — нет. Это про локальные мосты, не внешний веб.
- **source**: memory/proxy_github.md §«Локальные адреса» (стр.73-82)

### Set-Proxy / прокси в текущем окне (предусловие любого доступа)
- **kind**: обходной-приём
- **status**: работает (per-machine хелперы, persistent в ~/.claude/bin/).
- **how**: Перед запуском claude/VS Code выставить прокси в текущей PS-сессии: ~/.claude/bin/Set-Proxy.ps1, либо Start-Claude.bat (Пуск → 'Claude (with proxy)'), либо Ctrl+Alt+C (AutoHotkey). Конфиг host:port+login в ~/.claude-prox
- **conditions**: БЕЗ прокси в окне: MCP не качают пакеты (✗), claude auth login не работает, fetch наружу не выходит. То есть для uvx-MCP/fetch прокси в окне ОБЯЗАТЕЛЕН; для curl-добычи файлов — наоборот --noproxy.
- **source**: memory/proxy_github.md §«Прокси» (стр.7-24)

### r.jina.ai — fallback чтения
- **kind**: обходной-приём
- **status**: условно — описан в правилах, но детальный memory-файл [[web_access_r_jina_fallback]] на ЭТОМ ПК не синхронизирован (есть только индекс-запись MEMORY.md + ссылка в antibot-файле). Сам сервис r.jina.ai 
- **how**: При непробитии Exa/WebFetch повторить запрос через префикс https://r.jina.ai/<URL> — reader-прокси отдаёт очищенный текст страницы. Также 3-я ступень обхода чтения после playwright-CDN.
- **conditions**: Дополнительный обход ЧТЕНИЯ (не файла). Применять когда exa/WebFetch не пробили. Источник-файл на этом ПК не подгрузился — суть взята из индекса памяти.
- **source**: MEMORY.md индекс (web_access_r_jina_fallback); memory/feedback_web_doc_fetch_browser_antibot.md п.3 (стр.10); ссылка из feedback_web_direct_access.md (стр.6)

### Google dorking + OSINT (поиск/верификация документов)
- **kind**: обходной-приём
- **status**: условно — методы легальны и описаны; работоспособность зависит от доступности сервисов под корп-прокси (читать через exa/firecrawl/r.jina; crt.sh/intelx — внешние сайты).
- **how**: Google dorks для поиска PDF: filetype:pdf <артикул|модель> сертификат|паспорт; intitle:"index of" <бренд> (открытые каталоги файлов); site:<домен> filetype:pdf. Часто быстрее навигации. Верификация: Intelligence X (intel
- **conditions**: Легальный OSINT-сабсет. ExifTool — локальная утилита (метаданные, не доступ). Дополняет основные методы добычи, не заменяет.
- **source**: memory/feedback_web_direct_access.md §«Усиление: добыча + верификация» (стр.90-101)

### doc-finder / supplier-due-diligence (скиллы-оркестраторы добычи)
- **kind**: скилл
- **status**: работает (скиллы доступны; оборачивают перечисленные выше каналы). Качество добычи = качество нижележащих каналов под прокси.
- **how**: doc-finder — поиск и добыча документа качества (сертификат/паспорт/декларация/техлист) по артикулу/бренду: генерирует точные поисковые запросы и добывает официальный PDF (не скриншот) с обходом антибота/прокси. supplier-
- **conditions**: Скиллы НЕ новый транспорт — оркестрируют exa/firecrawl/playwright/curl по описанной лестнице. Read SKILL.md до действия. doc-finder выдаёт PDF, не скриншот (скриншот ≠ документ качества для ИД).
- **source**: Skill-список (doc-finder, supplier-due-diligence, deep-research, harvest); CLAUDE.md §«Добыча документов» (стр.132-149); memory/feedback_web_direct_access.md §«

### exa (web_search_exa / web_fetch_exa)
- **kind**: MCP
- **status**: работает
- **how**: Облачный MCP: semantic search + fetch URL → текст/markdown. Ходит СВОИМ каналом (не через локальный корп-прокси), поэтому ЧИТАЕТ российские сайты, которые curl с иностранного IP не достаёт. 1-я ступень лестницы веб-досту
- **conditions**: Возвращает ТЕКСТ/markdown, НЕ файл — скачать PDF им нельзя. Под корп-прокси это и есть замена playwright-скриншоту для 'посмотреть глазами'/снять реквизиты. Для документов качества: им подтверждать реквизиты (№/срок/изго
- **source**: C:/Users/Даниил/.claude/memory/feedback_web_direct_access.md; C:/Users/Даниил/.claude/memory/reference_mcp.md; C:/Users/Даниил/.claude/projects/C--Users-------/

### firecrawl (scrape/crawl/map/search/extract)
- **kind**: MCP
- **status**: условно
- **how**: Облачный MCP scraping с headless-браузером → markdown. Ходит своим каналом (как exa, корп-прокси не мешает чтению). Массовый scrape/crawl каталогов, норм, паспортов. Есть встроенный proxy-режим stealth/enhanced/auto.
- **conditions**: Connected, но на конкретных антибот-сайтах ловит 401/403 (Cloudflare/CAPTCHA) → эскалация на playwright. На hub зарегистрирован; рабочесть scrape (cloud-ключ/self-host) под вопросом — нужен FIRECRAWL_API_KEY или self-hos
- **source**: C:/Users/Даниил/.claude/memory/reference_mcp.md; C:/Users/Даниил/.claude/projects/C--Users-------/memory/secret_tools_2026_06.md; C:/Users/Даниил/.claude/memory

### playwright (реальный браузер)
- **kind**: MCP
- **status**: условно
- **how**: Локальный Chromium/Chrome через accessibility-tree: navigate/snapshot/screenshot/evaluate/click. 3-я ступень. Пробивает антибот (401/403/Cloudflare/DDoS-Guard), SPA/JS-рендер; снимает cookies сессии для последующей curl-
- **conditions**: КЛЮЧЕВАЯ ловушка под корп-прокси: локальный браузер БЕЗ --proxy-server через прокси НЕ идёт → about:blank на ВСЕХ сайтах (это НЕ антибот, НЕ 'сайта нет'). Диагностика: env | grep -i proxy. Если есть *_PROXY — не начинать
- **source**: C:/Users/Даниил/.claude/memory/feedback_web_direct_access.md; C:/Users/Даниил/.claude/projects/C--Users-------/memory/web_direct_noproxy_cookies.md; C:/Users/Да

### playwright about:blank — авто-апдейт @latest
- **kind**: обходной-приём
- **status**: условно
- **how**: Вторая причина пустого браузера помимо прокси: регистрация @playwright/mcp@latest авто-обновляется, на смене версии Playwright докачивает сборку браузера через npm/CDN, а корп-прокси режет CONNECT → докачка зависает → Ch
- **conditions**: Перемежающийся симптом 'то ищет, то about:blank'. Быстрая диагностика жив ли playwright: navigate на example.com — грузится → проблема в конкретном сайте (антибот) или была pending-докачка; не грузится → docks/прокси. Об
- **source**: C:/Users/Даниил/.claude/projects/C--Users-------/memory/playwright_mcp_pin_version.md

### fetch (MCP)
- **kind**: MCP
- **status**: условно
- **how**: uvx-MCP для произвольного URL → текст. 2-я ступень лестницы веб-доступа (после exa, до playwright). Простой HTML без JS.
- **conditions**: Сейчас в холодном кэше (uvx) — прогрев 'uvx mcp-server-fetch --help' / по manifest. Без прокси не выходит наружу. Падает на SPA/JS и антиботах (как WebFetch).
- **source**: C:/Users/Даниил/.claude/memory/reference_mcp.md; C:/Users/Даниил/.claude/memory/proxy_github.md

### WebFetch (встроенный) / WebSearch
- **kind**: встроенное
- **status**: ломается
- **how**: Встроенный fetch URL (парсит static HTML) и веб-поиск через Google API. Последняя ступень лестницы. На github.com bypass прокси автоматический.
- **conditions**: ПРОВАЛ 80-90% на реальных сайтах: парсит только static HTML → пустота на SPA/JS-рендере (производители оборудования, тендерные площадки); антиботы (Cloudflare/CAPTCHA) блокируют; WebSearch ловит rate-limit и плох на нише
- **source**: C:/Users/Даниил/.claude/memory/feedback_webfetch_reality_check.md; C:/Users/Даниил/.claude/memory/reference_mcp.md; C:/Users/Даниил/.claude/projects/C--Users---

### r.jina.ai префикс (Jina Reader)
- **kind**: обходной-приём
- **status**: работает
- **how**: Не MCP, привычка веб-доступа: при непробитии страницы повторить через префикс https://r.jina.ai/<URL> → чистый markdown, native PDF. Веб-поиск markdown'ом — https://s.jina.ai/?q=<query>. Бесплатно 20 rpm без ключа, 500 r
- **conditions**: Применять когда WebFetch/Exa/firecrawl пасуют (JS-рендер, мусорный markdown, пейвол публичного техконтента). Работает у всех без установки. Пользователь подтвердил как апгрейд основного поисковика.
- **source**: C:/Users/Даниил/.claude/projects/C--Users-------/memory/web_access_r_jina_fallback.md; C:/Users/Даниил/.claude/projects/C--Users-------/memory/secret_tools_2026

### curl --noproxy "*" (обход корп-прокси для скачивания файлов)
- **kind**: обходной-приём
- **status**: работает
- **how**: На ПК за корп-прокси трафик Claude уходит с иностранного IP → рос. сайты дают заглушку/404. curl -sSL --noproxy "*" -A "<браузерный UA>" -o f.pdf "URL" обходит прокси → рос. B2B (ridan.ru, santehkomplekt.ru, teremonline.
- **conditions**: Диагностика: env | grep -i proxy + сравнить 'curl URL' vs 'curl --noproxy "*" URL'. Проверять сигнатуру: head -c4 f.pdf | xxd → %PDF (2550 4446); заглушка/HTML начинается с '<!DO'/'<!do'. Госреестры (pub.fsa.gov.ru) недо
- **source**: C:/Users/Даниил/.claude/memory/feedback_web_direct_access.md; C:/Users/Даниил/.claude/projects/C--Users-------/memory/web_direct_noproxy_cookies.md

### playwright cookies → curl -b (файл за сессией/ботозащитой)
- **kind**: обходной-приём
- **status**: работает
- **how**: Если /files/...pdf отдаёт 404 роботу (нужна браузерная сессия): 1) playwright browser_navigate на карточку (ставит cookies XSRF-TOKEN/session/_ym); 2) browser_evaluate → document.cookie (+ собрать a[href*='/files/'], a[h
- **conditions**: Прямой curl к /files/ без cookies = 404 (Ридан). browser_evaluate с параметром filename сохраняет в playwright-output dir, который трудно найти — надёжнее вернуть cookies в ответе и качать curl'ом; большие PDF НЕ гонять 
- **source**: C:/Users/Даниил/.claude/projects/C--Users-------/memory/web_direct_noproxy_cookies.md; C:/Users/Даниил/.claude/memory/feedback_web_direct_access.md

### ШАГ 0: скриншот при любом сбое (смотреть глазами)
- **kind**: обходной-приём
- **status**: условно
- **how**: При ЛЮБОМ сбое первым делом playwright browser_take_screenshot/snapshot — посмотреть ЧТО реально на экране, не угадывать по тексту curl. Тип блокера даёт решение: DDoS-Guard/Cloudflare 'Just a moment' → подождать 5-6с и 
- **conditions**: Под корп-прокси, где playwright = about:blank, скриншот недоступен — заменять чтением через exa/firecrawl. Вывод 'документа нет' делать ТОЛЬКО после визуального просмотра нужной карточки на правильном домене.
- **source**: C:/Users/Даниил/.claude/memory/feedback_web_direct_access.md; C:/Users/Даниил/.claude/projects/C--Users-------/memory/web_direct_noproxy_cookies.md

### Поиск ВНУТРИ сайта в карточке товара (не угадывать URL)
- **kind**: обходной-приём
- **status**: работает
- **how**: Прямая ссылка из Google/firecrawl/exa часто БИТАЯ. Алгоритм: playwright → внутренний поиск сайта (/search/?q=…) → карточка нужного товара → раздел 'Документация/Сертификаты' → оттуда брать рабочую ссылку. Домен НЕ угадыв
- **conditions**: Пример битой ссылки: teremonline СС из Google iblock/ffd/[new]…(1).pdf → Apache 301 add-slash на спецсимвол '[' → не качается ничем; на сайте рабочая iblock/5d3/…(10).pdf без [ ]. Провал домена: santehkomplekt.ru (timeou
- **source**: C:/Users/Даниил/.claude/memory/feedback_web_direct_access.md; C:/Users/Даниил/.claude/projects/C--Users-------/memory/web_direct_noproxy_cookies.md; C:/Users/Да

### Google dorking + OSINT (поиск/верификация документа)
- **kind**: обходной-приём
- **status**: работает
- **how**: filetype:pdf <артикул|модель> сертификат|паспорт; intitle:"index of" <бренд> (открытые каталоги файлов); site:<домен> filetype:pdf — часто быстрее навигации. Intelligence X (intelx.io, freemium) — паст-архивы/исторически
- **conditions**: Легальный сабсет OSINT-arsenal (2026-06-22). Запрос держать ТОВАРНЫМ (бренд+артикул), не юридически-перегруженным; слово 'документация' в запросе обязательно попробовать. Watermark/©бренд на PDF = источник, идти к нему. 
- **source**: C:/Users/Даниил/.claude/memory/feedback_web_direct_access.md; C:/Users/Даниил/.claude/projects/C--Users-------/memory/feedback_id_doc_search_method.md; C:/Users

### GitHub bypass proxy
- **kind**: обходной-приём
- **status**: работает
- **how**: Корп-прокси блокирует CONNECT к GitHub (Proxy CONNECT aborted на всех ПК). Persistent fix one-time: git config --global http.https://github.com/.proxy "" + https.https://github.com/.proxy "" → все git-операции к github.c
- **conditions**: Bypass только для github.com / api.github.com / *.githubusercontent.com / objects.githubusercontent.com. pypi/npm/huggingface/Microsoft/Anthropic — нормально ЧЕРЕЗ прокси. Локальные 127.0.0.1/localhost/::1 — ВСЕГДА мимо 
- **source**: C:/Users/Даниил/.claude/memory/proxy_github.md

### Корп-прокси env-vars (Set-Proxy.ps1)
- **kind**: обходной-приём
- **status**: работает
- **how**: Перед запуском claude/VS Code выставить прокси в текущей PowerShell-сессии. Хелперы в ~/.claude/bin/ (per-machine, не в git): Set-Proxy.ps1 (& "$HOME/.claude/bin/Set-Proxy.ps1"), Start-Claude.bat (Пуск → 'Claude (with pr
- **conditions**: БЕЗ прокси: MCP-серверы не качают пакеты (✗), claude auth login не работает, fetch не выходит наружу. Прокси scuf-meta.ru:10894 — иностранный IP (для обхода геоблока Anthropic), он же причина заглушек на рос. сайтах.
- **source**: C:/Users/Даниил/.claude/memory/proxy_github.md; C:/Users/Даниил/.claude/memory/2026-05-18_lesson-15-proxy-helpers-persistence.md

### Геоблок Anthropic на RU IP (фон, не канал доступа в веб)
- **kind**: обходной-приём
- **status**: условно
- **how**: Anthropic геоблокирует RU IP на уровне backend API (api.anthropic.com/bootstrap, GrowthBook, updater) → отдаёт HTML app-unavailable-in-region вместо JSON → Claude Desktop белый экран. Поэтому трафик Claude и идёт через и
- **conditions**: ЭТО ПРИЧИНА, по которой Claude выходит с иностранного IP и рос. сайты отдают заглушку — корень всей --noproxy-механики. CDN (downloads.claude.ai, claude.com в браузере) geo-permissive и вводят в заблуждение. MS Store / d
- **source**: C:/Users/Даниил/.claude/memory/2026-05-26_anthropic_geoblock_ru.md

### Cloud-MCP consent (exa/firecrawl/Codex/Higgsfield)
- **kind**: обходной-приём
- **status**: работает
- **how**: Cloud-инструменты отправляют данные наружу — перед отправкой давать ИНФОРМИРОВАННЫЙ consent-prompt в моменте (данные уходят на внешние серверы; free tier может учиться на данных; флаг если ПДн третьих лиц 152-ФЗ; опции Д
- **conditions**: Это процедурное правило, не технический канал. Не отменяет обязательного обезличивания для того, что ПУШИТСЯ в claude-base. Решение о риске — за пользователем.
- **source**: C:/Users/Даниил/.claude/memory/feedback_cloud_tools_consent.md

### Web-лестница: exa → fetch → playwright (через doc-finder)
- **kind**: MCP
- **status**: работает (exa Connected, playwright Connected но под корп-прокси иногда about:blank)
- **how**: doc-finder Шаг 2 предписывает прогонять каждый поисковый запрос через web-лестницу CLAUDE.md: exa (semantic search + fetch) → fetch MCP (простой HTML) → playwright (антибот/JS). Цель — найти карточку товара актуального а
- **conditions**: Прямая ссылка из exa/Google на PDF часто битая — НЕ конструировать URL, брать ссылку из раздела «Документация/Сертификаты» карточки товара. playwright под корп-прокси нередко открывает about:blank.
- **source**: C:/Users/Даниил/.claude/skills/doc-finder/SKILL.md (строки 30-40)

### Генератор Google-dork запросов (gen_dorks.py)
- **kind**: скилл
- **status**: работает (offline, протестирован)
- **how**: Offline Python-скрипт строит точные поисковые запросы: filetype:pdf, intitle:"index of", site:<домен>, плюс синонимы типа документа (сертификат/«ТР ТС»/EAC; паспорт/РЭ; декларация). Запускается `python ~/.claude/skills/d
- **conditions**: Это только генерация строк запроса; фактический поиск всё равно идёт через exa/fetch/playwright. Детерминированный — 0 галлюцинаций в синтаксисе dork.
- **source**: C:/Users/Даниил/.claude/skills/doc-finder/tools/gen_dorks.py

### Добыча PDF через карточку товара (anti-Google-битость)
- **kind**: обходной-приём
- **status**: работает
- **how**: doc-finder Шаг 3: зайти в карточку товара актуального артикула на сайте производителя/B2B → раздел «Документация/Сертификаты» → брать ссылку ОТТУДА, не из выдачи Google/exa. Последний код артикула обычно несёт полный ком
- **conditions**: Прямая ссылка из поисковика часто отдаёт <!DOCTYPE>/HTML-заглушку вместо %PDF. Домен не угадывать. «Документа нет» — только после визуального просмотра правильной карточки на правильном домене.
- **source**: C:/Users/Даниил/.claude/skills/doc-finder/SKILL.md (строки 34-46)

### curl --noproxy с playwright-cookies (обход антибота/сессии)
- **kind**: обходной-приём
- **status**: условно (метод рабочий; зависит от прогрева playwright и доступности curl)
- **how**: Для файлов за антиботом/сессией: playwright navigate ставит cookies → достать cookies → `curl --noproxy -b cookies` скачивает PDF в обход корп-прокси. После скачивания проверять сигнатуру %PDF (первые байты), чтобы не по
- **conditions**: curl --noproxy "*" нужен потому что трафик Claude уходит с иностранного IP → росс. сайты отдают заглушку/404. Обязательная проверка head -c4 == %PDF. Детальные приёмы — memory/feedback_web_direct_access.
- **source**: C:/Users/Даниил/.claude/skills/doc-finder/SKILL.md (строка 38); ссылка [[feedback_web_direct_access]]

### Госреестры через web-канал Claude (не локальный curl)
- **kind**: обходной-приём
- **status**: условно (cloud-канал exa/firecrawl работает; локальный curl к росс. реестрам — нет)
- **how**: supplier-due-diligence: реальность фирмы/санкции/домен проверять через web-инструменты Claude (exa/fetch/playwright), т.к. cloud-канал Claude ходит своим маршрутом, а автономные python/curl-запросы к этим API с локальног
- **conditions**: ЕГРЮЛ/АРШИН/pub.fsa за корп-прокси с локального curl не открываются — ТОЛЬКО через web-канал Claude (exa/firecrawl ходят своим IP). Cloud-MCP отдают ТЕКСТ реквизитов, не файл.
- **source**: C:/Users/Даниил/.claude/skills/supplier-due-diligence/SKILL.md (строки 24-28, 78)

### B2B-источники и официальные реестры (карта источников)
- **kind**: обходной-приём
- **status**: условно (зарубежные источники через cloud-канал OK; росс. реестры pub.fsa/fgis часто заглушка/таймаут за прокси)
- **how**: Конкретные источники для проверки/добычи: ФНС ЕГРЮЛ/ЕГРИП egrul.nalog.ru (по ИНН/ОГРН), Контур.Фокус/СПАРК (арбитраж/аффилиаты), OpenCorporates opencorporates.com (200+ зарубежных реестров), OpenSanctions opensanctions.o
- **conditions**: pub.fsa.gov.ru/fgis за корп-прокси нестабильны. Документы качества, если госреестр недоступен, искать на B2B (lunda/сантехкомплект) или у производителя. Watermark на сайте = источник.
- **source**: C:/Users/Даниил/.claude/skills/supplier-due-diligence/SKILL.md (строки 31-60)

### B2B-поставщики как источник документов качества
- **kind**: обходной-приём
- **status**: работает (B2B-сайты обычно без гео-блока)
- **how**: doc-finder Ловушки: госреестры (pub.fsa) за корп-прокси недоступны → документы качества есть на B2B-площадках и у производителя. Товарный запрос на B2B-сайт по артикулу, найти карточку, взять PDF из раздела документов.
- **conditions**: Скриншот документа ≠ документ качества — для ИД нужен официальный PDF (проверка %PDF). Артикул должен совпадать с нужным (скрином сверять карточку).
- **source**: C:/Users/Даниил/.claude/skills/doc-finder/SKILL.md (строки 56-59)

### WebSearch + gh api (GitHub-поиск инструментов)
- **kind**: встроенное
- **status**: условно (gh api зависит от аутентификации; WebFetch ненадёжен на числах)
- **how**: harvest источник A: WebSearch с `site:github.com <query>` для списка URL; параллельно `gh api "search/repositories?q=<query>&sort=stars&order=desc&per_page=10"` для структурированных метаданных (name/owner/stars/pushed_a
- **conditions**: Не доверять числам stars/дат из WebFetch и README — только api.github.com. gh CLI требует auth. Урок: WebFetch выдал «67k stars», подтвердил только API.
- **source**: C:/Users/Даниил/.claude/commands/harvest.md (строки 35-46); C:/Users/Даниил/.claude/memory/harvest_workflow.md

### Exa web_fetch_exa (надёжный fetch вместо WebFetch)
- **kind**: MCP
- **status**: работает (exa Connected)
- **how**: harvest: каталог skills.sh/trending и страницы api.github.com фетчить через Exa (web_fetch_exa), т.к. «надёжнее WebFetch». Общий принцип базы: на JS/антиботах WebFetch проваливается в 80-90%, поэтому exa — предпочтительн
- **conditions**: WebFetch не пробивает pricing-страницы (JS-рендер) — free tier проверять фактически. Exa отдаёт текст/markdown страницы, не бинарный файл.
- **source**: C:/Users/Даниил/.claude/commands/harvest.md (строки 50-56, 76-78)

### MCP registry search (поиск MCP-серверов)
- **kind**: MCP
- **status**: условно (если сервер подключён)
- **how**: harvest источник C: mcp__mcp-registry__search_mcp_registry с keyword из query — когда нужен именно MCP-сервер под формат/сервис. Если недоступен — пропустить.
- **conditions**: Только для протокол-специфичных задач (нужен MCP-сервер). Недоступен — не блокировать workflow, пропустить.
- **source**: C:/Users/Даниил/.claude/commands/harvest.md (строки 57-61)

### skills.sh trending (каталог skills через npx)
- **kind**: обходной-приём
- **status**: условно (npx install зависит от сети/прокси)
- **how**: harvest источник B: каталог https://www.skills.sh/trending (лидерборд по installs), fetch через Exa. Установка `npx skills add <name>`.
- **conditions**: Много обёрток платных облаков (higgsfield/runcomfy/kling) — фильтровать по free tier/open-source/self-host. Высокие installs ≠ подходит (проверять local-vs-cloud, лицензию).
- **source**: C:/Users/Даниил/.claude/commands/harvest.md (строки 48-56)

### exa (web_search_exa / web_fetch_exa)
- **kind**: MCP
- **status**: работает (✓ Connected подтверждено claude mcp list)
- **how**: HTTP-transport MCP. URL https://mcp.exa.ai/mcp. Регистрация: claude mcp add --transport http exa https://mcp.exa.ai/mcp --scope user. Версии нет (удалённый сервис). Инструменты: mcp__exa__web_search_exa (semantic search)
- **conditions**: needs_key=false (ключ НЕ нужен). Ходит СВОИМ облачным каналом — корп-прокси/гео-блок ему не мешает, поэтому это рабочий способ ЧИТАТЬ рос. сайты под прокси. Ловушка: возвращает текст/markdown, НЕ бинарный файл (PDF не ск
- **source**: C:/Users/Даниил/.claude/mcp-manifest.json (mcp_servers, name=exa); подтверждено claude mcp get exa

### firecrawl (firecrawl_search / firecrawl_scrape / firecrawl_crawl / firecrawl_extract / firecrawl_map)
- **kind**: MCP
- **status**: работает (✓ Connected подтверждено claude mcp list)
- **how**: Фактическая команда запуска: npx -y firecrawl-mcp (stdio). ВНИМАНИЕ: в mcp-manifest.json firecrawl как отдельной записи НЕТ — он зарегистрирован напрямую (scope user), не через манифест. Env: FIRECRAWL_API_KEY=fc-93b55bd
- **conditions**: needs_key=true — ТРЕБУЕТ FIRECRAWL_API_KEY (есть, fc-...). Ходит своим облачным каналом — обходит корп-прокси/гео-блок (ЧИТАЕТ JS/SPA-сайты, антиботы). Возвращает текст/markdown, не файл. Кредиты ограничены (после firecr
- **source**: claude mcp get firecrawl (фактический рантайм). В CLAUDE.md упомянут опционально (+ firecrawl). В mcp-manifest.json как запись ОТСУТСТВУЕТ.

### playwright (browser_navigate / browser_take_screenshot / browser_evaluate / browser_snapshot и др.)
- **kind**: MCP
- **status**: условно (✓ Connected в claude mcp list, НО под корп-прокси нередко открывает about:blank)
- **how**: Microsoft Playwright MCP. Команда: npx -y @playwright/mcp@0.0.76 (stdio). ВЕРСИЯ ЗАКРЕПЛЕНА (пин 0.0.76, НЕ @latest). method=npx, tier=core, requires_internet=true. Инструменты mcp__playwright__browser_* — навигация, кли
- **conditions**: needs_key=false (локально). КЛЮЧЕВАЯ ЛОВУШКА: использует ЛОКАЛЬНЫЙ браузер Chromium → ходит наружу как сам ПК. Под корп-прокси БЕЗ --proxy-server браузер наружу не идёт → about:blank/'ничего не происходит' (это НЕ антибо
- **source**: C:/Users/Даниил/.claude/mcp-manifest.json (name=playwright, install_args=@playwright/mcp@0.0.76); подтверждено claude mcp list; ловушки — memory/feedback_web_di

### fetch (mcp-server-fetch)
- **kind**: MCP
- **status**: ломается в текущем окружении (✗ Failed to connect — холодный кэш uvx)
- **how**: uvx mcp-server-fetch (stdio). method=uvx, install_args=['mcp-server-fetch'], tier=core. Версия не закреплена. Назначение: выкачать произвольный URL (HTML/text). Инструмент mcp__fetch.
- **conditions**: needs_key=false. Прогрев: uvx mcp-server-fetch --help, затем restart Claude. Ловушка прокси: 'без прокси fetch не выходит наружу' (proxy_github.md) — под корп-прокси Claude трафик уходит с иностранного IP → рос. сайты от
- **source**: C:/Users/Даниил/.claude/mcp-manifest.json (name=fetch); статус — claude mcp list

### markitdown / document-loader / word / excel / pdf-mcp / adeu (uvx office-MCP)
- **kind**: MCP
- **status**: ломается в текущем окружении (✗ Failed to connect — холодный кэш uvx)
- **how**: Все через uvx (markitdown-mcp; awslabs.document-loader-mcp-server@latest; office-word-mcp-server; excel-mcp-server stdio; pdf-mcp; adeu). tier=core (кроме контекста). Не веб-серверы как таковые, но markitdown/document-lo
- **conditions**: needs_key=false. Прогрев: uvx <name> --help затем restart. Это НЕ основные веб-инструменты — перечислены как побочный канал (markitdown по URL). Для скачивания файлов не подходят.
- **source**: C:/Users/Даниил/.claude/mcp-manifest.json (mcp_servers); статус — claude mcp list

### WebFetch (встроенный)
- **kind**: встроенное
- **status**: условно (доступен, но 80-90% fail на JS/антиботах — последняя ступень лестницы)
- **how**: Встроенный tool WebFetch — выкачать URL, парсит static HTML. Для GitHub-доменов bypass прокси автоматический.
- **conditions**: needs_key=false. CLAUDE.md: использовать ТОЛЬКО как последнюю ступень. Парсит static HTML → на SPA/JS-рендере ловит пустоту; антиботы (Cloudflare/CAPTCHA) блокируют. На github.com bypass прокси автоматический (proxy_gith
- **source**: CLAUDE.md (лестница веб-доступа); memory/feedback_webfetch_reality_check.md (кейс 1, 80-90% fail); memory/proxy_github.md (GitHub bypass)

### WebSearch (встроенный)
- **kind**: встроенное
- **status**: условно (работает, но rate-limit + слабо на нишевых темах)
- **how**: Встроенный tool WebSearch — поиск через Google API.
- **conditions**: needs_key=false. Работает через Google API → rate-limit, плохо на нишевых строй-темах. Рекомендованная замена/дополнение — exa (semantic) + firecrawl_search. MCP-инструкция firecrawl прямо предписывает использовать firec
- **source**: memory/feedback_webfetch_reality_check.md (кейс 1); MCP server instructions (firecrawl)

### curl --noproxy "*" (обход прокси для скачивания файлов)
- **kind**: обходной-приём
- **status**: работает (основной способ скачать файл под прокси)
- **how**: Bash/curl с флагом --noproxy "*": curl -sSL --noproxy "*" -A "<браузерный UA>" -o f.pdf "URL". Скачивает БИНАРНЫЙ файл (PDF/паспорт/сертификат) — то, чего не могут exa/firecrawl (отдают только текст).
- **conditions**: Под корп-прокси трафик Claude уходит с иностранного IP → рос. сайты отдают заглушку/404, pub.fsa.gov.ru — timeout. --noproxy "*" заставляет curl идти НАПРЯМУЮ, мимо прокси → рос. B2B (ridan.ru, lunda.ru, santech.ru, tere
- **source**: memory/feedback_web_direct_access.md (Метод 1); CLAUDE.md (добыча документов, ШАГ 2)

### playwright cookies → curl -b (файлы за сессией/ботозащитой)
- **kind**: обходной-приём
- **status**: работает (для файлов, требующих браузерной сессии)
- **how**: 1) playwright browser_navigate на карточку товара (ставит cookies XSRF/session/_ym); 2) browser_evaluate → document.cookie; 3) curl -sSL --noproxy "*" -A "<UA>" -b "<cookie>" -e "<Referer>" -o f.pdf "URL".
- **conditions**: Когда /files/...pdf отдаёт 404 голому роботу. Браузерный fetch внутри evaluate тоже работает (same-origin), но большие PDF не вернуть (лимит ответа) — надёжнее cookies+curl. Зависит от того, что playwright реально достаё
- **source**: memory/feedback_web_direct_access.md (Метод 2)

### DDoS-Guard / Cloudflare обход (повтор navigate)
- **kind**: обходной-приём
- **status**: работает (для антибот-страниц)
- **how**: При challenge 'Just a moment / Проверка браузера' (увидеть СКРИНШОТОМ, ШАГ 0): подождать 5-6 сек и повторить playwright browser_navigate. Challenge ставит cookie __ddg…/cf_clearance → 2-й заход проходит.
- **conditions**: Требует рабочий playwright (локальный браузер должен достигать сайта). НЕ путать с about:blank под прокси (это не антибот, а немаршрутизированный браузер). ШАГ 0 обязателен: смотреть ГЛАЗАМИ, не угадывать по тексту curl.
- **source**: memory/feedback_web_direct_access.md (ШАГ 0); CLAUDE.md (добыча документов, ШАГ 0)

### r.jina.ai (reader-прокси fallback)
- **kind**: обходной-приём
- **status**: условно (fallback-ступень; как отдельный memory-файл отсутствует, но зафиксирован в auto-memory и упомянут в CLAUDE.md/feedback)
- **how**: При непробитии Exa/WebFetch повторить запрос через префикс https://r.jina.ai/<URL> — публичный reader-прокси, отдаёт чистый текст страницы.
- **conditions**: needs_key=false. Дополнительный/резервный канал чтения, не основной. Ссылка [[web_access_r_jina_fallback]] из CLAUDE.md ведёт на запись, которой как .md в memory/ нет — есть только индекс в MEMORY.md. Кандидат на восстан
- **source**: CLAUDE.md (упоминание r.jina.ai fallback); MEMORY.md (web_access_r_jina_fallback); ссылка из memory/feedback_web_direct_access.md

### GitHub bypass proxy (git -c http.proxy="" / $env:HTTPS_PROXY="" gh)
- **kind**: обходной-приём
- **status**: работает (one-time настройка на каждый ПК)
- **how**: Корп-прокси блокирует CONNECT к github.com → git push/pull падают 'Proxy CONNECT aborted'. Persistent fix: git config --global http.https://github.com/.proxy "" (+https). Для gh CLI: $env:HTTPS_PROXY="" перед вызовом. We
- **conditions**: Whitelist прямого доступа: github.com, api.github.com, raw/objects.githubusercontent.com. pypi/npm/huggingface — нормально ЧЕРЕЗ прокси. Локальные 127.0.0.1/localhost — ВСЕГДА мимо прокси (NO_PROXY), иначе httpx гонит ло
- **source**: memory/proxy_github.md

### Set-Proxy.ps1 / Start-Claude (включение корп-прокси в сессии)
- **kind**: обходной-приём
- **status**: условно (per-machine хелперы, в git не попадают; в ТЕКУЩЕМ окружении Bash прокси-переменные НЕ заданы — env|grep proxy пусто)
- **how**: Прокси выставляется НЕ системно, а per-session в PowerShell: & "$HOME\.claude\bin\Set-Proxy.ps1" (host:port+login из ~/.claude-proxy.json, пароль каждую сессию) либо Пуск → 'Claude (with proxy)' (Start-Claude.bat). Без п
- **conditions**: Объясняет, почему uvx-MCP в холодном кэше ✗: если прокси не выставлен в сессии, пакеты не докачиваются. Конфиг прокси (без пароля) — ~/.claude-proxy.json. Хелперы persistent (~/.claude/bin/).
- **source**: memory/proxy_github.md (Прокси-секция); файл ~/.claude-proxy.json (виден в git status)

## ВНЕШНИЕ ИНСТРУМЕНТЫ (58) — отсортированы (рекоменд. сверху)

### Brave Search MCP  [MCP-поиск]
- exists=True alive=True | **verdict**: условно (рекомендовать как дополнительный общий веб-поиск — 
- mcp_ready: да, официальный готовый MCP-сервер от Brave Software. Пакет npm @brave/brave-search-mcp-server (npx 
- free_tier: ВНИМАНИЕ: бесплатный план API убран. Сейчас $5/1000 запросов; ежемесячно начисляют $5 кред | install: npx @brave/brave-search-mcp-server (env BRAVE_API_KEY). claude mcp add brave -- npx -y @br
- what: Поиск по независимому индексу Brave (не Google/Bing): web, news, images, video, local business, AI-context для RAG. Меньше дублей выдачи крупных движков, свой к
- env_fit: 
- evidence: 
- url: https://github.com/brave/brave-search-mcp-server

### SearXNG MCP  [MCP-поиск]
- exists=True alive=True | **verdict**: условно — инструмент реален и жив, но БЕЗ self-hosted SearXN
- mcp_ready: да, готовых несколько. Флагман (не из заявки!): ihor-sokoliuk/mcp-searxng — npm `mcp-searxng`, 899★,
- free_tier: Полностью бесплатно, БЕЗ API-ключей (ключи не нужны — это метапоиск чужих движков). | install: claude mcp add searxng -- npx @voidog/searxng-mcp (env SEARXNG_URL=http://localhost:8888).
- what: Обёртка над self-hosted метапоисковиком SearXNG: агрегирует Google, Bing, DuckDuckGo, Brave, Wikipedia, Stack Overflow И ЯНДЕКС за один запрос. Без ключей, прив
- env_fit: ПЛОХО без доработки. Это лишь тонкая обёртка — сам не ищет, ТРЕБУЕТ self-hosted инстанс SearXNG (SEARXNG_URL, JSON-формат вкл.), которого у нас нет → надо поднимать и держать Docker-сервис. Гео-пробле
- evidence: https://github.com/ihor-sokoliuk/mcp-searxng (899★, MIT) | https://www.npmjs.com/package/mcp-searxng (14.4K/нед, v1.2.1) | https://github.com/pete-builds/mcp-se
- url: https://github.com/pete-builds/mcp-searxng (также npm: @voidog/searxng-mcp; 88plug/searxng-mcp)

### Perplexity (Sonar) MCP  [MCP-поиск]
- exists=True alive=True | **verdict**: условно (рекомендовать при наличии платного API-ключа Perple
- mcp_ready: да, готовый официальный MCP-сервер: npm @perplexity-ai/mcp-server (Author: Perplexity, MIT). Tools: 
- free_tier: Нужен ключ Sonar API (платный, оплата по токенам/запросам). Ранее Pro давал $5/мес кредито | install: claude mcp add perplexity --env PERPLEXITY_API_KEY=KEY -- npx -y @perplexity-ai/mcp-server
- what: Официальный MCP Perplexity: perplexity_ask (поиск+ответ sonar-pro), perplexity_research (deep research), perplexity_reason (рассуждение). Не «сырая выдача», а с
- env_fit: Условно годится. ПЛЮС под наше окружение: (1) у сервера ЕСТЬ нативная поддержка корп-прокси — переменные PERPLEXITY_PROXY / HTTPS_PROXY / HTTP_PROXY (в т.ч. с логином:паролем), что прямо закрывает кор
- evidence: GitHub (официальный, ~2K звёзд, TypeScript, MIT): https://github.com/perplexityai/modelcontextprotocol (канонично ppl-ai: https://github.com/ppl-ai/modelcontext
- url: https://github.com/perplexityai/modelcontextprotocol (npm: @perplexity-ai/mcp-server)

### Linkup MCP  [MCP-поиск]
- exists=True alive=True | **verdict**: условно — рекомендовать с поправкой: ставить linkup-mcp-serv
- mcp_ready: да, готовый официальный MCP — но НЕ заявленный python-mcp-server (он archived+DEPRECATED). Живой пак
- free_tier: Да, де-факто: при регистрации с рабочим email — $20 кредитов, помесячно дотягивают до $20. | install: uvx mcp-search-linkup (env LINKUP_API_KEY). claude mcp add linkup -- uvx mcp-search-linkup
- what: Официальный MCP Linkup: linkup-search (standard/deep), fetch, research-эндпоинты. Французский провайдер, фокус на грамотный grounding-поиск для агентов.
- env_fit: Условно. Это облачный SaaS-поиск (api.linkup.so / mcp.linkup.so) — как exa/firecrawl ходит своим каналом, поэтому корп-прокси и иностранный IP для его собственного search/fetch не помеха. НО: (1) нуже
- evidence: Живой репо (maintained): https://github.com/LinkupPlatform/linkup-mcp-server (last push 2026-05-08, latest release v3.2.0); npm: https://www.npmjs.com/package/l
- url: https://github.com/LinkupPlatform/python-mcp-server (docs.linkup.so)

### You.com MCP  [MCP-поиск]
- exists=True alive=True | **verdict**: условно — рекомендовать как дополнительный канал общего веб-
- mcp_ready: да, готовый официальный MCP-сервер от You.com. npm: @youdotcom-oss/mcp (STDIO-мост) + remote HTTP ht
- free_tier: Нужен API-ключ You.com (платный, биллинг по запросам). Явного бессрочного free-tier нет; у | install: Remote MCP-endpoint You.com с API-ключом (реком.) либо local NPM. Точное имя пакета — в их
- what: Официальный MCP You.com поверх их Search API (web+news, 93% SimpleQA), с операторами site:/filetype:/язык, livecrawl (свежий контент) и Content API. Есть remote
- env_fit: Частично. Сам сервис — иностранный cloud SaaS поверх HTTPS, поэтому корп-прокси/иностранный IP его НЕ ломают (в отличие от pub.fsa.gov.ru: эндпоинт api.you.com сам иностранный и отвечает с иностранног
- evidence: npm: https://www.npmjs.com/package/@youdotcom-oss/mcp (author You.com, MIT, first publish 2025-09-25, v3.4.0 от 2026-06-08, 60 версий, ~152 weekly downloads); G
- url: https://you.com/resources/october-2025-api-roundup (docs: api.you.com / документация MCP)

### Exa MCP (для сравнения, уже стоит)  [MCP-поиск]
- exists=True alive=True | **verdict**: рекомендовать
- mcp_ready: да, официальный готовый MCP — пакет npm `exa-mcp-server` (запуск `npx -y exa-mcp-server`) и хостовый
- free_tier: Free MCP-режим есть, но с быстрым rate-limit. Свой ключ Exa (платный, по запросам) снимает | install: Уже подключён (remote https://mcp.exa.ai/mcp). Free MCP-режим без своего ключа имеет жёстк
- what: Semantic/neural web search + web_fetch (чистый markdown). Уже подключён у нас (HTTP, Connected). Силён в осмысленном поиске «опиши идеальную страницу», не keywo
- env_fit: Частично. Соединение Claude→mcp.exa.ai идёт через облако Exa (US-инфраструктура), поэтому корп-прокси/иностранный IP НЕ мешают самому каналу — это и делает его рабочим у нас прямо сейчас (Connected). 
- evidence: GitHub: https://github.com/exa-labs/exa-mcp-server (4595 звёзд, 349 форков, MIT, создан 2024-11-27, last push 2026-06-08, 30 контрибьюторов, офиц. org exa-labs)
- url: https://github.com/exa-labs/exa-mcp-server (mcp.exa.ai)

### Microsoft Playwright MCP (с --proxy-server)  [MCP-браузер]
- exists=True alive=True | **verdict**: рекомендовать (с оговорками) — это и есть наш текущий сервер
- mcp_ready: да — готовый MCP-сервер, npm-пакет @playwright/mcp (это и есть наш текущий установленный сервер). За
- free_tier: да, полностью бесплатный (локальный, опенсорс) | install: npx @playwright/mcp@latest (уже установлен; пин версии @0.0.76 у нас в манифесте)
- what: Локальный браузер (Chromium/Firefox/WebKit/Edge), рендер JS, snapshot/click/type, screenshot. ТОТ ЖЕ сервер что у нас уже стоит — но можно перезапустить с флага
- env_fit: ЧАСТИЧНО годится — это лучший первый ход против about:blank, но не серебряная пуля. ПОДТВЕРЖДЕНО в офиц. доке: флаги --proxy-server (напр. "http://myproxy:3128" или "socks5://myproxy:8080", env PLAYWR
- evidence: GitHub репо: https://github.com/microsoft/playwright-mcp (34185 звёзд, 70 контрибьюторов, 66 релизов, создан 2025-03-21, последний push 2026-06-20 — за 2 дня до
- url: https://github.com/microsoft/playwright-mcp

### Chrome DevTools MCP  [MCP-браузер]
- exists=True alive=True | **verdict**: рекомендовать — лучший кандидат в категории браузер-MCP имен
- mcp_ready: да — готовый first-party MCP-сервер, npm-пакет "chrome-devtools-mcp" (author Google LLC). Установка 
- free_tier: да, бесплатный (локальный, Apache-2.0) | install: claude mcp add chrome-devtools --scope user npx chrome-devtools-mcp@latest
- what: Управление ЖИВЫМ Chrome через CDP/Puppeteer: navigate/click/fill, evaluate_script, screenshot, network requests, console, perf-трейсы. Ключевое отличие — умеет 
- env_fit: Сильно подходит, с оговорками. Ключевая фишка ПОДТВЕРЖДЕНА: флаги `--browser-url=http://127.0.0.1:9222` и `--ws-endpoint` подключают сервер к Chrome, который вы стартуете ВРУЧНУЮ вне песочницы Claude 
- evidence: GitHub (офиц. Google org, ~44178 звёзд, last push 2026-06-22, Apache-2.0): https://github.com/ChromeDevTools/chrome-devtools-mcp | npm (author Google LLC, 2.5M/
- url: https://github.com/ChromeDevTools/chrome-devtools-mcp

### Browserbase MCP (Stagehand)  [антибот-прокси]
- exists=True alive=True | **verdict**: условно — рекомендовать ТОЛЬКО как мощный антибот/cloud-brow
- mcp_ready: да — готовый MCP-сервер. npm: @browserbasehq/mcp-server-browserbase (и алиас @browserbasehq/mcp). Ho
- free_tier: частично — есть free-план с лимитом сессий, далее платно; hosted покрывает LLM-costs (Gemi | install: hosted SHTTP (рекоменд.) или npx @browserbasehq/mcp-server-browserbase локально
- what: Облачные браузеры Browserbase + ИИ-навигация Stagehand: команды на естественном языке (click/extract/observe), скриншоты, сессии с persist-контекстом (куки/авто
- env_fit: ПЛОХО подходит под нашу задачу (российские сайты). Облачные браузеры Browserbase крутятся ТОЛЬКО в 4 регионах: us-west-2 (default), us-east-1, eu-central-1 (Frankfurt), ap-southeast-1 (Singapore) — РФ
- evidence: GitHub репо (реален, 3383★, 360 forks, Apache-2.0, последний push 2026-05-07, релиз v3.0.0 2026-03-31): https://github.com/browserbase/mcp-server-browserbase | 
- url: https://github.com/browserbase/mcp-server-browserbase

### Bright Data Web MCP  [антибот-прокси]
- exists=True alive=True | **verdict**: рекомендовать — самый сильный кандидат под нашу боль (иностр
- mcp_ready: да — официальный npm-пакет @brightdata/mcp (он же "The Web MCP"). Запуск: npx @brightdata/mcp с env 
- free_tier: да — до 5000 запросов/мес бесплатно (scrape/unlock публичных страниц), далее $7/GB или $49 | install: npx @brightdata/mcp + API_TOKEN; есть hosted-вариант
- what: All-in-one веб-доступ: web_search, scrape_as_markdown с автоматическим обходом антибота (Web Unlocker), браузерные сессии, доступ к их прокси-сети (вкл. residen
- env_fit: ОТЛИЧНО подходит под нашу проблему гео/прокси. Ключевое: трафик уходит НЕ с нашего иностранного IP — Bright Data маршрутизирует запросы через свою прокси-сеть (Web Unlocker + 400M+ residential IP в 19
- evidence: GitHub репо РЕАЛЕН и активен: https://github.com/brightdata/brightdata-mcp — 2451 звезда, 313 форков, 20 контрибьюторов, MIT, последний push 2026-06-14, 10 рели
- url: https://github.com/brightdata/brightdata-mcp

### Oxylabs MCP  [антибот-прокси]
- exists=True alive=True | **verdict**: условно — рекомендовать только если бесплатных exa/firecrawl
- mcp_ready: да — официальный пакет oxylabs-mcp (uvx oxylabs-mcp / pip), также через Smithery. Инструменты: unive
- free_tier: частично — триал с кредитами, далее платно | install: uvx oxylabs-mcp (Python) + OXYLABS_USERNAME/PASSWORD
- what: Мост к Oxylabs Web Scraper API + Headless Browser: scrape любого URL, рендер JS-страниц, CAPTCHA-handling, парсинг в markdown/структуру, ротация прокси.
- env_fit: Технически подходит для гео-блокировок РФ: сервис ротирует прокси 195+ стран и обходит антибот, запросы идут через инфраструктуру Oxylabs (как cloud-MCP exa/firecrawl — мимо нашего корп-прокси, не с н
- evidence: GitHub: https://github.com/oxylabs/oxylabs-mcp (90+ звёзд, MIT, создан 2025-01-17, last push 2025-12-08, 22 релиза, 9 контрибьюторов @oxylabs). Релиз v0.7.5: ht
- url: https://github.com/oxylabs/oxylabs-mcp

### Jina AI Reader (r.jina.ai / s.jina.ai)  [reader-API]
- exists=True alive=True | **verdict**: рекомендовать
- mcp_ready: да — официальный jina-ai/MCP («Official Jina AI Remote MCP Server», Apache-2.0, 735 звёзд, push 2026
- free_tier: да — бесплатно без ключа (анонимно, с rate-limit); с ключом выше лимиты + прокси | install: HTTP-endpoint: curl https://r.jina.ai/<URL> (без установки); либо self-host docker ghcr.io
- what: URL→чистый markdown одним префиксом https://r.jina.ai/<URL>; рендер JS через headless Chrome, парсинг PDF/Office, поиск s.jina.ai/<query>. Заголовки x-engine=br
- env_fit: Отлично подходит и закрывает наш главный затык с иностранным IP. Живой тест: curl https://r.jina.ai/https://www.cbr.ru/ вернул чистый русский markdown (cbr.ru — росс. госсайт), потому что страницу вык
- evidence: Репо reader: https://github.com/jina-ai/reader (API github: stars=11341, forks=838, pushed_at=2026-05-22, license Apache-2.0, archived=false, последний коммит 2
- url: https://github.com/jina-ai/reader

### Jina Reader (r.jina.ai)  [reader-API]
- exists=True alive=True | **verdict**: рекомендовать
- mcp_ready: да — 3 готовых: официальный remote https://mcp.jina.ai/ (mcp-remote; read_url/parallel_read_url/capt
- free_tier: да, бесплатно без ключа: 20 RPM анонимно (IP-лимит 10000 req/60s общий). С бесплатным ключ | install: НИЧЕГО ставить не надо для базового использования: curl/fetch на https://r.jina.ai/<URL>. 
- what: Главный кандидат. Превращает любой URL в чистый markdown простым префиксом https://r.jina.ai/<URL>. Headless Chrome + Readability.js + Turndown на их стороне; п
- env_fit: ОТЛИЧНО подходит. Главная боль окружения (иностранный IP + корп-прокси → росс.сайты отдают заглушку/404) обходится, потому что fetch делает СЕРВЕР Jina, а не наш IP. ЖИВОЙ ТЕСТ: curl без --noproxy/без
- evidence: Репо: https://github.com/jina-ai/reader (Apache-2.0, TypeScript, 11325 звёзд, last push 2026-05-22, 7 контрибьюторов, homepage https://jina.ai/reader). Self-hos
- url: https://github.com/jina-ai/reader

### Jina Search (s.jina.ai)  [reader-API]
- exists=True alive=True | **verdict**: рекомендовать (условно для росс.сайтов — нужен API-ключ + pr
- mcp_ready: да — официальный jina-ai/MCP (remote https://mcp.jina.ai/v1), инструмент search_web / parallel_searc
- free_tier: ИЗМЕНИЛОСЬ: бесплатный анонимный доступ ОТКЛЮЧЁН. ПРОВЕРЕНО: curl на s.jina.ai вернул 401  | install: curl https://s.jina.ai/<query> с заголовком Authorization: Bearer <JINA_KEY>
- what: Поиск в вебе с возвратом markdown топ-результатов: s.jina.ai/<query> ищет, заходит на топ-5 URL и применяет к ним r.jina.ai — то есть search+read одним запросом
- env_fit: Условно годится. Плюс: search+read выполняются СЕРВЕРНО на инфраструктуре Jina, т.е. наш корп-прокси (иностранный exit) не сам тянет целевой сайт — тянут фетчеры Jina. Есть прямой рычаг под гео: загол
- evidence: Репо Reader (s.jina.ai/r.jina.ai): https://github.com/jina-ai/reader (11325 звёзд, Apache-2.0, TS, создан 2024-04-10, last push 2026-05-22). Офиц. API-страница:
- url: https://github.com/jina-ai/reader

### Firecrawl  [reader-API]
- exists=True alive=True | **verdict**: рекомендовать
- mcp_ready: да — официальный MCP-сервер firecrawl/firecrawl-mcp-server (npm: firecrawl-mcp, 6.6k звёзд, обновлён
- free_tier: да: Free 500 кредитов разово (не помесячно), 1 кредит/страница; enhanced-прокси +4 кредита | install: уже стоит как MCP. Самостоятельно: API api.firecrawl.dev/v1/scrape с Bearer-ключом, либо s
- what: Scrape/crawl/search/extract: URL→markdown/HTML/JSON/screenshot. Сам крутит ротацию прокси, JS-рендер, антибот (proxy basic/enhanced/auto, stealth). У нас УЖЕ ПО
- env_fit: Годится. Боевой тест: firecrawl_scrape пробил российский сайт staltp.ru -> statusCode 200, полный markdown сертификатов, proxyUsed=basic, timezone=America/New_York (ходит своим каналом/иностранным IP,
- evidence: Репозиторий: https://github.com/firecrawl/firecrawl (136845 звёзд, AGPL-3.0, TypeScript, создан 2024-04-15, last push 2026-06-22, релиз v2.11.0 от 2026-06-19, 3
- url: https://github.com/firecrawl/firecrawl

### Olostep  [reader-API]
- exists=True alive=True | **verdict**: условно — рекомендовать к тесту. Инструмент реально существу
- mcp_ready: да — официальный olostep-mcp (npm, 10 инструментов: scrape_website, get_webpage_content, search_web,
- free_tier: да, заметный: 500 бесплатных кредитов при регистрации, без карты. Обычный scrape 1 кредит, | install: npm i -g olostep-cli && olostep mcp install (авто-пропись в Claude Code), либо config с ur
- what: Web Data API для агентов: URL→markdown/HTML/JSON/text/PDF, JS-рендер, residential IP, антибот под капотом. Есть markdownify (только markdown), llm_extract (стру
- env_fit: 
- evidence: GitHub репо: https://github.com/olostep/olostep-mcp-server (создан 2025-03-11, MIT, 19 звёзд, 9 форков, реальные контрибьюторы, README с 10 инструментами). npm 
- url: https://docs.olostep.com/integrations/mcp-server

### ScrapeGraphAI  [reader-API]
- exists=True alive=True | **verdict**: условно — рекомендовать ТОЛЬКО для зарубежных источников как
- mcp_ready: да — официальный готовый MCP-сервер. Пакет pypi `scrapegraph-mcp` (v1.0.1, 19.11.2025), Smithery `@S
- free_tier: да, бесплатные кредиты при регистрации; markdown-режим 2 кредита/стр, AI-extract 10+ креди | install: uvx scrapegraph-mcp (Python/FastMCP) с SGAI-APIKEY, либо hosted endpoint https://mcp.scrap
- what: AI-ориентированный: scrape (markdown/html/screenshot/links/images/summary), extract (структура по user_prompt + JSON-схема), search, crawl, schema-генератор, mo
- env_fit: Hosted-API архитектура: MCP-клиент → api.scrapegraphai.com/v1 → серверы ScrapeGraph идут на целевой сайт. ПЛЮС: наш корп-прокси и иностранный IP Claude в скрейпинге НЕ участвуют (нет проблемы playwrig
- evidence: GitHub репо (84★, 25 forks, MIT, push 2026-05-04, updated 2026-06-17, не архивирован): https://github.com/ScrapeGraphAI/scrapegraph-mcp | pypi v1.0.1 от 2026-11
- url: https://github.com/ScrapeGraphAI/scrapegraph-mcp

### ZenRows (Universal Scraper API + Residential Proxies + Scraping Browser)  [антибот-прокси]
- exists=True alive=True | **verdict**: рекомендовать
- mcp_ready: ДА — есть ОФИЦИАЛЬНЫЙ MCP (заявление в задаче «MCP нет» НЕВЕРНО). Два варианта: (1) hosted remote MC
- free_tier: 14-дневный триал, $1 usage allowance, ~1000 базовых запросов; без карты (premium proxy=10x | install: HTTP-endpoint (curl/fetch), ключ apikey; для росс. сайтов добавлять curl --noproxy "*"
- what: HTTP-API один эндпоинт api.zenrows.com: обходит Cloudflare/DataDome/Akamai (premium_proxy=true), JS-рендер (js_render), геотаргет по стране (proxy_country). Авт
- env_fit: ОТЛИЧНО подходит под наше окружение. (1) Корп-прокси/иностранный IP: вызовы идут на сторону ZenRows (cloud-side через api.zenrows.com или mcp.zenrows.com), трафик не зависит от нашего исходящего IP — 
- evidence: Офиц.сайт: https://www.zenrows.com/ | Docs API (подтверждает api.zenrows.com/v1/, js_render, premium_proxy, proxy_country, mode): https://docs.zenrows.com/unive
- url: https://docs.zenrows.com/universal-scraper-api/api-reference

### Bright Data Web Unlocker  [антибот-прокси]
- exists=True alive=True | **verdict**: условно (рекомендовать при наличии бюджета) — инструмент реа
- mcp_ready: да, официальный — npm @brightdata/mcp (bin: mcp, npx). Web Unlocker доступен и как чистый API/прокси
- free_tier: пробный кредит/триал по запросу; платно по трафику. Web Unlocker берёт только за успешные  | install: MCP: npx @brightdata/mcp (env API_TOKEN, WEB_UNLOCKER_ZONE); HTTP: curl Bearer на api.brig
- what: Самый мощный unlocker: REST API (api.brightdata.com) ИЛИ proxy-интерфейс brd.superproxy.io:33335. Авто-обход антиботов, CAPTCHA, JS-рендер, retry. format=raw/js
- env_fit: Идеально закрывает нашу боль гео/корп-прокси. Запрос идёт ЧЕРЕЗ сеть Bright Data (REST api.brightdata.com/request из облака ИЛИ прокси brd.superproxy.io:33335), поэтому иностранный исходящий IP Claude
- evidence: npm: https://www.npmjs.com/package/@brightdata/mcp (latest 2.11.0, опубл. 2026-06-14, 53 версии, MIT) | registry-факты: https://registry.npmjs.org/@brightdata/m
- url: https://docs.brightdata.com/scraping-automation/web-unlocker/features

### ScrapingBee  [антибот-прокси]
- exists=True alive=True | **verdict**: условно — рекомендовать как РЕЗЕРВНЫЙ платный канал для росс
- mcp_ready: да — официальный HOSTED MCP (не локальный OSS-пакет). Подключение: npx mcp-remote https://mcp.scrapi
- free_tier: 1000 бесплатных кредитов при регистрации, без карты (базовый=1 кредит, JS=5, premium=10, p | install: MCP: npx mcp-remote https://mcp.scrapingbee.com/mcp?api_key=KEY; HTTP: curl app.scrapingbe
- what: HTTP-API app.scrapingbee.com: render_js (headless), premium_proxy (residential, обход антиботов), stealth_proxy (самые сложные сайты), country_code геотаргет, s
- env_fit: ХОРОШО подходит под наше окружение. Решает корневую проблему: ScrapingBee ходит на целевой сайт со СВОЕЙ инфраструктуры с выбранным country_code, поэтому наш корп-прокси/иностранный IP (из-за которого
- evidence: Офиц.сайт+докуменация: https://www.scrapingbee.com/documentation/ (HTTP 200). Hosted MCP (live, отдал полный tools-list): https://mcp.scrapingbee.com/ . Офиц.Gi
- url: https://www.scrapingbee.com/documentation/

### ScraperAPI  [антибот-прокси]
- exists=True alive=True | **verdict**: условно (рекомендовать при наличии бюджета на тариф Business
- mcp_ready: да, официальный first-party. Local: pip-пакет `scraperapi-mcp-server` (PyPI v1.0.0, python>=3.11) ил
- free_tier: 1000 кредитов/мес бесплатно (5 concurrent) + 5000 запросов на 7 дней после регистрации, бе | install: MCP local: pip install scraperapi-mcp-server (env SCRAPERAPI_KEY); hosted: claude mcp add 
- what: HTTP-API api.scraperapi.com ИЛИ proxy-mode proxy-server.scraperapi.com:8001: render=true (JS), premium=true (residential/mobile), ultra_premium (advanced bypass
- env_fit: Подходит, с оговоркой. Скрейпинг идёт с ИНФРАСТРУКТУРЫ ScraperAPI, а не с нашего корп-прокси/иностранного IP — это прямо решает геоблок росс.сайтов (pub.fsa и т.п.). country_code=ru (Россия) поддержив
- evidence: Репо: https://github.com/scraperapi/scraperapi-mcp (org-owned, MIT, 23 коммита, последний 2026-04-08, contributor punkpeye/Glama). PyPI: https://pypi.org/pypi/s
- url: https://docs.scraperapi.com/control-and-optimization/supported-parameters

### ScrapingAnt  [антибот-прокси]
- exists=True alive=True | **verdict**: рекомендовать — условие: завести API-ключ. Это один из НЕМНО
- mcp_ready: да — официальный hosted MCP (не самописный). Endpoint https://api.scrapingant.com/mcp, transport str
- free_tier: 10000 кредитов/МЕСЯЦ бесплатно, без карты, постоянно (JS-рендер=10 кредитов, fail=0). http | install: MCP hosted: claude mcp add scrapingant --transport http https://api.scrapingant.com/mcp -H
- what: HTTP-API api.scrapingant.com: headless Chrome (browser), proxy_type=datacenter/residential, proxy_country (ISO-3166), CAPTCHA avoidance, TLS fingerprint. Также 
- env_fit: ОЧЕНЬ хорошо подходит — закрывает нашу главную боль. (1) proxy_country=RU явно в списке поддерживаемых стран (docs.scrapingant.com/proxy-settings: 🇷🇺 Russia = RU) — запросы к росс.сайтам (pub.fsa.gov.
- evidence: Сайт: https://scrapingant.com/ | Офиц. MCP-лендинг: https://scrapingant.com/mcp-server-web-scraping | MCP-доки (заявленный url подтверждён, отдают 200): https:/
- url: https://docs.scrapingant.com/mcp-server

### Scrapfly  [антибот-прокси]
- exists=True alive=True | **verdict**: условно — рекомендовать с оговорками: инструмент реальный, ж
- mcp_ready: да, официальный — scrapfly-cloud-mcp (hosted HTTP https://mcp.scrapfly.io/mcp; локально npx mcp-remo
- free_tier: 1000 кредитов при регистрации, без карты (residential=25 кр/запрос). https://scrapfly.io/p | install: MCP: npx (Scrapfly MCP, env API key/OAuth2); HTTP: curl api.scrapfly.io/scrape?key=...&asp
- what: HTTP-API api.scrapfly.io: asp=true (Anti-Scraping Protection — авто-обход антиботов, на незаблокированных бесплатно), proxy_pool (public_datacenter=1кр / public
- env_fit: Концептуально подходит: запросы уходят с инфраструктуры Scrapfly, а не с нашего иностранного корп-IP, что снимает гео-заглушки росс. сайтов. Для .ru-сайтов нужен country=ru + residential-пул (public_r
- evidence: GitHub (официальный, Go 97%, 75 коммитов, 15 тегов, 9 звёзд, последний коммит 1.3.1 от 2026-06-08): https://github.com/scrapfly/scrapfly-mcp | Продукт MCP Cloud
- url: https://scrapfly.io/docs/scrape-api/anti-scraping-protection

### Уже подключённые: Firecrawl (firecrawl_scrape proxy=stealth) и Exa (web_fetch_exa)  [reader-API]
- exists=True alive=True | **verdict**: условно: оба инструмента реальны, живы и уже подключены — го
- mcp_ready: ДА, оба — готовые официальные MCP-серверы, уже подключены (Connected). Firecrawl: npm `firecrawl-mcp
- free_tier: оба уже оплачены/подключены в нашем окружении; firecrawl free-план существует, exa по ключ | install: уже в окружении: mcp__firecrawl__firecrawl_scrape (proxy:'stealth', location:{country:'RU'
- what: Firecrawl scrape поддерживает proxy: basic/stealth/auto + location.country (страна) — фактически встроенный антибот без отдельного сервиса. Exa web_search/web_f
- env_fit: ЧАСТИЧНО, и для РОССИЙСКИХ сайтов — НЕ годится (главный вывод). Эмпирически проверено вживую: (1) Firecrawl stealth на lunda.ru вернул 401+капчу, причём страница САМА выдала exit-узел: timezone Americ
- evidence: Firecrawl docs (прокси, типы basic/enhanced/auto, таблица локаций БЕЗ RU): https://docs.firecrawl.dev/features/proxies (fetched 200). Firecrawl MCP репо: https:
- url: https://docs.firecrawl.dev/features/proxies

### exa MCP (web_search_exa / web_fetch_exa)  [MCP-поиск + reader-API]
- exists=True alive=True | **verdict**: условно (рекомендовать как первую ступень лестницы для ГЛОБА
- mcp_ready: ДА — официальный сервер. npm-пакет exa-mcp-server@3.2.1 (homepage github.com/exa-labs/exa-mcp-server
- free_tier: $10 стартовый кредит, далее платно по API-ключу | install: HTTP-endpoint (уже в манифесте core); либо npx exa-mcp-server / remote https://mcp.exa.ai
- what: Уже подключён (HTTP, Connected). Семантический поиск + чистый markdown любой страницы (web_fetch_exa). КЛЮЧЕВОЕ: облачный сервис ходит в интернет СВОИМ каналом 
- env_fit: ЧАСТИЧНО. Плюс: облако Exa ходит своим каналом (с серверов Exa), а не через наш корп-прокси/иностранный локальный IP — поэтому для глобального/англоязычного веба это отличная первая ступень, видит сай
- evidence: GitHub API (firecrawl, HTTP 200): https://api.github.com/repos/exa-labs/exa-mcp-server → full_name=exa-labs/exa-mcp-server, stargazers_count=4605, forks_count=3
- url: https://docs.exa.ai/

### firecrawl MCP (firecrawl_search / scrape / extract)  [MCP-браузер + антибот-прокси]
- exists=True alive=True | **verdict**: рекомендовать — для веб-поиска и чтения текста/реквизитов (в
- mcp_ready: да — готовый официальный MCP-сервер, пакет npm "firecrawl-mcp-server" (репозиторий firecrawl/firecra
- free_tier: free-план есть (лимит кредитов), далее платно | install: npx -y firecrawl-mcp (env FIRECRAWL_API_KEY) или remote MCP
- what: Уже подключён (Connected). Скрейп/поиск/экстракция через облако Firecrawl с РЕНДЕРОМ JS и встроенным антиботом. У scrape есть параметр proxy: basic|stealth|enha
- env_fit: Годится с оговоркой. ПЛЮС: ходит СВОИМ облачным каналом мимо корп-прокси — подтверждено живым заходом на росс. сайт lunda.ru (вернул свой exit-IP 172.58.130.254, а не заглушку корп-прокси). Параметры 
- evidence: Существование+активность: https://github.com/firecrawl/firecrawl-mcp-server (statusCode 200, repository_id 899407931, latest release v3.2.1, ~6700 звёзд, last c
- url: https://github.com/firecrawl/firecrawl-mcp-server

### curl с cookies из Playwright (антибот-сессия)  [антибот-прокси]
- exists=True alive=True | **verdict**: условно — рекомендовать как штатный приём, но с двумя поправ
- mcp_ready: Готового единого MCP под эту связку НЕТ — это самописный workflow из двух реальных компонентов. Play
- free_tier: да | install: оба уже есть (playwright MCP + curl)
- what: Связка: playwright browser_navigate на карточку (ставит cookie __ddg.../cf_clearance DDoS-Guard/Cloudflare) → browser_evaluate document.cookie → curl --noproxy 
- env_fit: Частично годится, с серьёзной оговоркой про корп-прокси. ПЛЮС: curl --noproxy "*" уводит докач МИМО корп-прокси → ходит с локального (российского) IP, что для росс. сайтов чаще лучше, чем иностранный 
- evidence: curl flag -b/--cookie (заявленный URL подтверждён): https://curl.se/docs/manpage.html#-b — anchor реально существует, плюс локально curl 8.19.0 (Release-Date 20
- url: https://curl.se/docs/manpage.html#-b

### r.jina.ai / s.jina.ai (Jina Reader)  [reader-API / обход-гео]
- exists=True alive=True | **verdict**: рекомендовать (условно для росс.сайтов) — добавить как ступе
- mcp_ready: ДА, есть ОФИЦИАЛЬНЫЙ remote MCP-сервер: пакет/имя "jina-mcp-server", репо github.com/jina-ai/MCP (73
- free_tier: ДА, бесплатно без ключа: 20 RPM (с free-ключом 500 RPM) | install: ничего ставить не надо — просто префикс URL; опц. API-ключ для больших лимитов
- what: Префикс https://r.jina.ai/<URL> → возвращает чистый LLM-friendly markdown; страницу за вас фетчит и рендерит в браузере прокси Jina (свой канал, свой IP). s.jin
- env_fit: ЧАСТИЧНО годится — лучше многих для гео-блокировки, но не панацея под антибот РФ. Проверено вживую (curl --noproxy с нашей машины): (1) КАНАЛ СВОЙ: запрос уходит через --noproxy на r.jina.ai (HTTP 200
- evidence: Репо Reader (живой, 11.3k звёзд, последний коммит 21.05.2026, релиз docker ghcr.io/jina-ai/reader:oss): https://github.com/jina-ai/reader | Офиц. MCP (735 звёзд
- url: https://github.com/jina-ai/reader

### Wayback Machine (web.archive.org) + Availability/CDX API  [обход-гео (зеркало)]
- exists=True alive=True | **verdict**: рекомендовать
- mcp_ready: да — готовый MCP-сервер npm `mcp-wayback-machine` (v3.7.1, автор Joseph Mearman, npx без API-ключей;
- free_tier: да, полностью бесплатно | install: ничего; чистый HTTP API
- what: Зеркало контента, недоступного из-за гео/блокировки/404. API наличия снапшота: archive.org/wayback/available?url=<URL>[&timestamp=YYYYMMDD] → JSON со ссылкой на
- env_fit: ОТЛИЧНО подходит. Проверено практикой через корп-прокси БЕЗ обхода (--noproxy не понадобился): Availability API → HTTP 200/JSON, CDX API → реальная история снапшотов росс. госсайта pub.fsa.gov.ru с 20
- evidence: API (проверено curl): https://archive.org/wayback/available?url=pub.fsa.gov.ru&timestamp=20230101 → JSON snapshot 20220201; https://web.archive.org/cdx/search/c
- url: https://archive.org/help/wayback_api.php

### playwright MCP (уже подключён)  [MCP-браузер]
- exists=True alive=True | **verdict**: рекомендовать
- mcp_ready: да — официальный first-party MCP-сервер Microsoft, npm-пакет @playwright/mcp (НЕ просто API). Уже Co
- free_tier: да, бесплатно | install: npx @playwright/mcp@0.0.76 (пин версии обязателен — @latest зависает под корп-прокси, abou
- what: Полноценный headless-браузер: рендер JS/SPA, обход DDoS-Guard/Cloudflare (повторный navigate после 5-6 сек ставит cf_clearance), скриншот ГЛАЗАМИ для диагностик
- env_fit: Сам инструмент рабочий и подходит как браузерный tier для JS/SPA-рендера, скриншот-диагностики блокеров (ШАГ 0), прайминга cf_clearance/__ddg повторным navigate и как источник cookies для curl --nopro
- evidence: Репо: https://github.com/microsoft/playwright-mcp (34.2k stars, 2.8k forks, Apache-2.0, 555 commits, 66 contributors). Релиз: https://github.com/microsoft/playw
- url: https://github.com/microsoft/playwright-mcp

### fetcher-mcp (jae-jae) — Playwright stealth MCP  [MCP-браузер / антибот-прокси]
- exists=True alive=True | **verdict**: условно — рекомендовать как ЛОКАЛЬНЫЙ браузер-фетчер для рос
- mcp_ready: да — готовый MCP-сервер, npm-пакет "fetcher-mcp" (запуск: npx -y fetcher-mcp). Инструменты: fetch_ur
- free_tier: да, бесплатно (self-hosted, локальный браузер) | install: npx -y fetcher-mcp (или uvx-аналог); browser_install для Chromium
- what: MCP-сервер на Playwright headless: fetch_url/fetch_urls (батч параллельно), рендер JS, Readability→markdown. Параметр waitForNavigation:true специально для CAPT
- env_fit: Условно годится. ПЛЮС: работает ЛОКАЛЬНО (Playwright headless на машине пользователя) → использует локальный IP, а не иностранный, как cloud-MCP (exa/firecrawl) → нет гео-заглушек/404 на росс.сайтах (
- evidence: GitHub: https://github.com/jae-jae/fetcher-mcp (1.1k stars, 100 forks, 102 commits, latest v0.3.9 от 2026-01-14, README-правка 2025-09-26, MIT, TypeScript). npm
- url: https://github.com/jae-jae/fetcher-mcp

### Tavily MCP  [MCP-поиск]
- exists=True alive=True | **verdict**: условно (реальный и живой, готовый официальный MCP; но избыт
- mcp_ready: да, официальный — npm-пакет tavily-mcp (bin: tavily-mcp; mcpName io.github.tavily-ai/tavily-mcp). Ло
- free_tier: Да: 1000 кредитов/мес бесплатно, без карты (1-2 кредита/поиск). Дальше от $49/мес. Нужен к | install: npx -y tavily-mcp@latest (env TAVILY_API_KEY). Или remote: https://mcp.tavily.com/mcp/?tav
- what: Веб-поиск в реальном времени, оптимизированный под LLM/RAG: search, extract, map, crawl. Самый популярный поисковый MCP (~27K скач./нед на npm). Хорошая база дл
- env_fit: Условно годится. Tavily — облачный поисковый API (как exa/firecrawl): запросы идут через серверы Tavily, а не с нашего IP, поэтому иностранный IP/гео для САМОГО поиска не помеха (Tavily сам краулит). 
- evidence: GitHub репо (2130 звёзд, 272 форка, 20 контрибьюторов, создан 2025-01-27, last push 2026-06-21, MIT): https://github.com/tavily-ai/tavily-mcp | npm пакет tavily
- url: https://github.com/tavily-ai/tavily-mcp (npm: tavily-mcp)

### Yandex Search MCP  [MCP-поиск]
- exists=True alive=True | **verdict**: условно
- mcp_ready: Да, готовый официальный MCP. Два официальных варианта: (1) монорепо yandex-cloud/mcp -> npm @yandex-
- free_tier: Платный: нужен Yandex Cloud Search API key + folder_id (роль search-api.editor, scope yc.s | install: Remote (реком.): npx -y mcp-remote https://...apigw.yandexcloud.net:3000/sse --header ApiK
- what: Официальный MCP от Яндекса поверх Yandex Search API: web_search_post (выдача со ссылками) и ai_search_post (AI-ответ моделью Yazeka). Та же выдача, что yandex.r
- env_fit: Покрытие рунета/кириллицы/росс. поставщиков и нормбазы — лучшее, как заявлено (выдача yandex.ru). НО: (1) платно — требует подписки на Yandex Search API + API key + Folder ID + Yandex Cloud аккаунт (I
- evidence: Официальный репо (заявленный URL подтверждён): https://github.com/yandex/yandex-search-mcp-server (39 звёзд, Python/Dockerfile, создан 2025-06-26, tools ai_sear
- url: https://github.com/yandex/yandex-search-mcp-server (npm-обёртка: yandex-search-mcp)

### Kagi MCP  [MCP-поиск]
- exists=True alive=True | **verdict**: условно
- mcp_ready: да, готовый официальный MCP-сервер от Kagi Inc. Пакет PyPI: kagimcp (uvx kagimcp). Также docker mcp/
- free_tier: НЕТ бесплатного API. Требуется платная подписка Kagi + отдельный платный Search API (билли | install: uvx kagimcp (env KAGI_API_KEY). claude mcp add kagi -- uvx kagimcp.
- what: Официальный MCP Kagi: качественный поиск без рекламы/трекинга + summarizer и др. инструменты Kagi. Высокое качество выдачи, приватность.
- env_fit: ПЛОХО подходит под нашу задачу. (1) Требует ПЛАТНЫЙ Kagi API-ключ — pay-per-use, нужна привязка карты, осмысленного free-tier для Search/Extract нет (бесплатен только Small Web RSS). (2) Kagi — западн
- evidence: GitHub (официальный, 422 звезды, last push 2026-05-27, 7 контрибьюторов, MIT): https://github.com/kagisearch/kagimcp | PyPI kagimcp v1.0.0 от 2026-05-21, ~6200 
- url: https://github.com/kagisearch/kagimcp

### DuckDuckGo MCP  [MCP-поиск]
- exists=True alive=True | **verdict**: условно — реален и жив, но под наш иностранный IP+корп-прокс
- mcp_ready: да, готовый официальный MCP-сервер. Пакет PyPI: duckduckgo-mcp-server (uvx duckduckgo-mcp-server). Т
- free_tier: Полностью бесплатно, БЕЗ ключа и регистрации. | install: uvx duckduckgo-mcp-server. claude mcp add ddg -- uvx duckduckgo-mcp-server. Ключ НЕ нужен.
- what: Веб-поиск через DuckDuckGo + извлечение/парсинг контента страниц. Самый простой «бесплатный без регистрации» вариант. Тулзы search и fetch_content.
- env_fit: Слабо подходит. Тул search всегда ходит голым httpx без impersonation, а DuckDuckGo агрессивно rate-limit'ит/блокирует запросы с датацентровых/иностранных IP и общих корп-прокси (наш профиль: трафик C
- evidence: GitHub https://github.com/nickclyde/duckduckgo-mcp-server (1272 звезды, 171 форк, MIT, Python, 10 контрибьюторов, last push 2026-05-08, владелец https://github.
- url: https://github.com/nickclyde/duckduckgo-mcp-server (pypi: duckduckgo-mcp-server)

### Serper (Google) MCP  [MCP-поиск]
- exists=True alive=True | **verdict**: условно
- mcp_ready: да, 2 готовых неофициальных MCP-сервера. (1) marcopesani/mcp-server-serper — TS, npm-пакет `serper-s
- free_tier: Да: Serper даёт 2500 бесплатных запросов при регистрации (разовый грант), далее платно по  | install: npx -y serper-search-scrape-mcp-server (env SERPER_API_KEY). Или uvx serper-mcp-server. cl
- what: Доступ к выдаче Google через Serper API: google_search + scrape. По сути — настоящая выдача Google (включая google.ru-сегмент через параметры gl/hl) в виде MCP.
- env_fit: Условно годится. Serper — платный SERP-API (serper.dev, нужен SERPER_API_KEY; free-tier ~2500 запросов). Запросы идут в облако Serper, поэтому реальная выдача Google по РФ-сегменту достижима через пар
- evidence: GitHub API marcopesani/mcp-server-serper (200, 157★, created 2025-02-20, pushed 2025-03-13, updated 2026-06-22, not archived): https://api.github.com/repos/marc
- url: https://github.com/marcopesani/mcp-server-serper (также garylab/serper-mcp-server)

### browser-use (local MCP)  [MCP-браузер]
- exists=True alive=True | **verdict**: условно
- mcp_ready: да — встроенный MCP-сервер в самом фреймворке (модуль browser_use/mcp/server.py, класс BrowserUseSer
- free_tier: да, опенсорс бесплатный; НО требует свой LLM-ключ (OPENAI_API_KEY/ANTHROPIC_API_KEY) для а | install: claude mcp add browser-use -- uvx --from 'browser-use[cli]' browser-use --mcp (uvx — уже н
- what: Локальный MCP-сервер поверх движка browser-use: low-level инструменты (browser_navigate/click/type/extract_content/scroll) + автономный агент retry_with_browser
- env_fit: УСЛОВНО годится. ПЛЮС для росс.сайтов: сервер локальный, гоняет локальный Chrome/Chromium — трафик к сайтам идёт с НАШЕГО IP, а не с иностранного IP Claude, т.е. снимает геоблок/заглушки (главная боль
- evidence: https://github.com/browser-use/browser-use (репо, MIT, ~99.9k звёзд, 320 контрибьюторов, создан 2024-10-31, last push 2026-06-20); релизы 129 шт, последний 0.13
- url: https://github.com/browser-use/browser-use

### browser-use Cloud MCP  [MCP-браузер]
- exists=True alive=True | **verdict**: условно
- mcp_ready: да — официальный first-party hosted Cloud MCP (remote, HTTP). Эндпоинт https://api.browser-use.com/v
- free_tier: частично — стартовые кредиты, далее платно | install: HTTP/remote MCP endpoint + BROWSER_USE_API_KEY
- what: Облачный (hosted) вариант browser-use: браузер крутится в их инфраструктуре, подключение по API-ключу, без локальной установки браузера.
- env_fit: Условно годится. Сам MCP-транспорт — одно HTTPS-соединение к api.browser-use.com, поэтому наш корп-прокси/иностранный IP на транспорт почти не влияет (нужен лишь исходящий HTTPS через прокси + платный
- evidence: Офиц. док hosted Cloud MCP (проверено fetch): https://docs.browser-use.com/cloud/guides/mcp-server | Док локального OSS MCP: https://docs.browser-use.com/open-s
- url: https://docs.browser-use.com/

### Apify MCP  [MCP-поиск]
- exists=True alive=True | **verdict**: условно
- mcp_ready: да — официальный готовый MCP-сервер. npm-пакет @apify/actors-mcp-server (latest 0.11.3, beta 0.11.4-
- free_tier: да — $5 бесплатных кредитов/мес на платформе Apify | install: npx @apify/actors-mcp-server + APIFY_TOKEN (или hosted)
- what: Доступ к Apify Store (тысячи готовых Actors-скрейперов: соцсети, поисковики, карты, e-commerce, любой сайт). MCP запускает Actor и отдаёт результат; доступ к хр
- env_fit: Условно годится. (+) Hosted-сервер mcp.apify.com — иностранный SaaS (Apify, EU/Прага), доступен по HTTPS через OAuth/Bearer; иностранный IP тут не помеха, а скорее плюс — нужно лишь, чтобы корп-прокси
- evidence: npm: https://registry.npmjs.org/@apify/actors-mcp-server (latest 0.11.3, опубликован 2026-06-22, MIT, author Apify); GitHub: https://github.com/apify/apify-mcp-
- url: https://github.com/apify/apify-mcp-server

### Tavily Extract  [reader-API]
- exists=True alive=True | **verdict**: условно
- mcp_ready: да, официальный — tavily-ai/tavily-mcp (npm tavily-mcp v0.2.20; tools tavily-search/extract/map/craw
- free_tier: да, бесплатный аккаунт с кредитами; basic 1 кредит/5 URL, advanced 2 кредита/5 URL — очень | install: claude mcp add --transport http tavily "https://mcp.tavily.com/mcp/?tavilyApiKey=<key>" (н
- what: Extract API: URL (или до 20 за раз)→чистый markdown/text. Снимает boilerplate, рендерит JS. Есть query-режим: reranking чанков по релевантности вопросу + chunks
- env_fit: Условно. Tavily — US-облако (api.tavily.com / mcp.tavily.com); читает контент со СВОЕГО иностранного IP, не через наш корп-прокси. Это reader-API (отдаёт текст/markdown, НЕ скачивает файл). Для РОССИЙ
- evidence: GitHub репо (живой, 2.1k★, 272 forks, 218 коммитов, MIT, 14 contributors, последний коммит 2026-05-29 "feat: add keyless support"): https://github.com/tavily-ai
- url: https://docs.tavily.com/documentation/api-reference/endpoint/extract

### Spider.cloud  [reader-API]
- exists=True alive=True | **verdict**: условно
- mcp_ready: да, официальный — remote https://mcp.spider.cloud/mcp (Bearer) ИЛИ локально npx -y spider-cloud-mcp 
- free_tier: бесплатный баланс для теста (без подписки); pay-as-you-go $1/GB + $0.001/мин CPU, провалив | install: claude mcp add spider --transport http https://mcp.spider.cloud/mcp -H "Authorization: Bea
- what: Очень быстрый Rust-движок: scrape/crawl/search/transform, URL→markdown (на 60-80% меньше токенов чем raw HTML). Unblocker со stealth+ротацией прокси+авто-ретрая
- env_fit: Условно годится — но ТОЛЬКО как ПЛАТНЫЙ инструмент (нужен SPIDER_API_KEY, кредитная тарификация; без ключа ничего не работает). Сильная сторона под наше окружение: cloud-API ходит со своей инфраструкт
- evidence: Core engine (зрелый, живой): https://github.com/spider-rs/spider (254★, 211 forks, 166 releases, latest v2.48.13 2026-03-31, last push 2026-06-08). Офиц.сайт: h
- url: https://spider.cloud/mcp/

### Oxylabs Web Unblocker / Web Scraper API  [антибот-прокси]
- exists=True alive=True | **verdict**: условно
- mcp_ready: ДА, официальный MCP: пакет PyPI `oxylabs-mcp` (uvx oxylabs-mcp), репо oxylabs/oxylabs-mcp, mcp-name 
- free_tier: 1 неделя триал Web Scraper API без карты; AI Studio 1000 кредитов бесплатно; Web Unblocker | install: MCP: claude mcp add oxylabs -- command uvx args oxylabs-mcp (env OXYLABS_USERNAME/PASSWORD
- what: Web Unblocker — backconnect-прокси unblock.oxylabs.io:60000 (drop-in замена прокси, обход антиботов, JS-рендер, fingerprint, retry, sticky). Web Scraper API — R
- env_fit: Концептуально РЕШАЕТ нашу гл. боль (трафик с иностранного IP): все запросы идут через серверы Oxylabs из 195+ стран, можно задать geo=country:RU → росс. сайты видят росс. IP, обходя гео-заглушки/404 о
- evidence: GitHub (официальный, 98 stars, 25 forks, 74 commits, 9 contributors, MIT, последний коммит 08.06.2026, последний релиз v0.8.1 23.04.2026, 23 релиза): https://gi
- url: https://developers.oxylabs.io/products/web-unblocker

### Decodo (бывш. Smartproxy) Site Unblocker + Web Scraping API  [антибот-прокси]
- exists=True alive=True | **verdict**: условно
- mcp_ready: да, официальный готовый MCP-сервер. Имя пакета npm: @decodo/mcp-server (v1.2.3). Облачный эндпоинт h
- free_tier: MCP: до 2000 запросов бесплатно, без карты; прокси: 3-дневный триал (100MB residential). h | install: MCP: настройка в клиенте через npx (env API key Web Scraping API basic auth); прокси HTTP(
- what: Site Unblocker — proxy-эндпоинт с обходом антиботов/CAPTCHA/JS. Web Scraping API: jsRender, geo (страна выхода), locale, deviceType, tokenLimit. 115M+ residenti
- env_fit: НЕ ГОДИТСЯ под наше окружение БЕЗ зарубежного аккаунта. Технически — да: трафик scrape идёт через residential-сеть Decodo (125M+ IP, 195+ локаций, geo до country/city/ZIP/ASN, jsRender, anti-bot, loca
- evidence: Сайт/продукт: https://decodo.com/ ; https://decodo.com/proxies/site-unblocker (заявленный url, продукт существует) ; https://decodo.com/scraping/mcp-server . MC
- url: https://decodo.com/proxies/site-unblocker

### Zyte API (бывш. Crawlera / Smart Proxy Manager)  [антибот-прокси]
- exists=True alive=True | **verdict**: условно
- mcp_ready: самописный (официального Zyte MCP нет). Official channel = «build your own» через FastMCP+Docker MCP
- free_tier: $5 бесплатного кредита на первый месяц при регистрации (Enterprise $200). Тарификация толь | install: HTTP-endpoint: curl Bearer на api.zyte.com (или proxy-mode); ключ из app.zyte.com. Для рос
- what: HTTP-API api.zyte.com ИЛИ proxy-mode: ИИ-подбор минимальной связки прокси+техник под каждый сайт (5 ценовых тиров). ipType=residential/datacenter, geolocation (
- env_fit: ИДЕАЛЬНО решает гео/корп-прокси-проблему, НО платно и требует API-ключ. Server-side прокси: запросы уходят с IP самого Zyte, параметр geolocation=ISO-код (RU поддерживается, residential IP в 200+/249 
- evidence: Офиц.docs (200 OK): https://docs.zyte.com/zyte-api/usage/reference.html ; https://docs.zyte.com/zyte-api/usage/browser.html ; https://docs.zyte.com/zyte-api/usa
- url: https://docs.zyte.com/zyte-api/usage/reference.html

### curl --noproxy с кастомным User-Agent  [обход-гео / антибот-прокси]
- exists=True alive=True | **verdict**: условно
- mcp_ready: нет — это CLI-инструмент, вызывается через Bash tool. Отдельного MCP-сервера не требуется и не сущес
- free_tier: да, бесплатно | install: уже установлен (curl 8.19.0, Schannel)
- what: curl 8.19.0 уже стоит в Git Bash. Флаг --noproxy "*" заставляет ОБОЙТИ корп-прокси (исходить с локального IP компании, а не с иностранного выхода Claude). Брауз
- env_fit: ЧАСТИЧНО / НЕ подтверждено как заявлено. Эмпирическая проверка в этой сессии: флаги `--noproxy "*"` и `-A` существуют и работают как в документации, НО операционный механизм «исходить с локального IP 
- evidence: Локально: `curl --version` → curl 8.19.0 (x86_64-w64-mingw32) libcurl/8.19.0 Schannel, Release-Date 2026-03-11. Репозиторий: https://github.com/curl/curl — 42.2
- url: https://curl.se/docs/manpage.html#--noproxy

### mcp-server-fetch (официальный) с --proxy-url / --user-agent  [MCP-браузер / антибот-прокси]
- exists=True alive=True | **verdict**: условно
- mcp_ready: да — готовый MCP-сервер, пакет `mcp-server-fetch` (PyPI). У вас уже подключён как 'fetch' (холодный 
- free_tier: да, бесплатно (свой/чужой прокси отдельно) | install: uvx mcp-server-fetch ...args; для SOCKS5: uvx --with 'httpx[socks]' mcp-server-fetch --pro
- what: Официальный MCP-fetch (uvx mcp-server-fetch). HTML→markdown. Аргументы: --proxy-url <RU-прокси/SOCKS> (направить трафик через росс. точку выхода → обход гео), -
- env_fit: Частично. Реальны и подтверждены аргументы: `--proxy-url <URL>` (роутинг через прокси), `--user-agent='<строка>'` (обход UA-блока), `--ignore-robots-txt`. ВАЖНО: сервер сам НЕ даёт росс. точку выхода 
- evidence: PyPI (авторитетно): https://pypi.org/project/mcp-server-fetch/ — версия 2026.6.4, released Jun 3, 2026, Author "Anthropic, PBC.", License MIT, Python>=3.10. Док
- url: https://github.com/modelcontextprotocol/servers/tree/main/src/fetch

### Российский SOCKS5/HTTP-прокси или VPN с RU-выходом  [обход-гео]
- exists=True alive=True | **verdict**: условно
- mcp_ready: Не отдельный MCP — это транспортная возможность, встроенная в существующие fetch-инструменты. Готовы
- free_tier: зависит от провайдера прокси/VPN (нужен RU-эндпоинт) | install: curl -x socks5h://host:port URL; либо env HTTPS_PROXY/ALL_PROXY перед запуском uvx-сервера
- what: Корень проблемы 'иностранный IP → заглушка' — точка выхода. Локальный SOCKS5/VPN с РОССИЙСКОЙ точкой выхода решает радикально: задать HTTPS_PROXY/ALL_PROXY=sock
- env_fit: Технически годится и проверено ЛОКАЛЬНО на этой машине: curl 8.19.0 (release 2026-03-11) имеет -x/--proxy, --socks5, --socks5-hostname; вызов `curl -x socks5://127.0.0.1:9` вернул exit 7 (COULDNT_CONN
- evidence: curl manpage (-x/--proxy, socks5): https://curl.se/docs/manpage.html ; curl SOCKS docs: https://curl.se/docs/manpage.html#--socks5 ; curl source/release (жив, 8
- url: https://curl.se/docs/manpage.html#-x

### node-fetch fetch-mcp с enterprise-proxy (xiaobing-huang)  [антибот-прокси]
- exists=True alive=True | **verdict**: условно
- mcp_ready: Самописный/clone-build, имя пакета НЕ на npm. Это форк zcaceres/fetch-mcp; ставится вручную: git clo
- free_tier: да, бесплатно (self-hosted) | install: клон+build (Node), затем как stdio MCP; env HTTPS_PROXY=http://user:pass@proxy:8080
- what: MCP-fetch на node-fetch + https-proxy-agent, заточен под КОРПОРАТИВНЫЕ сети: автодетект HTTP_PROXY/HTTPS_PROXY/NO_PROXY, либо явный proxy в самом tool-call (при
- env_fit: НЕ решает нашу корневую проблему. Заявленные фичи (autodetect HTTP_PROXY/HTTPS_PROXY/NO_PROXY + case-insensitive, явный proxy в tool-call с приоритетом над env, wildcard/CIDR в NO_PROXY/bypass, basic-
- evidence: Репозиторий: https://github.com/xiaobing-huang/fetch-mcp (MIT, TypeScript, 0 stars/0 forks/0 releases/0 packages). Единственный авторский коммит — enterprise-pr
- url: https://github.com/xiaobing-huang/fetch-mcp

### Встроенные WebSearch / WebFetch (Claude Code)  [MCP-браузер (встроенный)]
- exists=True alive=True | **verdict**: условно
- mcp_ready: Не MCP. Это нативные server-tools харнесса/Claude API (web_search_*, web_fetch_*), встроены в Claude
- free_tier: да | install: встроены
- what: Нативные инструменты харнесса. WebFetch тянет URL и обрабатывает контент моделью; WebSearch — поиск. Ходят через инфраструктуру Anthropic (иностранный канал).
- env_fit: Плохо подходит для российских сайтов, годится для иностранных. (1) WebSearch — официально US-only (зафиксировано в schema самого инструмента: "Search the web... US-only"); поиск геопривязан к США, рос
- evidence: Офиц. документация WebSearch: https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool (актуальна — упоминает Opus 4.8/Fable 5, версия web_
- url: https://docs.anthropic.com/en/docs/claude-code

### Кэш поисковиков (Google cache / Yandex / Bing) как зеркало  [обход-гео (зеркало)]
- exists=True alive=True | **verdict**: условно
- mcp_ready: Нет. Готового MCP-сервера «search-engine cache» не существует. Доступ только техникой: вытащить URL 
- free_tier: да | install: ничего
- what: Сохранённые копии страниц у поисковиков как зеркало заблокированного/гео-закрытого контента. ВАЖНО: классический Google 'cache:'/webcache.googleusercontent.com 
- env_fit: Частично годится. Google-ветка бесполезна (мертва). Yandex «сохранённая копия» — единственная живая из поисковиков: русский индекс, с иностранного корп-IP Yandex доступен лучше, чем росс. госсайты (pu
- evidence: Заявленный URL ФЕЙКОВЫЙ (404): https://blog.google/products/search/google-search-cache-feature-deprecated/ — такой страницы нет (проверено firecrawl, statusCode
- url: https://blog.google/products/search/google-search-cache-feature-deprecated/

### Puppeteer MCP (self-hosted, sultannaufal)  [MCP-браузер]
- exists=True alive=True | **verdict**: отклонить
- mcp_ready: да (самостоятельный self-hosted сервер, имя: sultannaufal/puppeteer-mcp-server). НЕ npm/uvx-пакет: н
- free_tier: да, бесплатный (опенсорс, локальный) | install: docker / npm self-host + конфиг прокси в puppeteer launch args
- what: Self-hosted Puppeteer MCP: navigate/screenshot/click/evaluate, несколько транспортов (stdio/HTTP), API-key auth, Docker-деплой. (Офиц. reference puppeteer-MCP и
- env_fit: Слабо. Тот же headless Chromium без stealth и без встроенного обхода прокси, что и уже подключённый playwright-MCP. Своего proxy-bypass/анти-бот нет → упрётся в те же DDoS-Guard/Cloudflare/404 на росс
- evidence: GitHub API (прямой ответ, не только заявл. URL): https://github.com/sultannaufal/puppeteer-mcp-server — id 1025338552, owner sultannaufal id 68039339, TypeScrip
- url: https://github.com/sultannaufal/puppeteer-mcp-server

### Jina ReaderLM-v2 (self-host модель)  [reader-API]
- exists=True alive=True | **verdict**: отклонить
- mcp_ready: Нет готового MCP-сервера именно под ReaderLM-v2. Это МОДЕЛЬ, не сервер. Доступна тремя путями: (1) J
- free_tier: веса бесплатны (лицензия CC BY-NC 4.0 — НЕкоммерческая); через Reader API запрос ест 3x то | install: локально: transformers/vllm + GPU (рекоменд. RTX 3090/4090; CPU медленно). Через API: доба
- what: Локальная модель 1.5B (на базе Qwen2.5) для офлайн-конвертации HTML→markdown/JSON, 29 языков, до 512K токенов, бьёт GPT-4o на 15-20% по бенчмаркам экстракции. М
- env_fit: ВАЖНО: это КОНВЕРТЕР HTML→markdown/JSON, НЕ фетчер — сам URL не качает, ему надо подать готовый HTML. Поэтому под нашу задачу (обход гео/прокси) он напрямую НЕ решает узкое место (сам фетч). Два сцена
- evidence: HuggingFace модель-карточка (HTTP 200, 154 370 загрузок/мес, 1.54B, Qwen2.5-1.5B база, 29 языков вкл. русский, 512K контекст): https://huggingface.co/jinaai/Rea
- url: https://huggingface.co/jinaai/ReaderLM-v2

### archive.today (archive.ph / archive.is / archive.li)  [обход-гео (зеркало)]
- exists=True alive=True | **verdict**: отклонить
- mcp_ready: Нет. Выделенного MCP-сервера для archive.today НЕ существует. Все найденные MCP веб-архивации — толь
- free_tier: да, бесплатно | install: ничего; веб-сервис
- what: Делает текст+граф. снапшот любой страницы по запросу (красная строка — заархивировать live-URL, чёрная — искать готовый снапшот). Рендерит non-headless Chromium
- env_fit: НЕ ГОДИТСЯ под наше окружение. (1) Заблокирован Роскомнадзором в РФ с 2016 (Wikipedia). (2) Эмпирическая проверка с этой машины: все 3 домена (archive.today, archive.ph, archive.is) дают HTTP 000 / ti
- evidence: Существование/живость: https://en.wikipedia.org/wiki/Archive.today (основан 16.05.2012, события до янв.2026) ; https://wiki.archiveteam.org/index.php/Archive.to
- url: https://archive.today/

### Hyperbrowser MCP  [MCP-браузер]
- exists=None alive=None | **verdict**: 
- mcp_ready: да — hyperbrowser-mcp (npm)
- free_tier: да — бесплатные стартовые кредиты, далее платно | install: npx hyperbrowser-mcp + HYPERBROWSER_API_KEY
- what: Облачные браузеры Hyperbrowser: scrape_webpage, extract_structured_data, crawl_webpages, + агенты (Browser-Use/Claude Computer Use/OpenAI CUA), скриншоты, сесси
- env_fit: 
- evidence: 
- url: https://github.com/hyperbrowserai/mcp

### Steel.dev MCP  [MCP-браузер]
- exists=None alive=None | **verdict**: 
- mcp_ready: да — steel-dev/steel-mcp-server
- free_tier: да — опенсорс ядро (steel-browser, self-host бесплатно); облако с free-кредитами | install: npx/clone steel-mcp-server + STEEL_API_KEY (или self-host steel-browser)
- what: MCP-сервер поверх Steel browser API (Puppeteer-инструменты навигации). Опенсорсный браузер-API для ИИ-агентов; можно self-host (steel-browser) или их облако.
- env_fit: 
- evidence: 
- url: https://github.com/steel-dev/steel-mcp-server

### Diffbot Extract / Article API  [reader-API]
- exists=None alive=None | **verdict**: 
- mcp_ready: частично — официального вендорского MCP нет; есть сторонние обёртки на GitHub (поиск diffbot mcp), н
- free_tier: да: Free $0/мес, без карты, 10000 кредитов (1 кредит/страница, 2 с прокси), полный доступ  | install: чистый HTTP-эндпоинт, дёргается через curl/fetch: GET api.diffbot.com/v3/article?token=<t>
- what: Computer-vision экстракция: классифицирует страницу (article/product/discussion) и тянет структурированный JSON (текст, автор, дата, картинки, sentiment). Работ
- env_fit: 
- evidence: 
- url: https://www.diffbot.com/pricing/

### Apify (Website Content Crawler / RAG Web Browser)  [reader-API]
- exists=None alive=None | **verdict**: 
- mcp_ready: да — Apify MCP (mcp.apify.com), акторы доступны как MCP-инструменты: npx mcp-remote https://mcp.apif
- free_tier: да: Free-план $5 кредитов КАЖДЫЙ месяц + доступ к Apify Proxy; акторы бесплатны, платишь т | install: npx mcp-remote https://mcp.apify.com/?tools=<actor> --header "Authorization: Bearer <token
- what: Платформа акторов. Website Content Crawler — deep-crawl сайта→markdown для RAG. RAG Web Browser — search+fetch: гуглит, скрейпит топ-N полноценным браузером, от
- env_fit: 
- evidence: 
- url: https://apify.com/apify/rag-web-browser

### Postlight Parser (ex-Mercury Parser)  [reader-API]
- exists=True alive=False | **verdict**: отклонить
- mcp_ready: Нет официального MCP. Это npm-библиотека/CLI (@postlight/parser); обернуть в MCP можно самому. Есть 
- free_tier: полностью бесплатен (open source, Apache-2.0/MIT). Хостед Mercury Parser API ДАВНО закрыт  | install: npm -g install @postlight/parser, затем postlight-parser <URL> --format=markdown. Запускае
- what: Open-source экстрактор контента статьи (текст, заголовок, автор, дата, lead-image) из URL. CLI: postlight-parser <URL> --format=markdown. Поддерживает кастомные
- env_fit: Плохо подходит как инструмент веб-ДОСТУПА. Это Node CLI/lib, который сам ходит на URL через ЛОКАЛЬНУЮ сеть машины — тот же иностранный IP / корп-прокси, что и у Claude → росс. сайты отдадут заглушку/4
- evidence: GitHub репо: https://github.com/postlight/parser (5784★, 527 forks, Apache-2.0, archived=false). GitHub API: https://api.github.com/repos/postlight/parser — pus
- url: https://github.com/postlight/parser

## AUDIT NOTES

- ГЛАВНОЕ для текущего окружения (Windows, RU-локаль, корп-прокси, иностранный IP исходящего трафика Claude): доступ РАСПАДАЕТСЯ НА ДВА КОНТУРА, и это ключ ко всему.\n\n1) ЧТЕНИЕ страниц под корп-прокси — рабочие каналы exa и firecrawl: они ходят СВОИМ облачным каналом мимо корп-прокси, поэтому достают российские сайты, которые curl-через-прокси и playwright-через-прокси не видят. Это де-факто замен
- Зона веб-доступа покрыта плотно. ЕДИНАЯ ЛЕСТНИЦА (обязательный порядок чтения): exa → fetch MCP → playwright → WebFetch (последняя, 80-90% fail). Доп. обход чтения: r.jina.ai. ГЛАВНАЯ развилка под корп-прокси: ЧИТАТЬ страницу → exa/firecrawl (ходят своим каналом); СКАЧАТЬ файл → curl --noproxy '*' (+cookies из playwright за ботозащитой). Корень всего — геоблок Anthropic на RU IP (2026-05-26_anthro
- Скилл harvest лежит как slash-команда `C:/Users/Даниил/.claude/commands/harvest.md` (+ memory/harvest_workflow.md), а НЕ в skills/harvest/ — в skills/ его нет. У image-text-replace веб-части НЕТ: SKILL.md содержит лишь GitHub-ссылки на свои зависимости (EasyOCR/IOPaint/LaMa), а не методы добычи из веба — для зоны веб-доступа этот скилл пустой. Сквозной принцип всех скиллов добычи: НЕ доверять WebF
- ГЛАВНОЕ ПО ЗОНЕ ВЕБ-ДОСТУПА:  1) ЛЕСТНИЦА (обязательный порядок из CLAUDE.md): exa (semantic search+fetch) → fetch MCP (простой HTML) → playwright (антибот/SPA) → встроенный WebFetch (последняя, 80-90% fail). WebSearch встроенный — слабее exa/firecrawl.  2) КЛЮЧЕВОЕ РАЗДЕЛЕНИЕ под корп-прокси: облачные MCP (exa, firecrawl) ходят СВОИМ каналом и обходят гео-блок/прокси, но отдают ТОЛЬКО текст/markd
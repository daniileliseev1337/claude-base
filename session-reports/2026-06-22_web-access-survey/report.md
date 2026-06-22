# Session report — Сводка способов веб-доступа Claude (2026-06-22)

## Что сделал
- По запросу пользователя собрал **полную сводку всех способов беспрепятственного веб-доступа Claude** в текущем окружении.
- Метод: Workflow fan-out (67 агентов, 5.8M токенов, sonnet-сбор + opus-синтез) — аудит базы (56 каналов) ∥ внешний research (58 инструментов) → adversarial-верификация существования каждого. Параллельно — живая эмпирика окружения (curl/exa/firecrawl/WebFetch/playwright/r.jina/Wayback на RU/зарубеж).
- Deliverable: `СВОДКА-веб-доступ-Claude.md` (+ `empirical-env-matrix.md`, `wf-parsed.md`).
- Обновил базу (распространяется через sync-base): `CLAUDE.md` «Веб-доступ — лестница» (гео-разрез) и `memory/feedback_web_direct_access.md` ШАГ −1 (модель 3 состояний машины). Per-machine факт — в авто-память.

## Ключевые находки
- **Egress зависит от МАШИНЫ, диагностика `curl --noproxy "*" https://ipinfo.io/json`** (env-проверки мало — системный VPN в переменных не виден):
  - (a) ПК в РФ без прокси/VPN → RU-IP, всё напрямую.
  - (b) ПК в РФ + прокси в терминале → `--noproxy` = RU-IP (берёт росс.), playwright без --proxy-server = about:blank.
  - (c) системный VPN на всё устройство (этот хаб: Cloudflare WARP, Дубай AE) → `--noproxy` и playwright уходят за рубеж → росс. сайты режут; читать только облаком.
- **RU-коммерческие** (нормы/поставщики): берут облачные каналы (WebFetch/exa/firecrawl/r.jina); локальные (curl/playwright) на VPN-машине — нет.
- **RU-госсайты** (pub.fsa/ЕГРЮЛ/АРШИН) — заблокированы во ВСЕХ протестированных каналах (curl 000, exa 403, firecrawl tunnel-fail, jina 422); жив только Wayback (снимок 2022). **Это единственная реальная дыра.**
- playwright @0.0.76 (пин) — about:blank ушёл, зарубеж работает.

## Источники
- claude-base: CLAUDE.md, memory/feedback_web_direct_access.md, proxy_github.md, reference_mcp.md, скиллы doc-finder/supplier-due-diligence/harvest.
- Внешний research: GitHub/npm/pypi верификация 58 инструментов (exa/firecrawl).
- Эмпирика: ipinfo.io, example.com, consultant.ru, pub.fsa.gov.ru, archive.org/wayback.

## Где сломался / ограничения
- 4 verify-агента оборвались (Hyperbrowser/Steel/Apify/Diffbot — connection closed) — данные по ним частичны.
- Реальная пробиваемость росс. госсайтов через RU-гео антибот-API (ScrapingAnt/Bright Data) НЕ проверена боем — нужен free-ключ. Рекомендовано как «протестировать», не «гарантия».
- Часть субагентов в env_fit исходила из «curl --noproxy = локальный RU-IP» — верно для (a)/(b), НЕВЕРНО для (c); разрешено в пользу эмпирики.

## Уроки (в базу)
- Гео-доступ — функция МАШИНЫ, не глобальное правило; диагностировать ipinfo, держать модель 3 состояний.
- Системный VPN ≠ «нет прокси» в смысле доступа к росс. сайтам.
- Для росс. госсайтов нужен реальный RU-exit-IP — задача на следующую сессию (+ раздача через sync-base).

## SOLVE (выполнено в этой же сессии)
- **Диагноз:** блок росс. госсайтов — ЧИСТО ГЕО (живой RU-SOCKS5: pub.fsa/fgis → 200, антибота нет). Дорогие браузерные антибот-сервисы для СТРАНИЦ не нужны.
- **Создан скилл `ru-gov-access`** (`skills/ru-gov-access/SKILL.md` + `tools/ru_fetch.py`): определяет egress (ipinfo), на иностранном — RU-SOCKS5 (свой `$RU_PROXY` либо авто-источник бесплатных proxifly + health-check). End-to-end проверен: с egress=AE → pub.fsa HTTP 200, реальный HTML. Free, без ключей/MCP, раздаётся sync-base.
- **Граница (честно):** JSON-API реестров (FSA cert-search) за WAF → 403 с датацентрового RU-IP; для ДАННЫХ нужен residential-RU/браузер (residential `$RU_PROXY` / playwright `--proxy-server` / ScrapingAnt browser country=RU free — требует ключа, не тестировано). На ПК в РФ (офисный IP) API вероятно открывается напрямую.

## Остаётся
- (опц.) Протестировать data-слой реестров через ScrapingAnt free-ключ или residential `$RU_PROXY`.
- Проверить на рабочем ПК в РФ, что API реестров открывается напрямую `--noproxy`.
- Закоммитить+запушить правки базы (CLAUDE.md, feedback_web_direct_access.md, skills/ru-gov-access, session-report) для раздачи консьюмерам.

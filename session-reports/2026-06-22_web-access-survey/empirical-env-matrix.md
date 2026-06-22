# Эмпирическая матрица веб-доступа — DANIILPC (2026-06-22)

Снято живыми тестами с этой машины (Claude Code). Дополняет результаты Workflow `wb9kc8f9q`.

## Ключевой факт окружения

**Прямой egress = Cloudflare WARP, IP `104.28.250.184`, гео Дубай (AE), AS13335 Cloudflare.**
(`curl --noproxy "*" https://ipinfo.io/json`)

- Это НЕ российский и НЕ классический корп-HTTP-прокси (в shell нет `HTTP_PROXY/HTTPS_PROXY`).
- Весь локальный трафик (curl, локальный браузер playwright, вероятно uvx fetch MCP) выходит через WARP/Дубай.
- Следствие: зарубеж — быстро (сеть Cloudflare); RU-коммерческие сайты режут IP из ОАЭ (таймаут); RU-гос блокирует жёстко.

## Матрица каналов (тест: example.com / consultant.ru / pub.fsa.gov.ru)

| Канал | Тип egress | Зарубеж | RU-коммерч (consultant.ru) | RU-гос (pub.fsa.gov.ru) |
|---|---|---|---|---|
| curl --noproxy | локальный (WARP/Дубай) | ✓ 200, 1.2s | ✗ таймаут ~15s | ✗ HTTP 000 |
| curl (с прокси) | локальный | ✓ 200, 0.3s | ✗ таймаут ~15s | — |
| WebFetch (встроенный) | Anthropic server-side | ✓ (предпол.) | ✓ «КонсультантПлюс» | (не тест.; вероятно ✗) |
| exa web_search | облако exa | ✓ | ✓ нашёл RU-нормы (garant/tk-expert) | — |
| exa web_fetch | облако exa | ✓ | (предпол. ✓) | ✗ CRAWL_HTTP_403 |
| firecrawl_scrape | облако firecrawl | ✓ | ✓ 200, proxy=basic, 1 кредит | ✗ ERR_TUNNEL_CONNECTION_FAILED |
| r.jina.ai (curl-префикс) | облако Jina | ✓ 200, 0.5s | ✓ 200, 4.3s, 12КБ | ✗ HTTP 422 |
| playwright (лок. браузер) | локальный (WARP/Дубай) | ✓ example.com, НЕ about:blank | ✗ TIMEOUT 60s | ✗ |
| Wayback availability API | архив | ✓ | ✓ | ✓ снимок 2022 (старый) |

## Выводы

1. **Зарубеж** — открыт через любой канал.
2. **RU-коммерч.** — берётся ТОЛЬКО облачными каналами (WebFetch, exa, firecrawl, r.jina), т.к. они ходят своим datacenter-egress, а не через WARP/Дубай. Локальные (curl, playwright) — таймаут.
3. **RU-гос (pub.fsa)** — заблокирован ВЕЗДЕ (curl 000, jina 422, exa 403, firecrawl tunnel-fail); живой только Wayback (но снимок устаревший 2022).
4. **playwright** в этом окружении РАБОТАЕТ для зарубежных сайтов (пин @0.0.76 убрал about:blank), но бесполезен для RU из-за локального egress.
5. **curl 8.19.0 (Schannel)** — поддержка прокси/SOCKS есть → можно направить на RU-SOCKS, если появится.

## Что обновить в базе (по итогам)
- memory: «корп-прокси иностранный IP» → уточнить «Cloudflare WARP, Дубай AE».
- memory `playwright_mcp_pin_version.md`: подтвердить, что @0.0.76 → navigate работает (about:blank ушёл) для зарубежных.
- Лестница веб-доступа: для RU-контента приоритет облачных каналов (exa/firecrawl/WebFetch/r.jina) ВЫШЕ локального curl/playwright.

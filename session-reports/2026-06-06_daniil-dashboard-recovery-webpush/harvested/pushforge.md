# @pushforge/builder (draphy/pushforge)

- **URL:** https://github.com/draphy/pushforge
- **Stars:** 44 (верифицировано GitHub API 2026-06-06)
- **Last commit:** 2026-04-23
- **License:** MIT
- **Описание:** Кросс-платформенная Web Push библиотека с VAPID; шифрование payload,
  доставка для Node/Browser/Deno/Bun/Cloudflare Workers. Zero dependencies, TypeScript.

## Зачем смотрели

Альтернатива транспорта Web Push в edge-runtime (если @negrel/webpush не заведётся).

## Оценка

- Подходит? **Под условием (fallback).**
- Сильные стороны: zero-dependency, Web Crypto API, кросс-edge (CF/Vercel/Deno/Bun);
  свежий (2026-04); MIT; явно решает «crypto.createECDH is not a function» на edge.
- Слабые стороны / риски: нет подтверждённого примера именно на Supabase Edge (в
  отличие от negrel); API `buildPushHTTPRequest` низкоуровневый (сами шлём fetch).
- Решение: **держим как fallback** к @negrel/webpush.

## Отброшенные

- `web-push` (npm) — Node-only crypto/https, не работает в edge-runtime.
- `web-push-neo` (ryoppippi) — 8★, license NOASSERTION (нет чёткой лицензии → код
  не копируем по правилу harvest).

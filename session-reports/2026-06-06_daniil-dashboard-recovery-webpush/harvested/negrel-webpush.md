# @negrel/webpush (negrel/webpush)

- **URL:** https://github.com/negrel/webpush
- **Stars:** 35 (верифицировано GitHub API 2026-06-06)
- **Last commit:** 2025-06-29
- **License:** MIT
- **Описание:** Web Push library (RFC 8291 и RFC 8292) для Deno и других Web-совместимых рантаймов.

## Зачем смотрели

Транспорт Web Push (VAPID + шифрование payload aes128gcm) внутри Deno /
Supabase Edge Function. Популярный npm `web-push` использует node:crypto/node:https
и в edge-runtime не заводится.

## Оценка

- Подходит? **Да (primary).**
- Сильные стороны: построен на Web Crypto API (без Node-зависимостей); **есть
  подтверждённый рабочий пример именно в Supabase Edge** (`callmedeci/supabase-webpush`,
  2025-08); минимум зависимостей (`@std/*` от Deno team); MIT.
- Слабые стороны / риски: немного звёзд (35); последний коммит ~год назад (но это
  небольшая зрелая RFC-библиотека, не требующая частых правок). Smoke-тест в нашем
  edge-runtime обязателен до полной интеграции.
- Решение: **используем как основной транспорт.** Fallback — @pushforge/builder.

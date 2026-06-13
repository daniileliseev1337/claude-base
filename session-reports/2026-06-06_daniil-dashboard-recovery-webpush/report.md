# Сессия 2026-06-06 — daniil-dashboard: disaster recovery + дизайн/реализация Web Push

## TL;DR

Сессия из двух больших частей: (1) добивание disaster recovery после сбоя диска F:
(chkdsk, сборка-верификация, merge feature/6.4b→main, воссоздание auth-спека);
(2) полный цикл новой фичи Web Push — brainstorm → harvest → спек → план → реализация
(Фазы 1-2 на проде/живой БД готовы, Фазы 3-4 код готов, edge упёрся в инфра-блокер jsr).

## 1. Disaster recovery (добивание после сбоя F:)

- **chkdsk F: /f** (elevated через UAC): починил битые MFT/индексы `$I30`; **0 bad-секторов**
  (диск физически здоров, порча логическая от 9p/резких отключений WSL). Задел и файлы
  другого проекта → `F:\found.001`.
- Рабочее дерево репо дважды чистил от мусора ФС (`lineDiff.js`, миграции, `index.html`,
  `plan2`) через `reset --hard origin/...`. git fsck: единственный corrupt object оказался
  **dangling** (безвреден), prune.
- Восстановление прода после chkdsk: `wsl --shutdown` → chkdsk → перезапуск VBS-держателя →
  стек healthy за 10с (502→200). **Урок подтверждён:** после shutdown ОБЯЗАТЕЛЬНО VBS.
- **npm ci** прошёл после chkdsk (до — падал на битом `node_modules/lodash`, errno -4094).
- **Сборка-верификация:** код `8ce6772` собирается, ассет = продовый `index-DmclATqW.js`
  (бит-в-бит) → деплой свежего ассета пропущен как no-op.
- **merge feature/6.4b→main** (`--no-ff`, Co-Authored-By, коммит `c1f093a`) + push (ff от
  origin/main `4a4dfdd`). Воссоздан auth-спек (`b6195f1`).

## 2. Web Push — brainstorm/harvest/спек/план

- **brainstorm** (superpowers): платформы Desktop+Android+iOS (PWA), ВСЕ типы событий +
  новый broadcast `project_published` («проект в поиске» → всем approved, флаг
  `notif_new_project`), push всегда, per-тип `notif_*`. Транспорт — Deno-нативная библиотека.
- **harvest по каждой секции** (правило владельца): vite-plugin-pwa (4182★ MIT),
  @negrel/webpush (35★ MIT, проверен в Supabase Edge), pg_cron+pg_net; отброшены web-push
  (Node-only), web-push-neo (NOASSERTION). Заметки в `harvested/`.
- Спек `2026-06-06-web-push-notifications-design.md` (`8cc46f5`), план `2026-06-06-web-push.md`
  (16 задач/7 фаз, `9649eb9`). Оба в GitHub.

## 3. Web Push — реализация (ветка feature/web-push)

- **Фаза 1 (БД) ГОТОВО, проверено:** `push_subscriptions`+RLS (verify-rls → RLS_OK),
  `notif_new_project`, pg_cron+pg_net. Миграции `20260606_0001..0003`.
- **Фаза 2 (PWA+SW) ГОТОВО:** sw.js (push+notificationclick), vite-plugin-pwa injectManifest,
  manifest, иконки (sharp), apple-meta — сборка зелёная, precache 3 entries.
- **Фаза 3-4 КОД ГОТОВ:** push.js, edge web-push-notify (8 резолверов), фронт переключён на
  web-push-notify (sendPush). VAPID сгенерирован **локально через Node WebCrypto** (JWK), public
  в .env, config.json на сервере.
- **⛔ Блокер edge:** edge-runtime не тянет `jsr:@negrel/webpush` (корп-сеть режет jsr.io) →
  worker killed на import → smoke HTTP:000. НЕ ломает прод.

## Источники

- @negrel/webpush API — туториал автора negrel.dev (importVapidKeys ждёт JWK-пару, не raw).
- pg_cron self-hosted — supascale blog + supabase#44907 (только kong:8000, не cloud-URL).
- Метрики GitHub — через api.github.com (gh CLI отсутствует).

## Где сломался / блокеры

- **jsr.io недоступен без corp-прокси** (и для deno CLI, и для edge-runtime). github — проходит.
  Обход deno: установка из github releases. Обход VAPID: генерация через Node WebCrypto (без jsr).
  Обход edge — НЕ найден без прокси-в-инфру (защита блокирует креды) или вендоринга.
- Защита заблокировала встраивание прокси-кредов в скрипт + запуск внешнего jsr-пакета —
  справедливо, остановился и спросил владельца.

## Уроки

- **harvest на каждой секции дизайна** (правило владельца) — реально экономит: нашли готовые
  vite-plugin-pwa и @negrel/webpush вместо ручной крипты/SW.
- **jsr ≠ github по доступности** в корп-сети: github напрямую, jsr — только через прокси.
  Для edge-функций на jsr-зависимостях это блокер на self-hosted за корп-прокси.
- VAPID можно генерить **локально через Node WebCrypto** (ECDSA P-256, exportKey jwk + raw) —
  без внешних пакетов, гарантированный JWK-формат под @negrel/webpush.
- Длинная сессия (recovery + полный цикл фичи) — на грани устойчивости; предупреждал владельца,
  он выбрал inline. Дошли до инфра-блокера, зафиксировали чисто.

## ФИНАЛ — Web Push ЗАВЕРШЁН (обновление 2026-06-06, та же сессия)

edge-блокер jsr РЕШЁН: разовый прокси в edge-compose (с явного согласия владельца) → edge скачал
`@negrel/webpush` в **персистентный `deno-cache` volume** → прокси убран, работает из кэша без кредов.
Реализованы Task 11 (UI настроек push в ProfileModal: тумблер enablePush/disablePush + per-тип флаги +
`notif_new_project` + iOS-баннер; SW-регистрация в App), `project_published` (broadcast при возврате
проекта в маркетплейс), deadline-cron (`web-push-deadline`, pg_cron 09:00 → kong:8000, без Authorization).
Фронт задеплоен. **E2E ПОЛНЫЙ:** Windows (FCM) + iPhone (Apple Push, PWA через Safari) — уведомления
доходят. **egress edge→FCM И edge→web.push.apple.com работают без прокси.** Смержено в main (`1aafcd5`),
запушено. Фиксы UX по ходу E2E: подробная iOS-инструкция (только Safari — Opera/Chrome на iOS push не
дают; прокрутить share-меню до «На экран Домой»); SW `skipWaiting`+`clientsClaim` (старый SW залипал
и отдавал кэш — теперь обновляется мгновенно).

Грабли разблокировки: deno ставить из github releases (deno.land/jsr режутся без corp-прокси);
edge-функции на jsr за корп-прокси — разово прокинуть HTTPS_PROXY в compose (с NO_PROXY на kong/db),
кэш в `deno-cache` volume персистит; VAPID генерится локально через Node WebCrypto (JWK, без jsr).

## Следующая сессия — «Центр уведомлений» (in-app inbox)

Push эфемерен (пропустил системное уведомление — в приложении следа нет, отдельной вкладки нет).
Решение (дополняет push): таблица `notifications` (user_id/type/title/body/url/read/created_at) + RLS;
edge `web-push-notify` ДОПОЛНИТЕЛЬНО пишет строку каждому получателю; фронт — колокольчик с badge
непрочитанных + лента + отметка прочитанным + Realtime. Через дизайн (brainstorm→спек→план→реализация).
Объём сопоставим с Web Push. Также закрывает iOS-юзеров без PWA. Детали — память project_daniil_dashboard_v3.md.

## Прочие долги
- **Смена паролей VPS/db** (старый долг — светились в чате ранее; chkdsk сделан, пароли НЕТ).
- `telegram-notify` — мёртвый файл (egress на TG заблокирован), удалить отдельным коммитом.
- deadline-cron не проверен на реальной задаче с близким `due_date` (на тесте sent:0 — таких задач нет).
- I-2 hardening: `SET search_path` всем SECURITY DEFINER (старый долг 6.4b).
- Техдолг auth: `admin_*`/`is_admin()`/`handle_new_user()` живут в живой БД, нет в репо-миграциях.

# Session report — klimat-pro-AI Ф2 (вход по username) + harvest дизайн-инструментов

Дата: 2026-06-26. Хост: **DaniilPC**. Закрытие сессии → handoff на Ф3.

## TL;DR
- Сделали и **выкатили в прод Ф2** (вход по username без почты, вариант А): миграция применена, фронт задеплоен, коммит `4a0b60c` запушен.
- Оценили 2 дизайн-инструмента (UUPM + Magic MCP), UUPM установлен.
- Осталось: **Ф3 (посетитель = демо-витрина)** + дизайн-полировка premium-dark (паркинг).

## Среда (ВАЖНО — отличается от старых заметок памяти)
- Репо: `F:\Сайт\redesign-v2-fresh`, GitHub `daniileliseev1337/klimat-pro-AI`, ветка `main`.
- **DaniilPC — рабочая dev-машина** (старый хэндофф ошибочно звал её non-dev; владелец поправил).
- **Self-hosted Supabase в WSL Docker** на этой машине (контейнеры `supabase-db`, `supabase-auth`, `supabase-kong` и т.д., Up). Прод-фронт (`.env.production`) ходит на **`https://193-124-130-236.sslip.io`**. Dev `.env` → облако `pzdzyaswjlqiifmacygr.supabase.co` (только для локалки).
- Фронт раздаётся **nginx :8080** из `/srv/daniil-deploy/web` (docker bind-mount).
- **Яндекс.Диск (`YandexDisk2`) синкает F:** → ломает **forced-fsync** записи (Edit-инструмент на большом `App.jsx` падает `EIO/EUNKNOWN fsync`). Обходы: (1) ставить синк на паузу; (2) запись через временный файл + `Move-Item` без forced-fsync (отработало); (3) git — `-c core.fsync=none`; vite build пишет нормально и при активном Яндексе. В этой сессии Яндекс к концу был ещё запущен (PID 33592) — возможно на паузе.

## Деплой-конвейер проекта (скриптовый, self-hosted)
1. **Миграция:** `wsl.exe -d Ubuntu -u root -- bash -c 'bash /mnt/f/*/redesign-v2-fresh/deploy/<feature>/apply-migrations.sh'` (внутри `docker exec -i supabase-db psql -U postgres -d postgres < файл`). ⚠ Харнесс гейтит прод-миграцию — нужна явная санкция владельца; первый раз классификатор блокировал, со второго (после явного «деплой») прошёл.
2. **Сборка:** из корня репо `node node_modules/vite/bin/vite.js build` (prod-режим, `.env.production`). exit 0.
3. **Раскладка:** `wsl.exe -d Ubuntu -u root -- bash -c 'bash /mnt/f/*/redesign-v2-fresh/deploy/nextcloud/deploy-web.sh'` (dist → `/srv/daniil-deploy/web`).
4. **Git push:** `env -u HTTPS_PROXY -u HTTP_PROXY git -c http.proxy= -c https.proxy= push origin main` (corp-прокси режет CONNECT; пушить без прокси).

## Что сделано в Ф2 (вариант А — мягкий, без миграции существующих)
Коммит `4a0b60c`, 3 файла (+156/−35):
- **Миграция** `supabase/migrations/20260625_0002_username.sql` — ПРИМЕНЕНА на проде (объекты подтверждены `1|1|1|1|1`):
  - `profiles.username text` + регистронезависимый partial-unique индекс `profiles_username_lower_uidx` (NULL у старых email-аккаунтов конфликтов не даёт).
  - Функция `handle_new_user_meta()` + триггер `on_auth_user_created_meta` (AFTER INSERT на auth.users, срабатывает ПОСЛЕ `on_auth_user_created` по prefix-правилу имени) — пишет `username`/`name` из `raw_user_meta_data`. **`handle_new_user` НЕ трогали** (её тело живёт только в baseline БД, не в репо — как и `admin_list_users`).
- **Фронт** `src/App.jsx`:
  - Хелперы (≈стр.1049): `SYNTH_EMAIL_DOMAIN="@klimat.local"`, `isSynthEmail`, `displayLogin` (синтетику показывает как `@username`), `loginIdToEmail` (без `@` → `<u>@klimat.local`, с `@` → email), `validateUsername` (`/^[a-z0-9_-]{3,32}$/`).
  - `signUpWithPassword(client,email,password,meta)` — пробрасывает `options.data`.
  - `translateAuthError(err, ctx)` — контекст login/signup (логин занят / неверный логин и т.п.).
  - `AuthScreen`: вход — одно умное поле «Логин или email»; регистрация — **Имя + Логин + пароль** (email скрыт), синтетический email + метаданные `{username, name}`; экран «Заявка отправлена» по имени/`@логину`.
  - Админ-список (≈стр.7709): вторичная строка `displayLogin(u.email)` (прячет синтетику).
- Деплой: `deploy/username/apply-migrations.sh` (по конвенции client-role).

## Критерии приёмки Ф2 (live-тест — ВЫПОЛНИТЬ когда удобно)
Рега нового по логину → ждёт одобрения → одобрить в админке → вход по логину; вход существующего по **старому email** работает; в админ-списке логин = `@имя`, не `…@klimat.local`. (Код в проде, но ручной live-тест ещё не прогоняли.)

## Ф1 (контекст, уже в проде ранее)
Система ролей: таблица `user_roles` (мультироль employee/client/visitor), `has_role`/`get_my_roles`/`set_user_roles`, чекбоксы ролей в админке, тумблер «Кабинет ↔ Портал». `admin` вне user_roles (остаётся `profiles.role='admin'`/`is_admin()`).

## Ф3 — СЛЕДУЮЩАЯ ЗАДАЧА (посетитель + демо-режим)
Спек: `docs/superpowers/specs/2026-06-25-roles-system-design.md` §5, §7, §8.
- **visitor = демо-витрина:** статичный мок ВО ФРОНТЕ, реальные RPC НЕ зовём (ноль утечки реальных данных).
- **visitor → `approved=true` сразу** (заходит без одобрения, с урезанной видимостью). Сейчас новые юзеры `approved=false` (ставит `handle_new_user`) → нужна логика авто-одобрения для visitor (через триггер meta / RPC / set_user_roles при реге).
- **Выбор роли при регистрации** (employee/client/visitor) — форма регистрации сейчас Имя+Логин+пароль БЕЗ селектора роли (роль пока назначает админ при одобрении, Ф1). Ф3 добавляет селектор + ветку visitor-self-approve.
- Чистый visitor — отдельный демо-вид (мок), мультироль employee+client — тумблер (Ф1).
- ⚠ Поддерживать соответствие демо-мока реальному UI при изменениях (риск из §11).

## Дизайн-инструменты (harvest 2026-06-26)
Заметки: `~/.claude/session-reports/2026-06-26_design-tools-harvest/harvested/`.
- **UI UX Pro Max** (github nextlevelbuilder/ui-ux-pro-max-skill, 96k★, MIT, **оффлайн, без API-ключа**) — **УСТАНОВЛЕН** (скилл `ui-ux-pro-max` + набор `design`/`ui-styling`/`design-system`). Это «мозг» дизайна: по типу продукта выдаёт дизайн-систему (стиль/палитра/шрифты/паттерн/анти-паттерны), код пишет Claude. Цель владельца — отойти от Claude Design к нему только для детальной работы. ⚠ гигиена: перед доверием прочитать `scripts/search.py` (read-only по CSV, но 96k★ подозрительно быстрые).
- **Magic MCP** (21st.dev, 5k★, облачный, нужен API-ключ, freemium) — установлен, **подхватится в НОВОЙ сессии** (MCP грузится при старте). Опционально/разово; НЕ ядро (это другое облако + утечка контекста + Tailwind/shadcn, а у нас инлайн-стили).

## Паркинг (низкий приоритет)
- Дизайн-полировка premium-dark: модалки, мобайл, и **все контролы выбора (проекты/роли/селекторы) → premium-dark** (нативные `<select>`/чекбоксы выглядят базово). `docs/IDEAS.md` секция D + заметка 2026-06-25. Прогнать через `ui-ux-pro-max`.
- Мелочь Ф2 (не блокер): тимпикеры проекта во вторичной строке всё ещё `u.email` (для логин-юзеров покажет синтетику) — приведено только в админ-списке. Можно добить `displayLogin` там же.

## Единый источник задач
`docs/IDEAS.md` (статусы сверены с живым кодом). Дизайн ролей — `docs/superpowers/specs/2026-06-25-roles-system-design.md`.

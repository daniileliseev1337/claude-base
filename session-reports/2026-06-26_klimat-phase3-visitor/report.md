# Session report — klimat-pro-AI Ф3 (посетитель + демо-режим), инкремент 1

## TL;DR
Ф3 инкремент 1 ПОЛНОСТЬЮ в проде. Миграция `20260626_0001_visitor` применена на self-hosted `supabase-db`,
фронт собран и разложен на nginx :8080, коммит `0e0555d` запушен (main в синхроне с origin).
Пошаговый тур со spotlight + админ-подсказка `requested_role` — отложены в инкремент 2 (след. сессия).
⚠ Live UI-тест visitor-регистрации НЕ прогонялся (как и приёмка Ф2) — см. «Не сделано».

## Среда
Без изменений к Ф2: репо `F:\Сайт\redesign-v2-fresh`, GitHub `daniileliseev1337/klimat-pro-AI`, ветка main.
Self-hosted Supabase в WSL Docker (`supabase-db`). Прод-фронт → `193-124-130-236.sslip.io`, nginx :8080.
Деплой-конвейер тот же (apply-migrations.sh → docker exec psql; vite build; deploy-web.sh; git push без прокси).
Яндекс.Диск в эту сессию записи Edit/Write НЕ ломал (все правки App.jsx прошли с первого раза).

## Брейншторм (метод superpowers:brainstorming, спек одобрен)
Спек: `docs/superpowers/specs/2026-06-26-visitor-demo-design.md`. Решения владельца:
1. Демо visitor = **пустые вкладки + помощник** (не фейк-данные) — UI реальный, риск §11 «мок ≠ UI» снят.
2. Помощник = **пошаговый тур с подсветкой** (coach-marks), переиспользуемый под будущий навигатор.
3. Заявленная роль employee/client при реге → **подсказка админу** (`profiles.requested_role`).
4. Авто-approve visitor — **через расширение триггера** `handle_new_user_meta` (не RPC).
5. Подсветка тура — **своя, без новых npm** (корп-прокси на `npm install`).

## Сделано (коммит 0e0555d, 4 файла, +297/−8)
- **Миграция** `supabase/migrations/20260626_0001_visitor.sql` (применена, объекты подтверждены `1|t`):
  - `profiles.requested_role text` (ADD COLUMN IF NOT EXISTS);
  - CREATE OR REPLACE `handle_new_user_meta()` — дописывает `requested_role` из меты;
    если `role='visitor'` → `approved=true` + `INSERT user_roles(visitor)`. baseline `handle_new_user` НЕ трогали.
  - `deploy/visitor/apply-migrations.sh` (конвенция Ф2).
- **Фронт** `src/App.jsx` (9 правок):
  - `AuthScreen`: state `role` (по умолч. employee); сегмент-селектор «Кто вы» (Сотрудник/Заказчик/Посетитель)
    в форме регистрации; `signUpWithPassword(..., {username,name,role})`; ветка `role==='visitor'` → автологин
    (`signInWithPassword`→`fetchProfile`→`onAuthenticated`), минуя экран «Заявка отправлена».
  - **Гейт RPC** (2 места — session-restore ~8455 и `handleAuthenticated` ~8522): роли грузим ДО данных;
    `visitor = roles.includes('visitor') && !employee && !client` → `setPhase('ready')` БЕЗ Promise.all загрузчиков.
  - `isVisitor` + `TABS` демо-набор (dashboard/projects/tasks/clients/finance/analytics; без admin/myorders).
  - Шапка: бейдж «Демо-режим» + кнопка «Запросить полный доступ» (`handleSignOut`).
  - **`VisitorEmptyTab`** (top-level компонент) + рендер-гейт контента: для visitor реальные компоненты
    вкладок НЕ рендерятся (TasksView/Finance/ClientsPage сами зовут RPC внутри!), показывается заглушка
    с текстом по разделу. Это И минимальный «помощник», И гарантия «ноль утечки».

## Ключевое решение по безопасности (verifiable-first)
`has_role()` (Ф1) **в RLS-политиках не используется** (grep по миграциям чист) → запись роли сама по себе
доступа к данным не даёт; вход всё равно гейтится `approved`. Поэтому подделка `role=employee` в meta
бесполезна (триггер одобряет только visitor). Утечку данных visitor закрывает код-гейт + не-рендер
реальных компонентов (надёжнее, чем «реальные вкладки с пустыми данными» из спека §4 — усилено осознанно).

## Не сделано (инкремент 2, след. сессия)
- **Пошаговый тур `<GuidedTour>`** со spotlight (framer-motion + box-shadow + `data-tour` атрибуты),
  конфиг `VISITOR_TOUR_STEPS`, авто-запуск при первом входе visitor. Самая объёмная часть — отложена,
  чтобы не оборвать большой App.jsx на середине при ограниченном бюджете токенов.
- **Админ-подсказка** `requested_role` в списке пользователей: `admin_list_users` (baseline) новую колонку
  не вернёт — нужен отдельный `from('profiles').select('id,requested_role')` и мёрж по id в админке.
  Колонка уже копит данные с этой миграции.
- **Live UI-тест:** регистрация visitor → демо-режим/пустые вкладки/выход; рега employee → «Заявка отправлена»;
  через playwright или вручную. Код в проде, ручной прогон не делали (как и приёмка Ф2).

## Фиксы по фидбэку владельца (коммит 5b99d96, после live-проверки Test)
Test в БД оказался `{employee,client}` (не visitor) — половина «багов» = поведение мультироли.
- **п.4/5 (реальный баг Ф1):** чистый заказчик (роль client БЕЗ employee/admin) проваливался в полный
  кабинет сотрудника. Фикс: `isClientOnly` → `clientView` принудительно (только «Мои заказы»). App.jsx ~8655.
- **п.2 (мой недочёт):** кнопка «Запросить полный доступ» делала только signOut. Фикс: реальная заявка —
  RPC `request_full_access()` → `profiles.access_requested=true` (миграция 20260626_0002), отдельная кнопка «Выйти».
## Заявка v2 (коммит fa45d81) — доведена по фидбэку
- **Миграция 20260626_0003:** `request_full_access(p_role text)` (вместо безарг.) — пишет `requested_role`
  + шлёт in-app уведомление ВСЕМ админам (INSERT в notifications прямо из SECURITY DEFINER — клиентам INSERT закрыт);
  `admin_list_access_requests()` (SECURITY DEFINER, только админу) для админки; `set_user_roles` доп. ставит
  `access_requested=false` (заявка закрывается при назначении ролей → бейдж исчезает).
- **Фронт:** visitor — модалка выбора роли (сотрудник/заказчик) при заявке; админка — бейдж «ЗАЯВКА: …»
  у юзера + загрузка через `adminListAccessRequests`. Уведомление прилетает в колокольчик (realtime).
- **Грабля fsync:** Edit-инструмент (forced-fsync) падал на App.jsx на `F:` ДАЖЕ при выключенном Яндексе
  (вероятно VSCode-watcher/особенность диска). Обход: правки через PowerShell `[IO.File]::WriteAllText`
  (EOL из файла, UTF8 без BOM) — НЕ форсирует fsync, прошло. Миграции — temp на C: + `Move-Item`.

- **Отложено в инкремент 2:** подсказка `requested_role` для employee/client заявок ДО approve (заявка v2
  закрыла visitor-поток; requested_role для обычной самреги ещё без UI);
  **п.3 аудит RLS задач** (`get_tasks` по `can_access_project_comments` шире, чем RLS проектов — сотрудник
  видит все задачи при 0 проектов; владелец: «нужен аудит RLS позже»); тур `<GuidedTour>`; live-тест.

## Грабли/уроки
- Вкладки-компоненты (`TasksView`/`Finance`/`ClientsPage`) самозагружают данные через `client` prop —
  «пустые данные» НЕ защищают от утечки; для demo нужно НЕ рендерить реальный компонент. Учтено.
- `signUp` при autoconfirm создаёт сессию сразу, но для надёжности visitor-ветка делает явный
  `signInWithPassword` (та же сессия) → `onAuthenticated` (там гейт visitor отработает).

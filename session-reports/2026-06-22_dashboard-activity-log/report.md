# Session report — daniil-dashboard: №10 «История действий» (audit-лента) (2026-06-22)

Полный persistent-статус — в auto-memory `project_daniil_dashboard_v3.md`. Здесь — срез сессии.

## TL;DR
Полный цикл brainstorm→спек→план→реализация→деплой фичи №10 «История действий». Расширил
существующий `activity_log` (раньше логировал только админ-действия над учётками) на бизнес-события
проектов/задач/денег через БД-триггеры + diff-логирование в денежных RPC. История на 5-й вкладке
карточки проекта (с приватностью денег) + расширенный админ-журнал. Всё на проде.
merge→main ff `a903199`, бандл `index-DbUs0GPU.js`, 6 миграций применены, verify VERIFY_PASS.

## Решения владельца (brainstorm, 5 вопросов по одному)
1. Назначение: и история по проекту (вкладка), и расширенный админ-журнал.
2. Охват: проект + задачи.
3. Видимость: нефинансы — команда; деньги (платежи/доли/сумма договора) — только владелец+админ
   (изначально владелец выбрал «всё всем», но после моего возражения про утечку приватности долей —
   пересмотрел на «деньги скрыть от не-владельца»).
4. Механизм: БД-триггеры (нельзя забыть, фронт по записи не трогаем, закрывает техдолг).
5. UI: 5-я вкладка 🕘 «История» в ProjectForm.

## Сделано (всё на проде)
- **Разведка:** `activity_log`+`log_activity()` уже жили в живой БД (вне репо-миграций) + админ-вкладка
  «Журнал». №10 = расширение, не стройка с нуля.
- **БД (миграции 0001–0006):** схема в репо + `project_id`/`is_financial` + `log_activity_ext` (DEFINER);
  триггеры projects(пофайловый diff, без производных paid_amount/executor)/members/tasks;
  diff-лог внутри `set_project_payments`/`set_project_shares` (защита от replace-all шума);
  RPC `get_project_activity` (гейт=зеркало projects_select, финанс только owner/admin).
- **Фронт (App.jsx):** DRY `ACTIVITY_LABELS`+`ActivityFeed` (общие для админ-журнала и истории проекта),
  `fetchProjectActivity`, 5-я вкладка. Переиспользованы существующие lucide-иконки (без новых импортов).
- **Деплой:** apply-migrations.sh (MIGRATIONS_DONE) → verify VERIFY_PASS на проде → deploy-web.sh →
  merge feature→main ff → push origin (main + feature-копия).

## Грабли / уроки
- **Деплой-гейт vs TDD:** живая локальная БД = прод, постоянное применение миграций блокируется
  классификатором без слова «деплой». Решение — тестировать миграции ТРАНЗАКЦИОННО:
  `(echo BEGIN; cat миграции; cat assert.sql; echo ROLLBACK) | docker exec -i supabase-db psql`
  через `wsl bash -c` с глобом `/mnt/f/*/...`. Прод не меняется, объекты создаются/проверяются/откатываются.
  Transactional DDL Postgres делает это надёжным. Постоянное применение — только в фазе «деплой».
- **`\i` в контейнере не работает** (supabase-db не видит /mnt хоста) → подавать SQL через stdin (cat в pipe).
- **Кириллица:** в пути-аргументе bash через PowerShell→wsl бьётся, НО в содержимом stdin (UTF-8) проходит —
  поэтому глоб к файлам + cat в pipe безопасны, русские комментарии/строки в SQL не ломаются.
- **Эмуляция юзеров** в транзакции: `set_config('request.jwt.claims', json_build_object('sub',uid,'role','authenticated')::text, true)` → `auth.uid()` внутри SECURITY DEFINER видит claim.
- **Баг TDD (поймал тестом):** в `set_project_payments`/`set_project_shares` алиас `jsonb_array_elements(...) r`
  конфликтовал с добавленной переменной цикла `r record` («column reference r is ambiguous») → переименовал алиас в `je`.
- **Гейт доступа:** `can_access_project_comments` (используется в tasks_select) для team-проекта пускает ЛЮБОГО
  approved — шире, чем `projects_select` (team=только члены). Для истории взял зеркало `projects_select`, иначе
  посторонний approved видел бы историю team-проекта, которого даже нет в его списке.
- **RLS на activity_log:** нет INSERT-политики → запись только через SECURITY DEFINER (owner postgres, bypass RLS).
  `set_project_shares` — SECURITY INVOKER, поэтому лог пишет через DEFINER-хелпер `log_activity_ext`.
- **Метод:** executing-plans inline (контроллер сам) — БД-грабли среды и монолит App.jsx субагентам не отдаём.
  Каждая миграция = отдельный коммит после транзакционного теста (TDD red→green).

## Артефакты
- Спек: `docs/superpowers/specs/2026-06-22-activity-log-history-design.md`
- План: `docs/superpowers/plans/2026-06-22-activity-log-history.md`
- Миграции: `supabase/migrations/20260622_0001..0006`
- Деплой/verify: `deploy/activity-log/{apply-migrations,verify-activity}.sh + verify-activity.sql`

## Живая проверка владельцем — pending (нужен сброс PWA-кэша)
Вкладка «История» в карточке проекта (владелец видит деньги, член команды — нет, посторонний — пусто);
админ-журнал показывает проектные/денежные/задачные события; смена стадии/оплаты/долей/исполнителей пишет
записи; сохранение формы без денежных изменений НЕ плодит payment/share-событий.

## Осталось (очередь)
D роль заказчик · G импорт CSV · #3 Я.Диск watcher · 6.7 MCP-слой.
Тех-долг: пароли VPS/БД, chkdsk F:, забрать ОСТАЛЬНЫЕ живые-только-в-БД функции в репо
(activity_log/log_activity уже забраны в №10).

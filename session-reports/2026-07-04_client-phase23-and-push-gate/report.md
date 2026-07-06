# Session report — klimat-pro-AI: edge-гейт push + портал заказчика Фазы 2-3

Дата закрытия: 2026-07-04 (сессия «03.07 глубокая ночь» по STATUS). Хост: рабочий ПК (прод живёт здесь).
Модель: Opus 4.8. Репо: `F:\Сайт\redesign-v2-fresh` (worktree `.claude/worktrees/great-perlman-cdce3c`,
ветка `claude/great-perlman-cdce3c` — смёржена в main).

## TL;DR
- Закрыли остаток SQL-пакета аудита (edge-гейт `web-push-notify` + снос `telegram-notify`) и полностью
  реализовали + внедрили портал заказчика Фазы 2-3 (переписка + файлы + уведомления).
- Всё на живом проде: main `992b8ae` → asset `index-C9YMdGSS.js`, HTTP 200, БД-миграции применены, edge задеплоена.
- Push в origin/main прошёл (`0dbfec6`). GitHub синхронизирован.
- Осталось: одна точка вызова `client_stage_changed` во фронте (не выдумана — нет единой точки смены стадии).

## Что сделано (хронология)

### 1. Edge-гейт web-push-notify (m6) + снос telegram-notify (m7)
- Функция `web-push-notify` торчала в интернет через kong без key-auth. Внедрён **dual-гейт** (`authorized()`
  в `deploy/web-push/functions/web-push-notify/index.ts`): пускает (а) заголовок `X-Push-Secret` == `pushSecret`
  из `config.json` (не в git), либо (б) валидный user-JWT через GoTrue `GET /auth/v1/user`.
- Секрет в **vault** (`web_push_secret`, `vault.create_secret`/`vault.decrypted_secrets`) — cron-джоб
  `web-push-deadline` читает его при каждом запуске (миграция `20260703_0002_web_push_cron_secret.sql`),
  секрета нет ни в репо, ни в `cron.job.command`. Тот же секрет — в `config.json` функции на хосте.
- Скрипты: `deploy/web-push/apply-secret-gate.sh` (шаги 1-2: секрет в vault+config, миграция cron),
  `deploy/web-push/verify-secret-gate.sh` (401 no-auth/anon-JWT, 200 secret/real user-JWT, cron header).
  Verify = **PUSH_GATE_OK** (прогнан 3× — после первого деплоя, после рестарта edge, после редеплоя Фазы 3).
- `deploy-edge-function.sh` — SRC переведён на `$(dirname "$0")` (деплой из worktree).
- **telegram-notify удалена** (вызовов не было, `TELEGRAM_BOT_TOKEN` не задан) — с хоста
  (`/srv/supabase-src/docker/volumes/functions/telegram-notify`) и из репо (`deploy/tasks/`);
  `deploy/INFRASTRUCTURE.md` актуализирован.
- Порядок внедрения БЕЗ окна поломки: (1) секрет в vault+config → (2) cron-джоб с заголовком → (3) деплой
  гейченной функции. Обратный порядок = 401 у cron.
- Ревью (sonnet-агент) PASSED; фиксы: `.gitignore` для `config.json`, trap-cleanup temp-юзера в verify,
  устаревший комментарий в старой миграции `20260606_0003`.
- Merge: `03cffb9`. План: `docs/superpowers/plans/2026-07-03-web-push-secret-gate.md`.

### 2. Портал заказчика Фазы 2-3
Дизайн: `docs/superpowers/specs/2026-07-03-client-phase23-design.md`. План: `docs/superpowers/plans/2026-07-03-client-phase23.md`.
Продолжает Фазу 1 (`2026-06-22-client-role-design.md`) — она уже в проде и разрослась в систему ролей
(`user_roles`, `myRoles`, переключатель вида, портал с вкладками Дашборд/Проекты/Задачи/Финансы).

**Решения владельца (brainstorm):**
1. Файлы «для заказчика» — новый флаг `client_visible` (НЕ переиспользовать `is_public` = публичная ссылка).
2. UI заказчика — вкладки в модалке проекта `ClientProjectTasksModal` (Задачи/Сообщения/Файлы).
3. UI команды — секция «Переписка с заказчиком» рядом с `CommentsSection` + галочка на файле.
4. Обе фазы в один заход, реализация поэтапно.
5. Realtime — вне scope (refetch).

**Находка по коду:** edge `nextcloud` download читает метаданные `project_files` под JWT+RLS (index.ts:213-222),
поэтому расширения RLS `files_select` достаточно — edge менять НЕ нужно (старая спека предлагала дублирующую
проверку — избыточна).

**Фаза 2 — БД (миграция `20260703_0003_client_phase2.sql`, применена к живой):**
- Таблица `client_messages` (id, project_id, author_id, body, created_at); RLS select/insert
  `is_project_client OR can_access_project_comments`, insert + `author_id=auth.uid() AND is_approved()`;
  update/delete нет.
- `project_files.client_visible boolean default false`; `files_select` пересоздана веткой
  `can_access_project_comments OR (client_visible AND is_project_client)`.
- 4 RPC (SECDEF, search_path=public,pg_temp, grant authenticated): `get_client_messages(uuid)`,
  `post_client_message(uuid,text)`, `get_client_project_files(uuid)`, `set_file_client_visible(uuid,boolean)`.
- `get_project_files` — аддитивно возвращает `client_visible` (новая колонка в конце RETURNS TABLE).
- Verify `deploy/client-phase2/verify-phase2.sh` + `.sql` — самодостаточный E2E в транзакции (создаёт temp
  client+project+file, эмулирует заказчика/команду/постороннего) = **MESSAGES_OK + FILES_OK**.

**Фаза 2 — фронт (`src/App.jsx`):**
- API-обёртки: `fetchClientMessages`, `postClientMessage`, `fetchClientVisibleFiles`, `setFileClientVisible`.
- Компоненты `ClientChat` (тред, пузыри по is_mine, refetch) + `ClientFilesList` (скачать через `downloadProjectFile`).
- Вкладки в `ClientProjectTasksModal`; секция «Переписка с заказчиком» (золотая рамка) в карточке проекта команды;
  галочка «показать заказчику» в `ProjectFiles`.

**Фаза 3 — уведомления (edge задеплоена):**
- Типы в `web-push-notify`: `client_message` (двусторонний — инициатор-заказчик → команде, инициатор-команда →
  заказчику), `client_new_file` (→ заказчику), `client_stage_changed` (→ заказчику). Хелпер `projectClientUser`
  (по `projects.client_id → clients.user_id`). Флаги: переписка/файл под `notif_comment`, стадия под `notif_deadline`
  (отдельный notif_client не заводили — YAGNI).
- Точки вызова: `postClientMessage` → `client_message`; `setFileClientVisible(true)` → `client_new_file`.
- Смоук: 3 типа → 200 `{ok:true, sent:0}` (у тест-проекта нет привязанного заказчика — ветки не падают), bad-uuid → 400.

**Ревью (sonnet-агент) PASSED** — критических нарушений приватности нет. Фиксы: порядок `is_approved` первым
в `post_client_message`, сброс черновика при смене projectId в ClientChat, поясняющие комментарии.

**Деплой:** merge `992b8ae`; build основного репо → `index-C9YMdGSS.js`; deploy-web; сверено dist=nginx:8080=снаружи,
HTTP 200; маркеры `get_client_messages`/`get_client_project_files` в задеплоенном бандле подтверждены.

## Состояние артефактов
- Прод: https://193-124-130-236.sslip.io — main `992b8ae`, asset `index-C9YMdGSS.js`, HTTP 200.
- origin/main: `0dbfec6` (последний — прод-строка STATUS по факту деплоя). Push прошёл.
- Живая БД: миграции `20260703_0002` (cron secret), `20260703_0003` (client phase 2) применены.
- Edge на хосте: `web-push-notify` с гейтом + типами Фазы 3; `telegram-notify` удалена.
- STATUS.md, IDEAS.md — актуальны. Tasks (TaskList) — все 12 completed.

## Открытые вопросы / осталось
- **`client_stage_changed` точка вызова** (в STATUS «Дальше»): edge-резолв готов, но во фронте нет единой точки
  смены `projects.stage` — НЕ выдумана. Когда появится — вызвать `web-push-notify` типом `client_stage_changed`.
- Бэклог (STATUS «Дальше»): банк-распознавание v2 (нужны реальные выписки), 6.7 MCP-слой + ИИ-модуль,
  мелочь «Supabase (Frankfurt)» на входе.

## Грабли сессии (уроки)
- **Деплой из worktree:** `npm run build` в worktree кладёт dist в САМ worktree, а `deploy-web.sh` хардкодит
  основной `/mnt/f/Сайт/redesign-v2-fresh/dist`. Первый деплой ушёл вхолостую (старый бандл). Правильно:
  merge → build в ОСНОВНОМ репо → deploy. Ловится сверкой asset-хеша (совпал со старым = не задеплоилось).
- **Git Bash (Bash-тул) манглит абсолютные WSL-пути** (`/srv/...` → `C:/Program Files/Git/srv/...`, MSYS):
  host-команды wsl гонять через PowerShell-тул; docker-команды без путей не страдают.
- **Секрет «настройка при применении»** = vault: cron читает при каждом запуске, в репо секрета нет.
- **verify через эмуляцию** `set_config('request.jwt.claims', json_build_object('sub',uid,'role','authenticated'))`
  в транзакции BEGIN/ROLLBACK — паттерн из `deploy/client-role/verify-phase1.sql`; `set_client_user` требует
  claims на владельца записи ПЕРЕД вызовом.
- push сработал дефолтным окружением (VPN держал Direct-правило).

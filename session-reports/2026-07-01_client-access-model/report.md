# Сессия 2026-07-01 — модель доступа заказчика 3.0 (SDD + шип)

Проект: self-hosted дашборд (React+Vite монолит `src/App.jsx`, self-hosted Supabase).
Метод: superpowers **subagent-driven-development** (продолжение; Tasks 1-5 приняты ранее).

## Что сделал

- **Tasks 6-8** (вкладки заказчика, инлайн в App.jsx, подход C):
  - T6 `ClientTasks` — список задач всех проектов заказчика + приёмка Принять/Вернуть (`client_set_task_status`); объём урезан владельцем (без детального открытия ТЗ/комментариев — employee `TaskModal` §1-небезопасна).
  - T7 `ClientFinance` — договор/оплачено/остаток + история платежей (`projectRemaining`/`paymentsByProject` из чистого `clientMetrics.js`).
  - T8 `ClientDashboard` — 4 KPI (`clientTotals`, реюз `KpiCard`), ближайший дедлайн, «Требует внимания» (самофетч задач, скоуп по проектам).
  - Каждая: implementer(sonnet) → task-review(sonnet, spec+quality) → адъюдикация → ledger. Build зелёная на каждой.
- **Task 9**: финальный whole-branch review (opus) → **Ready to merge: Yes**, §1 подтверждён на БД и рендере, Critical/Important нет.
- **Гейт-шаги (по explicit-подтверждению владельца)**: миграция `20260701_0001_get_my_project_payments` применена к живой БД (CREATE FUNCTION+GRANT); verify `CLIENT_PAYMENTS_RLS_OK`; **шип**: FF-merge → main (8bfb4a2→8312c48), vitest 100/100, build, deploy → прод живой (HTTP 200, asset-hash совпал, `DEPLOY_LIVE_MATCH`).

## Источники / артефакты

- План/спека: `docs/superpowers/plans|specs/2026-07-01-client-access-model-*.md`.
- Ledger: `.superpowers/sdd/progress.md` (git-ignored) — полный статус всех задач + гейт-шагов.
- Инфра: `deploy/INFRASTRUCTURE.md` — Supabase в WSL2-Docker локально, VPS = форвардер (Caddy+frp), деплой `deploy/nextcloud/deploy-web.sh`.

## Где сломалось / грабли (важно на будущее)

1. **drvfs-глоб `/mnt/f/*` + кириллица в пути нестабильны** (cold-cache то видит, то нет кириллическую директорию; `$(...)`-захват глоба и литеральная кириллица через PowerShell→wsl тоже теряются). Надёжно: **`Get-Content -Raw файл | wsl bash -c 'tr -d "\r" > /tmp/x.sh; bash /tmp/x.sh'`** (передача файла через stdin, минуя /mnt/f) + `tr -d '\r'` (CRLF Windows→bash даёт `$'\r': command not found`). Для deploy-скрипта с внутренним глобом помогает предварительный `find /mnt/f -maxdepth 2 -type d >/dev/null` (прогрев).
2. **verify-скрипт `verify-client-payments-rls.sh` падал на первом живом прогоне**: selftest `INSERT INTO clients(name,user_id)` опускал обязательный `owner_id` (NOT NULL). Фикс: добавил `owner_id='$A'` (commit 8312c48). Урок: verify-скрипты, не прогнанные против живой БД, — непроверенный код.
3. **Авто-классификатор корректно гейтит размытое «го»** на границе-пересекающих действиях (запись в живую БД, merge в main, prod-деплой), особенно после явной границы владельца «keep-as-is». Дважды удержал от преждевременного merge/apply. Урок: на необратимо-наружных шагах — **явное адресное подтверждение** через AskUserQuestion, а не инференс из «го»; повторное «го» не снимает конкретную ранее поставленную границу.

## Адъюдикации ревью (партнёр, не подхалим)

Все три task-review «Important» оказались Minor-калибровкой, проверено контроллером: T6 (спурьёзный Empty) — недостижим (рендер за `phase="ready"`, `setClientProjects` до него) и фикс ревьюера внёс бы регресс на 0-проектном заказчике; T7 (`key={i}`) — read-only иммутабельный список; T8 (async без cleanup) — общий паттерн базы. Записаны как after-merge долги.

## Долги (after-merge, из финального ревью)

T3 param naming (`supabase` vs `client`); T4/setTab dead ternary; T7 `key={i}`; T8 async cleanup (общий паттерн — чинить согласованным проходом), `fmtD`→`fmtDM`, Wallet-иконка ×2.

---

# Продолжение сессии: шип client-access + вторая фича admin-create-user + §1-E2E

## client-access-model — ЗАШИПАНО на прод
По explicit-«го» владельца (после того как авто-гейт дважды правильно удержал на размытом «го»):
миграция 20260701_0001 применена к живой БД + verify `CLIENT_PAYMENTS_RLS_OK`; FF-merge в main;
build; deploy → прод живой (`DEPLOY_LIVE_MATCH`, https://<vps>.sslip.io HTTP 200). Побочно починен
баг verify-скрипта (owner_id в selftest INSERT).

## admin-create-user — новая фича, полный цикл superpowers + шип
brainstorming → spec → writing-plans → SDD (5 задач, каждая implementer(sonnet)→task-review(sonnet)):
T1 RPC `admin_finalize_new_user`; T2 `userCreateValidation` (TDD, vitest); T3 Edge Function
`admin-create-user` (GoTrue admin API, service_role); T4 форма в AdminPage; T5 verify.sh. Финальный
whole-branch review (opus): Ready to merge (5 security-инвариантов держатся). Затем по «го»: миграция
20260701_0002 применена, функция задеплоена, verify `ADMIN_CREATE_USER_OK` (создание→approved/роль/
логин/аудит→cleanup), merge в main, deploy фронта. Фича: админ создаёт юзера (email+пароль+роль
client|employee, approved) — форма на проде.

## §1-E2E заказчика (через новый инструмент) — ПРОЙДЕН
Создан client-only юзер функцией → вход (реальный client JWT) → под ним: `get_my_client_projects`=0,
`get_my_project_payments`=0 (проекции без чужого); ПРЯМЫЕ `transactions`=0, `project_shares`=0,
`projects`=0 — RLS блокирует чувствительные таблицы реальной клиентской сессии. §1 подтверждён на
рантайме данных (не только статикой). Cleanup выполнен.

## Новые уроки среды (в дополнение к drvfs-граблям)
1. **Edge-функции с кириллицей в комментах деплоить ТОЛЬКО `cp` с /mnt/f** (Linux-сторона, UTF-8
   цел). `Get-Content|wsl` stdin ДРОПАЕТ кириллические байты → битый UTF-8 → Deno не грузит модуль
   («could not find an appropriate entrypoint», при этом grep U+FFFD=0 — байты дропнуты, не заменены).
   Коммитнутый `deploy-edge-function.sh` (cp) — правильный; я зря пайпил, потерял время.
2. **`UID` — readonly builtin в bash** (numeric user id): `UID=$(...)` падает. В скриптах — другое имя (NUID).
3. **`find` для локации в /mnt/f**: правильный `maxdepth` (файл на глубине N от /mnt/f, не угадывать мелко).
4. **Авто-гейт классификатора** надёжно ловит размытое «го» на прод-запись/merge/деплой/секреты — это
   правильно; на необратимо-наружных шагах брать **явное адресное** подтверждение (AskUserQuestion), не инференс.

## Статус
Обе фичи в main (local ahead origin на 12 коммитов — НЕ пушено), на проде живые. Долги обеих фич —
after-merge (в ledger `.superpowers/sdd/progress.md`). Ветки `feature/*` не удалены.

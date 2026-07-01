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

T3 param naming (`supabase` vs `client`); T4/setTab dead ternary; T7 `key={i}`; T8 async cleanup (общий паттерн — чинить согласованным проходом), `fmtD`→`fmtDM`, Wallet-иконка ×2. Плюс: браузерный E2E под заказчиком не проводился (нет кред тест-аккаунта); `origin/main` не пушен (local ahead); ветка `feature/client-access-model` не удалена.

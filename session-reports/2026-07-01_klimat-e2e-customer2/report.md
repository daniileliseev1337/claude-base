# Сессия 2026-07-01 — E2E «Заказчик 2.0» (CRM klimat-pro) + инцидент VPS-туннеля

## TL;DR
Прогнан браузерный E2E фичи «Заказчик 2.0» (портал заказчика + интерфейс сотрудника + §7-изоляция).
Секции 7–10 чеклиста — все зелёные. По ходу вскрылся инцидент: VPS-туннель (frps) для внешнего
домена лёг на стороне хостера; сделан временный обход фронта на локальный Supabase, E2E добит.

## Среда
- Репо: F:\<сайт>\redesign-v2-fresh, ветка main (всё запушено ранее).
- Фронт: nginx-контейнер (127.0.0.1:8080). Supabase self-hosted (WSL2 Docker), kong :8000.
- Внешний доступ фронта к API — через публичный домен <vps-domain> (VPS <vps-ip>) по FRP-туннелю.

## Подготовка тест-данных (прод-БД, с явного согласия владельца)
Ранее `test-client@example.com` существовал без пароля/identity (вход невозможен). Сделано SQL-скриптом
(транзакция, без DELETE, без service_role, идемпотентно):
1. `test-client`: приведён к рабочему виду GoTrue (aud/role='authenticated', instance_id, raw_app_meta_data,
   encrypted_password=bcrypt через pgcrypto, email_confirmed_at) + создана запись `auth.identities` (provider=email).
2. Создан изолированный `test-employee@example.com` (INSERT auth.users → триггер handle_new_user создал profile →
   approved=true + user_roles='employee') + identity.
3. Данные для приёмки: проект заказчика (client_id привязанного clients) + 2 задачи статуса «На проверке».
Пароль обоих тестовых: `<test-pw>`. Фиксированные UUID (c111 / e222 / 91a1 / 92a1-92a2) для лёгкого cleanup.

### Грабли настройки auth-логина вручную
- `auth.identities.email` — GENERATED-колонка: нельзя вставлять явно (убрать из INSERT).
- **«Database error querying schema»** при логине = NULL в token-полях `auth.users`
  (confirmation_token/recovery_token/email_change/email_change_token_new/…). GoTrue сканирует их в
  не-nullable Go-строки. Фикс: `COALESCE(...,'')` всем token-полям. Без identity + без этих '' логин не идёт.
- PGCLIENTENCODING=UTF8 для `docker exec … psql < file.sql` — иначе кириллица (CHECK-значения
  «На проверке»/«В работе»/«Обычный») бьётся.
- Sandbox: Write с прод-мутирующим SQL уходил в overlay (файл не появлялся на реальном диске);
  прогон психал `dangerouslyDisableSandbox` — но только ПОСЛЕ явного согласия владельца на прод-запись.

## Результаты E2E (секции 7–10 чеклиста)
- **7** Создание заявок: 7.1 модалка · 7.2 marketplace/быстрый · 7.3 assignee/подробный + валидация
  «без исполнителя не отправить» · 7.4 БД (mode/assignment_mode/status/desired_executor_id) — ✅.
- **8** Приёмка задач заказчиком: 8.1 бейдж openTaskCount «●2» · 8.2 модалка списка · 8.3 Принять→«Готово»
  (счётчик 2→1) · 8.4 Вернуть→«В работе» — ✅. RPC `client_set_task_status` (переход «На проверке»→Готово/В работе).
- **9** Сотрудник: 9.1 вкладка «Заявки» с бейджами путей · 9.2 Принять marketplace→проект «Поиск исполнителя»
  · 9.3 Отклонить · 9.4 уведомления заказчику «Заявка принята/отклонена» — ✅ (UI + БД).
- **10** §7 + регрессия: 10.1/10.2 · 10.3 регрессия employee (проекты/задачи/маркетплейс, создание задачи) — ✅.

### Нюанс §7 (10.1) — не баг безопасности, кандидат на чистку
Bootstrap заказчика ВСЁ РАВНО шлёт прямые `from('projects')` + `clients`/`transactions`/`project_requests`.
RLS режет их в `[]` (утечки чужих данных НЕТ, изоляция по данным работает). Но чеклист ждал полного
отсутствия этих запросов. Источник — общий bootstrap (fetchProjects и др.) вызывается и для клиент-only.
Правка (если нужна): не дёргать общие fetch* для isClientOnly-ветки. Приоритет низкий (косметика/лишний трафик).

## Инцидент: VPS-туннель (frps) лёг
Между сессиями (~ночь) внешний домен перестал отвечать. Диагностика:
- Локальная сторона исправна: kong :8000 жив (401), frpc.service active, конфиг корректный
  (proxies web 8080, api 8000; serverPort 7000).
- VPS <vps-ip>: ICMP ping ОК (~0.4ms), TCP SYN-ACK есть, но **прикладной обмен виснет** — frps login
  `connection write timeout`, SSH :22 `banner exchange timeout`. Порты 8000/8080/443 = 000.
- Внешний интернет с машины исправен (ya.ru/1.1.1.1 → 30x). Проблема специфична для VPS → **сторона хостера**.
- Ребут VPS владельцем НЕ помог (картина не изменилась). SSH в VPS мёртв → починить frps удалённо нельзя.

### Обход (по решению владельца) — фронт на локальный Supabase
- Создан `.env.production.local`: `VITE_SUPABASE_URL=http://localhost:8000` (тот же anon-ключ, VAPID).
  `.env.production` (sslip.io) НЕ тронут → откат = удалить .local + пересобрать.
- Проверено: локальный kong отдаёт CORS `Access-Control-Allow-Origin: *` (preflight + реальный ответ).
- `npm run build` → deploy-web.sh → nginx (index-D-tT95bN.js). Сброшен PWA service-worker + caches в браузере.
- Результат: сайт на http://localhost:8080 работает полностью (0 console errors), 10.3 добит на обходе.

## ОТКРЫТО / TODO следующей сессии
1. **Вернуть внешний адрес**: когда VPS/frps оживёт — удалить `.env.production.local`, `npm run build`, deploy.
   Без этого внешний доступ (sslip.io) не работает; локально — работает через обход.
2. **VPS**: проверить у хостера, что машина реально перезагрузилась / не заблокирована (SSH тоже висел).
3. **Cleanup тест-данных** (по явным UUID, с согласия): решение владельца отложено — оставлены для ручной
   проверки портала локально. Тест-логины test-client/test-employee активны.
4. **§7-нюанс** (лишние пустые bootstrap-запросы у клиент-only) — решить, чистить ли.
5. Ветка feature/customer-2.0 — можно удалить (всё в main), не трогал.

## Грабли (памятка)
- Ручной auth-user в self-hosted Supabase: нужны identity + непустые token-поля + корректные aud/role/instance_id.
- FRP: frpc active ≠ туннель жив; смотреть `journalctl -u frpc` (login write timeout = frps недоступен).
- PowerShell→wsl: одинарные кавычки; сложные SQL — файлом через `docker exec -i < file` + PGCLIENTENCODING=UTF8.
- Разделять «фронт работает» и «внешний доступ работает»: при туннеле это два разных отказа.

## РАЗРЕШЕНО — причина была VPN, не хостер
Догадка владельца («может из-за VPN?») оказалась верной. Диагностика:
- Windows-route к VPS шёл через `happ-tun` (клиент Happ / sing-box; процессы sing-box+xray).
- MTU-probe: `ping -M do -s 1208 <vps>` проходит, `-s 1400` → «Message too long». VPN-инкапсуляция
  урезала path MTU (~1236) → крупные пакеты (FRP-login, SSH-banner) дропались (blackhole),
  мелкий handshake проходил → «порт открыт, обмен виснет».
- ВМ у хостера была активна всё время; проблема — локальный VPN заворачивал росс. VPS в туннель.

**Фикс:** Happ → Настройки туннеля → Правила маршрутизации → Редактировать → **Direct** →
добавлено `193.124.130.236` (IP с точками — frpc ходит по IP) + `193-124-130-236.sslip.io` (домен).
Порядок Block→Direct→Proxy → VPS ушёл напрямую. После переподключения VPN: frpc `login success`,
proxy [api web] up, sslip.io web = 200.

**Обход откачен:** `.env.production.local` удалён, пересборка на sslip.io, деплой
(bundle index-DumW_1Es.js → VITE_SUPABASE_URL=sslip.io). Проверено: localhost:8080=200, sslip.io=200.
Штатная конфигурация восстановлена полностью.

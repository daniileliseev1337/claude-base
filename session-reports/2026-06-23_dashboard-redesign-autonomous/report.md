# Session report — UI-редизайн дашборда (+ автономная фаза + багфиксы + handoff)

**Дата:** 2026-06-22 → 2026-06-23. **Проект:** self-hosted дашборд (React+Vite, self-hosted Supabase, Nextcloud).
**Репо:** `F:\Сайт\redesign-v2-fresh`. **Прод:** https://193-124-130-236.sslip.io

## TL;DR
Редизайн max-wow black&gold реализован, задеплоен, 2 бага исправлены. Создан универсальный
класс `.kp-card`. Осталось применить его к 4 экранам + полировка → **handoff в новый чат**.

## Что сделано (на проде, бандл обновлён)
1. **Редизайн (6 задач):** живой золотой canvas-фон (BackgroundCanvas.jsx), `.gold-ingot` слиток-рамка
   + breathe/shimmer/ingot анимации (alternate, без рывка) + бейдж ⌘K, 3D-tilt+рамка на Card/KpiCard,
   шапка (значок-breathe + текст-shimmer + бейдж ⌘K + панель-туман). count-up уже был (AnimatedNumber).
2. **2 бага исправлены** (коммит 38079cf): canvas `z-index:-1` (контент вкладок не уходит под фон);
   убрана боковая mask шапки (углы не затемнены).
3. **Единый стиль (начат):** универсальный `.kp-card` (фон + слиток-рамка + spotlight + hover) +
   `.kp-rise` (stagger) в index.css; `TaskCardBoard` (4806) переведён на `.kp-card`. Коммит 8197f0f.

## Что ОСТАЛОСЬ по дизайну (для нового чата)
- Применить `.kp-card` к карточкам-секциям экранов: **Проекты, Финансы (`Finance` 5378), Аналитика
  (`Analytics` 5592), Заказчики (`ClientsPage` 6824)**. Паттерн (как в TaskCardBoard 4806):
  добавить `className="kp-card" onMouseMove={spotlightMove}` + УБРАТЬ inline `background/border/borderRadius`
  (их задаёт `.kp-card`). Оставить padding/прочее.
- **magnetic** на главные кнопки (компонент `MagneticButton` уже импортирован).
- **stagger** — класс `.kp-rise` на блоки дашборда (можно с inline `animationDelay`).
- **должность профиля** — ⚠ в `profile` НЕТ поля должности; «Гл. инженер» выдумывать нельзя.
  Решение владельца: добавить поле в БД ИЛИ дать текст.

## Ключевые локации (App.jsx ~8205 строк)
- `Card` 1185, `KpiCard` 1372, `spotlightMove` 1179 + `tiltMove/tiltLeave` рядом.
- `TaskCardBoard` 4806 (пример применения `.kp-card`).
- Экраны: `TasksView` 4921, `Finance` 5378, `Analytics` 5592, `ClientsPage` 6824.
- Шапка 8398+ (лого 8429 brand-shimmer, бейдж cmdk-badge, профиль ~8490+).
- index.css: `.kp-card`/`.kp-rise`/`.gold-ingot`/`.brand-breathe`/`.brand-shimmer`/`.cmdk-badge`.
- `BackgroundCanvas.jsx` (z-index:-1, fixed).

## Грабли среды (КРИТИЧНО соблюдать)
- **F: сбоит на fsync больших файлов** → App.jsx править через `C:\temp\App.jsx` (Edit) → `Copy-Item` на F.
  index.css — можно прямой Edit (средний файл, проходит).
- **git только Windows-сторона:** `git -C "F:\Сайт\redesign-v2-fresh" -c safe.directory=* -c core.fsyncMethod=writeout-only`.
  В PowerShell НЕ `| tail/head`. Коммиты на main, БЕЗ push (если не просят).
- **Деплой (по слову):** `npm run build` (в репо) → `wsl bash -c 'bash /mnt/f/*/redesign-v2-fresh/deploy/nextcloud/deploy-web.sh'`.
  Бандл-хэш меняется. На сервере: `wsl bash -c 'ls /srv/daniil-deploy/web/assets/'`.
- **PWA SW кэширует старый бандл** — после деплоя не виден без сброса: владельцу инкогнито/переустановка PWA;
  в playwright: `navigator.serviceWorker.getRegistrations()→unregister` + `caches.keys()→delete` + reload.
- **Визуальная проверка:** playwright блокирует `file://` и localhost (corp-прокси). Прод (https sslip.io)
  через playwright доступен — навигация/скриншот/клик работают (для приёмки). Владелец смотрит сам.

## Артефакты в git (main, НЕ запушено)
- Спек/эталон/план редизайна: `docs/superpowers/specs/2026-06-23-dashboard-ui-redesign-design.md`,
  `km-etalon-black-gold.html` (эталон стиля — источник истины), `docs/superpowers/plans/2026-06-23-dashboard-ui-redesign.md`.
- Спек блока Я.Диск (отдельная задача, требует выбора владельца + OAuth-токен): `docs/superpowers/specs/2026-06-23-yadisk-read-block-spec.md`.
- Коммиты: dd1d8eb, 2fc2698, 06166b3, 45c3c2c, 7f1a888, c30db59, d453344, 38079cf, 8197f0f.

## Уроки
1. `model:'fable'` → молчаливый fallback на claude-opus-4-8 (проверять модель в `subagents/agent-*.jsonl`).
2. canvas-фон `z-index:0 fixed` (positioned) перекрывает static-контент → давать `z-index:-1`.
3. strict-mode + присваивание read-only DOM (clientWidth) = TypeError → defensive try/catch + таймер-страховка.
4. PWA SW: деплой не виден без сброса SW.
5. Не реализовывать блок с неоднозначными требованиями автономно — спек-вопросник честнее.

## Открытый вопрос (не дизайн)
- Блок Я.Диск считывание: выбрать вариант A/B/C + дать OAuth-токен `danii1126` + маппинг папка↔проект.
  Спек готов (`2026-06-23-yadisk-read-block-spec.md`).

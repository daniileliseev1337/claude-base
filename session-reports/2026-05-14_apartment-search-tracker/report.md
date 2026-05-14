# Session report: трекер-анализатор поиска квартиры (harvest stage)

**Дата начала:** 2026-05-14
**Host:** Claude Code on the web (worktree, репо `claude-base`)
**Project cwd:** `/home/user/claude-base/` (web-sandbox)
**Источник:** Claude Code Web (ветка `claude/apartment-search-tracker-Y4Nmx`)

---

## Запрос пользователя (кратко)

> «А можно создать или как то ещё с помощью тебя сделать трекер - анализатор
> поиска вартиры по яндекс-недвижемости ?»

Уточнения:
- Формат: **сначала harvest** (искать готовые инструменты).
- Функции: **и трекинг истории, и скоринг/фильтрация**.
- Артефакт: **отдельный проект** (не часть claude-base).

---

## Что делал (хронология)

1. STOP-процедура: прочитан CLAUDE.md, отмечено что MCP-аудит неприменим
   (web-сессия, локальные MCP-серверы недоступны).
2. AskUserQuestion: уточнил формат, фокус, место хранения. Получил направление —
   harvest, трекинг+скоринг, отдельный проект.
3. WebSearch ×4 параллельно: разные запросы про парсеры Yandex Realty / CIAN /
   Avito, telegram-боты для мониторинга, аналитика цен.
4. WebFetch на GitHub API для 5 топ-кандидатов: получены метаданные
   (stars/last_commit/license/archived).
5. WebFetch x3 на ещё двух кандидатов (flathunter, cian-parser-showcase) —
   часть запросов получила 403 (rate limit).
6. Фильтрация по правилам CLAUDE.md (<12 мес, ≥50 stars, ясная лицензия).
7. Записал заметки в `harvested/` по каждому проверенному репозиторию.

---

## Источники

### MCP-серверы

- `WebSearch` — встроенный (не MCP) — поиск кандидатов на GitHub.
- `WebFetch` — встроенный — чтение метаданных через api.github.com.
- `github` MCP — **не использовался**: scope ограничен `daniileliseev1337/claude-base`,
  external repos лучше через WebFetch/WebSearch.

### Скиллы (по триггерам)

- Не активировались (нет триггеров под realty/scraping).

### Slash-команды

- Не использовались.

### Harvest

- Что искал:
  - `github yandex realty parser python tracker apartment`
  - `github "realty.yandex" scraper price history price tracker`
  - `github яндекс недвижимость парсер аренда квартиры`
  - `github apartment search aggregator cian avito yandex realty tracker scoring`
  - `github 2025 realty parser python telegram bot apartment monitoring price history`
  - `github "yandex realty" OR "cian" parser fresh 2024 2025 active maintained`
- Кандидатов всего проверено: 10.
- Прошли фильтр (полностью или с оговоркой): **2** — `zxcloli666/House-Research`
  (с оговоркой по звёздам), `lenarsaitov/cianparser` (с оговоркой по
  активности).
- Прошли частично (для адаптации/референса): 0 прямых под Yandex Realty.
- Отброшены: 8 (мертвые / неподходящий стек / не Россия / архивированы).
- Заметки сохранены в:
  `session-reports/2026-05-14_apartment-search-tracker/harvested/`
  - `romankazakov-yar.md`
  - `zxcloli666-House-Research.md`
  - `lenarsaitov-cianparser.md`
  - `_dead-candidates.md` (сборная под отброшенные)

---

## Главная находка (честно)

**Прямого активно поддерживаемого парсера для realty.yandex.ru с приличной
репутацией на GitHub НЕТ.**

Причины:
1. Яндекс активно блокирует скрейперы: SmartCaptcha, JS-обфускация,
   IP-rate-limits, поведенческий fingerprinting.
2. Публичного API у Yandex Realty нет (есть только YRL — формат для
   агентств чтобы публиковать у них, не для чтения данных).
3. Скрейпинг сайта противоречит их ToS.
4. Любой обходящий капчу скрипт устаревает через 3-6 месяцев.

**Что есть:**
- Под **CIAN**: `lenarsaitov/cianparser` (188★, MIT, 15 мес давности).
- Под **Avito + CIAN**: `zxcloli666/House-Research` (5★, MIT, свежий,
  TypeScript/Deno).
- Прямые «yar», «yrlparser», «yrl-feed-parser» — мёртвы или не про то.

---

## Артефакты для пользователя

На этом этапе (harvest only) — **финальных артефактов в cwd нет**, есть
только заметки в session-reports и итоговый отчёт. Реальный проект
(код трекера) — следующая сессия после решения пользователя по
рекомендациям.

---

## Итерации, ошибки, что переделывал

- Изначально хотел искать только Yandex Realty. После 2 поисков увидел
  что чистого варианта нет — расширил поиск на CIAN/Avito (это
  главные альтернативы по покрытию в РФ) и на общие realty-трекеры
  (flathunter и пр.) для архитектурного референса. Это правильный
  pivot — узкий поиск дал бы пустоту.
- GitHub API через WebFetch вернул 403 на 2 запросах (rate limit). Не
  переделывал — данных от других запросов уже хватило для вердикта.
  Помеченный candidate (`CreatmanCEO/cian-parser-showcase`) оставлен в
  `_dead-candidates.md` с пометкой «требует ручной проверки».

---

## Что выдумывал / подставлял placeholder

- Ничего не выдумывал. Где не было данных — отметил явно («метаданные
  через API получить не удалось», «требует ручной проверки»).

---

## Цитаты пользователя (если важные)

> «А можно создать или как то ещё с помощью тебя сделать трекер -
> анализатор поиска вартиры по яндекс-недвижемости ?»

(на старте — открытый вопрос, не директивная команда; стиль «изучи и
предложи варианты»)

> «продолжи»

(после AskUserQuestion — подтверждение направления)

---

## Открытые вопросы для следующих сессий

1. **Решение пользователя по trade-off:**
   - A) Брать House-Research как base + допиливать Yandex (большой риск
        и потеря времени на антибот).
   - B) Брать cianparser как библиотеку + свой тонкий слой (трекинг
        SQLite + скоринг + Excel/Telegram) + **ручной ввод** для Yandex
        Realty (через избранное в личном кабинете).
   - C) Свой минимальный скрипт без всякого парсинга — фокус на анализе
        данных, которые пользователь сам вставляет (URLs/HTML/JSON
        экспорт).
2. Что важнее в первой итерации — Yandex Realty конкретно или просто
   рабочий трекер по доступным источникам (CIAN/Avito)?
3. Где будут жить данные — локальный SQLite, Google Sheets, Excel,
   PostgreSQL?
4. Уведомления нужны (Telegram/Email) или достаточно «открыл и
   посмотрел»?

---

## Auto-sync

**В начале сессии (auto-pull):**
- Неприменимо: это web-сессия в worktree `claude-base`, hooks
  `~/.claude/scripts/auto-pull.ps1` не запускаются.

**В конце сессии (auto-push прогноз):**
- Изменения в managed paths: `session-reports/2026-05-14_apartment-search-tracker/`
  (отчёт + harvested-заметки).
- Будут закоммичены в текущей ветке `claude/apartment-search-tracker-Y4Nmx`
  и запушены в `daniileliseev1337/claude-base`. Создастся draft PR.
- Это **web-flow**, не auto-sync hooks с локального ПК. На локальный ПК
  изменения попадут при следующей сессии Claude Code через auto-pull
  из `daniileliseev1337/claude-base#main` — но только если эта ветка
  будет смержена в `main`.

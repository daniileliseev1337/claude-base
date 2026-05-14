# apartment-tracker

Трекер-анализатор поиска квартиры. Собирает объявления (CIAN автоматически,
Yandex Realty — попытка автомата + ручной ввод как fallback), хранит историю
цен в SQLite, считает скоринг по твоим весам, экспортирует в Excel,
шлёт уведомления в Telegram.

## Кратко: что умеет

- **Источники**:
  - **CIAN** — через библиотеку [`cianparser`](https://github.com/lenarsaitov/cianparser)
    (MIT, обёртка вокруг cloudscraper).
  - **Yandex Realty** — best-effort парсинг (capture HTML вручную из браузера
    + автоматическое извлечение полей), всегда доступен ручной ввод.
  - **Manual** — добавление лотов вручную через CLI или YAML/JSON.
- **Трекинг истории**: каждое появление лота обновляет `last_seen`, цена
  пишется в `price_history`. Видишь когда лот появился/исчез/подешевел.
- **Скоринг 0-100**: настраиваемые веса в `config.yaml`. Критерии:
  цена за м², расстояние до метро, этаж, площадь, ремонт, год постройки,
  тип продавца, и т.д.
- **Excel-дашборд**: лист «Лоты» + «Скоринг» + «История цен» + «Сравнение».
- **Telegram-уведомления**: новый лот, падение цены, изменение статуса,
  превышение порога скоринга.

## Что НЕ умеет (честно)

- Нет надёжного парсера Yandex Realty: Яндекс активно блокирует ботов
  (SmartCaptcha, JS-обфускация). Best-effort работает на части страниц,
  на остальных — ручной ввод. См. [Yandex Realty — особенности](#yandex-realty--особенности).
- Нет веб-UI. Только CLI + Excel + Telegram.
- Не строит карты и не считает расстояние до точек интереса
  автоматически — нужно вводить вручную (например, минуты до метро
  с самой карточки).

## Установка

```bash
cd apartment-tracker
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или: .venv\Scripts\activate  # Windows PowerShell
pip install -e .
```

## Первоначальная настройка

```bash
# 1. Скопировать примеры конфигов
cp config_examples/config.example.yaml config.yaml
cp config_examples/.env.example .env

# 2. Отредактировать config.yaml — выставить свои веса скоринга и пороги
# 3. Заполнить .env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (опционально)

# 4. Инициализировать БД
apartment-tracker init
```

## Использование

### Добавить лот вручную (Yandex Realty / любой URL)

```bash
apartment-tracker add --source yandex --url "https://realty.yandex.ru/offer/12345"
```

CLI спросит: цена, площадь, комнаты, этаж, год, ремонт, минуты до метро и т.д.
Все поля опциональны кроме цены, площади, комнат, URL.

### Спарсить CIAN по фильтру

```bash
# Добавить фильтр в БД
apartment-tracker filter-add \
    --name "moscow_2k_central" \
    --source cian \
    --url "https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&room2=1&region=1"

# Прогон фильтра
apartment-tracker scrape --filter moscow_2k_central
```

### Пересчитать скоринг

```bash
apartment-tracker score
```

### Экспорт в Excel

```bash
apartment-tracker export --out apartments.xlsx
```

### Telegram-уведомления

```bash
# Разовый прогон: новые лоты + изменения цены с прошлого запуска
apartment-tracker notify
```

### История одного лота

```bash
apartment-tracker history --id cian:12345678
```

### Автоматический polling

Запусти cron-job на `scripts/poll.py` (Linux/Mac) или Task Scheduler (Windows)
с периодом 1-3 часа. См. `scripts/poll.py` для примера.

## Структура проекта

```
apartment-tracker/
├── apartment_tracker/
│   ├── cli.py              # CLI entry point
│   ├── db.py               # SQLite schema + queries
│   ├── models.py           # dataclasses
│   ├── scoring.py          # настраиваемый скоринг
│   ├── tracker.py          # дедупликация, обнаружение изменений
│   ├── exporter.py         # Excel-дашборд
│   ├── notifier.py         # Telegram-уведомления
│   └── sources/
│       ├── base.py
│       ├── manual.py
│       ├── cian.py
│       └── yandex.py
├── config_examples/
│   ├── config.example.yaml # все настройки скоринга + telegram
│   └── .env.example        # секреты (токены)
├── scripts/
│   └── poll.py             # cron-friendly прогон
├── tests/
│   └── test_scoring.py
├── pyproject.toml
└── README.md
```

## Yandex Realty — особенности

Яндекс активно борется со скрейперами:
- SmartCaptcha при подозрительном трафике (любой бот ловится за 5-20 запросов).
- JS-рендеринг основного контента — без headless-браузера почти ничего не
  достать.
- Поведенческий fingerprinting на IP + User-Agent + cookies.
- Публичного API нет.

В этом проекте Yandex Realty работает так:
1. **Попытка автоматического парсинга** через `requests` + ротация
   User-Agent. Получится для ~30% карточек, остальные дадут капчу.
2. **HTML-импорт**: открой страницу в браузере, нажми Ctrl+S → сохрани
   страницу как HTML, передай в CLI:
   ```bash
   apartment-tracker add --source yandex --html-file ./saved-page.html --url <original-url>
   ```
   Парсер извлечёт цену, площадь, этаж, и т.д. из локального HTML.
3. **Ручной ввод**: CLI спросит поля интерактивно.

Альтернатива (не реализована, но возможна позже):
- Использовать `playwright` или `selenium` с реальным браузером и
  ручным решением капчи. Тяжелее, но надёжнее.

## SQLite-схема

См. `apartment_tracker/db.py`. Основные таблицы:
- `listings` — карточки лотов (id, source, url, поля квартиры, статус).
- `price_history` — все наблюдаемые цены с timestamp.
- `scores` — рассчитанные скоринги (с breakdown по критериям).
- `filters` — сохранённые URL-фильтры для periodic polling.

## Скоринг — как считается

Конфиг в `config.yaml`, секция `scoring`:
- `weights` — вес каждого критерия (целое, сумма = 100).
- `thresholds` — границы нормализации в 0..1 для каждого критерия.

Формула:
```
score = sum_i (weight_i * normalize_i(value_i)) / 100 * 100  → 0..100
```

Если поле в карточке отсутствует — критерий считается с нейтральным
значением 0.5 (или пропускается, см. `policy` в конфиге).

Веса можно менять в любой момент и пересчитывать (`score` команда). Старые
скоринги сохраняются вместе с `config_version` — видно как менялся
рейтинг при изменении весов.

## Лицензия

MIT.

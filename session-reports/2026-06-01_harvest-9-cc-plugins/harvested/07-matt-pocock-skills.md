# Matt Pocock skills — mattpocock/skills

## Источник
- URL: https://github.com/mattpocock/skills
- Matt Pocock (известный TypeScript educator)
- Прислал пользователь как «7-я позиция», выделил `/grill-me` и `/handoff`

## Метаданные (GitHub API, 2026-06-01)
- ⭐ Stars: **113,633** (топовый)
- 🍴 Forks: 9,957
- 📜 License: **MIT** ✅
- 📅 Created: 2026-02-03
- 📅 Last push: 2026-05-31 (вчера — очень активный)
- 🐛 Open issues: 51
- Описание: «Skills for Real Engineers. Straight from my .claude directory.»

## Что это — набор из ~17 skills (не 2)
Установка **selective**: `npx skills@latest add mattpocock/skills` →
выбираешь нужные.

- **Engineering (9):** diagnose, grill-with-docs, triage,
  improve-codebase-architecture, setup-matt-pocock-skills, tdd, to-issues,
  to-prd, zoom-out, prototype
- **Productivity (4):** caveman, grill-me, handoff, write-a-skill
- **Misc (4):** git-guardrails-claude-code, migrate-to-shoehorn,
  scaffold-exercises, setup-pre-commit

SKILL.md формат, Claude Code совместимый.

## Сравнение с нашим стеком

| Pocock skill | Наш аналог | Статус |
|---|---|---|
| `handoff` | наш `handoff-to-new-chat` | наш лучше (proactive detection, наши триггеры) |
| `diagnose` | `superpowers:systematic-debugging` | есть |
| `tdd` | `superpowers:test-driven-development` | есть |
| `write-a-skill` | `skill-creator` + `superpowers:writing-skills` | есть |
| `caveman` | отвергли в #1 (домен) | ⚫ |
| `grill-me` | `superpowers:brainstorming` | спорно — см. ниже |

## Ключевой нюанс: grill-me vs наш brainstorming

`/grill-me` — «relentlessly interviewed about a plan until **every branch
of the decision tree is resolved**». Наш `brainstorming` мягче — «explores
intent».

**Почему grill-me потенциально лучше для нас:** правила CLAUDE.md #1-2 —
«не выдумывать, спрашивать при неопределённости». Жёсткий допрос grill-me
реализует этот принцип агрессивнее. Выдумка в нашем домене = ошибка в
спецификации/расчёте. Жёсткий pre-work допрос бьёт по этой проблеме напрямую.

**НЕ списываем через «у нас есть brainstorming»** (урок сессии). Стоит
реально сравнить содержание SKILL.md grill-me vs brainstorming — может
grill-me взять как замену/дополнение.

## Вердикт
🟡 **Selective, НЕ весь набор** (16 skills = дублирование + шум).

| Skill | Решение |
|---|---|
| `grill-me` | 🟡 Сравнить с brainstorming — кандидат на замену/дополнение под «не выдумывай» |
| `handoff` | ⚫ Наш `handoff-to-new-chat` лучше |
| `git-guardrails-claude-code` | 🟡 Заценить на developer-ПК (git safety) |
| `improve-codebase-architecture` | 🟡 Заценить на developer-ПК (ADRs для claude-base) |
| `diagnose`, `tdd`, `caveman`, прочее | ⚫ Дублирует superpowers |

## РЕШЕНИЕ: создать свой skill `domain-grilling` (2026-06-01)

### Почему не заменять brainstorming на grill-me напрямую
Прочитал `skills/productivity/grill-me/SKILL.md`:
- **Описание:** «Interview the user relentlessly about a plan or design until
  reaching shared understanding, resolving each branch of the decision tree.»
- **Методология (золото):** вопросы по одному + к каждому своя рекомендация +
  decision-tree resolution + codebase-first.
- **ПОДВОХ — триггер ручной:** «explicitly mentions "grill me"». Активируется
  только по явной команде. brainstorming — авто (но на код).

Прямая замена НЕ решит проблему пользователя: на строй-задачах grill-me
по-прежнему не сработает сам (нужна явная команда «grill me»). Плюс
codebase-first нерелевантно для стройки.

### Дизайн нового skill (решения пользователя)
- **Имя (рабочее):** `domain-grilling` (финал — на этапе создания)
- **Scope:** ДОПОЛНЯЕТ brainstorming (тот остаётся для кода/developer),
  новый — для строй-задач. Не конфликтуют (разные триггеры).
- **Раскат:** на все 9 ПК (домен-критичный — помогает на основной работе).
- **Механика:** из grill-me (MIT) — one-at-a-time + рекомендация + decision-tree.
- **Авто-триггеры (свои):** «составь спецификацию», «посчитай ВОР/объёмы»,
  «напиши раздел ПД/РД», «подбери оборудование», «составь смету», «составь КП»,
  «разбери УПД», «сделай расчёт», и т.п.
- **Library/norm-first** вместо codebase-first: если вопрос решается через
  `norm-lookup`/library — искать там, не спрашивать пользователя.
- **Привязка к CLAUDE.md #1-2** «не выдумывай, спрашивай при неопределённости».

### Как создавать (отдельная задача на этапе внедрения)
Через `superpowers:brainstorming` (creative work) → `writing-skills` /
`skill-creator`. Тестировать через Skill Creator Eval/Benchmark (#5.1).
**MIT-лицензия grill-me позволяет взять механику.**

## Прочие skills набора
1. git-guardrails-codebase-architecture — заценить на developer-ПК при
   следующей claude-base разработке.
2. `grill-with-docs` (engineering, с ADR-FORMAT + CONTEXT-FORMAT) — более
   продвинутая версия grill с документами/контекстом. Изучить как доп-источник
   идей для `domain-grilling`.

## Рекомендация пользователю
- `handoff` — пропускаем, наш кастомный лучше.
- `grill-me` — главный кандидат, но нужно сравнить содержание с brainstorming
  прежде чем решать (наш «не выдумывай» принцип может выиграть от жёсткого
  допроса). Предлагаю заценить.
- Остальной набор — selective, не целиком.

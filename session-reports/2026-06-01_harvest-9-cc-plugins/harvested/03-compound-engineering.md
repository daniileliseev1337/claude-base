# Compound Engineering — EveryInc/compound-engineering-plugin

## Источник
- URL: https://github.com/EveryInc/compound-engineering-plugin
- Homepage: https://every.to/guides/compound-engineering
- Автор: Every Inc (Dan Shipper, известный publishing/AI house)
- Прислал пользователь как «3-я позиция» подборки 9

## Метаданные (GitHub API, 2026-06-01)
- ⭐ Stars: **18,851**
- 🍴 Forks: 1,416
- 📜 License: **MIT** ✅
- 📅 Created: 2025-10-09 (~8 мес назад)
- 📅 Last push: 2026-06-01 (сегодня, очень активный)
- 🐛 Open issues: 85
- ❌ Archived: no
- Описание: «Official Compound Engineering plugin for Claude Code, Codex, Cursor, and more»

## Что делает
**Полноценный Claude Code plugin** с `.claude-plugin/plugin.json`:
- **37 skills** (slash-команды `/ce-*`)
- **51 custom agent** (review, research, workflow роли)
- Native command definitions в `.claude/commands/`
- Артефакты в `docs/brainstorms/`, `docs/pulse-reports/`, `STRATEGY.md`

### 5-step cycle
1. **`/ce-brainstorm`** — интерактивный сбор требований
2. **`/ce-plan`** — конвертация в implementation spec
3. **`/ce-work`** — execution с task tracking + git worktrees
4. **`/ce-code-review`** — multi-agent code analysis
5. **`/ce-compound`** — документирование learnings для будущих циклов

### Ключевые slash-команды
`/ce-strategy`, `/ce-ideate`, `/ce-brainstorm`, `/ce-plan`, `/ce-work`,
`/ce-debug`, `/ce-code-review`, `/ce-compound`, `/ce-product-pulse`

## Установка
- Claude Code: `/plugin install compound-engineering` (через marketplace)
- Cursor / Codex / Copilot: свои marketplace
- Universal: `bunx @every-env/compound-plugin install`

## Анализ применимости к нашей базе

### Сравнение с существующим стеком

| Их шаг | Наш аналог | Покрытие |
|---|---|---|
| `/ce-brainstorm` | `superpowers:brainstorming` | ✅ Полное |
| `/ce-plan` | `superpowers:writing-plans` | ✅ Полное |
| `/ce-work` | `superpowers:executing-plans` + `subagent-driven-development` | ✅ Полное |
| `/ce-code-review` | `auditor` + `requesting-code-review` skill + узкие ревьюеры | ✅ У нас доменно лучше |
| `/ce-compound` | `harvested/` + `memory/feedback_*.md` + session-reports | 🟡 Частично, без explicit step |
| Архитектура main→subagent | main → domain agent → reviewer | ✅ Полное |

### Где Compound объективно лучше
1. **`/ce-compound` как explicit step** — у нас learning артефакты есть, но нет
   slash-команды которая бы forced-структуру в конце pipeline. У них это
   обязательный 5-й шаг.
2. **Cohesive plugin** — один зонтик вместо разрозненных superpowers skills.
   Снижает когнитивную нагрузку для тех кто не знает наш стек.
3. **51 review-агент** — потенциально есть роли (security, perf, style)
   которые в нашем `auditor` представлены одной фигурой.

### Где Compound не подходит
1. **Огромный context overhead** — 37 skills + 51 agent в каждой сессии.
   На ПК сотрудника-проектировщика это шум.
2. **Generic SDE focus** — `/ce-strategy` для product roadmap не нужен в
   «составь спецификацию <организация>». Domain mismatch.
3. **Английский** — конфликт с нашей дисциплиной русского общения
   (CLAUDE.md правило #5).
4. **Slash-namespace конфликт** — `/ce-brainstorm` параллельно с
   `superpowers:brainstorming` запутает пользователей.

### Архитектурный вопрос: два слоя работы
Наша работа делится:
1. **Applied domain** (стройка) — спецификации, КП, акты, расчёты. Compound
   здесь **не помогает** — не знает АОСР, ГЭСН, СПДС.
2. **Meta-development** (разработка `claude-base`) — новые skills/agents/chains.
   Compound **вписывается идеально**.

## Решение
🟡 **Установить точечно на developer-ПК для meta-development. НЕ раскатывать на 8 ПК команды.**

### Конкретно
- ✅ **На developer-ПК (этот ноутбук) — поставить.** Когда я пишу новый
  skill/agent/chain — Compound даст structured workflow от brainstorm до
  compound. Это закрывает реальную дыру в `chain:claude-base-component`
  (которого у нас нет).
- ❌ **На 8 ПК команды — НЕ ставить.** Их работа = applied domain. Compound
  будет шумом + конфликтом по slash-namespace.
- ✅ **Адаптировать идею `/ce-compound` к нашим chains** — добавить explicit
  «compound» step в pipelines где применимо (например в `chain:project-doc-pack`
  когда дойдёт до реализации).

### Открытые вопросы
1. Если ставить на developer-ПК — через `/plugin install compound-engineering`
   из marketplace или клонировать в `~/.claude/plugins/` локально для контроля?
2. Изучить 51 review-агент — есть ли паттерны для адаптации в наш `auditor`
   (security, perf, style роли)? Это отдельная задача, не из этой harvest-волны.
3. Стоит ли сразу создать `chain:claude-base-component` под наш meta-dev
   workflow (на основе их 5-step)? Или ждать триггера «3-я разработка
   нового skill»?

## Идеи в копилку
- ✅ **Explicit `/compound` step в наших chains** — обязательный финальный
  шаг «что мы выучили, что добавить в memory/». Применить к `chain:project-doc-pack`
  когда будем строить.
- ✅ **Изучить структуру 51 review-агента** — возможно роли (security-reviewer,
  perf-reviewer, accessibility-reviewer) можно адаптировать к нашему домену
  (norm-reviewer, cost-reviewer, schedule-reviewer для разделов ПД).

## Рекомендация пользователю
- На developer-ПК (этот): ставим через `/plugin install compound-engineering`
  для meta-development задач (разработка `claude-base`).
- На 8 ПК команды: не ставим. Compound заточен под generic SDE, наш домен
  другой, и есть конфликт по slash-namespace.
- Идея `/ce-compound`-шага — берём в копилку для адаптации в наши chains.

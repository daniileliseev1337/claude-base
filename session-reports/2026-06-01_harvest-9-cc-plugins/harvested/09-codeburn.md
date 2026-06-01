# Codeburn — getagentseal/codeburn

## Источник
- URL: https://github.com/getagentseal/codeburn
- Прислал пользователь как «9-я позиция» (последняя) подборки

## Метаданные (GitHub API, 2026-06-01)
- ⭐ Stars: **7,407**
- 🍴 Forks: 557
- 📜 License: **MIT** ✅
- 📅 Created: 2026-04-13
- 📅 Last push: 2026-06-01 (сегодня — очень активный)
- 🐛 Open issues: 40
- Описание: «See where your AI coding tokens go. Interactive TUI dashboard
  for Claude Code, Codex, and Cursor cost observability.»

## Что делает
TUI-дашборд расхода токенов / стоимости:
- Daily cost charts, breakdown по проектам/моделям
- 13 категорий задач, one-shot success rates
- `optimize` команда: re-read files, low read/edit ratios, **unused MCP
  servers**, bloated config files, context-heavy sessions
- Каждая находка: estimated savings ($/токены) + ready-to-paste fix

## ✅ Constraint check — идеально
- MIT, open-source, self-hosted, **бесплатно**, no API keys, no subscription.
- Privacy: «Everything runs locally. No wrapper, no proxy, no API keys.»
  Читает session-файлы с диска (`~/.claude/projects/`), данные НЕ уходят
  наружу. Цены через LiteLLM (кэш локально 24h).

## Установка
- `npx codeburn` (без установки)
- `npm install -g codeburn`
- `brew install codeburn`
Требует Node (есть).

## Применимость — прямое попадание

| Codeburn даёт | Наша потребность |
|---|---|
| Метрики токенов | `memory/token_economy.md` — правила БЕЗ метрик |
| Дашборд | **Закрывает идею `/token-stats` из #1** — не писать свой |
| `optimize` → unused MCP | Подтвердит что **Adobe MCP не используется** |
| `optimize` → re-read files | Урок cascade loading |
| `optimize` → bloated config | Большой CLAUDE.md |
| `optimize` → context-heavy | Триггеры `handoff-to-new-chat` |

**Ключевой бонус:** НЕ грузит контекст Claude (отдельный CLI, post-hoc
чтение session-файлов) → zero overhead на сессии.

## Вердикт
🟢 **Ставим, раскат на все 9.**
- Легко (`npx codeburn`), бесплатно, локально, zero session overhead.
- Превращает дисциплину токенов из эвристик в измеримую.
- developer-ПК: + самооптимизация claude-base config через `optimize`.
- 8 ПК: self-monitoring + руководитель может проверить расход на конкретном ПК.

## Идеи / применение
- ✅ **Идея `/token-stats` из #1 закрыта** — Codeburn это и есть, свой не пишем.
- ✅ Прогнать `codeburn optimize` на этом ПК → проверить метрикой
  гипотезы: Adobe MCP unused, bloated CLAUDE.md, re-read паттерны.
- ✅ Дополнить `memory/token_economy.md` ссылкой на Codeburn как инструмент
  измерения.

## Ограничение
- Локальный per-PC, НЕ агрегирует по команде. Для централизованного
  мониторинга расхода 9 ПК — Codeburn сам не подходит (надо на каждом ПК
  смотреть отдельно). Если нужна агрегация — отдельная задача.

## РЕАЛЬНЫЙ ПРОГОН на developer-ПК (2026-06-01)
Node v24.15.0. `npx -y codeburn status / optimize`.

### Итог: Health F (20/100, 9 issues), $1410.60/30 дней, ~18% потенциал экономии

### Находка 1: 10 MCP серверов, половина 0% coverage (High)
Schema unused tools грузится в system prompt каждую сессию + cached prefix.
- Adobe (59c626be): **0/57** за 38 сессий ← подтверждает решение отключить
- PDF_Tools_View: 0/20 · Vercel (a4a36433): 0/18 · Claude_Preview: 0/13
- Gmail (6b6ce0a3): 0/12 · **adeu (наш эталон): 0/11** за 22 сессии
- Desktop_Commander: 1/26 (4%) · Windows-MCP: 2/18 (11%)
- word: 9/54 (17%) · PDF_Tools_Fill: 2/36 (6%)
- **Экономия чистки MCP: ~65M токенов (~$43/мес)**
- ⚠ НЕ удалять слепо: word/pdf-mcp нужны для документов (эпизодические).
  adeu 0% — вопрос пользователю. Connectors (Vercel/Gmail/Preview/PDF_View) —
  кандидаты на отключение.

### Находка 2: pdf-mcp retry-heavy (High) — ВАЖНО для Word/PDF
**pdf-mcp: 7/11 edit-turns retried (64% retry)** в одном проекте.
Codeburn независимо флагнул pdf-mcp как retry-heavy → **объективное
подтверждение жалобы пользователя на косяки PDF**. Первая зацепка для
Word/PDF сессии. Codeburn советует НЕ удалять, а аудировать retry-причину.

### Находка 3: 7 дорогих сессий с weak delivery (~$142 потенциал)
Review-кандидаты (не доказательство waste): сессии с тратами но без
edit-turns / много retries. Codeburn предлагает one-time session-opener
(назвать deliverable, стоп при 2 фейлах) — НЕ добавлять в CLAUDE.md.

### Actionable выводы
1. ✅ Adobe MCP — отключить (0% подтверждён).
2. ❓ Решить судьбу adeu (0%), connectors Vercel/Gmail/Preview/PDF_View.
3. 🔥 pdf-mcp retry — зацепка для Word/PDF сессии.
4. ✅ Codeburn оправдал себя сразу — actionable метрики на первом прогоне.

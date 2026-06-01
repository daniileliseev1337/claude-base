# Harvest-сводка: 9 CC-плагинов (2026-06-01)

Анализ подборки из 9 плагинов/инструментов, присланной пользователем.
Цель — отфильтровать через harvest-workflow и понять что брать в раскат
на developer-hub `claude-base`, что взять как идею, что пропустить.

## Легенда
- 🟢 **Взять** — установить и/или раскатить на команду
- 🟡 **Идея** — не ставим, но идею адаптируем в наши skills/agents/chains
- 🔴 **Заменить** — наш аналог хуже, переходим на это
- ⚫ **Пропустить** — не подходит / уже есть лучше / риски

## ⚠ Глобальные constraints (от пользователя, действуют для всех 9)
1. **Подписки не покупаются.** К-7 не оплачивает платные сервисы. Берём
   только **free tier / open-source / self-host**. Платный-only инструмент
   без free tier → отпадает или ищем open-source альтернативу.
2. **Не списывать через «у нас уже есть X» без верификации** что X работает.
   Подтверждённые failure: WebFetch (80-90% fail), Adobe Firefly (не работает).
   См. `memory/feedback_webfetch_reality_check.md`.
3. **Раскат избирательный.** developer-ПК (этот) ≠ 8 ПК команды. Meta-dev
   инструменты (Compound) — только на developer-ПК. Domain-критичные — в раскат.
4. **Обезличивание** всего что пушится в claude-base.

## Прогресс
| # | Инструмент | Решение | Что взять как идею | Подробнее |
|---|------------|---------|---------------------|-----------|
| 1 | Caveman | ⚫ Пропустить | `/token-stats` дашборд экономии токенов (TODO отдельной задачей) | [01-caveman.md](harvested/01-caveman.md) |
| 2a | Exa | 🟢 Ставим | semantic search; гибрид cloud Exa (публичные) + локальный fastembed (приватные запросы со шифрами) для `norm-lookup` v2 | [02-exa-firecrawl.md](harvested/02-exa-firecrawl.md) |
| 2b | Firecrawl | 🟢 Ставим, решить deployment (cloud / self-host / гибрид) | scraping каталогов производителей; решает реальную проблему 80-90% fail WebFetch | [02-exa-firecrawl.md](harvested/02-exa-firecrawl.md) |
| 3 | Compound Engineering | 🟡 Поставить точечно на developer-ПК для meta-dev (`claude-base`), НЕ раскатывать на 8 ПК | explicit `/compound` step в наших chains; изучить 51 review-агент для адаптации в `auditor` | [03-compound-engineering.md](harvested/03-compound-engineering.md) |
| 4 | Higgsfield | 🟢 **Ставим, если есть free tier** — закрывает дыру image/video generation (Adobe Firefly не работает) | проверить free credits при установке; если free tier нет → искать open-source альтернативу (constraint: подписки не покупаются) | [04-higgsfield.md](harvested/04-higgsfield.md) |
| 🚨 | Adobe MCP (claude.ai connector) | 🔴 **Отключить** — не работает + подписок нет и не будет | Это remote connector «claude.ai Adobe for creativity» (.claude.json:686), НЕ в эталоне 9. Отключить: claude.ai → Settings → Connectors → Adobe → Disconnect. Бонус: разгрузит context | — |
| 5 | Anthropic Official (4 шт) | ⏳ | — | — |
| 6 | OpenAI codex-plugin-cc | ⏳ | — | — |
| 7 | Matt Pocock skills | ⏳ | — | — |
| 8 | Morph | ⏳ | — | — |
| 9 | Codeburn | ⏳ | — | — |

## Накопительный список «идей на потом»
*(не плагины, а методики/паттерны которые подсмотрели и хотим у себя)*

- **`/token-stats`** (из Caveman) — slash-команда: пересчитывает session-report'ы, показывает где утечки токенов. У нас уже есть `memory/token_economy.md` (правила), но без метрик. Дополнить можно отдельным TODO.
- **Semantic search в `norm-lookup` v2** (из Exa) — когда библиотека норм
  разрастётся, добавить поиск по смыслу через локальный `fastembed` (он уже
  есть как зависимость `pdf-mcp`). **Без cloud**.
- **Firecrawl self-host** (из Firecrawl) — open-source, на своём сервере К-7
  = бесплатно навсегда (constraint: подписки не покупаются). Предпочтительнее
  cloud API. Закрывает scraping каталогов производителей + 80-90% fail WebFetch.
- **Explicit `/compound` step в наших chains** (из Compound Engineering) —
  обязательный финальный шаг «что выучили, что добавить в memory/». Применить
  к `chain:project-doc-pack` и будущим chains.
- **Адаптация 51 review-агента** (из Compound Engineering) — изучить их
  роли (security/perf/style) и адаптировать к нашему домену в `auditor`
  (norm-reviewer, cost-reviewer, schedule-reviewer для разделов ПД).

## Итоговая рекомендация
*(заполнится после анализа всех 9)*

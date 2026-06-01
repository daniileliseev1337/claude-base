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
| 4 | Higgsfield | 🟢 направление принято, **🗣 ОБСУЖДЕНИЕ НЕ ЗАВЕРШЕНО** (deployment, ComfyUI setup, раскат, приватность) | гибрид: Higgsfield облако (video/Veo, 10 credits/мес) + ComfyUI локально (images без лимитов, приватность) | [04-higgsfield.md](harvested/04-higgsfield.md) |
| 🚨 | Adobe MCP (claude.ai connector) | 🔴 **Отключить** — не работает + подписок нет и не будет | Это remote connector «claude.ai Adobe for creativity» (.claude.json:686), НЕ в эталоне 9. Отключить: claude.ai → Settings → Connectors → Adobe → Disconnect. Бонус: разгрузит context | — |
| 5.1 | Skill Creator | 🟢 **уже стоит**, начать Eval/Benchmark наших skills | закрывает дыру: пишем skills, но не тестируем; Benchmark для backlog «5 агентов не по template» | [05-anthropic-official.md](harvested/05-anthropic-official.md) |
| 5.2 | Legal | ⚫ **Пропуск (подтверждено)** — РФ-право (common law mismatch) | configurable contract-review playbook → свой `contract-reviewer-rf` при потребности | [05-anthropic-official.md](harvested/05-anthropic-official.md) |
| 5.3 | Frontend Design | 🟢 **Раскат на все 9** (лёгкий skill, lazy, уже auto-installed здесь) | deployment: проверить `claude-plugins-official` marketplace на всех 9 ПК | [05-anthropic-official.md](harvested/05-anthropic-official.md) |
| 5.4 | Security Guidance | 🟢 на developer-ПК (защита раската), не раскат | pre-tool hook на уязвимости в Python-скриптах; gap: PowerShell не покрыт → PSScriptAnalyzer | [05-anthropic-official.md](harvested/05-anthropic-official.md) |
| 6 | OpenAI codex-plugin-cc | 🟢 **Раскат на все 9** (free ChatGPT tier) + **consent-prompt** | cross-model review для всех. Consent-prompt при `/codex:` (данные→OpenAI, free tier→обучение, ПДн 152-ФЗ) [Да/Нет/Обезличить]. Реализация hook на этапе внедрения. Инструкция: завести free GPT аккаунт | [06-codex-plugin-cc.md](harvested/06-codex-plugin-cc.md) |
| 7 | Matt Pocock skills (~17 шт) | 🟢 **СОЗДАТЬ свой `domain-grilling`** (механика grill-me + свои строй-триггеры). `handoff` ⚫ (наш лучше). Остальное ⚫ дублирует | grill-me триггер ручной → не решает; нужен свой skill с АВТО-триггерами под строй («составь спец», «посчитай ВОР»...), library-first. Дополняет brainstorming, раскат на 9 | [07-matt-pocock-skills.md](harvested/07-matt-pocock-skills.md) |
| 8 | Morph | ⚫ **Пропуск** — код-only, НЕ решает Word/PDF (цитата docs); free tier 200 req/мес мизерный | — (WarpGrep не нужен, Grep работает) | [08-morph.md](harvested/08-morph.md) |
| 🔥 | **Word/PDF косяки** | 🚨 **HIGH PRIORITY отдельная тема** — не из 9 плагинов | системная боль пользователя. Нужна диагностика (что/где ломается) → фикс word-helper/pdf-helper ИЛИ harvest docx/pdf инструментов. После #9 | [08-morph.md](harvested/08-morph.md) |
| 9 | Codeburn | 🟢 **Ставим, раскат на все 9** (MIT, локально, бесплатно, zero overhead) | закрывает идею `/token-stats` из #1; `optimize` подтвердит unused Adobe MCP + bloated config; метрики для `token_economy.md` | [09-codeburn.md](harvested/09-codeburn.md) |

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

## Итоговая рекомендация (все 9 разобраны, 2026-06-01)

### 🟢 БЕРЁМ (7 позиций)
| Инструмент | Раскат | Закрывает |
|---|---|---|
| **Exa** | команда (профильные) | semantic search (дыра) |
| **Firecrawl** (self-host) | сервер К-7 | 80-90% fail WebFetch (дыра) |
| **Frontend Design** | все 9 (уже auto-installed) | внутренние UI, lazy |
| **Codex** + consent | все 9 | cross-model review (новый capability) |
| **Codeburn** | все 9 | метрики токенов, zero overhead |
| **Skill Creator** | уже стоит | Eval/Benchmark наших skills |
| **Security Guidance** | ✅ уже auto-installed | уязвимости Python перед раскатом |
| **Compound Engineering** | developer-ПК | meta-dev claude-base |
| **Higgsfield + ComfyUI** | 🗣 не завершено | image/video generation (дыра) |

### 🟢 СОЗДАЁМ СВОЁ (1)
| Что | На основе | Закрывает |
|---|---|---|
| **`domain-grilling` skill** | механика grill-me (#7) + свои строй-триггеры | brainstorming не срабатывает на строй-задачах |

**Статус domain-grilling (2026-06-01):** ✅ draft создан в
`~/.claude/skills/domain-grilling/SKILL.md`, зарегистрирован (виден в
Skill list, hot-reload). **На тестировании** (решение пользователя — оставить
как есть, тестировать). Раскат на 9 — ПОСЛЕ успешного теста.
- ⚠ Наблюдение для теста: пересечение триггеров с `spec-writer`
  («составь спецификацию», «спец», «новая спец»). Ожидаемо НЕ конфликт —
  domain-grilling грилит вводные ПЕРЕД, spec-writer генерирует ПОСЛЕ
  (грилинг → генерация). Проверить на тесте что взаимодействуют правильно,
  а не дублируют/перебивают.

### ⚫ ПРОПУСКАЕМ (3)
- **Caveman** — домен (русская детализация vs англ. compression)
- **Legal** — РФ-право (common law mismatch)
- **Morph** — код-only, не решает Word/PDF

### 🔴 ОТКЛЮЧИТЬ (1)
- **Adobe MCP** (claude.ai connector) — не работает + подписок нет

### 🔥 ОТДЕЛЬНЫЙ ПРИОРИТЕТ (вне 9)
- **Word/PDF косяки** — системная боль, нужна диагностика → фикс/harvest

---

## Предлагаемый порядок внедрения

**Фаза 0 — быстрое, бесплатное, zero-risk:**
1. `npx codeburn optimize` → метрики (подтвердит Adobe unused, bloated config)
2. Отключить Adobe MCP (claude.ai → Connectors)
3. Frontend Design — проверить раскат на 9 (уже auto-installed здесь)

**Фаза 1 — закрывают реальные дыры:**
4. Exa + Firecrawl self-host → WebFetch fail
5. Создать `domain-grilling` skill → brainstorming на стройке
6. Higgsfield + ComfyUI → image/video (🗣 сначала завершить обсуждение)

**Фаза 2 — developer-инструменты:**
7. Codex + consent-hook
8. Security Guidance
9. Compound Engineering (meta-dev)
10. Skill Creator → начать Eval/Benchmark

**Фаза 3 — отдельный приоритет:**
11. 🔥 Word/PDF диагностика → фикс word-helper/pdf-helper или harvest

---

## Статус: анализ 9 ЗАВЕРШЁН (2026-06-01). Дальше — этап внедрения.

### Хвосты этапа внедрения (зафиксированы, не потеряются)
- 🗣 **Higgsfield (#4)** — deployment, ComfyUI setup, раскат, приватность (Фаза 1)
- **Codex consent** — hook vs инструкция, склоняемся к hook (Фаза 2)
- **`domain-grilling`** — финальный дизайн при создании skill (Фаза 1)
- **Adobe MCP** — пользователь отключает в claude.ai → Connectors (веб)

### Отложено на ОТДЕЛЬНУЮ сессию (вместе)
- 🔥 **Word/PDF косяки** — диагностика (Word/PDF? какие задачи? что ломается?
  нужны конкретные примеры файлов).
- 🗣 **Higgsfield + ComfyUI** — deployment image/video. Решение 2026-06-01:
  в той же сессии что Word/PDF. **Искать бесплатные аналоговые решения**
  (готовые open-source генераторы) если Higgsfield free tier мал.
- Обе темы — возможно отдельная сессия (решение пользователя 2026-06-01).

### Следующая тема (эта сессия)
- **Анализ 4 законов Anthropic** (Claude MD) — сравнение с Karpathy:
  дополняют / заменяют / часть лучше. Пользователь скинет.

---
name: gsd-redux
upstream: https://github.com/gsd-build/get-shit-done  (canonical, рекомендован)
fork: https://github.com/open-gsd/get-shit-done-redux  (активный fork, меньше материала)
npm: @opengsd/get-shit-done-redux, @opengsd/gsd-sdk
license: MIT (Lex Christopherson 2025)
stars: 63K (upstream active), 635 (fork)
last_commit: 2026-05-25 (оба активны)
language: TypeScript + JS + Shell
node_min: 22.0.0
harvested_at: 2026-05-22
revised_at: 2026-05-25 (URL upstream исправлен с open-gsd/redux=404 на gsd-build/get-shit-done; assumption «upstream archived» оказалась ошибочной — upstream активен)
applies_to: software engineering workflows (не наш профиль напрямую)
verdict: ВЗЯТЬ 2-3 КОНЦЕПТА точечно, не клонировать целиком
agents_count_upstream: 33 agent.md (как на 2026-05-25)
---

# GSD Redux — Meta-prompting + spec-driven workflow для Claude Code

## Что это

Spec-driven development framework для AI coding agents. Решает context rot через 6-шаговый lifecycle: Initialize → Discuss → Plan → Execute → Review → Verify. Артефакт-driven: каждая фаза пишет/читает структурированные docs (ROADMAP.md, PLAN.md, STATE.md, REVIEW.md, DECISIONS.md, AI-SPEC.md).

## Структура (8+ агентов, ~40 команд)

### Агенты

- `gsd-code-fixer` — применяет фиксы из REVIEW.md, atomic commits per finding
- `gsd-code-reviewer` — статический анализ → REVIEW.md
- `gsd-codebase-mapper` — генерирует STACK.md / ARCHITECTURE.md / CONVENTIONS.md / TESTING.md / INTEGRATIONS.md / CONCERNS.md
- `gsd-ai-researcher` — изучение фреймворков (Context7-MCP) → AI-SPEC.md
- `gsd-advisor-researcher` — design decisions → DECISIONS.md
- `gsd-assumptions-analyzer` — risk, assumptions → STATE.md
- `gsd-executor` — выполнение плана фазы (parallel waves)

### 6 namespace-роутеров (вместо 86 flat-skills)

- `gsd:workflow`, `gsd:project`, `gsd:review`, `gsd:context`, `gsd:manage`, `gsd:ideate`
- **Cold start 120 токенов** (vs ~2150 при flat подходе) — namespace lazy-load на нужный subset.

### Команды (выборочно — самые интересные)

- `/gsd-new-project`, `/gsd-discuss-phase`, `/gsd-plan-phase`, `/gsd-execute-phase`, `/gsd-review-phase`, `/gsd-verify-phase`
- `/gsd-status` — текущее состояние из STATE.md
- `/gsd-map-codebase` — анализ архитектуры (4 фокуса: tech / arch / quality / concerns)
- `/gsd-thread` — сегментация контекста при переполнении (новый чат с миграцией STATE.md + current PLAN.md)
- `/gsd-health --context` — utilization guard (warning 60%, critical 70%)

### SDK + CJS dual interface

- TS SDK для programmatic use + CJS CLI для классического Claude Code
- Sync Runtime Bridge через `synckit` + SharedArrayBuffer (~0.1ms steady-state)

## Что у нас УЖЕ есть похожего

- Named chains (`docx-from-template`, `pdf-scan-extract`) ≈ phase lifecycle
- `handoff-to-new-chat` skill ≈ `/gsd-thread`
- `auditor` agent ≈ `gsd-code-reviewer` (но domain-агностик)
- `session-reports/<...>/report.md` ≈ STATE.md
- `chains-pattern` skill ≈ методология lifecycle

## Чего у нас НЕТ (ценные идеи для заимствования)

### Концепт 1: Context health monitoring (для нашего handoff-to-new-chat)

- Утилизация контекста по % с порогами 60% (warning) / 70% (critical)
- При critical → auto-trigger `/gsd-thread`
- **У нас** сейчас proactive triggers по эвристике (5+ Read, 3+ Agent, 30+ turns) — это OK, но без явных %

### Концепт 2: Structured artifacts как контейнеры контекста

- ROADMAP.md (1 фраза/фаза, 10-15 KB) — общий план
- REQUIREMENTS.md (5-10 KB) — требования
- STATE.md (1-3 KB, frontmatter + progress) — текущее состояние
- PLAN.md (20-40 KB на волну) — детальный план фазы
- REVIEW.md (5-20 KB) — findings с line refs
- DECISIONS.md (10-15 KB) — design decisions + rationale
- AI-SPEC.md (20-30 KB) — best practices для AI системы

**Cascade loading:** агент читает только нужные секции для своей задачи. Не одна большая простыня контекста.

### Концепт 3: Agent prompt structure (методология написания агентов)

Каждый `gsd-*.md` агент имеет четкую структуру:
- Frontmatter: name, description, tools, scope/color
- Role (что за специалист, опыт)
- When to invoke (триггеры подключения)
- Tools available (какие именно tool calls)
- Input artifacts (что читает: STATE.md, PLAN.md, …)
- Output artifacts (что пишет: REVIEW.md, фиксы в коде, …)
- Lifecycle hooks (что делает в начале / в процессе / в конце)
- Output format (структура финального ответа)

**Это методология которой нам не хватает** для создания узких доменных агентов.

### Концепт 4: Atomic commits per finding (low priority для нас)

- gsd-code-fixer коммитит каждый finding отдельно для per-finding rollback
- У нас работа документ-driven, аналог = версии .docx с Track Changes per правка (через `adeu` MCP)

## Что НЕ применимо

- gsd-executor (выполнение кода) — у нас не код
- Unit tests / pytest patterns — нет в наших workflows
- Git commit semantics — наша работа в Office/PDF, не git
- Stack analysis для frameworks (LangChain, CrewAI) — нам нужны ГОСТ/СНиП lookups, не software

## План адаптации (для отдельной сессии)

### Phase A (8-12ч): Заимствование 2 концептов

1. **Расширить `handoff-to-new-chat` SKILL.md** — добавить context utilization thresholds + примеры cascade loading.
2. **Изучить точную структуру agent.md в GSD** — взять как template.
3. **Создать `~/.claude/agents/_TEMPLATE.md`** — методология написания доменных агентов.

### Phase B (16-24ч): 5-8 новых доменных агентов

На основе template:
- `pto-engineer` (расчёты, разделы ПД/РД)
- `сметчик` (КС-смета, ГЭСН/ФЕР)
- `снабженец` (УПД, цены поставщиков)
- `audit-rd-section` (нормоконтроль раздела РД)
- `id-engineer` (журналы, акты ИД)
- `kp-writer` (коммерческое предложение)
- + по обсуждению с пользователем

## Конкретные файлы для изучения

Открыть на github upstream (`gsd-build/get-shit-done`, 33 agent.md):

**Тier 1 (must-read для адаптации):**
- `/agents/gsd-code-reviewer.md` — пример "checker" агента
- `/agents/gsd-codebase-mapper.md` — пример "mapper" агента который пишет 6 docs
- `/agents/gsd-ai-researcher.md` — пример research-агента с Context7-MCP
- `/agents/gsd-doc-writer.md` (38K) — **document writer** (релевантно нашему профилю — мы документ-driven)
- `/agents/gsd-domain-researcher.md` (6K) — **domain researcher** (релевантно — мы тоже domain-specific)

**Тier 2 (для полноты):**
- `/agents/gsd-advisor-researcher.md`, `gsd-assumptions-analyzer.md`, `gsd-executor.md`, `gsd-code-fixer.md`

Плюс не-агентные части:
- `/commands/gsd/workflow/*` — пример namespace router
- `/sdk/src/state/index.ts` — STATE.md parser
- `/sdk/src/phase-runner.ts` — phase lifecycle логика

## Что сделано на основе этой заметки (2026-05-25)

Адаптация Phase A (Concept 1+2+3) закрыта в session 2026-05-25:

- **Concept 1 (Context health monitoring)** — внедрено в `~/.claude/skills/handoff-to-new-chat/SKILL.md` как двухуровневая система WARNING (~60%) / CRITICAL (~70%).
- **Concept 2 (Structured artifacts)** — внедрено как §1-2 «Дисциплина контекста» в SKILL.md + CLAUDE.md (cascade loading + STATE/PLAN/REVIEW/DECISIONS как контейнеры).
- **Concept 3 (Agent prompt structure)** — внедрено как `~/.claude/agents/_TEMPLATE.md` v1.0. POC агенты: `pto-engineer`, `сметчик`, `снабженец`, `audit-rd-section` (auditor PASSED для первых 2, pending для остальных).

См. `~/.claude/session-reports/2026-05-25_context-economy-and-domain-agents/report.md`.

## Не клонировать целиком

40-50ч на полную адаптацию + 70% выкинуть = переусложнение (Karpathy §2). Точечно 8-12ч на 2-3 концепта — ROI положительный (реально потратили ~3.5ч на адаптацию, см. session-report 2026-05-25).

## Ссылки

- **Upstream (canonical, рекомендован):** https://github.com/gsd-build/get-shit-done
- **Fork (активный, меньше материала):** https://github.com/open-gsd/get-shit-done-redux
- NPM: https://www.npmjs.com/package/@opengsd/get-shit-done-redux

## Исправление от 2026-05-25

Предыдущая версия заметки (2026-05-22) содержала **неверный URL**
`https://github.com/open-gsd/redux` — этот репозиторий **не существует**
(404 при попытке доступа через `api.github.com`). Правильные URL —
выше в секции «Ссылки».

Также предыдущая версия указывала «upstream archived ('meme-coin rug-pull')» —
это **ошибочно**. Upstream `gsd-build/get-shit-done` активен (63K stars,
33 agent.md, последний коммит < 1 года). Fork `open-gsd/get-shit-done-redux`
существует параллельно, но **меньше** материала (635 stars).

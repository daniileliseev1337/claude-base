# Harvest: оркестрация + надзор над Claude-сессиями (2026-07-01)

Тема (запрос владельца): чтобы Claude мог видеть/управлять другими своими сессиями (не субагентами внутри одной), следить за правилами по ходу, оркестровать «оркестры» — supervised semi-autonomous, не «тотальная автономия».
Метод: exa-поиск по 3 нишам + верификация через GitHub API (звёзды/лицензию НЕ добил — API-fetch резал на лимите; репо свежие/активные, досверить перед установкой).

## Ниша 1+2 — оркестрация СЕССИЙ + надзор (ближе всего к идее)
- **Conductor** (rmindgh/Conductor) 🎯 — «одна Claude-сессия видит/понимает/УПРАВЛЯЕТ всеми другими»: approve безопасных вызовов, BLOCK опасных (rm -rf/force push) через PreToolUse-хук, send задачи, chain (A→B), Telegram-алерты. Через Anthropic Remote Control API (--rc сессии, WebSocket wss://api.anthropic.com/.../subscribe). Python. Свежий. ⚠ облачный компонент (Remote Control регистрирует сессии на серверах Anthropic — не КНР, но не полностью локально); сырой; звёзды не досверил.
- **claude-squad** (smtg-ai) — популярный (создан 03.2025), tmux+worktrees, N агентов, yolo-режим, review перед push. Но ЧЕЛОВЕК-driven TUI, не Claude-супервизор. Go.
- **sisyphus** (crouton-labs, 02.2026) — оркестратор-Claude в Ralph-loop: дробит→спавнит параллельных агентов в tmux→ревьюит→респавн с полным состоянием. Роли/модели. «Оркестратор stateless, respawn fresh каждый цикл».
- **cwork** (getriff-ai, 03.2026) — worktrees + self-healing review-loop (review→fix→re-review) + tournament mode + real-time kanban dashboard + mobile dispatch. Богатый, автономный.
- (Также: claudio, code-conductor, stackai — parallel Claude Code через worktrees, менее выделяются.)

## Ниша 3 — судья/надзор за правилами по ходу (транскрипт-judge)
- **open-bias** (open-bias/open-bias) 🎯 — «Reliability Harness: make your agents follow rules». Judge-движок: компилирует **RULES.md**, отдельная LLM судит правила ПО ОДНОМУ, ловит **ДРЕЙФ** (sidecar LLM), async (0 задержки — судит в фоне, вмешивается след. ходом) / sync, fail_action=intervene/block/shadow, majority-агрегация нескольких судей. Обёртка NeMo как опция. Буквально «судья следит по ходу». Свежий.
- **NeMo Guardrails** (NVIDIA-NeMo/Guardrails, 2023, зрелый) — programmable guardrails before/after каждого вызова, agent-middleware, self-check input/output/hallucination, jailbreak-детект, API-сервер. ⚠ телеметрия (анонимный пинг NVIDIA), Colang-flows (кривая обучения), больше content-safety чем «наши правила». Apache-2.0.
- **pydantic-ai-guardrails** — llm_judge/tool_allowlist/require_tool_use/auto-retry, но привязан к Pydantic AI.

## Ниша 4 — supervised semi-autonomous фреймворк (runtime + верификация + human-in-loop)
- **Overseer** (nikitavivat/Overseer, 05.2026) 🎯 — «quality control ВНУТРИ runtime»: верификаторы = узлы графа, снапшоты каждого шага, «когда система провалила свои же проверки — ПАУЗА и ждёт человека, а не притворяется». Anthropic-адаптер + локальные (Ollama/vLLM), SQLite, live UI. Ровно «supervised semi-autonomous».
- **LangGraph** (langchain-ai, зрелый, огромный) — фундамент: durable execution, human-in-the-loop (interrupts), память, стриминг. Generic. Основа чтобы строить своё.
- **swarmweave** (pypi v0.1) — supervisor + shared-context + self-improving (Mentor/LessonBook), Apache-2.0, NO telemetry, Anthropic SDK адаптер в планах. Новьё.

## Вывод
Три прямых попадания по слоям: **Conductor** (управление сессиями), **open-bias** (правила по ходу), **Overseer** (semi-autonomous runtime + пауза-на-человека). Baseline для «строить своё» — **LangGraph**. Всё дополняет council-of-high-intelligence (в трекере) и нить «дашборд+телеметрия+петля обратной связи».
Приватность: Conductor завязан на Anthropic Remote Control (облако Anthropic). open-bias/Overseer/LangGraph — локальные.

## Раунд 2 — расширение (свежие углы)

### Human-in-the-loop / approval-гейты («человек на развилках»)
- **HumanLayer** (humanlayer/humanlayer, YC F24) 🎯 — API/SDK: `require_approval()` блокирует high-stakes вызовы до одобрения человеком (отказ → фидбек в LLM), `human_as_tool()` — агент сам спрашивает; каналы Slack/Email/Discord/SMS. ДЕТЕРМИНИРОВАННО (в слое инструмента), любой LLM/фреймворк. Free tier + usage. ⚠ SaaS/API (облако), но есть SDK-примитивы.
- **LangGraph HITL middleware** — то же ЛОКАЛЬНО/нативно: interrupt_on tool-calls, approve/edit/reject/respond, checkpointer-состояние. Часть LangGraph.

### Agent-runtime security / firewall (правила на уровне MCP/LLM-прокси)
- **Invariant Guardrails + Gateway** (invariantlabs-ai) 🎯🎯 — контекстные guardrails как MCP/LLM-ПРОКСИ (сменить base URL, БЕЗ правок кода). Декларативные Python-правила: ограничения tool-call, **data-flow правила** (прочитал подозрительное → блок send_email), prompt-injection, loop-detection. Работает ЛОКАЛЬНО (LocalPolicy, self-host Gateway/Explorer). MCP-native — прямо под нашу MCP-базу. Сильнее open-bias по контекстным/security-правилам. Интеграции AutoGen/Swarm/OpenHands/BrowserUse.

### Claude swarm / hive-mind (тяжеловесы)
- **Ruflo / claude-flow** (ruvnet/ruflo) 🎯 — **~33K звёзд**, «ведущий meta-harness для Claude Code». 100+ агентов, swarm (hierarchical/mesh/adaptive + Raft/Byzantine/Gossip), **Queen-led hive-mind** (Queen = стратегия + quality-control/ревью выводов + синтез обучения), self-learning память, **федерация между машинами с mTLS + PII-stripping** (приватность!), 311 MCP-tools, 17 хуков, autopilot (автоциклы), loop-workers (таймер). `npx ruflo init`. TS. ⚠ ОГРОМНЫЙ (311 tools — риск переусложнения, «обёртка обёртки»), v3alpha.

### Вывод раунда 2
+ HumanLayer (человек-на-развилках), + Invariant (MCP-level локальный rule-firewall — под нашу базу), + Ruflo (33k-звёздный тяжеловес: Queen-надзор + федерация, но alpha/сложный). Метрики (кроме Ruflo ~33k) не досверял.

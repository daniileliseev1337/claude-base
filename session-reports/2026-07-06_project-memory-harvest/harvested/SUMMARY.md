# Harvest: persistent structured project-memory для Claude Code

- **Дата:** 2026-07-06
- **Задача:** пользователь вручную ведёт per-project папку памяти (memory/README/CLAUDE.md/журнал
  сессий; эталон — боевой объект пользователя), хочет внедрить готовый фреймворк/шаблон. Файловый подход
  предпочтителен (мультидевайс через Яндекс.Диск), MCP-память — вторично.
- **Egress машины:** иностранный (NL/Cloudflare) → GitHub через Exa (api.github.com своим IP);
  `curl --noproxy` до api.github.com не пробивается, обычный curl упирается в анонимный rate-limit 60/ч.
- **Метаданные:** верифицированы через api.github.com (не по числам из README).
- **Охват:** GitHub (основной). skills.sh и MCP-registry НЕ прочёсывались — GitHub дал переизбыток
  сильных кандидатов, застревать смысла нет. При желании — дозакрыть отдельно.

## Класс 1 — Файловые per-project шаблоны (ровно сценарий пользователя; markdown, no server, MIT)

| repo | ⭐ | pushed | lic | суть |
|---|---|---|---|---|
| renefichtmueller/claude-cortex | 10 | 2026-06-24 | MIT | file-based memory across sessions/projects/**devices**; MEMORY.md индекс ≤200 строк → topic-файлы; activity-log, project-*, **incident-runbooks** (bug→root cause→fix→prevention), feedback-*, reference-*. Поведение задаётся инструкциями в CLAUDE.md. Чистейший матч. |
| conorbronsdon/claude-context-os | 9 | 2026-06-12 | MIT | «OS для контекста»: `/start`→work→`/end` session-loop, sessions/ по дням, **4 типа памяти user/feedback/project/reference (совпадают с нашей auto-memory!)**, `/dream` авто-куратор (rot-detection, поиск противоречий → reviewable proposal, git-revertable). claude.ai sync. |
| awrshift/claude-memory-kit | 25 | 2026-07-06 | MIT | per-project client folders + **experiments/** sandbox; daily/YYYY-MM-DD; promotion daily→knowledge/concepts→.claude/rules (после 6 мес стабильного паттерна); `/close-day` ритуал с auto-backfill. Zero deps. Мультипроект-изоляция как у эталона пользователя. |
| IlyaGorsky/memory-toolkit | 13 | 2026-04-19 | MIT | «session-layer, которого не хватало рядом с CLAUDE.md»: workstreams, handoff-роутинг, auto-save хуки (PostToolUse/PreCompact), Haiku-watcher извлекает decisions/plans. ~/.claude/projects/<proj>/memory/. |
| blas0/UnseveredMemory | 47 | 2026-01-03 | MIT | enforcement через хуки SessionStart/UserPromptSubmit/SessionEnd (переживает compaction); context/scratchpad/decisions/sessions + .ai/ static. Bash+markdown. Застой (pushed янв). |

**Звёзды тут слабый сигнал** — ниша возникла весной 2026, репы молодые. Отбирать по структуре, не по ⭐.

## Класс 2 — MCP-память (динамический recall, семантический поиск; сложнее, менее прозрачно)

| repo | ⭐ | pushed | lic | суть |
|---|---|---|---|---|
| basicmachines-co/basic-memory | 3170 | 2026-06-08 | **AGPL-3.0 ⚠** | самый популярный; markdown+Obsidian, local-first, MCP. Вирусная лицензия — идеи можно, код копировать в базу нельзя. |
| GreatScottyMac/context-portal (ConPort) | 763 | 2026-01-27 | Apache-2.0 | «memory-bank» MCP, project knowledge-graph + RAG. Застой (pushed янв), SQLite (менее git-friendly для Я.Диск-синка). |
| butterflyskies/memory-mcp | 4 | 2026-07-03 | Apache-2.0 | markdown+YAML в git-репо, **локальные эмбеддинги** (no API key), `sync` push/pull для мультидевайса. Молодой. |
| прочие (Exa, не верифиц.) | — | — | — | dck/brain-mcp (Rust+Obsidian+vector), honam867/obsidian-memory-layer, jodfie/Obsidian-Memory, gosidian (Go, 50 tools), agent-lore/lithos. |

## Класс 3 — Spec-driven фреймворки (соседний класс: структурируют РАБОТУ, не память сессий)

| repo | ⭐ | lic | суть |
|---|---|---|---|
| github/spec-kit | 118231 | MIT | constitution + phased gates (specify/plan/tasks). Про спеки фич, не про память. |
| buildermethods/agent-os | 4973 | MIT | product/ (mission/roadmap/stack) + specs/ + standards-injection. product/ ≈ долгоживущая память проекта. |
| BMAD-METHOD / OpenSpec | — | — | 20+ агентов / минималист two-folder. Тяжело / не про память. |

## Вывод

То, что пользователь изобрёл вручную, — **конвергентный паттерн**: 10+ независимых проектов пришли к
одной схеме (MEMORY.md индекс → topic-файлы + журнал сессий + start/end ритуал + хуки-enforcement +
типизированная память). claude-context-os независимо переизобрёл наши же 4 типа (user/feedback/
project/reference) — сильное подтверждение правильности подхода.

**Чего у нас (глобальная база) НЕТ и стоит взять идеями:**
1. **Bootstrap per-project с нуля** — команда/скилл, создающая структуру папки одним заходом
   (сейчас собирается вручную из наработок).
2. **Auto-curation / rot-detection** (`/dream` из context-os) — курирование памяти на устаревание/
   противоречия. Лечит «память редко дописывается/устаревает».
3. **Per-project журнал сессий** в самой папке проекта (у нас session-reports глобальные в базе, а
   не рядом с объектом).

**Рекомендация:** не ставить чужой фреймворк целиком (своя зрелая система + Я.Диск + русский +
доменная база) — взять 2-3 идеи выше и оформить СВОЙ bootstrap-скилл. Ближайший референс структуры —
claude-cortex; ритуалов и курирования — claude-context-os; мультипроект/промоушена — claude-memory-kit.

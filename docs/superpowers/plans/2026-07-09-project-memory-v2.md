# project-memory v2 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Усилить ядро project-memory — надёжная доставка контекста проекта (независимо от cwd), блокирующий гейт чтения перед работой, `КОНТЕКСТ.md` с ролью-мостиком к доменным агентам.

**Architecture:** Облегчённый механизм — 1 новый UserPromptSubmit-хук (path-detect + инжекция ядра раз на сессию) + регистрация факта чтения в существующий `log-tool-usage.ps1` (PostToolUse) + 1 новый PreToolUse-гейт (блок мутаций exit 2 пока `КОНТЕКСТ.md` не прочитан). Walk-up вынесен в общий `find_project.ps1` (реюз из `session_start.ps1`). Вне проектов-памяти — мгновенный no-op.

**Tech Stack:** PowerShell 5.1 (хуки, ASCII-only source + UTF-8 stdin-обвязка), Python 3.12 (bootstrap, pytest), settings.shared.json (регистрация).

## Global Constraints

- **Кодировка (жёстко, 3 бага за 2026-07-09):** каждый .ps1-хук первой логикой ставит `[Console]::InputEncoding/OutputEncoding = UTF8`; источник ASCII-only, кириллица через кодпоинты (как `session_start.ps1`).
- **No-op вне проектов:** хук первым делом проверяет наличие проекта (путь+`Claude/journal`); нет → `exit 0` за ~5мс.
- **Инжекция ядра — ОДИН раз на сессию** (маркер), не на каждый промпт.
- **exit 0 всегда** у UserPromptSubmit/PostToolUse (не ломать сессию); `exit 2` ТОЛЬКО у PreToolUse-гейта на мутацию без чтения.
- **Пути в шаблонах — относительные.** Обезличивание: без ФИО/шифров/объектов.
- **Ревьюер-гейт:** готовый Этап 1 → `auditor` (архитектура базы) до выдачи владельцу.
- JournalName = `ЖУРНАЛ СЕССИЙ.md`; ядро-папка = `Claude/`.

---

## Task 1: `КОНТЕКСТ.md` — шаблон + bootstrap с маппингом домен→агент

**Files:**
- Create: `skills/project-memory/templates/core/КОНТЕКСТ.md.tmpl`
- Modify: `skills/project-memory/tools/bootstrap.py` (CORE_FILES += КОНТЕКСТ; `--role`/`--domain` → агент)
- Test: `skills/project-memory/tests/test_bootstrap.py`

**Interfaces:**
- Produces: `КОНТЕКСТ.md` в `Claude/` при bootstrap; функция `domain_to_agent(domain: str) -> str`.

- [ ] **Step 1: Шаблон `КОНТЕКСТ.md.tmpl`** — секции ТВОЯ РОЛЬ (роль, домен, `Ведущий агент: [АГЕНТ]`, «работать ЧЕРЕЗ него»), КРИТЕРИИ ГОТОВНОСТИ, ГРАБЛИ (топ-3), ФАКТЫ→FACTS.md. Плейсхолдеры `[ПРОЕКТ]/[РОЛЬ]/[ДОМЕН]/[АГЕНТ]/[ДАТА]`.

- [ ] **Step 2: Failing-тест маппинга** в test_bootstrap.py:
```python
def test_domain_to_agent_maps_known_domains():
    from bootstrap import domain_to_agent
    assert domain_to_agent("ОВ") == "designer"
    assert domain_to_agent("ВОР") == "pto-engineer"
    assert domain_to_agent("ИД") == "id-engineer"
    assert domain_to_agent("смета") == "сметчик"
    assert domain_to_agent("???") == ""   # неизвестный → пусто, не выдумывать
```

- [ ] **Step 3: Прогнать — FAIL** (`pytest ... -k domain_to_agent`, ImportError/AttributeError).

- [ ] **Step 4: Реализация** `domain_to_agent` в bootstrap.py — dict-маппинг (ОВ/ВК/ЭО/СС→designer; объёмы/ВОР/спеки→pto-engineer; ИД/акт→id-engineer; смета→сметчик; снабжение/УПД→снабженец; письмо→letter-writer; КП→kp-writer; замечания→expertiza-responder; Revit→pyrevit-engineer; норма→norm-lookup). Ключи — по подстроке, регистр-независимо. + добавить `("КОНТЕКСТ.md.tmpl", Path("Claude")/"КОНТЕКСТ.md")` в CORE_FILES, render заменяет `[РОЛЬ]/[ДОМЕН]/[АГЕНТ]` (из `--role/--domain`, агент авто из домена).

- [ ] **Step 5: Тест bootstrap создаёт КОНТЕКСТ** :
```python
def test_bootstrap_creates_kontekst(tmp_path):
    from bootstrap import bootstrap
    rep = bootstrap("Тест", tmp_path)
    assert (tmp_path/"Claude"/"КОНТЕКСТ.md").exists()
```

- [ ] **Step 6: Прогнать оба — PASS** (`pytest skills/project-memory/tests/test_bootstrap.py -v`).

- [ ] **Step 7: Commit** — `feat(project-memory): КОНТЕКСТ.md шаблон + домен→агент маппинг в bootstrap`.

---

## Task 2: `find_project.ps1` — общий walk-up (path ИЛИ cwd → проект)

**Files:**
- Create: `skills/project-memory/tools/hooks/find_project.ps1`
- Test: `skills/project-memory/tests/test_hooks.py` (вызов через powershell)

**Interfaces:**
- Produces: скрипт печатает JSON `{root, journal, kontekst}` или пусто. Вход: `-StartPath <путь>`. Walk-up 12 уровней ищет `<d>/Claude/<journal>`; поддержка когда сам путь внутри `Claude/`.

- [ ] **Step 1: Failing-тест** — создать `tmp/proj/Claude/ЖУРНАЛ СЕССИЙ.md`, вызвать `find_project.ps1 -StartPath tmp/proj/sub/file.txt`, ждать root=tmp/proj в выводе.

- [ ] **Step 2: FAIL** (файла нет).

- [ ] **Step 3: Реализация** — вынести walk-up из `session_start.ps1:36-49` в параметризованную функцию (StartPath вместо cwd); UTF-8-обвязка + JournalName из кодпоинтов; печать JSON root/journal/kontekst (kontekst = `<root>/Claude/КОНТЕКСТ.md` если есть). Нет проекта → пустой вывод, exit 0.

- [ ] **Step 4: PASS** тест.

- [ ] **Step 5: Рефактор** `session_start.ps1` — звать `find_project.ps1` (один дом walk-up); прогнать существующий test_hooks — зелёный.

- [ ] **Step 6: Commit** — `refactor(project-memory): walk-up → общий find_project.ps1`.

---

## Task 3: `project_context.ps1` — UserPromptSubmit (доставка ①, инжекция раз/сессию)

**Files:**
- Create: `skills/project-memory/tools/hooks/project_context.ps1`
- Test: `skills/project-memory/tests/test_hooks.py`

**Interfaces:**
- Consumes: `find_project.ps1`. Вход: stdin JSON `{prompt, cwd, session_id}`.
- Produces: инжектит в контекст ядро (КОНТЕКСТ + верх журнала + STATUS) + директиву гейта ОДИН раз на сессию+проект (маркер `<state>/ctx_<sid>_<hash>.json`).

- [ ] **Step 1: Failing-тест** — prompt с путём в проект-память → вывод содержит `СТОП` и `КОНТЕКСТ`; второй вызов той же сессии → тихо (маркер). Prompt без проекта → пусто.

- [ ] **Step 2: FAIL.**

- [ ] **Step 3: Реализация** — UTF-8 stdin; извлечь пути из `prompt` (regex Windows `C:\…`, кавычки) + fallback cwd; для каждого `find_project.ps1`; первый с ядром = проект; маркер инжекции `ctx_<sid>_<projhash>` — есть и свежий → exit 0 (не долбить); иначе Write-Output ядро (КОНТЕКСТ.md полностью + верх журнала 2 записи + STATUS.md) + `СТОП. По проекту <X> подтверди: ✓ прочитал КОНТЕКСТ`; поставить маркер. Вне проекта → exit 0 мгновенно.

- [ ] **Step 4: PASS.**

- [ ] **Step 5: Замер** — `project_context.ps1` ≤ session_start +100мс (не превысить бюджет).

- [ ] **Step 6: Commit** — `feat(project-memory): доставка ядра через path-detector (UserPromptSubmit)`.

---

## Task 4: Блокирующий гейт — регистрация чтения + PreToolUse exit 2

**Files:**
- Modify: `scripts/log-tool-usage.ps1` (PostToolUse: ловить Read(КОНТЕКСТ.md) → маркер `прочитано`)
- Create: `skills/project-memory/tools/hooks/project_gate.ps1` (PreToolUse)
- Test: `skills/project-memory/tests/test_hooks.py`

**Interfaces:**
- Consumes: `find_project.ps1`, маркер сессии.
- Produces: `project_gate.ps1` — на Write/Edit/Task в папке проекта без маркера `прочитано` → stderr + `exit 2`; иначе exit 0.

- [ ] **Step 1: Failing-тест** — (a) Read КОНТЕКСТ проекта → log-tool-usage ставит маркер `read`; (b) Write в проект без `read` → project_gate exit 2; (c) после `read` → exit 0; (d) Write вне проекта → exit 0.

- [ ] **Step 2: FAIL.**

- [ ] **Step 3: log-tool-usage** — добавить БЛОК (после UTF-8, не ломая вес-гейт): если `tool_name==Read` и `tool_input.file_path` заканчивается `Claude\КОНТЕКСТ.md` → записать маркер `ctxread_<sid>_<projhash>`. Fail-open, exit как раньше.

- [ ] **Step 4: `project_gate.ps1`** — UTF-8 stdin; tool ∈ {Write,Edit,MultiEdit,NotebookEdit,Task}; путь аргумента (или cwd для Task) → `find_project.ps1`; проект есть И маркера `ctxread` нет → `Write-Error "[project-memory] Сначала прочитай Claude/КОНТЕКСТ.md проекта <X>"; exit 2`; иначе exit 0. Вне проекта → exit 0.

- [ ] **Step 5: PASS** все 4.

- [ ] **Step 6: Commit** — `feat(project-memory): блокирующий гейт мутаций по факту чтения КОНТЕКСТ (exit 2)`.

---

## Task 5: Регистрация хуков + доки + ревьюер-гейт

**Files:**
- Modify: `settings.shared.json` (UserPromptSubmit += project_context; PreToolUse += project_gate)
- Modify: `skills/project-memory/SKILL.md`, `skills/project-memory/README.md`

- [ ] **Step 1:** В settings.shared.json добавить в СУЩЕСТВУЮЩИЕ блоки: UserPromptSubmit += `project_context.ps1`; PreToolUse += `project_gate.ps1` (не дублировать матчеры). log-tool-usage уже в PostToolUse.

- [ ] **Step 2:** SKILL.md — секция «v2: доставка+гейт+КОНТЕКСТ» (что делает, маркеры, no-op-граница). README — сниппет установки хуков (через update-config).

- [ ] **Step 3:** Живой smoke — сессия из папки проекта И путём в сообщении: ядро инжектится, гейт блокирует Write до Read, после Read пропускает.

- [ ] **Step 4: Ревьюер-гейт** — `auditor`: Этап 1 vs спека (доставка/гейт/роль-мостик), кодировка, no-op вне проектов, exit-коды. PASSED → выдача владельцу.

- [ ] **Step 5: Commit** — `feat(project-memory): v2 Этап 1 (фундамент) — регистрация хуков + доки`.

---

## Следующие этапы (отдельные планы, НЕ в этой сессии)

Декомпозированы по scope-check — каждый самостоятелен, свой план:

- **Этап 2 — ⑥ Живой дашборд статуса** (`render_status.py`, реюз understanding-map render_map; событийная регенерация Stop/curate + auto-refresh HTML; `Claude/СТАТУС.html`). План: `docs/superpowers/plans/2026-07-XX-project-memory-dashboard.md`.
- **Этап 3 — ⑤ Реакция на жалобы** (маркеры недовольства в `project_context.ps1` → стоп-сигнал; паттерн grilling-detector).
- **Этап 4 — ④ Опц. файлы** (`РЕШЕНИЯ.md`, `ГРАБЛИ.md` — создаются по потребности, не bootstrap).

## Self-Review (coverage vs спека)

- ① доставка → Task 2+3 ✓; ② гейт → Task 4 ✓; ③ КОНТЕКСТ+роль-мостик → Task 1 ✓;
  регистрация/доки/ревью → Task 5 ✓. ④⑤⑥ → следующие этапы (явно отложены) ✓.
- Global Constraints (кодировка/no-op/инжекция-раз/exit-коды) — в каждой хук-задаче ✓.
- Открытый вопрос спеки «куда влить гейт» → решён: отдельный project_gate.ps1 (чистота > экономия 180мс на мутациях) ✓.

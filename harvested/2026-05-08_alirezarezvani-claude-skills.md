# alirezarezvani/claude-skills

**URL:** https://github.com/alirezarezvani/claude-skills
**License:** MIT (LICENSE file present, 2025 Alireza Rezvani)
**Активность:** last push 2026-05-06, 14 102 stars, 1 893 forks, 22 open issues, активно поддерживается с 2025-10-19
**Статус:** **partially adopted** — методологические идеи берём, скиллы целиком — нет.

## Что делает

Большая коллекция скиллов и агентов для Claude Code (а также Codex, Gemini CLI, Cursor и 8 других AI coding tools). 235 скиллов + 28 агентов + 27 slash-команд + 305 Python CLI tools (stdlib-only). Покрывает engineering, marketing, product management, c-level advisory, finance, regulatory/quality (медицина/фарма), business growth.

Архитектура:
- **SKILL.md** с YAML frontmatter, описанием когда применять.
- **Python tools** — детектируют нарушения, выдают JSON-репорты.
- **Sub-agents** для review.
- **Slash commands** для ручного запуска.
- **Pre-commit hooks** для автоматической проверки.

## Почему может быть полезно нам

**Прямой пользы — мало.** Репо нацелен на разработчиков ПО + продуктовый/маркетинговый слой. Нашей аудитории (строительные проектировщики) почти ничего:

- engineering/ — DevOps (docker, helm, terraform), data analysis, llm-ops. Не наш домен.
- marketing/ (43 скилла), c-level/ (28), product-team/, finance/, business-growth/ — 0% релевантности.
- ra-qm-team/ — медицина (FDA, MDR), фарма, IT-безопасность (ISO 27001/13485, GDPR). Про СП/ГОСТ/СНиП — нет.

**Косвенной пользы — много.** Это **очень дисциплинированный** репо с проработанной методологией. Из неё стоит взять идеи, не код.

## Найденные паттерны для адаптации

### 1. Confidence tagging 🟢🟡🔴

В их `Communication standard`:
> Confidence tagging — 🟢 verified / 🟡 medium / 🔴 assumed

**Применение у нас:** в `agents/auditor.md` каждое замечание тегируется уровнем уверенности. Сейчас наш auditor выдаёт только PASS/FAIL — теряется тонкость. С тегами:
- 🟢 — проверено фактом (например, индекс Hisense сверен с каталогом).
- 🟡 — проверено косвенно (например, расход воздуха consistent между sheet'ами).
- 🔴 — допущение, требует ручного контроля.

### 2. Context-first перед AskUserQuestion

Из их `SKILL.md template`:
> ## Before Starting
> **Check for context first:** If `[domain]-context.md` exists, read it before asking questions. Use that context and only ask for information not already covered.

**Применение у нас:** в `agents/designer.md` добавить блок «прежде чем спрашивать пользователя — проверь, нет ли в текущем рабочем каталоге `project-context.md` (или подобного файла с описанием объекта)». Это **сокращает количество вопросов** на повторяющихся задачах в одном проекте.

### 3. Proactive Triggers секция в скиллах

Из их шаблона:
> ## Proactive Triggers
> Surface these issues WITHOUT being asked when you notice them in context:
> - [Trigger 1: specific condition → what to flag]

**Применение у нас:** в `agents/designer.md` явно перечислить «без запроса флагуй: «здание называется кинопарк, а тип объекта в задаче — больница»; «ТЗ нет, расчётов нет — без них продолжать нельзя»; «индексы оборудования даются по памяти — пометь [ПРОВЕРИТЬ ПО КАТАЛОГУ]»».

Это формализует уроки из кейса VRF Кинопарка.

### 4. Multi-mode скиллы

Из их шаблона:
> ## How This Skill Works
> ### Mode 1: Build from Scratch
> ### Mode 2: Optimize Existing
> ### Mode 3: [Situation-Specific]

**Применение у нас:** в `skills/word-helper`, `pdf-helper`, `excel-helper` явно разделить «генерация с нуля» vs «правки существующего» vs «копия шаблона + replace placeholders». Третий mode — урок из кейса ПНР Вентиляции.

### 5. Quality Checklist для новых скиллов

Из `SKILL-AUTHORING-STANDARD.md`:
> ### Structure
> - [ ] YAML frontmatter с name, description, version
> - [ ] Practitioner voice — "You are an expert in X"
> - [ ] Context-first
> - [ ] Multi-mode
> - [ ] SKILL.md ≤10KB — heavy content в references/
> ### Content
> - [ ] Action-oriented
> - [ ] Opinionated
> - [ ] Tables, checklists, examples
> ### Integration
> - [ ] Related Skills с WHEN/NOT disambiguation

**Применение у нас:** добавить `SKILL-AUTHORING-STANDARD.md` в claude-base (своими словами, переформулировано) — единый стандарт для всех будущих скиллов.

### 6. karpathy-coder тулинг (для разработки плагинов)

У них 4 Python-tool'a, которые **детектируют нарушения** принципов Karpathy:
- `complexity_checker.py` — cyclomatic complexity, class density, nesting.
- `diff_surgeon.py` — flag drive-by refactors, comment-only changes, quote swaps.
- `assumption_linter.py` — flag «just», «obviously», «should work» в плане.
- `goal_verifier.py` — score плана за качество критериев успеха.

**Применение у нас:** для **разработки плагинов Revit/AutoCAD** на рабочем ПК эти тулы могут реально помогать. Установить как отдельный установленный плагин Claude Code:

```
/plugin install karpathy-coder@claude-code-skills
```

Это **не наша адаптация**, а просто **использование официального плагина** через marketplace. Не нарушает наш harvest-workflow — мы не копируем код в claude-base.

Для строительных задач — не применимо, тулы не работают на DOCX/PDF/XLSX.

## Ограничения / риски

### Прямые риски

- **«232+ скиллов» — anti-pattern**. У нас уже было 17 скиллов, и это оказалось слишком много (см. кейсы Волны 11). Их 232 — почти гарантированно куча неработающих и дублирующихся. Не пытаться адаптировать «всё что есть».
- **Маркетинговый налёт.** «SkillCheck Validated» бэдж ведёт на их же сайт `getskillcheck.com` — не независимая валидация. README говорит «5,200+ stars», API показывает 14 102 — README устарел или взрывной рост (часто признак промо).
- **Cross-tool compatibility (Codex/Cursor/Gemini)** — реализована через `scripts/convert.sh`, который переименовывает файлы под формат конкретного агента. Содержательно — те же скиллы.

### Лицензионные

- MIT — copyright Alireza Rezvani 2025.
- При прямой адаптации кода — должны сохранить attribution в `LICENSE.NOTICE` файле claude-base.
- При адаптации **идей** (что мы делаем) — attribution желателен, но юридически не обязателен. В нашем случае — упомянем источник в каждом адаптированном файле.

## Тест в sandbox

**Не проводился.** Изучение по WebFetch / `gh api` без клонирования. Адаптация идей не требует запуска кода.

Если в будущем захотим **установить `karpathy-coder` как Claude Code плагин** через marketplace — это безопасно (через официальный механизм Anthropic), не наш harvest-flow.

## Решение

**Не adopt** как сами скиллы или код. Их 232 скилла — не для наших задач.

**Частичный adopt — методологические идеи:**

1. **Confidence tagging 🟢🟡🔴** → добавить в `agents/auditor.md` (после ≥1 реальной задачи через v2 архитектуру, чтобы понять как именно использовать).
2. **Proactive Triggers** в `agents/designer.md` — формализовать уроки из VRF Кинопарка и ПНР Вентиляции.
3. **Multi-mode** в `skills/*-helper/SKILL.md` — Build / Optimize / Template-replace.
4. **Quality Checklist** для будущих скиллов — переписать `SKILL-AUTHORING-STANDARD.md` своими словами в claude-base.

**Дисциплина применения:** не делать всё сразу. Каждое из 4 изменений — отдельный коммит после **реального теста**, который покажет нужно ли это. Иначе повторим anti-pattern «много правил наперёд».

## Attribution

При адаптации каждого паттерна — упомянуть в комментарии файла:
> Адаптировано из [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT). Идея переформулирована своими словами под нашу базу.

## Приоритет

1. **Confidence tagging** — высокий (улучшает наш auditor по конкретной слабости).
2. **Multi-mode для документных скиллов** — средний (закрывает урок ПНР Вентиляции про «копия шаблона + replace»).
3. **Proactive Triggers** — средний (нужно сформулировать через анализ ≥3 кейсов).
4. **SKILL-AUTHORING-STANDARD** — низкий (полезно когда будем создавать новые скиллы; пока не создаём).

karpathy-coder как plugin — отдельная история, не блокирует.

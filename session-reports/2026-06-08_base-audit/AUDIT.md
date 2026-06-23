# Генеральный аудит claude-base — 2026-06-08

> Workflow `claude-base-deep-audit`: 93 агента, 3.26M токенов, ~14 мин.
> 84 читателя (16 агентов + 18 скиллов + 3 команды + 47 memory) → 3 Opus-аналитика → adversarial-verify → синтез.
> Run ID: wf_bea9a53c-8ab.

## Фаза 1 (до Workflow) — гигиена верхнего уровня: ЗАКРЫТА
- Удалён `.feedback-config.json.bak` (plaintext PAT, не в git — утечки не было).
- Удалены `CLAUDE.md.PRE_REFACTOR_BAK` (71КБ), `_sandbox/` (40МБ), `cache/debug/telemetry` (~1МБ). Освобождено ~41МБ.
- `reference_mcp.md` 10→9; дубль `team_subscriptions` слит; 3 orphans в каталог.
- Case-fix git: `memory/memory.md` → `MEMORY.md` (единственный на 449 файлов).

---

## ГЛАВНЫЙ ДИАГНОЗ: почему агенты не вызывались

**Все 16 агентов функционально уникальны — 0 на удаление, 0 на мёрж.** Проблема НЕ в содержании (11/16 выровнены по шаблону), а в **маршрутизации**:

### Root causes
1. **Маршрутизация идёт по frontmatter-полю `description`, а там резюме роли, не триггеры.** У 13/16 — «кто он» («Доменный агент проектирования…»), а не «когда меня звать». Пользователь пишет «подбери VRF» / «посчитай воздухообмен» — совпадения нет, агент невидим. **Единая первопричина.**
2. **Архитектура `main→domain→auditor` задана прозой в CLAUDE.md без enforcement.** Исполняется «по памяти»; под давлением скорости main Claude делает inline. Правило 7 (нормы только через norm-lookup) нарушается так же.
3. **Цепочка ревьюеров мертва с обоих концов.** Ревьюеры (auditor, word-checker, pdf-reviewer, excel-validator, audit-rd-section, rd-coordinator, norm-lookup) — 2-й уровень после генератора, но генераторы сами не вызываются. Входящих ссылок нет.
4. **Триггеры на профжаргоне** («нормоконтроль», «СПДС», «УПД», «АОСР», «Мосгосэкспертиза», «ВОР», «исх. №»). Живая речь короче: «проверь раздел ОВ», «разбери накладную», «акт на скрытые работы».
5. **Конкуренция с общим `auditor` и inline-путём** main Claude. У узких ревьюеров нет «When NOT to invoke» vs auditor.
6. **Редкость домена** (НЕ чинится правкой description): id-engineer, expertiza-responder, pyrevit-engineer — объективно редкие события. Не путать «не звали из-за жаргона» (чинится) и «не звали из-за редкости» (не чинится → решать после 20-30 сессий).
7. **Broken refs и отсутствующие конфиги** дают мгновенный failure: `.library-config.json`, `Documents/norms/`, хардкод-пути шаблонов (КП/ИД) не существуют → norm-lookup/kp-writer/id-engineer тормозят.

### Fixes (по приоритету)
1. **ПРАВКА №1: переписать `description` ВСЕХ 16 агентов** — начинать с 5-7 живых фраз, потом строка про роль. Без неё остальное бесполезно.
2. **Закрепить spawn ревьюера детерминированно:** (а) PostToolUse-hook на запись .docx/.xlsx/.pdf; либо (б) явный шаг spawn reviewer в After completion каждого генератора.
3. **Дать ревьюерам прямые пользовательские триггеры** (убрать зависимость от мёртвого 1-го уровня).
4. **Добавить всем ревьюерам «When NOT to invoke»** с границей vs auditor.
5. **Довести 5 недо-шаблонных агентов** (designer, auditor, excel-validator, pdf-reviewer, word-checker) до _TEMPLATE.md v1.0.
6. **Починить broken refs и конфиги;** добавить FACTS.md в Required reading где нет.
7. **Убрать `[PLANNED]` у kp-writer** в сметчик.md/снабженец.md (~стр.56) — файл существует, метка = мёртвая зона.
8. **Зарегистрировать named chains** (pto→снабженец→сметчик, designer→audit-rd-section→auditor) или сделать агентов самодостаточными.
9. **Сделать Правило 7 императивным** с примерами запрещённого.

---

## СКИЛЛЫ: 0 delete, 16 fix, 2 keep (acad-recreation, pnr-vor-helper)
Два системных дефекта:
1. **16/18 нарушают 3-слойный стандарт — нет `tools/`** (10 без слоя, 5 держат скрипты в `scripts/`, 1 в корне).
2. **~25+ битых ссылок.** Худшие: `spec-writer` (7/8 wikilinks мертвы — правила S/J/I/R висят без файлов), `karpathy-guidelines` (6, в т.ч. 3 несуществующих агента code-reviewer/lisp-improver/brainstorm-partner), `upd-parser` (4).
- Обезличивание перед push: <организация> / ИНН 7724915051 / шифр R-090226727A в `word-helper`, `upd-parser`, `yandex-disk-uploader`, `spec-writer`, `cad-reader`, `pnr-vor-helper`.

## КОМАНДЫ: все 3 здоровы (`/format`, `/harvest`, `/sync-base`) — действий нет.

## ПАМЯТЬ: ~26/47 без действий. Adversarial ОТКЛОНИЛ все 5 archive/merge
(2026-05-07-pnr-ventilation, 2026-05-13_harvest-workflow, 2026-05-15_extras, 2026-05-18_lesson-15, role_detection — у каждого уникальный неабсорбированный контент → keep/fix). Реальные действия — точечные:
- **`~/Desktop/<организация>_audit_report.docx` битой ссылкой в 5 файлах разом** (backlog_promptfoo, backlog_teammate, project_designer_decomposition, rd_plugins_test_plan, chains-pattern) — почистить одним проходом.
- **GPL-конфликт:** reference_licenses_k7.md (override) vs необновлённый harvest_workflow.md.
- **reference_pyrevit_k7.md осиротел** (in_index=false) → добавить в MEMORY.md.
- reference_mcp: битый `bin/diff-pdf/diff-pdf.exe`, добавить exa в опц. таблицу.
- sessions_policy.md: добавить в индекс + строка «MCP: X/8»→«X/9».
- archive_v1.md: путь к v1-папке устарел.
- профанити/feedback_webfetch: encoding-артефакты («в†»→«→»), дублированные секции.
- Несколько wiki-links с дефисами вместо подчёркиваний.

---

## РЕШЕНИЯ ПОЛЬЗОВАТЕЛЯ (needs_user_decision)
1. **Enforcement spawn ревьюера:** PostToolUse-hook (жёстко, меняет харнесс) ИЛИ правка After completion (мягко, «по памяти»)?
2. **Объём правки агентов:** все 16 description за раз (Workflow) ИЛИ инкрементально?
3. **id-engineer / pyrevit-engineer / expertiza-responder:** оставить как редкие ИЛИ архив? Решать ТОЛЬКО после 20-30 сессий с исправленными триггерами.
4. **scripts/→tools/ у 5 скиллов:** переименовать с правкой sys.path ИЛИ оставить scripts/ как задекларированный слой 3? (backlog_tools_layer_migration).
5. **Битые feedback-заметки spec-writer/upd-parser:** создать реальные memory/*.md ИЛИ заинлайнить правила S/J/I/R в SKILL.md?
6. **Обезличивание перед push:** заменить <организация>/ИНН/шифр на плейсхолдеры сейчас ИЛИ в момент коммита?

# Session report — Workflow-аудит базы + полное обезличивание

**Дата:** 2026-06-23
**Машина:** ноутбук (hostname DANIIL→DANIIL-LAPTOP, egress Дубай)
**Метод:** Workflow read-only аудит (30 агентов, opus аудит+синтез / sonnet верификация, 1.9M токенов) → реестр → детерминированная починка CRITICAL.

## Сделано — CRITICAL обезличивание (БЛОКЕР раздачи) ЗАКРЫТО
Workflow нашёл системный изъян, пропущенный прошлыми сессиями: **реальные идентификаторы в pushed-базе** (нарушение правила 6).
- Имя организации + смежная фирма + RGB-палитра + extension → плейсхолдеры (`<организация>` и т.д.).
- Коды объектов/заказчиков + шифр чертежа + реквизиты договоров → плейсхолдеры.
- `.py`-тесты обезличены на валидные значения (`TEST-1`); regression OK.
- **Бинарный бланк с реквизитами (адрес/ИНН/ОГРН) убран из git** + `.gitignore` (`skills/word-helper/templates/*.docx`).
- 2 reference-файла + 3 папки `session-reports/` с «k7» переименованы.
- **Проверка: `git grep` идентификаторов по ВСЕЙ базе = 0**, verify-base 23/23.
- Коммиты: `e40c4d1`, `eec9143`. (Заметка: часть правок ушла фоном в auto-sync — git-хуки коммитят сами.)

## ОСТАЁТСЯ из реестра (41 находка; CRITICAL закрыты, ниже — хвост)

### MAJOR (13) — структурная гигиена
1. **shared→auto битые ссылки (раздаются битыми у всех ПК):** мигрировать в `memory/` обезличенные `playwright_mcp_pin_version.md`, `web_access_survey_2026_06.md`, `feedback_user_rules_docs_cascade.md` (auto→shared); привести ссылки к snake_case. `muzey_r4_viv_pdf_assembly` — НЕ мигрировать (проектная), в `id-tom-priemka` заменить на обезличенную формулировку. `id-engineer.md:399` `[[id-volume-graph]]` — сделать условной (блок pto).
2. **CLAUDE.md:157** → `feedback_user_rules_docs_cascade.md` битая (файл только в auto-memory).
3. **2 forward-link:** `upd-parser` `[[feedback-upd-pdf-parsing]]`, `local-video-digest` `[[reference_ffmpeg_video_frames]]` — создать заметки или убрать.
4. **Эталон MCP:** счётчик «/9»→«/11» в `reference_agents.md:50`, `role_detection.md:18`, `sessions_policy.md:69`.
5. **harvest стейл:** порядок источников в `harvest_proactive.md`/`2026-05-13` под действующий `commands/harvest.md`.
6. **designer.md:** обещает .docx/.xlsx, но во frontmatter нет word/excel-MCP — добавить MCP (по образцу pto-engineer) ИЛИ переписать на python-путь.
7. **block-behavior.md** дублирует 5 принципов Karpathy — @import в CLAUDE.md ИЛИ переписать как companion с примерами.
8. **pd-tep-extractor** Layer-3: вынести пайплайн в `scripts/`.
9. **doc-finder/supplier-due-diligence:** свернуть near-verbatim веб-лестницу до ссылки на `ru-gov-access` + `feedback_web_direct_access` (канон).
10. **harvest_workflow ↔ harvest_proactive:** дубль «Фильтр кандидатов» — вынести в один.

### MINOR (16) — гигиена
rd-coordinator секция «When NOT to invoke»; letter-writer без Bash; excel-helper стабильный Python→scripts/; orphan-скиллы (local-video-digest, id-tom-priemka←id-engineer, acad-recreation) — указатели из агентов; cad-reader/yandex-disk-uploader русские триггеры; domain-grilling tooling вне папки; индекс MEMORY.md неполон (53 файла, ~33 в каталоге); feedback_manual_procedure_verbatim сирота; webfetch_reality_check/web_doc_fetch помечены «ПОГЛОЩЕНО»; verify-claude-base.ps1 усилить (JSON-валидация, count MCP==11, agents==16, Test-Path memory, **grep-гард на идентификаторы перед push**).

### Прочее
- **Граф базы** — пересобрать `/graphify --update` (labels содержали идентификаторы; на обезличенной базе пересобрать). Устарел (staleness-хук).
- **local-osint-recon** — оформить (Пассив + Gobuster, источник — каталог на Desktop). См. [[osint_arsenal_local]].

## Уроки
- **Workflow-аудит окупился:** нашёл блокер обезличивания (имя организации в ~100 файлах), который не видели sync-base/verify и прошлые сессии. Рекомендация реестра: добавить **grep-гард на идентификаторы в verify-claude-base.ps1** — чтобы ловить автоматически перед push.
- Обезличивание делается детерминированным скриптом (словарь замен) по ВСЕМ расширениям, не только .md; .gitignore (без расширения) и бинарники — отдельно.

## ДОВОДКА ВЫПОЛНЕНА (2026-06-23, 15 коммитов от cb30c12)

**CRITICAL — закрыто полностью:**
- Обезличены орг/объекты/шифры (git grep = 0), бинарный бланк убран из git.
- **+ ФИО/email/домен/hostname** (Ivan Fesenko, Поляков, Deliseev, k-7.tech, DELISEEV-PC) —
  обезличены в методбазе + scripts-текст (70+ файлов). Намеренно оставлен `daniileliseev1337/claude-base-feedback`
  в github_repo-конфиге scripts (функциональный owner feedback-канала).
- **verify-base PII-гард [7]** (Select-String регистронезависимо) — СРАЗУ окупился: нашёл ФИО/email,
  что регистрозависимый grep и 30-агентный Workflow пропустили; ловит даже свежие auto-sync файлы.

**MAJOR — ~12/13 закрыто:** все битые ссылки (0 в shared), shared→auto миграция (3 заметки),
эталон MCP /9→/11, designer.md word/excel-MCP, block-behavior→companion, веб-лестница дубли свёрнуты,
harvest стейл. Открыт #8 (pd-tep Layer-3 → scripts — разработка).

**MINOR — ключевые:** verify-base [7]+[8] (PII-гард + эталоны MCP==11/agents==16/JSON), letter-writer Bash,
cad-reader RU-триггеры, id-engineer→id-tom-priemka handoff, пометки «ПОГЛОЩЕНО».

**ОСТАЁТСЯ (хвост):**
- **Граф базы** — пересобрать (79 структурных файлов изменено, навигатор устарел; крупная операция субагентов).
- pd-tep/excel-helper Layer-3 (вынос Python в scripts/) — разработка.
- backlog-статусы (rd_plugins_test_plan, 3 backlog) — нужно решение пользователя (active→archived?).
- Мелочь: MEMORY.md индекс полнота, rd-coordinator секция «When NOT» структурно, orphan acad-recreation/local-video указатели.
- verify-base.ps1 паттерны гарда содержат «К-7» как сигнатуры — git grep их видит (не PII, детектор); при желании обфусцировать.

# Session report — secret-tools внедрение + tooling (handoff → ИД)

**Дата:** 2026-06-08 · **Host:** DANIILPC (hub, MAX x5, отдел Проектирования)

## TL;DR
- Внедрены и **розданы команде** 5 «секретных» инструментов; Codex удалён; памятка команде → PDF; инсталлер починен; плагины почищены; graphify раздан всем.
- Всё запушено в `origin/main` (claude-base + claude-lite-instaler), **AHEAD=0**, working tree чист.
- **Осталось (next-сессия): разработка ИД** (приоритет #1) — исходники собраны.

## Что сделано

### Secret-tools (harvest → внедрение → раздача)
Оценены 6 (метаданные через GitHub API): r.jina.ai, graphify (62k★), playwright (33k★), firecrawl (6.5k★), perplexity (2.3k★), glif (157★, archived).
- **playwright-mcp** → **Тир-0 всем**: добавлен в `mcp-manifest.json` (method `npx`) + поддержка `npx` в `setup-extras.ps1`. DryRun-verified, ✓Connected.
- **firecrawl-mcp** → активирован с ключом (локально в `.claude.json`, вне claude-base). Self-host на hub (Docker) — отложен.
- **graphify** → `uv tool install "graphifyy[openai]"`; skill `/graphify` + references + CLAUDE.md-регистрация **розданы всем через git**; offline код-граф работает (демо scripts: 46 узлов, 0 токенов).
- **r.jina.ai** → правило веб-доступа (память `web_access_r_jina_fallback`); ключ `JINA_API_KEY` в env.
- **Ollama** → установлен (winget), `qwen2.5:7b` скачана. **НО 7B не грузится на 16GB RAM** (свободно 2.2) — docs-граф упёрся в железо. Связка graphify↔Ollama технически настроена (openai-пакет, `--backend=ollama`), но llama-server падает по RAM.
- **glif** → archived → опциональный в sync-base.

### Решения распространения
- Раздача ключей: «**сначала бесключевые**» (Тир-0 без ключей всем; механизм ключей — отдельно).
- Тир-0 (playwright) → manifest/setup-extras. Опциональные (graphify CLI, Ollama, glif) → sync-base.
- Firecrawl команде → **self-host на hub** (Docker, `FIRECRAWL_API_URL`) — отложено.
- Ключи на будущее → **encrypted-vault** (AES в git + пароль вне репо + DPAPI) — не реализован.

### Прочее
- **Codex удалён** (npm uninstall + из sync-base).
- **Памятка команде → PDF**: `Памятка-<организация>-Claude.pdf` (cwd ПаПочка) — 7 разделов (агенты/скиллы/команды + системные + новые инструменты + установка). Конвертер `_md2docx.py` (нет pandoc) — кандидат в word-helper/tools.
- **Инсталлер** (claude-lite-instaler) починен по фидбэку с рабочего ПК (Skudriavtsev): PATH-fix (`Install-ClaudeCode` — официальный installer не добавлял `.local/bin` в PATH → Stage 6/8 падали), убран `2>&1` (`Install-VSCodeExt` — node DeprecationWarning → NativeCommandError), число серверов 9-10→11-12. Запушен.
- **Плагины почищены**: удалён кэш 5 нерелевантных (marketing/finance/c-level/business-growth/product), реестр `installed_plugins.json` синхронизирован (backup). Осталось: superpowers, claude-md-management (enabled) + engineering-skills, engineering-advanced (disabled, оставлены).
- **sync-base** = единая точка: проверяет playwright(extras)/graphify/Ollama/Exa/Inkscape + git pull. Коллеге достаточно `/sync-base`.
- Анализ LLM/Ollama (Explore): генеративка в проде = SD+LaMa (image-text-replace), Claude через MCP. Ollama для docs упёрся в RAM.

## Коммиты origin/main
- **claude-base**: `8a7b41f`,`9d3a3fe` (playwright manifest+setup-extras), `35ec857` (codex removal), `dd8c5fb` (graphify skill), `622460c` (sync-base единая точка).
- **claude-lite-instaler**: `5d5682c` (PATH + 2>&1 fixes).

## Файлы
- Памятка: `cwd ПаПочка/Памятка-<организация>-Claude.{pdf,docx,md}` + `_md2docx.py`.
- ИД-исходники: `~/.claude/work/2026-06-08_id-session/sources/feedback/` — **18 файлов** + `INDEX.md` (work/ заигнорена, **необезличено**).

## Открытые хвосты
- **docs-граф graphify**: Ollama 7B не тянет (16GB) → варианты `qwen2.5:3b` / `GEMINI_API_KEY` (не-конфид.) / мощнее ПК.
- **firecrawl self-host** (Docker на hub) — инфра-этап.
- **encrypted-vault** для ключей — когда понадобятся cloud/платные.
- **Тест на рабочем ПК**: чистый consumer-flow (`git pull` → `setup-extras` → `/sync-base`).
- Памятка `reference_id_assembly_method` (разд.18-26) — локально, **путь не задан** (уточнить у пользователя).

---

## ИД-разработка (NEXT, приоритет #1, «безумно важно»)

### Задача
Формализовать **методику сборки/проверки тома ИД** инженерных систем → прокачать агент **id-engineer**.

### Исходники (собраны)
- `~/.claude/work/2026-06-08_id-session/sources/feedback/` — **18 feedback-файлов** (этапы 1-3 + грабли), `INDEX.md` = точка входа (карта по этапам).
- `~/.claude/memory/backlog_id_assembly_session.md` — закладка кейса.
- Методичка `reference_id_assembly_method` (разд.18-26) — локально на машине автора, **путь уточнить**.

### 3 этапа методики
1. **Переформат актов ВСО** под новую шапку (частью в `reference_docx_table_reformat`).
2. **Реестр замечаний** техзаказчика/технадзора (№/суть/решение/статус/тип; категоризация наши/не-наши).
3. **Реверс-инжиниринг устройства тома** (ядро): комплекты вокруг актов + 3 прошивки; типы АОСР/АОМР/**АОУСИТО**; цепочка журнал→акт→материалы/Реестр→паспорта→схемы→ВСО/ПВ; нумерация = 2 стр PDF; метод Workflow-картирования эталонного тома.

### Грабли (учесть)
word `search_and_replace` на таблицах (anti-patterns A3.8 — N-кратное задвоение), docx-трансформер (`reference_docx_table_reformat`).

### Подход (инсайт пользователя 08.06): граф зависимостей — ядро решения
ИД по природе = **паутина зависимостей** (журнал→акт→материалы→паспорта→схемы→ВСО; что от чего тянется, зачем, что делать). Цель — построить **граф устройства тома** (узлы = типы документов/актов, рёбра = цепочки/зависимости): **редактируемый + queryable + понятный любому Claude**. Сильнее «простыни» в промпте — `id-engineer` query'ит граф («что нужно к АОСР на гидроизоляцию»).

**Важная тонкость graphify:** он ИЗВЛЕКАЕТ граф из существующих файлов, а не выводит методологию. «Зачем/как/что делать» синтезируем МЫ из корпуса.

**Развилка (определяет и железо):**
- **(A) Моделируем граф методики** из feedback-корпуса+методички в graphify-формате (`graph.json`) — **облачный Claude, железо не лимит** (DANIILPC ок). graphify даёт формат + query/path/explain + визуал.
- **(B) Авто-извлечение** из эталонного тома (PDF) через graphify+LLM — нужен сильный бэкенд (Gemini/Claude; Ollama 7B на 16 ГБ не тянет → GPU-ПК).
- Вероятно **гибрид**: модель методики (A) → сверка с реальным томом (B).

### Цель ИД-сессии (уточнена)
Не просто «прокачать промпт id-engineer», а **построить граф устройства тома ИД (модель зависимостей) + научить id-engineer его query'ить**.

### Следующий шаг
Прочитать `INDEX.md` + ключевые файлы корпуса (cascade) → синтезировать **устройство тома как граф зависимостей** (подход A) → прокачать `id-engineer` (query графа) → ревью word-checker/auditor. **Корпус необезличен** — обезличить перед переносом в `agents/`.

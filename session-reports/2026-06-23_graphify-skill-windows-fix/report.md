# Сессия 2026-06-23 — graphify SKILL под Windows + пересборка графа + сверка реестра

Машина: DANIIL-LAPTOP (хаб, .developer-marker есть; иностранный egress Дубай). MAX x20.
Продолжение «доводки claude-base». Старт HEAD=0689945, финал HEAD=5b4fed4 (+ фоновые auto-sync).

## Сделано

### #1 — graphify-скилл под Windows-грабли + пересборка графа (главное)

**Закодированы 5 граблей в `skills/graphify/tools/graph_update_win.py`** (новый слой-3 скилла,
раньше tools/ у graphify не было). Subcommands `detect`/`merge`/`finalize`:
- грабля 1 (path): `.graphify_root` хранит POSIX `/c/Users/...` → Windows-Python видит 0 файлов
  → всё «deleted». `detect` коэрсит `/c/`→`C:/`.
- грабля 2 (encoding): модуль форсит utf-8 stdout на импорте.
- грабля 3 (source_file): субагенты иногда кладут путь в `source_location`, `source_file:null`.
  `merge` восстанавливает; + ужесточён промпт субагента в `extraction-spec.md` (профилактика у источника).
- грабля 4 (КОРЕНЬ, выяснено): `graphify.build.build_merge` делает `build(старое+новое)` и
  **потом** прунит по `source_file` из ОБЪЕДИНЁННОГО графа → `prune_sources=[изменённый]` удаляет
  и свежеизвлечённые узлы. Поэтому документированный flow update.md (`prune=deleted+changed`)
  теряет переэкстракцию изменённых файлов — отсюда ручная пересборка прошлой сессии. `merge` НЕ
  использует build_merge: ручной prune ТОЛЬКО старого графа → combine new-first → dedup.
- грабля 5 (commit-stamp + порядок): голый Step 4 `to_json` не штамповал `built_at_commit` →
  staleness-хук оставался красным. `finalize` штампует HEAD; Step 4 в SKILL.md тоже теперь
  штампует (общее улучшение). КЛЮЧЕВОЕ — **порядок коммита**: структурные правки → `HEAD` →
  пересборка со штампом этого HEAD → коммит ТОЛЬКО `graphify-out/` (не структурный путь, не реди-стейлит).

**Правки скилла:** `tools/graph_update_win.py` (нов.), `references/update.md` (Windows-callout +
порядок коммита + generic-flow сохранён), `references/extraction-spec.md` (source_file/source_location),
`SKILL.md` (Step 4 built_at_commit, указатель на helper, секция Tools).

**Тесты helper'а:** юнит (native_root/relativize/normalize_extraction) + sandbox-цепочка
detect→merge→finalize, в т.ч. net-loss guard и `--force`. Все PASSED.

**Пересборка графа:** 18 changed (6 .py AST + 12 .md). Субагент экстракции — **sonnet ×1**
(выбор пользователя). Экстракция чистая (0 null source_file, 0 путей в source_location, 0 абсолютных —
ужесточённый промпт сработал). Граф **934 → 970 узлов** (1064 ребра, 163 сообщества),
built_at_commit=174214c, commit 5b4fed4. Верификация: 0 orphan-рёбер, 0 абсолютных, 1 missing
(`enum` — известный безвредный stdlib AST-артефакт). **Staleness self-check
`git diff 174214c HEAD -- <структурные>` ПУСТ → граф НЕ устареет** (грабля 5 закрыта end-to-end).

Релейбл 163 сообществ пропущен намеренно (токен-дисциплина; граф запрашивается по graph.json, не по
именам в отчёте) — отчёт с placeholder «Community N».

### #2 — сверка реестра 41 находки на остаточные MINOR

После обеих доводочных сессий (obezlichivanie + graf-dovodka) закрыто: все 13 MAJOR (включая #8
pd-tep/excel-helper Layer-3→tools/), backlog-статусы, MEMORY.md +21, rd-coordinator When-NOT,
orphan-указатели, verify-base PII-гард.

**Остаточные MINOR (5, некритичные, требуют новых структурных правок → батчить в отдельную сессию
с одной пересборкой в конце):**
1. `yandex-disk-uploader` — нет RU-триггеров (cad-reader получил).
2. `domain-grilling` — tooling (reminder.txt/triggers.txt/хук grilling-detector.ps1) не co-located.
3. `feedback_manual_procedure_verbatim` — сирота (только индекс ссылается).
4. `local-osint-recon` — скилл не создан (сырьё на Desktop osint-arsenal-catalog).
5. `verify-base.ps1` — сигнатуры «К-7» PII-гарда видны git grep (косметика, не PII).

## Грабли/уроки
- build_merge прунит и НОВЫЕ узлы — фундаментальная причина, почему generic update.md flow ломает
  инкрементальную пересборку изменённых файлов. Закодировано в helper.
- Bash-heredoc в этом окружении схлопывает `\\`→`\` — литеральные бэкслеши писать через `chr(92)`
  или Write-tool, не heredoc.
- Фоновый auto-sync коммитит правки сам (HEAD двигается в фоне) — built_at_commit брать ПОСЛЕ того,
  как auto-sync закоммитил структурное.
- project-MEMORY.md (auto-memory индекс) на диске в double-encoded mojibake — точечно не править.

## Источники
- `skills/graphify/{SKILL.md,references/update.md,references/extraction-spec.md}`,
  `scripts/graph-staleness-check.ps1`, пакет `graphifyy` (build_merge/to_json исходники).
- Память: `graphify_update_windows_traps.md` (обновлена: ручной→helper + корень грабли 4 + порядок коммита).

## Артефакты
- `skills/graphify/tools/graph_update_win.py` (нов.), правки 3 файлов скилла.
- Граф `graphify-out/graph.json` (970 узлов), commit 5b4fed4.

## Остаётся
- 5 MINOR выше (батч + 1 пересборка).
- 1 узел графа без source_file (`enum`, безвреден).

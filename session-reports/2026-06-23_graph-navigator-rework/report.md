# Сессия 2026-06-23 — переработка графа базы в достоверный навигатор

Машина: DANIIL-LAPTOP (хаб). Продолжение сессии graphify-skill-windows-fix. Пользователь
поставил вопрос: граф задуман как достоверный навигатор Claude по базе (агенты/скиллы/правила/
память), но им НЕ пользуются — «где-то написано не доверять и пропускать». План утверждён
(`plans/eager-forging-forest.md`), реализованы все 3 фазы.

## Диагноз (подтверждён исследованием)
1. Свежесть хрупкая/хаб-онли/ручная; родной `graphify hook install` post-commit = только КОД,
   для doc-базы бесполезен.
2. Конфликт инструкций: CLAUDE.md:267 «query первым» vs CLAUDE.md:268 + staleness-хук
   «устаревший врёт / не доверять». Защита побеждала → греп.
3. Трение query: ручной vocab-ритуал (references/query.md), без кросс-языка.
4. Узкий триггер (только явный «вопрос об устройстве базы»).
5. Дефект качества: LLM-субагенты фрагментировали кросс-ссылки в concept-узлы
   («norm-lookup agent (referenced by designer)») вместо рёбер — рвало обход.

Калибровка: descriptions агентов/скиллов уже в каждом system-prompt → роутинг «какой агент»
граф не ускоряет. Ценность — тела памяти/references + паутина связей + «где описано».

## Сделано — 2-слойный навигатор (skeleton-first)

### Фаза A — детерминированный always-fresh скелет (фундамент)
`skills/graphify/tools/skeleton_build.py` (0 LLM-токенов). Канонические узлы
(`agent__/skill__/memory__/rule__/mcp__/chain__/command__/tool__`, кириллица транслитерируется),
рёбра из `[[wikilinks]]` + упоминаний имён + frontmatter + CLAUDE.md-секций + skill→tools.
**Дефект #5 устранён:** упоминание «norm-lookup» в designer.md → реальное ребро
`agent__designer → agent__norm_lookup` (не concept-фрагмент). Итог: 160 узлов / 708 рёбер,
0 orphan, <2с. Грабля парсера: `import yaml` недоступен → fallback не понимал YAML block-scalar
(`description: |`/`>`) → описания терялись; написан yaml-free block-aware парсер (портативно,
yaml на консьюмерах нет). + `references/skeleton.md`.

### Фаза B — query в один вызов
`skills/graphify/tools/graph_query.py`: скорер по name/label/description; **русский матчится
нативно** (описания несут RU-frontmatter с живыми фразами) — vocab-ритуал не нужен. Отдаёт
вход-сущности + 1-hop связи + source_file. Демо: «ответ на замечания экспертизы»→
expertiza-responder, «составить смету КС-2»→сметчик, «подбор оборудования»→designer/pto,
«токен-дисциплина модель субагентов»→rule токен-дисциплина[12]. Грабля: `_clip` резал описание
до 300 симв (триггеры во 2-м абзаце терялись) → поднял до 2000.

### Фаза C — снять конфликт + привычка
- `scripts/graph-staleness-check.ps1` переписан: **SessionStart-хук молча пересобирает скелет,
  если built_at_commit≠HEAD** (0 токенов, <2с) → свежий на каждом ПК; убраны «устаревший врёт /
  не доверять». ASCII-only (PS 5.1/no-BOM устойчивость; первая версия упала на `<` в строке +
  кириллице без BOM).
- `CLAUDE.md` graphify-секция: 2-слойность (скелет-навигатор always-fresh / семантика-обогащение),
  **query-first через graph_query.py** перед чтением тел, истина в source_file.
- `SKILL.md` Tools: добавлены skeleton_build + graph_query.
- `skeleton.json` — gitignored (локальный производный, как graph.html); каждый ПК строит свой.

Семантический слой (graph_update_win.py flow) оставлен как опциональное обогащение (решение
пользователя). Коммиты: 883d6f7 (+ фоновые auto-sync). Хук молчит @ HEAD (скелет свеж).

## Грабли/уроки
- `graphify.build.build_merge` прунит и НОВЫЕ узлы (из прошлой части сессии).
- yaml на консьюмерах может отсутствовать — frontmatter парсить без него.
- PS 5.1 + no-BOM + кириллица + `<` в строке = парс-краш; инфра-хуки писать ASCII-only.
- Свежесть лучше держать через SessionStart-rebuild (0 токенов) чем через нытьё «пересобери».

## Остаётся / follow-up
- **Портативность скелета на консьюмеры без пакета `graphifyy`:** skeleton_build импортирует
  graphify.build/cluster/export. Если у консьюмера нет пакета — хук тихо не пересоберёт, query
  упадёт на committed graph.json. graphify ставится через sync-base, так что обычно ОК; для
  100% — сделать skeleton_build dependency-free (писать node-link стдлибом). #1 hardening.
- 5 MINOR из реестра 41 (yandex-disk RU-триггеры, domain-grilling tooling, сирота
  feedback_manual_procedure_verbatim, local-osint-recon, verify-base «К-7») — батч-сессия.
- Английские описания (graphify-скилл) не матчат RU-запрос — мелочь (CLAUDE.md-правило покрывает).
- Семантический graph.json теперь отстаёт от HEAD (enrichment, по плану ОК; обновить на хабе по желанию).

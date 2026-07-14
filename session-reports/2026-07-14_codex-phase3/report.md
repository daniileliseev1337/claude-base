# Сессия 2026-07-14 · Фаза 3 мульти-LLM: разведка + Эпик 1 реализован

## Что сделано
1. **Веер разведки** (5 субагентов sonnet параллельно) — отчёты в `recon/` рядом, сводка `recon/00-СВОДКА.md`. Топ-находки: корень падения Revit/AutoCAD под Codex = CRLF-баг Python MCP SDK (не кириллица); `[profiles.X]` в config.toml deprecated → отдельные файлы `<name>.config.toml`; плоский AGENTS.md в корне проекта = 4 таргета разом (Copilot default-on, Cursor, Codex-ext, Gemini); hooks.json официален, но в десктопе не исполняется (#21639 + trust-review); `codex exec`/`codex mcp-server`/официальный плагин openai/codex-plugin-cc — оркестрация готова с обеих сторон.
2. **Эпик 1 «Фундамент синка (Гибрид C)»** — brainstorming → спека → план (8 задач) → субагентный конвейер (implementer+reviewer на задачу, sonnet) → финальное ревью → фиксы. **Реализовано полностью, 37/37 тестов:**
   - `codex_sync.py`: чистый `render_all()`, манифест хешей (`.local-state/codex-sync-manifest.json`), подкоманды `check`/`diff`/`sync --force-overwrite`, трёхсторонняя сверка (clean/canon-newer/manual-drift), атомарная запись, junctions в check;
   - хук `codex-autosync.ps1` (PostToolUse Edit|Write → sync, lock) + `codex-drift-check.ps1` (SessionStart после auto-pull, общий lock) — оба в settings.shared.json;
   - golden-master снапшоты (`UPDATE_GOLDEN=1`);
   - `gen_project_agents.py` (project-memory): плоский project-AGENTS.md с маркером собственности + mtime-напоминание в session_start.
   - Done-when 1-5 доказаны живьём (автопуш маркера туда-обратно, дрейф-эскалация, force-сброс).
3. Спека и план — в проекте «Реворк базы»: `docs/superpowers/specs/2026-07-14-epic1-sync-foundation-design.md`, `docs/superpowers/plans/2026-07-14-epic1-sync-foundation.md`.

## Где споткнулись / уроки
- **auto-push-хук перехватывает коммиты** имплементеров generic-сообщениями «auto-sync: ...» (гонка Stop-хука с явным git commit субагента). Историю не переписывали; в диспатчи добавляли инструкцию «не переписывай, фиксируй фактические хеши».
- Ревьюер задачи 2 поймал реальный кросс-задачный Critical (манифест не писался из живого пути) — закрыт по дизайну задачей 3 с доказательством. Потадачные ревью на sonnet стабильно ловили содержательные баги (JSON-экранирование Windows-путей в golden; IndexError на пустом AGENTS.md; гонка хуков; невидимость junctions).
- PowerShell 5.1 пайпы ломают кириллицу в stdin-JSON (тесты хуков — через прямую запись UTF8-байт в stdin процесса); `core.strip()` съедает whitespace-правки (тест-рецепт «пробел в конец» не создаёт дрейфа).
- `session_start.ps1` project-memory — ASCII-only по инварианту файла: новые сообщения на английском.

## Открыто / бэклог
- Смоук десктоп-Codex после эпика (открыть приложение, увидеть правила) — за владельцем.
- Бэклог Minor (не блокирует): докстринг CLI, тесты first-sync-с-дрейфом и частичного force, try/finally в _write_atomic, кириллица в auto-sync.log, двойной warn в diff_cmd, «мёртвые» inputs манифеста.
- AGENTS.md в корне проекта «Реворк базы» сгенерирован, в git проекта НЕ закоммичен (решение владельца).
- Эпики 2-6 — по карте `docs/superpowers/specs/2026-07-14-codex-phase3-roadmap.md`; разведка №1 (CRLF-фикс) — прямой вход Эпика 3.

Коммиты базы: d4bac6b..0712b57 (16, включая фоновые auto-sync). SDD-леджер: `.superpowers/sdd/progress.md`.

## Дополнение (та же сессия, ночь): Эпик 2 реализован
Решение владельца: полная разработка → обкатка → выпуск (реестр в roadmap-доке).
Эпик 2 SDD-конвейером: реестр TARGETS + targets.json; base.toml → managed-блок
(только таблицы, фильтр коллизий, tomllib-гейт exit 4); профили plus/pro файлами
из codex-layer/profiles/ (полный дрейф-контроль); свежая машина; чек-лист
vscode-verify.md. 49/49 тестов. Ревью-волна: Important «битый config.toml вне
блока роняет check» — закрыт фиксом с тестом. Поправка владельца по VS Code:
маршрут = Codex-расширение (тот же ~/.codex), мой Copilot-mcp.json план — в бэклог.
Урок: top-level ключ в managed-блоке в конце TOML-файла прилипает к последней
чужой таблице — эталон ограничен таблицами. Коммиты: b38f800..24802fe.

# Одноразовая инструкция для dev-ноутбука после мержа PR «remote-base-audit»

> Выполнить ОДИН раз на хабе (dev-ПК) после мержа PR с ветки
> `claude/database-phone-access-jkgcfl`. По завершении файл можно удалить
> (или оставить как протокол — отметь галочки).

## 1. Подтянуть и перезапустить
- [ ] Смержить PR в main.
- [ ] Новая сессия Claude Code (auto-pull подтянет main). **Перезапустить Claude Code**
      полностью — hot-reload нет, новые CLAUDE.md/agents подхватятся только после рестарта.

## 2. Личный слой
- [ ] `git -C "$HOME/.claude" status` — если в CLAUDE.md есть незакоммиченные ЛИЧНЫЕ
      правки (бывшая USER EXTENSIONS) — перенести их в `~/.claude/CLAUDE.user.md`
      и откатить локальный diff (`git checkout -- CLAUDE.md`).
- [ ] Проверить, что `@~/.claude/CLAUDE.user.md` в конце CLAUDE.md действительно
      подхватывается: `/memory` в Claude Code должен показать импорт. Если файла нет —
      создать пустой (или запустить `/sync-base`, он создаст).

## 3. Граф базы (теперь — версионируемая часть базы)
- [ ] Если graphify CLI не стоит: `uv tool install graphifyy`.
- [ ] Построить/обновить граф базы: `graphify "$HOME/.claude" --update`
      (первый раз — полный прогон; доки потребуют Ollama или GEMINI_API_KEY).
- [ ] Закоммитить и запушить: `graphify-out/graph.json`, `graphify-out/.graphify_labels.json`,
      `graphify-out/GRAPH_REPORT.md` (.gitignore-исключение уже в PR).
- [ ] **Дальше — правило хаба:** после значимых правок базы — `graphify ~/.claude --update`
      и коммит graphify-out вместе с правкой (вшито в CLAUDE.md, секция graphify).

## 4. Проверить PowerShell-правки (отсюда, из облака, их исполнение не проверить)
- [ ] `scripts/auto-pull.ps1`: новая сессия → в `auto-sync.log` строка extras-diff;
      при PENDING должен появиться файл `~/.claude/.local-state/extras-pending.flag`,
      при up-to-date — исчезнуть. Проверить оба состояния (изменив манифест тестово).
- [ ] STOP-уведомление: при существующем флаге Claude в первой реплике даёт одну
      строку «⚠ … запусти /sync-base» — без перечислений.
- [ ] `setup-extras.ps1` пока НЕ понимает `tier` и `method: claude-mcp-add` (поля
      инертны, unknown method = skip — безопасно). Доработать на ноутбуке, когда
      будет время; до тех пор exa и optional-логику ведёт сам /sync-base.

## 5. Прогнать /sync-base на ноутбуке
- [ ] Запустить `/sync-base` целиком: шаги 0–6, инвентарь, установка exa
      (`claude mcp add --transport http exa https://mcp.exa.ai/mcp --scope user`).

## 6. Smoke-тест поведенческих правок (новая сессия)
- [ ] Доменный запрос («разбери накладную» / «посчитай смету») → первой строкой
      должна появиться `Роутинг: …` и спавн доменного агента.
- [ ] Вопрос «как у нас принято добывать документы под антиботом?» → Claude идёт
      в `graphify query`, не читает memory подряд.
- [ ] Дать xlsx с формулами без кэша → Claude обязан сказать «значения не пересчитаны»,
      а не «ячейки пустые».

## 7. Отложенное решение (после обкатки)
- [ ] `permissions.deny: ["WebFetch"]` в settings.shared.json — НЕ включено сознательно:
      norm-lookup использует WebFetch как документированный fallback (~10 мест алгоритма).
      Если лестница веб-доступа покажет себя — сначала заменить fallback в norm-lookup
      на fetch/playwright, потом включать deny.

## 7а. Телеметрия инструментов (обкатка на dev-ПК ДО раскатки)
- [ ] Подключить hook **только в личный** `~/.claude/settings.json` (НЕ shared):
      `PostToolUse` → `scripts/log-tool-usage.ps1` (сниппет — в шапке самого скрипта).
- [ ] Поработать день-два → `pwsh scripts/aggregate-tool-usage.ps1 -Days 2` —
      проверить: лог пишется, агенты/скиллы фиксируются, ничего не тормозит.
- [ ] ОК → перенести hook-блок в `settings.shared.json` (раскатится merge-скриптом всем),
      добавить вызов сводки в /sync-base-отчёт и абзац телеметрии в feedback consumer'ов.

## 7б. Блок ПТО (скелет уже в репо: blocks/pto/BLOCK.md)
- [ ] Заполнить TODO в `blocks/pto/BLOCK.md`: pilot_machines (свой hostname), таблицу
      разграничения триггеров по мере появления агентов семьи.
- [ ] Перенести в блок уже «утёкшее»: `chains/id-volume-cascade.md` → `blocks/pto/chains/`,
      `skills/id-volume-graph/` → `blocks/pto/skills/` (git mv, чтобы сохранить историю).
- [ ] Новых агентов семьи класть СРАЗУ в `blocks/pto/agents/` (не в общий agents/).
- [ ] После переноса: `graphify ~/.claude --update` (граф должен увидеть blocks/) + коммит.
- [ ] Smoke-тесты блока — чек-лист в самом BLOCK.md.

## 8. Люди
- [ ] Обновить памятку сотрудникам. Суть: база обновляется сама (auto-pull);
      по подсказке Claude или раз в 1–2 недели — `/sync-base` в отдельной сессии;
      личные правила — в `CLAUDE.user.md`, файлы базы не редактировать;
      уроки/косяки уходят разработчику сами (feedback-канал).
- [ ] Разослать: после обновления базы всем нужен ОДИН перезапуск Claude Code.

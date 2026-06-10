# 2026-06-10 — Dev-сессия хаба: мерж remote-base-audit + чек-лист после мержа

## Контекст
Продолжение dev-линии 08–09.06. Пользователь принёс ветку `claude/database-phone-access-jkgcfl`
(аудит базы из облачной сессии на Fable 5: роутинг-гейт, лестница веба, ловушки Excel/Word,
tools-allowlist агентов, blocks/, телеметрия). Задача: принять изменения и выполнить
`docs/2026-06-09-laptop-after-merge.md` (одноразовый чек-лист хаба).

## Что сделал
1. **Мерж** ветки в main (no-ff, чисто) + push. «Удаление» handoff-отчёта в diff было
   артефактом two-dot diff — three-dot подтвердил, что ветка его не трогает.
2. **Личный слой**: `CLAUDE.user.md` создан; личных правок в CLAUDE.md не было.
3. **Граф базы построен и запушен**: 1188 узлов / 1464 ребра / 183 сообщества;
   корпус 452 файла (~387k слов), detect уважает .gitignore (приватное не попало).
   AST 375 узлов (0 токенов) + семантика 23 чанками через субагентов.
4. **Флаг-механика auto-pull верифицирована** (оба состояния: PENDING → флаг создан,
   up-to-date → удалён). PENDING восстановлен честно (долг до /sync-base).
5. **Телеметрия (7а)**: PostToolUse-hook в ЛИЧНЫЙ settings.json (не shared); активен
   после рестарта; агрегатор прогонять через день-два.
6. **Блок ПТО (7б)**: pilot_machines=[DANIIL]; `chains/id-volume-cascade.md` и
   `skills/id-volume-graph/` → `blocks/pto/` (git mv, история сохранена); пути в
   id-engineer.md/SKILL.md/skills.md обновлены; активация в `.local-state/blocks.json`.
7. **STOP-аудит синхронизирован**: эталон 11 core MCP (добавлены playwright, exa),
   `MCP: X/11`; reference_mcp.md переписан (firecrawl → опциональные).

## Где сломался / уроки
- **ГЛАВНЫЙ ИНЦИДЕНТ**: 11 экстракционных субагентов задиспатчены параллельно БЕЗ
  `model` → унаследовали Fable 5 → ~11M токенов, 5-часовой лимит MAX x5 сожжён за
  ~40 минут, 10/11 агентов умерли на лимите. Дострой на **haiku** (17 чанков, 3 батча
  по ≤6): ~1.3M haiku-токенов, все чанки за ~1.5 мин каждый. Урок в личной памяти
  (`feedback_subagent_model_economy`) — кандидат в базу: `memory/token_economy.md` +
  Workflow-правило CLAUDE.md (озвучка стоимости фан-аута + явный model).
- Windows multiprocessing: `graphify.extract()` требует `if __name__ == '__main__'`-guard
  в вызывающем скрипте (ProcessPoolExecutor + spawn).
- PowerShell-сериализованный settings.json: `&` хранится как `&` — Edit-tool по
  сырому тексту не матчится, править через ConvertFrom/ConvertTo-Json.
- На DANIIL (ноутбук разработчика) ПРОКСИ НЕТ — разовый «Could not resolve host»
  при push был временным DNS-сбоем, повторный push прошёл без всяких флагов.
  Правило bypass-proxy из proxy_github актуально для корп-ПК, не для этого хоста.
- Hostname этого ПК = `DANIIL` (не DANIILPC, как местами в памяти).

## Зафиксированные нюансы (для следующих dev-сессий)
- Скиллы внутри `blocks/<имя>/skills/` выпадают из авто-реестра скиллов Claude Code —
  это задумано («0 токенов у неактивных»), доступ по абсолютным путям из Required
  reading; если пилотам нужен авто-триггер — доработать активацию /sync-base
  (копировать и skills). Записано в blocks/pto/BLOCK.md.
- Манифест графа сохранён до git mv блока ПТО — первый `--update` пересчитает
  перемещённые файлы (кэш смягчит).
- 6 чанков экстракции выжили от Fable-агентов — их usage неизвестен, в cost.json
  учтены только haiku-токены (~1.4M).

## Осталось (после рестарта Claude Code)
1. Рестарт (новые CLAUDE.md/agents/командный /sync-base подхватятся).
2. `/sync-base` целиком (шаги 0–6, инвентарь, exa уже стоит на хабе).
3. Smoke-тесты поведения: роутинг-строка на доменном запросе; graphify query на
   «как у нас принято…»; xlsx с формулами без кэша → «значения не пересчитаны».
4. Телеметрия: через 1–2 дня `aggregate-tool-usage.ps1 -Days 2` → при ОК перенести
   hook в settings.shared.json + сводка в /sync-base + абзац в feedback.
5. Памятка сотрудникам + рассылка про один рестарт (п.8 чек-листа).
6. Отложено сознательно: deny WebFetch (сначала обкатка лестницы + замена fallback
   в norm-lookup); доработка setup-extras.ps1 (tier / claude-mcp-add).
7. Пользователь обещал ЕЩЁ вводные по работе всей базы — ждать, не предполагать.

## Продолжение сессии (плагины + telegram-бот + план изучения репо)
- **Плагины**: пользователь поставил 7 новых (firecrawl, chrome-devtools-mcp, telegram,
  atomic-agents, agenthub, demo-video, karpathy-coder), twilio и часть выключил.
  Плагины per-PC, другим НЕ раскатываются (раскатка = settings.shared.json + установка,
  кандидат в /sync-base). Сводка маркетплейса (144+35 плагинов) дана в чате; кандидаты
  на установку: session-report, hookify, self-improving-agent, skill-security-auditor,
  context7. Идея на будущее: упаковать claude-base как плагин (plugin-dev).
- **Telegram-бот настроен**: Claude-work-base (@Daniilcoop_bot), Bun 1.3.14 установлен,
  плагин enabled, токен в `~/.claude/channels/telegram/.env`. После рестарта: запустить
  `claude --channels plugin:telegram@claude-plugins-official`, написать боту → получить
  6-значный код → `/telegram:access pair <код>`. Дальше пользователь пересылает боту
  ссылки на GitHub-репо из «Избранного» (лежат там нумерованными списками с описаниями).
- **Следующая большая задача**: изучить присланные репо — «нужно нам / не нужно /
  заменяет / облегчает» (как тест обновлённой базы: роутинг-гейт, query-before-build
  по графу, лестница веба, harvest-методика). Блок ПТО — на обкатке (пилот DANIIL).

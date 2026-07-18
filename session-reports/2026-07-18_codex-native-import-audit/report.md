# Handoff LITE: native Codex import acceptance audit (2026-07-18)

> Состояние ноутбука закрыто и передано на домашний ПК. Переносимый источник:
> `Claude/reports/2026-07-18-codex-native-import-audit-handoff.md` в папке проекта.

## Цель

Проверить фактическую работоспособность и согласованность импортированных в Codex skills, agents, MCP и plugins; не приравнивать регистрацию к runtime PASS.

## Зафиксированные факты

- Владелец выполнил штатный Import from Claude Code с отмеченными инструментами/настройками, проектами и сессиями.
- После импорта `codex mcp list` показывает 15 enabled stdio MCP и HTTP `exa` со статусом `Not logged in`; регистрация не равна runtime PASS.
- В `~/.codex/config.toml` присутствуют 19 блоков `mcp_servers` (включая env-подблоки), в том числе Word, Excel, PDF, Revit, AutoCAD и импортированные внешние серверы.
- `python ~/.claude/scripts/codex_sync.py check` возвращает exit `2`: `canon-newer config.toml#managed`. Причина ветки — native import удалил managed-маркеры, поэтому parser получил `disk is None`; содержательный diff этим не доказан. Не запускать sync до явного решения о слиянии.
- Найдено 16 валидных agent TOML, 40 shared/imported каталогов skills в `~/.agents/skills` и 37 в `~/.claude/skills`. Отдельная read-only runtime-discovery увидела 98 уникальных skills.
- Native config объявляет 12 plugins, но cache/registry/declaration не доказывают installed, enabled или runtime. У двух Claude engineering plugins installPath отсутствует на диске; есть неоднозначности версий/cache.
- Полный release не доказан. Предыдущие profile, GUI и hook smoke имеют только свои узкие claims.

## Критические runtime-наблюдения

- Broad discovery записал итог, но процесс превысил 120 секунд; один из трёх SessionStart hooks завершился ошибкой.
- Override `mcp_servers = {}` не дал доказанного no-MCP baseline: после ответа были шесть неназванных shutdown-handshake timeout примерно по 30 секунд.
- Marketplace manager сам попытался выполнить auto-upgrade через `git clone` и получил timeout, хотя prompt запрещал tools/network.
- Models cache сообщил о missing field `supports_reasoning_summaries`; skill descriptions были сокращены до 2% skill-context budget; unsupported marketplace sources пропущены loader'ом.
- Новые тяжёлые `codex exec`, MCP и plugin smoke на этом ноутбуке не выполнять.

## Текущие ограничения

- Нет разрешения на write-операции в реальных проектах, login, установку пакетов или платные вызовы.
- Для runtime допускаются только read-only handshake/health-check без передачи пользовательских данных; остановиться перед login, платным действием или изменением внешней системы.
- Не изменять `codex-layer/AGENTS.codex.md` и `codex-layer/mcp-whitelist.json`: это user-owned dirty.

## Завершённые read-only исследования

- `skills_inventory`: подтверждены 40 shared, 37 Claude, 37 пересечений, 3 shared-only, 11 junctions и расхождение старого manifest с физическим/runtime scope.
- `agents_inventory`: 16 TOML валидны; семь reviewer-ролей явно read-only, у девяти production-ролей фактическая write-policy runtime не доказана.
- `mcp_inventory2`: reconciled native MCP/plugins, канон и device-local границы; конфликты регистрации не объявлены runtime PASS.
- `release_matrix`: сохранены узкие PASS и открытые gates полного release.

## Следующий шаг на домашнем ПК

1. Читать переносимый handoff и JSON из `Claude/reports/` в папке проекта.
2. Снять собственный device-local read-only preflight; состояние профиля ноутбука не переносить как факт домашнего ПК. `codex_sync.py check` и `git status` выполнять только при наличии локальных скрипта и claude-base; иначе записать `NOT PRESENT` и не копировать их с ноутбука.
3. Найти по официальному Codex manual настоящий способ изолировать MCP и marketplace; доказать его no-tool контролем до component smoke.
4. Собрать acceptance matrix и проверять по одному компоненту. Перед login, install/download, платным, browser, Revit/AutoCAD live или write-действием запросить разрешение.
5. Перед любым общим claim PASS дать полную матрицу независимому auditor.

## Prompt for the new chat

> Продолжение полного acceptance-аудита Codex на домашнем ПК. Работай из текущего корня проекта. Сначала прочитай `Claude/CLAUDE.md`, две верхние записи `Claude/ЖУРНАЛ СЕССИЙ.md`, верх `Claude/STATUS.md`, затем `Claude/reports/2026-07-18-codex-native-import-audit-handoff.md`. Точный laptop runtime-discovery лежит рядом в `2026-07-18-codex-runtime-discovery.json`. Цель не сокращать: проверить фактическую работоспособность, актуальность, routing и непротиворечивость всех skills, agents, MCP и plugins. Начни с собственного read-only preflight. Device-local `codex_sync.py check` и `git status` выполняй только если соответствующие script/repository существуют; иначе запиши `NOT PRESENT` и не копируй их с ноутбука. Не копируй laptop config и не запускай `codex_sync.py sync` или широкий `codex exec`. Сначала докажи настоящий no-MCP/no-marketplace контроль, затем тестируй по одному компоненту и веди acceptance matrix. Full release сохраняй NOT PASS до доказательства каждой строки и независимого аудита.

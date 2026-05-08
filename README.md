# claude-base

Общая база Claude Code: глобальные правила (`CLAUDE.md`), агенты, скиллы, эмпирическая память, отчёты сессий, harvest внешних инструментов.

**Этот репо клонируется в `~/.claude/` каждого ПК пользователя через [claude-lite-instaler](https://github.com/daniileliseev1337/claude-lite-instaler).** Все ПК синхронизируют изменения через git.

## Что внутри

| Папка / файл | Назначение |
|---|---|
| `CLAUDE.md` | Глобальный manifest: STOP-процедура, 5 принципов Karpathy, MCP-роутинг, скилл-роутинг, агенты-проверяльщики, harvest-workflow, прокси. CORE-секция управляется installer'ом, USER EXTENSIONS — личное. |
| `agents/` | Агенты Claude Code: доменные (`designer`), общий ревьюер (`auditor`), узкие read-only ревьюеры (`pdf-reviewer`, `excel-validator`, `word-checker`). |
| `skills/` | Скиллы: `karpathy-guidelines`, `pdf-helper`, `excel-helper`, `word-helper`. |
| `memory/` | Эмпирические наблюдения по реальным задачам. Кейсы провалов и успехов, обезличенные. |
| `sessions/` | Per-session reports: каждая закончившаяся сессия складывает сюда `<дата>_<тема>/` с `report.md`, `harvested/`, `artifacts/`. |
| `harvested/` | Каталог внешних инструментов (notes-only). Каждая запись — независимая оценка какого-то репо или библиотеки с GitHub. |
| `_sandbox/` | **Локальная** изолированная папка для тестов внешних инструментов. **В .gitignore**, не пушится. |
| `scripts/` | Auto-sync скрипты: `auto-pull.ps1` (SessionStart hook), `auto-push.ps1` (SessionEnd hook). Подробности — в `scripts/README.md`. |
| `settings.json` | Конфигурация Claude Code hooks (SessionStart/SessionEnd → auto-sync). Глобальная, едина для всех ПК пользователя. Локальные настройки — в `settings.local.json` (gitignored). |

## Архитектура

Агентская: **main → доменный агент → ревьюер**. Подробности в `CLAUDE.md`.

- Доменные агенты — узкоспециализированные эксперты (на сегодня: `designer` для проектирования инженерных систем). Остальные домены добавляются по факту реальных повторяющихся задач, не наперёд.
- Ревьюеры — независимые, без права записи в файлы. Получают только ТЗ и артефакт. Failure-mode строгий.
- Лимит глубины вызовов: 2 уровня.

## Использование

**Установка** через [claude-lite-instaler](https://github.com/daniileliseev1337/claude-lite-instaler):

```powershell
git clone https://github.com/daniileliseev1337/claude-lite-instaler
cd claude-lite-instaler
.\Install.ps1
```

Установщик клонирует `claude-base` в `~/.claude/` и настраивает связку (VS Code, MCP-серверы, прокси, hooks).

**Без установщика** (если нужно вручную):

```powershell
git clone https://github.com/daniileliseev1337/claude-base $env:USERPROFILE\.claude
```

## Auto-sync между ПК

После установки Claude Code автоматически синхронизирует `~/.claude/` с GitHub:

- **На старте сессии (SessionStart hook):** `auto-pull.ps1` делает `git pull --rebase --autostash`. Подтягивается всё, что добавили на других ПК.
- **На завершении сессии (SessionEnd hook):** `auto-push.ps1` коммитит изменения в whitelist-путях (`agents/`, `skills/`, `memory/`, `sessions/`, `harvested/`, `CLAUDE.md`) и пушит на origin.

**Whitelist защищает** от случайного push'а `credentials`, `history.jsonl`, `plugins/`, `projects/`, `_sandbox/`. Эти пути **никогда** не коммитятся автоматически.

Лог: `~/.claude/auto-sync.log`. При конфликте rebase — скрипт абортит, ничего не теряет, ждёт ручного резолва.

## Дисциплина расширения

- **Новый агент** создаётся **только** после ≥3 успешных применений основного Claude в этом домене без агента.
- **Новых правил наперёд не пишем.** Эмпирические наблюдения → `memory/`, не в инструкции агентов.
- **Внешние инструменты** — через harvest-workflow (см. `CLAUDE.md`): заметки и тестирование в sandbox да, копирование кода без согласия — нет.

## Безопасность

`.gitignore` использует **whitelist-подход** — игнорируется всё, кроме явно разрешённых директорий. Это защищает от случайного попадания credentials, истории чатов и других конфиденциальных данных в публичный репо.

**Никогда** не должно попадать в git:
- `.credentials.json` (auth-токены Anthropic)
- `history.jsonl` (история чатов)
- `cache/`, `downloads/`, `plugins/`, `backups/`, `file-history/`, `projects/`
- `_sandbox/` (локальные тесты)

## История

Старая база (Волны 1-11, проектная база `claude-stroy-base` с архитектурой «скиллы + lazy-load + триггерные карты») заархивирована:
- Тег `archive/v1-legacy` в репо `claude-stroy-base`.
- Ветка `v2` там же — промежуточный vault, не использовался.

Причина перехода: эмпирически доказано, что архитектура «правила + скиллы + триггерные карты в локальном vault» хуже, чем глобальная база в `~/.claude/` с агентами + ревьюерами.

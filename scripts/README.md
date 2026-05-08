# scripts/

Auto-sync скрипты для синхронизации `~/.claude/` с git-репо `claude-base`.

## Файлы

- **`auto-pull.ps1`** — `SessionStart` hook. Делает `git pull --rebase --autostash` тихо. Логирует в `~/.claude/auto-sync.log`. Всегда `exit 0` чтобы не блокировать старт сессии.
- **`auto-push.ps1`** — `SessionEnd` hook. Проверяет git status whitelisted путей, при изменениях — commit + pull --rebase + push. Логирует в `~/.claude/auto-sync.log`.

## Whitelist managed paths

`auto-push.ps1` коммитит **только** эти пути:

- `agents/`
- `skills/`
- `commands/`
- `memory/`
- `sessions/`
- `harvested/`
- `CLAUDE.md`
- `README.md`

Всё остальное (credentials, history, plugins, projects, `_sandbox/`) — **никогда** не коммитится автоматически. Это защита от утечки конфиденциальных данных. Whitelist дублирует политику `.gitignore` (defense in depth).

## Hooks конфигурация

Прописана в `claude-base/settings.json` → после `git clone` это `~/.claude/settings.json`. Claude Code читает её и срабатывает на:

- **SessionStart** → `auto-pull.ps1`
- **SessionEnd** → `auto-push.ps1`

## Что в логе

`~/.claude/auto-sync.log` — append-only. Формат:

```
[2026-05-09 12:30:15] auto-pull: start
[2026-05-09 12:30:16] auto-pull: ok
[2026-05-09 14:45:02] auto-push: start
[2026-05-09 14:45:02] auto-push: managed changes in: memory, sessions
[2026-05-09 14:45:03] auto-push: commit ok
[2026-05-09 14:45:05] auto-push: pushed to origin/main
```

При проблеме (FAILED / exception / pull conflict) — тоже видно в логе.

## Что делать при конфликте

Если auto-pull или auto-push упал из-за конфликта (например, ты правил `CLAUDE.md` USER EXTENSIONS на двух ПК одновременно):

1. Открой `~/.claude/auto-sync.log` — увидишь когда упал.
2. Перейди в `~/.claude/`, выполни `git status` — увидишь конфликт.
3. Резолви руками: правишь файл, `git add`, `git rebase --continue`, `git push`.

Скрипт **никогда** не пытается силой перезаписать или потерять твои изменения — при конфликте просто аборт ребейза, ничего не теряется.

## Ограничения

- **Нет rate-limiting.** Каждая SessionEnd → попытка push. Если ты открыл и закрыл 10 сессий за час, push'ей будет 10 (с одинаковым timestamp в commit message). Это не страшно (commit'ы линейные, история чистая), но если хочется группировать — добавить можно позже.
- **Без credentials prompt.** Если `git push` требует ввод пароля — повиснет. Используй SSH-ключ или Personal Access Token в URL/credential helper.
- **Один main branch.** Хуки работают только с `origin/main`. Если в будущем добавим feature-branches или PR-flow — переписать.

## Manual trigger

Если хочется запустить вручную (не дожидаясь session start/end):

```powershell
# Pull
& "$env:USERPROFILE\.claude\scripts\auto-pull.ps1"

# Push
& "$env:USERPROFILE\.claude\scripts\auto-push.ps1"
```

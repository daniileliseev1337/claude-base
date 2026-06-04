# Auto-sync инфраструктура (информационно)

_Вынесено из CLAUDE.md 2026-05-26 (Phase 1 refactoring для экономии overhead токенов в каждой сессии). Загружается через Read только когда нужно._

---

## Auto-sync инфраструктура (информационно)

`~/.claude/` склонирована через git из репо
[claude-base](https://github.com/daniileliseev1337/claude-base). Между
ПК синхронизация **автоматическая** через Claude Code hooks
(`~/.claude/settings.json`):

- **SessionStart hook** в†’ запускает `~/.claude/scripts/auto-pull.ps1`
  в†’ `git pull --rebase --autostash` (актуализирует базу от других ПК).
- **SessionEnd hook** в†’ запускает `~/.claude/scripts/auto-push.ps1`
  в†’ если есть изменения в whitelist managed paths (agents/, skills/,
  memory/, session-reports/, harvested/, CLAUDE.md) в†’ `git add` +
  `git commit` + `git push origin main`. Personal files (credentials,
  history, plugins, projects) **никогда** не коммитятся.

Лог auto-sync: `~/.claude/auto-sync.log`.

**Важно для понимания:**
- Это **не правило в CLAUDE.md**, которому я следую как модель — это
  системные hooks, срабатывают автоматически без моего участия.
- Системное правило Claude Code «не пушить без явной просьбы пользователя»
  касается **моих** ручных `git push` через Bash tool — оно **не**
  отменяет auto-sync hooks.
- Подробности и история ловушек настройки — в `memory/2026-05-09_hooks-debugging.md`.

---

---
description: Сверить локальную claude-base (~/.claude) с GitHub origin, подтянуть обновления (git pull), проверить per-machine инструменты (Exa MCP, Codex CLI) и выдать чеклист того, что нужно доставить руками. Безопасно — push не делает автоматически.
allowed-tools: Bash
---

# /sync-base — актуализация claude-base с GitHub

Сверяет локальную базу `~/.claude` с origin (claude-base на GitHub),
подтягивает обновления, проверяет per-machine инструменты, выдаёт чеклист
ручных действий.

Использование: `/sync-base` (без аргументов).

## ВАЖНЫЕ правила
- **Bypass proxy для GitHub ОБЯЗАТЕЛЕН** (корп-прокси блокирует CONNECT к
  github.com). Все git-команды к origin — с `-c http.proxy="" -c https.proxy=""`.
- **НЕ делать `git push` автоматически.** Только предложить, если есть
  локальные незапушенные коммиты (могут содержать приватное — решает пользователь).
- **Путь с кириллицей** — всегда оборачивать `"$HOME/.claude"` в кавычки.
- При конфликте rebase — остановиться, показать конфликт, спросить пользователя.

## Алгоритм

### Шаг 1. Сверка с GitHub
```bash
git -C "$HOME/.claude" -c http.proxy="" -c https.proxy="" fetch origin main
echo "BEHIND (origin впереди нас):"; git -C "$HOME/.claude" rev-list --count HEAD..origin/main
echo "AHEAD (у нас незапушенного):"; git -C "$HOME/.claude" rev-list --count origin/main..HEAD
git -C "$HOME/.claude" status -sb | head -3
```

### Шаг 2. Если BEHIND > 0 — подтянуть
```bash
git -C "$HOME/.claude" -c http.proxy="" -c https.proxy="" pull --rebase --autostash origin main
```
Затем показать что обновилось:
```bash
git -C "$HOME/.claude" log --oneline -10
```
Особо отметить новые/изменённые файлы в `skills/`, `agents/`, `memory/`,
`commands/`, `chains/` — это то, что реально влияет на работу.

### Шаг 3. Если AHEAD > 0 — предупредить (НЕ пушить сам)
Сообщить: «На этом ПК N локальных коммитов, которых нет на GitHub.»
Показать их: `git -C "$HOME/.claude" log --oneline origin/main..HEAD`.
Спросить пользователя, пушить ли (могут быть приватные данные —
проверить обезличивание перед push).

### Шаг 4. Проверить per-machine инструменты (git их НЕ переносит)
```bash
echo "=== Exa MCP ==="; claude mcp list 2>&1 | grep -i exa || echo "НЕТ — доустановить"
echo "=== Codex CLI ==="; codex --version 2>&1 || echo "НЕТ — опционально"
```

### Шаг 5. Доклад пользователю
Выдать структурированный итог:

**✅ Подтянуто из git:** перечислить ключевые обновления (skills/agents/memory/commands).

**🔲 Доустановить руками (per-machine, если отсутствует из Шага 4):**
- Exa MCP: `claude mcp add --transport http exa https://mcp.exa.ai/mcp`
- Codex CLI (опц): `npm i -g @openai/codex` → `codex login` → `/plugin install codex@openai-codex`

**🔲 Веб (claude.ai), проверить разово:**
- Adobe MCP отключён? (Settings → Connectors → Adobe → Disconnect) — 0% использования

**🔲 Developer-ПК only:**
- `/plugin install compound-engineering` (если этот ПК — developer)

## Если всё актуально
Если BEHIND=0 и все per-machine инструменты на месте — коротко: «База
актуальна, всё на месте» + что проверено. Не разводить отчёт.

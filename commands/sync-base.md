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
echo "=== Inkscape (правка вектор-PDF, pdf-helper) ==="; inkscape --version 2>&1 | head -1 || echo "НЕТ — доустановить (нужен для правки чертежей-PDF)"
echo "=== graphify (граф кода/docs больших папок — опц.) ==="; graphify --version 2>&1 | head -1 || echo "НЕТ — опционально"
echo "=== Ollama (локальный LLM-бэкенд graphify для docs-графа — опц.) ==="; ollama --version 2>&1 | head -1 || echo "НЕТ — опционально"
```

### Шаг 5. Доклад пользователю
Выдать структурированный итог:

**✅ Подтянуто из git:** перечислить ключевые обновления (skills/agents/memory/commands).

**🔲 Доустановить руками (per-machine, если отсутствует из Шага 4):**
- Exa MCP: `claude mcp add --transport http exa https://mcp.exa.ai/mcp --scope user`
- Inkscape (правка вектор-PDF, скилл `pdf-helper`): `winget install Inkscape.Inkscape`
  (или inkscape.org, нужна версия 1.x). ⚠ Медленный на слабом железе/без GPU.
  GPL-3.0 — используется как внешняя программа, не в коде. После установки —
  перезапуск терминала, чтобы `inkscape` появился в PATH.
- graphify (опц., граф кода/docs — для разбора больших папок: проекты, ИД-том, кодовые базы): `uv tool install graphifyy` → `graphify install --platform claude` (даёт `/graphify`). Для **кода** работает offline (бесплатно). Для **docs/PDF** нужен LLM-бэкенд (Ollama ниже, или `GEMINI_API_KEY`/`ANTHROPIC_API_KEY`). MIT.
- Ollama (опц., локальный LLM для graphify docs/PDF-графа конфиденц. данных — данные не уходят в облако): `winget install Ollama.Ollama` → `ollama pull qwen2.5:7b` (~5 ГБ). ⚠ Без GPU медленно (ночные/пакетные прогоны). Для кода graphify работает и без Ollama.
- glif-mcp (опц., ⚠ archived — визуальные AI-workflow glif.app, узкая ниша): `claude mcp add glif -s user -e GLIF_API_KEY=<key> -- npx -y @glifxyz/glif-mcp-server`. Нужен `GLIF_API_KEY` (glif.app). Ставить только если реально нужно.

**🔲 Веб (claude.ai), проверить разово:**
- Adobe MCP отключён? (Settings → Connectors → Adobe → Disconnect) — 0% использования

**🔲 Developer-ПК only:**
- `/plugin install compound-engineering` (если этот ПК — developer)

## Если всё актуально
Если BEHIND=0 и все per-machine инструменты на месте — коротко: «База
актуальна, всё на месте» + что проверено. Не разводить отчёт.

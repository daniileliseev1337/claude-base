---
description: Единая команда актуализации claude-base — pull обновлений, самопроверка базы, установка инструментов по манифесту (core молча, optional по выбору), полный инвентарь того, что стоит/не стоит/требует ключа. Безопасно — push не делает автоматически.
allowed-tools: Bash, Read, AskUserQuestion
---

# /sync-base — единая актуализация claude-base

Одна команда «обнови мне всё»: git pull + самопроверка + установка/инвентарь инструментов.
Объединяет прежние ручные шаги (Update-ClaudeBase, setup-extras) — пользователю
знать о них не нужно. Использование: `/sync-base` (без аргументов).

## ВАЖНЫЕ правила
- **Bypass proxy для GitHub ОБЯЗАТЕЛЕН** (корп-прокси блокирует CONNECT к
  github.com). Все git-команды к origin — с `-c http.proxy="" -c https.proxy=""`.
- **НЕ делать `git push` автоматически.** Только предложить, если есть
  локальные незапушенные коммиты (могут содержать приватное — решает пользователь).
- **Путь с кириллицей** — всегда оборачивать `"$HOME/.claude"` в кавычки.
- При конфликте rebase — остановиться, показать конфликт, спросить пользователя.
- Отказ от optional-инструмента — записать, но **в инвентаре показывать всегда**
  (пользователь мог передумать; «отказался однажды» ≠ «исчез навсегда»).

## Алгоритм

### Шаг 0. Личный слой
Если нет `~/.claude/CLAUDE.user.md` — создать с заголовком:
```bash
test -f "$HOME/.claude/CLAUDE.user.md" || printf '# CLAUDE.user.md — личные правила этого ПК (в git не попадает)\n' > "$HOME/.claude/CLAUDE.user.md"
```

### Шаг 1. Сверка с GitHub и pull
```bash
git -C "$HOME/.claude" -c http.proxy="" -c https.proxy="" fetch origin main
echo "BEHIND (origin впереди нас):"; git -C "$HOME/.claude" rev-list --count HEAD..origin/main
echo "AHEAD (у нас незапушенного):"; git -C "$HOME/.claude" rev-list --count origin/main..HEAD
```
Если BEHIND > 0:
```bash
git -C "$HOME/.claude" -c http.proxy="" -c https.proxy="" pull --rebase --autostash origin main
git -C "$HOME/.claude" log --oneline -10
```
Отметить новые/изменённые файлы в `skills/`, `agents/`, `memory/`, `commands/`,
`chains/`, `graphify-out/` — это то, что реально влияет на работу.
Если AHEAD > 0 — предупредить, показать коммиты, НЕ пушить самому
(проверить обезличивание, решает пользователь).

### Шаг 2. Самопроверка базы
```powershell
pwsh -File "$HOME/.claude/scripts/verify-claude-base.ps1"
```
(если скрипта нет — пропустить с пометкой). Провалившиеся проверки — в итоговый отчёт.

### Шаг 3. Инвентарь инструментов по манифесту
Прочитать `~/.claude/mcp-manifest.json` (поля `tier`, `needs_admin`, `needs_key`,
`size_mb`) и `~/.claude/.local-state/declined.json` (если есть). Снять факт:
```bash
claude mcp list
```
Для каждого элемента манифеста определить статус: `установлен` / `НЕ установлен` /
`отклонён ранее (дата)` / `нужен админ` / `нужен ключ`.

### Шаг 4. Установка
- **`tier: core`, не установлено** → ставить сразу, без вопросов:
  - MCP с `method: uvx|npx|github-zip-uv` — через `pwsh -File "$HOME/.claude/scripts/setup-extras.ps1"`
    (идемпотентен, ставит недостающее по манифесту);
  - `method: claude-mcp-add` (exa) — выполнить `register_command` из манифеста напрямую.
- **`tier: optional`, не установлено** → ОДИН вопрос списком (AskUserQuestion,
  multiSelect): название + назначение + размер. Включая отклонённые ранее
  (пометить «отклонял <дата>»). Выбранное — ставить; невыбранное — записать в
  `~/.claude/.local-state/declined.json` (`{"имя": "YYYY-MM-DD"}`).
- **`needs_admin: true`** на корп-ПК без админ-прав → не пытаться, в отчёт:
  «требует админа — пропущено». Если есть user-space обход — предложить его.
- **`needs_key: true`** без ключа → в отчёт: «нужен ключ от разработчика» (не молча).
- Прочее per-machine (вне манифеста): Inkscape (`winget install Inkscape.Inkscape`,
  нужен админ), graphify CLI (`uv tool install graphifyy` — нужен для query по графу
  базы), Ollama (опц., локальный LLM для graphify-доков). Предлагать в том же
  optional-списке.

### Шаг 5. Снять флаг уведомления
Если установка по манифесту прошла (setup-extras обновил marker) — удалить
`~/.claude/.local-state/extras-pending.flag`. Если что-то core не встало —
флаг ОСТАВИТЬ (уведомление в STOP продолжит напоминать).

### Шаг 6. Итоговый отчёт (всегда, компактно)
```
✅ База: подтянуто N коммитов (ключевое: ...) / актуальна
✅ Самопроверка: X/Y (провалы: ...)
📦 Инструменты:
   установлено: ...
   поставлено сейчас: ...
   отклонено тобой (можно передумать): ...
   требует админа: ...   требует ключа: ...
```
Если всё актуально и стоит — одной строкой: «База актуальна, всё на месте».

## Примечания
- `Update-ClaudeBase.bat` остаётся ТОЛЬКО как bootstrap самого первого запуска
  на новом ПК (когда Claude-сессии ещё нет). Дальше — только `/sync-base`.
- Web (claude.ai) разово: Adobe MCP отключён? (Settings → Connectors → Disconnect).
- Developer-ПК only: `/plugin install compound-engineering`.

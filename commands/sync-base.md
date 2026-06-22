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
```bash
# pwsh (PowerShell 7) есть не на всех ПК — fallback на встроенный Windows PowerShell 5.1
if command -v pwsh >/dev/null; then PS="pwsh"; else PS="powershell -NoProfile -ExecutionPolicy Bypass"; fi
$PS -File "$HOME/.claude/scripts/verify-claude-base.ps1"
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
  - MCP с `method: uvx|npx|github-zip-uv` — через `$PS -File "$HOME/.claude/scripts/setup-extras.ps1"`
    (тот же fallback `pwsh`/`powershell`, что в Шаге 2; идемпотентен, ставит недостающее по манифесту);
  - `method: claude-mcp-add` (exa) — выполнить `register_command` из манифеста напрямую.
- **Version-drift (уже установленные MCP)** → сверить зарегистрированную команду
  (`claude mcp get <name>`) с `install_args`/`register_args` манифеста. Если версия
  расходится (напр. `@latest` вместо закреплённой) — перерегистрировать:
  `claude mcp remove <name> -s user` + `claude mcp add` по манифесту, напомнить про
  restart. Сейчас актуально для **playwright** (закреплён `@playwright/mcp@0.0.76`):
  `@latest` авто-обновлялся и на смене версии докачка браузера через корп-прокси
  зависала → Chrome на about:blank. setup-extras сверяет по ИМЕНИ и сам этого не чинит.
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
  optional-списке. **Установленность Inkscape проверять по путям установки**
  (`Test-Path 'C:\Program Files\Inkscape\bin\inkscape.exe'` и аналоги), НЕ через
  `command -v`/PATH — winget не добавляет Inkscape в PATH, ложный «не установлен».

### Шаг 4.5. Блоки (`~/.claude/blocks/`)
Прочитать `blocks/*/BLOCK.md` и `.local-state/blocks.json` (активные блоки этого ПК).
- `status: experimental` → предлагать ТОЛЬКО если hostname в `pilot_machines`.
- `status: stable` → предложить по описанию `roles` (один вопрос, отказ — в declined.json,
  в инвентаре показывать всегда).
- **Активация**: скопировать `blocks/<имя>/agents/*.md` в `~/.claude/agents/` с префиксом
  `block-<имя>-` (копии gitignored), записать в `.local-state/blocks.json`, напомнить про
  restart Claude Code. **Деактивация**: удалить копии `agents/block-<имя>-*`, убрать из json.
- При обновлении базы (Шаг 1 подтянул правки в `blocks/`) — пересоздать копии активных
  блоков (источник истины — `blocks/`, копии всегда перезаписываемы).

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

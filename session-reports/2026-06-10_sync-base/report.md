# Отчёт сессии: /sync-base (плановая актуализация)

**Дата:** 2026-06-10
**Машина:** хаб (маркер developer есть)
**Тема:** прогон /sync-base — pull, самопроверка, инвентарь инструментов, hub-рутина pull-feedback.

## Что сделано

1. **Git-сверка:** BEHIND 0 / AHEAD 0 — база актуальна, pull не требовался.
2. **Самопроверка** `scripts/verify-claude-base.ps1`: **23/23 PASS** (включая pytest evals — 21 тест).
   Нюанс: в Git Bash нет `pwsh` — скрипт запущен через `powershell.exe` (Windows PowerShell 5.1), отработал штатно.
3. **Инвентарь по манифесту** (`mcp-manifest.json`, last_updated 2026-06-09):
   - MCP: все 12 из манифеста установлены и `✓ Connected` (11 core + optional autocad-mcp). Сверх манифеста подключён firecrawl.
   - Python-пакеты: все 15 (7 core + 8 optional) импортируются без ошибок.
   - Per-machine: graphify 0.8.35 ✓, Ollama ✓, Inkscape ✓ (стоит в `C:\Program Files\Inkscape\`, просто не в PATH Git Bash — `command -v` его не видит, проверять Test-Path).
   - Ставить/предлагать было нечего — declined.json не создавался.
4. **Блоки:** активен `pto` (blocks.json). Копий `block-pto-*` в `agents/` нет — это НЕ рассинхрон: `blocks/pto/agents/` ещё пуст («агенты семьи в разработке»), копировать нечего. База не обновлялась — пересоздание копий не требовалось.
5. **Флаг** `.local-state/extras-pending.flag` снят — весь core на месте.
6. **Hub-рутина:** `pull-feedback.ps1` — 8 веток, файлы в `feedback-inbox/all/`. Свежее на ревью: 3 отчёта консумера за 09–10.06 (upd-batch, graph-system, document-control-sum-rule).

## Где сломалось / уроки

- `pwsh` отсутствует в PATH Git Bash на этой машине — шаг 2 /sync-base падает, если запускать буквально `pwsh -File ...` через Bash. Рабочий обход: `powershell -NoProfile -ExecutionPolicy Bypass -File ...`. Кандидат на правку текста скилла sync-base (fallback pwsh → powershell).
- Проверка Inkscape через `command -v` даёт ложный «не установлен» — winget-установка не добавляет его в PATH. Проверять стандартные пути установки.

## Follow-up: уроки внедрены в базу (по «да» хаба)

Правки `commands/sync-base.md` (хирургически, 2 урока выше):
1. Шаг 2: fallback `pwsh` → `powershell -NoProfile -ExecutionPolicy Bypass` (PowerShell 7 есть не на всех ПК); та же оговорка для setup-extras.ps1 в Шаге 4.
2. Шаг 4: проверка Inkscape — по стандартным путям установки (`Test-Path`), не `command -v` (winget не добавляет в PATH).

Граф базы обновить НЕ удалось (см. ниже) — `graphify-out/` остался на прежнем состоянии,
staleness по sync-base.md минимальная (2 точечные правки текста шагов).

### Блокер: graphify docs-бэкенд на этой машине

- Без API-ключа graphify отказывается извлекать 6 изменённых doc-файлов (нужен GEMINI/ANTHROPIC/OPENAI/... ключ или `--backend`).
- `--backend ollama` по умолчанию ждёт `qwen2.5-coder:7b` (стоит `qwen2.5:7b` — лечится `--model`).
- Главное: llama-server НЕ загружает модель из `~/.ollama/models/blobs/` — кириллический путь профиля (`C:\Users\Даниил\...`) приходит в него битым (`������`). Ollama на этой машине неработоспособна для graphify, пока `OLLAMA_MODELS` не перенесён на ASCII-путь (напр. `C:\ollama-models`) с повторным pull (~4.7 GB).
- Решение хаба: либо ключ для облачного бэкенда, либо перенос OLLAMA_MODELS. До тех пор — граф обновлять при следующей значимой правке базы.

## Итог

База актуальна, 23/23 самопроверка, весь инструментарий манифеста стоит, флаг долга снят. Уроки сессии внедрены в текст скилла sync-base. Открытый хвост: ревью свежего feedback из inbox (решение хаба, в эту сессию не входило).

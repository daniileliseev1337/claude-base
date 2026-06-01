# Актуализация всех ПК команды с claude-base (2026-06-01)

Что внедрено в harvest-сессии 9 плагинов и как это получить на каждом ПК.

## TL;DR — минимум для всех ПК
```
1. ~/.claude/scripts/Update-ClaudeBase.bat      # git-синк базы
2. claude mcp add --transport http exa https://mcp.exa.ai/mcp   # per-machine
```
Этого достаточно чтобы получить `domain-grilling` + Exa. Остальное — опционально.

## Что каким каналом берётся

| Инструмент | Канал | Команда / действие |
|---|---|---|
| **domain-grilling** skill | git ✅ | `Update-ClaudeBase.bat` (или `git -C ~/.claude pull`) |
| memory (уроки), отчёты | git ✅ | то же |
| **Exa MCP** | per-machine ❗ | `claude mcp add --transport http exa https://mcp.exa.ai/mcp` |
| **Codex** CLI+plugin | per-machine ❗ | `npm i -g @openai/codex` → `codex login` → `/plugin install codex@openai-codex` |
| frontend-design, skill-creator, security-guidance | auto ✅ | официальный marketplace ставит сам. Проверить `/plugin` |
| **Codeburn** (метрики) | per-machine (опц) | `npx codeburn` (без установки) |
| **Compound Engineering** | per-machine | `/plugin install compound-engineering` — ТОЛЬКО developer-ПК |

❗ = git pull НЕ переносит, ставить на каждом ПК отдельно.

## По ролям ПК

### Все 9 ПК (базовый набор)
1. `Update-ClaudeBase.bat` — получить domain-grilling + memory + отчёты
2. `claude mcp add --transport http exa https://mcp.exa.ai/mcp` — Exa
3. (опц) `npx codeburn` — глянуть свой расход токенов
4. Codex (опц, для cross-model review): `npm i -g @openai/codex` + `codex login` + plugin
5. Проверить что frontend-design/skill-creator/security-guidance активны (`/plugin`)

### Developer-ПК (этот + тот кто разрабатывает базу) — дополнительно
6. `/plugin install compound-engineering` — meta-dev claude-base
7. Активно использовать Skill Creator (Eval/Benchmark) при создании skills

## Действия в вебе (claude.ai, на каждом аккаунте)
- **Отключить Adobe MCP**: Settings → Connectors → Adobe → Disconnect
  (Codeburn: 0% использования, 57 неиспользуемых tools грузятся зря)
- (опц) проверить другие 0%-connectors: Vercel, Gmail, Claude_Preview, PDF_Tools

## Codex privacy (правило, не hook)
Перед `/codex:review` на документе с **ФИО / шифрами / реквизитами заказчиков**
— Claude спрашивает разрешение (данные уходят на серверы OpenAI, free tier
может использовать для обучения, ПДн третьих лиц по 152-ФЗ). Опции:
[Да / Нет / Обезличить сначала]. Реализация — правило в CLAUDE.md
(финализируется отдельно).

## Pending (решается в отдельных сессиях)
- 🔥 **Word/PDF косяки** + **Higgsfield/ComfyUI** (image/video) — отдельная сессия
- **Firecrawl self-host** — требует сервер К-7 + docker (Фаза 1, инфра-задача)
- **domain-grilling раскат** — после теста через Skill Creator Eval
- **Exa user scope** — сейчас local на developer-ПК; для постоянного
  использования в разных папках перевести в user scope
- **MCP cleanup** — adeu 0%, мусорные connectors (в Word/PDF сессию)

## Идея на автоматизацию (упростить будущие актуализации)
Добавить `claude mcp add exa` в `setup-extras.ps1` → тогда
`Update-ClaudeBase.bat` ставил бы Exa автоматически на каждом ПК
(одна команда вместо двух). Требует правки скрипта — отдельная задача.

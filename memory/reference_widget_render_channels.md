# Reference — каналы рендеринга виджетов в Claude Code / Desktop

Где и как Claude может показать интерактивный виджет (карта понимания, дашборд, диаграмма).
Проверено эмпирически (env, ToolSearch, playwright) + по докам через `claude-code-guide`
(сессия 2026-06-29). Тип: reference.

## Матрица каналов

| Поверхность | show_widget (visualize) | MCP-app (ui:// resource) | standalone HTML-файл |
|---|---|---|---|
| Claude Desktop → вкладка **Code** | ✅ рендерит | ❌ текст/JSON | ✅ |
| Claude Desktop → **Chat** | н/п (там Artifacts) | ✅ рендерит | ✅ |
| **VS Code**-расширение Claude Code | ❌ инструмента нет | ❌ текст/JSON | ✅ (Simple Browser) |
| CLI в терминале | ❌ | ❌ | ✅ (открыть в браузере) |
| Телефон (мобайл) | — | только **remote** MCP | ✅ (браузер) |

## Ключевые факты

- **`show_widget` (MCP `visualize`) есть ТОЛЬКО при `CLAUDE_CODE_ENTRYPOINT=claude-desktop`.**
  В VS Code-расширении инструмента нет вовсе (ToolSearch по `visualize`/`show_widget` пуст —
  проверено живьём). Это не конфиг-MCP (в `claude mcp list` его нет) — инжект среды.
- **Claude Code НЕ хост MCP Apps** (apps-surface, `text/html;profile=mcp-app`, `_meta.ui.resourceUri`) —
  by design, включающего флага нет. Официальный список хостов MCP Apps: Claude (web+desktop),
  Goose, VS Code (через GitHub Copilot, НЕ через расширение Claude Code), ChatGPT.
- **Мобайл рендерит виджеты только у remote-коннекторов** (custom connector по публичному URL,
  заведённый на claude.ai). Локальный Stdio MCP-сервер телефон не видит — нет сетевого канала
  («Custom connectors connect from Anthropic's cloud, not from your local device»).
- **Один канал на Desktop+Code+телефон не существует.** Самый широкий: remote MCP connector
  через claude.ai = Desktop + телефон (но Code всё равно без виджета). Универсальный по всем
  поверхностям — только **standalone HTML-файл**.

## Как Claude выбирает канал (без угадывания среды)

Смотри не «какая среда», а **есть ли инструмент `mcp__visualize__show_widget`**:
1. доступен → widget-режим (Desktop) + параллельно HTML-файл;
2. нет (ToolSearch пуст) → только standalone HTML-файл.
Запасной сигнал: `$env:CLAUDE_CODE_ENTRYPOINT` (`claude-desktop` → виджет есть).

## Связано

- Скилл `understanding-map` (`~/.claude/skills/understanding-map/`) — карта понимания через
  оба канала (`tools/render_map.py`: widget + standalone), хук-детектор проактива
  `scripts/understanding-map-detector.ps1`.
- MCP-app прототип (для Desktop Chat / будущего remote): `C:\Users\Public\understanding-mcp\`.
- Баг ext-apps#671 — iframe MCP Apps иногда не строится при успешном `resources/read`.

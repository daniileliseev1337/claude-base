# Session report — 2026-06-29 — Скилл understanding-map (карта понимания через show_widget)

Продолжение виджет-моста (сессии 2026-06-26/27/28). Среда: Claude Code внутри Claude Desktop
(вкладка Code, `CLAUDE_CODE_ENTRYPOINT=claude-desktop`). Машина DANIILPC, кириллица в путях,
роль ПК — хаб (`.developer-marker` есть).

## Что сделано (итог)

Развернулась цель: с «MCP-app мост» на «виджеты там, где работаю (Code/VS Code/файл)». Нашли,
что нужный канал — встроенный **`show_widget`** (MCP `visualize`), а не самодельный MCP-сервер.
Оформили это в переиспользуемый скилл.

Создан скилл `~/.claude/skills/understanding-map/`:
- `SKILL.md` — слои 1-2: триггеры (реактив + проактив), decision-дерево выбора канала.
- `tools/render_map.py` — детерминированный генератор «карты понимания» из JSON в HTML,
  2 режима: `widget` (CDS-фрагмент под show_widget) и `standalone` (чертёжный лист, mobile,
  ГОСТ-штамп). Сквозной принцип skill-development: рендер — кодом, не каждый раз заново.
- `examples/sample_map.json` — few-shot формат (все 3 зоны ok/as/pe) + dogfood-контент.
- `triggers.txt` / `reminder.txt` — UTF-8 sidecar для хука.

Хук проактива `~/.claude/scripts/understanding-map-detector.ps1` (UserPromptSubmit, по образцу
`grilling-detector.ps1`): на содержательную/неоднозначную задачу впрыскивает напоминание
предложить карту. Зарегистрирован в `settings.json` (3-м в UserPromptSubmit). Само-фильтр в
reminder против шума.

## Факты (проверено, не из головы)

- `show_widget` рендерит виджет в окне Claude Code (вкладка Code в Desktop) — подтверждено
  владельцем визуально. `render_map.py` widget-режим показан через show_widget вживую.
- `show_widget` НЕ существует в VS Code-расширении (ToolSearch пуст — проверил тамошний Claude).
  Привязан к `entrypoint=claude-desktop`; в `claude mcp list` его нет (инжект среды, не конфиг).
- Claude Code не хост MCP Apps (by design) + мобайл только remote — подтверждено `claude-code-guide`
  (opus) по докам. Детали в `memory/reference_widget_render_channels.md`.
- standalone-режим проверен playwright (desktop 1280 + mobile 390) — чертёжный лист рендерится,
  адаптив работает. Файл отдан владельцу на телефон (`Desktop\карта-понимания.html`).
- Хук протестирован через файловый stdin-redirect: hit → reminder, no-hit → пусто.

## Где сломался / грабли

- **graphify-граф не построен** на этом ПК (`no graph at graph.json`) — query-before-build
  сделал fallback'ом по списку скиллов (дубля нет).
- **Edit settings.json по отступам не прошёл** (ConvertTo-Json форматирование + `&`
  вместо `&`). Решение: программная правка через `ConvertFrom-Json`/`ConvertTo-Json -Depth 20`
  с бэкапом `.bak` и валидацией. Грабля для памяти: settings.json правит надёжнее кодом.
- **Тест хука завис на 2 мин**: PowerShell-пайп `'json' | & script` передаёт ОБЪЕКТЫ, а хук
  читает raw stdin (`[Console]::In.ReadToEnd()`) → виснет ожидая консоль. Правильный тест —
  файловый redirect: `cmd /c "powershell -File hook.ps1 < input.json"`. Грабля для harvest.

## Уроки (в скилл / память)

- Канал виджетов в Claude Code = `show_widget` (Desktop-only), не MCP-app. MCP-app остаётся
  для Desktop Chat / будущего remote (телефон). Универсальный канал — только standalone HTML.
- Детект канала — по наличию инструмента `mcp__visualize__show_widget`, не по «угадыванию среды».
- Паттерн хука-детектора (ASCII .ps1 + UTF-8 sidecar triggers/reminder, fail-open) переносим
  на любой проактив-скилл.

## Открыто / дальше

- Распространение: скилл готов к push в claude-base (хаб). Финальный push — за владельцем.
- У сотрудников на не-Desktop (CLI/VS Code) сработает только standalone-режим (деградирует ок).
- Возврат правок: show_widget шлёт через `sendPrompt` (текст в чат) vs структурный
  `app.sendMessage` в MCP-app — оценить на практике.
- Судьба `understanding-mcp` (Stdio-сервер): развивать для remote/телефона или заморозить.
- Настроить детект-триггеры хука под реальный поток (риск шума) — по обратной связи.

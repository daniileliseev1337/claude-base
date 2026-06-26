# Канал доставки виджета: MCP App (Apps SDK) — «show widget в чате»

Источник: skill build-mcp-app (mcp-server-dev plugin), прочитан 2026-06-27.

## Что это
«Show widget» в десктопном Claude Code = MCP App. MCP-сервер регистрирует:
- **tool** с `_meta.ui.resourceUri: "ui://..."` — хендлер возвращает ДАННЫЕ (text/JSON), не HTML;
- **resource** (`ui://...`, mime `RESOURCE_MIME_TYPE = "text/html;profile=mcp-app"`) — отдаёт HTML виджета.
Хост рендерит HTML в **iframe-песочнице inline в чате**, прокидывает данные через `ontoolresult`.

## Почему критично для нашего виджета-моста
1. **Единый канал показа (унификация владельца)** — рендерится в чате Claude, без внешнего браузера/файла.
2. **Канал возврата правок ВСТРОЕН** — `app.sendMessage` (видимое сообщение) / `app.updateModelContext`
   (тихий контекст). Уровень (б), который раньше считали «отдельным большим куском», — в протоколе.
3. **standalone-HTML уже годится** — iframe CSP блокирует CDN/esm.sh («renders blank»), всё надо
   инлайнить server-side. Наш `*-standalone.html` (либы вшиты) уже CSP-совместим → готовый widget-resource.

## App-класс (widget ↔ host ↔ Claude)
- `app.ontoolresult` — данные от tool в виджет
- `app.sendMessage({role,content})` — инжект сообщения в беседу (возврат правок)
- `app.updateModelContext(...)` — тихое обновление контекста
- `app.callServerTool(...)` — вызвать другой tool сервера
- `app.getHostContext()` — тема/размеры/displayMode

## Цена / ограничения
- Нужен **MCP-сервер** (Node/TS: tool + resource), деплой: remote streamable-HTTP (tunnel) ИЛИ локальный MCPB-bundle.
- iframe **CSP жёсткий**: нет произвольных origin, нет window.open (→ app.openLink), нет DOM хоста.
- Нужен **хост с apps-surface**: Claude Desktop / desktop Claude Code — да; **VSCode-расширение — ПОД ВОПРОСОМ** (проверить через claude-code-guide перед стройкой).
- Тест в Desktop: конфиг через mcp-remote; агрессивный кэш ресурсов (полный перезапуск после правки HTML).

## Вывод для дизайна
Развилка канала доставки виджета:
- **A. HTML-файл** (что есть) — просто, открывается в браузере; НЕ в чате, нет авто-возврата.
- **B. MCP App** — в чате, унификация, возврат встроен; цена — MCP-сервер + apps-surface хост.
Рекомендация: целиться в **B** как архитектуру моста (решает унификацию + возврат), переиспользуя
standalone-HTML как widget-resource; движок графа (mermaid лёгкий / React Flow тяжёлый) — ВНУТРИ виджета.
Первый шаг — проверить apps-surface в целевой среде, затем минимальный MCP-сервер с одним tool+resource.

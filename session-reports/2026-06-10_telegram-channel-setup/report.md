# 2026-06-10 — Установка Telegram-канала Claude Code (домашний ПК)

## Задача
Развернуть Telegram-канал Claude Code по локальной инструкции с рабочего стола:
бот отвечает как Claude Code, доступ с телефона. Канал живёт на одной машине.

## Что сделано (машинная часть — полностью)
1. Плагин `telegram@claude-plugins-official` v0.0.6 установлен через CLI:
   `claude plugin install telegram@claude-plugins-official` (scope: user) —
   интерактивная сессия не понадобилась.
2. Токен бота записан напрямую в `~/.claude/channels/telegram/.env`
   (`TELEGRAM_BOT_TOKEN=...`) — README плагина явно разрешает ручную запись,
   `/telegram:configure` делает то же самое.
3. **Bun** (пререквизит MCP-сервера канала, в локальной инструкции отсутствовал!)
   установлен: `npm install -g bun` → 1.3.14 в `%APPDATA%\npm` (в PATH).
   npm-постинсталл не отработал сам — бинарник-заглушка; лечится
   `cd node_modules/bun && node install.js`.
4. Зависимости сервера прогреты: `bun install` в папке плагина
   (grammy 1.41.1, MCP SDK 1.27.1).
5. Верификация сети: `getMe` через corp-прокси из Bun fetch → 200, бот виден.

## Итог: канал РАБОТАЕТ (подтверждено пользователем)
- Окно канала запущено из сессии через `Start-Process powershell` — окно
  унаследовало прокси-env, пароль заново не понадобился.
- Пейринг выполнен вручную правкой `access.json` + маркер в `approved/`
  (скилл `/telegram:access` в сессии не подгрузился — но его SKILL.md
  документирует ручную процедуру, сделано по ней).
- Политика переведена на `allowlist` (один пользователь).
- md-инструкция с токеном удалена с рабочего стола.

## Где сломалось / уроки
- **Инструкция не упоминала Bun** — без него канал молча не стартует
  (`.mcp.json` плагина: `command: "bun"`). Проверять пререквизиты плагина
  по его README, а не только по локальной шпаргалке.
- `npm install -g bun` на Windows может оставить бинарник-заглушку
  («postinstall script was not run») — лечение: `node install.js` в пакете.
- `curl.exe` (Schannel) через corp-прокси даёт exit 35 на HTTPS без `-k` —
  это проверка отзыва сертификата, а не блокировка: Node/Bun fetch через
  тот же прокси работают штатно. Не делать вывод «API заблокирован» по curl.
- PowerShell-tool сессия в Claude Code зависла после `claude plugin install`
  (все последующие команды уходили в фон и висли) — обход: Git Bash
  с явным `PATH=/usr/bin:/bin` (в этом окружении PATH сломан, `ls`/`cat`
  без него не находятся).
- `claude plugin list` из субшелла тоже висит — состояние установленных
  плагинов надёжнее читать из `~/.claude/plugins/installed_plugins.json`.
- **Скрипты из claude-base несли Mark-of-the-Web** (все 4 файла в `~/.claude/bin/`):
  при политике RemoteSigned PowerShell отказывался запускать Set-Proxy.ps1
  («не имеет цифровой подписи»). Лечение одноразовое:
  `Get-ChildItem ~\.claude\bin | Unblock-File`. Видимо, метку ставит установщик
  base (zip-скачивание) — кандидат в фикс инсталлера.
- **ГЛАВНЫЕ грабли: `claude plugin install` ставит плагин ВЫКЛЮЧЕННЫМ**
  (`Status: ✘ disabled` в `claude plugin list`). Сессия с `--channels` молча
  игнорирует выключенный плагин: TUI грузится, все обычные MCP стартуют,
  а канал — нет, без единой ошибки. Лечение: `claude plugin enable
  telegram@claude-plugins-official` + перезапуск сессии. Диагностика:
  смотреть `claude plugin list` и отсутствие `mcp-logs-plugin-*` в
  `AppData/Local/claude-cli-nodejs/Cache/<proj>/`.
- Поллингом бота владеет ОДИН сервер (lock-файл `channels/telegram/bot.pid`);
  новый сервер при старте убивает старого владельца и забирает поллинг.
  «Бот печатает и молчит» = поллит сервер сессии БЕЗ `--channels`
  (входящее принято, но не маршрутизируется). Проверка владельца: PID из
  bot.pid → чья цепочка родителей (claude с `--channels` или нет).
- `taskkill`/`tasklist` с флагами из Git Bash — экранировать `//PID`
  (MSYS-конвертация путей съедает `/PID`).

## Автозапуск при входе в систему (добавлено по просьбе пользователя)
- `shell:startup\start-telegram-channel.cmd` → `~/.claude/bin/local-telegram-channel.ps1`
  (локальный, `local-` префикс, в git не уходит).
- Пароль прокси — DPAPI-файл `~/.claude-proxy.pass` (расшифровка только этим
  пользователем на этом ПК); host/user — из `~/.claude-proxy.json`. Пароль при
  входе НЕ спрашивается. Сброс: удалить .pass, скрипт спросит и пересохранит.
- Скрипт перед запуском canale сам делает `claude plugin enable telegram@...`
  (см. грабли ниже) и выставляет прокси-env.

## Ещё грабли (вторая волна)
- **Sync базы затирает enable плагина:** merge-хук переписывает
  `enabledPlugins` в `settings.json` из git-файла `settings.shared.json`,
  где telegram нет → плагин «сам» выключается после каждого синка. В shared
  добавлять нельзя (канал должен жить на одном ПК). Локальный обход:
  re-enable в автозапуск-скрипте прямо перед стартом claude.
- **PSModulePath от pwsh7 ломает PS 5.1:** окно, порождённое из pwsh-сессии,
  наследует PSModulePath → `Microsoft.PowerShell.Security` не грузится →
  падают ConvertTo/From-SecureString (DPAPI). Лечение: `set "PSModulePath="`
  в стартовом cmd. При реальном логоне окружение чистое, но защита нужна.
- **PS 5.1 не читает UTF-8 без BOM:** кириллица в .ps1 ломает парсер.
  Локальные .ps1 — только ASCII (или UTF-8 с BOM).
- **taskkill без `//T` оставляет дерево:** убитый claude оставил bun-серверы
  зомби, они продолжали поллить бота («печатает и молчит» в новой форме).
  Убивать канал — только `taskkill //PID <ps> //F //T`.
- Из Git Bash флаги Windows-утилит экранировать: `//PID`, `//F`, `//T`.

## Источники
- Локальная инструкция на рабочем столе (удалена — содержала токен).
- README + skills плагина: `~/.claude/plugins/cache/claude-plugins-official/telegram/0.0.6/`.

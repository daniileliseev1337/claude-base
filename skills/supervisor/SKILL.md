---
name: supervisor
description: >
  Надзор за АВТОНОМНЫМ Claude официальными средствами — авто-одобрение/блокировка его же
  действий по правилам. Триггеры: «пусть Claude работает сам, но под надзором»,
  «авто-одобрение headless-воркера», «блокируй опасные команды агента», «Telegram-алерт
  на опасное действие», «надзор за оркестрацией/фоновым прогоном», «supervised
  semi-autonomous», «canUseTool арбитр», «пульт с телефона» (одобрять живую сессию
  удалённо). Два слоя: (1) авто-арбитр (headless, официальный canUseTool SDK) — рутину
  пропускает, опасное/неизвестное deny+escalate; (2) пульт remote-control — человек
  одобряет живую сессию с телефона/браузера. НЕ для полноценной песочницы/syscall-изоляции
  (это грубая сеть безопасности, не тюрьма) и не для правки самого Claude Code.
---

# supervisor — надзор за автономным Claude (официальными средствами)

Полуавтономный Claude под контролем — только официальные механизмы Claude Code
(в рамках подписки, без reverse-engineering, без стороннего SaaS). Код: `tools/`.

## Когда какой слой
- **Фоновый/ночной headless-прогон, никто не смотрит** → Слой 1 (авто-арбитр).
- **Хочешь сам одобрять живую сессию с телефона/браузера** → Слой 2 (пульт), см. [REMOTE_CONTROL.md](REMOTE_CONTROL.md).

## Слой 1 — авто-арбитр (headless)
Перед каждым tool-call воркера SDK спрашивает `can_use_tool` (`tools/arbiter.py`) → `rules.decide()`:
- **safe** (Read/Glob/Grep/git status/поиск…) → allow молча, не дёргает;
- **опасное** (`rm -rf`/`rm -r -f`, `git push --force`, `git reset --hard`, `chmod 777`, `mkfs`, `dd if=`, обёртки `bash -c`/`powershell -c`, пайп-в-шелл `… | bash`, drop database/table) и **неизвестный tool** → **deny + escalate** (Telegram/лог), НИКОГДА не тихий allow;
- ошибка в правилах → **deny by default** (fail-safe).

Запуск:
```
cd tools
python arbiter.py "<задача воркеру>"
```
Зависимость: `claude-agent-sdk` (optional в `mcp-manifest.json` → ставит `/sync-base`, или `pip install claude-agent-sdk`).
Env (опц.): `SUPERVISOR_TG_TOKEN`+`SUPERVISOR_TG_CHAT` — Telegram-алерт; `SUPERVISOR_LOG` — путь аудит-лога. Без Telegram эскалации идут в stdout (`[ESCALATE] …`) И в durable-лог (пишется ПЕРВЫМ, до сети).

Тесты (18): `cd tools && python -m pytest tests\ -v` → 18 passed (13 rules + 5 arbiter).

## Слой 2 — пульт (живые интерактивные сессии)
`claude remote-control` — заходишь с телефона/браузера (claude.ai/code или Claude mobile app) и **сам** одобряешь каждое действие. Approval здесь делает ЧЕЛОВЕК (официального авто-approve для интерактивных сессий нет — это работа Слоя 1). Полная процедура + приватность-caveat (discovery видит все сессии аккаунта) — [REMOTE_CONTROL.md](REMOTE_CONTROL.md).

## Граница гарантии (честно — не переоценивать)
Это **грубая сеть безопасности, НЕ песочница**. Слой 1 надёжно гейтит **prompt-worthy** вызовы воркера, которого САМ запускает (`_options()` пиннит `permission_mode="default"` + изолирует настройки `setting_sources=[]`, чтобы SDK не авто-разрешил вызовы через `bypassPermissions`/`acceptEdits` или ambient `permissions.allow`). Он **НЕ** гейтит вызовы, которые SDK авто-разрешает внутри себя, и **НЕ** надзирает за сессиями, которые арбитр не запускал — для «каждого вызова без исключений» нужен `PreToolUse`-hook (отдельный апгрейд; стаб `_keepalive_hook` заложен). Не заявлять «перехватывает каждый вызов», пока hook не подключён. Не заменяет syscall-изоляцию/ФС-ограничения.

## Правка правил
`rules.decide(tool_name, tool_input) -> {"action": "allow"|"deny"|"escalate", "reason": str}` — чистая логика. Меняешь правило → правь `tools/rules.py` + тест в `tools/tests/test_rules.py` (TDD: сперва падающий тест).

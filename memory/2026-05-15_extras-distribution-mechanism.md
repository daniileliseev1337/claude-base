# Кейс: механизм распространения extras (MCP + Python pkgs) через manifest

**Дата:** 2026-05-15
**Контекст:** После handoff Daniil-а с DELISEEV-PC (autocad-mcp +
Python-stack из 7 пакетов) пользователь запросил «чтобы это
автоматически подтягивалось через auto-sync на все ПК». Я сделал
push back и предложил гибрид «manifest + ручной запуск с
подсказкой» вместо полной автоматизации.

## Главное

В `~/.claude/` появилась пара:
- `mcp-manifest.json` — реестр Python-пакетов и MCP-серверов
- `scripts/setup-extras.ps1` — идемпотентный установщик читающий
  manifest
- `scripts/auto-pull.ps1` дополнен diff-проверкой и уведомлением

Когда owner редактирует manifest и пушит — другие ПК при auto-pull
видят PENDING-уведомление в логе. Claude в первой реплике сессии
по правилу «auto-sync статус» подсказывает пользователю запустить
setup-extras. Сотрудник запускает руками за 30 секунд.

## Push back: почему не полная автоматизация

Запрос пользователя дословно: «чтобы это всё подтяговолось через
автосинк». Дословное исполнение — установка из `SessionStart`
hook'а. Это **невозможно** по трём причинам:

### 1. Timeout 30 секунд для hook'а

`paddlepaddle` 105 МБ + pip resolution = 5+ минут. Hook будет убит
посередине. На машине останется частичная установка, при следующем
запуске Claude — half-broken state.

Увеличить timeout до 600 сек тоже плохо: пользователь не понимает
почему Claude **не отвечает** после `claude` команды.

### 2. Auto-classifier security boundary

Системные установки (`winget install`, `pip install -g`) от
agent-инициированных процессов **блокируются**. На моей машине
сегодня auto-classifier заблокировал `winget install Python.Python.3.12`
при автоматическом запуске. Пользователь сам выполнил руками — это
работает потому что **user-action**, не agent.

Hook не агент в строгом смысле (это shell script вызванный Claude
Code), но классификатор может расширить запрет на любые
non-explicitly-authorized системные действия в будущем.

### 3. UX

Пользователь открывает Claude → внезапно начинается скачивание
1+ ГБ. Нет подтверждения, нет понимания зачем. Это **плохой
дизайн** независимо от технических деталей.

## Компромисс: трёхшаговая система

### Шаг 1 — Manifest (полная auto-sync)

`mcp-manifest.json` — обычный файл, попадает в whitelist `.gitignore`.
Auto-pull разносит его на все ПК **автоматически**. Это **уже
полноценный auto-sync**.

### Шаг 2 — Diff-уведомление (полу-auto)

`auto-pull.ps1` после успешного pull считает hash manifest'а,
сравнивает с marker'ом `~/.claude/.local-state/setup-extras.applied`.
Если разные — пишет в `auto-sync.log`:
```
extras-diff PENDING: marker missing -- setup-extras never run
extras-diff PENDING: manifest changed (a1b2c3 -> d4e5f6)
extras-diff: up-to-date
```

Claude в первой реплике сессии по правилу из CLAUDE.md USER EXTENSIONS
«auto-sync статус в начале сессии» подхватывает эту строку и
**подсказывает** пользователю.

### Шаг 3 — Ручной запуск (явное согласие)

Пользователь **одобряет**: «да, давай поставим». Claude через Bash
запускает `setup-extras.ps1`. Скрипт идемпотентно ставит **только
недостающее** (по diff'у manifest vs `claude mcp list`/`importlib.util.find_spec`).

После успеха — обновляет marker с новым hash. Следующий auto-pull
видит match, PENDING не пишется.

## Эффект для пользователя

| Сценарий | Что происходит |
|----------|----------------|
| **Owner редактирует manifest, добавляет новый MCP** | Push в claude-base |
| **Любой сотрудник открывает Claude после этого** | auto-pull подтягивает manifest. auto-sync.log: `extras-diff PENDING: manifest changed`. Claude в первой реплике: «появился новый MCP, запустить установку?» |
| **Сотрудник: «да»** | Claude запускает setup-extras.ps1, ставит **только новое**, остальное skip как уже установленное. ~30 секунд |
| **Сотрудник: «не сейчас»** | Ничего не происходит. Marker не обновляется. На следующей сессии Claude напомнит снова |

## Структура manifest

```json
{
  "$schema_version": 1,
  "python_user_packages": [
    {
      "name": "matplotlib",       // pip-name
      "import_name": "matplotlib", // optional, если ≠ pip-name (e.g. paddlepaddle → paddle)
      "purpose": "...",
      "min_python": "3.10",
      "max_python": "3.12",
      "size_mb": 30                // optional, для disk estimate
    }
  ],
  "mcp_servers": [
    {
      "name": "word",
      "method": "uvx",              // или "github-zip-uv"
      "install_args": [...],
      "register_args": [...]
    },
    {
      "name": "autocad-mcp",
      "method": "github-zip-uv",
      "source_url": "...zip",
      "extracted_name": "...",
      "install_dir": "$env:USERPROFILE\\.claude\\mcp-servers\\autocad-mcp",
      "register_args": [..., "{install_dir}\\.venv\\Scripts\\python.exe", "-m", "autocad_mcp"],
      "post_install_note": "...if AutoCAD: run APPLOAD..."
    }
  ]
}
```

## Уроки

### Урок: «full auto через hooks» — анти-паттерн

В попытке угодить запросу «всё автоматически» легко согласиться
запихнуть установку в hook. Это технически **возможно** с
костылями (длинный timeout, обход classifier'а), но **плохо** по
сути: непрозрачно, легко ломается, hard-to-debug.

**Правильнее**: разделить «распространение данных» (полностью auto
через git) и «применение действий на машине» (явный пользовательский
запуск с подсказкой).

### Урок: pip-name vs import-name

Не все пакеты на PyPI имеют то же имя для `import`. Примеры:
- `paddlepaddle` → `import paddle`
- `Pillow` → `import PIL`
- `beautifulsoup4` → `import bs4`
- `pyyaml` → `import yaml`

Если делаем проверку «установлен ли пакет» через
`importlib.util.find_spec()` — нужно использовать **import-name**,
не pip-name. Manifest учитывает это полем `"import_name"`.

### Урок: marker per-machine для idempotency

Marker файл с manifest_hash в `.local-state/` — простой способ:
- (a) не запускать ненужное при повторе
- (b) детектить разницу когда manifest обновился
- (c) держать **локальным** (в `.gitignore`, не пушится)

Альтернатива через `claude mcp list` diff каждый раз — медленнее
(вызов внешнего процесса) и менее надёжна (что если claude command
не доступна на свежем ПК до конца установки).

## Связанные документы

- `~/.claude/mcp-manifest.json` — реестр
- `~/.claude/scripts/setup-extras.ps1` — установщик
- `~/.claude/scripts/SETUP-EXTRAS-README.md` — инструкция
  для сотрудников
- `~/.claude/scripts/auto-pull.ps1` — добавлена diff-проверка
- `~/.claude/.gitignore` — `.local-state/` исключён, `mcp-manifest.json`
  whitelist
- `~/.claude/session-reports/2026-05-15_master-struktura-projektov-naming/INSTRUCTIONS_FOR_MAIN_PC.md` —
  изначальный handoff Daniil-а

## Открытые вопросы

1. **`claude-lite-instaler` Stage 8** — для **новых** установок
   запускать `setup-extras.ps1` автоматически как часть Install.ps1.
   Отложено до следующей сессии, не критично для текущей задачи.
2. **macOS support в manifest** — сейчас manifest заточен под
   Windows (`winget install`, `pywin32`). Для Mac понадобятся отдельные
   методы установки (`brew install`, разные имена пакетов). Когда
   подключим coauthor на Mac с Claude Code — расширим.
3. **Дополнительный pip-источник** в случае private packages — пока
   все наши packages с public PyPI, проблемы нет. Если когда-нибудь
   появятся private dependencies — добавим `index_url` в manifest.

# setup-extras — установка дополнительных MCP и Python-пакетов

## Что это

Механизм автоматического распространения **установок** (Python-пакетов
и MCP-серверов) между ПК команды.

Через обычный `git`/`auto-sync` распространяются **только файлы**.
Системные установки (`winget install Python`, `pip install`, клонирование
MCP-сервера) — не файлы. Этот механизм закрывает разницу.

## Как это работает

1. **Центральный реестр** — `~/.claude/mcp-manifest.json`. Owner базы
   (Даниил) редактирует этот файл когда хочет добавить новый MCP-сервер
   или Python-пакет для всей команды.
2. **Auto-pull** на каждом ПК подтягивает обновлённый manifest при
   следующем старте Claude Code. Также `auto-pull.ps1` сравнивает hash
   manifest'а с **marker'ом** локального состояния
   (`~/.claude/.local-state/setup-extras.applied`). Если они расходятся —
   пишет в `auto-sync.log` строку `extras-diff PENDING: ...`.
3. **Claude в первой реплике** сессии (по правилу «auto-sync статус
   в начале сессии») читает tail `auto-sync.log` и **подсказывает**
   пользователю: «обнаружены новые extras, готов запустить установку?»
4. **Сотрудник** (с явного согласия) запускает:
   ```powershell
   pwsh ~/.claude/scripts/setup-extras.ps1
   ```
   Скрипт идемпотентно ставит только **недостающее** (пакеты, MCP).
   После успеха обновляет marker — следующий `auto-pull` уже не
   будет писать `PENDING`.

## Зачем не делать установку из hook'а автоматически

Хотелось бы, но **технически нельзя**:

- **SessionStart timeout 30 секунд.** Установка paddlepaddle 105 МБ +
  pip resolution занимает 5+ минут — hook будет убит посередине, на
  машине останется частичная установка.
- **Auto-classifier** Claude Code блокирует системные установки
  (`winget install`, `pip install -g`) из агент-инициированных
  процессов. Hook не агент по сути, но классификатор может среагировать.
- **UX**: пользователь открывает Claude и **внезапно** начинается
  скачивание гигабайт. Без подтверждения это нагрузка на диск и сеть
  без понимания зачем.

Поэтому компромисс: **уведомление в начале сессии + ручной запуск**
сотрудником. Это занимает 30 секунд внимания, но **прозрачно**.

## Как добавить новый MCP-сервер в manifest

1. Открой `~/.claude/mcp-manifest.json` на своей машине.
2. Добавь объект в массив `mcp_servers`:

   **Если MCP запускается через uvx (Python-пакет в PyPI):**
   ```json
   {
     "name": "my-new-mcp",
     "purpose": "Что делает",
     "method": "uvx",
     "install_args": ["my-mcp-package-name"],
     "register_args": ["-s", "user", "--", "uvx", "my-mcp-package-name"]
   }
   ```

   **Если MCP клонируется из GitHub (типа autocad-mcp):**
   ```json
   {
     "name": "my-github-mcp",
     "purpose": "Что делает",
     "method": "github-zip-uv",
     "source_url": "https://github.com/owner/repo/archive/refs/heads/main.zip",
     "extracted_name": "repo-main",
     "install_dir": "$env:USERPROFILE\\.claude\\mcp-servers\\my-github-mcp",
     "register_args": ["-s", "user", "--", "{install_dir}\\.venv\\Scripts\\python.exe", "-m", "my_mcp_module"],
     "post_install_note": "Optional manual step description"
   }
   ```

3. Закоммить + push:
   ```powershell
   cd ~/.claude
   git add mcp-manifest.json
   git commit -m "manifest: add my-new-mcp"
   git push
   ```

4. На других ПК при следующем старте Claude `auto-pull` подтянет
   manifest и напишет `extras-diff PENDING`. Сотрудники запустят
   `setup-extras.ps1` чтобы получить новый MCP.

## Как добавить новый Python-пакет

Аналогично — в массив `python_user_packages`:
```json
{
  "name": "my-pkg",
  "purpose": "Зачем",
  "min_python": "3.10",
  "max_python": "3.12"
}
```

Если pip-имя ≠ import-имя (как `paddlepaddle` → `import paddle`),
добавь поле `"import_name": "paddle"`.

## Параметры setup-extras.ps1

| Флаг | Что делает |
|------|------------|
| `-Yes` | Не спрашивать confirmation (для CI/non-interactive) |
| `-DryRun` | Показать что было бы установлено, ничего не менять |
| `-SkipPython` | Пропустить установку Python 3.12 (если он уже стоит другим путём) |

## Файлы

| Файл | Назначение |
|------|------------|
| `~/.claude/mcp-manifest.json` | Реестр пакетов/MCP, общий для всех ПК (auto-sync) |
| `~/.claude/scripts/setup-extras.ps1` | Установщик, читает manifest |
| `~/.claude/.local-state/setup-extras.applied` | Marker per-PC (in .gitignore, не синкается) |
| `~/.claude/auto-sync.log` | Лог auto-pull и setup-extras |

## Связанные документы

- `~/.claude/CLAUDE.md` — главный manifest, правила работы
- `~/.claude/memory/2026-05-15_extras-distribution-mechanism.md` —
  кейс с обоснованием архитектуры
- `~/.claude/session-reports/2026-05-15_master-struktura-projektov-naming/INSTRUCTIONS_FOR_MAIN_PC.md` —
  изначальный handoff Daniil-а с описанием стека autocad-mcp + Python

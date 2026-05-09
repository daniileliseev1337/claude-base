# Кейс: настройка SessionStart / SessionEnd hooks Claude Code на Windows

**Дата:** 2026-05-09
**Контекст:** Этап 3 миграции на v2 архитектуру — настройка auto-pull/push
hooks для синхронизации `~/.claude/` между ПК пользователя через GitHub
(`claude-base` репо).

> Кейс полезен при первой настройке Claude Code hooks с PowerShell-скриптами
> на Windows, особенно если имя пользователя содержит пробел / кириллицу.

## Главное

Цель — заставить Claude Code запускать `auto-pull.ps1` на старте сессии
и `auto-push.ps1` на завершении. Сами PowerShell-скрипты работали
корректно из консоли с первого раза. **Проблема была не в скриптах, а в
формате `settings.json` для hooks** — потребовалось 5 итераций фикса
прежде чем найти рабочую комбинацию.

## 5 ловушек, через которые мы прошли

### Ловушка 1 — `matcher: ""` для SessionStart не распознаётся

**Симптом:** Hook вообще не вызывается. `auto-sync.log` не появляется.
Внутри Claude Code сессии в логах никаких ошибок, тишина.

**Причина:** Claude Code v2.1.137-138 для `SessionStart` хука требует
явного значения matcher. Пустая строка (`""`) — не работает.

**Фикс:** matcher должен быть `"startup"` (новая сессия) или `"resume"`
(возобновление). Для покрытия обоих случаев — два блока в массиве:

```json
"SessionStart": [
  { "matcher": "startup", "hooks": [...] },
  { "matcher": "resume",  "hooks": [...] }
]
```

Для `SessionEnd` `matcher: "*"` работает корректно (match-all).

### Ловушка 2 — `%USERPROFILE%` не разрешается в `shell: "powershell"`

**Симптом:** Hook вызывается, но падает с ошибкой:
```
%USERPROFILE%\.claude\scripts\auto-pull.ps1 : Не удалось зарегистрировать
сервер "%USERPROFILE%". Все значения дополнительных...
```

**Причина:** `%USERPROFILE%` — это синтаксис cmd.exe для переменных
окружения. PowerShell видит это как буквальный текст, не разрешает.
Когда Claude Code запускает команду через `shell: "powershell"`, PS
получает строку без подстановки cmd-переменных.

**Фикс:** заменить на `$HOME` — это **PowerShell-built-in** переменная,
эквивалентная `$env:USERPROFILE` на Windows. Разрешается автоматически.

```json
"command": "$HOME\\.claude\\scripts\\auto-pull.ps1"
```

### Ловушка 3 — путь без `&` оператора и кавычек ломается на пробеле

**Симптом:** Даже с `$HOME` hook падает при имени пользователя с
пробелом (например, `C:\Users\Даниил ПК\`). Сообщение в стиле
`Имя "C:\Users\Даниил" не распознано как команда`.

**Причина:** PowerShell интерпретирует `$HOME\.claude\scripts\auto-pull.ps1`
как **выражение**, не команду. Без `&` оператора путь со пробелами
разрезается по аргументам.

**Фикс:** обернуть путь в кавычки и добавить `&`:

```json
"command": "& \"$HOME\\.claude\\scripts\\auto-pull.ps1\""
```

В JSON: `&`, пробел, `\"` (открывающая `"`), `$HOME`, `\\.` (один
backslash), путь, `\"` (закрывающая `"`).

### Ловушка 4 — `~/.claude/sessions/` зарезервирован Claude Code'ом

**Симптом:** Auto-push работает первый раз, но потом git клиент
сходит с ума: каждое close сессии генерирует commit с файлами
`sessions/27068.json`, `55040.json`, и т.п. Pull --rebase падает с
конфликтами от untracked файлов. 10+ авто-sync коммитов за минуты.

**Причина:** Claude Code сам пишет transient JSON-файлы состояния
сессий в `~/.claude/sessions/<id>.json`. Если у нас в whitelist
auto-push есть `sessions`, эти файлы воспринимаются как наши.

**Фикс:**

1. Переименовать **нашу** папку `sessions/` → `session-reports/`. Claude
   Code в `sessions/` не трогать.
2. В `auto-push.ps1` убрать `'sessions'` из managed paths whitelist,
   добавить `'session-reports'`.
3. В `.gitignore` добавить hard-block: `sessions/` и `**/sessions/`,
   чтобы даже случайный коммит не прошёл.

### Ловушка 5 — `git pull --rebase --autostash` зависает в hook context

**Симптом:** Auto-push успешно делает commit, логирует «commit ok»,
пишет «pulling before push...» — и на этом застревает. Скрипт убивается
по timeout (60 → 180 сек). Локальный коммит остаётся ahead origin/main,
не доходит до GitHub.

**Причина (гипотеза):** `git pull --rebase --autostash` в Claude Code
SessionEnd hook context зависает. Из обычного PowerShell тот же скрипт
отрабатывает за 2 секунды. В hook'е — не возвращается до timeout.
Возможно ждёт interactive prompt, или process tree Claude Code
вмешивается в I/O.

**Фикс:** **убрать** pull-перед-push из auto-push. Логика:

- Auto-push: `commit + push`. Если push отвергнут (race) — лог, скрипт
  завершается. Локальный коммит остаётся ahead.
- На следующем SessionStart auto-pull (`pull --rebase --autostash`) —
  **этот** работает! — подтянет origin и положит локальный коммит
  поверх.
- На следующем SessionEnd auto-push — push снова попробует, теперь
  пройдёт.

Это «eventually consistent» модель: при race с другим ПК — догонит за
один-два цикла. Для команды 1-2 человека на разных ПК — приемлемо.

После убирания pull-перед-push: commit + push занимает **4 секунды**,
ничего не зависает.

## Что в итоге работает

`settings.json` (финальный):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [{
          "type": "command",
          "command": "& \"$HOME\\.claude\\scripts\\auto-pull.ps1\"",
          "shell": "powershell",
          "timeout": 30
        }]
      },
      {
        "matcher": "resume",
        "hooks": [{ ...то же что startup... }]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "& \"$HOME\\.claude\\scripts\\auto-push.ps1\"",
          "shell": "powershell",
          "timeout": 60
        }]
      }
    ]
  }
}
```

`auto-push.ps1` (упрощённый):

```powershell
# 1. status check для managed paths
# 2. git add managed
# 3. git commit
# 4. git push origin main   ← сразу, БЕЗ pull-перед-push
# 5. log result
```

`auto-pull.ps1` (без изменений):

```powershell
git pull --rebase --autostash    ← работает в SessionStart, не зависает
```

## Уроки для следующих раз

1. **При настройке hooks Claude Code** — начинай с manual-теста
   скрипта (он работает или нет в обычной консоли). Если manual работает,
   а hook не работает — **проблема в settings.json формате**, не в скрипте.

2. **`%USERPROFILE%` в shell-командах PowerShell** — не работает.
   Используй `$HOME` или `$env:USERPROFILE`.

3. **Пути с пробелом или кириллицей** в shell-команде через PowerShell —
   обязательно `& "..."` (амперсанд + кавычки), даже если выглядит
   избыточно.

4. **Не используй имя `sessions/`** для своих папок в `~/.claude/` —
   занято Claude Code'ом.

5. **`git pull --rebase --autostash` в SessionEnd hook** — может
   зависнуть. Не делай pull-перед-push в этом контексте; полагайся на
   SessionStart-pull для conflict resolution.

6. **Whitelist в auto-push** должен быть **строгий**: только наши
   управляемые папки. Лучше потерять коммит-другой при race, чем
   запушить случайный transient файл Claude Code.

7. **Промежуточные log-метки** в hook-скриптах (`Write-SyncLog
   "stage X..."`) бесценны при отладке. Без них непонятно где скрипт
   зависает.

## Метрики кейса

- **5 итераций фикса** settings.json до рабочей версии.
- **3 архитектурных правки** (sessions→session-reports, убран
  pull-перед-push, taimout 60→180→60).
- **~3 часа отладки** на реальном ПК пользователя.
- **Финальный успех:** auto-pull <2 сек, auto-push 4 сек, end-to-end
  работает без зависаний.

Все правки задокументированы в commit-истории `claude-base` от
`78800b4` до `5100e74` (commits с префиксом `fix(...)`).

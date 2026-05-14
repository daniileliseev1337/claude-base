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

---

## Дополнение от 2026-05-12 — ловушка 6 (корпоративный прокси режет HTTP CONNECT)

> Появилась через 3 дня после первичной настройки, когда систему
> попробовали запустить на рабочем ПК за корп-прокси. Не часть
> первичных 5 ловушек, но напрямую ломает те же `auto-pull.ps1` /
> `auto-push.ps1`, поэтому фиксируется здесь.

### Симптом

На ПК с активным корп-прокси (например `scuf-meta.ru:10894`)
`Set-Proxy.ps1` корректно ставит прокси в env-vars текущей сессии,
smoke-test проходит (`HTTPS request through proxy ... OK (HTTP 200)`),
`claude: OK`, `uvx: OK`. Но **любой git-вызов** через тот же прокси
падает:

```
fatal: unable to access 'https://github.com/.../claude-base.git/':
Proxy CONNECT aborted
```

В частности:
- `Apply-ClaudeMd.ps1` Stage 7 падает на `git pull`.
- `auto-pull.ps1` при SessionStart молча отваливается (в `auto-sync.log`
  — `FAILED (exit=128)`).
- `auto-push.ps1` при SessionEnd не доносит коммит до GitHub.

Дополнительная путаница: **`Apply-ClaudeMd.ps1` маскирует сетевую
ошибку под merge-конфликт.** На любой `exit != 0` от `git pull` он
выводит «Likely a conflict in the USER EXTENSIONS section of CLAUDE.md»
и предлагает резолвить вручную через `git rebase --continue`. Это
сбивало с толку — реальный stderr git'а в логи не попадал.

### Причина

Корп-прокси (Cisco/Forcepoint/Microsoft Forefront/Squid с DLP-политикой)
часто настроены **пропускать обычные HTTPS-запросы** (GET, POST к
веб-сайтам), но **блокировать метод HTTP CONNECT** — именно он
используется для туннелирования произвольного TLS через прокси, и
именно его использует git/curl при `https://github.com/...`. Политика
безопасности обычно объясняется так: GET — это документы, CONNECT —
это «открытый туннель куда угодно», DLP не может его инспектировать.

Тогда же: **Claude сам нуждается в прокси** для `api.anthropic.com` —
без прокси из корп-сети наружу не выйдет вообще. То есть «просто
отключить прокси» — не вариант, ломает Claude.

### Фикс

Локально для команды git обнулить прокси через
`-c http.proxy="" -c https.proxy=""`. Эта опция git перебивает
`HTTP_PROXY`/`HTTPS_PROXY` env-vars и `git config http.proxy` **только
для одной вызванной команды**. Env-vars родительского процесса не
трогаются — Claude продолжает ходить к Anthropic API через прокси, а
git идёт мимо прокси прямо в GitHub (если прямой выход разрешён
сетью без прокси, что обычно так на корп-ПК — там блокируют
**неавторизованный** трафик, но не сам факт исходящих соединений).

В `~/.claude/scripts/auto-pull.ps1`:
```powershell
$output = & git -c http.proxy="" -c https.proxy="" pull --rebase --autostash 2>&1
```

В `~/.claude/scripts/auto-push.ps1`:
```powershell
$pushOut = & git -c http.proxy="" -c https.proxy="" push origin main 2>&1
```

В `Apply-ClaudeMd.ps1` — три места (CASE 1 fresh clone, CASE 2 pull,
CASE 4 migration clone). В CASE 2 параллельно заменена шаблонная
ошибка про USER EXTENSIONS на разбор stderr git'а с тремя ветками:
`Network/proxy error` (matches `Proxy CONNECT aborted|Could not resolve
host|Failed to connect|unable to access`), `Merge conflict` (matches
`CONFLICT|merge conflict|could not apply`), `Unknown`. Реальный git
output выводится в лог.

### Когда применять

- **Если корп-прокси пропускает HTTPS GET и режет CONNECT** — фикс
  обязателен.
- **Если прямой выход в GitHub разрешён без прокси** (домашний ПК,
  персональная сеть) — фикс безвреден: `-c http.proxy=""` просто
  игнорирует пустую строку, git идёт стандартным путём.
- **Если корп-прокси режет всю сеть наружу полностью** (нет прямого
  выхода к GitHub даже без прокси) — фикс **не поможет**, нужен
  Вариант A: скачивание ZIP вручную через тот же прокси (HTTPS GET
  пройдёт), без auto-sync. Так сделано на ПК Apoliakov.

Поэтому `-c http.proxy=""` кладётся в скрипты **по умолчанию** — не
делает хуже ни в одном из сценариев.

### Подтверждение в боевых условиях

На рабочем ПК с прокси `scuf-meta.ru:10894 (user: danzombi)` после
правки `Apply-ClaudeMd.ps1` Stage 7 прошёл с `[OK] ~/.claude/ updated
from claude-base`. Это значит `git pull` через `-c http.proxy=""`
обошёл CONNECT-блокировку при включённом прокси.

### Коммиты

- `claude-base@8efec4b` — `auto-pull.ps1` + `auto-push.ps1` (2 строки).
- `claude-lite-instaler@b81a5d4` — `Apply-ClaudeMd.ps1` (3 правки
  прокси + классификация ошибок pull).

### Урок 8 для следующих раз

**Корп-прокси и git** — если прокси режет HTTP CONNECT (типично для
DLP-настроенных корп-прокси), git/curl ломается на `Proxy CONNECT
aborted`, хотя обычный HTTPS GET проходит. Лекарство —
`git -c http.proxy="" -c https.proxy=""` в нужных командах. Env-vars
родителя не трогать — другие приложения (Claude к API Anthropic) от
прокси зависят.

**Урок 9 для следующих раз** — не маскировать сетевую ошибку под
merge-конфликт. Любой `if (exit_code != 0) { print "merge conflict";
}` после `git pull` — потенциальная ловушка диагностики. Лучше дать
git'у писать в консоль естественно + общая подсказка про две главные
причины (network vs merge), чем хитрить с захватом stderr (см. урок 10).

### Дополнение от 2026-05-12 (через 30 минут) — седьмая ловушка (PS 5.1 `2>&1`)

Сразу после правки в Apply-ClaudeMd (коммит `b81a5d4`) — повторный
прогон на рабочем ПК упал с `NativeCommandError`. Причина — наша
**собственная** правка:

```powershell
$pullOutput = & git -c http.proxy="" -c https.proxy="" pull --rebase --autostash 2>&1 | Out-String
```

Идея была хорошая — захватить stderr git'а в строку для regex-
классификации Network/Merge/Unknown. Реализация — кривая для
Windows PowerShell 5.1.

**Что происходит:** PowerShell 5.1 при `2>&1` на native exe (git/npm/
etc) оборачивает **каждую stderr-строку** в `ErrorRecord`
(`NativeCommandError` / `RemoteException`). git fetch при успешной
загрузке пишет в stderr нормальные progress-строки (`From
https://...`, `Counting objects:`, и т.п.). PowerShell это считает
ошибками. Под `$ErrorActionPreference = 'Stop'` (стандарт для
Apply-ClaudeMd) — первая stderr-строка прерывает скрипт даже когда
git вернул exit 0.

**Почему в hooks (auto-pull/auto-push) это не падает:** там
`$ErrorActionPreference = 'SilentlyContinue'` — NativeCommandError
проглатывается, скрипт продолжает.

**Фикс (коммит `5290252` в claude-lite-instaler):**

Убрать `2>&1 | Out-String`. Запускать git напрямую — stderr течёт
в консоль естественно (пользователь видит реальный git output).
Скрипт проверяет только `$LASTEXITCODE`. Сообщения об ошибке —
общие («see git output above + возможные причины»), без regex-
классификации.

### Урок 10 для следующих раз

**`2>&1` на native exec в Windows PowerShell 5.1 — ловушка.** Под
`ErrorActionPreference = 'Stop'` падает на любой stderr-line даже
при успешном exit code. Альтернативы:

1. **Не использовать `2>&1`** — просто запустить exec, проверить
   `$LASTEXITCODE`. Stderr идёт в консоль нативно. **Самый простой
   и робастный путь.**
2. Если **обязательно** нужно захватить stderr — обернуть в
   `cmd /c "... 2>&1"`. cmd собирает stderr в строку до того, как
   PowerShell успеет обернуть в ErrorRecord. Но кавычки сложно
   эскейпить, особенно если в команде есть свои `""`.
3. Локально установить `$ErrorActionPreference = 'Continue'` в блоке
   `try` вокруг exec — менее надёжно (зависит от версии PS).

Под PowerShell 7+ эта проблема не воспроизводится (там нативные
команды не оборачиваются в ErrorRecord), но мы целимся в стандартный
Windows PowerShell 5.1, который идёт из коробки.

---

## Дополнение от 2026-05-14 — восьмая ловушка (auto-push не догоняет ahead-origin коммиты)

> Обнаружено в первый день работы по новой политике «каждая сессия пишет
> session-report». Рабочий ПК (`R-090226727A`) накопил 2 локальных
> коммита, hook их видел и каждый раз выходил с `no managed changes`.

### Симптом

На рабочем ПК в `~/.claude/auto-sync.log`:
```
[2026-05-14 11:29:39] auto-push: start
[2026-05-14 11:29:39] auto-push: no managed changes
[2026-05-14 11:35:47] auto-push: start
[2026-05-14 11:35:47] auto-push: no managed changes
```

Hook отрабатывает на каждом SessionEnd, но **никогда** не пушит. При
этом `git log` показывает 2 коммита локально **ahead origin/main**:
```
92aaac8 (HEAD) auto-sync: session 2026-05-14 11:28 from R-090226727A
01cc78f         auto-sync: session 2026-05-13 17:55 from R-090226727A
0874823 (origin/main) ...
```

То есть коммиты сделаны (Claude в чате выполнил `git commit`), но
push никогда не прошёл — и hook их **не догоняет**.

### Причина

В `auto-push.ps1` логика была:
```powershell
foreach ($path in $Managed) {
    $status = & git status --porcelain -- $path
    if ($status) { $changedPaths += $path }
}
if ($changedPaths.Count -eq 0) {
    Write-SyncLog "no managed changes"
    exit 0     # <-- выход БЕЗ push
}
# ниже -- stage + commit + push
```

Проверка только **working tree** через `git status --porcelain`. Если
все изменения уже закоммичены (working tree чист), переменная
`$changedPaths` пуста, hook выходит до push'а.

**Сценарий приводящий к проблеме:**
- Пользователь или Claude в чате вручную выполнил `git commit` (например,
  чтобы зафиксировать session-report).
- `git push` упал (сеть, прокси CONNECT до фикса, истёкший PAT, и т.п.)
  или вообще не делался.
- Working tree становится чистым, hook видит «нет изменений» и выходит.
- Локальные коммиты остаются `ahead origin/main` навсегда — hook их
  не пушит на последующих SessionEnd, потому что повторно не выполняет
  push без новых изменений в working tree.

Комментарий в коде утверждал «next SessionEnd will retry push» — это
было **неверно**: retry происходил только при новых working-tree
изменениях, не при уже закоммиченных-но-не-запушенных.

### Фикс (коммит `fcb350f` в claude-base)

В `auto-push.ps1` добавлена проверка ahead-origin:

```powershell
if ($changedPaths.Count -eq 0) {
    # No working tree changes -- check if local commits are ahead of origin.
    # Quick fetch (safe in hook context -- unlike git pull --rebase).
    & git -c http.proxy="" -c https.proxy="" fetch --quiet origin main 2>&1 | Out-Null
    $aheadOut = & git rev-list --count origin/main..HEAD 2>$null
    $aheadCount = if ($aheadOut) { [int]$aheadOut } else { 0 }

    if ($aheadCount -eq 0) {
        Write-SyncLog "no managed changes, no commits ahead origin"
        exit 0
    }
    Write-SyncLog "no working tree changes, but $aheadCount commit(s) ahead -- proceeding to push"
}
# ... иначе stage + commit как раньше ...

# Push -- общий блок для обоих сценариев (fresh-commit-from-staging
# или ahead-only push)
```

Также: блок push вынесен в **shared path** -- общий для обоих
сценариев, не дублируется внутри ветки «есть managed changes».

`git fetch --quiet` безопасен в hook-context (в отличие от
`git pull --rebase --autostash` который зависал -- 5-я ловушка):
fetch только обновляет refs, не делает merge/rebase, не блокируется
на интерактивный prompt.

### Урок 11 для следующих раз

**Hook должен догонять не только working tree changes, но и
ahead-origin коммиты.** Иначе при любой неудачной push-попытке (сеть
/ прокси / истекший PAT / interrupt) локальные коммиты «зависают» и
никогда не доедут до origin.

Проверочные команды для диагностики (если коммиты «зависли»):
```powershell
cd $env:USERPROFILE\.claude
git fetch origin
git rev-list --left-right --count HEAD...origin/main
# Левое число > 0 -- локально ahead, нужно push
# Правое > 0 -- origin ahead, нужно pull
```

### Урок 12 — иногда дело не в hook'е, а в аутентификации

Параллельная находка дня: на рабочем ПК hook не мог запушить **даже
после фикса** -- получал `HTTP 403 Permission denied`. Причина не в
скрипте: **PAT в Git Credential Manager истёк / имел недостаточный
scope** для write-операций на private (или даже public) репо.

Симптом:
```
remote: Permission to daniileliseev1337/claude-base.git denied to daniileliseev1337.
fatal: unable to access ... The requested URL returned error: 403
```

При этом `git pull` работает (анонимный fetch на public репо), `git
push` -- падает на auth.

**Лечение:**
```powershell
cmdkey /delete:LegacyGeneric:target=git:https://github.com
cd $env:USERPROFILE\.claude
git push origin main
# открывается окно Git Credential Manager
# -> Sign in to GitHub через браузер
# -> Credential Manager создаёт свежий PAT с правильным scope
# -> push проходит
```

Это разовое действие на ПК, дальше токен сохранён и hook работает
молча.

**Превентивная мера для следующих сотрудников при установке
системы**: добавить в `Install.ps1` шаг «Stage 8: первичная
аутентификация GitHub» с явным push'ем в `~/.claude/` -- чтобы PAT
сохранился сразу при установке, а не лопнул при первом hook-вызове
через месяц. (Отдельная задача для claude-lite-instaler.)

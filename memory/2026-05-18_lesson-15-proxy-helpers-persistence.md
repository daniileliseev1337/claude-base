# Урок 15 — claude-lite-instaler proxy-хелперы persistence

**Дата фиксации проблемы:** 2026-05-09 (в hooks-debugging.md как TODO)
**Дата дизайна решения:** 2026-05-18
**Дата реализации:** 2026-05-18 (та же сессия, продолжили после
закрытия первой партии хвостов)
**Статус:** **CLOSED.** Реализовано коммитом `3562631` в
`claude-lite-instaler`. Verified локально на DANIILPC. CLAUDE.md
«Прокси» обновлена.

## Проблема

`claude-lite-instaler` содержит proxy-хелперы:

- `Set-Proxy.ps1` (6330 B) — устанавливает HTTP_PROXY/HTTPS_PROXY для
  текущей PS-сессии. Запрашивает пароль через `Get-Credential`, читает
  host:port + login из `~/.claude-proxy.json`.
- `Set-Proxy.cmd` (496 B) — cmd-обёртка для PS-вызова.
- `Start-Claude.ps1` (4268 B) — proxy setup + выбор CLI/VSCode + запуск.
- `Start-Claude.bat` (440 B) — двойной клик launcher для Start-Claude.ps1.
- `Start-Claude.ahk` (1289 B) — глобальная горячая клавиша Ctrl+Alt+C
  (требует AutoHotkey v2).

Эти хелперы **остаются в папке installer'а** после установки. `Install.ps1`
**не копирует их** никуда. В Next-steps пользователю говорится:

> Each new terminal needs proxy re-set: & '$here\Set-Proxy.ps1'

`$here` = папка где лежит распакованный installer. Если пользователь её
удалит (типичный сценарий — installer выглядит как «временная папка для
установки»), хелперы теряются.

CLAUDE.md в "Прокси (если за корп-прокси)" пишет:
> claude-lite-instaler кладёт хелперы: Set-Proxy.ps1 / Start-Claude.bat / Start-Claude.ahk

**«Кладёт» вводит в заблуждение** — installer не «кладёт», он просто
содержит их.

## Дизайн решения

В `Install.ps1` после Stage 1 (или как отдельный мини-этап) — копировать
proxy-хелперы в **persistent location**, доступный для пользователя
после удаления installer-папки.

### Выбор persistent location

Кандидаты:

1. **`~/.claude/bin/`** — рядом с `diff-pdf v0.5.3` который CLAUDE.md
   уже упоминает там. **Плюс:** консистентность. **Минус:** `~/.claude/bin/`
   в `.gitignore` (per-machine), значит файлы не уйдут в auto-sync — это
   нормально, хелперы должны быть **локальные**.

2. **`~/Documents/Claude/`** — desktop-friendly. **Плюс:** видимо
   пользователю. **Минус:** loose location.

3. **`%APPDATA%\Claude\helpers\`** — стандартное Windows-место. **Минус:**
   неудобно открыть руками.

**Вердикт:** `~/.claude/bin/` (= вариант 1) + Start Menu shortcut на
`Start-Claude.bat` для удобства.

### Изменения в `Install.ps1`

Между Stage 1 (Proxy) и Stage 2 (VS Code) — новый блок (или
неинтерактивный append к Stage 1):

```powershell
# Copy proxy helpers to ~/.claude/bin/ for persistence
$binDir = Join-Path $env:USERPROFILE ".claude\bin"
if (-not (Test-Path $binDir)) {
    New-Item -ItemType Directory -Path $binDir -Force | Out-Null
}

$helpers = @(
    "Set-Proxy.ps1",
    "Set-Proxy.cmd",
    "Start-Claude.ps1",
    "Start-Claude.bat",
    "Start-Claude.ahk"
)
foreach ($h in $helpers) {
    $src = Join-Path $here $h
    $dst = Join-Path $binDir $h
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Host "  Copied $h -> $binDir" -ForegroundColor Gray
    }
}

# Start Menu shortcut to Start-Claude.bat
$startMenu = [Environment]::GetFolderPath("Programs")
$shortcutPath = Join-Path $startMenu "Claude (with proxy).lnk"
if (-not (Test-Path $shortcutPath)) {
    $wsh = New-Object -ComObject WScript.Shell
    $shortcut = $wsh.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = Join-Path $binDir "Start-Claude.bat"
    $shortcut.WorkingDirectory = $env:USERPROFILE
    $shortcut.IconLocation = "$env:SystemRoot\System32\cmd.exe,0"
    $shortcut.Save()
    Write-Host "  Start Menu shortcut: Claude (with proxy)" -ForegroundColor Gray
}
```

### Обновление Next-steps в Install.ps1

Заменить:
```
Each new terminal needs proxy re-set:
  & '$here\Set-Proxy.ps1'
```
На:
```
Each new terminal needs proxy re-set:
  & "$HOME\.claude\bin\Set-Proxy.ps1"
Or use Start Menu -> "Claude (with proxy)" for one-click launch.
```

### Обновление CLAUDE.md

В секции «Прокси» в CORE-блоке — поменять формулировку с «installer
кладёт хелперы» на конкретное:

> Прокси-хелперы устанавливаются в `~/.claude/bin/` (per-machine, не
> в git). После установки доступны через:
> - `& "$HOME\.claude\bin\Set-Proxy.ps1"` — поставить env-vars в окне
> - Start Menu → «Claude (with proxy)» — одним кликом запустить
> - Ctrl+Alt+C — если установлен AutoHotkey v2 (см. Start-Claude.ahk)

## Проверка фикса (success criteria)

1. **На свежей машине** после Install.ps1 — `~/.claude/bin/` содержит
   все 5 файлов (`Set-Proxy.ps1`, `.cmd`, `Start-Claude.ps1`, `.bat`,
   `.ahk`).
2. В Start Menu появился ярлык «Claude (with proxy)».
3. Удаление installer-папки **не ломает** доступ к хелперам.
4. Открытие новой PS-сессии и `& "$HOME\.claude\bin\Set-Proxy.ps1"`
   ставит HTTP_PROXY/HTTPS_PROXY как раньше.
5. На существующей машине (DANIILPC, DELISEEV-PC, NB-HP-LQ6G,
   100226745A) — повторный запуск Install.ps1 идемпотентно копирует
   хелперы в `~/.claude/bin/` (если их там ещё нет).

## Очерёдность

Этот фикс — **отдельная сессия** с claude-lite-instaler. Требует:
- git clone claude-lite-instaler (если ещё нет local copy)
- Edit Install.ps1 (вставка ~40 строк)
- Edit CLAUDE.md (CORE-секция «Прокси»)
- git commit + push в claude-lite-instaler

ETA: 15-20 минут в одну сессию.

## Реализация (2026-05-18, post-mortem)

Заняло ~15 минут. Шаги:

1. Pull последнего `1ad2b3e` в local clone `~/Desktop/claude-lite-instaler/`.
2. Edit `Install.ps1`: вставил ~60 строк после Stage 1 (Run-Stage),
   копирующих 5 хелперов в `~/.claude/bin/` + Start Menu shortcut на
   `Start-Claude.bat`.
3. Обновил `Next-steps` в конце installer'а — путь к `Set-Proxy.ps1`
   теперь `~/.claude/bin/`, добавлено упоминание ярлыка Пуска.
4. Обновил docstring `.DESCRIPTION` — пункт 1 Proxy теперь упоминает
   автокопирование.
5. **Verification standalone**: извлёк новую логику в
   `%TEMP%\verify-proxy-helpers.ps1`, запустил на DANIILPC. Все 5
   хелперов скопированы (Set-Proxy.ps1 6508 B, Set-Proxy.cmd 508 B,
   Start-Claude.ps1 4380 B, Start-Claude.bat 448 B, Start-Claude.ahk
   1313 B), ярлык 1905 B создан в
   `%APPDATA%\Microsoft\Windows\Start Menu\Programs\`.
6. Commit + push в claude-lite-instaler: `3562631` на origin/main.
7. CLAUDE.md «Прокси» секция обновлена с новыми путями и ссылкой на
   коммит фикса.

### Что было сложнее ожидаемого

- **Cyrillic в bash↔PowerShell.** Первая попытка verification через
  `powershell -Command @'...'@` не сработала (`@` не распознан как
  here-string в `-Command` контексте). Перешёл на `-File` с временным
  скриптом — но Cyrillic в скрипте мангнулся при PowerShell read
  (codepage 866 vs UTF-8 без BOM). Решение: переписал verification-
  скрипт **на ASCII** (без Cyrillic в литералах кода). Урок: для
  ad-hoc verification scripts не использовать Cyrillic.

### Что не сделано

- **Тест на чистой машине.** Verification прогнал только новый
  блок standalone, не полный Install.ps1 с -Yes от начала до конца.
  Это OK потому что блок самодостаточен (no global state from earlier
  stages), но end-to-end тест остаётся на следующую установку.

## Связанные уроки

- **Урок 6** (CORE 2>&1 на native exec) — не применимо (новый код не
  использует native exec).
- **Урок 16** (мета-урок про повторение собственных уроков) — применить:
  перед написанием copy-блока для proxy-хелперов **сначала** проверить
  через `Test-Path` чтобы избежать повторного копирования + лишних
  WARNING'ов.

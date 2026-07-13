# restore-ccd-sessions.ps1 — вернуть список сессий в Recents десктоп-приложения
# после смены аккаунта Claude.
#
# Проблема: десктоп-приложение хранит реестр «Recents» в
#   %APPDATA%\Claude\claude-code-sessions\<UUID аккаунта>\<UUID организации>\local_*.json
# — по папке на аккаунт. После логина в другой аккаунт список пуст, хотя сами
# транскрипты (~/.claude/projects) целы.
#
# Что делает: определяет текущий аккаунт из ~/.claude.json, копирует в его папку
# файлы сессий из папок всех остальных аккаунтов (без перезаписи существующих;
# при дублях между источниками берётся самый свежий). Исходные папки не трогает.
# Перед копированием делает бэкап целевой папки. Идемпотентен.
#
# Запуск: powershell -File "$HOME\.claude\scripts\restore-ccd-sessions.ps1"
# После запуска перезапустить приложение Claude.

$ErrorActionPreference = 'Stop'

# 1. Текущий аккаунт
$cfgPath = Join-Path $HOME '.claude.json'
if (-not (Test-Path $cfgPath)) { Write-Host "ОШИБКА: не найден $cfgPath"; exit 1 }
$cfg = Get-Content $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json
$accountUuid = $cfg.oauthAccount.accountUuid
$accountEmail = $cfg.oauthAccount.emailAddress
if (-not $accountUuid) { Write-Host 'ОШИБКА: в ~/.claude.json нет oauthAccount.accountUuid (не залогинен?)'; exit 1 }
Write-Host "Текущий аккаунт: $accountEmail ($accountUuid)"

# 2. Реестр сессий приложения
$root = Join-Path $env:APPDATA 'Claude\claude-code-sessions'
if (-not (Test-Path $root)) { Write-Host "ОШИБКА: не найден реестр $root (приложение не ставилось?)"; exit 1 }

$accountDir = Join-Path $root $accountUuid
if (-not (Test-Path $accountDir)) {
    Write-Host 'Папка текущего аккаунта в реестре ещё не создана.'
    Write-Host 'Запусти в приложении одну новую сессию (появится папка) и повтори скрипт.'
    exit 1
}

# Целевая папка организации: самая свежая внутри папки аккаунта
$target = Get-ChildItem $accountDir -Directory | Where-Object { $_.Name -notlike '*.bak*' } |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $target) { Write-Host 'ОШИБКА: внутри папки аккаунта нет папки организации. Запусти одну сессию в приложении.'; exit 1 }
Write-Host "Целевая папка: $($target.FullName)"

# 3. Источники: папки всех остальных аккаунтов
$sources = Get-ChildItem $root -Directory | Where-Object { $_.Name -ne $accountUuid } |
    ForEach-Object { Get-ChildItem $_.FullName -Directory } | Where-Object { $_.Name -notlike '*.bak*' }
if (-not $sources) { Write-Host 'Других аккаунтов в реестре нет — восстанавливать нечего.'; exit 0 }

# 4. Слияние: не перезаписывать существующие; при дублях источников — самый свежий
$existing = @{}
Get-ChildItem $target.FullName -Filter 'local_*.json' | ForEach-Object { $existing[$_.Name] = $true }

$candidates = @{}
foreach ($src in $sources) {
    foreach ($f in Get-ChildItem $src.FullName -Filter 'local_*.json') {
        if ($existing.ContainsKey($f.Name)) { continue }
        if (-not $candidates.ContainsKey($f.Name) -or $f.LastWriteTime -gt $candidates[$f.Name].LastWriteTime) {
            $candidates[$f.Name] = $f
        }
    }
}

if ($candidates.Count -eq 0) {
    Write-Host 'Новых сессий для переноса нет — реестр уже актуален.'
    exit 0
}

# 5. Бэкап целевой папки (только когда есть что копировать)
$stamp = Get-Date -Format 'yyyy-MM-dd_HHmmss'
$bak = "$($target.FullName).bak-$stamp"
Copy-Item $target.FullName $bak -Recurse
Write-Host "Бэкап: $bak"

$copied = 0
foreach ($f in $candidates.Values) {
    Copy-Item $f.FullName (Join-Path $target.FullName $f.Name)
    $copied++
}

$total = (Get-ChildItem $target.FullName -Filter 'local_*.json').Count
Write-Host "Скопировано новых сессий: $copied. Всего в реестре аккаунта: $total."
Write-Host 'Перезапусти приложение Claude — список Recents обновится.'

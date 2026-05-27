<#
.SYNOPSIS
Per-PC setup helper для knowledge library. Спрашивает у пользователя
полный путь к папке Claude_Library на этом ПК и записывает в
~/.claude/.library-config.json.

.DESCRIPTION
На DANIILPC (owner с .developer-marker): создаёт 8 категорийных подпапок
если их нет — потому что Daniel пишет в библиотеку.

На consumer ПК: read-only режим, подпапки должны быть подтянуты Я.Диск
sync'ом после принятия invite от Daniil. Скрипт только регистрирует путь.

Запускается ОДИН РАЗ при первой установке + повторно при:
- Переустановке Windows / смене Windows user.
- Смене пути Я.Диска (например переехал на другой диск).
- Daniil ротировал shared доступ (новый invite).

Не интерактивный для hook'ов — только manual запуск (использует Read-Host).
#>

$ErrorActionPreference = 'Stop'

$ClaudeDir = Join-Path $env:USERPROFILE '.claude'
$ConfigFile = Join-Path $ClaudeDir '.library-config.json'
$DeveloperMarker = Join-Path $ClaudeDir '.developer-marker'

Write-Host ""
Write-Host "=== Set-LibraryRoot: настройка knowledge library ===" -ForegroundColor Cyan
Write-Host ""

# 1. Определить роль
$isDeveloper = Test-Path $DeveloperMarker
if ($isDeveloper) {
    Write-Host "Роль: developer (DANIILPC). Подпапки будут созданы если их нет." -ForegroundColor Green
} else {
    Write-Host "Роль: consumer. Read-only: подпапки должны быть подтянуты Я.Диск sync'ом." -ForegroundColor Yellow
}

# 2. Спросить путь
$defaultPath = Join-Path $env:USERPROFILE "YandexDisk\Claude_Library"
Write-Host ""
Write-Host "Введи полный путь до папки Claude_Library на этом ПК." -ForegroundColor Cyan
Write-Host "  - На DANIILPC: '$defaultPath' или другой если Я.Диск в другом месте." -ForegroundColor Gray
Write-Host "  - На consumer ПК: путь к shared папке, как её показывает Я.Диск" -ForegroundColor Gray
Write-Host "    (может быть с префиксом 'От Даниила' или похожим)." -ForegroundColor Gray
$inputPath = Read-Host "Путь (Enter для default: $defaultPath)"
if (-not $inputPath) { $inputPath = $defaultPath }

# 3. Проверить существование
if (-not (Test-Path $inputPath)) {
    if ($isDeveloper) {
        Write-Host ""
        Write-Host "Папка не существует. Создаю (developer mode)." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $inputPath -Force | Out-Null
    } else {
        Write-Host ""
        Write-Host "ERROR: папка '$inputPath' не существует." -ForegroundColor Red
        Write-Host "Шаги для consumer ПК:" -ForegroundColor Yellow
        Write-Host "  1. Открой Я.Диск в браузере -> раздел 'Доступы'." -ForegroundColor Yellow
        Write-Host "  2. Прими invite от Daniil на папку Claude_Library." -ForegroundColor Yellow
        Write-Host "  3. Дождись окончания первичного sync (10-30 минут)." -ForegroundColor Yellow
        Write-Host "  4. Запусти этот скрипт заново." -ForegroundColor Yellow
        exit 1
    }
}

# 4. На developer — создать 8 подпапок
if ($isDeveloper) {
    $subdirs = @('spds', 'ov', 'vk', 'eo', 'ss', 'ppr', 'prikazy', 'shablony')
    foreach ($sub in $subdirs) {
        $subPath = Join-Path $inputPath $sub
        if (-not (Test-Path $subPath)) {
            New-Item -ItemType Directory -Path $subPath -Force | Out-Null
            Write-Host "  + создана подпапка: $sub" -ForegroundColor Green
        }
    }
}

# 5. Smoke check: посчитать PDF и подпапки
$pdfCount = 0
$subFound = 0
foreach ($sub in @('spds', 'ov', 'vk', 'eo', 'ss', 'ppr', 'prikazy', 'shablony')) {
    $subPath = Join-Path $inputPath $sub
    if (Test-Path $subPath) {
        $subFound++
        $pdfCount += @(Get-ChildItem $subPath -Filter '*.pdf' -ErrorAction SilentlyContinue).Count
    }
}

if ($subFound -eq 0 -and -not $isDeveloper) {
    Write-Host ""
    Write-Host "WARN: ни одной из 8 ожидаемых подпапок не найдено." -ForegroundColor Yellow
    Write-Host "Я.Диск ещё не закончил sync? Подожди и проверь снова через ls '$inputPath'." -ForegroundColor Yellow
}

# 6. Записать конфиг
$cfg = [PSCustomObject]@{
    library_path = $inputPath
}
$json = $cfg | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText($ConfigFile, $json, [System.Text.UTF8Encoding]::new($false))

Write-Host ""
Write-Host "OK. Конфиг записан: $ConfigFile" -ForegroundColor Green
Write-Host "  library_path: $inputPath" -ForegroundColor Green
Write-Host "  Найдено подпапок: $subFound / 8" -ForegroundColor Green
Write-Host "  Найдено PDF: $pdfCount" -ForegroundColor Green
Write-Host ""
Write-Host "Готово. После restart Claude Code агент 'norm-lookup' будет использовать эту библиотеку." -ForegroundColor Cyan

<#
.SYNOPSIS
Per-PC setup helper для knowledge library. Спрашивает у пользователя
полный путь к папке Claude_Library на этом ПК и записывает в
~/.claude/.library-config.json.

.DESCRIPTION
Определяет роль через write-permission test (не через .developer-marker —
тот про git claude-base, а не про Я.Диск ownership):

- Owner Я.Диска (Daniil на DANIILPC и R-090226727A) — может писать в
  Claude_Library, скрипт создаёт 8 категорийных подпапок если их нет.
- Consumer ПК сотрудников (shared папка read-only) — скрипт только
  регистрирует путь, подпапки должны быть подтянуты Я.Диск sync'ом.

Запускается ОДИН РАЗ при первой установке + повторно при:
- Переустановке Windows / смене Windows user.
- Смене пути Я.Диска (например переехал на другой диск).
- Daniil ротировал shared доступ (новый invite).

Не интерактивный для hook'ов — только manual запуск (использует Read-Host).

ВАЖНО про прокси: Я.Диск-клиент в фоне может ходить через корп-прокси
(зависит от настроек Я.Диск-клиента в системе). Сам Set-LibraryRoot
работает ТОЛЬКО с локальной файловой системой — никаких сетевых вызовов.
Будущие обращения к Я.Диск API из norm-lookup должны идти bypass прокси
(см. anti-patterns.md A4.4).
#>

$ErrorActionPreference = 'Stop'

$ClaudeDir = Join-Path $env:USERPROFILE '.claude'
$ConfigFile = Join-Path $ClaudeDir '.library-config.json'

Write-Host ""
Write-Host "=== Set-LibraryRoot: настройка knowledge library ===" -ForegroundColor Cyan
Write-Host ""

# 1. Спросить путь
$defaultPath = Join-Path $env:USERPROFILE "YandexDisk\Claude_Library"
Write-Host "Введи полный путь до папки Claude_Library на этом ПК." -ForegroundColor Cyan
Write-Host "  - Owner (Daniil): '$defaultPath' или где у тебя Я.Диск" -ForegroundColor Gray
Write-Host "  - Сотрудник: путь к shared папке как показывает Я.Диск" -ForegroundColor Gray
Write-Host "    (может быть с префиксом 'От Даниила' или похожим)." -ForegroundColor Gray
$inputPath = Read-Host "Путь (Enter для default: $defaultPath)"
if (-not $inputPath) { $inputPath = $defaultPath }

# 2. Проверить существование
$pathExisted = Test-Path $inputPath
if (-not $pathExisted) {
    Write-Host ""
    Write-Host "Папка '$inputPath' не существует." -ForegroundColor Yellow
    $createIt = Read-Host "Создать её сейчас? (y/N)"
    if ($createIt -eq 'y' -or $createIt -eq 'Y') {
        New-Item -ItemType Directory -Path $inputPath -Force | Out-Null
        Write-Host "  + создана: $inputPath" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Шаги для сотрудника:" -ForegroundColor Yellow
        Write-Host "  1. Открой Я.Диск в браузере -> раздел 'Доступы'." -ForegroundColor Yellow
        Write-Host "  2. Прими invite от Daniil на папку Claude_Library." -ForegroundColor Yellow
        Write-Host "  3. Дождись окончания первичного sync (10-30 минут)." -ForegroundColor Yellow
        Write-Host "  4. Запусти этот скрипт заново." -ForegroundColor Yellow
        exit 1
    }
}

# 3. Определить ownership через write-permission test
$testFile = Join-Path $inputPath ".write-test-$(Get-Random)"
$canWrite = $false
try {
    Set-Content -Path $testFile -Value "test" -ErrorAction Stop
    Remove-Item $testFile -Force -ErrorAction SilentlyContinue
    $canWrite = $true
} catch {
    $canWrite = $false
}

if ($canWrite) {
    Write-Host ""
    Write-Host "Режим: owner (write-access). Подпапки будут созданы если их нет." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Режим: read-only (shared папка). Подпапки приходят через Я.Диск sync." -ForegroundColor Yellow
}

# 4. Если owner — создать 8 подпапок
if ($canWrite) {
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

if ($subFound -eq 0 -and -not $canWrite) {
    Write-Host ""
    Write-Host "WARN: ни одной из 8 ожидаемых подпапок не найдено." -ForegroundColor Yellow
    Write-Host "Я.Диск ещё не закончил sync? Проверь снова через несколько минут." -ForegroundColor Yellow
}

# 6. Записать конфиг
$jsonPath = $inputPath -replace '\\', '\\'
$json = "{`r`n    `"library_path`": `"$jsonPath`"`r`n}"
$utf8NoBOM = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($ConfigFile, $json, $utf8NoBOM)

Write-Host ""
Write-Host "OK. Конфиг записан: $ConfigFile" -ForegroundColor Green
Write-Host "  library_path: $inputPath" -ForegroundColor Green
Write-Host "  Найдено подпапок: $subFound / 8" -ForegroundColor Green
Write-Host "  Найдено PDF: $pdfCount" -ForegroundColor Green
Write-Host ""
Write-Host "Готово. После restart Claude Code агент 'norm-lookup' будет использовать эту библиотеку." -ForegroundColor Cyan
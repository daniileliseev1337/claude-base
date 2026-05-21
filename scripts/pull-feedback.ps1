<#
.SYNOPSIS
Скрипт для Daniil'а — забрать новый feedback со всех веток
claude-base-feedback репо в локальный обзор.

.DESCRIPTION
Запускается на DANIILPC периодически (раз в день/неделю).
Workflow:

1. Клонирует/обновляет ~/.claude/feedback-inbox/ от claude-base-feedback.
2. Fetch всех branches feedback/*.
3. Для каждой ветки — checkout и копирование новых файлов в
   `~/.claude/feedback-inbox/all/<branch>/<filename>.md`.
4. Список новых файлов выводит в консоль для review.

Конфиг — `~/.claude/.feedback-config.json` (тот же что у consumers, но
с правом read+admin на feedback-репо):
{
  "github_repo": "daniileliseev1337/claude-base-feedback",
  "token": "ghp_..."
}

Использование:
  powershell -File ~/.claude/scripts/pull-feedback.ps1

После review Daniil решает что внедрять в shared базу и руками
коммитит в claude-base main.
#>

$ErrorActionPreference = 'Stop'

$ClaudeDir = Join-Path $env:USERPROFILE '.claude'
$InboxDir = Join-Path $ClaudeDir 'feedback-inbox'
$ConfigFile = Join-Path $ClaudeDir '.feedback-config.json'

if (-not (Test-Path $ConfigFile)) {
    Write-Host "FAIL: $ConfigFile not found." -ForegroundColor Red
    Write-Host "Создай файл с {github_repo, token}." -ForegroundColor Yellow
    exit 1
}

$cfg = Get-Content $ConfigFile -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $cfg.github_repo -or -not $cfg.token) {
    Write-Host "FAIL: .feedback-config.json missing github_repo or token" -ForegroundColor Red
    exit 1
}

$repo = $cfg.github_repo
$token = $cfg.token

# Clone repo if missing, else fetch
$repoUrl = "https://${token}@github.com/${repo}.git"
$repoLocal = Join-Path $InboxDir '.repo'

if (-not (Test-Path $repoLocal)) {
    Write-Host "Clone $repo to $repoLocal..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $InboxDir -Force | Out-Null
    & git clone $repoUrl $repoLocal 2>&1 | Out-Null
} else {
    Write-Host "Fetch updates for $repo..." -ForegroundColor Cyan
    Push-Location $repoLocal
    & git fetch --all --prune 2>&1 | Out-Null
    Pop-Location
}

# Перечень feedback/* веток
Push-Location $repoLocal
$branches = & git branch -r 2>&1 | Where-Object { $_ -match 'origin/feedback/' } | ForEach-Object { ($_ -replace 'origin/', '').Trim() }
Pop-Location

if (-not $branches) {
    Write-Host "Нет feedback/* веток в репо." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "=== Найдено $($branches.Count) ветка(ок) feedback ===" -ForegroundColor Green
foreach ($branch in $branches) {
    Write-Host ""
    Write-Host "--- $branch ---" -ForegroundColor Cyan
    $branchOutDir = Join-Path $InboxDir 'all' ($branch -replace '/', '_')
    New-Item -ItemType Directory -Path $branchOutDir -Force | Out-Null

    Push-Location $repoLocal
    & git checkout -q $branch 2>&1 | Out-Null

    # Скопировать всё из feedback/ в branchOutDir
    $feedbackPath = Join-Path $repoLocal 'feedback'
    if (Test-Path $feedbackPath) {
        $files = Get-ChildItem $feedbackPath -File -Filter '*.md'
        foreach ($f in $files) {
            $dest = Join-Path $branchOutDir $f.Name
            $isNew = -not (Test-Path $dest)
            Copy-Item $f.FullName $dest -Force
            $mark = if ($isNew) { '[NEW]' } else { '[upd]' }
            Write-Host "  $mark $($f.Name)" -ForegroundColor $(if ($isNew) { 'Green' } else { 'Gray' })
        }
    } else {
        Write-Host "  (нет feedback/ папки в ветке)" -ForegroundColor DarkGray
    }
    Pop-Location
}

Push-Location $repoLocal
& git checkout -q main 2>&1 | Out-Null
Pop-Location

Write-Host ""
Write-Host "=== Готово. Все feedback файлы в $InboxDir\all\ ===" -ForegroundColor Green
Write-Host "Ревью: открыть нужный файл, решить что внедрять в shared базу." -ForegroundColor Yellow

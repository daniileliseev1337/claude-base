<#
.SYNOPSIS
Собирает локальный feedback от consumer-ПК для Daniil'а (Phase 2 sync-redesign).

.DESCRIPTION
Запускается из auto-push.ps1 на ПК без .developer-marker (consumer mode).
Назначение — собрать структурированный feedback в формате который Daniil
потом ревью'ет и решает что внедрить в shared базу.

Workflow:

1. Сканирует ~/.claude/feedback-pending/*.md — файлы которые Claude
   написал в текущей сессии (если были error/suggestion/harvest finding).
2. Для каждого: добавляет metadata frontmatter (если нет) — hostname,
   user.email из git config, дата.
3. Перемещает в ~/.claude/feedback-staging/<yyyy-mm-dd>-<hostname>-<basename>.md.
4. Если ~/.claude/.feedback-config.json существует с github_repo — push'ит
   в branch feedback/<hostname-userprefix>. Если нет — оставляет
   локально в staging (Daniil заберёт вручную).

Claude в текущей сессии **сам** пишет feedback-pending/*.md когда
обнаруживает что что-то полезное надо передать Daniil'у (см. правило
"Feedback collection" в CLAUDE.md).

Идемпотентен: повторный запуск без новых pending = no-op.
#>

$ErrorActionPreference = 'Continue'

$ClaudeDir = Join-Path $env:USERPROFILE '.claude'
$PendingDir = Join-Path $ClaudeDir 'feedback-pending'
$StagingDir = Join-Path $ClaudeDir 'feedback-staging'
$ConfigFile = Join-Path $ClaudeDir '.feedback-config.json'
$LogFile = Join-Path $ClaudeDir 'auto-sync.log'

function Write-FbLog { param($msg)
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] feedback-collector: $msg" |
        Add-Content -Path $LogFile -Encoding UTF8 -ErrorAction SilentlyContinue
}

# Identification — кто и откуда (для metadata frontmatter)
$hostname = $env:COMPUTERNAME
$userEmail = & git -C $ClaudeDir config user.email 2>$null
if (-not $userEmail) { $userEmail = 'unknown' }
$userPrefix = ($userEmail -split '@')[0]

# Ensure dirs exist
if (-not (Test-Path $StagingDir)) {
    New-Item -ItemType Directory -Path $StagingDir -Force | Out-Null
}
if (-not (Test-Path $PendingDir)) {
    # Нет pending dir — feedback не собирался в эту сессию
    Write-FbLog "no feedback-pending/ — nothing to collect"
    exit 0
}

$pendingFiles = @(Get-ChildItem $PendingDir -File -Filter '*.md' -ErrorAction SilentlyContinue)
if ($pendingFiles.Count -eq 0) {
    Write-FbLog "feedback-pending/ empty — nothing to collect"
    exit 0
}

Write-FbLog "found $($pendingFiles.Count) pending feedback file(s)"

$now = Get-Date -Format 'yyyy-MM-dd_HHmm'

foreach ($f in $pendingFiles) {
    $content = Get-Content $f.FullName -Raw -Encoding UTF8

    # Добавляем frontmatter если его нет
    if ($content -notmatch '(?s)^---\s*\r?\n') {
        $frontmatter = @"
---
collected: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz')
hostname: $hostname
user: $userEmail
basename: $($f.BaseName)
---

"@
        $content = $frontmatter + $content
    }

    # Move to staging с уникальным именем
    $newName = "${now}-${hostname}-${userPrefix}-$($f.BaseName).md"
    $destPath = Join-Path $StagingDir $newName

    [System.IO.File]::WriteAllText($destPath, $content, [System.Text.UTF8Encoding]::new($false))
    Remove-Item $f.FullName -Force

    Write-FbLog "staged: $newName"
}

# Если есть config с GitHub репо — push через API (Phase 2 follow-up)
if (Test-Path $ConfigFile) {
    try {
        $cfg = Get-Content $ConfigFile -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($cfg.github_repo -and $cfg.token) {
            Write-FbLog "remote push to $($cfg.github_repo) — not implemented yet (Phase 2 follow-up). Files остаются в staging."
            # TODO Phase 2-follow-up: push each staging file через GitHub API:
            # POST /repos/$cfg.github_repo/contents/feedback/<branch>/<filename>
            # Authorization: token $cfg.token
            # branch: feedback/${hostname}-${userPrefix}
        }
    } catch {
        Write-FbLog "WARN: .feedback-config.json invalid JSON: $_"
    }
} else {
    Write-FbLog "no .feedback-config.json — feedback staged locally в $StagingDir. Daniil заберёт вручную."
}

exit 0

<#
.SYNOPSIS
SessionStart hook: pull latest claude-base into ~/.claude/.

.DESCRIPTION
Triggered by Claude Code on session start (settings.json hooks).
Runs git pull --rebase --autostash silently. Logs to ~/.claude/auto-sync.log.
Always exits 0 to avoid blocking session start.

If there is a rebase conflict (rare; happens when CORE block of CLAUDE.md
was edited locally AND in claude-base) -- aborts the rebase, leaves the
working tree as-is, logs the failure. User resolves manually.
#>

$ErrorActionPreference = 'SilentlyContinue'

$claudeDir = Join-Path $env:USERPROFILE '.claude'
$logFile   = Join-Path $claudeDir 'auto-sync.log'

function Write-SyncLog { param($msg)
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] auto-pull: $msg" | Add-Content -Path $logFile
}

# Skip if ~/.claude/ is not a git repo
if (-not (Test-Path (Join-Path $claudeDir '.git'))) {
    exit 0
}

Push-Location $claudeDir
try {
    Write-SyncLog "start"

    $output = & git pull --rebase --autostash 2>&1
    $exit = $LASTEXITCODE

    $output | Out-String | Add-Content -Path $logFile

    if ($exit -ne 0) {
        Write-SyncLog "FAILED (exit=$exit), aborting rebase"
        & git rebase --abort 2>&1 | Out-Null
    } else {
        Write-SyncLog "ok"
    }
} catch {
    Write-SyncLog "exception: $_"
} finally {
    Pop-Location
}

# Always exit 0 -- never block session start
exit 0

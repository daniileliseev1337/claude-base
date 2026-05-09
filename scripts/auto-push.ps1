<#
.SYNOPSIS
SessionEnd hook: commit and push managed paths in ~/.claude/ to claude-base.

.DESCRIPTION
Triggered by Claude Code on session end (settings.json hooks).
Checks git status of WHITELIST paths. If there are changes -- commits and
pushes to origin/main. Logs to ~/.claude/auto-sync.log.

Whitelist (managed paths -- only these are auto-committed):
    agents/, skills/, commands/, memory/, session-reports/, harvested/,
    CLAUDE.md, README.md

Anything outside the whitelist is NEVER auto-committed -- protects against
accidental push of credentials, history, plugins, projects, _sandbox, etc.
Those are also gitignored, but defense in depth.

Always exits 0 to avoid blocking session end.

Conflict handling: pulls before pushing. If pull conflicts, aborts and skips
push. User resolves on next manual interaction.
#>

$ErrorActionPreference = 'SilentlyContinue'

$claudeDir = Join-Path $env:USERPROFILE '.claude'
$logFile   = Join-Path $claudeDir 'auto-sync.log'

# Whitelist of managed paths. Files OUTSIDE these are NEVER auto-committed.
# IMPORTANT: 'sessions' is intentionally NOT in this list -- Claude Code
# itself uses ~/.claude/sessions/ for transient JSON session state. Our
# per-session reports go to session-reports/ (different name to avoid
# collision).
$Managed = @(
    'agents',
    'skills',
    'commands',
    'memory',
    'session-reports',
    'harvested',
    'CLAUDE.md',
    'README.md'
)

function Write-SyncLog { param($msg)
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] auto-push: $msg" | Add-Content -Path $logFile
}

# Skip if ~/.claude/ is not a git repo
if (-not (Test-Path (Join-Path $claudeDir '.git'))) {
    exit 0
}

Push-Location $claudeDir
try {
    Write-SyncLog "start"

    # Find managed paths with changes
    $changedPaths = @()
    foreach ($path in $Managed) {
        if (-not (Test-Path $path)) { continue }
        $status = & git status --porcelain -- $path 2>$null
        if ($status) { $changedPaths += $path }
    }

    if ($changedPaths.Count -eq 0) {
        Write-SyncLog "no managed changes"
        exit 0
    }

    Write-SyncLog "managed changes in: $($changedPaths -join ', ')"

    # Stage changes
    foreach ($path in $changedPaths) {
        & git add -- $path 2>&1 | Out-Null
    }

    # Commit (skip if nothing was actually staged after add)
    $hostname = $env:COMPUTERNAME
    $msg = "auto-sync: session $(Get-Date -Format 'yyyy-MM-dd HH:mm') from $hostname"
    $commitOut = & git commit -m $msg 2>&1
    $commitExit = $LASTEXITCODE

    $commitOut | Out-String | Add-Content -Path $logFile

    if ($commitExit -ne 0) {
        Write-SyncLog "commit returned exit=$commitExit (likely nothing to commit)"
        exit 0
    }

    Write-SyncLog "commit ok"

    # Push directly without pull-before-push.
    # Empirically, `git pull --rebase --autostash` hangs in Claude Code
    # SessionEnd hook context (process times out without finishing).
    # If push gets rejected (remote moved), we accept that the local
    # commit stays ahead -- the next SessionStart auto-pull will do a
    # rebase and the next SessionEnd will retry push. Eventually consistent.
    Write-SyncLog "pushing to origin/main..."
    $pushOut = & git push origin main 2>&1
    $pushExit = $LASTEXITCODE
    $pushOut | Out-String | Add-Content -Path $logFile

    if ($pushExit -eq 0) {
        Write-SyncLog "pushed to origin/main"
    } else {
        Write-SyncLog "push FAILED (exit=$pushExit) -- commit stays ahead, will retry next cycle"
    }
} catch {
    Write-SyncLog "exception: $_"
} finally {
    Pop-Location
}

# Always exit 0 -- never block session end
exit 0

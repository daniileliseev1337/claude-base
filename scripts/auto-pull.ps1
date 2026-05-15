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

    $output = & git -c http.proxy="" -c https.proxy="" pull --rebase --autostash 2>&1
    $exit = $LASTEXITCODE

    $output | Out-String | Add-Content -Path $logFile

    if ($exit -ne 0) {
        Write-SyncLog "FAILED (exit=$exit), aborting rebase"
        & git rebase --abort 2>&1 | Out-Null
    } else {
        Write-SyncLog "ok"
    }

    # --- Extras diff check (mcp-manifest.json vs .local-state/setup-extras.applied) ---
    # If manifest exists and either (a) marker missing or (b) marker hash != current
    # manifest hash -- log a notification line so user/Claude knows there is
    # pending extras setup. Doesn't try to auto-install (timeout + auto-classifier
    # + UX) -- only notifies. User runs setup-extras.ps1 manually when ready.
    $manifestFile = Join-Path $claudeDir 'mcp-manifest.json'
    $markerFile   = Join-Path $claudeDir '.local-state\setup-extras.applied'
    if (Test-Path $manifestFile) {
        $currentHash = (Get-FileHash $manifestFile -Algorithm SHA256).Hash
        $needsRun = $false
        $reason = ""
        if (-not (Test-Path $markerFile)) {
            $needsRun = $true
            $reason = "marker missing -- setup-extras never run on this machine"
        } else {
            try {
                $marker = Get-Content $markerFile -Raw | ConvertFrom-Json
                if ($marker.manifest_hash -ne $currentHash) {
                    $needsRun = $true
                    $reason = "manifest changed since last setup ($($marker.manifest_hash.Substring(0,8)) -> $($currentHash.Substring(0,8)))"
                }
            } catch {
                $needsRun = $true
                $reason = "marker unreadable"
            }
        }
        if ($needsRun) {
            Write-SyncLog "extras-diff PENDING: $reason. Run: pwsh `"`$HOME\.claude\scripts\setup-extras.ps1`""
        } else {
            Write-SyncLog "extras-diff: up-to-date (manifest hash matches marker)"
        }
    }
} catch {
    Write-SyncLog "exception: $_"
} finally {
    Pop-Location
}

# Always exit 0 -- never block session start
exit 0

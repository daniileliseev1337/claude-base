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
    'formatting-templates',
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

    # Defense-in-depth: disable interactive credential prompt and clear
    # proxy env-vars at the top of the hook -- applies to BOTH fetch
    # (in the ahead-origin check below) and push (later). See traps
    # 14 (hook hangs on prompt) and 15 (proxy env breaks git push)
    # in memory/2026-05-09_hooks-debugging.md.
    $env:GIT_TERMINAL_PROMPT = '0'
    Remove-Item Env:HTTP_PROXY  -ErrorAction SilentlyContinue
    Remove-Item Env:HTTPS_PROXY -ErrorAction SilentlyContinue
    Remove-Item Env:http_proxy  -ErrorAction SilentlyContinue
    Remove-Item Env:https_proxy -ErrorAction SilentlyContinue
    Remove-Item Env:ALL_PROXY   -ErrorAction SilentlyContinue
    Remove-Item Env:all_proxy   -ErrorAction SilentlyContinue

    # Find managed paths with changes in working tree
    $changedPaths = @()
    foreach ($path in $Managed) {
        if (-not (Test-Path $path)) { continue }
        $status = & git status --porcelain -- $path 2>$null
        if ($status) { $changedPaths += $path }
    }

    if ($changedPaths.Count -eq 0) {
        # No working tree changes -- but maybe local commits are ahead origin.
        # Scenario: user (or Claude in chat) did `git commit` manually but
        # `git push` failed (network, missing PAT, etc). Working tree is clean,
        # the previous hook logic exited without push, and these commits
        # would never reach origin on their own.
        #
        # Quick fetch to refresh origin/main ref (safe in hook context --
        # unlike `git pull --rebase` which hangs, fetch is read-only).
        & git -c http.proxy="" -c https.proxy="" fetch --quiet origin main 2>&1 | Out-Null
        $aheadOut = & git rev-list --count origin/main..HEAD 2>$null
        $aheadCount = if ($aheadOut) { [int]$aheadOut } else { 0 }

        if ($aheadCount -eq 0) {
            Write-SyncLog "no managed changes, no commits ahead origin"
            exit 0
        }
        Write-SyncLog "no working tree changes, but $aheadCount commit(s) ahead -- proceeding to push"
    } else {
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
    }

    # Push (shared path: covers both fresh-commit-from-staging and ahead-origin cases)
    # Empirically, `git pull --rebase --autostash` hangs in Claude Code
    # SessionEnd hook context, so we never pre-pull. If push gets rejected
    # (remote moved), local commit stays ahead -- next SessionStart auto-pull
    # rebases, next SessionEnd retries push. Eventually consistent.

    # GIT_TERMINAL_PROMPT=0 and proxy env-cleanup applied at hook start
    # (traps 14, 15) -- still in effect for this push.

    Write-SyncLog "pushing to origin/main..."
    $pushOut = & git -c http.proxy="" -c https.proxy="" push origin main 2>&1
    $pushExit = $LASTEXITCODE
    $pushOut | Out-String | Add-Content -Path $logFile

    if ($pushExit -eq 0) {
        Write-SyncLog "pushed to origin/main"
    } else {
        Write-SyncLog "push FAILED (exit=$pushExit) -- commit stays ahead, will retry next cycle"

        # Smart diagnostic: parse `denied to <user>` to distinguish trap 12a
        # (expired/wrong-scope PAT for repo owner) from 12b (wrong account
        # entirely -- collaborator missing). See memory/2026-05-09_hooks-debugging.md.
        $pushText = ($pushOut | Out-String)
        if ($pushText -match 'denied to (?<user>[\w.-]+)') {
            $deniedUser = $Matches['user']
            # Extract repo owner from origin URL
            $originUrl = & git remote get-url origin 2>$null
            if ($originUrl -match 'github\.com[:/](?<owner>[\w.-]+)/') {
                $repoOwner = $Matches['owner']
                if ($deniedUser -eq $repoOwner) {
                    Write-SyncLog "diagnose: 403 denied to '$deniedUser' (owner) -- likely expired PAT or insufficient scope (trap 12a). Run: cmdkey /delete:LegacyGeneric:target=git:https://github.com  then re-push."
                } else {
                    Write-SyncLog "diagnose: 403 denied to '$deniedUser' (not owner '$repoOwner') -- WRONG ACCOUNT or missing collaborator (trap 12b). Owner must add '$deniedUser' as collaborator in repo Settings."
                }
            }
        } elseif ($pushText -match 'Proxy CONNECT aborted') {
            Write-SyncLog "diagnose: proxy CONNECT aborted -- corp proxy blocking git. Check whether HTTP_PROXY env is needed for git on this machine (often NOT). See trap 6, 15."
        } elseif ($pushText -match 'could not read Username') {
            Write-SyncLog "diagnose: GIT_TERMINAL_PROMPT=0 prevented interactive auth -- means credentials missing. Run `git push origin main` manually once to trigger Credential Manager flow."
        }
    }
} catch {
    Write-SyncLog "exception: $_"
} finally {
    Pop-Location
}

# Always exit 0 -- never block session end
exit 0

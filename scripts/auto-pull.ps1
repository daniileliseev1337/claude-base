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

# Retry wrapper для git pull. Retryable errors:
# SSL handshake glitches, schannel/TLS, transient network, DNS, connection reset.
# 3 попытки с 5-сек паузой между ними.
function Invoke-GitPullRetry {
    param([int]$MaxAttempts = 3, [int]$DelaySec = 5)
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        $out = & git -c http.proxy="" -c https.proxy="" pull --rebase --autostash 2>&1
        $exit = $LASTEXITCODE
        if ($exit -eq 0) {
            return @{ Success = $true; Output = $out; Attempts = $i }
        }
        $text = ($out | Out-String)
        $isRetryable = (
            $text -match 'schannel' -or
            $text -match 'SSL/TLS' -or
            $text -match 'handshake' -or
            $text -match 'Connection reset' -or
            $text -match 'Could not resolve' -or
            $text -match 'Failed to connect' -or
            $text -match 'transient' -or
            $text -match 'Operation timed out'
        )
        if (-not $isRetryable -or $i -eq $MaxAttempts) {
            return @{ Success = $false; Output = $out; Attempts = $i }
        }
        Write-SyncLog "pull attempt $i/$MaxAttempts failed (retryable: SSL/network), retry in ${DelaySec}s..."
        Start-Sleep -Seconds $DelaySec
    }
}

# Skip if ~/.claude/ is not a git repo
if (-not (Test-Path (Join-Path $claudeDir '.git'))) {
    exit 0
}

Push-Location $claudeDir
try {
    # Pre-flight: проверить не была ли прервана предыдущая операция
    $lastLines = Get-Content $logFile -Tail 8 -ErrorAction SilentlyContinue
    if ($lastLines) {
        $lastEntry = ($lastLines | Where-Object { $_ -match 'auto-(pull|push):' } | Select-Object -Last 1)
        if ($lastEntry -match 'auto-(pull|push): start' -and
            $lastEntry -notmatch 'DONE|ok|FAILED|pushed|no managed') {
            Write-SyncLog "WARN: previous hook was interrupted (last: '$lastEntry'). Возможно timeout или kill."
        }
    }

    Write-SyncLog "start"

    # === Zero-touch GitHub bypass-proxy (idempotent) ===
    # Корп-прокси блокирует CONNECT к github.com. Для ручных git/gh операций
    # пользователю нужен persistent global config bypass. Применяем сами при
    # первом auto-pull на каждом ПК. Idempotent — если уже настроено, skip.
    # См. CLAUDE.md раздел "GitHub — обязательный bypass proxy".
    $ghBypass = & git config --global --get http.https://github.com/.proxy 2>$null
    if ($null -eq $ghBypass) {
        & git config --global http.https://github.com/.proxy "" 2>&1 | Out-Null
        & git config --global https.https://github.com/.proxy "" 2>&1 | Out-Null
        Write-SyncLog "GitHub bypass-proxy auto-applied (was unset) — manual git/gh ops к GitHub теперь работают без -c флагов"
    }

    # Sanity check ДО pull — узнать сколько коммитов мы behind
    & git fetch --quiet origin main 2>&1 | Out-Null
    $beforeBehind = & git rev-list --count HEAD..origin/main 2>$null
    if ($beforeBehind -and [int]$beforeBehind -gt 0) {
        Write-SyncLog "behind origin by $beforeBehind commit(s), will rebase"
    }

    $pullResult = Invoke-GitPullRetry -MaxAttempts 3 -DelaySec 5
    $output = $pullResult.Output
    $exit = if ($pullResult.Success) { 0 } else { 1 }

    $output | Out-String | Add-Content -Path $logFile

    if ($exit -ne 0) {
        Write-SyncLog "FAILED after $($pullResult.Attempts) attempt(s), aborting rebase"
        & git rebase --abort 2>&1 | Out-Null
    } else {
        # Sanity check ПОСЛЕ pull — точно ли подтянули
        $afterBehind = & git rev-list --count HEAD..origin/main 2>$null
        if ($beforeBehind -and [int]$beforeBehind -gt 0 -and [int]$afterBehind -gt 0) {
            Write-SyncLog "WARN: pull reported success but HEAD still behind by $afterBehind (something wrong)"
        }
        $tag = if ($pullResult.Attempts -gt 1) {
            "ok (after $($pullResult.Attempts) attempts, pulled $beforeBehind commit(s))"
        } elseif ([int]$beforeBehind -gt 0) {
            "ok (pulled $beforeBehind commit(s))"
        } else {
            "ok (already up to date)"
        }
        Write-SyncLog $tag
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
    # === Merge shared settings → personal (Phase 1 sync-redesign 2026-05-21) ===
    # После успешного pull — вливаем shared values в local settings.json.
    # Идемпотентен: если ничего не изменилось, no-op.
    $mergeScript = Join-Path $claudeDir 'scripts\merge-shared-settings.ps1'
    if (Test-Path $mergeScript) {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $mergeScript 2>&1 | Out-Null
    }
} catch {
    Write-SyncLog "exception: $_"
} finally {
    Pop-Location
    Write-SyncLog "DONE"
}

# Always exit 0 -- never block session start
exit 0

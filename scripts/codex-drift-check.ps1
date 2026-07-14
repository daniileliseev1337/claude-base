<#
.SYNOPSIS
SessionStart hook (после auto-pull): дрейф-скан ~/.codex (Эпик 1, Гибрид C).
exit 0 всегда. 0=молчание; canon-newer=тихий sync + строка; manual-drift=строка-эскалация.
#>
$ErrorActionPreference = 'SilentlyContinue'
$claudeDir = Join-Path $env:USERPROFILE '.claude'
try {
    if (-not (Test-Path (Join-Path $env:USERPROFILE '.codex'))) { exit 0 }
    # общий lock с codex-autosync.ps1: параллельный sync из двух хуков недопустим;
    # протухший (>120 c) игнорируется
    $lock = Join-Path $claudeDir '.local-state\codex-sync.lock'
    if ((Test-Path $lock) -and (((Get-Date) - (Get-Item $lock).LastWriteTime).TotalSeconds -lt 120)) { exit 0 }
    New-Item -ItemType File -Force -Path $lock | Out-Null
    try {
        $env:PYTHONIOENCODING = 'utf-8'
        $syncPy = Join-Path $claudeDir 'scripts\codex_sync.py'
        $report = & python $syncPy check 2>$null
        $code = $LASTEXITCODE
        if ($code -eq 2) {
            & python $syncPy sync 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Output "✓ codex-синк: канон новее — ~/.codex пересобран"
            } else {
                Write-Output "⚠ codex-синк не прошёл (exit $LASTEXITCODE) — python ~/.claude/scripts/codex_sync.py check"
            }
        } elseif ($code -eq 3) {
            Write-Output "⚠ дрейф ~/.codex (ручные правки поверх генератора) — занести в канон или отбросить:"
            $report | Where-Object { $_ -match 'manual-drift' } | ForEach-Object { Write-Output ("  " + $_) }
            Write-Output "  diff: python ~/.claude/scripts/codex_sync.py diff · отбросить: ... sync --force-overwrite <ключ|all>"
        }
        # Эпик 3: активный доменный мост — напоминание + контроль CRLF-патча
        $overlay = Join-Path $claudeDir '.local-state\codex-mcp-overlay.json'
        if (Test-Path $overlay) {
            $names = $null
            try { $names = (Get-Content $overlay -Raw -Encoding UTF8 | ConvertFrom-Json).enable } catch {}
            if ($names -and $names.Count -gt 0) {
                Write-Output ("i доменный MCP-мост Codex включён: " + ($names -join ', ') + " — после задачи: python ~/.claude/scripts/codex_sync.py mcp off")
                & python (Join-Path $claudeDir 'scripts\mcp_crlf_patch.py') --from-overlay --check 2>$null | Out-Null
                if ($LASTEXITCODE -ne 0) {
                    Write-Output ("! CRLF-патч слетел (обновление venv?) — python ~/.claude/scripts/codex_sync.py mcp on " + ($names -join ' '))
                }
            }
        }
    } finally { Remove-Item -Force $lock }
} catch { }
exit 0

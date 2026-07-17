<#
.SYNOPSIS
PostToolUse(Edit|Write) hook: правка канона ~/.claude -> codex_sync.py sync (Эпик 1, Гибрид C).
Всегда exit 0. Тихо выходит: не-канонный путь, нет ~/.codex, свежий lock.
#>
$ErrorActionPreference = 'SilentlyContinue'
$claudeDir = Join-Path $env:USERPROFILE '.claude'
$logFile   = Join-Path $claudeDir 'auto-sync.log'
function Write-SyncLog { param($msg)
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] codex-autosync: $msg" | Add-Content -LiteralPath $logFile -Encoding UTF8
}
try {
    if (-not [Console]::IsInputRedirected) { exit 0 }
    try {
        [Console]::InputEncoding  = New-Object System.Text.UTF8Encoding($false)
        [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
    } catch { }
    $raw = [Console]::In.ReadToEnd()
    if (-not $raw -or -not $raw.Trim()) { exit 0 }
    $payload = ($raw.Trim([char]0xFEFF)) | ConvertFrom-Json
    $fp = $payload.tool_input.file_path
    if (-not $fp) { exit 0 }
    $fpNorm = ([IO.Path]::GetFullPath($fp)).ToLowerInvariant()
    $hit = $false
    foreach ($sub in @('core','codex-layer','agents','skills')) {
        $w = ([IO.Path]::GetFullPath((Join-Path $claudeDir $sub)) + '\').ToLowerInvariant()
        if ($fpNorm.StartsWith($w)) { $hit = $true; break }
    }
    if (-not $hit) { exit 0 }
    if (-not (Test-Path (Join-Path $env:USERPROFILE '.codex'))) { exit 0 }
    # lock от параллельных прогонов; протухший (>120 c) игнорируется
    $lock = Join-Path $claudeDir '.local-state\codex-sync.lock'
    if ((Test-Path $lock) -and (((Get-Date) - (Get-Item $lock).LastWriteTime).TotalSeconds -lt 120)) { exit 0 }
    New-Item -ItemType File -Force -Path $lock | Out-Null
    try {
        $env:PYTHONIOENCODING = 'utf-8'
        & python (Join-Path $claudeDir 'scripts\codex_sync.py') sync 2>> $logFile | Out-Null
        if ($LASTEXITCODE -eq 3) {
            Write-Output "⚠ codex-sync: ручной дрейф в ~/.codex не перезаписан — 'python ~/.claude/scripts/codex_sync.py diff' и занести в канон или --force-overwrite"
        } elseif ($LASTEXITCODE -ne 0) {
            Write-Output "⚠ codex-sync failed (exit $LASTEXITCODE) — детали в ~/.claude/auto-sync.log"
            Write-SyncLog "sync exit $LASTEXITCODE (file: $fp)"
        } else {
            Write-SyncLog "sync OK (trigger: $fp)"
        }
    } finally { Remove-Item -Force $lock }
} catch { Write-SyncLog "exception: $_" }
exit 0

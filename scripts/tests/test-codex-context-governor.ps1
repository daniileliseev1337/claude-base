param([switch]$KeepTmp)
$ErrorActionPreference = 'Stop'

$hook = Join-Path (Split-Path $PSScriptRoot -Parent) 'codex_context_governor.ps1'
if (-not (Test-Path -LiteralPath $hook)) { throw 'governor hook not found' }

$tmp = Join-Path $env:TEMP ('codex-governor-test-' + [guid]::NewGuid().ToString('N'))
$originalProfile = $env:USERPROFILE
$global:OutputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)

function Invoke-Governor([string]$event, [string]$turn) {
    $payload = [ordered]@{
        session_id = 'governor-test-session'
        cwd = 'C:\demo'
        turn_id = $turn
        model = 'gpt-5.6-terra'
        hook_event_name = $event
    } | ConvertTo-Json -Compress
    $out = $payload | & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $hook 2>$null
    if ($LASTEXITCODE -ne 0) { throw "$event exited $LASTEXITCODE" }
    return ($out | Out-String)
}

try {
    $env:USERPROFILE = $tmp
    $pre = Invoke-Governor 'PreCompact' 'turn-pre' | ConvertFrom-Json
    if ($pre.continue -ne $false -or $pre.stopReason -notmatch 'handoff' -or $pre.systemMessage -notmatch '190k') {
        throw 'PreCompact contract failed'
    }
    $post = Invoke-Governor 'PostCompact' 'turn-post' | ConvertFrom-Json
    if ($post.systemMessage -notmatch 'Automatic compaction') { throw 'PostCompact contract failed' }
    $statePath = Join-Path $tmp '.claude\.local-state\codex-context-governor\governor-test-session.json'
    $state = Get-Content -Raw -Encoding utf8 $statePath | ConvertFrom-Json
    if ($state.event -ne 'PostCompact' -or $state.turn_id -ne 'turn-post') { throw 'state contract failed' }
    Write-Host 'PASS codex context governor contract'
} finally {
    $env:USERPROFILE = $originalProfile
    if (-not $KeepTmp) { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}

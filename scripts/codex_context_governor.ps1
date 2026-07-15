$ErrorActionPreference = 'SilentlyContinue'

try {
    [Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
} catch { }

try {
    $raw = [Console]::In.ReadToEnd()
    if ($raw) { $raw = $raw.Trim([char]0xFEFF) }
    $event = $raw | ConvertFrom-Json
    if ($event.hook_event_name -notin @('PreCompact', 'PostCompact')) { exit 0 }

    $stateDir = Join-Path $env:USERPROFILE '.claude\.local-state\codex-context-governor'
    New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
    $session = if ($event.session_id) { $event.session_id } else { 'unknown-session' }
    $state = [ordered]@{
        event = $event.hook_event_name
        session_id = $event.session_id
        cwd = $event.cwd
        turn_id = $event.turn_id
        model = $event.model
        recorded_at = (Get-Date).ToString('o')
    }
    $state | ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $stateDir "$session.json") -Encoding utf8

    if ($event.hook_event_name -eq 'PreCompact') {
        [ordered]@{
            continue = $false
            stopReason = 'Context governor: handoff required before compaction.'
            systemMessage = 'Context reached the native 190k limit. Before continuing: finish a safe step, update Claude/STATUS.md, the top session journal and session-report; then prepare a LITE prompt with state links and move to a new task. Do not estimate tokens from the transcript.'
        } | ConvertTo-Json -Compress
    } else {
        [ordered]@{
            systemMessage = 'Automatic compaction completed. Check the context-governor record; handoff before the next substantive step remains preferred.'
        } | ConvertTo-Json -Compress
    }
} catch {
    exit 0
}

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
    $handoffLite = 'Continue after PreCompact. First read Claude/CLAUDE.md, the top of Claude/ЖУРНАЛ СЕССИЙ.md, and Claude/STATUS.md; finish a safe step, update STATUS, the journal, and the current session-report. Then continue only with the recorded next step. Do not estimate context from the transcript.'
    $state = [ordered]@{
        event = $event.hook_event_name
        session_id = $event.session_id
        cwd = $event.cwd
        turn_id = $event.turn_id
        model = $event.model
        recorded_at = (Get-Date).ToString('o')
        handoff_required = ($event.hook_event_name -eq 'PreCompact')
        handoff_lite = $handoffLite
    }
    $state | ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $stateDir "$session.json") -Encoding utf8

    if ($event.hook_event_name -eq 'PreCompact') {
        [ordered]@{
            continue = $false
            stopReason = 'Context governor: handoff required before compaction.'
            systemMessage = 'Auto-compaction stopped: handoff required. Before the next substantive step, finish a safe step and update Claude/STATUS.md, the top session journal, and the current session-report. Then create a new task with the LITE prompt in governor state. Do not estimate tokens from the transcript.'
        } | ConvertTo-Json -Compress
    } else {
        [ordered]@{
            systemMessage = 'Automatic compaction completed. Check context-governor state; handoff remains preferred before the next substantive step.'
        } | ConvertTo-Json -Compress
    }
} catch {
    exit 0
}

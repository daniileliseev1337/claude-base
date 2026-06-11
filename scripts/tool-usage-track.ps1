# PostToolUse-хук: телеметрия tool calls + напоминание о гейте сессии при пороге.
# Пишет ~/.claude/.local-state/tool-usage.jsonl; каждые 75 вызовов сессии подсказывает
# Claude предложить handoff (см. CLAUDE.md «Токен-дисциплина»).
$ErrorActionPreference = 'SilentlyContinue'
$raw = [Console]::In.ReadToEnd()
try { $j = $raw | ConvertFrom-Json } catch { exit 0 }
if (-not $j.session_id) { exit 0 }

$state = Join-Path $env:USERPROFILE '.claude\.local-state'
$log = Join-Path $state 'tool-usage.jsonl'
if (-not (Test-Path $state)) { New-Item -ItemType Directory -Force $state | Out-Null }

# ротация: > 5 МБ — в архив, чтобы подсчёт не деградировал
$f = Get-Item $log -ErrorAction SilentlyContinue
if ($f -and $f.Length -gt 5MB) { Move-Item $log "$log.old" -Force }

$rec = @{ ts = (Get-Date -Format o); session = $j.session_id; tool = $j.tool_name } | ConvertTo-Json -Compress
Add-Content -Path $log -Value $rec -Encoding utf8

$count = (Select-String -Path $log -Pattern $j.session_id -SimpleMatch).Count
if ($count -ge 75 -and ($count % 75) -eq 0) {
    $msg = "Telemetry: $count tool calls в этой сессии. Сработал гейт сессии (CLAUDE.md 'Токен-дисциплина') — " +
           "если текущая задача позволяет, предложи пользователю handoff в новый чат (skill handoff-to-new-chat). Один раз на задачу."
    @{ hookSpecificOutput = @{ hookEventName = 'PostToolUse'; additionalContext = $msg } } |
        ConvertTo-Json -Compress -Depth 4 | Write-Output
}
exit 0

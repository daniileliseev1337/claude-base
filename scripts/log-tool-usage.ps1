<#
.SYNOPSIS
PostToolUse hook: пишет одну JSONL-строку на каждый вызов инструмента.

.DESCRIPTION
Телеметрия использования инструментов (аудит 2026-06-09: «активы копятся быстрее,
чем используются, и никто не измеряет»). Лог — ~/.claude/.local-state/tool-usage.jsonl,
per-PC, в git не летит (.local-state gitignored). Агрегация — aggregate-tool-usage.ps1.

ПОДКЛЮЧЕНИЕ (после обкатки на dev-ПК — в settings.shared.json):
  "hooks": { "PostToolUse": [ { "matcher": "*", "hooks": [ { "type": "command",
    "command": "& \"$HOME\\.claude\\scripts\\log-tool-usage.ps1\"",
    "shell": "powershell", "timeout": 10 } ] } ] }

Hook получает JSON в stdin: tool_name, tool_input, session_id и др.
Всегда exit 0 — телеметрия НИКОГДА не должна ломать работу.
#>

$ErrorActionPreference = 'SilentlyContinue'
try {
    $raw = [Console]::In.ReadToEnd()
    $j = $raw | ConvertFrom-Json

    $entry = [ordered]@{
        ts   = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
        tool = $j.tool_name
    }
    # Для спавна агентов фиксируем КАКОЙ агент; для скиллов — какой скилл
    if ($j.tool_name -in @('Task','Agent') -and $j.tool_input.subagent_type) {
        $entry.agent = $j.tool_input.subagent_type
    }
    if ($j.tool_name -eq 'Skill' -and $j.tool_input.skill) {
        $entry.skill = $j.tool_input.skill
    }

    $dir = Join-Path $env:USERPROFILE '.claude\.local-state'
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $logFile = Join-Path $dir 'tool-usage.jsonl'
    ($entry | ConvertTo-Json -Compress) | Add-Content -Path $logFile -Encoding UTF8
} catch { }
exit 0

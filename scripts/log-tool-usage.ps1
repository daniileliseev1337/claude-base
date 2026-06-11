<#
.SYNOPSIS
PostToolUse hook: пишет одну JSONL-строку на каждый вызов инструмента
+ каждые 75 вызовов сессии напоминает про гейт сессии (CLAUDE.md «Токен-дисциплина»).

.DESCRIPTION
Телеметрия использования инструментов (аудит 2026-06-09: «активы копятся быстрее,
чем используются, и никто не измеряет»). Лог — ~/.claude/.local-state/tool-usage.jsonl,
per-PC, в git не летит (.local-state gitignored). Агрегация — aggregate-tool-usage.ps1.

С 2026-06-11 добавлено (инцидент 100M токенов/день): поле session + порог-напоминание.
На пороге (каждые 75 вызовов за сессию) хук возвращает additionalContext — Claude
обязан предложить пользователю handoff в новый чат (длинный хвост сессии умножает
cache-read расход).

ПОДКЛЮЧЕНИЕ (после обкатки на dev-ПК — в settings.shared.json):
  "hooks": { "PostToolUse": [ { "matcher": "*", "hooks": [ { "type": "command",
    "command": "& \"$HOME\\.claude\\scripts\\log-tool-usage.ps1\"",
    "shell": "powershell", "timeout": 10 } ] } ] }

Hook получает JSON в stdin: tool_name, tool_input, session_id и др.
Всегда exit 0 — телеметрия НИКОГДА не должна ломать работу.
ВАЖНО: файл сохранён в UTF-8 С BOM — powershell.exe 5.1 без BOM читает кириллицу
как ANSI и ломается на парсинге (байт «ё» = смарт-кавычка).
#>

$ErrorActionPreference = 'SilentlyContinue'
try {
    $raw = [Console]::In.ReadToEnd()
    $j = $raw | ConvertFrom-Json

    $entry = [ordered]@{
        ts   = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
        tool = $j.tool_name
    }
    if ($j.session_id) { $entry.session = $j.session_id }
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

    # Ротация: > 5 МБ — в .old, чтобы подсчёт порога не деградировал
    $f = Get-Item $logFile -ErrorAction SilentlyContinue
    if ($f -and $f.Length -gt 5MB) { Move-Item $logFile "$logFile.old" -Force }

    ($entry | ConvertTo-Json -Compress) | Add-Content -Path $logFile -Encoding UTF8

    # Порог-напоминание: каждые 75 вызовов текущей сессии
    if ($j.session_id) {
        $count = (Select-String -Path $logFile -Pattern $j.session_id -SimpleMatch).Count
        if ($count -ge 75 -and ($count % 75) -eq 0) {
            $msg = "Telemetry: $count tool calls в этой сессии. Сработал гейт сессии " +
                   "(CLAUDE.md 'Токен-дисциплина') — если текущая задача позволяет, предложи " +
                   "пользователю handoff в новый чат (skill handoff-to-new-chat). Один раз на задачу."
            @{ hookSpecificOutput = @{ hookEventName = 'PostToolUse'; additionalContext = $msg } } |
                ConvertTo-Json -Compress -Depth 4 | Write-Output
        }
    }
} catch { }
exit 0

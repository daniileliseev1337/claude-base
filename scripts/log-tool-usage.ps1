<#
.SYNOPSIS
PostToolUse hook: пишет одну JSONL-строку на каждый вызов инструмента
+ гейт сессии ПО ВЕСУ tool-результатов (Блок 2 реворка, 2026-07-06).

.DESCRIPTION
Телеметрия использования инструментов (аудит 2026-06-09: «активы копятся быстрее,
чем используются, и никто не измеряет»). Лог — ~/.claude/.local-state/tool-usage.jsonl,
per-PC, в git не летит (.local-state gitignored). Агрегация — aggregate-tool-usage.ps1.

История гейта:
- 2026-06-11 (инцидент 100M токенов/день): порог = 75 ВЫЗОВОВ, повтор каждые 75.
- 2026-07-06 (Блок 2 реворка): счётчик штук заменён ВЕСОМ — суммой байт
  tool_response, вернувшихся в ОСНОВНОЙ контекст. Причины (проверено фактами):
  subagent-driven сессии делают много ЛЁГКИХ вызовов (гейт орал рано при 142 KB
  веса), `%75` повторялся (75/150/...) и терялся в гонке параллельных вызовов,
  сообщение приходило OEM-кракозябрами. Калибровка по 12 живым транскриптам:
  тяжёлые сессии = 1.0–1.8 МБ tool-результатов, средние 375–574 КБ.

Механика гейта:
- вес вызова = длина ConvertTo-Json(tool_response); копится в
  .local-state/toolgate/<session_id>.json под именованным mutex (гонки нет);
- порог: 512 КБ (~130K токенов результатов), override — env CLAUDE_TOOLGATE_BYTES;
- срабатывает ОДИН раз на сессию — на первом пересечении порога (fired=true);
- субагентские вызовы (transcript_path содержит \subagents\) в вес не идут,
  в телеметрию пишутся с sub=1; без session_id — телеметрия без гейта.

ПОДКЛЮЧЕНИЕ (settings.json / settings.shared.json):
  "hooks": { "PostToolUse": [ { "matcher": "*", "hooks": [ { "type": "command",
    "command": "& \"$HOME\\.claude\\scripts\\log-tool-usage.ps1\"",
    "shell": "powershell", "timeout": 10 } ] } ] }

Hook получает JSON в stdin: session_id, transcript_path, cwd, tool_name,
tool_input, tool_response, duration_ms и др. Всегда exit 0 — телеметрия
НИКОГДА не должна ломать работу.
ВАЖНО: файл сохранён в UTF-8 С BOM — powershell.exe 5.1 без BOM читает кириллицу
как ANSI и ломается на парсинге. Тесты: scripts/tests/test-toolgate.ps1.
#>

$ErrorActionPreference = 'SilentlyContinue'
try {
    # UTF-8 в обе стороны: PS 5.1 по умолчанию OEM-866 — stdin с кириллицей
    # приходит покалеченным, а additionalContext уезжает кракозябрами
    # (доказано вживую 2026-07-06).
    try {
        [Console]::InputEncoding  = New-Object System.Text.UTF8Encoding($false)
        [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
    } catch { }

    $raw = [Console]::In.ReadToEnd()
    if ($raw) { $raw = $raw.Trim([char]0xFEFF) }   # защитный срез BOM
    $j = $raw | ConvertFrom-Json

    # Вес того, что ВЕРНУЛОСЬ в основной контекст этим вызовом
    $bytes = 0
    if ($j.tool_response) {
        $s = $j.tool_response | ConvertTo-Json -Compress -Depth 10
        if ($s) { $bytes = $s.Length }
    }
    $isSub = ("$($j.transcript_path)" -match '[\\/]subagents[\\/]')

    $entry = [ordered]@{
        ts   = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
        tool = $j.tool_name
    }
    if ($j.session_id) { $entry.session = $j.session_id }
    $entry.bytes = $bytes
    if ($isSub) { $entry.sub = 1 }
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

    # Append + ротация под общим mutex: параллельные вызовы теряли строки
    # (Add-Content натыкался на занятый файл и молча глотал ошибку) — та же
    # гонка, что глушила старый %75-порог.
    $logMutex = New-Object System.Threading.Mutex($false, 'claude-toolusage-log')
    $null = $logMutex.WaitOne(3000)
    try {
        # Ротация телеметрии: > 5 МБ — в .old (гейт от длины jsonl не зависит)
        $f = Get-Item $logFile -ErrorAction SilentlyContinue
        if ($f -and $f.Length -gt 5MB) { Move-Item $logFile "$logFile.old" -Force }
        ($entry | ConvertTo-Json -Compress) | Add-Content -Path $logFile -Encoding UTF8
    } finally {
        try { $logMutex.ReleaseMutex() } catch { }
        $logMutex.Dispose()
    }

    # ===== Гейт сессии по весу =====
    if ($j.session_id -and -not $isSub) {
        $gateBytes = 512KB
        if ($env:CLAUDE_TOOLGATE_BYTES -match '^\d+$') { $gateBytes = [long]$env:CLAUDE_TOOLGATE_BYTES }

        $stateDir = Join-Path $dir 'toolgate'
        if (-not (Test-Path $stateDir)) { New-Item -ItemType Directory -Path $stateDir -Force | Out-Null }
        # housekeeping: состояния сессий старше 7 дней (только уборка, НЕ логика гейта)
        try {
            Get-ChildItem $stateDir -Filter '*.json' -ErrorAction SilentlyContinue |
                Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } |
                Remove-Item -Force -ErrorAction SilentlyContinue
        } catch { }

        $stateFile = Join-Path $stateDir ($j.session_id + '.json')
        $fireNow = $false; $total = 0

        $mutex = New-Object System.Threading.Mutex($false, ('claude-toolgate-' + $j.session_id))
        # Результат WaitOne сознательно не проверяется (риск принят, аудит 2026-07-06):
        # при таймауте 5с продолжаем без лока — держатели только копии этого же хука
        # (миллисекунды), а зависание/точность гейта дешевле, чем потеря телеметрии.
        $null = $mutex.WaitOne(5000)
        try {
            $st = $null
            if (Test-Path $stateFile) {
                $st = Get-Content $stateFile -Raw -Encoding UTF8 | ConvertFrom-Json
            }
            if (-not $st) { $st = [pscustomobject]@{ bytes = 0; fired = $false } }
            $total = [long]$st.bytes + $bytes
            $fireNow = (-not $st.fired) -and ($total -ge $gateBytes)
            $newState = [ordered]@{ bytes = $total; fired = ([bool]$st.fired -or $fireNow) }
            ($newState | ConvertTo-Json -Compress) | Set-Content -Path $stateFile -Encoding UTF8
        } finally {
            try { $mutex.ReleaseMutex() } catch { }
            $mutex.Dispose()
        }

        if ($fireNow) {
            $kb = [math]::Round($total / 1KB)
            $limitKb = [math]::Round($gateBytes / 1KB)
            $msg = "Сработал гейт сессии по весу: ~$kb KB tool-результатов вернулось в основной контекст (порог $limitKb KB). " +
                   "CLAUDE.md 'Токен-дисциплина': на границе текущей задачи предложи пользователю handoff " +
                   "в новый чат (skill handoff-to-new-chat). Напоминание одно на сессию — дальше решает человек."
            @{ hookSpecificOutput = @{ hookEventName = 'PostToolUse'; additionalContext = $msg } } |
                ConvertTo-Json -Compress -Depth 4 | Write-Output
        }
    }
} catch { }
exit 0

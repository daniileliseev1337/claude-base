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
- 2026-07-07 (v2.5, решение владельца): ПЕРВИЧНЫЙ сигнал = РЕАЛЬНЫЙ token-fill
  окна из транскрипта сессии (каждый api-ход пишет usage; последняя запись =
  фактический размер контекста). Байт-прокси остался ТОЛЬКО fallback'ом, когда
  транскрипт недоступен/не парсится. Порог владельца: ~70% окна 1M.

Механика гейта:
- ПЕРВИЧНО: реальный контекст = input + cache_creation + cache_read из ПОСЛЕДНЕЙ
  usage-записи transcript_path (хвост файла ~256 КБ, парс с конца); порог
  700000 токенов (≈70% окна 1M), override — env CLAUDE_TOOLGATE_CTX_TOKENS
  (машины с окном 200K: ставить ~140000);
- FALLBACK (транскрипта нет/битый): вес = длина ConvertTo-Json(tool_response),
  копится в .local-state/toolgate/<session_id>.json; порог 512 КБ (~130K токенов
  результатов), override — env CLAUDE_TOOLGATE_BYTES;
- срабатывает ОДИН раз на сессию — на первом пересечении (fired=true), стейт
  под именованным mutex (гонки нет);
- субагентские вызовы (transcript_path содержит \subagents\) в гейт не идут,
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

# Реальный размер контекста сессии: последняя usage-запись транскрипта
# (input + cache_creation + cache_read). Возврат -1 = «не знаю» -> fallback на байты.
function Get-ContextTokens([string]$tp) {
    try {
        if (-not $tp) { return -1 }
        if (-not (Test-Path -LiteralPath $tp)) { return -1 }
        $fs = [IO.File]::Open($tp, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
        try {
            $take = [Math]::Min($fs.Length, 262144)
            if ($take -le 0) { return -1 }
            $null = $fs.Seek(-$take, [IO.SeekOrigin]::End)
            $buf = New-Object byte[] ([int]$take)
            $null = $fs.Read($buf, 0, [int]$take)
        } finally { $fs.Dispose() }
        $lines = ([Text.Encoding]::UTF8.GetString($buf)) -split "`n"
        for ($i = $lines.Count - 1; $i -ge 0; $i--) {
            $L = $lines[$i]
            if ($L -notmatch '"usage"' -or $L -notmatch '"input_tokens"') { continue }
            try {
                $u = ($L | ConvertFrom-Json).message.usage
                if ($u -and $null -ne $u.input_tokens) {
                    return [long]$u.input_tokens + [long]$u.cache_creation_input_tokens + [long]$u.cache_read_input_tokens
                }
            } catch { }   # обрезанная/чужая строка хвоста — идём выше
        }
        return -1
    } catch { return -1 }
}

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

    # ===== Гейт сессии: реальный token-fill, fallback — вес байт =====
    if ($j.session_id -and -not $isSub) {
        $gateBytes = 512KB
        if ($env:CLAUDE_TOOLGATE_BYTES -match '^\d+$') { $gateBytes = [long]$env:CLAUDE_TOOLGATE_BYTES }
        $ctxLimit = 700000
        if ($env:CLAUDE_TOOLGATE_CTX_TOKENS -match '^\d+$') { $ctxLimit = [long]$env:CLAUDE_TOOLGATE_CTX_TOKENS }
        $ctx = Get-ContextTokens "$($j.transcript_path)"

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
            if ($ctx -gt 0) {
                # первичный сигнал: реальный контекст из транскрипта
                $fireNow = (-not $st.fired) -and ($ctx -ge $ctxLimit)
            } else {
                # fallback: накопленный вес tool-результатов
                $fireNow = (-not $st.fired) -and ($total -ge $gateBytes)
            }
            $newState = [ordered]@{ bytes = $total; fired = ([bool]$st.fired -or $fireNow); ctx = $ctx }
            ($newState | ConvertTo-Json -Compress) | Set-Content -Path $stateFile -Encoding UTF8
        } finally {
            try { $mutex.ReleaseMutex() } catch { }
            $mutex.Dispose()
        }

        if ($fireNow) {
            if ($ctx -gt 0) {
                $msg = "Сработал гейт сессии: РЕАЛЬНЫЙ контекст ~$ctx токенов (порог $ctxLimit, env CLAUDE_TOOLGATE_CTX_TOKENS). " +
                       "CLAUDE.md 'Токен-дисциплина': на границе текущей задачи предложи пользователю handoff " +
                       "в новый чат (skill handoff-to-new-chat). Напоминание одно на сессию — дальше решает человек."
            } else {
                $kb = [math]::Round($total / 1KB)
                $limitKb = [math]::Round($gateBytes / 1KB)
                $msg = "Сработал гейт сессии по весу (fallback, транскрипт недоступен): ~$kb KB tool-результатов " +
                       "вернулось в основной контекст (порог $limitKb KB). CLAUDE.md 'Токен-дисциплина': на границе " +
                       "текущей задачи предложи пользователю handoff в новый чат (skill handoff-to-new-chat). " +
                       "Напоминание одно на сессию — дальше решает человек."
            }
            @{ hookSpecificOutput = @{ hookEventName = 'PostToolUse'; additionalContext = $msg } } |
                ConvertTo-Json -Compress -Depth 4 | Write-Output
        }
    }
} catch { }
exit 0

# test-toolgate.ps1 - black-box tests for log-tool-usage.ps1 (Blok 2 rework:
# weight-based session gate instead of call counter-75).
# Contract under test:
#   T1 telemetry line per call: ts/tool/session + bytes (serialized tool_response length)
#   T2 no fire below threshold; per-session state file toolgate/<session>.json accumulates bytes
#   T3 fire EXACTLY at first crossing: additionalContext JSON, readable UTF-8 Cyrillic, fired=true
#   T4 never fires again after crossing (once per session)
#   T5 RACE: N parallel invocations -> exactly one fire, bytes sum correct
#   T6 subagent call (transcript_path with \subagents\) -> telemetry sub=1, NO accumulation
#   T7 no session_id -> telemetry only, no state, no fire even with huge payload
#   T8 agent/skill fields preserved (Task->agent, Skill->skill) - aggregate compat
#   T9 exit code always 0
# Threshold override: env CLAUDE_TOOLGATE_BYTES (tests use small values).
# ASCII-only source on purpose (PS 5.1 no-BOM trap). Cyrillic asserted via codepoints.

param([switch]$KeepTmp)
$ErrorActionPreference = 'Stop'
$HookPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'log-tool-usage.ps1'
if (-not (Test-Path $HookPath)) { Write-Host "hook not found: $HookPath"; exit 1 }

# --- isolated environment ---------------------------------------------------
$TmpRoot = Join-Path $env:TEMP ("toolgate-test-" + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Path $TmpRoot -Force | Out-Null
$OrigProfile = $env:USERPROFILE
$OrigGate    = $env:CLAUDE_TOOLGATE_BYTES

# child processes must receive UTF-8 on stdin (mirrors the harness).
# CRITICAL: BOM-less! [Text.Encoding]::UTF8 prepends BOM to the pipe and the
# child's JSON parse dies on it (proven 2026-07-06).
$global:OutputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)

$script:Pass = 0; $script:Fail = 0
function Assert([bool]$cond, [string]$name) {
    if ($cond) { $script:Pass++; Write-Host "  PASS  $name" }
    else       { $script:Fail++; Write-Host "  FAIL  $name" -ForegroundColor Red }
}

# word "geyt" (Cyrillic) built from codepoints - the fire-message must contain it readable
$CyrGate = [string]([char]0x0433) + [char]0x0435 + [char]0x0439 + [char]0x0442

function New-Payload {
    param([string]$Session, [int]$RespChars = 100, [string]$Tool = 'Read',
          [string]$Transcript = 'C:\fake\projects\proj\sess.jsonl', [hashtable]$ToolInput)
    $p = [ordered]@{
        session_id      = $Session
        transcript_path = $Transcript
        cwd             = 'C:\fake\proj'
        hook_event_name = 'PostToolUse'
        tool_name       = $Tool
        tool_input      = if ($ToolInput) { $ToolInput } else { @{ file_path = 'C:\fake\f.txt' } }
        tool_response   = @{ content = ('x' * $RespChars) }
    }
    if (-not $Session) { $p.Remove('session_id') }
    return ($p | ConvertTo-Json -Compress -Depth 8)
}

function Invoke-Hook([string]$Json) {
    # fresh child powershell per call, isolated USERPROFILE, pipe JSON via stdin
    $out = $Json | & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $HookPath 2>$null
    $script:LastExit = $LASTEXITCODE
    return @($out) -join "`n"
}

function Get-State([string]$Session) {
    $f = Join-Path $TmpRoot ".claude\.local-state\toolgate\$Session.json"
    if (Test-Path $f) { return (Get-Content $f -Raw -Encoding UTF8 | ConvertFrom-Json) }
    return $null
}

function Get-TelemetryLines {
    # plain enumerating return: rows flow through pipelines one-by-one.
    # Callers MUST wrap in @() before .Count (PS 5.1: PSCustomObject has no
    # intrinsic .Count; and a comma-return here would feed Where-Object the
    # whole array as ONE item - both traps hit during Blok 2, see report).
    $f = Join-Path $TmpRoot '.claude\.local-state\tool-usage.jsonl'
    if (Test-Path $f) { Get-Content $f -Encoding UTF8 | Where-Object { $_ } |
        ForEach-Object { try { $_ | ConvertFrom-Json } catch {} } | Where-Object { $_ } }
}

try {
    $env:USERPROFILE = $TmpRoot
    $env:CLAUDE_TOOLGATE_BYTES = '1000'

    Write-Host "== T1/T2: telemetry with bytes, accumulate below threshold, no fire =="
    $s1 = 'test-sess-basic'
    $out1 = Invoke-Hook (New-Payload -Session $s1 -RespChars 100)
    Assert ($out1 -notmatch 'additionalContext') 'T2 no fire below threshold'
    $tele = @(Get-TelemetryLines)
    Assert ($tele.Count -eq 1) 'T1 exactly one telemetry line'
    Assert ($tele[0].tool -eq 'Read' -and $tele[0].session -eq $s1) 'T1 line has tool+session'
    Assert ($tele[0].bytes -gt 100 -and $tele[0].bytes -lt 400) 'T1 line has plausible bytes field'
    $st = Get-State $s1
    Assert ($null -ne $st -and $st.bytes -eq $tele[0].bytes -and -not $st.fired) 'T2 state accumulates, not fired'

    Write-Host "== T3: first crossing fires once, readable UTF-8 =="
    $out2 = Invoke-Hook (New-Payload -Session $s1 -RespChars 1200)
    Assert ($out2 -match 'hookSpecificOutput' -and $out2 -match 'additionalContext') 'T3 fires at first crossing'
    Assert ($out2 -match 'PostToolUse') 'T3 hookEventName present'
    Assert ($out2 -match 'handoff-to-new-chat') 'T3 message mentions handoff skill'
    Assert ($out2.Contains($CyrGate)) 'T3 Cyrillic readable (no mojibake)'
    Assert ($out2 -match 'KB') 'T3 message reports weight in KB'
    $st = Get-State $s1
    Assert ($st.fired -eq $true) 'T3 state marked fired'

    Write-Host "== T4: never fires again in same session =="
    $out3 = Invoke-Hook (New-Payload -Session $s1 -RespChars 5000)
    Assert ($out3 -notmatch 'additionalContext') 'T4 no repeat fire'

    Write-Host "== T6: subagent call -> telemetry flagged, no accumulation =="
    $s2 = 'test-sess-subag'
    $null = Invoke-Hook (New-Payload -Session $s2 -RespChars 3000 -Transcript 'C:\fake\projects\proj\subagents\agent-1.jsonl')
    $st2 = Get-State $s2
    Assert ($null -eq $st2 -or $st2.bytes -eq 0) 'T6 subagent bytes not accumulated'
    $subLines = @(Get-TelemetryLines | Where-Object { $_.session -eq $s2 })
    Assert ($subLines.Count -eq 1 -and $subLines[0].sub -eq 1) 'T6 telemetry line flagged sub=1'

    Write-Host "== T7: no session_id -> telemetry only, no fire =="
    $before = @(Get-TelemetryLines).Count
    $out4 = Invoke-Hook (New-Payload -Session '' -RespChars 5000)
    Assert ($out4 -notmatch 'additionalContext') 'T7 no fire without session'
    Assert (@(Get-TelemetryLines).Count -eq $before + 1) 'T7 telemetry still written'

    Write-Host "== T8: agent/skill fields preserved (aggregate compat) =="
    $s3 = 'test-sess-fields'
    $null = Invoke-Hook (New-Payload -Session $s3 -Tool 'Agent' -ToolInput @{ subagent_type = 'auditor' })
    $null = Invoke-Hook (New-Payload -Session $s3 -Tool 'Skill' -ToolInput @{ skill = 'graphify' })
    $rows3 = @(Get-TelemetryLines | Where-Object { $_.session -eq $s3 })
    Assert (@($rows3 | Where-Object { $_.agent -eq 'auditor' }).Count -eq 1) 'T8 agent field logged'
    Assert (@($rows3 | Where-Object { $_.skill -eq 'graphify' }).Count -eq 1) 'T8 skill field logged'

    Write-Host "== T9: exit code 0 =="
    Assert ($script:LastExit -eq 0) 'T9 exit 0'

    Write-Host "== T5: RACE - 8 parallel invocations, exactly one fire =="
    # Start-Job needs the REAL profile for its persistence path; children get
    # the sandbox profile via arguments inside the scriptblock.
    $env:USERPROFILE = $OrigProfile
    $s5 = 'test-sess-race'
    $env:CLAUDE_TOOLGATE_BYTES = '150000'
    $payload = New-Payload -Session $s5 -RespChars 25000
    $jobs = 1..8 | ForEach-Object {
        Start-Job -ScriptBlock {
            param($json, $hook, $profile, $gate)
            $env:USERPROFILE = $profile
            $env:CLAUDE_TOOLGATE_BYTES = $gate
            $global:OutputEncoding = New-Object System.Text.UTF8Encoding($false)
            $out = $json | & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $hook 2>$null
            return (@($out) -join "`n")
        } -ArgumentList $payload, $HookPath, $TmpRoot, '150000'
    }
    $results = $jobs | Wait-Job -Timeout 120 | Receive-Job
    $jobs | Remove-Job -Force
    $fired = @($results | Where-Object { $_ -match 'additionalContext' })
    Assert ($fired.Count -eq 1) ("T5 exactly one fire under race (got " + $fired.Count + ")")
    $st5 = Get-State $s5
    $expected = 8 * ((New-Payload -Session $s5 -RespChars 25000 | ConvertFrom-Json).tool_response | ConvertTo-Json -Compress -Depth 10).Length
    Assert ($st5.bytes -eq $expected) ("T5 bytes sum exact: " + $st5.bytes + " vs " + $expected)
    # durability, not instant visibility: the last writer may still be
    # flushing when we read - poll briefly before judging
    $raceLines = @()
    for ($i = 0; $i -lt 10; $i++) {
        $raceLines = @(Get-TelemetryLines | Where-Object { $_.session -eq $s5 })
        if ($raceLines.Count -ge 8) { break }
        Start-Sleep -Milliseconds 300
    }
    Assert ($raceLines.Count -eq 8) ("T5 all 8 telemetry lines survived race (got " + $raceLines.Count + ")")
}
finally {
    $env:USERPROFILE = $OrigProfile
    if ($null -ne $OrigGate) { $env:CLAUDE_TOOLGATE_BYTES = $OrigGate }
    else { Remove-Item Env:\CLAUDE_TOOLGATE_BYTES -ErrorAction SilentlyContinue }
    if ($KeepTmp) { Write-Host "KEEP-TMP: $TmpRoot" }
    else { Remove-Item $TmpRoot -Recurse -Force -ErrorAction SilentlyContinue }
}

Write-Host ""
Write-Host ("RESULT: {0} passed, {1} failed" -f $script:Pass, $script:Fail)
if ($script:Fail -gt 0) { exit 1 } else { exit 0 }

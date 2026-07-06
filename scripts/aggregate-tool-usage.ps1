<#
.SYNOPSIS
Сводка телеметрии инструментов: что вызывалось, а что молчит.

.DESCRIPTION
Читает ~/.claude/.local-state/tool-usage.jsonl (пишется log-tool-usage.ps1),
выводит: топ инструментов/агентов/скиллов за период + список агентов и скиллов
базы, которые НИ РАЗУ не вызывались. Запуск руками или из /sync-base.
На consumer-ПК сводку можно приложить абзацем в feedback-отчёт.

.PARAMETER Days
Период в днях (по умолчанию 14).
#>
param([int]$Days = 14)

$claudeDir = Join-Path $env:USERPROFILE '.claude'
$logFile = Join-Path $claudeDir '.local-state\tool-usage.jsonl'
if (-not (Test-Path $logFile)) { Write-Host "Лога нет ($logFile) — hook не подключён?"; exit 0 }

$cutoff = (Get-Date).AddDays(-$Days)
$rows = Get-Content $logFile | ForEach-Object { try { $_ | ConvertFrom-Json } catch {} } |
        Where-Object { $_ -and ([datetime]$_.ts) -ge $cutoff }

Write-Host "=== Телеметрия за $Days дн.: $($rows.Count) вызовов ==="
Write-Host "`n-- Топ инструментов --"
$rows | Group-Object tool | Sort-Object Count -Descending | Select-Object -First 15 |
    ForEach-Object { Write-Host ("  {0,5}  {1}" -f $_.Count, $_.Name) }

Write-Host "`n-- Агенты: вызывались --"
$usedAgents = $rows | Where-Object agent | Group-Object agent | Sort-Object Count -Descending
$usedAgents | ForEach-Object { Write-Host ("  {0,5}  {1}" -f $_.Count, $_.Name) }

Write-Host "`n-- Агенты базы, НЕ вызванные ни разу за период --"
$allAgents = Get-ChildItem (Join-Path $claudeDir 'agents\*.md') |
    Where-Object { $_.Name -notin @('agents.md','_TEMPLATE.md') } |
    ForEach-Object { $_.BaseName }
$silent = $allAgents | Where-Object { $_ -notin $usedAgents.Name }
if ($silent) { $silent | ForEach-Object { Write-Host "  ✗ $_" } } else { Write-Host "  (таких нет)" }

Write-Host "`n-- Скиллы: вызывались --"
$rows | Where-Object skill | Group-Object skill | Sort-Object Count -Descending |
    ForEach-Object { Write-Host ("  {0,5}  {1}" -f $_.Count, $_.Name) }
exit 0

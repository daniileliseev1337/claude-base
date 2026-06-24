# graph-staleness-check.ps1 - SessionStart hook (claude-base)
# Keeps the DETERMINISTIC navigation skeleton always-fresh (0 tokens) so Claude can
# trust it and navigate the base via query instead of grep.
#
# Architecture (see CLAUDE.md graphify section + skills/graphify/references/skeleton.md):
#   * skeleton.json - deterministic backbone (agents/skills/memory/rules/...), built
#     WITHOUT an LLM from structural signals. This hook rebuilds it at session start if
#     it lags HEAD -> on every PC the navigator stays fresh and trustworthy.
#   * graph.json - semantic ENRICHMENT (LLM, hub, occasional). Its staleness is NOT a
#     reason to distrust the graph: the skeleton is fresh. The old "stale graph lies"
#     warnings are removed.
#
# Runs AFTER auto-pull.ps1 (HEAD current). Silent on success. Never breaks session start
# (exit 0 everywhere). ASCII-only on purpose (robust under PowerShell 5.1 / no-BOM).

$ErrorActionPreference = 'SilentlyContinue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}

$base    = Join-Path $HOME '.claude'
$skel    = Join-Path $base 'graphify-out\skeleton.json'
$builder = Join-Path $base 'skills\graphify\tools\skeleton_build.py'
$pyfile  = Join-Path $base 'graphify-out\.graphify_python'
$log     = Join-Path $base 'graphify-out\skeleton-hook.log'
function Write-HookLog($m){ try { Add-Content -LiteralPath $log -Value ((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')+' | '+$m) -Encoding UTF8 -EA SilentlyContinue } catch {} }
if (-not (Test-Path $builder)) { exit 0 }   # skeleton tool not rolled out yet - stay silent

# current HEAD (short)
Push-Location $base
$head = (git rev-parse --short HEAD 2>$null)
Pop-Location

# is the skeleton fresh? (built_at_commit == HEAD)
$fresh = $false
if ((Test-Path $skel) -and $head) {
  $raw = Get-Content $skel -Raw -Encoding UTF8
  if ($raw -match '"built_at_commit"\s*:\s*"([^"]+)"') {
    if ($Matches[1] -eq $head) { $fresh = $true }
  }
}
if ($fresh) { Write-HookLog "HEAD=$head action=fresh-skip"; exit 0 }   # already fresh - quiet

# rebuild the skeleton (deterministic, 0 tokens, seconds)
$py = 'python'
if (Test-Path $pyfile) {
  $p = (Get-Content $pyfile -Raw -Encoding UTF8).Trim()
  if ($p) { $py = $p }
}
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
Push-Location $base
& $py $builder *> $null
$ok = $?
Pop-Location

if ($ok) {
  Write-HookLog "HEAD=$head action=REBUILT-ok"
  Write-Output '[graph] base navigator (skeleton) rebuilt & fresh - query first: python skills/graphify/tools/graph_query.py "your question" (truth lives in source_file).'
} else {
  Write-HookLog "HEAD=$head action=REBUILD-FAILED"
}
exit 0

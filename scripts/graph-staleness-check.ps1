# graph-staleness-check.ps1 — SessionStart hook (claude-base)
# Держит ДЕТЕРМИНИРОВАННЫЙ навигационный скелет графа всегда свежим (0 токенов),
# чтобы Claude мог доверять ему и ходить по базе через query, а не грепом.
#
# Архитектура (см. CLAUDE.md секция graphify + skills/graphify/references/skeleton.md):
#   • skeleton.json — детерминированный костяк (agents/skills/memory/rules/...), строится
#     БЕЗ LLM из структурных сигналов. Этот хук пересобирает его при старте сессии, если
#     он отстал от HEAD → на каждом ПК навигатор всегда свежий и достоверный.
#   • graph.json — семантическое ОБОГАЩЕНИЕ (LLM, хаб, изредка). Его устаревание — не повод
#     «не доверять»: костяк свежий. Поэтому старые предупреждения «устаревший врёт» убраны.
#
# Запускается ПОСЛЕ auto-pull.ps1 (HEAD актуален). Тихо при успехе. Никогда не ломает
# старт сессии — exit 0 везде.

$ErrorActionPreference = 'SilentlyContinue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}

$base    = Join-Path $HOME '.claude'
$skel    = Join-Path $base 'graphify-out\skeleton.json'
$builder = Join-Path $base 'skills\graphify\tools\skeleton_build.py'
$pyfile  = Join-Path $base 'graphify-out\.graphify_python'
if (-not (Test-Path $builder)) { exit 0 }   # скелет-инструмент ещё не раскатан — молчим

# HEAD (short)
Push-Location $base
$head = (git rev-parse --short HEAD 2>$null)
Pop-Location

# Свеж ли скелет? (built_at_commit == HEAD)
$fresh = $false
if ((Test-Path $skel) -and $head) {
  $raw = Get-Content $skel -Raw -Encoding UTF8
  if ($raw -match '"built_at_commit"\s*:\s*"([^"]+)"') {
    if ($Matches[1] -eq $head) { $fresh = $true }
  }
}
if ($fresh) { exit 0 }   # уже свежий — тихо

# Пересобрать костяк (детерминированно, 0 токенов, секунды)
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
  Write-Output "[graph] Навигатор базы (skeleton) пересобран и свеж — query: python skills/graphify/tools/graph_query.py ""<вопрос>"" (истина в source_file)."
}
exit 0

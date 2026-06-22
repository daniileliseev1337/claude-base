# graph-staleness-check.ps1 — SessionStart hook (claude-base)
# Предупреждает ОДНОЙ строкой, если граф знаний базы (graphify-out/graph.json)
# построен на коммите, отставшем от HEAD по СТРУКТУРНЫМ путям (agents/skills/
# memory/blocks/chains/CLAUDE.md/mcp-manifest). «Устаревший граф вреднее
# отсутствующего — он уверенно врёт» (CLAUDE.md). Тихо, если граф свеж/отсутствует.
#
# Запускается ПОСЛЕ auto-pull.ps1 (тот делает git pull → HEAD актуален).
# Не падает ни при каких условиях — exit 0 везде (хук не должен ломать старт).

$ErrorActionPreference = 'SilentlyContinue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}

$base  = Join-Path $HOME '.claude'
$graph = Join-Path $base 'graphify-out\graph.json'
if (-not (Test-Path $graph)) { exit 0 }

# built_at_commit достаём regex'ом — не парсим 1.3 МБ JSON целиком
$raw = Get-Content $graph -Raw -Encoding UTF8
if ($raw -notmatch '"built_at_commit"\s*:\s*"([^"]+)"') { exit 0 }
$built = $Matches[1]
if ([string]::IsNullOrWhiteSpace($built)) { exit 0 }

Push-Location $base
$head    = (git rev-parse --short HEAD 2>$null)
$changed = git diff --name-only "$built" HEAD -- agents skills memory blocks chains CLAUDE.md mcp-manifest.json 2>$null
$code    = $LASTEXITCODE
Pop-Location

if ($code -ne 0)  { exit 0 }   # built-коммит не в истории (rebase/gc) — не шуметь
if (-not $changed) { exit 0 }  # структурных изменений нет — граф актуален

$n = ($changed | Measure-Object).Count
$isHub = Test-Path (Join-Path $base '.developer-marker')
$action = if ($isHub) {
  "Пересобрать: /graphify ~/.claude --update (через скилл), затем закоммитить graphify-out/."
} else {
  "На свежих зонах не доверять графу — читать файл-источник; обновление прилетит от хаба."
}
Write-Output "[graph-stale] Граф базы устарел: built=$built, HEAD=$head, изменилось $n структурных файлов (agents/skills/memory/blocks/chains/CLAUDE.md/mcp-manifest). Навигатор может «уверенно врать». $action"
exit 0

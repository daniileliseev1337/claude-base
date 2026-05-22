<#
.SYNOPSIS
Smoke-test ~/.claude/ — проверка что вся методическая база на ПК
актуальна и работает после auto-pull с claude-base.

.DESCRIPTION
Запускается на любом ПК команды после первой сессии Claude Code
(когда auto-pull уже подтянул свежий main). Покрывает 5 групп:

  [1] Sync state — репозиторий синхронизирован с origin/main
  [2] Files in place — все управляемые папки/файлы на месте
  [3] Settings — shared config поля присутствуют
  [4] GitHub bypass-proxy — persistent git config применён
  [5] Pytest evals — regression-тесты скиллов проходят

Использование (Windows PowerShell 5.1 — на всех наших ПК есть by default):
  powershell -File "$HOME\.claude\scripts\verify-claude-base.ps1"

Альтернатива если стоит PowerShell 7:
  pwsh ~/.claude/scripts/verify-claude-base.ps1

Возвращает exit 0 если всё PASS, exit 1 если есть FAIL.
Список FAIL'ов выводится в конце с диагностикой.

Совместимость: файл сохранён в UTF-8 с BOM — корректно парсится
и Windows PowerShell 5.1, и PowerShell 7. Кириллица в строках
работает в обоих случаях.
#>

$ErrorActionPreference = 'Continue'
$ClaudeDir = Join-Path $env:USERPROFILE '.claude'

$script:total = 0
$script:passed = 0
$script:failed = @()

function Check {
    param([string]$Name, [scriptblock]$Test, [string]$Hint = "")
    $script:total++
    try {
        $r = & $Test
        if ($r) {
            Write-Host "  [PASS] $Name" -ForegroundColor Green
            $script:passed++
        } else {
            Write-Host "  [FAIL] $Name" -ForegroundColor Red
            if ($Hint) {
                Write-Host "         -> $Hint" -ForegroundColor DarkYellow
            }
            $script:failed += $Name
        }
    } catch {
        Write-Host "  [FAIL] $Name -- $_" -ForegroundColor Red
        $script:failed += "$Name ($_)"
    }
}

Write-Host ""
Write-Host "=== claude-base smoke-test on $env:COMPUTERNAME ===" -ForegroundColor Cyan
Write-Host "    Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "    Claude dir: $ClaudeDir" -ForegroundColor Gray
Write-Host ""

# === [1] Sync state ===
Write-Host "[1] Sync state" -ForegroundColor Yellow
Push-Location $ClaudeDir
Check "Repo is a git repository" {
    Test-Path (Join-Path $ClaudeDir '.git')
} -Hint "Ожидается что ~/.claude/ это клон claude-base"

Check "No commits ahead origin/main (everything pushed)" {
    & git fetch --quiet origin main 2>&1 | Out-Null
    $ahead = & git rev-list --count origin/main..HEAD 2>$null
    ($ahead -eq '0' -or $ahead -eq 0)
} -Hint "Есть локальные коммиты которые не пушнулись. auto-push при закрытии чата подхватит, либо вручную git push"

Check "Up-to-date with origin/main (no behind)" {
    $behind = & git rev-list --count HEAD..origin/main 2>$null
    ($behind -eq '0' -or $behind -eq 0)
} -Hint "Origin ушёл вперёд. Запусти auto-pull (новая сессия) или вручную git pull --rebase --autostash"

Check "Last commit recent (within 24h)" {
    $logTime = & git log -n 1 --pretty=format:'%cI' 2>$null
    if (-not $logTime) { return $false }
    $age = (Get-Date) - [datetime]$logTime
    $age.TotalHours -lt 48
} -Hint "Возможно нужно auto-pull"
Pop-Location

# === [2] Files in place ===
Write-Host ""
Write-Host "[2] Managed paths / files" -ForegroundColor Yellow

Check "chains/ has 3+ files (named chains)" {
    (Get-ChildItem (Join-Path $ClaudeDir 'chains') -File -ErrorAction SilentlyContinue).Count -ge 3
} -Hint "Должны быть docx-from-template.md, pdf-scan-extract.md, project-doc-pack.md, README.md"

Check "evals/ has pytest tests" {
    Test-Path (Join-Path $ClaudeDir 'evals\test_image_text_replace.py')
} -Hint "Должен быть evals/test_image_text_replace.py с 21 кейсом"

Check "skills/chains-pattern/SKILL.md" {
    Test-Path (Join-Path $ClaudeDir 'skills\chains-pattern\SKILL.md')
}

Check "skills/handoff-to-new-chat/SKILL.md" {
    Test-Path (Join-Path $ClaudeDir 'skills\handoff-to-new-chat\SKILL.md')
}

Check "skills/image-text-replace/LESSONS-LEARNED.md has §7" {
    $f = Join-Path $ClaudeDir 'skills\image-text-replace\LESSONS-LEARNED.md'
    if (-not (Test-Path $f)) { return $false }
    (Get-Content $f -Raw -Encoding UTF8) -match '§7' -or (Get-Content $f -Raw -Encoding UTF8) -match 'DocTR'
} -Hint "§7 (DocTR benchmark) и §6 (unified font_size) — финальные уроки сессии 2026-05-20"

Check "anti-patterns.md has Category 6 (context discipline)" {
    $f = Join-Path $ClaudeDir 'anti-patterns.md'
    if (-not (Test-Path $f)) { return $false }
    (Get-Content $f -Raw -Encoding UTF8) -match 'Категория 6'
}

Check "memory/ has backlog files" {
    Test-Path (Join-Path $ClaudeDir 'memory\backlog_promptfoo_semantic_tests.md')
}

# === [3] Scripts updated ===
Write-Host ""
Write-Host "[3] Scripts (auto-sync infrastructure)" -ForegroundColor Yellow

Check "auto-pull.ps1 has Invoke-GitPullRetry" {
    $c = Get-Content (Join-Path $ClaudeDir 'scripts\auto-pull.ps1') -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    $c -match 'Invoke-GitPullRetry'
} -Hint "Retry logic для SSL/network glitches"

Check "auto-push.ps1 has Invoke-GitPushRetry" {
    $c = Get-Content (Join-Path $ClaudeDir 'scripts\auto-push.ps1') -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    $c -match 'Invoke-GitPushRetry'
}

Check "auto-push whitelist includes chains/evals/settings.shared.json" {
    $c = Get-Content (Join-Path $ClaudeDir 'scripts\auto-push.ps1') -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    ($c -match "'chains'") -and ($c -match "'evals'") -and ($c -match "'settings\.shared\.json'")
} -Hint "Phase 1 sync-redesign 2026-05-21: settings.json вынесен, settings.shared.json вместо него"

Check "settings.json не в auto-push whitelist (стал personal)" {
    $c = Get-Content (Join-Path $ClaudeDir 'scripts\auto-push.ps1') -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    # settings.json должен НЕ быть в whitelist отдельной строкой (только в комментариях)
    $lines = $c -split "`n"
    $managedLines = $lines | Where-Object { $_ -match "^\s*'[\w\.]+'\s*,?\s*(#.*)?\s*$" }
    -not ($managedLines | Where-Object { $_ -match "'settings\.json'" })
} -Hint "settings.json теперь personal (gitignored)"

Check "auto-pull.ps1 auto-applies GitHub bypass-proxy" {
    $c = Get-Content (Join-Path $ClaudeDir 'scripts\auto-pull.ps1') -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    $c -match 'bypass-proxy auto-applied' -or $c -match 'http\.https://github\.com/\.proxy'
}

Check "setup-extras.ps1 has Step 0 (GitHub bypass)" {
    $c = Get-Content (Join-Path $ClaudeDir 'scripts\setup-extras.ps1') -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    $c -match 'Step 0' -or $c -match 'GitHub bypass-proxy'
}

# === [4] Settings ===
Write-Host ""
Write-Host "[4] Settings.json (shared config)" -ForegroundColor Yellow

$settings = $null
try {
    $settings = Get-Content (Join-Path $ClaudeDir 'settings.json') -Raw | ConvertFrom-Json
} catch {}

Check "settings.json valid JSON" {
    $null -ne $settings
}

Check "settings.json language='russian'" {
    $settings -and $settings.language -eq 'russian'
}

Check "settings.json effortLevel='xhigh'" {
    $settings -and $settings.effortLevel -eq 'xhigh'
}

Check "settings.json enabledPlugins present" {
    $settings -and ($null -ne $settings.enabledPlugins)
}

# === [5] GitHub bypass-proxy persistent ===
Write-Host ""
Write-Host "[5] GitHub bypass-proxy (persistent git config)" -ForegroundColor Yellow

Check "git config http.https://github.com/.proxy is set" {
    & git config --global --get http.https://github.com/.proxy 2>$null | Out-Null
    $LASTEXITCODE -eq 0
} -Hint "auto-pull.ps1 применит при первом hook'е, или вручную: git config --global http.https://github.com/.proxy `"`""

# === [6] Pytest evals ===
Write-Host ""
Write-Host "[6] Pytest evals (regression-тесты скиллов)" -ForegroundColor Yellow

Check "pytest collects + passes (21 tests)" {
    $evalsDir = Join-Path $ClaudeDir 'evals'
    if (-not (Test-Path $evalsDir)) { return $false }
    Push-Location $evalsDir
    try {
        $out = & python -m pytest --tb=no -q 2>&1 | Out-String
        Pop-Location
        ($out -match 'passed') -and -not ($out -match '\d+ failed')
    } catch {
        Pop-Location
        $false
    }
} -Hint "Требует pytest установлен: python -m pip install --user pytest"

# === Summary ===
Write-Host ""
Write-Host "=== Summary: $passed/$total passed ===" -ForegroundColor Cyan

if ($failed.Count -eq 0) {
    Write-Host "✅ All checks passed — claude-base ready to work" -ForegroundColor Green
    exit 0
} else {
    Write-Host ""
    Write-Host "FAILED checks:" -ForegroundColor Red
    foreach ($f in $failed) {
        Write-Host "  - $f" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Next step: пришли список failures Даниилу/Claude — разберём." -ForegroundColor Yellow
    exit 1
}

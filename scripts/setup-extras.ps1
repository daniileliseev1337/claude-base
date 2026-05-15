<#
.SYNOPSIS
Установка дополнительных Python-пакетов и MCP-серверов из mcp-manifest.json.

.DESCRIPTION
Читает ~/.claude/mcp-manifest.json и устанавливает всё что описано:
  - Python user-packages (pip install --user)
  - MCP-серверы (uvx или github-zip-uv) + регистрация через `claude mcp add`

Идемпотентен: повторный запуск пропускает уже установленное.

Когда запускать:
  - Один раз после первой установки claude-base (или Install.ps1 Stage 8
    вызовет автоматически).
  - При появлении уведомления в auto-sync.log "extras-diff: N pending..."
    -- это значит owner репо добавил новый MCP/пакет в manifest.

Параметры:
  -Yes        не спрашивать подтверждения
  -DryRun     показать что будет установлено, не делать
  -SkipPython пропустить установку Python 3.12 (если он уже стоит другим путём)

.NOTES
Требует: PowerShell 5.1+, активное интернет-соединение, прокси-env если за корп-прокси.

Файлы:
  ~/.claude/mcp-manifest.json -- описание что ставить
  ~/.claude/.local-state/setup-extras.applied -- marker per-machine
                                                  (имя и hash manifest'а)
#>

[CmdletBinding()]
param(
    [switch]$Yes,
    [switch]$DryRun,
    [switch]$SkipPython
)

$ErrorActionPreference = 'Stop'

# === Constants ===
$ClaudeDir   = "$env:USERPROFILE\.claude"
$Manifest    = "$ClaudeDir\mcp-manifest.json"
$LocalState  = "$ClaudeDir\.local-state"
$MarkerFile  = "$LocalState\setup-extras.applied"
$LogFile     = "$ClaudeDir\auto-sync.log"
$Py312Path   = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"

# === Helpers ===
function Write-Step { param($m) Write-Host "==> $m" -ForegroundColor Cyan }
function Write-OK   { param($m) Write-Host "  [OK]   $m" -ForegroundColor Green }
function Write-Skip { param($m) Write-Host "  [skip] $m" -ForegroundColor Gray }
function Write-Warn { param($m) Write-Host "  [WARN] $m" -ForegroundColor Yellow }
function Write-Err  { param($m) Write-Host "  [ERR]  $m" -ForegroundColor Red }
function Log        { param($m) "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] setup-extras: $m" | Add-Content -Path $LogFile -ErrorAction SilentlyContinue }

# === Pre-flight ===
if (-not (Test-Path $Manifest)) {
    Write-Err "Manifest not found: $Manifest"
    Write-Err "Run 'git pull' in ~/.claude/ to fetch manifest first."
    exit 1
}

$manifest = Get-Content $Manifest -Raw | ConvertFrom-Json

$pyPkgs    = @($manifest.python_user_packages)
$mcpSrvs   = @($manifest.mcp_servers)
$totalPy   = $pyPkgs.Count
$totalMcp  = $mcpSrvs.Count

Write-Host ""
Write-Host "=== claude-base extras setup ===" -ForegroundColor White
Write-Host "Manifest path:  $Manifest" -ForegroundColor Gray
Write-Host "Python pkgs in manifest: $totalPy" -ForegroundColor Gray
Write-Host "MCP servers in manifest: $totalMcp" -ForegroundColor Gray
Write-Host ""

if ($DryRun) { Write-Host "MODE: DryRun (no changes)" -ForegroundColor Yellow; Write-Host "" }

# Estimate disk size
$estMb = 0
foreach ($p in $pyPkgs)  { if ($p.size_mb) { $estMb += $p.size_mb } }
foreach ($s in $mcpSrvs) { if ($s.size_mb) { $estMb += $s.size_mb } }
if ($estMb -gt 0) {
    Write-Host "Disk estimate: ~$estMb MB (excluding model downloads on first use, e.g. PaddleOCR +500MB)" -ForegroundColor Gray
    Write-Host ""
}

if (-not $Yes -and -not $DryRun) {
    $resp = Read-Host "Proceed with install? (y/N)"
    if ($resp -ne 'y' -and $resp -ne 'Y') {
        Write-Warn "Cancelled by user."
        exit 0
    }
}

New-Item -ItemType Directory -Path $LocalState -Force -ErrorAction SilentlyContinue | Out-Null

# === Step 1: Python 3.12 ===
if (-not $SkipPython) {
    Write-Step "Step 1: Python 3.12 (for paddlepaddle/matplotlib stack)"
    if (Test-Path $Py312Path) {
        $v = & $Py312Path --version 2>&1
        Write-OK "Python 3.12 already installed: $v at $Py312Path"
    } else {
        if ($DryRun) {
            Write-Host "  [dry] Would install Python 3.12 via winget"
        } else {
            Write-Host "  Installing Python 3.12 (user-mode, no admin)..."
            Write-Host "  Command: winget install --id Python.Python.3.12 --scope user --silent --accept-source-agreements --accept-package-agreements"
            $wingetExit = (Start-Process -FilePath "winget" -ArgumentList @(
                "install", "--id", "Python.Python.3.12", "--scope", "user", "--silent",
                "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity"
            ) -Wait -PassThru -NoNewWindow).ExitCode
            if ($wingetExit -ne 0) {
                Write-Err "winget exit=$wingetExit. Install Python 3.12 manually from https://www.python.org/downloads/release/python-31210/"
                Log "Python install FAILED (winget exit=$wingetExit)"
                exit 1
            }
            if (-not (Test-Path $Py312Path)) {
                Write-Err "winget reported success but Python 3.12 not found at $Py312Path"
                exit 1
            }
            Write-OK "Python 3.12 installed: $(& $Py312Path --version 2>&1)"
            Log "Python 3.12 installed"
        }
    }
} else {
    Write-Skip "Step 1: Python install (--SkipPython flag)"
}

# === Step 2: Python user-packages ===
Write-Step "Step 2: Python user-packages ($totalPy total)"
$installedPy = @()
$pendingPy   = @()
if (Test-Path $Py312Path) {
    foreach ($p in $pyPkgs) {
        $name = $p.name
        # pip-name and import-name may differ (e.g. paddlepaddle -> paddle).
        # If import_name is given in manifest, use it for the spec-check.
        $importName = if ($p.import_name) { $p.import_name } else { $name }
        $check = & $Py312Path -c "import importlib.util; print('OK' if importlib.util.find_spec('$importName') else 'MISSING')" 2>&1 | Out-String
        if ($check -match 'OK') {
            $installedPy += $name
            Write-Skip "$name (import: $importName) -- already installed"
        } else {
            $pendingPy += $name
            Write-Host "  [pend] $name (import: $importName) -- will install"
        }
    }
    if ($pendingPy.Count -gt 0 -and -not $DryRun) {
        Write-Host ""
        Write-Host "  Installing pending: $($pendingPy -join ', ')"
        & $Py312Path -m pip install --user $pendingPy 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-OK "All Python packages installed"
            Log "Python packages installed: $($pendingPy -join ',')"
        } else {
            Write-Err "pip install exit=$LASTEXITCODE"
            Log "pip install FAILED (exit=$LASTEXITCODE) for: $($pendingPy -join ',')"
            exit 1
        }
    } elseif ($pendingPy.Count -gt 0) {
        Write-Host ""
        Write-Host "  [dry] Would: $Py312Path -m pip install --user $($pendingPy -join ' ')"
    } else {
        Write-OK "All $totalPy Python packages already present"
    }
} else {
    Write-Warn "Python 3.12 not available, skipping pkg installation"
}

# === Step 3: MCP servers ===
Write-Step "Step 3: MCP-серверы ($totalMcp total)"
$registeredMcp = (& claude mcp list 2>&1 | Out-String)

foreach ($srv in $mcpSrvs) {
    $name = $srv.name
    # PowerShell -match treats input as single string by default (no multiline).
    # claude mcp list outputs one server per line as "name: command - status".
    # Use substring check on per-line basis: split by newline, check each line starts with "name:".
    $alreadyRegistered = $false
    foreach ($line in ($registeredMcp -split "`r?`n")) {
        if ($line.TrimStart() -match "^${name}:") {
            $alreadyRegistered = $true
            break
        }
    }
    if ($alreadyRegistered) {
        Write-Skip "$name -- already registered in ~/.claude.json"
        continue
    }

    if ($DryRun) {
        Write-Host "  [dry] Would install + register: $name (method=$($srv.method))"
        continue
    }

    Write-Host ""
    Write-Host "  Installing $name (method=$($srv.method))..."

    if ($srv.method -eq 'uvx') {
        # Just register -- uvx will fetch package on first use
        $regArgs = @('mcp', 'add', $name) + $srv.register_args
        & claude $regArgs 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-OK "$name registered"
            Log "MCP registered: $name (uvx)"
        } else {
            Write-Err "$name registration failed (claude mcp add exit=$LASTEXITCODE)"
            Log "MCP register FAILED: $name"
        }

    } elseif ($srv.method -eq 'github-zip-uv') {
        # 1. Download ZIP
        $installDir = $srv.install_dir -replace '\$env:USERPROFILE', $env:USERPROFILE
        if (Test-Path $installDir) {
            Write-Skip "$installDir exists, skipping clone"
        } else {
            $parentDir = Split-Path $installDir -Parent
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
            $tmpZip = Join-Path $env:TEMP "$name.zip"
            Write-Host "    Downloading $($srv.source_url)..."
            Invoke-WebRequest -Uri $srv.source_url -OutFile $tmpZip -UseBasicParsing
            Expand-Archive -Path $tmpZip -DestinationPath $parentDir -Force
            $extracted = Join-Path $parentDir $srv.extracted_name
            Rename-Item -Path $extracted -NewName (Split-Path $installDir -Leaf)
            Remove-Item $tmpZip -Force
            Write-OK "$name source extracted to $installDir"
        }

        # 2. uv sync
        $venvPython = "$installDir\.venv\Scripts\python.exe"
        if (Test-Path $venvPython) {
            Write-Skip "$name venv already exists"
        } else {
            Write-Host "    Running uv sync (creates venv with deps)..."
            Push-Location $installDir
            try {
                & uv sync 2>&1 | Out-Null
                if ($LASTEXITCODE -ne 0) {
                    Write-Err "uv sync failed for $name (exit=$LASTEXITCODE)"
                    Log "MCP install FAILED: $name (uv sync)"
                    continue
                }
                Write-OK "$name venv ready"
            } finally {
                Pop-Location
            }
        }

        # 3. Register
        $regArgsRaw = $srv.register_args
        $regArgs = @('mcp', 'add', $name) + ($regArgsRaw | ForEach-Object {
            $_ -replace '\{install_dir\}', $installDir
        })
        & claude $regArgs 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-OK "$name registered"
            Log "MCP registered: $name (github-zip-uv)"
            if ($srv.post_install_note) {
                $note = $srv.post_install_note -replace '\{install_dir\}', $installDir
                Write-Warn "Post-install: $note"
            }
        } else {
            Write-Err "$name registration failed"
        }
    } else {
        Write-Warn "${name}: unknown method '$($srv.method)', skipping"
    }
}

# === Step 4: Marker ===
if (-not $DryRun) {
    $manifestHash = (Get-FileHash $Manifest -Algorithm SHA256).Hash
    @{
        applied_at = (Get-Date).ToString("o")
        manifest_hash = $manifestHash
        host = $env:COMPUTERNAME
    } | ConvertTo-Json | Set-Content -Path $MarkerFile -Encoding utf8
    Write-OK "Marker written: $MarkerFile"
    Log "setup-extras applied (manifest hash: $($manifestHash.Substring(0,8)))"
}

# === Done ===
Write-Host ""
Write-Host "=== Готово ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Дальше:" -ForegroundColor White
Write-Host "  1. Перезапустить Claude Code чтобы появились новые MCP-tools" -ForegroundColor Gray
Write-Host "  2. Проверка: claude mcp list" -ForegroundColor Gray
Write-Host "  3. Для autocad-mcp с реальным AutoCAD -- ручной APPLOAD (см. post-install note выше)" -ForegroundColor Gray
Write-Host ""

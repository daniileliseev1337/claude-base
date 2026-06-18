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

# === Pre-flight notification: HF token check ===
if (-not (Test-Path "$env:USERPROFILE\.claude\.hf-token") -and -not $env:HF_TOKEN) {
    Write-Host ""
    Write-Host "[INFO] Перед началом установки:" -ForegroundColor Cyan
    Write-Host "  Для полной функциональности (image-text-replace v3.0 SD-полировка)" -ForegroundColor Cyan
    Write-Host "  нужен HuggingFace токен. Получить можно у Даниила: Deliseev@k-7.tech" -ForegroundColor Cyan
    Write-Host "  GitHub: daniileliseev1337" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Без токена: image-text-replace будет работать в v2 режиме (без SD)" -ForegroundColor Gray
    Write-Host "  LaMa и EasyOCR — установятся в любом случае" -ForegroundColor Gray
    Write-Host ""
}

# === Constants ===
$ClaudeDir    = "$env:USERPROFILE\.claude"
$ManifestPath = "$ClaudeDir\mcp-manifest.json"
$LocalState   = "$ClaudeDir\.local-state"
$MarkerFile   = "$LocalState\setup-extras.applied"
$LogFile      = "$ClaudeDir\auto-sync.log"
$Py312Path    = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"

# === Helpers ===
function Write-Step { param($m) Write-Host "==> $m" -ForegroundColor Cyan }
function Write-OK   { param($m) Write-Host "  [OK]   $m" -ForegroundColor Green }
function Write-Skip { param($m) Write-Host "  [skip] $m" -ForegroundColor Gray }
function Write-Warn { param($m) Write-Host "  [WARN] $m" -ForegroundColor Yellow }
function Write-Err  { param($m) Write-Host "  [ERR]  $m" -ForegroundColor Red }
function Log        { param($m) "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] setup-extras: $m" | Add-Content -Path $LogFile -ErrorAction SilentlyContinue }

# === Step 0: GitHub bypass-proxy (persistent git config) ===
#
# Корп-прокси блокирует CONNECT к github.com на всех наших ПК.
# Empirical fact (2026-05-20): git push/pull/fetch падают с
# "Proxy CONNECT aborted". Решение — persistent bypass для github-домена.
# См. CLAUDE.md раздел "GitHub — обязательный bypass proxy".
#
# Идемпотентно: если bypass уже установлен — skip.
Write-Step "Step 0: GitHub bypass-proxy (persistent git config)"
# Проверка через $LASTEXITCODE — однозначно работает в PS 5.1 и PS Core 7.
# Старая проверка `$x -eq ""` ломалась в PS 5.1, потому что `git config --get`
# несуществующего ключа возвращает пустую строку (а не $null), и условие
# ошибочно срабатывает «already configured» на свежем ПК.
git config --global --get http.https://github.com/.proxy 2>$null | Out-Null
$httpExit = $LASTEXITCODE
git config --global --get https.https://github.com/.proxy 2>$null | Out-Null
$httpsExit = $LASTEXITCODE
if ($httpExit -eq 0 -and $httpsExit -eq 0) {
    Write-OK "GitHub bypass-proxy already configured"
} else {
    git config --global http.https://github.com/.proxy ""
    git config --global https.https://github.com/.proxy ""
    Write-OK "Applied: git config --global http.https://github.com/.proxy `"`""
    Log "Step 0: applied GitHub bypass-proxy persistent config"
}

# === Step 0.5: ccusage — мониторинг токенов + statusline ===
#
# settings.shared.json содержит statusLine "ccusage statusline" (живой расход
# токенов в строке статуса CLI). Без установленного ccusage строка просто
# не отрисуется — ставим. npm (если есть Node) -> bun (user-scope, без админа).
Write-Step "Step 0.5: ccusage (мониторинг токенов + statusline)"
try {
    if (Get-Command ccusage -ErrorAction SilentlyContinue) {
        Write-OK "ccusage already installed"
    } elseif ($DryRun) {
        Write-Host "  [dry] ccusage будет установлен (npm, иначе bun user-scope)" -ForegroundColor Yellow
    } else {
        $npmCmd = Get-Command npm -ErrorAction SilentlyContinue
        $bunExe = $null
        $bunCmd = Get-Command bun -ErrorAction SilentlyContinue
        if ($bunCmd) { $bunExe = $bunCmd.Source }
        elseif (Test-Path "$env:USERPROFILE\.bun\bin\bun.exe") { $bunExe = "$env:USERPROFILE\.bun\bin\bun.exe" }

        if ($npmCmd) {
            npm install -g ccusage 2>$null | Out-Null
        } else {
            if (-not $bunExe) {
                Write-Host "  Node/npm нет — ставлю bun (user-scope, без админа)..." -ForegroundColor Gray
                Invoke-RestMethod 'https://bun.sh/install.ps1' | Invoke-Expression
                if (Test-Path "$env:USERPROFILE\.bun\bin\bun.exe") { $bunExe = "$env:USERPROFILE\.bun\bin\bun.exe" }
            }
            if ($bunExe) { & $bunExe add -g ccusage 2>$null | Out-Null }
        }

        if (Get-Command ccusage -ErrorAction SilentlyContinue) {
            Write-OK "ccusage installed — statusline появится после перезапуска Claude Code"
            Log "Step 0.5: ccusage installed"
        } else {
            Write-Warn "ccusage не встал в PATH текущей сессии — после перезапуска терминала проверь: ccusage --version"
            Log "Step 0.5: ccusage install attempted, not in PATH yet"
        }
    }
} catch {
    Write-Warn "ccusage setup failed (не критично, statusline просто не появится): $($_.Exception.Message)"
    Log "Step 0.5: FAILED: $($_.Exception.Message)"
}

# === Pre-flight ===
if (-not (Test-Path $ManifestPath)) {
    Write-Err "Manifest not found: $ManifestPath"
    Write-Err "Run 'git pull' in ~/.claude/ to fetch manifest first."
    exit 1
}

$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json

$pyPkgs    = @($manifest.python_user_packages)
$mcpSrvs   = @($manifest.mcp_servers)
$totalPy   = $pyPkgs.Count
$totalMcp  = $mcpSrvs.Count

Write-Host ""
Write-Host "=== claude-base extras setup ===" -ForegroundColor White
Write-Host "Manifest path:  $ManifestPath" -ForegroundColor Gray
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
        $v = & $Py312Path --version 2>$null
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
            Write-OK "Python 3.12 installed: $(& $Py312Path --version 2>$null)"
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
        # 2>$null drops stderr to avoid PS 5.1 NativeCommandError wrapping
        # (memory/2026-05-09_hooks-debugging.md Урок 10).
        $check = & $Py312Path -c "import importlib.util; print('OK' if importlib.util.find_spec('$importName') else 'MISSING')" 2>$null | Out-String
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
        # IMPORTANT: NO 2>&1. pip writes lots of stderr (progress, warnings).
        # Under $ErrorActionPreference='Stop' (set at top), 2>&1 wraps each
        # stderr line in NativeCommandError and aborts the script mid-install.
        # Let pip output flow to console natively; rely on $LASTEXITCODE for
        # success/failure decision. (memory/2026-05-09_hooks-debugging.md
        # Урок 10 -- мы повторили эту ошибку при первом написании setup-extras.)
        & $Py312Path -m pip install --user $pendingPy
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
$registeredMcp = (& claude mcp list 2>$null | Out-String)

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

    if ($srv.method -eq 'uvx' -or $srv.method -eq 'npx') {
        # Just register -- uvx/npx will fetch package on first use
        $regArgs = @('mcp', 'add', $name) + $srv.register_args
        & claude $regArgs 2>$null | Out-Null
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

        # 1b. Local patches (idempotent) for servers that need a post-extract fix.
        #     Revit-Connector: upstream main.py uses localhost + proxy-aware httpx,
        #     which hangs on corp-proxy / IPv6 machines. See memory/reference_revit_mcp.md.
        if ($name -eq 'Revit-Connector') {
            $patcher = Join-Path $PSScriptRoot 'patch-revit-mcp.ps1'
            if (Test-Path $patcher) {
                & $patcher -InstallDir $installDir
                Log "Revit-Connector main.py patched (IPv4 + trust_env=False)"
            } else {
                Write-Warn "patch-revit-mcp.ps1 not found next to setup-extras.ps1"
            }
        }

        # 2. uv sync
        $venvPython = "$installDir\.venv\Scripts\python.exe"
        if (Test-Path $venvPython) {
            Write-Skip "$name venv already exists"
        } else {
            Write-Host "    Running uv sync (creates venv with deps)..."
            Push-Location $installDir
            try {
                # NO 2>&1 -- uv sync prints lots of progress; let it flow to console.
                & uv sync
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
        & claude $regArgs 2>$null | Out-Null
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

# === Step 4: Model downloads (LaMa, EasyOCR, SD) ===
#
# HF token обязателен ТОЛЬКО для SD download (LaMa и EasyOCR грузятся без auth).
# Storage: ~/.claude/.hf-token (gitignored, per-machine).
# Содержимое: одна строка "hf_..." без кавычек, без пробелов.
# Получить: https://huggingface.co/settings/tokens (read scope достаточен).
# Auto-classifier блокирует committing token в public repo, поэтому
# каждый ПК должен иметь свой .hf-token локально.
#
$HFTokenFile = "$ClaudeDir\.hf-token"
$HFToken = $null
if (Test-Path $HFTokenFile) {
    $HFToken = (Get-Content $HFTokenFile -Raw).Trim()
    Write-Host "  HF token loaded from .hf-token"
} elseif ($env:HF_TOKEN) {
    $HFToken = $env:HF_TOKEN
    Write-Host "  HF token from environment variable"
} else {
    # Prominent message — new user needs to contact Daniil for token
    Write-Host ""
    Write-Host "+=========================================================================+" -ForegroundColor Yellow
    Write-Host "|  ВНИМАНИЕ: Stable Diffusion (SD) не будет установлен                    |" -ForegroundColor Yellow
    Write-Host "+=========================================================================+" -ForegroundColor Yellow
    Write-Host "|                                                                         |" -ForegroundColor Yellow
    Write-Host "|  SD требуется для финальной 'scan-полировки' в image-text-replace v3.0  |" -ForegroundColor Yellow
    Write-Host "|  (полностью неотличимая от скана вставка текста).                       |" -ForegroundColor Yellow
    Write-Host "|                                                                         |" -ForegroundColor Yellow
    Write-Host "|  Что работает БЕЗ SD: image-text-replace v2.3 (Times Bold + smart cap)  |" -ForegroundColor Yellow
    Write-Host "|  Что НЕ работает без SD: --sd-refine финальный AI-pass                  |" -ForegroundColor Yellow
    Write-Host "|                                                                         |" -ForegroundColor Yellow
    Write-Host "|  ЧТОБЫ ВКЛЮЧИТЬ SD:                                                     |" -ForegroundColor Yellow
    Write-Host "|                                                                         |" -ForegroundColor Yellow
    Write-Host "|  1. Напиши Даниилу: Deliseev@k-7.tech                               |" -ForegroundColor Yellow
    Write-Host "|     (GitHub: daniileliseev1337)                                         |" -ForegroundColor Yellow
    Write-Host "|     Запроси HuggingFace токен для распространения SD моделей.           |" -ForegroundColor Yellow
    Write-Host "|                                                                         |" -ForegroundColor Yellow
    Write-Host "|  2. Получив строку 'hf_...', выполни:                                   |" -ForegroundColor Yellow
    Write-Host "|     'hf_xxx...' | Out-File -Encoding ascii `"$HFTokenFile`" -NoNewline   |" -ForegroundColor Yellow
    Write-Host "|                                                                         |" -ForegroundColor Yellow
    Write-Host "|  3. Запусти setup-extras повторно — SD скачается автоматически.        |" -ForegroundColor Yellow
    Write-Host "|     (5.4 GB, 10-60 мин на корп-сети)                                    |" -ForegroundColor Yellow
    Write-Host "|                                                                         |" -ForegroundColor Yellow
    Write-Host "|  LaMa и EasyOCR — устанавливаются БЕЗ token, продолжаю...               |" -ForegroundColor Yellow
    Write-Host "|                                                                         |" -ForegroundColor Yellow
    Write-Host "+=========================================================================+" -ForegroundColor Yellow
    Write-Host ""
    Log "SD skipped — no .hf-token, user notified to contact Daniil (Deliseev@k-7.tech)"
}

$SDCacheDir = 'C:\sd-cache'  # ASCII-safe, обязательно для HF symlinks
$LamaCacheDir = 'C:\iopaint-cache\torch\hub\checkpoints'
$LamaModelUrl = 'https://github.com/Sanster/models/releases/download/add_big_lama/big-lama.pt'
$LamaModelPath = "$LamaCacheDir\big-lama.pt"

Write-Step "Step 4: Model downloads for image-text-replace v3.0"

# 4a. LaMa model (~196 MB from GitHub Releases, no auth needed)
if (Test-Path $LamaModelPath) {
    $size = (Get-Item $LamaModelPath).Length / 1MB
    Write-Skip "LaMa model already present ($('{0:N0}' -f $size) MB)"
} elseif ($DryRun) {
    Write-Host "  [dry] Would download LaMa model from $LamaModelUrl"
} else {
    Write-Host "  Downloading LaMa model (~196 MB from GitHub, ~1-3 min)..."
    New-Item -ItemType Directory -Path $LamaCacheDir -Force | Out-Null
    try {
        # curl with retries — Invoke-WebRequest часто рвётся на больших файлах
        & curl.exe -L --retry 10 --retry-delay 5 --retry-all-errors `
            -o $LamaModelPath $LamaModelUrl
        if ($LASTEXITCODE -eq 0 -and (Test-Path $LamaModelPath)) {
            $size = (Get-Item $LamaModelPath).Length / 1MB
            Write-OK "LaMa model downloaded ($('{0:N0}' -f $size) MB)"
            Log "LaMa model downloaded to $LamaModelPath"
        } else {
            Write-Warn "LaMa download exit=$LASTEXITCODE. image-text-replace LaMa mode will retry на первом запуске."
        }
    } catch {
        Write-Warn "LaMa download exception: $_"
    }
}

# 4b. EasyOCR Russian model warmup (~100 MB from GitHub Releases)
$easyOcrUserDir = "$env:USERPROFILE\.EasyOCR\model"
if ((Test-Path "$easyOcrUserDir\cyrillic_g2.pth") -or
    (Test-Path "$easyOcrUserDir\craft_mlt_25k.pth")) {
    Write-Skip "EasyOCR Russian models already cached"
} elseif ($DryRun) {
    Write-Host "  [dry] Would warmup EasyOCR Reader(['ru','en'])"
} else {
    if (Test-Path $Py312Path) {
        Write-Host "  Warming up EasyOCR (downloads ~100 MB Russian + detection models)..."
        & $Py312Path -c "import easyocr; easyocr.Reader(['ru','en'], gpu=False, verbose=False); print('EasyOCR ready')"
        if ($LASTEXITCODE -eq 0) {
            Write-OK "EasyOCR models ready"
            Log "EasyOCR Russian models cached"
        } else {
            Write-Warn "EasyOCR warmup exit=$LASTEXITCODE. Will retry on first skill use."
        }
    } else {
        Write-Warn "Python 3.12 not available — EasyOCR warmup skipped"
    }
}

# 4c. SD inpaint model (~3.4 GB UNet + ~2 GB other from HF, requires token)
$sdSnapshotDir = "$SDCacheDir\models--runwayml--stable-diffusion-inpainting"
$sdUnetFile = "$sdSnapshotDir\snapshots\*\unet\diffusion_pytorch_model.bin"
if (Test-Path $sdUnetFile) {
    Write-Skip "SD-1.5 inpaint model already cached at $SDCacheDir"
} elseif ($DryRun) {
    Write-Host "  [dry] Would download SD model from HuggingFace (~5.4 GB total, requires HF auth)"
} else {
    if (-not (Test-Path $Py312Path)) {
        Write-Warn "Python 3.12 not available — SD download skipped"
    } elseif (-not $HFToken) {
        Write-Warn "No HF token — SD download skipped. Pipeline без --sd-refine продолжит работать."
        Write-Host "    Чтобы добавить SD: получи token на https://huggingface.co/settings/tokens"
        Write-Host "    и положи в $HFTokenFile (одна строка hf_...)"
    } else {
        Write-Host "  Downloading SD-1.5 inpaint model (~5.4 GB total, 10-60 min on corp net)..."
        New-Item -ItemType Directory -Path $SDCacheDir -Force | Out-Null
        $env:HF_TOKEN = $HFToken
        $env:HF_HOME = $SDCacheDir
        $sdDownloadCmd = @"
import os
os.environ['HF_HOME'] = r'$SDCacheDir'
from huggingface_hub import snapshot_download, login
login(token=os.environ['HF_TOKEN'])
for attempt in range(10):
    try:
        path = snapshot_download(
            repo_id='runwayml/stable-diffusion-inpainting',
            cache_dir=r'$SDCacheDir',
            allow_patterns=['*.json', '*.txt', '*.safetensors', '*.bin', '*.model'],
            ignore_patterns=['*.ckpt', '*.fp16.*'],
            max_workers=2,
        )
        print(f'OK: {path}')
        break
    except Exception as e:
        print(f'retry on: {type(e).__name__}')
"@
        & $Py312Path -c $sdDownloadCmd
        if ($LASTEXITCODE -eq 0 -and (Test-Path $sdSnapshotDir)) {
            Write-OK "SD-1.5 inpaint model downloaded to $SDCacheDir"
            Log "SD model downloaded"
        } else {
            Write-Warn "SD download exit=$LASTEXITCODE. Possible network issue или auth fail. Pipeline без --sd-refine продолжит работать."
        }
    }
}

# === Step 5: Marker ===
if (-not $DryRun) {
    $manifestHash = (Get-FileHash $ManifestPath -Algorithm SHA256).Hash
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

# Финальный reminder про SD если token отсутствует
if (-not (Test-Path $HFTokenFile) -and -not $env:HF_TOKEN) {
    Write-Host "Если нужна полная функциональность image-text-replace v3.0 (SD scan-полировка):" -ForegroundColor Magenta
    Write-Host "  Напиши Даниилу (Deliseev@k-7.tech) — он даст HuggingFace token" -ForegroundColor Magenta
    Write-Host "  → положи в $HFTokenFile → запусти setup-extras снова" -ForegroundColor Magenta
    Write-Host ""
}

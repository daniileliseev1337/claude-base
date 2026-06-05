<#
.SYNOPSIS
    K7 acad-recreation installer (idempotent). Усиливает autocad-mcp на этом ПК.
.DESCRIPTION
    1) Копирует LISP-toolkit в ASCII-путь (C:\ProgramData\K7-acad) — путь профиля
       может содержать кириллицу, LISP (load) её не любит.
    2) Применяет cp1251-патч к file_ipc.py установленного сервера (если ещё не применён) + бэкап.
    3) Печатает строку автозагрузки для acad.lsp (правку acad.lsp оставляем пользователю —
       не трогаем чужой autoload вслепую).
    Запускать после каждой переустановки сервера через setup-extras (патч затирается upstream zip).
    Comments intentionally ASCII to avoid PS 5.1 cp1251/BOM issues.
#>
$ErrorActionPreference = 'Stop'

# --- 1. toolkit -> ASCII dir ---
$asciiDir = 'C:\ProgramData\K7-acad'
New-Item -ItemType Directory -Force $asciiDir | Out-Null
$toolkitSrc = Join-Path $PSScriptRoot 'acad_lisp_toolkit.lsp'
$toolkitDst = Join-Path $asciiDir 'acad_lisp_toolkit.lsp'
Copy-Item $toolkitSrc $toolkitDst -Force
Write-Host "[1/3] toolkit -> $toolkitDst"

# --- 2. cp1251 patch to server (idempotent) ---
$fip = Join-Path $env:USERPROFILE '.claude\mcp-servers\autocad-mcp\src\autocad_mcp\backends\file_ipc.py'
if (Test-Path $fip) {
    $content = [IO.File]::ReadAllText($fip)
    if ($content -match 'encoding="cp1251"') {
        Write-Host "[2/3] cp1251 already present - skip"
    } else {
        Copy-Item $fip "$fip.bak" -Force
        $old = @'
                        try:
                            text = result_file.read_text(encoding="utf-8")
                        except UnicodeDecodeError:
                            text = result_file.read_text(encoding="cp1252")
'@
        $new = @'
                        try:
                            text = result_file.read_text(encoding="utf-8")
                        except UnicodeDecodeError:
                            try:
                                text = result_file.read_text(encoding="cp1251")
                            except UnicodeDecodeError:
                                text = result_file.read_text(encoding="cp1252")
'@
        if ($content.Contains($old.Replace("`r`n","`n")) -or $content.Contains($old)) {
            $content = $content.Replace($old, $new).Replace($old.Replace("`r`n","`n"), $new.Replace("`r`n","`n"))
            [IO.File]::WriteAllText($fip, $content, (New-Object Text.UTF8Encoding $false))  # no BOM
            Write-Host "[2/3] cp1251 patch applied (RESTART Claude Code to activate). Backup: $fip.bak"
        } else {
            Write-Host "[2/3] WARN: anchor block not found (server version changed?). Patch manually via file_ipc_cp1251.patch"
        }
    }
} else {
    Write-Host "[2/3] server not found at $fip - skip (install autocad-mcp first)"
}

# --- 3. autoload line for acad.lsp ---
$loadLine = '(load "C:/ProgramData/K7-acad/acad_lisp_toolkit.lsp")'
Write-Host "[3/3] Add toolkit autoload to AutoCAD:"
Write-Host "      - quick (this session): APPLOAD -> $toolkitDst"
Write-Host "      - permanent: add this line to your acad.lsp (AutoCAD Support path):"
Write-Host "        $loadLine"
Write-Host ""
Write-Host "DONE. After server patch -> restart Claude Code. Verify in AutoCAD: (type LM:getdynprops) => SUBR"

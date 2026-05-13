# Write XLSX file from output_table.json using ZipArchive + minimal OOXML
# Usage: powershell -ExecutionPolicy Bypass -File write_xlsx.ps1

$ErrorActionPreference = "Stop"

$jsonPath = "C:\Users\Deliseev\.claude\projects\C--Users-Deliseev\2bd085c4-98fd-4f2f-8b40-46162fed05ef\output_table.json"
$outPath = "C:\Users\Deliseev\Desktop\Было стало П и РД\СКС ЛВС было-стало 2026-05-13.xlsx"
$sheetName = "ПДЦ"

# Load data
Write-Host "Loading JSON..."
$rows = Get-Content $jsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
$rowCount = $rows.Count
$colCount = 28
Write-Host "Rows: $rowCount, Cols: $colCount"

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

# Helpers
function Esc-Xml($s) {
    if ($null -eq $s) { return "" }
    $str = [string]$s
    $str = $str -replace '&', '&amp;'
    $str = $str -replace '<', '&lt;'
    $str = $str -replace '>', '&gt;'
    $str = $str -replace '"', '&quot;'
    $str = $str -replace "'", '&apos;'
    # Strip control chars except tab/newline
    $sb = New-Object System.Text.StringBuilder
    foreach ($ch in $str.ToCharArray()) {
        $code = [int]$ch
        if ($code -lt 32 -and $code -ne 9 -and $code -ne 10 -and $code -ne 13) { continue }
        [void]$sb.Append($ch)
    }
    return $sb.ToString()
}

function Col-Letter([int]$colIdx) {
    # 1-based: 1=A, 27=AA, 28=AB
    $n = [int]$colIdx
    $s = ""
    while ($n -gt 0) {
        $mod = [int](($n - 1) % 26)
        $s = [char](65 + $mod) + $s
        $n = [int][Math]::Floor(($n - 1) / 26)
    }
    return $s
}

# Pre-build column letters
$colLetters = @()
for ($c = 1; $c -le $colCount; $c++) {
    $colLetters += (Col-Letter $c)
}

# Determine cell style index
# Style indexes:
#  0 = default
#  1 = bold (preamble labels)
#  2 = bold+center+gray-fill+border (main header)
#  3 = bold+yellow-fill+border (group row)
#  4 = bold+red-fill+border (ИСКЛЮЧЕНА pomet ka)
#  5 = bold+green-fill+border (НОВАЯ pometka)
#  6 = number "#,##0.00" + border
#  7 = text + border + wrap (data)
#  8 = number int + border
function Get-StyleIdx($rowIdx0, $colIdx1, $value, $cellText) {
    # rowIdx0 — 0-based
    $excelRow = $rowIdx0 + 1
    # Preamble rows 1-11 (excelRow 1-11)
    if ($excelRow -le 11) {
        if ($null -ne $value -and "$value".Trim() -ne "") { return 1 } # bold
        return 0
    }
    # Header row 12: cols A-N and O-AB
    if ($excelRow -eq 12 -or $excelRow -eq 13) { return 2 } # bold-gray
    # Group rows: rows where columns 4 (D) or 18 (R) have text, but column 1/15 is empty (no № value)
    # Determine for entire row, not per cell
    return -1 # let caller decide
}

# Pre-compute row types
$rowTypes = @()
for ($i = 0; $i -lt $rowCount; $i++) {
    $excelRow = $i + 1
    $row = $rows[$i]
    if ($excelRow -le 11) { $rowTypes += "preamble"; continue }
    if ($excelRow -eq 12 -or $excelRow -eq 13) { $rowTypes += "header"; continue }
    # Check group: D ($row[3]) or R ($row[17]) not empty AND A/O empty
    $aEmpty = ($null -eq $row[0]) -or ("$($row[0])".Trim() -eq "")
    $oEmpty = ($null -eq $row[14]) -or ("$($row[14])".Trim() -eq "")
    $dHas = ($null -ne $row[3]) -and ("$($row[3])".Trim() -ne "")
    $rHas = ($null -ne $row[17]) -and ("$($row[17])".Trim() -ne "")
    if ($aEmpty -and $oEmpty -and ($dHas -or $rHas)) { $rowTypes += "group"; continue }
    $rowTypes += "data"
}

# Build sheet XML
Write-Host "Building sheet XML..."
$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
[void]$sb.AppendLine('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">')

# dimension comes first
[void]$sb.AppendLine("<dimension ref=`"A1:AB$rowCount`"/>")

# sheetViews must come BEFORE cols/sheetData per OOXML schema
[void]$sb.AppendLine('<sheetViews><sheetView workbookViewId="0"><pane ySplit="13" topLeftCell="A14" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>')

# Column widths
[void]$sb.AppendLine('<cols>')
[void]$sb.AppendLine('<col min="1" max="1" width="5"/>')      # A №
[void]$sb.AppendLine('<col min="2" max="2" width="18"/>')     # B Производитель
[void]$sb.AppendLine('<col min="3" max="3" width="22"/>')     # C Модель
[void]$sb.AppendLine('<col min="4" max="4" width="45"/>')     # D Наименование
[void]$sb.AppendLine('<col min="5" max="5" width="8"/>')      # E Ед.изм
[void]$sb.AppendLine('<col min="6" max="6" width="9"/>')      # F Кол-во
[void]$sb.AppendLine('<col min="7" max="12" width="13"/>')    # G..L Цена/Стоимость BYLO
[void]$sb.AppendLine('<col min="13" max="14" width="13"/>')   # M-N стоимость ИД
[void]$sb.AppendLine('<col min="15" max="15" width="5"/>')    # O №
[void]$sb.AppendLine('<col min="16" max="16" width="18"/>')   # P Производитель
[void]$sb.AppendLine('<col min="17" max="17" width="22"/>')   # Q Модель
[void]$sb.AppendLine('<col min="18" max="18" width="45"/>')   # R Наименование
[void]$sb.AppendLine('<col min="19" max="19" width="8"/>')    # S Ед.изм
[void]$sb.AppendLine('<col min="20" max="20" width="9"/>')    # T Кол-во
[void]$sb.AppendLine('<col min="21" max="26" width="13"/>')   # U..Z Цена/Стоимость STAL
[void]$sb.AppendLine('<col min="27" max="28" width="13"/>')   # AA-AB стоимость ИД
[void]$sb.AppendLine('</cols>')

[void]$sb.AppendLine('<sheetData>')

for ($r = 0; $r -lt $rowCount; $r++) {
    $excelRow = $r + 1
    $row = $rows[$r]
    $rowType = $rowTypes[$r]

    # Skip entirely empty rows (no <row> tag for them - that's invalid OOXML)
    $hasAny = $false
    for ($c = 0; $c -lt $colCount; $c++) {
        $v = $row[$c]
        if ($null -ne $v -and "$v" -ne "") { $hasAny = $true; break }
    }
    if (-not $hasAny) { continue }

    # row height for headers
    $rowAttr = ""
    if ($rowType -eq "header") { $rowAttr = ' ht="35" customHeight="1"' }
    elseif ($rowType -eq "group") { $rowAttr = ' ht="18"' }

    [void]$sb.Append("<row r=`"$excelRow`"$rowAttr>")
    for ($c = 1; $c -le $colCount; $c++) {
        $val = $row[$c-1]
        if ($null -eq $val -or "$val" -eq "") { continue }
        $cellRef = $colLetters[$c-1] + $excelRow

        # Determine style
        $styleIdx = 0
        $isExcluded = ($c -eq 14 -and "$val".Trim() -eq "ИСКЛЮЧЕНА")
        $isNew = ($c -eq 28 -and "$val".Trim() -eq "НОВАЯ")

        if ($rowType -eq "preamble") {
            $styleIdx = 1  # bold
        }
        elseif ($rowType -eq "header") {
            $styleIdx = 2  # bold gray
        }
        elseif ($rowType -eq "group") {
            $styleIdx = 3  # bold yellow
        }
        elseif ($isExcluded) {
            $styleIdx = 4  # bold red
        }
        elseif ($isNew) {
            $styleIdx = 5  # bold green
        }
        elseif ($rowType -eq "data") {
            # Number columns G(7), J(10), U(21), X(24) — price/cost
            if ($c -eq 7 -or $c -eq 10 -or $c -eq 21 -or $c -eq 24) { $styleIdx = 6 }
            # Qty columns F(6), T(20) — integer
            elseif ($c -eq 6 -or $c -eq 20) { $styleIdx = 8 }
            else { $styleIdx = 7 }
        }

        # Determine type — number or string
        $isNumber = $false
        $numericValue = $null
        if ($val -is [double] -or $val -is [int] -or $val -is [decimal] -or $val -is [long] -or $val -is [float]) {
            $isNumber = $true
            $numericValue = [double]$val
        }
        elseif ($val -is [string]) {
            $trimmed = "$val".Trim()
            # Don't convert strings that look like position numbers in data rows ONLY for № cols — they should still be numbers OK
            # Try parse as number (with comma or dot decimal)
            $tryParse = $trimmed -replace ' ', '' -replace ',', '.'
            $parsed = 0.0
            if ([double]::TryParse($tryParse, [Globalization.NumberStyles]::Any, [Globalization.CultureInfo]::InvariantCulture, [ref]$parsed)) {
                # Only treat as number if the column is numeric-by-style (price/cost/qty/№)
                if ($c -in @(1, 6, 7, 10, 15, 20, 21, 24)) {
                    $isNumber = $true
                    $numericValue = $parsed
                }
            }
        }

        if ($isNumber) {
            [void]$sb.Append("<c r=`"$cellRef`" s=`"$styleIdx`"><v>$($numericValue.ToString([Globalization.CultureInfo]::InvariantCulture))</v></c>")
        } else {
            $escaped = Esc-Xml $val
            [void]$sb.Append("<c r=`"$cellRef`" s=`"$styleIdx`" t=`"inlineStr`"><is><t xml:space=`"preserve`">$escaped</t></is></c>")
        }
    }
    [void]$sb.AppendLine("</row>")

    if ($r % 500 -eq 0) { Write-Host "  row $r..." }
}

[void]$sb.AppendLine('</sheetData>')

# Auto-filter (must come after sheetData per OOXML)
[void]$sb.AppendLine('<autoFilter ref="A12:AB12"/>')

[void]$sb.AppendLine('</worksheet>')

$sheetXml = $sb.ToString()
Write-Host "Sheet XML size: $($sheetXml.Length) chars"

# Build styles.xml
$stylesXml = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<numFmts count="2">
  <numFmt numFmtId="164" formatCode="#,##0.00"/>
  <numFmt numFmtId="165" formatCode="0"/>
</numFmts>
<fonts count="3">
  <font><sz val="11"/><name val="Calibri"/></font>
  <font><b/><sz val="11"/><name val="Calibri"/></font>
  <font><sz val="9"/><name val="Calibri"/></font>
</fonts>
<fills count="6">
  <fill><patternFill patternType="none"/></fill>
  <fill><patternFill patternType="gray125"/></fill>
  <fill><patternFill patternType="solid"><fgColor rgb="FFD9D9D9"/><bgColor indexed="64"/></patternFill></fill>
  <fill><patternFill patternType="solid"><fgColor rgb="FFFFEB9C"/><bgColor indexed="64"/></patternFill></fill>
  <fill><patternFill patternType="solid"><fgColor rgb="FFFFC7CE"/><bgColor indexed="64"/></patternFill></fill>
  <fill><patternFill patternType="solid"><fgColor rgb="FFC6EFCE"/><bgColor indexed="64"/></patternFill></fill>
</fills>
<borders count="2">
  <border><left/><right/><top/><bottom/><diagonal/></border>
  <border><left style="thin"><color indexed="64"/></left><right style="thin"><color indexed="64"/></right><top style="thin"><color indexed="64"/></top><bottom style="thin"><color indexed="64"/></bottom><diagonal/></border>
</borders>
<cellStyleXfs count="1">
  <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
</cellStyleXfs>
<cellXfs count="9">
  <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
  <xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"><alignment wrapText="1"/></xf>
  <xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
  <xf numFmtId="0" fontId="1" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
  <xf numFmtId="0" fontId="1" fillId="4" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
  <xf numFmtId="0" fontId="1" fillId="5" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
  <xf numFmtId="164" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1" applyAlignment="1"><alignment vertical="center"/></xf>
  <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
  <xf numFmtId="165" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
</cellXfs>
<cellStyles count="1">
  <cellStyle name="Normal" xfId="0" builtinId="0"/>
</cellStyles>
<dxfs count="0"/>
<tableStyles count="0" defaultTableStyle="TableStyleMedium2" defaultPivotStyle="PivotStyleLight16"/>
</styleSheet>
'@

$workbookXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>
<sheet name="$sheetName" sheetId="1" r:id="rId1"/>
</sheets>
</workbook>
"@

$workbookRels = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
'@

$rootRels = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
'@

$contentTypes = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>
'@

# Write to ZIP
Write-Host "Writing XLSX to $outPath"
if (Test-Path $outPath) { Remove-Item $outPath -Force }

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

$fs = [System.IO.File]::Open($outPath, [System.IO.FileMode]::Create)
try {
    $zip = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Create)
    try {
        function Add-ZipEntry($zip, $name, $content) {
            $entry = $zip.CreateEntry($name, [System.IO.Compression.CompressionLevel]::Optimal)
            $stream = $entry.Open()
            try {
                $bytes = $utf8NoBom.GetBytes($content)
                $stream.Write($bytes, 0, $bytes.Length)
            }
            finally {
                $stream.Close()
            }
        }
        Add-ZipEntry $zip "[Content_Types].xml" $contentTypes
        Add-ZipEntry $zip "_rels/.rels" $rootRels
        Add-ZipEntry $zip "xl/workbook.xml" $workbookXml
        Add-ZipEntry $zip "xl/_rels/workbook.xml.rels" $workbookRels
        Add-ZipEntry $zip "xl/styles.xml" $stylesXml
        Add-ZipEntry $zip "xl/worksheets/sheet1.xml" $sheetXml
    }
    finally {
        $zip.Dispose()
    }
}
finally {
    $fs.Dispose()
}

$fi = Get-Item $outPath
Write-Host "DONE. File size: $($fi.Length) bytes"

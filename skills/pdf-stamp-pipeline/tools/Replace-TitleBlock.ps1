<#
.SYNOPSIS
    Массовая замена основной надписи (штампа) в PDF: pikepdf collapse -> pdfcpu overlay -> PyMuPDF clean.

.DESCRIPTION
    REFERENCE-РЕАЛИЗАЦИЯ (реконструкция из feedback 2026-05-25_pdf-stamp-pipeline).
    Оригинальный рабочий прототип — на машине автора (R-090226727A). Перед боевым
    использованием проверить пути и pdfcpu. Метод и параметры — см. SKILL.md.

    Требует: pdfcpu в ~/.claude/bin/pdfcpu/, Python с pikepdf + PyMuPDF (fitz).

.PARAMETER InputPdf   Исходный том/лист PDF.
.PARAMETER StampPdf   PDF нового штампа (full-page, прозрачный фон).
.PARAMETER OutputPdf  Результат.
.PARAMETER Pages      Опц. диапазон "5-50" (пропустить титул/оглавление).

.EXAMPLE
    .\Replace-TitleBlock.ps1 -InputPdf "Том.pdf" -StampPdf "stamp.pdf" -OutputPdf "out.pdf" -Pages "5-50"
#>
param(
    [Parameter(Mandatory)][string]$InputPdf,
    [Parameter(Mandatory)][string]$StampPdf,
    [Parameter(Mandatory)][string]$OutputPdf,
    [string]$Pages = ""
)

$ErrorActionPreference = 'Stop'
$pdfcpu = "$HOME\.claude\bin\pdfcpu\pdfcpu.exe"
if (-not (Test-Path $pdfcpu)) { throw "pdfcpu не найден: $pdfcpu — установить (см. SKILL.md)" }

$tmpClean   = [System.IO.Path]::GetTempFileName() + ".pdf"
$tmpStamped = [System.IO.Path]::GetTempFileName() + ".pdf"

# --- Стадия 1: pikepdf — collapse content streams в Form XObject ---
# Оставляем stream[0] (схемы + боковая шкала), оборачиваем в Form XObject (изоляция
# graphics state, PDF 1.7 §8.10 — нет stack underflow в Acrobat). Удаляем legacy XObject.
$py1 = @"
import sys, pikepdf
src, dst = sys.argv[1], sys.argv[2]
pdf = pikepdf.open(src)
for page in pdf.pages:
    cs = page.get('/Contents')
    if isinstance(cs, pikepdf.Array) and len(cs) > 1:
        form = pikepdf.Stream(pdf, cs[0].read_bytes())
        form.Type = pikepdf.Name('/XObject'); form.Subtype = pikepdf.Name('/Form')
        form.BBox = page.MediaBox; form.Matrix = pikepdf.Array([1,0,0,1,0,0])
        form.Resources = page.Resources
        page.Resources.XObject['/CleanBody'] = form
        page.Contents = pikepdf.Stream(pdf, b'q\n/CleanBody Do\nQ\n')
    xobj = page.Resources.get('/XObject')
    if xobj:
        for legacy in ('/fzFrm0', '/fullpage'):
            if legacy in xobj: del xobj[legacy]
pdf.save(dst); print('stage1 ok')
"@
$env:PYTHONIOENCODING = "utf-8"
python -c $py1 $InputPdf $tmpClean
if (-not $?) { throw "Стадия 1 (pikepdf) упала" }

# --- Стадия 2: pdfcpu overlay нового штампа ---
# pos:full (не badge), scale:1.0 abs (без масштаба), rot:0 (иначе дефолт 25°).
$desc = "pos:full, scale:1.0 abs, rot:0"
if ($Pages) {
    & $pdfcpu stamp add -pages $Pages --mode pdf $StampPdf $desc $tmpClean $tmpStamped
} else {
    & $pdfcpu stamp add --mode pdf $StampPdf $desc $tmpClean $tmpStamped
}
if ($LASTEXITCODE -ne 0) { throw "Стадия 2 (pdfcpu) упала, код $LASTEXITCODE" }

# --- Стадия 3: PyMuPDF clean — нормализация Type1-шрифтов (фикс Acrobat «Ошибка на странице») ---
$py3 = @"
import sys, fitz
fitz.open(sys.argv[1]).save(sys.argv[2], garbage=4, clean=True, deflate=True, deflate_fonts=True)
print('stage3 ok')
"@
python -c $py3 $tmpStamped $OutputPdf
if (-not $?) { throw "Стадия 3 (PyMuPDF) упала" }

Remove-Item $tmpClean, $tmpStamped -ErrorAction SilentlyContinue
Write-Host "OK -> $OutputPdf"
Write-Host "ВЕРИФИКАЦИЯ (обязательно): pdfcpu validate --mode strict; рендер ВСЕХ листов; re-grep старого шифра/ФИО (должно быть 0)."

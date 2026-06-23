<#
.SYNOPSIS
  Replace title block (stamp) in <организация> project documentation PDFs.

.DESCRIPTION
  Two-stage pipeline:
    1. pikepdf removes legacy /fzFrm0 + /fullpage Form XObjects.
    2. pdfcpu stamp add --mode pdf overlays a new stamp template PDF.

  The stamp PDF must itself contain the stamp positioned in the bottom-right corner
  of an A3-landscape page (e.g., generated from Word footer).
#>

param(
    [Parameter(Mandatory=$true)][string]$InputPdf,
    [Parameter(Mandatory=$true)][string]$StampPdf,
    [Parameter(Mandatory=$true)][string]$OutputPdf,
    [string]$Pages = ""
)

$ErrorActionPreference = "Stop"

$InputPdf = (Resolve-Path $InputPdf).Path
$StampPdf = (Resolve-Path $StampPdf).Path

$pdfcpu = "$HOME\.claude\bin\pdfcpu\pdfcpu_0.12.1_Windows_x86_64\pdfcpu.exe"
if (-not (Test-Path $pdfcpu)) { throw "pdfcpu not installed: $pdfcpu" }

# Step 1: pikepdf clean — write to a .pdf file in tempdir
$tmpDir = [System.IO.Path]::GetTempPath()
$cleaned = Join-Path $tmpDir ("pdfclean_" + [Guid]::NewGuid().ToString("N") + ".pdf")

$pyScript = @"
import pikepdf
src = r'$InputPdf'
dst = r'$cleaned'
pdf = pikepdf.open(src)
collapsed = 0
removed_xo = 0
for page in pdf.pages:
    cs = page.Contents
    if isinstance(cs, pikepdf.Array) and len(cs) > 1:
        # Оставляем только stream[0] (схемы + боковая шкала).
        # Оборачиваем в Form XObject — это изолирует graphics state
        # по спеке PDF (PDF 1.7 §8.10), поэтому несбалансированные q
        # внутри не утекают наружу. Безопаснее чем ручная компенсация Q.
        body_bytes = cs[0].read_bytes()
        form = pikepdf.Stream(pdf, body_bytes)
        form.Type = pikepdf.Name('/XObject')
        form.Subtype = pikepdf.Name('/Form')
        form.BBox = page.MediaBox
        form.Matrix = pikepdf.Array([1, 0, 0, 1, 0, 0])
        # Копируем Resources страницы в форму, чтобы внутренние ссылки сохранились
        if '/Resources' in page:
            form.Resources = page.Resources
        # Регистрируем форму как XObject у страницы
        if '/Resources' not in page:
            page.Resources = pikepdf.Dictionary()
        if '/XObject' not in page.Resources:
            page.Resources.XObject = pikepdf.Dictionary()
        page.Resources.XObject['/CleanBody'] = form
        # Заменяем Contents на единственный вызов формы
        page.Contents = pikepdf.Stream(pdf, b'q\n/CleanBody Do\nQ\n')
        collapsed += 1
    else:
        # Одиночный stream — убираем явные вызовы /fzFrm0
        cs_bytes = cs.read_bytes()
        new_cs = cs_bytes.replace(b'q\n/fzFrm0 Do\nQ\n', b'').replace(b'/fzFrm0 Do', b'')
        if new_cs != cs_bytes:
            page.Contents = pikepdf.Stream(pdf, new_cs)
    # Удаляем legacy XObjects штампа
    if '/Resources' in page and '/XObject' in page.Resources:
        xo = page.Resources.XObject
        for n in ['/fzFrm0', '/fullpage']:
            if n in xo:
                del xo[n]
                removed_xo += 1
pdf.save(dst)
print(f'collapsed {collapsed} pages, removed {removed_xo} XObjects')
"@

$pyFile = Join-Path $tmpDir ("clean_" + [Guid]::NewGuid().ToString("N") + ".py")
[System.IO.File]::WriteAllText($pyFile, $pyScript, [System.Text.UTF8Encoding]::new($false))
$env:PYTHONIOENCODING = "utf-8"
& python $pyFile
Remove-Item $pyFile
if (-not (Test-Path $cleaned)) { throw "pikepdf step failed: $cleaned not created" }

# Step 2: pdfcpu overlay (промежуточный)
$stamped = Join-Path $tmpDir ("pdfstamped_" + [Guid]::NewGuid().ToString("N") + ".pdf")
$stampDesc = "pos:full, scale:1.0 abs, rot:0"
$pdfcpuArgs = @("stamp", "add", "--mode", "pdf")
if ($Pages -ne "") { $pdfcpuArgs += @("-p", $Pages) }
$pdfcpuArgs += @($StampPdf, $stampDesc, $cleaned, $stamped)

Write-Host "pdfcpu stamp add --mode pdf ..."
& $pdfcpu @pdfcpuArgs
Remove-Item $cleaned -ErrorAction SilentlyContinue

if (-not (Test-Path $stamped)) { throw "pdfcpu step failed" }

# Step 3: PyMuPDF clean — фиксит Type1-шрифты без FirstChar/Widths
# (наследие pypdf-сборки, ломает Acrobat) + полный garbage collection
$cleanScript = @"
import fitz
doc = fitz.open(r'$stamped')
doc.save(r'$OutputPdf', garbage=4, clean=True, deflate=True, deflate_fonts=True)
doc.close()
"@
$pyFile2 = Join-Path $tmpDir ("clean_" + [Guid]::NewGuid().ToString("N") + ".py")
[System.IO.File]::WriteAllText($pyFile2, $cleanScript, [System.Text.UTF8Encoding]::new($false))
Write-Host "PyMuPDF clean (fix fonts + garbage collect)..."
& python $pyFile2 2>&1 | Where-Object { $_ -notmatch 'MuPDF error: format error: cannot find object' }
Remove-Item $pyFile2
Remove-Item $stamped -ErrorAction SilentlyContinue

if (-not (Test-Path $OutputPdf)) { throw "Output not created: $OutputPdf" }
$size = (Get-Item $OutputPdf).Length
Write-Host "OK: $OutputPdf ($([math]::Round($size/1KB, 1)) KB)"

# Validate strict-mode
Write-Host "Validating (strict)..."
& $pdfcpu validate --mode strict "$OutputPdf" 2>&1 | Select-Object -First 3

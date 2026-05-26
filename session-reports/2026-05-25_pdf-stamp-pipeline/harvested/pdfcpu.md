# pdfcpu — заметка harvest 2026-05-25

**Источник:** [github.com/pdfcpu/pdfcpu](https://github.com/pdfcpu/pdfcpu)
**Stars:** 8650 | **Last commit:** 2026-05-11 | **License:** Apache-2.0 ✓
**Язык:** Go (single-binary CLI, no runtime dependencies)
**Release использован:** v0.12.1 Windows x86_64 (8.5 MB)

## Что умеет (по нашей задаче)

- `stamp add --mode pdf` — PDF-on-PDF full-page overlay
- `stamp add --mode image` — image overlay
- `stamp add --mode text` — text overlay (Unicode, custom fonts)
- `stamp remove` — удаление **своих** stamps (не помогает с legacy /fzFrm0)
- `-p "1-10,15,20-30"` — selective pages
- `pos:full|tl|tc|tr|cl|c|cr|bl|bc|br` — позиционирование (anchor)
- `scale:N abs|rel` — масштаб (abs = absolute, rel = relative to page)
- `rot:N` — поворот (default 25° для image-stamps!)
- `op:N` — opacity 0..1

## Тест на нашем PDF (СТраница для проб.ORIG.pdf, A3 landscape)

Команда:
```powershell
pdfcpu stamp add --mode pdf etr_stamp.pdf "pos:full, scale:1.0 abs, rot:0" in.pdf out.pdf
```

Результат: full-page overlay. Старый штамп остался поверх (нужен pikepdf-первый-шаг). Скорость — секунды.

## Ловушки

1. **`-mode pdf` vs `--mode pdf`** — в PowerShell short-форма `-mode` ломалась как `-m + ode`. Использовать `--mode`.
2. **`pos:br` по умолчанию делает «бейджик»** — уменьшает stamp.pdf и ставит badge в правый-нижний. Нужно явно `pos:full` чтобы лечь страница-на-страницу.
3. **Поворот 25° default** для image-stamps. Для pdf-mode default 0, но лучше явно `rot:0`.
4. **`stamp remove` удаляет только pdfcpu-stamps** — не работает с legacy Form XObjects из других сборок.

## Установка (Windows)

```powershell
$bin = "$HOME\.claude\bin\pdfcpu"
New-Item -ItemType Directory -Force $bin | Out-Null
$url = "https://github.com/pdfcpu/pdfcpu/releases/download/v0.12.1/pdfcpu_0.12.1_Windows_x86_64.zip"
$env:HTTPS_PROXY = ""  # GitHub bypass
Invoke-WebRequest $url -OutFile "$bin\pdfcpu.zip" -UseBasicParsing
Expand-Archive "$bin\pdfcpu.zip" $bin -Force
```

После — `pdfcpu.exe` в `$bin\pdfcpu_0.12.1_Windows_x86_64\pdfcpu.exe`.

## Кандидат на manifest

Добавить в `~/.claude/setup-extras.ps1` (см. `~/.claude/extras-manifest.json`):
```json
{
  "name": "pdfcpu",
  "version": "0.12.1",
  "url": "https://github.com/pdfcpu/pdfcpu/releases/download/v0.12.1/pdfcpu_0.12.1_Windows_x86_64.zip",
  "type": "github-zip",
  "install_to": "~/.claude/bin/pdfcpu/",
  "executable": "pdfcpu_0.12.1_Windows_x86_64/pdfcpu.exe"
}
```

## Связано

- [[2026-05-25_pdf-stamp-pipeline]] — основной report
- [[pdf-helper]] — методический скилл (обновить триггеры на «pdfcpu», «batch stamp»)

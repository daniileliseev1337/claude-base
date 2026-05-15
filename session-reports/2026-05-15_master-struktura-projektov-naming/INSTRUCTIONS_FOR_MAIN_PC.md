# Инструкция для главного ПК (DANIILPC)

> **Источник:** сессия 2026-05-15 на DELISEEV-PC. Подробности — в `report.md` рядом.
> **Цель:** воспроизвести на главном ПК всю инфраструктуру, поднятую на DELISEEV-PC,
> чтобы можно было продолжать работу с DWG/PDF/инженерными xlsx с теми же
> возможностями.

## 1. Что появилось нового (резюме)

| Что | Зачем | Где |
|---|---|---|
| **autocad-mcp** v3.0 (puran-water) | Native MCP-сервер для AutoCAD LT + headless ezdxf. 8 tools после рестарта Claude Code | `~/.claude/mcp-servers/autocad-mcp/` (не синкается через claude-base — ставить локально) |
| **Python user-пакеты** | DXF-генерация, PDF OCR без Tesseract, network diagrams | user-mode `pip install` |
| **Методика naming шкафов** | Универсальная схема для всех инженерных проектов | `artifacts/project_master_structure_naming.md` |
| **Скрипты-эталоны** | Перезапускаемые: xlsx→DXF, PDF→OCR, network graph | `artifacts/*.py` |
| **harvest база** | 37 заметок по PDF/DWG/diagrams инструментам | `harvested/` рядом + `~/.claude/harvested/` |
| **memory знания** | autocad-mcp путь, PDF OCR pipeline | `artifacts/reference_*.md` (на главном ПК положи в `~/.claude/projects/<id>/memory/`) |

## 2. Поэтапная установка на главном ПК

### 2.1. Pull свежей базы claude-base

```powershell
cd ~/.claude
git pull --rebase
```

Это подтянет с DELISEEV-PC:
- `session-reports/2026-05-15_master-struktura-projektov-naming/` (включая artifacts/)
- 37 harvest-заметок в `harvested/` (если whitelist включает корень `harvested/`)

> ⚠ `~/.claude/projects/<id>/memory/` **НЕ синкается** (auto-memory локальная).
> Если хочешь те же memory-знания на главном ПК — скопируй вручную:
> ```powershell
> Copy-Item ~/.claude/session-reports/2026-05-15_master-struktura-projektov-naming/artifacts/reference_*.md `
>   ~/.claude/projects/<твой-project-id>/memory/ -Force
> # Затем обновить MEMORY.md руками — добавить строки про новые reference'ы.
> ```

### 2.2. Python пакеты (user-mode, без админ-прав)

```powershell
python -m pip install --user matplotlib networkx ezdxf pypdfium2 pdfplumber paddleocr paddlepaddle
```

Проверь версии:
```powershell
python -c "import matplotlib, networkx, ezdxf, pypdfium2, pdfplumber, paddleocr; print('OK')"
```

Что ставится и зачем:
- **matplotlib + networkx** — graph-визуализация (структурные схемы из xlsx)
- **ezdxf** — генерация и чтение DXF/DWG из Python
- **pypdfium2** — рендер PDF без лимита 2000×2000 (наш pdf-mcp не пробивает)
- **pdfplumber** — таблицы из векторных PDF
- **paddleocr + paddlepaddle** — OCR русского+английского без Tesseract (~1 GB)

> Удалить если не нужны: `pip uninstall <name>`.

### 2.3. autocad-mcp (главный приз — нативная работа с DWG в Claude Code)

#### 2.3.1. Скачать репо

```powershell
# Через ZIP — обходит проблемы с git+корп-прокси
$dest = "$env:USERPROFILE\.claude\mcp-servers"
New-Item -ItemType Directory -Path $dest -Force | Out-Null
$repoDir = "$dest\autocad-mcp"
$zipUrl = "https://github.com/puran-water/autocad-mcp/archive/refs/heads/main.zip"
$zipPath = "$env:TEMP\autocad-mcp-main.zip"
Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
Expand-Archive -Path $zipPath -DestinationPath $dest -Force
$extracted = Join-Path $dest "autocad-mcp-main"
if (Test-Path $repoDir) { Remove-Item $repoDir -Recurse -Force }
Rename-Item $extracted $repoDir
```

> Альтернатива через git (если прокси пропускает):
> ```powershell
> git clone https://github.com/puran-water/autocad-mcp.git $repoDir
> ```

#### 2.3.2. uv sync (venv + зависимости)

Нужен `uv` (Astral). Проверь: `uv --version`. Если нет:
```powershell
python -m pip install --user uv
```

Затем:
```powershell
cd ~/.claude/mcp-servers/autocad-mcp
uv sync
```

Создаст `.venv` с Python и зависимостями (mcp 1.26, pywin32, ezdxf, ...).

#### 2.3.3. Зарегистрировать MCP

```powershell
$venvPython = "$env:USERPROFILE\.claude\mcp-servers\autocad-mcp\.venv\Scripts\python.exe"
claude mcp add autocad-mcp -s user -e AUTOCAD_MCP_BACKEND=auto -- $venvPython -m autocad_mcp
```

Запись попадёт в `~/.claude.json`. Проверь:
```powershell
claude mcp list | Select-String "autocad"
```
Должно показать `autocad-mcp ... ✓ Connected`.

#### 2.3.4. Загрузить LISP в AutoCAD (только если AutoCAD установлен)

В AutoCAD LT 2024+:
1. `APPLOAD`
2. Browse → `~/.claude/mcp-servers/autocad-mcp/lisp-code/mcp_dispatch.lsp` → **Load**
3. В командной строке должно появиться: `=== MCP Dispatch v3.1 loaded ===`
4. (Рекомендую) Добавить в **Startup Suite** через **Contents → Add** в том же диалоге

Без AutoCAD — autocad-mcp работает только в `ezdxf` headless backend.

#### 2.3.5. Рестарт Claude Code

Закрыть/переоткрыть VS Code-расширение или CLI-сессию. После рестарта появятся 8 новых MCP tools:
`drawing` · `entity` · `layer` · `block` · `annotation` · `pid` · `view` · `system`.

### 2.4. d2 (опционально, для сетевых диаграмм через ELK-layout)

Auto-classifier Claude Code блокирует прямое скачивание `.exe` с GitHub.
Вариант ручной:
1. Скачать ZIP вручную с https://github.com/terrastruct/d2/releases/latest
2. Распаковать `d2.exe` в `%LOCALAPPDATA%\Programs\d2\`
3. (Опционально) Добавить в PATH

## 3. Эталонные артефакты (`artifacts/` рядом)

| Файл | Что |
|---|---|
| `build_dxf_from_xlsx.py` | Генерация DXF структурной схемы из xlsx (200 шкафов) — ezdxf |
| `build_structure_diagram.py` | Графовая структурная схема через matplotlib+networkx |
| `render_dxf_preview.py` | Превью DXF в PNG/SVG (matplotlib backend ezdxf) |
| `test_paddleocr_pdf.py` | Извлечение текста из PDF в кривых через pypdfium2+PaddleOCR |
| `Перенаименование_шкафов_ПСИ-158.xlsx` | П-таблица (43 шкафа, Л2) |
| `Шкафы_ПСИ-158_v2_5сетей.xlsx` | Р-таблица (200 шкафов, 5 сетей МИС/СБ/ОП/СОТ/СВН) |
| `project_master_structure_naming.md` | Методика naming `[Объект]-[Блок]-[Сеть]-[Тип][ЭП]` |
| `reference_*.md` | Memory-знания (autocad-mcp путь, PDF OCR pipeline) |

## 4. Ловушки и важные нюансы

### 4.1. PaddleOCR на Windows
- **`enable_mkldnn=False` обязательно** для больших картинок (oneDNN runtime баг)
- При первом запуске качает ~500 MB моделей в `~/.paddlex/official_models/`
- Можно использовать `lang='ru'` для русского — PaddleOCR подгрузит `eslav_PP-OCRv5_mobile_rec`

### 4.2. PowerShell UTF-8
Перед запуском Python-скриптов с русским print:
```powershell
$env:PYTHONIOENCODING = "utf-8"
```
Или в скрипте заменять кириллицу/спецсимволы на латиницу.

### 4.3. git+корп-прокси
Если `git clone` падает с `Proxy CONNECT aborted` хотя `$env:HTTPS_PROXY` установлен — обходить через `Invoke-WebRequest`-ZIP (PS подхватывает env-прокси).

### 4.4. pdf-mcp лимит 2000×2000
Наш текущий `pdf_render_pages` рендерит max 2000×2000 px. Для крупных чертежей (A2×3) этого мало. Решение — использовать `pypdfium2.PdfDocument(...).render(scale=...)` без лимита.

### 4.5. settings.json self-modification
Auto-classifier Claude Code блокирует правку `~/.claude/settings.json` через мою Edit-операцию (даже через `/update-config` skill). Это hard-deny security boundary — менять вручную.

### 4.6. Прокси-пароль в env-var
`$env:HTTPS_PROXY` хранит пароль в открытом виде. Рекомендую перенести в Windows Credential Manager или git credential helper. Сменить пароль если он засветился где-то.

## 5. Что НЕ запушено в claude-base (требует ручной установки на главном ПК)

- `~/.claude/mcp-servers/autocad-mcp/` — папка 150+ MB, не в whitelist auto-sync
- `~/.claude.json` — содержит регистрацию MCP-серверов, личные данные
- `~/.claude/projects/<id>/memory/` — auto-memory локальная
- Python user-packages — ставятся через `pip install --user`
- d2 binary — заблокирован для авто-установки
- AutoLISP в AutoCAD — пользовательское действие в AutoCAD GUI
- Файлы на Desktop (xlsx/PDF/PNG/SVG в `Здадчака\`) — рабочая папка проекта

## 6. После установки на главном ПК — sanity check

```powershell
# 1. Python пакеты
python -c "import matplotlib, networkx, ezdxf, pypdfium2, pdfplumber, paddleocr; print('All OK')"

# 2. MCP autocad-mcp
claude mcp list | Select-String "autocad-mcp.*Connected"

# 3. ezdxf пробный DXF
python -c "import ezdxf; doc=ezdxf.new(); doc.modelspace().add_text('Hello'); doc.saveas('test.dxf'); print('ezdxf OK')"

# 4. PaddleOCR (загрузит модели ~500MB)
python -c "from paddleocr import PaddleOCR; PaddleOCR(lang='ru', enable_mkldnn=False); print('PaddleOCR OK')"
```

Если все 4 проверки прошли — главный ПК готов работать на уровне DELISEEV-PC.

## 7. Связанные документы в этой папке

- `report.md` — полный session-report
- `harvested/{pdf,dwg,diagrams}/` — 37 заметок по инструментам
- `artifacts/` — все скрипты и xlsx-артефакты

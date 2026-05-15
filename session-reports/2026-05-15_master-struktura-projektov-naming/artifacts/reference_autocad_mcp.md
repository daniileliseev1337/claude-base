---
name: reference-autocad-mcp
description: "Установленный MCP-сервер для AutoCAD LT (puran-water/autocad-mcp v3.0). Путь, регистрация, 8 tools и инструкции по AutoLISP."
metadata: 
  node_type: memory
  type: reference
  originSessionId: fb892ce7-0051-4258-b832-c80cab5ecb76
---

**Где живёт:** `C:\Users\Deliseev\.claude\mcp-servers\autocad-mcp\`

**Источник:** [puran-water/autocad-mcp](https://github.com/puran-water/autocad-mcp), 250 ⭐, MIT (на 2026-05-15).
**Установка через ZIP** (git clone не пробил корп-прокси), затем `uv sync`.

**Регистрация в Claude Code** (user scope):
```powershell
claude mcp add autocad-mcp -s user -e AUTOCAD_MCP_BACKEND=auto -- "<repoDir>\.venv\Scripts\python.exe" -m autocad_mcp
```
Запись попала в `C:\Users\Deliseev\.claude.json`. После рестарта сессии Claude Code
загружает MCP tools автоматически.

**8 групп tools** (после рестарта сессии):
`drawing` · `entity` · `layer` · `block` · `annotation` · `pid` · `view` · `system`

**Два backend'а:**
- `file_ipc` — через AutoLISP (требует AutoCAD LT 2024+ запущенный). Нужно
  загрузить `<repoDir>\lisp-code\mcp_dispatch.lsp` через APPLOAD в AutoCAD
  (+ в Startup Suite чтобы грузился автоматически).
- `ezdxf` — headless, без AutoCAD. Активируется при `AUTOCAD_MCP_BACKEND=ezdxf`
  или автоматически при `auto` если AutoCAD не запущен.

**Health-чек:** `claude mcp list` → должно показать `autocad-mcp ... ✓ Connected`.

**Зависимости установлены в venv:** mcp 1.26, pywin32 (COM), ezdxf, matplotlib, pydantic, structlog.

**Запуск вне Claude Code** (для отладки):
```powershell
& "C:\Users\Deliseev\.claude\mcp-servers\autocad-mcp\.venv\Scripts\python.exe" -m autocad_mcp
```

**Связанные:** [[reference-ezdxf-dxf-generation]], [[reference-harvest-tools-2026-05]]

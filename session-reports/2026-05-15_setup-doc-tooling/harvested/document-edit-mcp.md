# document-edit-mcp

**URL:** https://github.com/alejandroBallesterosC/document-edit-mcp
**Stars:** 49
**Last commit:** 2025-11-10 (полгода назад, в пределах нормы)
**License:** MIT
**Тип:** MCP-сервер (Python 3.10+)

## Что делает

Универсальный документ-сервер для Claude Desktop: Word + Excel + PDF + CSV в одном MCP. Доступен через Smithery registry.

Из заявленного функционала **по PDF**:
- **Создание PDF из текста** (generation)
- **Конвертация Word → PDF**

В README **НЕ заявлены**: merge, split, form-fill, аннотации, водяные знаки, удаление страниц, поворот. То есть это **PDF generation server**, а не PDF editor.

## Почему подходит нам

Слабо. По нашему ТЗ нужно именно **редактирование существующих PDF**, а здесь только генерация новых. Из плюсов — Word/Excel в одном MCP, но эти задачи у нас закрыты отдельными MCP (`word`, `excel`).

## Как подключить

Через Smithery (быстро):
```powershell
npx -y @smithery/cli install @alejandroBallesterosC/document-edit-mcp --client claude
```

Или вручную: clone + `./setup.sh` (bash, на Windows потребует git-bash / WSL).

## Подводные камни

- **49 stars** — формально не дотягивает до нашего порога ≥50, но репутация автора прослеживается (Smithery-листинг, 10 коммитов, Docker-образ).
- **PDF editing функций минимум** — фактически он закрывает только text-to-PDF, что мы умеем через reportlab/markdown→pdf сами в 3 строки.
- Дублирует уже установленные у нас `word` и `excel` MCP — если поставить, придётся решать, какой MCP отвечает за Word.
- Логи пишутся в `logs/document_mcp.log` в директории установки — следить за разрастанием.

## Вердикт

❌ **Не брать.** Не закрывает наши целевые операции (merge / split / forms / annotations). PDF-генерацию мы получим проще через свой Python-скрипт. А Word/Excel-функционал перекрывается с уже работающими MCP `word` и `excel`.

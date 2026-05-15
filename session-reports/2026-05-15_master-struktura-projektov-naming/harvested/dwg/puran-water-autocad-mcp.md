# puran-water/autocad-mcp
- URL: https://github.com/puran-water/autocad-mcp
- Stars: 250
- Last commit: 2026-02-20
- License: MIT
- Описание: MCP server для AutoCAD LT 2024+ с двумя backend'ами: File IPC (живой AutoCAD на Windows) и ezdxf headless (любая ОС, без AutoCAD), + произвольное выполнение AutoLISP-кода.

## Зачем смотрели
Сценарии 1 (xlsx→DWG через MCP), 2 (read DWG), 3 (write DWG/DXF), 7 (AutoLISP-скрипты), 8 (MCP-сервер для DWG).

## Оценка
- **Подходит? Да — это «джекпот» из найденных MCP.**
- **Сильные стороны:**
  - **Dual backend**: ezdxf для headless (без AutoCAD), File IPC для живого AutoCAD.
  - **execute_lisp tool** — произвольный AutoLISP. Превращает сервер из фиксированного API в расширяемую платформу.
  - 8 консолидированных tools: drawing management, entity CRUD, layers, blocks, annotations, **P&ID symbols** (для инженерных схем — критично нашему сценарию!), viewports, system ops.
  - Focus-free автоматизация через `PostMessageW` — не отбирает фокус окна.
  - Чистый MIT.
  - У него самые подробные комментарии в README среди всех CAD MCP-серверов.
- **Слабые стороны / риски:**
  - File IPC backend требует AutoCAD LT 2024+ только на Windows.
  - На MCP registry официально пока нет (только GitHub).
  - Свежий (февраль 2026), активная разработка — API может меняться.
- **Решение: используем активно.** Конкретно: ставим как MCP-сервер для Claude Code (после согласования с пользователем), backend = ezdxf для генерации DXF из xlsx ПСИ-158. P&ID символы могут пригодиться для СКС/ЛВС-схем как структурные блоки. **Это основной кандидат на интеграцию.**

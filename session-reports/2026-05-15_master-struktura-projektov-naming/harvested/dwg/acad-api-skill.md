# ADN-DevTech/acad-api-skill
- URL: https://github.com/ADN-DevTech/acad-api-skill
- Stars: 4
- Last commit: 2026-05-06
- License: MIT
- Описание: Официальный Claude Code skill от Autodesk DevTech для разработки AutoCAD/Civil 3D/Plant 3D-плагинов на .NET 10 — с корректным loading сборок, шаблонами проектов, .bundle-упаковкой.

## Зачем смотрели
Сценарии 7 (AutoCAD plugin) + 8 (MCP/skill для Claude Code) — официальная история от вендора AutoCAD.

## Оценка
- **Подходит? Да (важная находка, несмотря на 4★).**
- **Сильные стороны:**
  - **Официальный от Autodesk** (организация `ADN-DevTech` — Authorized Developer Network).
  - **Прямая совместимость с Claude Code** — копируется как `CLAUDE.md` + `skills/`.
  - MIT.
  - Свежий (коммит за 9 дней до сессии).
  - Включает append-only discovery log — модель документирует находки, человек верифицирует и переносит в canonical skills. Концепция нашему репозиторию `claude-base` родная.
  - Решает реальные боли: галлюцинации про DLL paths, структуру проекта, неправильные assembly loading.
- **Слабые стороны / риски:**
  - Молодой (только 4★), API skill'а может меняться.
  - Заточен под .NET 10 — для legacy AutoCAD (2019, 2021) может не подойти.
  - Не покрывает Python/ezdxf workflow — только .NET-плагины.
- **Решение: ставим на радар как образцовый skill** для расширения нашей методики. Если возникнет задача «сделай мне AutoCAD-плагин на C#» — берём за основу. Также **полезно изучить структуру их skill** как референс для наших собственных skills под Revit/AutoCAD. Возможный candidate для **adopt в `~/.claude/skills/`** при первой реальной .NET-задаче.

# Бриф пилота: bim-plugin-builder (отдельная сессия)

Источник решения: session-reports/2026-06-10_repo-harvest/report.md (вердикт ВЗЯТЬ).
Репо: github.com/<автор>/bim-plugin-builder (MIT, 2026-05, 1⭐ single-author — форкнуть в базу).

## Что это
C#-плагины Revit/Tekla БЕЗ Visual Studio: PowerShell + dotnet SDK 8. Сам генерит .csproj
и .addin, деплоит в Addins. Поддержка Revit 2020–2026 (net48 / net8.0-windows).

## Цель пилота
Собрать тестовую кнопку под Revit 2025 на машине с Revit. При успехе:
- skill для компилируемых аддонов;
- fallback-секция в агенте pyrevit-engineer (когда IronPython не хватает — C#-аддон).

## Предусловия
- dotnet SDK 8 (~200 МБ) — поставить;
- машина с Revit 2025 (НЕ хаб-ноутбук DANIIL, если на нём Revit нет — уточнить у пользователя);
- скрипт ~100 строк — перед запуском прочитать целиком (безопасность).

## Критерии успеха (до старта, Karpathy #4)
1. Кнопка собирается без VS и появляется в ленте Revit 2025.
2. Время от нуля до кнопки ≤ 1 час.
3. Решение: форк в claude-base + skill, либо вердикт «не надо» с причиной в report.md.

Модель сессии: обычная (sonnet/opus) — Fable не нужна. Субагенты — по матрице CLAUDE.md.

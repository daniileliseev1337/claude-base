# orcastor/cad2x-converter
- URL: https://github.com/orcastor/cad2x-converter
- Stars: 193
- Last commit: 2026-05-11
- License: LGPL-2.1
- Описание: Минималистичный standalone CLI-конвертер DXF/DWG → DXF/PDF/PNG/SVG, бинарник 2.9MB, без GUI и зависимостей, кроссплатформенный (Win/Mac/Linux/Android/iOS).

## Зачем смотрели
Сценарий 4 (DWG → SVG/PNG для предпросмотра без AutoCAD).

## Оценка
- **Подходит? Да.**
- **Сильные стороны:**
  - Standalone бинарник 2.9MB — кидаем в `~/.claude/bin/` и забываем.
  - Без GUI, без AutoCAD, без ODA.
  - **Read** DWG/DXF → **write** DXF v2007 / PDF / PNG / SVG.
  - Поддержка TTF/TTC шрифтов — для кириллицы критично.
  - LGPL-2.1 при использовании как **внешнего CLI** через subprocess — не вирусная.
  - Свежий (коммит за 4 дня до сессии).
- **Слабые стороны / риски:**
  - LGPL-2.1 — если динамически линкуем библиотеку, надо публиковать наши изменения **самой библиотеки**. CLI-вариант через subprocess — нейтрально.
  - Качество рендера для сложных DWG может уступать AutoCAD.
  - Не пишет DWG — только DXF/раст/вектор.
- **Решение: используем как внешний CLI** для генерации SVG/PNG-превью DWG-файлов в session-reports и в pipeline проверки. Ставим в `~/.claude/_sandbox/bin/` (после согласования с пользователем).

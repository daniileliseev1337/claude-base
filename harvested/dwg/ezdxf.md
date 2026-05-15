# mozman/ezdxf
- URL: https://github.com/mozman/ezdxf
- Stars: 1290
- Last commit: 2026-05-14
- License: MIT
- Описание: Python-интерфейс к DXF-файлам с встроенной поддержкой рендеринга в PNG/PDF/SVG через matplotlib.

## Зачем смотрели
Сценарии 1 (xlsx→DWG), 2 (чтение DWG), 3 (запись DWG/DXF), 4 (DWG→SVG/PNG). Базовая библиотека для всего workflow.

## Оценка
- **Подходит? Да (базовый инструмент).**
- **Сильные стороны:**
  - Чистая MIT-лицензия — можно встраивать куда угодно.
  - Активная поддержка (коммит за день до сессии), автор Manfred Moitzi надёжный.
  - Полная поддержка DXF R12...R2018 (read/write), R13/R14 read-only (upgrade в R2000).
  - `drawing` add-on рендерит в PNG/PDF/SVG через matplotlib — без AutoCAD.
  - `odafc` add-on — мост к ODA File Converter для DWG read/write.
  - Кроссплатформенный (Windows/Linux/macOS), Python 3.10+.
  - Хорошая документация и примеры.
- **Слабые стороны / риски:**
  - DWG напрямую не читает — нужен ODA File Converter (бесплатный, но внешний).
  - Рендер требует matplotlib/PySide6 как дополнительные зависимости.
  - Python 3.10+ — старые системы не подойдут.
- **Решение: используем как фундамент.** Ставим в каждый проект где нужны DWG. Под xlsx→DWG для ПСИ-158 — основной инструмент.

# LibreDWG/libredwg
- URL: https://github.com/LibreDWG/libredwg
- Stars: 1394
- Last commit: 2026-05-06
- License: GPL-3.0
- Описание: GNU LibreDWG — C-библиотека для свободного чтения/записи DWG-файлов с CLI-утилитами (dwgread, dwgwrite, dwg2dxf, dwg2SVG).

## Зачем смотрели
Сценарии 2 (чтение DWG), 3 (запись DWG). Единственный по-настоящему свободный нативный DWG-парсер (без зависимости от ODA).

## Оценка
- **Подходит? Под условием (GPL-3.0).**
- **Сильные стороны:**
  - **Нативно читает DWG** — не нужен ODA File Converter.
  - Активный (Free Software Foundation проект, ночные релизы).
  - Включает CLI-утилиты: `dwgread`, `dwg2dxf`, `dwg2SVG` — можно использовать без линковки.
  - Поддерживает все версии DWG от R13 до 2018.
  - Python/Perl/Ruby bindings.
- **Слабые стороны / риски:**
  - **GPL-3.0** — вирусная лицензия. Если линкуем как библиотеку — наш код тоже GPL.
  - **Использование как внешний CLI** — нейтрально, можно вызывать `dwg2dxf input.dwg output.dxf` через subprocess.
  - На Windows сборка нестабильна, лучше брать готовые бинарники.
  - Поддержка DXF записи неполная.
- **Решение: держим в уме как fallback CLI** для DWG→DXF, если ODA File Converter недоступен. **Код не копируем** в наши скрипты. Не ставим как Python-пакет в production.

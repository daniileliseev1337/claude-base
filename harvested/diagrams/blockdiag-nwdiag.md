# blockdiag/nwdiag + blockdiag/blockdiag

- **nwdiag:** https://github.com/blockdiag/nwdiag — 135 stars, Apache 2.0, Python.
- **blockdiag:** https://github.com/blockdiag/blockdiag — 240 stars, Apache 2.0, Python.
- **Last commit:** не показан явно, проект **очень редко обновляется** (последние релизы — 2020-2021 годы по PyPI). **Фильтр актив <12 мес — НЕ проходит.**

## Применимость к нашей задаче

- **Плюсы:**
  - **Специально для network diagrams** — единственный из найденных «честно» специализированный.
  - Синтаксис понятный:
    ```
    nwdiag {
      network dmz { address = "210.x.x.x/24"; web01; web02; }
      network internal { address = "172.x.x.x/24"; web01; db01; }
    }
    ```
  - Рисует **bus-style** network segments — то что нужно для подсетей в СКС.
- **Минусы:**
  - **Заброшен** (или почти). Доступен через PlantUML (там встроен), но самостоятельный проект мёртв.
  - PNG/SVG, без штампа ГОСТ.
- **Вывод:** через **PlantUML** этот синтаксис **жив** и пригоден. Прямой `nwdiag` Python-пакет — не брать.

## Лицензия

Apache-2.0 — зелёный.

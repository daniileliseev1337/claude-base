# NetBox + topology плагины

- **NetBox core:** https://github.com/netbox-community/netbox — 20.5k stars, Apache 2.0, актив.
- **netbox-community/netbox-topology-views:** https://github.com/netbox-community/netbox-topology-views — **1000 stars**, Apache 2.0, **v4.5.1 от 29 Mar 2026** (актив). Экспорт **XML для drawio** + PNG.
- **iDebugAll/nextbox-ui-plugin:** https://github.com/iDebugAll/nextbox-ui-plugin — 633 stars, MIT + proprietary topoSphere SDK (флаг!), v1.0.5 — Nov 2024 (на грани 12 мес).

## Применимость к нашей задаче

- **Плюсы (если бы у нас был NetBox):**
  - NetBox — единое место для inventory шкафов/кабелей/портов; топология строится автоматически по связям cables.
  - topology-views даёт SVG + **экспорт в drawio** — это закрывает почти все наши требования.
- **Минусы для нашей текущей задачи:**
  - **Требует развёрнутый NetBox** (PostgreSQL + Redis + Django) — это инфраструктура, не разовый инструмент.
  - Загрузка 200 шкафов в NetBox = почти такая же работа, как в Excel.
  - Если же NetBox уже есть в инфраструктуре заказчика — это **лучший вариант** (single source of truth).
- **Вывод:** **отложенно** — стоит держать в голове на будущее, если возьмёмся за крупный проект где имеет смысл поднять NetBox. Для разового xlsx → схема избыточно.

## Лицензия

Apache-2.0 (core + topology-views) — зелёный. nextbox-ui-plugin содержит проприетарный SDK — **флаг**, не использовать.

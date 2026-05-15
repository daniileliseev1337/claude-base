# DWG / AutoCAD harvest — index

Дата: 2026-05-15
Сессия: master-struktura-projektov-naming
Контекст: проектирование ПСИ-158 (медицинский комплекс), СКС/ЛВС, 200 шкафов из xlsx → нужны DWG-схемы и планы.

## Сравнительная таблица (отсортировано по релевантности)

| # | Имя | Stars | Last commit | License | Описание | Сценарий |
|---|---|---|---|---|---|---|
| 1 | mozman/ezdxf | 1290 | 2026-05-14 | MIT | Python DXF read/write + matplotlib рендер в PNG/PDF/SVG | 1,2,3,4 |
| 2 | LibreDWG/libredwg | 1394 | 2026-05-06 | GPL-3.0 | C-библиотека для DWG read/write (нативно, без ODA) | 2,3 |
| 3 | orcastor/cad2x-converter | 193 | 2026-05-11 | LGPL-2.1 | Standalone CLI: DWG/DXF → DXF/PDF/PNG/SVG, 2.9MB, кроссплатф. | 4 |
| 4 | puran-water/autocad-mcp | 250 | 2026-02-20 | MIT | MCP server: ezdxf headless + AutoLISP via IPC, P&ID примитивы | 1,2,3,7,8 |
| 5 | daobataotie/CAD-MCP | 336 | 2025-07-21 | MIT | MCP server для AutoCAD/GstarCAD/ZWCAD через COM (Windows) | 8 |
| 6 | datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN | 364 | 2026-05-06 | dual (MIT+EULA) | DWG → XLSX+PDF, бесплатно для не-коммерции | 2 |
| 7 | luanshixia/AutoCADCodePack | 518 | 2024-05-26 | MIT | C# обёртка над AutoCAD .NET API (LINQ-стиль) | 7 |
| 8 | mlightcad/libredwg-web | 54 | 2026-04-29 | GPL-3.0 | DWG/DXF JS-парсер на базе libredwg (для браузера) | 2 |
| 9 | dotoritos-kim/dxf-json | 122 | 2026-05-08 | GPL-3.0 | TypeScript DXF-парсер для Node+браузера | 2 |
| 10 | Autodesk-AutoCAD/AutoLispExt | 132 | 2026-04-10 | Apache-2.0 | Официальное VSCode-расширение для AutoLISP | 7 |
| 11 | ADN-DevTech/acad-api-skill | 4 | 2026-05-06 | MIT | Официальный Claude Code skill от Autodesk для AutoCAD .NET 10 плагинов | 7,8 |
| 12 | AnCode666/multiCAD-mcp | 33 | 2026-03-15 | Apache-2.0 | MCP для нескольких CAD (AutoCAD/BricsCAD/...) | 8 |
| 13 | thepiruthvirajan/autocad-mcp-server | 37 | 2025-07-28 | Apache-2.0 | Python MCP — стены/двери/окна для архит. планов | 1,8 |
| 14 | zh19980811/Easy-MCP-AutoCad | 159 | 2026-01-22 | NONE | Китайский MCP-сервер для AutoCAD (без лицензии — не копируем) | 8 |
| 15 | wtertinek/Linq2Acad | 76 | 2024-05-29 | MIT | LINQ-стиль обёртка для AutoCAD .NET | 7 |
| 16 | mxcad/mxcad | 29 | 2026-05-07 | NOASSERTION | Web-CAD движок для рендера/редактирования в браузере | 4 |
| 17 | fuzziness/kabeja | 127 | 2021-09-10 | NONE | Java DXF → SVG (не поддерживается, без лицензии) | 4 |
| 18 | iamjinlei/dxf2png | 50 | 2018-08-07 | NOASSERTION | Go: headless DXF → bitmap (старое, без лицензии) | 4 |
| 19 | reclosedev/pyautocad | 592 | 2021-11-19 | BSD-2 | COM-обёртка для AutoCAD из Python (заброшен с 2021) | 7 |
| 20 | ahmetcemkaraca/AutoCAD_MCP | 13 | 2025-08-08 | MIT | MCP для AutoCAD 2025 — 2D/3D ассистент | 8 |

Сценарии: 1=xlsx→DWG, 2=read DWG, 3=write DWG/DXF, 4=DWG→SVG/PNG, 5=diff dwg, 6=topology, 7=AutoCAD plugin/script, 8=MCP

## Рекомендации по сценариям

- **Сценарий 1 (xlsx → DWG, основной кейс ПСИ-158):**
  **ezdxf (Python, MIT)** — читаем xlsx через openpyxl/pandas, отрисовываем шкафы как блоки в DXF, экспортируем → ODA File Converter конвертирует DXF→DWG. Полностью headless, без AutoCAD. Это **наш базовый стек**.

- **Сценарий 2 (чтение DWG):** ezdxf + odafc addon (DWG→DXF→read). Альтернатива: libredwg (GPL — флаг) или dotoritos-kim/dxf-json (если делаем веб-инструмент).

- **Сценарий 3 (запись DWG/DXF):** ezdxf для DXF; для DWG — ezdxf + ODA File Converter (внешний бесплатный конвертер от Open Design Alliance).

- **Сценарий 4 (DWG→SVG/PNG):** **orcastor/cad2x-converter** — standalone CLI 2.9MB, без зависимостей, кроссплатф. Идеален для предпросмотра в session-reports. LGPL-2.1 = можно использовать как внешний CLI, не линковать статически.

- **Сценарий 5 (diff DWG):** готовых нет с приличными звёздами. Делаем сами через ezdxf: парсим оба файла, сравниваем сущности по handle/координатам.

- **Сценарий 6 (topology):** не нашлось готового для CAD. Топологию рисуем через ezdxf вручную (узлы шкафов + полилинии соединений), либо рендерим через graphviz/networkx → SVG → DXF.

- **Сценарий 7 (AutoCAD plugins):** **luanshixia/AutoCADCodePack** + **Linq2Acad** для .NET; **ADN-DevTech/acad-api-skill** — это официальный AI-skill от Autodesk для генерации плагинов через Claude Code, стоит изучить и потенциально установить.

- **Сценарий 8 (MCP):** топ-3:
  - **puran-water/autocad-mcp** — самый интересный, dual backend (ezdxf headless + AutoCAD IPC),
  - **daobataotie/CAD-MCP** — если нужно живое управление AutoCAD из чата,
  - **ADN-DevTech/acad-api-skill** — официальная история от Autodesk.

## Топ-5 итог

1. **ezdxf** (MIT, 1290★, активный) — фундамент всего.
2. **puran-water/autocad-mcp** (MIT, 250★) — MCP-обёртка ровно под наш сценарий (ezdxf + AutoLISP).
3. **orcastor/cad2x-converter** (LGPL, 193★) — DWG-предпросмотр.
4. **ADN-DevTech/acad-api-skill** (MIT, 4★) — официальный Autodesk skill для Claude Code (молодой, но важный — следить).
5. **LibreDWG** (GPL-3.0, 1394★) — единственный open-source нативный DWG-парсер. GPL = используем как внешний CLI, не как библиотеку в проприетарном коде.

## Файлы

См. соседние `.md` в этой папке — по одному на каждый репозиторий из топа.

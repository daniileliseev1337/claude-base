# Отброшенные кандидаты (с причиной)

## По constraint-check (платное / SaaS, нет приемлемого free-tier для коммерч. использования)

- **GoJS** (gojs.net, floorplanner sample) — мощный диаграммный движок, но **коммерческая
  лицензия** (платная для коммерч. проектов). Отпадает.
- **Syncfusion EJ2 Floor Planner** — богатый функционал (walls/snapping/JSON/PDF), но
  **коммерческая лицензия Syncfusion**. Отпадает.
- **Archilogic Floor Plan SDK** — требует publishable access token + облачный SaaS,
  платный. Отпадает.

## Не тот класс (готовые React/Next-приложения-планировщики, не встраиваемые библиотеки;
## заточены под РИСОВАНИЕ плана с нуля, а нам нужно класть точки поверх готового плана из Revit)

- **fedepaj/arcada-planner** (React + Konva + Zustand) — редактор планов, рисование стен/мебели.
- **ahmethakanbesel/floor-maker** (React 19 + react-konva, MIT) — создание планов, 0★, свежий.
- **charmlinn/blueprint3d-modern** (Three.js + Next.js) — 2D/3D планировщик, рисование с нуля.
- **softpython2884/IntelliPlan** (Next.js) — AI-планировщик помещений.
- **bugfishtm/floor-plan-designer** (jQuery, single HTML) — редактор планов для игр.
- **RobinWeitzel/floor-planner** (TS, Canvas, toJSON/loadJSON) — мелкий свежий, мало метрик;
  ближе к либе, но про рисование стен/мебели, не про маркеры поверх готового плана.

> Вывод: класс «готовый планировщик» нам не подходит — нужен canvas/interaction ДВИЖОК
> (Konva/Fabric) + своя логика приборов, либо SVG-путь (interact.js). Нишевые indoorjs /
> schema-editor — как референсы идей, не зависимости.

## skills.sh / MCP registry

- **skills.sh/trending** — только AI-агентские скиллы (видео/картинки/облачные обёртки
  runcomfy/doany-ai, grill-me и т.п.). JS-canvas-движков нет → источник нерелевантен задаче.
- **MCP registry** — про протокол-интеграции, не про фронтенд-движки → пропущен.

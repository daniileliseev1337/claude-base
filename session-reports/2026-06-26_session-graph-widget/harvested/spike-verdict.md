# Учение (спайк) — Fabric vs React Flow на эталонном графе сессии

Дата: 2026-06-26. Метод: один и тот же `ref-graph.json` (граф этой сессии, 12 узлов / 11 рёбер,
типы task/question/decision/step/assumption, уверенность confirmed/assumption/pending),
отрисован двумя движками, отрендерен в playwright (http://127.0.0.1:8765), факты — console + DOM + скриншоты.
Папка спайка: C:\Users\Public\widget-spike\ (ASCII — против MAX_PATH-граблей кириллицы).

## Факты

| Критерий | Fabric (proto-fabric.html) | React Flow (proto-reactflow.html) |
|---|---|---|
| Автономный HTML без сборки | ✅ CDN, 1 файл | ✅ **3 UMD-файла локально, 0 errors / 0 warnings** |
| fitView (весь граф в кадре) | ❌ 6 из 12 узлов, обрезан | ✅ 12/12, из коробки |
| Подсветка уверенности | видна только верхушка | ✅ вся карта (зел/жёлт/красн) |
| Рёбра | прямые линии, пересчёт — наш код | smoothstep, следуют сами |
| zoom / pan / MiniMap / Controls | ❌ нет (писать самим) | ✅ всё из коробки (DOM подтвердил) |
| Визуал узла | canvas-рисование | ✅ произвольный HTML/CSS |
| Объём нашего кода | ~95 стр, треть — механика | ~80 стр, механики ~0 |

DOM-проверка RF: nodes=12, edges=11, minimap=true, controls=true, background=true.

## Выводы (оба меняют ранее сказанное — по факту)

1. **Страх «React Flow требует сборку» — ОПРОВЕРГНУТ эмпирически.** UMD-путь (react@18 umd +
   react-dom umd + reactflow@11 umd, всё локальными файлами) даёт автономный HTML без bundler.
   Shell = папка с 3 .js + .html. Это снимает главный аргумент против React Flow.
   (NB: спайк на reactflow@11 UMD; v12 @xyflow/react — основной дистрибутив ESM, UMD под вопросом —
   проверить при фиксации, либо остаться на v11 UMD, либо собрать v12 shell разово через vite.)

2. **При равном коде React Flow даёт кратно больше.** Fabric: треть кода — механика, и всё равно
   нет fit/zoom/minimap → большой граф обрезается. React Flow: механики 0, fit/zoom/pan/MiniMap/
   Controls бесплатно, весь граф + цветовая карта рисков виден сразу.

## Рекомендация

- **Лёгкий «Сверка» → mermaid** (согласовано ранее).
- **Тяжёлый «Карта сессии» → React Flow** (UMD shell + `session-graph.json`, который эмитит Claude).
- Цена React Flow (React-стек освоить) реальна, но shell собирается/копируется ОДИН раз → «тяжело
  в учении, легко в бою»: дальше Claude каждую сессию льёт только JSON.

## Артефакты
- C:\Users\Public\widget-spike\{ref-graph.json, proto-fabric.html, proto-reactflow.html, + 5 либ}
- Скриншоты: C:\Users\Даниил ПК\shot-fabric.png, shot-reactflow.png

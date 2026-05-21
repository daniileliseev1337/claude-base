# Направление 2. Open-source генераторы (text → slides)

Цель: «текст лекции в Markdown → красивые слайды», локально, без облаков, экспорт желателен .pptx.

## Сравнительная таблица

| # | Инструмент | Repo | Stars | Last release | License | Сильные стороны | Минусы | Экспорт PPTX | Кириллица |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Slidev** | slidevjs/slidev | **46.6k** | v52.15.2 (May 2026, активный) | MIT | Markdown + Vue components, code highlighting, presenter notes, drawing/zoom, темы; есть русская документация; огромное сообщество | Vue-стек для красивых тем требует JS-навыков; .pptx экспортирует **как картинки** (текст невыбираемый) | да (PDF, PNG, PPTX) — но pptx = raster slides | да, через CSS @font-face можно подключить любой шрифт |
| 2 | **Marp** | marp-team/marp + marp-cli | **11.8k** (core repo) | marp-cli v4.4.0 (май 2025; основной репо обновлялся в 2025-26) | MIT | Самый простой markdown, минимум настройки, **CLI экспорт без браузера**, отлично для шаблонных корпоративных слайдов; есть VS Code extension | Меньше «вау-эффектов» чем Slidev; .pptx тоже **raster** (картинки) | да (HTML, PDF, PPTX, PNG) — pptx raster | да, через CSS |
| 3 | **reveal.js** | hakimel/reveal.js | **71.3k** | активный 2026 | MIT | Самый известный, browser-native, nested slides, LaTeX, Markdown-плагин | **PPTX из коробки НЕТ** (только PDF + HTML); JS-настройка сложнее markdown-инструментов | нет (только PDF/HTML) | да |
| 4 | **Spectacle** | FormidableLabs/spectacle | **10.1k** | spectacle@10.2.3 (окт 2025) | MIT | React/JSX, для разработчиков знающих React, live code demos | Не markdown — JSX-синтаксис; нет .pptx; нужен React-сетап | нет | да |
| 5 | **slidev2pptx** (доп.) | zhangyu94/slidev2pptx | малый | — | MIT | Конвертер Slidev → editable PPTX (не raster), вытаскивает текст | Экспериментальный, не для production; работает только со Slidev | да (с текстом!) | да |

## Что отсек

- **mdx-deck** — заброшен (~2 года без коммитов на момент проверки), не годится.
- **remark** (gnab/remark) — жив, но фичей мало, нет нативного .pptx, проигрывает Marp по всем параметрам.
- **eagle-html-slides** — нишевый, малое сообщество, не нашёл активной разработки в 2026.

## Ключевой нюанс по PPTX из markdown-инструментов

И Slidev, и Marp экспортируют в .pptx **как растровые слайды** (каждый слайд = картинка внутри PowerPoint). Это значит:
- Финальный pptx **визуально идеален** (как видишь в браузере).
- Но **редактировать текст в PowerPoint нельзя** — только перерисовать слайд из markdown и переэкспортировать.
- Для лекции на 30 слайдов которая один раз готовится и потом просто показывается — это **нормально**.
- Если нужны живые правки текста прямо в PowerPoint после выгрузки — это **не подходит**, ищи `slidev2pptx` или используй Gamma/Kimi.

## РЕКОМЕНДУЮ

**Топ-1: Marp** — для задачи «лекция один раз, markdown как source-of-truth, показ через PDF или встроенный presenter» Marp оптимален: CLI экспорт работает offline без браузера, конфигурация в одном файле, шаблоны простые, MIT-лицензия чистая, активный (последний release май 2025), нет лишних JS-зависимостей. 11.8k stars при простоте — это здоровый показатель.

**Если хочется красивее и не пугает Vue: Slidev** — 46.6k stars и активные релизы каждые 1-2 недели говорят сами за себя. Тоже годится, но порог входа выше.

**Не рекомендую для этой задачи:** reveal.js (нет pptx), Spectacle (JSX, нет pptx) — они хороши для других задач (web-презентации, dev-talks), но не под «корпоративная лекция в PowerPoint».

## Источники

- [Slidev GitHub](https://github.com/slidevjs/slidev)
- [Marp GitHub](https://github.com/marp-team/marp)
- [marp-cli releases](https://github.com/marp-team/marp-cli/releases)
- [reveal.js GitHub](https://github.com/hakimel/reveal.js)
- [Spectacle GitHub](https://github.com/FormidableLabs/spectacle)
- [slidev2pptx (editable PPTX export)](https://github.com/zhangyu94/slidev2pptx)
- [PkgPulse сравнение Slidev/Marp/reveal.js 2026](https://www.pkgpulse.com/guides/slidev-vs-marp-vs-revealjs-code-first-presentations-2026)
- [DasRoot обзор markdown-инструментов 2026](https://dasroot.net/posts/2026/04/markdown-presentation-tools-marp-slidev-reveal-js/)

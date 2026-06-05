---
date: 2026-06-04
topic: autocad-mcp-harvest (Workflow fan-out)
status: completed
tool: Workflow (Opus 4.8) — первый реальный запуск в нашей практике
cost: 8 агентов, ~766K subagent-токенов, ~4.5 мин
---

# Harvest AutoCAD-инструментов под recreation-профиль (Workflow)

**Запрос пользователя:** используем неофициальный puran-water/autocad-mcp; точно ли изучили
всё и лучший ли он; предложение — улучшать его обучением + забирать полезное (пример:
luxaeterna333/ClaudeCAD). **Метод:** Workflow fan-out (scout свежего + deep-read 6 seed +
синтез). Прошлый harvest (15.05, 20 инструментов) устарел и был под другой сценарий.

## Главный вердикт

**Остаёмся на puran-water/autocad-mcp.** Из 11 разобранных кандидатов ни один не закрывает
все три наши оси (живой AutoCAD + фирменные динблоки + кириллица + recreation) одновременно.

**Находка scout (не было в harvest 15.05):** `prumputira/autocad-mcp` v5.0 — прямая эволюция
нашей же кодовой базы (те же 3 backend, **Apache-2.0**, 8→22 инструмента). Это не миграция,
а **cherry-pick** (общая родословная). Главный выигрыш — batch-инструменты.

**ClaudeCAD (ссылка пользователя): код брать НЕЛЬЗЯ** — лицензии нет (`license=null`),
встроена коммерческая лицензионная защита + привязка к их прокси `api.wellflow.dev`,
0 звёзд, 1 коммит. In-process .NET-плагин — другой класс. **Но методология — золото.**

## Что забрать в наш стек (по приоритету)

**P0 (прямой выигрыш под recreation):**
1. **batch-инструменты `draw_*_batch`** (prumputira) — −60-70% API-вызовов = наш главный
   bottleneck по токенам при сотнях примитивов. Cherry-pick кодом (Apache, общая база).
2. **multi-view 9-tile PDF препроцессинг** (ClaudeCAD-идея) — overview 1920px + 2×2
   квадранты (10% overlap) + 4 угловых deep-zoom под штамп. На нашей стороне в Python
   (pdf2image+crop). Бьёт в боль с подложками/штампами.
3. **capture_screenshot живого AutoCAD** (NCO-1986) — скрин реального ACAD точнее
   matplotlib-рендера ezdxf. Feedback-loop: нарисовал→заскринил→сверил→поправил.

**P1 (кириллица — наша больная зона):**
4. ⚠ **cp1251-fix в `file_ipc.py`** (EmptyKot) — сейчас fallback на **cp1252**, а нужен
   **cp1251**. Это фактический БАГ нашего сервера — зафиксировать в коде, не обходами.
5. **Lee Mac dynblock-LISP как `tools/`-слой** (EmptyKot) — `LM:setdynpropvalue` и др.
   Наш execute_lisp уже исполняет; положить готовый детерминированный слой (Karpathy «код в tools/»).
6. **LOGFILEMODE-стриминг отклика** (EmptyKot) — надёжный канал чтения вывода, дешевле скрина.

**P2 (методология, ортогонально backend):**
7. keyword pre-router + алиасы (Igualguana) — детерминированный обход LLM на частых командах.
8. канонический LISP-скелет (ClaudeCAD): `(_.UNDO _GROUP)`→`LAYER _M`→геометрия→`_END`+`ZOOM _E`;
   координаты `'(X Y)`; + safety-блоклист (`wblock/shell/startapp/vl-registry-write/quit`).
9. 5-фазный протокол + INVENTORY-таблица + two-pass self-verify (ClaudeCAD) → чек-лист под ОВ.
10. prompt caching системного промпта (стабильный блок методологии/норм/LISP-конвенций).

**P3 (точечное):** excel_export DWG (prumputira), selection() human-in-loop (EmptyKot),
VARIANT `VT_ARRAY|VT_R8` (референс COM-fallback), accoreconsole headless (moisesbritez92).

**НЕ брать (анти-паттерны):** graceful degradation extrude→box (молчаливая подмена геометрии);
regen после каждой сущности; ASCII-whitelist режущий кириллицу; regex-NLP вместо модели.

## Наши уникальные наработки (нет ни у кого из 11)

1. **Программное управление dyn-props динамических блоков** — НИ ОДИН кандидат не делает штатно.
2. **Кириллица end-to-end** (вход Unicode в коде / выход cp1251 файлом / vla-Open).
3. **PDFIMPORT-калибровка подложки** (units_per_mm по двум равным сегментам).
4. **Block+scale в правильном порядке.**
5. **focus-free dispatch (PostMessageW) + COM на полном AutoCAD через execute_lisp.**

**Главный риск:** наш COM-сценарий держится на `execute_lisp` (README puran-water заявляет
LT без COM) → регресс upstream опасен → **держать вендор-снапшот + тесты COM-пути; cherry-pick
из prumputira (Apache) вместо слепого следования upstream puran-water.**

## Внедрено в базу

- Этот отчёт (полный synth).
- `reference_acad_ov_dwg_recreation` — добавлен раздел «Заимствования (backlog по приоритету)».
- Workflow-инструмент: первый боевой запуск; reference_workflow_tool пополнить кейсом.

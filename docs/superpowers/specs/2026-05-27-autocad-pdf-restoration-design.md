# AutoCAD-based PDF Restoration Workflow — Design Spec

**Дата:** 2026-05-27
**Статус:** Draft, ожидает review пользователя
**Автор:** Claude (DANIILPC) после консультации с пользователем
**Контекст-сессия:** `2026-05-27_pdf-editing-methodology-fix`

---

## TL;DR

Переходим с **PDF content-stream surgery** (через `pikepdf` + `PyMuPDF`) на **AutoCAD round-trip** для восстановления испорченных проектных PDF (legacy без исходных DWG). Pipeline: `PDFIMPORT` → layer/entity cleanup → вставка штамп-блока с атрибутами → `PLOT to PDF`. Результат — чистый vector PDF + бонусом DWG/DXF исходник на будущее.

PDF surgery остаётся как fallback для случаев когда AutoCAD недоступен или PDFIMPORT даёт мусор.

---

## Контекст: почему уходим от PDF surgery

### Что было пройдено в сессии 2026-05-27

Испытуемый файл `Desktop\Страницы_из_ПСИ_158_ОБ_ИОС1_5_Том_ПД_сводный_BACKUP_20260522_150437.pdf` (1 стр, A0, ~2.3 МБ) — испорчен 4-мя слоями накладывающихся штампов из прошлых попыток overlay-редактирования.

11 итераций surgery (v1-v11) показали:

| Подход | Результат | Проблема |
|---|---|---|
| **clip-path** (pikepdf, v2-v3) | Визуально чистый, но в editor видна selectable "Объект Фигура" | Контент физически остаётся, не удалён |
| **apply_redactions** (PyMuPDF, v4) | Удалил рамку, текст остался видим (наложения) | Не пробивает Form XObjects и fragmented streams |
| **q/Q group surgery** (pikepdf parse, v7-v8) | Удалил 1263 групп = большую часть | Не нашёл text objects (BT...ET) |
| **+ BT/ET text filter** (v9) | + 391 text object | Outer text без q/Q wrap остался |
| **+ path filter + Image removal** (v10-v11) | Зона визуально чистая | Под whiteout от прошлых Claude остался **оригинальный** штамп (Стадия Р, Лист 35) который я не видел при render |

**Корневая проблема:** PDF — формат для **печати**, не для редактирования. Editing на content-stream уровне работает против архитектуры формата. На сложных PDF с многослойными overlay-артефактами (как в нашем случае) **гарантированный** результат недостижим — всегда остаются скрытые слои которые невидны при render но появляются после ручной чистки в editor.

Параллельная сессия Claude на рабочем ПК (2026-05-22→2026-05-27) прошла **17 итераций v1-v17** через тот же путь и финализировала pipeline v12 — clip-path + redact graphics=2 + overlay. Это всё равно **скрытие**, не удаление; selectable artifacts остаются.

### Что меняем

AutoCAD создан **для редактирования** чертежей. После PDFIMPORT каждый объект становится **отдельным entity** на распознаваемом layer. Whiteout прямоугольники, старые штампы, наложения — всё видится **как отдельные объекты** и удаляется через select-by-property → erase. Штамп вставляется как **готовый block с атрибутами** — гарантированно корректно по ГОСТ 21.101.

---

## Текущее состояние AutoCAD MCP на DANIILPC

### Что установлено (из reference 2026-05-15 и cookbook 2026-05-21)

- **MCP сервер:** `puran-water/autocad-mcp v3.0`, 250★, MIT
- **Путь:** `~/.claude/mcp-servers/autocad-mcp/`
- **Регистрация в Claude Code:** `user scope`, env `AUTOCAD_MCP_BACKEND=auto`
- **8 групп tools:** `system` · `drawing` · `entity` · `layer` · `block` · `annotation` · `pid` · `view`
- **AutoCAD:** 2025 (пользователь подтвердил 2026-05-27)
- **AutoLISP плагины:** `mcp_dispatch.lsp` + `attribute_tools.lsp` загружены через APPLOAD + Startup Suite (сделано 2026-05-23)

### Два backend'а

| | `file_ipc` (нативный) | `ezdxf` (fallback) |
|---|---|---|
| AutoCAD нужен запущенным | **Да** | Нет (headless) |
| Формат файлов | **DWG напрямую** | Только DXF |
| `execute_lisp` (произвольный AutoLISP) | **Да** | Запрещён |
| `PDFIMPORT` команда | **Да** (через `execute_lisp`) | **Нет** (нет AutoCAD'а) |
| Screenshot через `view.get_screenshot` | PrintWindow (не отбирает фокус) | matplotlib |
| Channel | JSON в `C:\temp\*.json` + `PostMessageW(WM_CHAR)` к MDIClient | — |

**Для нашей задачи нужен `file_ipc`** — PDFIMPORT существует только в AutoCAD, не в ezdxf.

### Открытый вопрос (был незакрыт после 2026-05-23)

Не сделан финальный smoke-test что `system.status` возвращает `backend: file_ipc` (не `ezdxf`). Это **первый** шаг новой сессии.

---

## User Workflow — что должно быть открыто и что делает пользователь

### До старта сессии Claude

1. **Запустить AutoCAD 2025**
2. Открыть **любой DWG** (можно пустой `acadiso.dwg`)
3. Убедиться что в командной строке AutoCAD появилась строка о загрузке `mcp_dispatch.lsp` (Startup Suite автозагрузка). Если нет — APPLOAD руками.
4. Оставить AutoCAD **окно открытым** (можно свернуть, MCP использует PostMessage не требующий focus)

### Что делает пользователь во время работы Claude

- **Не закрывает** AutoCAD
- **Не редактирует** активный DWG руками (race condition с MCP командами)
- **Может смотреть** в AutoCAD как меняется чертёж — viewport видит изменения в реальном времени
- **Может отвечать** на вопросы Claude (если что-то нужно подтвердить — выбор шифра, расположение штампа)

### Что делает Claude

- Все операции через `mcp__autocad-mcp__*` tools — **не** через `win32com.client` напрямую (это workaround, см. cookbook урок)
- Никаких COM-скриптов в `Desktop\` — всё через MCP
- Промежуточные DWG сохраняются в **рабочую папку сессии** (`Desktop\_acad_session_<тема>\`), не на рабочем столе

### После окончания

- Финальный PDF (через `drawing.plot_pdf`) — в нужной целевой папке проекта
- DWG/DXF исходник — там же, для будущих правок без round-trip
- Лишние файлы сессии удаляются

---

## Technical Workflow — 5 этапов

### Этап 0: Preflight (smoke-test backend)

```
mcp__autocad-mcp__system  operation=status
```

Ожидаем `"backend": "file_ipc"`. Если `"ezdxf"` — диагностика:
- AutoCAD не запущен? → попросить пользователя запустить
- LISP плагин не загрузился? → проверить через `(c:mcp-dispatch)` в AutoCAD CLI вручную
- Env var не подхватился? → проверить `claude.json`

```
mcp__autocad-mcp__system  operation=execute_lisp  data={"code": "(+ 1 2)"}
```

Smoke-test execute_lisp — должен вернуть `3`.

### Этап 1: PDFIMPORT (PDF → DWG entities)

PDFIMPORT — встроенная команда AutoCAD 2017+, конвертирует **vector** PDF в DWG entities. Через AutoLISP:

```lisp
(command "-PDFIMPORT" "F" "<путь_к_pdf>" "1" "" "Y" "N" "Y" "1.0" "0,0" "0" "Y" "Y" "Y" "Y" "")
```

Параметры (порядок и значения для AutoCAD 2025, требует проверки на месте):
- `F` — File (не SCM Manager)
- `<путь>` — абсолютный путь к PDF
- `1` — номер страницы (мы тестируем 1)
- `""` — все слои
- `Y` — Vector geometry: yes
- `N` — Solid fills: no (не нужны нам — это могут быть whiteout заливки!)
- `Y` — TrueType text: yes
- `1.0` — масштаб
- `0,0` — insertion point
- `0` — rotation
- `Y/N` — другие параметры

**Open question:** точный синтаксис `-PDFIMPORT` в AutoCAD 2025. Возможно потребуется expression `(setvar ...)` для PDFIMPORTMODE / PDFIMPORTLAYERS перед командой. Проверить через `(help "PDFIMPORT")` в smoke.

### Этап 2: Анализ структуры импорта (read-only)

```
mcp__autocad-mcp__drawing  operation=info
mcp__autocad-mcp__layer    operation=list
mcp__autocad-mcp__entity   operation=count  layer=<each_layer>
```

Цель — понять как PDFIMPORT разложил содержимое:
- Все layers с именами и количеством entities
- Layer Solid fills (если опция была Y) — это могут быть whiteout прямоугольники
- Layer текста vs layer линий
- Есть ли уже named layers (если PDF имел OCG — маловероятно после pypdf)

### Этап 3: Cleanup (удаление штампа + whiteout + artifacts)

**3.1 — Удалить заведомо мусорные layers:**
```
mcp__autocad-mcp__layer  operation=freeze  data={"name": "PDF_Solid_Fills"}
# Если frozen layer не мешает — потом erase его entities
```

**3.2 — Выделить и удалить entities в зоне штампа:**

Bbox штампа известен из PROBE — в нашем тесте (2810, 0, 3360, 189) в PDF coords. После PDFIMPORT с insertion (0,0) scale 1.0 — те же координаты в DWG model space.

```
mcp__autocad-mcp__entity  operation=list  layer=<each>
# Получить список → отфильтровать по bbox → erase
```

Для каждого entity в zone:
```
mcp__autocad-mcp__entity  operation=erase  entity_id=<id>
```

**3.3 — Финальная проверка:**
```
mcp__autocad-mcp__system  operation=execute_lisp  data={"code": "(command \"_.ZOOM\" \"W\" \"2810,0\" \"3360,189\") (command \"_.SCREENSHOT\")"}
```

Визуальный контроль через `view.get_screenshot`.

### Этап 4: Вставить штамп-блок с атрибутами

```
mcp__autocad-mcp__block  operation=list
# Найти название штамп-блока в библиотеке (имя предоставит пользователь)

mcp__autocad-mcp__block  operation=insert_with_attributes  data={
  "name": "STAMP_GOST_21_101",
  "x": 2810, "y": 0,
  "scale": 1.0,
  "rotation": 0,
  "attributes": {
    "RAZRAB": "Самсонова",
    "PROVERIL": "Захаров",
    "NCONTR": "Березеско",
    "GIP": "Самсонова",
    "DATE": "06.26",
    "CIPHER": "ПСИ-158-ОБ-ИОС1.5",
    "STAGE": "П",
    "SHEET": "42",
    "TOTAL_SHEETS": "53",
    "PROJECT_NAME": "Строительство многопрофильной клиники ГБУЗ МО «Балашихинская областная больница»",
    "DRAWING_TITLE": "Архитектурное освещение фасадов. Групповые сети. Кровля. Блок 1"
  }
}
```

**Open question:** имена атрибутов в нашем block (`RAZRAB` / `Разраб.` / другие) — узнать от пользователя или через `block.get_attributes` на пилотном инсерте.

### Этап 5: PLOT to PDF

```
mcp__autocad-mcp__drawing  operation=plot_pdf  data={"path": "<целевая_папка>/<имя>.pdf"}
```

Также сохранить DWG для будущих правок:
```
mcp__autocad-mcp__drawing  operation=save  data={"path": "<целевая_папка>/<имя>.dwg"}
mcp__autocad-mcp__drawing  operation=save_as_dxf  data={"path": "<целевая_папка>/<имя>.dxf"}
```

---

## Acceptance Criteria

Финальный PDF должен:

1. ✅ Открываться в Adobe / Foxit без warnings
2. ✅ Не содержать selectable "Объектов Фигура" в зоне штампа
3. ✅ Содержать **один** штамп с актуальными подписантами (Самсонова/Захаров/Березеско/Самсонова, 06.26, ПСИ-158-ОБ-ИОС1.5, Стадия П, Лист 42, Листов 53)
4. ✅ Содержать **только один** экземпляр шифра (Ctrl+F найдёт 1 ПСИ-158, не 4)
5. ✅ Не содержать whiteout прямоугольников (Под селектированными objects не остаётся скрытого текста)
6. ✅ Чертёж (схема, размеры, легенда, штриховка) — нетронут
7. ✅ Vector quality (не растровый) — текст searchable через Ctrl+F, размеры точные

Тестовый случай: испытуемый PDF Балашиха backup.

---

## Open Questions (до старта реализации)

1. **PDFIMPORT синтаксис в AutoCAD 2025** — точные параметры командной строки. Проверить через `(help "PDFIMPORT")` или эмпирически на пилотном файле.

2. **Solid fills option** — `Y` или `N`? Если `Y` — whiteout прямоугольники станут entities и их можно удалить. Если `N` — они потеряются при импорте, но и любой legitimate solid hatch на чертеже тоже. Эмпирически: для нашего испытуемого PDF попробовать оба варианта на копиях.

3. **Качество vectorization текста** — TrueType text=Y, но AutoCAD может представить текст как path (если шрифт не embedded и не subsetted). Эмпирически проверить на ПСИ-158 markers.

4. **Layer naming в PDFIMPORT** — AutoCAD создаёт layers `PDF_<color>_<linetype>` или подобные. Возможно нужна вручная стратегия фильтрации.

5. **Имя штамп-блока + имена атрибутов** — пользователь предоставит путь и название блока в DWG библиотеке.

6. **Headless mode для batch 53 листов** — после успешного теста на 1 листе нужно решить как batch'ить (один AutoCAD instance, sequential PDFIMPORT 53 раза? Или Script Manager?). Это отдельная итерация после MVP.

---

## Тестовый случай — Pilot

**Файл:** `Desktop\Страницы_из_ПСИ_158_ОБ_ИОС1_5_Том_ПД_сводный_BACKUP_20260522_150437.pdf` (испытуемый, 1 страница A0)

**Шаги:**
1. Preflight (`system status` → file_ipc)
2. PDFIMPORT на пустой DWG, посмотреть результат через screenshot
3. **Контрольная точка с пользователем** — оценить качество vectorization
4. Если ОК — cleanup + block insert
5. PLOT to PDF в `Desktop\_acad_session_pilot\result.pdf`
6. Adobe-test result vs испытуемый

**Не делаем сразу batch на 53 листа** — только 1 лист как proof of concept.

---

## Что станет результатом сессии

Если pilot успешен:

1. **Skill** `~/.claude/skills/acad-pdf-restoration/` — методология workflow с примерами AutoLISP команд
2. **Chain** `chain:acad-pdf-restoration` в `~/.claude/chains/` — если pipeline стабилизируется в 4-5 этапов
3. **Memory** `feedback_acad_pdfimport_<тема>.md` — конкретные параметры PDFIMPORT которые сработали
4. **Anti-patterns** A11.* категория "AutoCAD round-trip" — для типичных ошибок (Solid fills, шрифты, layer naming)
5. **Anti-patterns** A7.6-7.8 из surgery опыта (Y-инверсия PyMuPDF, clip-path vs delete, apply_redactions не пробивает Form XObjects) — записать **отдельно** как «уроки кружного пути, чтобы следующий Claude не повторил»

Если pilot провален:

1. Документировать причину в `session-reports/2026-05-27_pdf-editing-methodology-fix/report.md`
2. Откатиться на pipeline v11 (PDF surgery) как best-effort fallback
3. Эскалация пользователю — рассмотреть Hurricane / Lee Mac UpdateTitleBlock (требуют DWG исходников, у нас их нет)

---

## Связанные

- [[2026-05-21_acad-mcp-hovs-tables]] — предыдущая сессия с AutoCAD MCP (заполнение таблиц)
- [[2026-05-21_acad-com-cookbook]] — cookbook AutoCAD COM (как fallback)
- [[reference-autocad-mcp]] — installation reference
- [[2026-05-22_ahp-stamp-overlay]] (feedback с рабочего ПК) — провал PDF overlay
- [[2026-05-27_ahp-balashiha-replies-v2-pipeline]] (feedback с рабочего ПК) — pipeline v12 PDF surgery
- harvested round-1/2/3 — TOP-инструменты PDF editing (всё остаётся актуальным для legacy сценариев)

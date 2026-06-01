# Handoff: AutoCAD MCP pilot — финал (insert + PLOT)

**Дата:** 2026-05-28
**Контекст:** Продолжение из сессии 2026-05-27_pdf-editing-methodology-fix → 2026-05-28 pilot

## TL;DR для нового Claude

PDF surgery провалился за 11 итераций. AutoCAD MCP workflow — **PDFIMPORT + ssget _C + erase** — очистил зону штампа от 3 наложенных копий + whiteout **за 1 итерацию**. Pilot DWG сохранён в `C:/temp/pilot_cleaned.dwg` + `Desktop\_acad_session_pilot\pilot_cleaned.dwg`. Осталось: insert штамп-блок + PLOT to PDF.

## Что готово

| Файл | Где |
|---|---|
| `pilot_cleaned.dwg` (6.6 МБ) | `C:/temp/` и `Desktop\_acad_session_pilot\` |
| `pilot_input.pdf` (исходный backup, 2.3 МБ) | `C:/temp/` |
| `stamps_lib.dwg` (штамп-библиотека, 274 КБ) | `C:/temp/` и `Desktop\Оформление\Листы со штампами.dwg` |
| Spec | `~/.claude/docs/superpowers/specs/2026-05-27-autocad-pdf-restoration-design.md` |

## Что осталось

1. **Pivot к stamps_lib.dwg.** В текущей AutoCAD-сессии оба DWG открыты, но active = `pilot_cleaned.dwg`. Через MCP `vla-activate` НЕ переключает active document (COM-ограничение). Решения:
   - **Простое:** пользователь сам нажимает на вкладку `stamps_lib.dwg` в AutoCAD
   - **Программное:** перезапустить AutoCAD с только stamps_lib.dwg → `system.init` → block.list
2. **Узнать имя штамп-блока** через `block list` после переключения. Возможно блоков нет (DWG = просто список нарисованных листов с штампами) — тогда придётся **скопировать штамп вручную** через AutoCAD (выделить → Ctrl+C with base point → Ctrl+V в pilot).
3. **Insert + attribute values** актуальные (из отчёта v12 с рабочего ПК):
   - Разраб: Самсонова 06.26
   - Проверил: Захаров 06.26
   - Н.контр: Березеско 06.26
   - ГИП: Самсонова 06.26
   - Шифр: ПСИ-158-ОБ-ИОС1.5
   - Стадия: П
   - Лист/Листов: уточнить (был p42 из 53)
   - Координаты вставки: **(985, 0) в мм** (правый нижний угол A0 1188×841 mm)
4. **PLOT to PDF** через `drawing.plot_pdf` или `execute_lisp (command "_-PLOT" ...)`. Сохранить в `_acad_session_pilot/pilot_result.pdf`.
5. **Adobe-test:** открыть pilot_result.pdf — должно быть **vector**, **без selectable artifacts**, с **одним правильным штампом**.

## Ключевые уроки (записать в anti-patterns + memory после успеха)

### Hard rules для AutoCAD MCP file_ipc
1. **`system.init` ОБЯЗАТЕЛЕН** после старта AutoCAD (MCP backend выбирается при старте MCP, не динамически)
2. **Кириллица в путях через JSON escape** → битый путь. Использовать ASCII paths: `C:/temp/...` копировать перед операцией
3. **Кириллица в именах layer/block** не проходит через MCP `layer/entity` tools с filter параметром. Использовать `ssget` с filter list: `(ssget "_X" (list (cons 8 "PDF _Геометрия")))`
4. **PDFIMPORT scale = 0.3528** (pt → mm). PDF MediaBox 3368×2384 pt = 1188×841 mm = A0
5. **`drawing.open` MCP** только открывает в фоне, **не переключает** active. Использовать `vla-open`. Active переключение через MCP **невозможно** — user interaction needed
6. **PDFIMPORT params для CAD-PDF с whiteout-загрязнением:** `PDFIMPORTLAYERS=0` (Use PDF layers), `PDFIMPORTMODE=0` (Insert as objects). Создаёт 3 слоя: `PDF _Геометрия`, `PDF _Сплошная заливка`, `PDF _Текст`. Whiteout прямоугольники → "Сплошная заливка". **НЕ freeze слой целиком** — там же легитимные solid fills (стрелки светильников). Использовать `ssget _C bbox_штампа` для локального удаления

### Сравнение методов
| | PDF surgery (pikepdf v1→v11) | AutoCAD MCP |
|---|---|---|
| Итераций | 11 | 1 |
| Время | ~3 часа | ~3 мин |
| Whiteout под штампом обнаружен | НЕТ | ДА |
| Selectable artifacts | оставались | нет |
| Качество | сомнительное | сохранено |

## Стартовый промпт для новой сессии

```
Привет. Продолжение pilot AutoCAD PDF restoration.

КОНТЕКСТ:
- PDF surgery 11 итераций провалился (см. spec)
- AutoCAD MCP file_ipc workflow за 1 итерацию очистил зону штампа от 3 наложенных копий + whiteout
- pilot_cleaned.dwg сохранён в C:/temp/ и Desktop\_acad_session_pilot\

ТЕКУЩЕЕ СОСТОЯНИЕ:
- AutoCAD 2025 запущен с двумя DWG: pilot_cleaned.dwg (active) + stamps_lib.dwg
- Backend file_ipc активен (после system.init)
- Зона штампа на pilot_cleaned.dwg пуста (985,0)-(1191,72) мм
- Чертёж и легенда — целы

ЧТО ДЕЛАЕМ:
1. Пользователь переключает active на stamps_lib.dwg в AutoCAD
2. block.list → если пусто, нужно копировать штамп через UI (Ctrl+C with base point)
3. Insert на pilot в (985, 0) с актуальными атрибутами (Самсонова, Захаров, Березеско, 06.26, ПСИ-158-ОБ-ИОС1.5, Стадия П)
4. PLOT to PDF → _acad_session_pilot/pilot_result.pdf
5. Adobe-test
6. После успеха: Skill acad-pdf-restoration + memory feedback

ФАЙЛЫ:
- ~/.claude/docs/superpowers/specs/2026-05-27-autocad-pdf-restoration-design.md (spec)
- ~/.claude/session-reports/2026-05-27_pdf-editing-methodology-fix/handoff-acad-pilot.md (этот handoff)

ПЕРВЫЙ ШАГ: STOP-процедура CLAUDE.md, потом system.status (должен быть file_ipc — если нет, system.init).
Если AutoCAD закрылся — открыть с pilot_cleaned.dwg.
```

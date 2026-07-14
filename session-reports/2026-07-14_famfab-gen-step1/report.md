# 2026-07-14 · DANIILPC · famfab/gen шаг №1: ядро + схема v2 + валидатор

## Что сделано
Трек C программы «Усиление Claude в Revit» (проект «Revit шаблон наш»), порядок работ №1
спека боеготовности — без живого Revit:
- `famfab/gen/gen_core.py` — двухрежимное ядро (IronPython 2.7 в Revit / CPython офлайн):
  Report (пустой=FAIL, атомарная запись + .done-семафор), read_json utf-8-sig,
  fresh_modules (кэш Routes), run_tx→reuse vf_core, regen-гейт (IsModifiable),
  save_as/close_doc + gc.collect.
- `gen_schema.json` (draft-07) + `gen_schema.md` — схема v2 «нашего диалекта»: мм,
  RU вне формул, секции по конвейеру Bones→Muscle→Skin→MEP→nested, gate-ожидания
  verify-слоя в том же JSON; ловушки зашиты by construction (роль RP service→not-a-ref,
  EQ только по RP, sketch_dims вместо solid-edge, коннекторы только у родителя и т.д.).
- `gen_validate.py` — 3 слоя: jsonschema-структура; линтер формул (гейт «молчаливого 0»,
  кириллица в теле формулы, гомоглифы по словам, дефисы, латинская «A» vs «А»,
  instance-распространение, text-конкатенация, юниты после числа, trig/if/деление);
  линтер ловушек (дим<2мм→align, ось↔вид, blend-копланарность, MEP-enum'ы Revit 2025,
  shared/спека вложений, каталог/lookup, gate-ссылки и gate.connectors).
- smoke: `cube_v2.json` (класс cube_etalon: каталог Size_Code/ShowCap S/M/L) и
  `tube_v2.json` (класс TUBE: revolve+sketch_dims, 2 duct-коннектора от D/2, каталог
  D/L/D2, lookup Flow/Power боевым паттерном `size_lookup(...)*1 м³/ч`).
- TDD: 67 pytest (все RED→GREEN), CLI-смоуки PASS, негативный смоук (3 инъекции→3 FAIL).

## Ревью-гейт (архитектура базы)
Код-ревьюер + auditor (оба sonnet, параллельно): **обе проверки NOT PASSED первой волной**.
- BLOCKER (auditor): в tube_v2 значения Flow были колонкой Pres источника
  (340/330/400 Па вместо 230/300/595 м³/ч) — сдвиг колонки при переносе из CSV.
- 6 MAJOR (код-ревью): KeyError на dim без ключа `a`; unit-unknown мёртв для кириллицы;
  gate.connectors не валидировался; PIPE_SYSTEMS без Supply/ReturnHydronic (сверено
  с API-докой); 3 обещанных в доке WARN не были реализованы; lookup-таблицы смоуков
  не были подключены формулами.
Фикс-волна по TDD (+11 тестов), сверка tube_v2↔SHUFT_TUBE_XL.csv детерминированным
скриптом → PASS. Точечная правка verify-слоя: `vf_checks.check_family_flags` обобщён
(итерирует любые ключи `flags`, поведение для зонтов идентично).

## Источники
Спек/рамка famfab 14.07; журнал проекта 13–14.07 (ловушки канала); verify-слой
(vf_core/vf_checks/vf_flex/vf_expected); скилл-оригинал revit-family-generator
(schema v0.1, README-provenance — не тронут); zonty_lib/skpt_lib;
battle/tube_formulas.txt (боевой синтаксис size_lookup); memory
`revit_family_editor_api_traps.md` (№1–31); ZONTY_data.md (№32–60).

## Споткнулся / уроки
- Пути из промпта вели в папку реворка базы — реальный проект нашёлся через git show
  коммита famfab (память: проект = «Revit шаблон наш»).
- В ТЗ дайджеста ловушек SKPT_data.md/TUBE_data.md значились как «файлы ловушек» —
  на деле это данные изделий; нумерованные ловушки живут в memory-файле. Субагент
  зафиксировал расхождение явно (правильное поведение).
- Перенос табличных данных из CSV руками = сдвиг колонки (Flow←Pres). Урок: любые
  числа из источника сверять скриптом, не глазами — сверка добавлена в процесс.
- Хвост verify: smoke_static.py не передаёт gate.expected_clusters в
  check_connectivity (тихий дефолт 1) — заметка на шаг 3–4.

## Продолжение той же сессии: ревью схемы + шаг 2
Владелец ответил на 4 вопроса (RU в формулах разрешён → гейт-WARN; mirrored_pair дефолт;
справочник gen_templates.json+override; оба режима флекса) — внесено по TDD (80 тестов).
Шаг 2 на живом стенде: gen_bones + gen_muscle + smoke_cube_bones → отчёт PASS
(4 RP, 7 параметров, 4 dims, 3 типа, флекс каркаса Width/Length 100→150→100 с точностью
0.0 мм). Урок стенда: имена центр-RP RU-шаблона 2025 = «По центру (Влево/Вправо)» /
«По центру (Вперед/Назад)», категория «Обобщенные модели» — НЕ «Центр (лево/право)»
из провенанса; первая итерация смоука упала на этом (KeyError → добавлен guard).
Inline-код через канал ломается на экранировании кавычек — только execfile файлом.

## Дальше
Шаг 3 (рекомендация: новым чатом): gen_skin (extrusion/revolve/sweep/blend/void,
видимость/материал/subcategory) + полный cube_v2 — гейт vf_checks на инстансе в
тест-проекте (8/8-класс). Затем шаг 4: gen_mep + tube_v2 + флекс by_key в vf_flex.

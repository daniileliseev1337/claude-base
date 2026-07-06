---
created: 2026-07-04
status: active
tags: [reference, revit, family-editor, ironpython, api, traps]
related:
  - [[reference_pyrevit]]
  - [[reference_revit_mcp]]
---

# Ловушки Revit Family Editor API (IronPython, Revit 2025) — накоплено на ZPVR

Загружать ДО написания скриптов генерации/правки семейств через Revit-Connector MCP.
Каждая ловушка стоила реальной ошибки/диалога на боевом семействе ZPVR CompactAir.

## Параметры и размеры

1. **formula-параметр НЕЛЬЗЯ привязать к размеру (labeled dimension).** Диалог
   «Параметр X невозможно изменить, так как определяется формулой». Dimension хочет
   driving, formula тоже driving → конфликт. РЕШЕНИЕ: для параметрики через размеры —
   driving-параметр БЕЗ формулы, значения задавать по типам (type values), не формулой.

2. **radial dimension ПОСТФАКТУМ на готовой окружности → 8 ошибок «Зависимости не
   выполняются» при смене типа.** Навесить radial+FamilyLabel на extrusion-circle с
   fixed-радиусом не тянет геометрию при flex. РЕШЕНИЕ: параметрику радиуса встраивать
   при СОЗДАНИИ — через REVOLVE (профиль-прямоугольник, dim высоты профиля = driving-param,
   ось на RP; alignment линий профиля к reference planes). Доказано на ZPVR: радиус
   патрубка follows D (200/250/315), позиция follows L и H.

3. **⚠ flex-тест через `fm.Set(param, val)` ПОРТИТ значения ТЕКУЩЕГО типа!** Каждый Set
   на текущем типе перезаписывает его type-value в каталоге. Симптом: после серии flex
   тип «450» вдруг имеет L=1350. RESET: flex ТОЛЬКО через `fm.CurrentType = ty` +
   Regenerate (смена типа не мутирует значения). Если нужен Set — восстановить значения
   типов после.

## ФОП (shared parameter file)

4. **Правка ФОП-текста: split('\r\n'), НЕ split('\n').** split('\n') на utf-16 тексте
   оставляет '\r' → при join получается '\r\r' → Revit «Error in readParamDatabase».
   Запись: `open(path,'wb').write(b'\xff\xfe' + text.encode('utf-16-le'))`. Бэкап перед правкой.

5. **Переименование параметра в ФОП не меняет GUID** — существующие семейства хранят
   старое имя по GUID; влияет только на будущие добавления. Миграция существующих — отдельно.

## Кириллица и окружение

6. **Кириллица в литералах execute_revit_code ломается (IronPython latin-1).** Русские
   значения (наименование, материал, ед.изм) — через bridge-файлы utf-8 + `codecs.open(f,'r','utf-8')`.
   Имена файлов шаблонов (.rft кириллицей) — тоже из файла. ASCII-путь к проекту — junction.

7. **Revit-Connector: инструменты DEFERRED** — не «мертвы», а не загружены. Оживлять
   `ToolSearch select:mcp__Revit-Connector__execute_revit_code,...` после каждого реконнекта.
   Реконнект закрывает документы — SaveAs .rfa на диск СРАЗУ после каждого этапа.
   HTTP-обход (POST /execute_code/) — костыль, НЕ нужен.

## Геометрия / коннекторы

8. **Duct-коннектор: ассоциировать CONNECTOR_DIAMETER→D** (RADIUS ассоциировать нельзя).
   `ConnectorElement.CreateDuctConnector(doc, Mechanical.DuctSystemType.Fitting, ConnectorProfileType.Round, face.Reference)`.
   Pipe: `CreatePipeConnector(doc, Plumbing.PipeSystemType.SupplyHydronic/ReturnHydronic, ref)`.
   Electrical: `CreateElectricalConnector(doc, Electrical.ElectricalSystemType.PowerBalanced, ref)`,
   привязка RBS_ELEC_VOLTAGE / RBS_ELEC_APPARENT_LOAD → ADSK.

9. **Видимость по параметру:** `el.get_Parameter(BuiltInParameter.IS_VISIBLE_PARAM)` →
   `fm.AssociateElementParameterToFamilyParameter(vp, yesno_param)`. Работает (ZPVR: водяные
   патрубки visible = Heater_Water).

10. **safe transaction** (гасить диалоги): IFailuresPreprocessor.DeleteAllWarnings +
    SetForcedModalHandling(False) + SetClearAfterRollback(True). Иначе модальный диалог
    вешает MCP (connection closed).

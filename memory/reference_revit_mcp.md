# reference_revit_mcp — pyRevit MCP (Revit-Connector): паттерны и грабли

Канонический справочник по live-работе с Autodesk Revit через MCP `Revit-Connector`
(pyRevit Routes). Распространяется со всей базой. Локальная копия-удобство (авто-load при
работе в папке сервера) — `~/.claude/mcp-servers/revit-mcp-python/CLAUDE.md` (в git НЕ трекается).
Используется агентом [[pyrevit-engineer]]. Сервер в `mcp-manifest.json` (tier optional, needs_admin).

## Что это
Мост Claude Code → `main.py` (FastMCP) → pyRevit Routes (REST внутри Revit, `127.0.0.1:48884`)
→ Revit API. Ключевой инструмент `execute_revit_code` (IronPython 2.7 в контексте `doc`; доступны
`doc`/`uidoc`/`DB`/`revit`/`print`) + ~18 готовых tools (get_revit_model_info, list_levels,
list_revit_views, get_revit_view, list_families, place_family, color_splash, и др.).
Repo: github.com/revit-mcp/revit-mcp-python (MIT). Routes в draft, БЕЗ аутентификации.

## Установка/подключение (кратко; полно — post_install_note в манифесте)
Нужны Revit + pyRevit + admin. Шаги в Revit UI (за пользователем): Extensions → «MCP Server for
Revit Python» → Install+Enable; Settings → Routes → on; `%APPDATA%\pyRevit\pyRevit_config.ini`
секция `[routes]`: `server_host="127.0.0.1"`, `server_port=48884` (по умолчанию 0.0.0.0 — небезопасно);
pyRevit Reload; проверка `http://127.0.0.1:48884/revit_mcp/status/`; restart Claude Code.

## Грабли и паттерны (ОБЯЗАТЕЛЬНО при live-работе)

**Кириллица.** IronPython 2.7 парсит exec-исходник как latin-1 (объявление `# coding` игнорится) →
прямые литералы `u"Текст"` ломаются (кракозябры `ÐÐ¾Ð·...`). Хелпер (идемпотентный — `str`/`unicode`
в IronPython это одно, повторный `.decode` падает):
```python
def u(s):
    try: return s.decode("utf-8")
    except Exception: return s
```
Оборачивать им ВСЕ русские литералы. Данные из Revit (`doc.Title`, имена семейств) корректны сами.

**safe_tx — транзакция с гашением диалогов.** Модальный диалог вешает Routes-поток (таймаут 60с,
запрос «зависает»). Обёртка:
```python
class Swallow(DB.IFailuresPreprocessor):
    def PreprocessFailures(self, fa):
        fa.DeleteAllWarnings(); return DB.FailureProcessingResult.Continue
def safe_tx(name, fn):
    t = DB.Transaction(doc, name); t.Start()
    fo = t.GetFailureHandlingOptions(); fo.SetForcedModalHandling(False)
    fo.SetFailuresPreprocessor(Swallow()); fo.SetClearAfterRollback(True)
    t.SetFailureHandlingOptions(fo)
    try: fn(); t.Commit(); return "ok"
    except Exception as e:
        if t.HasStarted() and not t.HasEnded(): t.RollBack()
        return "err: " + str(e)
```

**Read-only ADSK-параметры.** Электрические/тепловые ADSK-параметры (фазы, мощности) часто
формульные/из каталога семейства → `IsReadOnly=True`, через API не записать, только правкой rfa.
Проверять `p.IsReadOnly` до записи. Обозначение модели в спеках обычно в `ADSK_Марка` /
«Модель сборочной единицы» (редактируемые), не в имени типа Revit.

**Имя типа элемента.** Читать/писать `DB.Element.Name.__get__(et)` / `et.Name = ...`;
`getattr(et,'Name','?')` может вернуть default. Внимание: выноски/спеки часто читают НЕ имя типа,
а параметр (`ADSK_Марка`) — менять надо его.

**Спеки.** У `ViewSchedule` нет `TEXT_FONT`. Ячейки: `TableSectionData.GetTableCellStyle(r,c)` /
`SetCellStyle`. СКРЫТЫЕ колонки сдвигают индексы — `GetCellText(sec,r,c)` нумерует ТОЛЬКО видимые,
а `Definition.GetField(i)` — все; строить порядок видимых по `IsHidden`, иначе перепутаешь поля
(реальный случай: принял `ADSK_Масса` за `ADSK_Количество`). Ручные таблицы (ХОВС) хранят данные в
секции `Header`, не `Body`. `SetCellText` на теле стандартного расписания запрещён (значения — из
параметров элементов).

**Шрифты — 3 уровня** (унификация, напр. «GOST Common»):
1. Типы: `TextNoteType`/`DimensionType`/`SpotDimensionType` — `BuiltInParameter.TEXT_FONT`.
2. Ячейки спек — через `TableCellStyle.FontName` (`GetCellStyleOverrideOptions().Font=True`).
3. ВНУТРИ семейств: `doc.EditFamily(fam)` → в famdoc сменить `TextNoteType.TEXT_FONT` → `fdoc.LoadFamily(doc, opt)` → `fdoc.Close(False)`.
   `IFamilyLoadOptions` (out-параметры через `.Value`):
   `class FamOpt(DB.IFamilyLoadOptions): def OnFamilyFound(self,fu,ov): ov.Value=True; return True` (+ `OnSharedFamilyFound` с `src.Value=DB.FamilySource.Family`).
   EditFamily/LoadFamily МЕДЛЕННЫЕ → батчами по 3-6 (иначе таймаут 60с; ответы могут
   рассинхрониться — отправить уникальный `print`-маркер для пересинхрона). Системные «Ведомости
   изменений» — шрифт в семействе «Форма»/штампа.

**get_revit_view** не находит виды с кириллическими именами (теряется кодировка параметра) →
временно переименовать вид в ASCII (в транзакции) → отрендерить → вернуть имя. Рендерит ТОЛЬКО
модельные виды (не листы). Рендер pdf-mcp/PyMuPDF garbлит спец-шрифты (GOST type в таблицах) —
таблицы читать через API, схемы/планы визуально ок.

**Аннотации — ОБЯЗАТЕЛЬНЫЙ визуальный контроль.** После add/move выноски/текста — отрендерить и
посмотреть глазами; вслепую по координатам ставить нельзя (позиция выходит неудачной). Одна
`TextNote` может иметь НЕСКОЛЬКО leaders (одна надпись → 2+ одинаковых элемента) — при анализе
«есть ли выноска» брать ВСЕ `tn.GetLeaders()`, не `lds[0]`, иначе добавишь дубль.

**Листы/штамп.** «Листов» (общее число) — глобальный параметр (напр. «Кол-во листов»), поле штампа
`ADSK_Штамп_Количество листов` read-only подвязано к нему → менять глобальный, обновятся все листы.
Экспорт листов в PDF: `doc.Export(folder, ids, PDFExportOptions())` — путь только ASCII
(кириллица в литерале пути ломается; брать `System.IO.Path.GetTempPath()`).

**Боевые модели.** Routes без аутентификации; работать по копии, правки подтверждать, после —
предложить save/sync. Финальная приёмка поведения — на реальной модели (даже при live-MCP: до/после).

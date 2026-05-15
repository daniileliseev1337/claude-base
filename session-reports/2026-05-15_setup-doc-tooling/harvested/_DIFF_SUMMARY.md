# Diff-tools harvest — итог 2026-05-15

Цель: 2-5 готовых инструментов для сравнения версий .docx / .xlsx / .pdf
с покрытием всех трёх форматов хотя бы одним инструментом.

## Сводная таблица

| Инструмент | Stars | Last commit | License | Формат | Тип | Diff-уровень |
|---|---|---|---|---|---|---|
| **adeu** | 75 | 2026-05-15 | MIT | docx | MCP + SDK + CLI | структурный + native Track Changes |
| **redlines** | 156 | 2025-11-24 | MIT | text (any extract) | Python lib | текстовый, MD/HTML/JSON output |
| **ExcelCompare** | 850 | 2022-04-22 | MIT | xls/xlsx/xlsm/ods | Java CLI | cell-level, formula-aware |
| **diff-pdf** | 4 200 | 2026-03-28 | GPL-2.0 | pdf | C++ CLI | визуальный, попиксельно, output PDF |
| **diff-pdf-visually** | 73 | 2025-04-01 | Apache/MIT | pdf | Python lib + CLI | визуальный, regression-check |

## Покрытие форматов

- **DOCX:** adeu (1й приоритет, MCP+native Track Changes) + redlines (fallback на текстовый diff после extract через word MCP).
- **XLSX:** ExcelCompare (с флагом — Java + старый). **Альтернатива дешевле:** дотянуть наш `excel-helper` скилл openpyxl-логикой формула-diff. Решает пользователь.
- **PDF:** diff-pdf (визуальный, через CLI/subprocess; GPL допустим как внешний бинарь) + pdf-mcp (уже есть в стеке) для текстового слоя. diff-pdf-visually — запасной Python API.

## Рекомендация (топ-2 для немедленного подключения)

### 1. **adeu** — для docx
Закрывает самую частую и сложную задачу: правка/сравнение Word с сохранением
форматирования и нативными Track Changes. Это MCP-сервер — встаёт в наш
стек без обвязки:
```
uvx adeu init
```
Дополняет существующий `word` MCP (тот — на запись/чтение, этот — на безопасный
редактор + diff).

### 2. **diff-pdf** — для pdf
Закрывает визуальный diff PDF (то, что pdf-mcp **не умеет** — он только текст
и метаданные). Установка через Chocolatey, вызов из Claude Code subprocess'ом:
```
choco install diff-pdf
diff-pdf --output-diff=diff.pdf v1.pdf v2.pdf
```
GPL допустим **только как внешний бинарь**, код не копируем.

### XLSX — отдельно
Для xlsx **не рекомендую тащить ExcelCompare** на этом этапе:
- Java-зависимость на Windows без админ-прав = инсталляционный геморрой.
- Проект заморожен с 2022.
- У нас уже есть `excel-helper` скилл + `excel` MCP — нарастить
  formula-diff поверх openpyxl дешевле, чем интегрировать чужой Java-CLI.

Поднимать ExcelCompare имеет смысл, **если** появится задача сравнить две
большие книги (>50 листов, тысячи формул), где наш скилл начнёт тормозить.

## Что НЕ берём (рассмотрены и отброшены)

- **Python-Redlines (JSv4)** — обёртка над .NET DLL OpenXmlPowerTools,
  тянет dotnet runtime. adeu решает то же чище.
- **docx-compare (Ignema)** — использует git-diff на распакованном docx XML;
  результаты «грязные» для непрограммистов.
- **pdf-diff (JoshData / serhack / jturner314)** — мелкие проекты, малая
  активность, перекрываются diff-pdf.
- **MCP diff-servers (diff-mcp / mcp-server-diff-*)** — это generic
  text-diff обёртки над `diff`/`difflib`, не специализированы под docx/xlsx/pdf.
  Если понадобится текст-diff внутри MCP — proще встроить вызов redlines.

## Открытые вопросы пользователю

1. Ставим **adeu** в основной MCP-стек (добавляем 9-й сервер к эталонным 8)
   или держим как «по запросу»?
2. По xlsx: дотягиваем `excel-helper` скилл или всё-таки ставим ExcelCompare?
3. diff-pdf через `choco install` — у вас Chocolatey уже установлен или
   качать ZIP с релизов?

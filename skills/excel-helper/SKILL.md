---
name: excel-helper
description: |
  Универсальная методология работы с Excel: чтение, запись, анализ формул,
  выявление расхождений между листами/файлами, валидация, сравнение версий.
  Подключается на любые задачи с .xlsx где требуется не просто "открой
  файл", а осмысленный анализ или правка.

  Триггеры:
  - "Excel", ".xlsx", ".xls", ".csv"
  - "формулы Excel", "анализ Excel", "валидация Excel"
  - "сравнить таблицы", "найди расхождения", "diff xlsx"
  - "сводная", "pivot", "summary"
  - "openpyxl", "pandas", "формула не считает"
  - "дубликаты", "уникальные значения"
  - "циркулярная ссылка", "#REF!", "#DIV/0", "#NAME?"
  - "условное форматирование", "conditional formatting"
---

# excel-helper

## Когда подключаться

Любая задача с `.xlsx` где нужно понять структуру, найти ошибки, сравнить, посчитать. Если просто «открой файл и покажи первую строку» — Read tool через MCP excel хватит, без скилла.

## Иерархия инструментов

| Задача | Инструмент | Заметка |
|--------|------------|---------|
| CRUD ячеек, листов, форматов | `excel-mcp-server` | Стандартный путь, через Claude напрямую |
| Анализ всего файла, агрегации | Python `openpyxl` | Когда нужны цикл/условия/перебор сотен строк |
| Сравнение двух файлов | Python `pandas` | DataFrame.compare() или merge + diff |
| Большие файлы (>100к строк) | Python `pandas` с `chunksize` или `polars` | openpyxl читает медленно |
| Чтение формул как текст vs значений | `openpyxl` с `data_only=False` (формулы) или `data_only=True` (значения) | По умолчанию формулы |
| Запись формул | excel-mcp поддерживает; openpyxl: `cell.value = "=SUM(A1:A10)"` | Excel пересчитает при открытии |

## Типовые задачи

### Найти расхождения между двумя файлами (pandas — табличный diff)

```python
import pandas as pd
df1 = pd.read_excel("v1.xlsx", sheet_name="Sheet1")
df2 = pd.read_excel("v2.xlsx", sheet_name="Sheet1")

# Если ключ — колонка "ID":
merged = df1.merge(df2, on="ID", how="outer", indicator=True, suffixes=("_v1", "_v2"))
print(merged[merged["_merge"] != "both"])  # что добавилось/удалилось

# Расхождения в общих строках:
common = merged[merged["_merge"] == "both"]
for col in [c for c in df1.columns if c != "ID"]:
    diff = common[common[f"{col}_v1"] != common[f"{col}_v2"]]
    if not diff.empty:
        print(f"\n=== {col} ===")
        print(diff[["ID", f"{col}_v1", f"{col}_v2"]])
```

### Cell-by-cell diff с подсветкой в новом xlsx

Когда нужно **визуально** показать что изменилось — итерация по совпадающим листам, цветовая подсветка изменённых ячеек, добавленных строк, удалённых строк. Структура листов считается одинаковой.

```python
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from copy import copy

YELLOW = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")  # изменилось
GREEN  = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # добавилось (есть в v2, нет в v1)
RED    = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # удалилось (есть в v1, нет в v2)

def cell_diff(v1_path: str, v2_path: str, out_path: str) -> dict:
    """
    Открывает v2 как базу (он "новый"), сравнивает с v1, заливает изменённые ячейки.
    Возвращает счётчики по типам различий.
    """
    wb1 = load_workbook(v1_path, data_only=False)
    wb2 = load_workbook(v2_path, data_only=False)
    stats = {"changed": 0, "added": 0, "removed": 0, "sheets_only_in_v2": [], "sheets_only_in_v1": []}

    for name in wb2.sheetnames:
        if name not in wb1.sheetnames:
            stats["sheets_only_in_v2"].append(name)
            continue
        ws1, ws2 = wb1[name], wb2[name]
        max_row = max(ws1.max_row, ws2.max_row)
        max_col = max(ws1.max_column, ws2.max_column)
        for r in range(1, max_row + 1):
            for c in range(1, max_col + 1):
                v1 = ws1.cell(r, c).value
                v2 = ws2.cell(r, c).value
                if v1 == v2:
                    continue
                target = ws2.cell(r, c)
                if v1 is None and v2 is not None:
                    target.fill = GREEN
                    stats["added"] += 1
                elif v1 is not None and v2 is None:
                    target.fill = RED
                    target.value = f"[DELETED] was: {v1}"
                    stats["removed"] += 1
                else:
                    target.fill = YELLOW
                    stats["changed"] += 1

    for name in wb1.sheetnames:
        if name not in wb2.sheetnames:
            stats["sheets_only_in_v1"].append(name)

    wb2.save(out_path)
    return stats
```

**Применение:**
```python
stats = cell_diff("v1.xlsx", "v2.xlsx", "diff_highlighted.xlsx")
print(stats)  # {'changed': 12, 'added': 3, 'removed': 1, ...}
```

### Formula-level diff (формулы vs значения)

Когда расхождение в **самой формуле**, а не в её значении — стандартный `data_only=True` это скроет. Сравниваем формулы как текст, отдельно от cached-значений.

```python
from openpyxl import load_workbook

def formula_diff(v1_path: str, v2_path: str) -> list:
    """
    Возвращает список расхождений в формулах: [(sheet, A1, formula_v1, formula_v2), ...].
    Только те ячейки, где хотя бы в одном из файлов есть формула.
    """
    wb1 = load_workbook(v1_path, data_only=False)
    wb2 = load_workbook(v2_path, data_only=False)
    out = []
    for name in set(wb1.sheetnames) & set(wb2.sheetnames):
        ws1, ws2 = wb1[name], wb2[name]
        for row in ws2.iter_rows():
            for cell in row:
                f2 = cell.value if isinstance(cell.value, str) and cell.value.startswith("=") else None
                f1_val = ws1.cell(cell.row, cell.column).value
                f1 = f1_val if isinstance(f1_val, str) and f1_val.startswith("=") else None
                if f1 != f2 and (f1 or f2):
                    out.append((name, cell.coordinate, f1, f2))
    return out

for sheet, coord, f1, f2 in formula_diff("v1.xlsx", "v2.xlsx"):
    print(f"{sheet}!{coord}:")
    print(f"  v1: {f1}")
    print(f"  v2: {f2}")
```

**Ловушка:** если ячейка в v1 содержит формулу `=SUM(A1:A10)` со значением `55`, а в v2 — просто число `55` (формула удалена, оставлено значение) — `formula_diff` это поймает (`f1` есть, `f2` нет). Это и есть нужное поведение: пользователь часто хочет знать, где формула "захардкожена" в значение.

### Валидация формул — найти #REF! / #DIV/0! / #NAME?

```python
from openpyxl import load_workbook
wb = load_workbook("file.xlsx", data_only=True)  # data_only=True вернёт CACHED значения
errors = []
for sheet in wb.sheetnames:
    ws = wb[sheet]
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and cell.value.startswith("#"):
                errors.append((sheet, cell.coordinate, cell.value))
for e in errors:
    print(f"{e[0]}!{e[1]}: {e[2]}")
```

**Важно**: чтобы Excel пересчитал и закэшировал значения, файл должен быть открыт и сохранён в Excel хотя бы один раз. Если файл создан Python — `data_only=True` вернёт `None` для формул.

### Найти дубликаты по ключу

```python
import pandas as pd
df = pd.read_excel("file.xlsx")
dups = df[df.duplicated(subset=["ID"], keep=False)]
print(dups.sort_values("ID"))
```

### Найти циркулярные ссылки

`openpyxl` напрямую их не флагует. Косвенный признак: в `data_only=True` mode значение ячейки `0` или `None`, а в `data_only=False` mode — формула, ссылающаяся (прямо или транзитивно) на саму себя. Простой эвристический поиск:

```python
import re
from openpyxl import load_workbook
wb = load_workbook("file.xlsx", data_only=False)
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith("="):
                # Самопрямая ссылка:
                if cell.coordinate in cell.value:
                    print(f"Self-ref: {ws.title}!{cell.coordinate} = {cell.value}")
```

### Условное форматирование (выделить ошибки)

`excel-mcp` это умеет. Через Python:

```python
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
wb = load_workbook("file.xlsx")
ws = wb["Sheet1"]
red = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")
for row in ws.iter_rows(min_row=2):
    for cell in row:
        if cell.value is None:
            cell.fill = red
wb.save("highlighted.xlsx")
```

## Ловушки

1. **Locale (русская)** — формулы хранятся английскими функциями (`SUM`, `IF`), а отображаются `СУММ`, `ЕСЛИ`. При записи через Python — пиши на английском, Excel сам переведёт.
2. **Десятичный разделитель** — в русской локали запятая, в файлах CSV. Pandas: `pd.read_csv(..., decimal=",")`.
3. **Кодировка CSV от 1С** — обычно `cp1251` (Windows-1251). Если получишь "Я€" вместо русских — `encoding="cp1251"`.
4. **Дата в Excel — это число** (с 1900-01-01 = 1). При сравнении дат в pandas из xlsx — конвертировать через `pd.to_datetime()`.
5. **Пустые ячейки vs `None` vs `0`** — openpyxl возвращает `None` для пустых, `pandas` — `NaN`. Не путать с `0`.
6. **Объединённые ячейки (merged)** — значение хранится только в верхней-левой ячейке диапазона; остальные `None`. Для итерации `for row in ws.iter_rows()` придётся unmerge или пробрасывать значение из якоря.
7. **Большие файлы** — `openpyxl` читает медленно (~1 сек на 10к строк). Для >100к строк — `pandas.read_excel` с движком `openpyxl` или `polars`.
8. **Запись через openpyxl стирает условное форматирование и сводные**, если их не загрузить с `keep_vba=True` и не пересохранить аккуратно. Лучше править через excel-mcp.

## Когда вызывать агента excel-validator

После любой правки Excel или перед сдачей файла заказчику — спавнить subagent `excel-validator`. Он проверит формулы (нет ли #REF! / #DIV/0!), типы данных по колонкам, дубликаты, расхождения с эталоном (если эталон передан), и выдаст отчёт со списком замечаний.

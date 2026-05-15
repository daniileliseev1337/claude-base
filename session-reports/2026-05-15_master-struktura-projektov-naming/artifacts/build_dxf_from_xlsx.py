"""
Генерация DXF-схемы ЛВС ПСИ-158 из xlsx-таблицы со 200 шкафами.
Структурная схема в формате AutoCAD: прямоугольники-шкафы с подписями,
группировка по объектам/блокам/этажам/сетям, цветовое кодирование сетей.

Открыть в AutoCAD / DraftSight / LibreCAD / любом DWG-вьювере.
"""
from pathlib import Path

import openpyxl
import ezdxf
from ezdxf import zoom

BASE = Path(r"C:\Users\Deliseev\Desktop\Здадчака")
XLSX = BASE / "Шкафы_ПСИ-158_v2_5сетей.xlsx"
OUT = BASE / "Структурная_схема_ПСИ-158_v2.dxf"

# Цвета AutoCAD Color Index (ACI) для сетей
NET_ACI = {
    "МИС": 5,   # blue
    "СБ":  1,   # red
    "ОП":  30,  # orange
    "СОТ": 3,   # green
    "СВН": 6,   # magenta/violet
}
NET_ORDER = ["МИС", "СБ", "ОП", "СОТ", "СВН"]

# Размеры
CELL_W = 28   # ширина прямоугольника шкафа
CELL_H = 14   # высота прямоугольника шкафа
GAP_X = 4     # зазор между шкафами в ряду
GAP_Y = 4     # зазор между рядами этажей
BLOCK_GAP = 16  # зазор между блоками
OBJECT_GAP = 60 # зазор между объектами

# Создаём DXF документ
doc = ezdxf.new(dxfversion="R2010", setup=True)
doc.layers.add(name="0_ОСНОВНОЙ", color=7)  # белый
doc.layers.add(name="1_ТЕКСТ",   color=7)
doc.layers.add(name="2_РАМКА",   color=8)   # серый
doc.layers.add(name="3_СВЯЗИ",   color=8)
for net, aci in NET_ACI.items():
    doc.layers.add(name=f"NET_{net}", color=aci)

msp = doc.modelspace()

# Читаем xlsx
wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb["Шкафы"]

rows = []
for r in ws.iter_rows(min_row=2, values_only=True):
    if not r or r[0] is None:
        continue
    rows.append({
        "n": r[0], "net": r[1], "object": r[2], "block": r[3],
        "floor": r[4], "room": r[5], "type": r[6],
        "new_name": r[7], "system_id": r[8],
        "old_name": r[9], "old_p_name": r[10],
        "status": r[11], "comment": r[12] or "",
    })
print(f"Прочитано шкафов: {len(rows)}")

# Группируем
def floor_to_int(s):
    if isinstance(s, int):
        return s
    s = str(s)
    if "Подвал" in s:
        return 0
    if "этаж" in s:
        try:
            return int(s.split()[0])
        except ValueError:
            return -1
    return -1

# Получим список объектов и блоков
objects = {}  # name -> set of blocks
for row in rows:
    objects.setdefault(row["object"], set()).add(str(row["block"]))

print("Объекты:", {k: sorted(v) for k, v in objects.items()})

# Помощник: рисуем шкаф (прямоугольник + текст)
def draw_cabinet(x, y, w, h, row):
    net = row["net"]
    name = row["new_name"]
    type_ = row["type"]
    layer = f"NET_{net}"

    # рамка
    poly = msp.add_lwpolyline(
        [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)],
        close=True, dxfattribs={"layer": layer, "color": NET_ACI[net]},
    )

    # заливка через solid hatch (опционально для ШГК)
    if type_ == "ШГК":
        hatch = msp.add_hatch(color=NET_ACI[net], dxfattribs={"layer": layer})
        hatch.paths.add_polyline_path(
            [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], is_closed=True
        )

    # подпись имени по центру
    txt_h = 1.6 if type_ == "ШД" else 2.0
    fc = 7 if type_ == "ШГК" else NET_ACI[net]
    t1 = msp.add_text(
        name,
        dxfattribs={"layer": "1_ТЕКСТ", "height": txt_h, "color": fc},
    )
    t1.set_placement((x + w/2, y + h - 3), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

    # помещение
    if row["room"]:
        t2 = msp.add_text(
            f"пом. {row['room']}",
            dxfattribs={"layer": "1_ТЕКСТ", "height": 1.1, "color": 8},
        )
        t2.set_placement((x + w/2, y + h/2 - 0.5), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

    # тип шкафа в углу
    t3 = msp.add_text(
        type_,
        dxfattribs={"layer": "1_ТЕКСТ", "height": 1.4, "color": fc},
    )
    t3.set_placement((x + 1.5, y + 1), align=ezdxf.enums.TextEntityAlignment.LEFT)

    return (x + w/2, y + h/2)  # центр шкафа

# Раскладываем
positions = {}  # new_name -> (x, y) центр

# === ГК ===
# 4 блока в ряд, в каждом блоке 5 сетей в ряд × этажи 0-9 сверху вниз
gk_x0 = 0
gk_y0 = 0

# колонки по блоку×сети
gk_blocks = ["ГК1", "ГК2", "ГК3", "ГК4"]
gk_col_w = 5 * (CELL_W + GAP_X)  # 5 сетей на блок

for bi, block in enumerate(gk_blocks):
    bx = gk_x0 + bi * (gk_col_w + BLOCK_GAP)
    # подпись блока сверху
    block_lbl = msp.add_text(
        f"Блок {block[-1]}",
        dxfattribs={"layer": "2_РАМКА", "height": 4, "color": 7},
    )
    block_lbl.set_placement(
        (bx + gk_col_w/2, gk_y0 + 11 * (CELL_H + GAP_Y) + 2),
        align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER,
    )
    # подписи сетей сверху колонок
    for ni, net in enumerate(NET_ORDER):
        nx = bx + ni * (CELL_W + GAP_X)
        net_lbl = msp.add_text(
            net,
            dxfattribs={"layer": f"NET_{net}", "height": 2.5, "color": NET_ACI[net]},
        )
        net_lbl.set_placement(
            (nx + CELL_W/2, gk_y0 + 10 * (CELL_H + GAP_Y) + 4),
            align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER,
        )

    for floor in range(0, 10):
        # этаж 6 для блока 4 — резервная серверная МИС, специальная
        # этаж 5-9 для блока 4 (кроме 6) — нет шкафов
        # этаж 0 Б2 - ШГК, не ШД
        for ni, net in enumerate(NET_ORDER):
            nx = bx + ni * (CELL_W + GAP_X)
            # этаж снизу вверх: подвал внизу, 9 этаж вверху
            ny = gk_y0 + floor * (CELL_H + GAP_Y)

            # найти шкаф
            found = None
            for r in rows:
                if (r["object"] == "ГК" and r["block"] == block
                        and floor_to_int(r["floor"]) == floor
                        and r["net"] == net):
                    found = r
                    break
            if found:
                cx, cy = draw_cabinet(nx, ny, CELL_W, CELL_H, found)
                positions[found["new_name"]] = (cx, cy)

    # подписи этажей слева
    for floor in range(0, 10):
        ny = gk_y0 + floor * (CELL_H + GAP_Y)
        lbl_text = "Подвал" if floor == 0 else f"{floor} этаж"
        msp.add_text(
            lbl_text,
            dxfattribs={"layer": "2_РАМКА", "height": 2, "color": 8},
        ).set_placement(
            (bx - 3, ny + CELL_H/2),
            align=ezdxf.enums.TextEntityAlignment.RIGHT,
        )

# Подпись ГК сверху
gk_total_w = 4 * gk_col_w + 3 * BLOCK_GAP
msp.add_text(
    "ГЛАВНЫЙ КОРПУС ЦРБ",
    dxfattribs={"layer": "0_ОСНОВНОЙ", "height": 7, "color": 7},
).set_placement(
    (gk_x0 + gk_total_w/2, gk_y0 + 11 * (CELL_H + GAP_Y) + 12),
    align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER,
)

# Рамка ГК
msp.add_lwpolyline(
    [
        (gk_x0 - 18, gk_y0 - 4),
        (gk_x0 + gk_total_w + 4, gk_y0 - 4),
        (gk_x0 + gk_total_w + 4, gk_y0 + 11 * (CELL_H + GAP_Y) + 8),
        (gk_x0 - 18, gk_y0 + 11 * (CELL_H + GAP_Y) + 8),
    ],
    close=True, dxfattribs={"layer": "2_РАМКА", "color": 8},
)

# === ПАК ===
pak_x0 = gk_x0 + gk_total_w + OBJECT_GAP
pak_nets = ["МИС", "СБ", "СОТ"]

msp.add_text(
    "ПАК",
    dxfattribs={"layer": "0_ОСНОВНОЙ", "height": 7, "color": 7},
).set_placement(
    (pak_x0 + len(pak_nets) * (CELL_W + GAP_X)/2,
     gk_y0 + 11 * (CELL_H + GAP_Y) + 12),
    align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER,
)

for ni, net in enumerate(pak_nets):
    nx = pak_x0 + ni * (CELL_W + GAP_X)
    msp.add_text(
        net,
        dxfattribs={"layer": f"NET_{net}", "height": 2.5, "color": NET_ACI[net]},
    ).set_placement(
        (nx + CELL_W/2, gk_y0 + 10 * (CELL_H + GAP_Y) + 4),
        align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER,
    )

for floor in [0, 2]:
    for ni, net in enumerate(pak_nets):
        nx = pak_x0 + ni * (CELL_W + GAP_X)
        ny = gk_y0 + floor * (CELL_H + GAP_Y)
        found = None
        for r in rows:
            if (r["object"] == "ПАК" and floor_to_int(r["floor"]) == floor
                    and r["net"] == net):
                found = r
                break
        if found:
            cx, cy = draw_cabinet(nx, ny, CELL_W, CELL_H, found)
            positions[found["new_name"]] = (cx, cy)

pak_total_w = len(pak_nets) * (CELL_W + GAP_X)
msp.add_lwpolyline(
    [
        (pak_x0 - 4, gk_y0 - 4),
        (pak_x0 + pak_total_w + 4, gk_y0 - 4),
        (pak_x0 + pak_total_w + 4, gk_y0 + 11 * (CELL_H + GAP_Y) + 8),
        (pak_x0 - 4, gk_y0 + 11 * (CELL_H + GAP_Y) + 8),
    ],
    close=True, dxfattribs={"layer": "2_РАМКА", "color": 8},
)

# === КПП + ПП ===
kpp_x0 = pak_x0 + pak_total_w + OBJECT_GAP
kpp_nets = ["СБ", "СОТ", "СВН"]
kpp_objects = ["КПП1", "КПП2", "КПП3", "КПП4", "КПП5", "ПП"]

msp.add_text(
    "КПП и Подземный паркинг",
    dxfattribs={"layer": "0_ОСНОВНОЙ", "height": 7, "color": 7},
).set_placement(
    (kpp_x0 + len(kpp_objects) * (CELL_W + GAP_X)/2,
     gk_y0 + 11 * (CELL_H + GAP_Y) + 12),
    align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER,
)

# каждый объект — столбец, в нём 3 сети (этажи не имеют значения, всё на 1 этаже)
for oi, obj in enumerate(kpp_objects):
    ox = kpp_x0 + oi * (CELL_W + GAP_X)
    # подпись объекта
    msp.add_text(
        obj,
        dxfattribs={"layer": "0_ОСНОВНОЙ", "height": 3, "color": 7},
    ).set_placement(
        (ox + CELL_W/2, gk_y0 + 10 * (CELL_H + GAP_Y) + 4),
        align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER,
    )

    for ni, net in enumerate(kpp_nets):
        ny = gk_y0 + (1 + ni) * (CELL_H + GAP_Y)
        found = None
        for r in rows:
            if r["object"] == obj and r["net"] == net:
                found = r
                break
        if found:
            cx, cy = draw_cabinet(ox, ny, CELL_W, CELL_H, found)
            positions[found["new_name"]] = (cx, cy)

kpp_total_w = len(kpp_objects) * (CELL_W + GAP_X)
msp.add_lwpolyline(
    [
        (kpp_x0 - 4, gk_y0 - 4),
        (kpp_x0 + kpp_total_w + 4, gk_y0 - 4),
        (kpp_x0 + kpp_total_w + 4, gk_y0 + 11 * (CELL_H + GAP_Y) + 8),
        (kpp_x0 - 4, gk_y0 + 11 * (CELL_H + GAP_Y) + 8),
    ],
    close=True, dxfattribs={"layer": "2_РАМКА", "color": 8},
)

# === Связи ШГК → ШД (тонкие линии по цвету сети) ===
shgk_pos = {}
shd_list = []
for row in rows:
    pos = positions.get(row["new_name"])
    if not pos:
        continue
    if row["type"] == "ШГК":
        shgk_pos.setdefault(row["net"], []).append(pos)
    else:
        shd_list.append((row["net"], pos))

for net, shd_pos in shd_list:
    if net not in shgk_pos:
        continue
    primary = shgk_pos[net][0]
    msp.add_line(
        primary, shd_pos,
        dxfattribs={"layer": "3_СВЯЗИ", "color": NET_ACI[net]},
    )

# Подпись внизу
total_w = kpp_x0 + kpp_total_w
msp.add_text(
    "СТРУКТУРНАЯ СХЕМА ЛВС ПСИ-158 (200 шкафов, 5 сетей) — авто из xlsx",
    dxfattribs={"layer": "0_ОСНОВНОЙ", "height": 5, "color": 7},
).set_placement(
    (total_w/2, gk_y0 - 12),
    align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER,
)

# Зум на всё
zoom.extents(msp, factor=1.1)

# Сохранить
doc.saveas(OUT)
print(f"OK: {OUT}")
print(f"Размер: {OUT.stat().st_size / 1024:.1f} KB")

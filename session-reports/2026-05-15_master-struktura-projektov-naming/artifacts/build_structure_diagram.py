"""
Построение структурной схемы ЛВС ПСИ-158 (200 шкафов, 5 сетей)
на основе xlsx Шкафы_ПСИ-158_v2_5сетей.xlsx
"""
import math
from pathlib import Path

import openpyxl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

BASE = Path(r"C:\Users\Deliseev\Desktop\Здадчака")
XLSX = BASE / "Шкафы_ПСИ-158_v2_5сетей.xlsx"
OUT_PNG = BASE / "Структурная_схема_ПСИ-158_v2.png"
OUT_SVG = BASE / "Структурная_схема_ПСИ-158_v2.svg"

NET_COLORS = {
    "МИС": "#1F77B4",
    "СБ":  "#D62728",
    "ОП":  "#FF7F0E",
    "СОТ": "#2CA02C",
    "СВН": "#9467BD",
}
NET_ORDER = ["МИС", "СБ", "ОП", "СОТ", "СВН"]

wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb["Шкафы"]

rows = list(ws.iter_rows(min_row=2, values_only=True))
print(f"Прочитано строк: {len(rows)}")

G = nx.DiGraph()
node_attrs = {}
shgk_by_net = {n: [] for n in NET_ORDER}
shd_by_net = {n: [] for n in NET_ORDER}

for row in rows:
    if not row or row[0] is None:
        continue
    n, net, obj, block, floor, room, type_, new_name, system_id, *_ = row
    G.add_node(new_name)
    node_attrs[new_name] = dict(
        net=net, type=type_, object=obj, block=block, floor=floor, room=room
    )
    if type_ == "ШГК":
        shgk_by_net[net].append(new_name)
    else:
        shd_by_net[net].append(new_name)

print("ШГК по сетям:", {n: len(v) for n, v in shgk_by_net.items()})
print("ШД  по сетям:", {n: len(v) for n, v in shd_by_net.items()})

# рёбра: каждый ШД --- ШГК своей сети
for net in NET_ORDER:
    shgks = shgk_by_net[net]
    if not shgks:
        continue
    primary_shgk = shgks[0]
    for shgk in shgks[1:]:
        G.add_edge(primary_shgk, shgk)
    for shd in shd_by_net[net]:
        G.add_edge(primary_shgk, shd)

# Layout: каждой сети свой сектор круга 72°
# ШГК -- ближе к центру (R1), ШД -- дальше (R2..R3) в том же секторе
pos = {}
R_SHGK = 8.0     # радиус ШГК (ядро схемы)
R_SHD_MIN = 18.0  # начальный радиус ШД
R_SHD_STEP = 2.2  # шаг между концентрическими «слоями» ШД
SECTOR_DEG = 360 / len(NET_ORDER)  # 72°
SECTOR_PADDING_DEG = 4              # зазор между секторами

# нумерация секторов по часовой, МИС наверху
NET_SECTORS = {}
for idx, net in enumerate(NET_ORDER):
    center_deg = 90 - idx * SECTOR_DEG  # центр сектора
    NET_SECTORS[net] = center_deg

for net, center_deg in NET_SECTORS.items():
    sector_half = (SECTOR_DEG - SECTOR_PADDING_DEG) / 2

    # ШГК — на ближнем радиусе по центру сектора
    shgks = shgk_by_net[net]
    for i, shgk in enumerate(shgks):
        # если несколько ШГК (МИС: основной + резерв) — слегка раздвинуть по углу
        offset_deg = (i - (len(shgks) - 1) / 2) * 4
        a = math.radians(center_deg + offset_deg)
        pos[shgk] = (R_SHGK * math.cos(a), R_SHGK * math.sin(a))

    # ШД — заполнить сектор по слоям/кольцам
    shds = shd_by_net[net]
    n = len(shds)
    if n == 0:
        continue

    # сколько ШД на слое — чем дальше, тем больше окружность
    # старт с 14, прирост на каждом следующем слое +2
    layers = []
    remaining = n
    per_layer_start = 14
    layer_idx = 0
    while remaining > 0:
        capacity = per_layer_start + layer_idx * 2
        take = min(capacity, remaining)
        layers.append(take)
        remaining -= take
        layer_idx += 1

    shd_idx = 0
    for li, count in enumerate(layers):
        r = R_SHD_MIN + li * R_SHD_STEP
        # равномерно по сектору
        if count == 1:
            angles = [center_deg]
        else:
            angles = [
                center_deg - sector_half + j * (2 * sector_half / (count - 1))
                for j in range(count)
            ]
        for ang_deg in angles:
            if shd_idx >= n:
                break
            a = math.radians(ang_deg)
            pos[shds[shd_idx]] = (r * math.cos(a), r * math.sin(a))
            shd_idx += 1

# Рисуем
fig, ax = plt.subplots(figsize=(48, 40))

# центральный узел "Сети операторов / ядро"
core_xy = (0.0, 0.0)
ax.scatter(*core_xy, s=2200, c="#333333", zorder=4, edgecolors="black", linewidths=1.2)
ax.text(0, 0, "Сети\nоператоров", color="white", ha="center", va="center",
        fontsize=11, fontweight="bold", zorder=5)
# рёбра core → ШГК
for net, shgks in shgk_by_net.items():
    for shgk in shgks:
        ax.plot([0, pos[shgk][0]], [0, pos[shgk][1]],
                color=NET_COLORS[net], linewidth=1.5, alpha=0.8, zorder=2)

# рёбра ШГК → ШД (по сети, тонкие)
for net in NET_ORDER:
    shgks = shgk_by_net[net]
    if not shgks:
        continue
    primary = shgks[0]
    px, py = pos[primary]
    for shd in shd_by_net[net]:
        sx, sy = pos[shd]
        ax.plot([px, sx], [py, sy], color=NET_COLORS[net],
                linewidth=0.35, alpha=0.25, zorder=1)

# узлы: ШГК крупные, ШД маленькие
node_colors = [NET_COLORS[node_attrs[n]["net"]] for n in G.nodes()]
node_sizes = [1100 if node_attrs[n]["type"] == "ШГК" else 130 for n in G.nodes()]
nx.draw_networkx_nodes(
    G, pos, ax=ax,
    node_color=node_colors, node_size=node_sizes,
    alpha=0.95, edgecolors="black", linewidths=0.6,
)

# подписи: ШГК -- жирно, ШД -- мелко но читаемо
shgk_labels = {n: n for n in G.nodes() if node_attrs[n]["type"] == "ШГК"}
shd_labels  = {n: n for n in G.nodes() if node_attrs[n]["type"] == "ШД"}
nx.draw_networkx_labels(G, pos, labels=shgk_labels, ax=ax,
                        font_size=11, font_weight="bold")
nx.draw_networkx_labels(G, pos, labels=shd_labels, ax=ax, font_size=5.5)

# заголовки секторов
for net, center_deg in NET_SECTORS.items():
    a = math.radians(center_deg)
    # «далёкий» радиус для подписи
    rr = R_SHD_MIN + 18
    ax.text(rr * math.cos(a), rr * math.sin(a),
            f"ЛВС {net}", fontsize=26, fontweight="bold",
            color=NET_COLORS[net], ha="center", va="center")

# легенда
legend_handles = [mpatches.Patch(color=NET_COLORS[n], label=f"ЛВС {n}") for n in NET_ORDER]
ax.legend(handles=legend_handles, loc="upper left",
          fontsize=13, title="Сети", title_fontsize=15)

ax.set_title(
    "Структурная схема ЛВС ПСИ-158 — 200 шкафов в 5 сетях\n"
    "(автогенерация из Шкафы_ПСИ-158_v2_5сетей.xlsx)",
    fontsize=22,
)
ax.axis("off")
plt.tight_layout()

plt.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
plt.savefig(OUT_SVG, format="svg", bbox_inches="tight")
print(f"OK: {OUT_PNG}")
print(f"OK: {OUT_SVG}")

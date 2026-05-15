"""Рендер DXF в SVG/PNG для предпросмотра."""
from pathlib import Path
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt

BASE = Path(r"C:\Users\Deliseev\Desktop\Здадчака")
DXF = BASE / "Структурная_схема_ПСИ-158_v2.dxf"
PNG = BASE / "Структурная_схема_ПСИ-158_v2_DXF.png"
SVG = BASE / "Структурная_схема_ПСИ-158_v2_DXF.svg"

doc = ezdxf.readfile(DXF)
msp = doc.modelspace()

fig = plt.figure(figsize=(40, 24))
ax = fig.add_axes([0, 0, 1, 1])
ctx = RenderContext(doc)
backend = MatplotlibBackend(ax)
Frontend(ctx, backend).draw_layout(msp, finalize=True)

fig.savefig(PNG, dpi=150, bbox_inches="tight")
fig.savefig(SVG, format="svg", bbox_inches="tight")
print(f"OK PNG: {PNG}")
print(f"OK SVG: {SVG}")

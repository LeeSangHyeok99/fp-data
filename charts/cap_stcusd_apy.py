"""
Cap stcUSD Average APY (area chart)
Four Pillars 스타일. cap.app/protocol 의 stcUSD Average APY 곡선 재현.
APY가 출시 초기 두 자릿수(~13%)에서 시장 수준(~5%)으로 압축된 흐름.
Source: https://cap.app/protocol (cap.app API 접근 차단(403)으로 이미지에서 추출)
"""

import sys
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import apply_style, create_figure, save_chart

df = pd.read_csv("outputs/data/cap_stcusd_apy.csv", parse_dates=["date"])

LINE = "#c5d92c"  # stcUSD 라임/올리브

# -----------------------------------------------------------------------------
# 차트
# -----------------------------------------------------------------------------
fig, ax = create_figure("area")

x = mdates.date2num(df["date"])
y = df["apy"].values
YMAX = 15.0

# 라인 아래 세로 그라데이션 필 (라인색 → 투명)
grad = np.empty((256, 1, 4))
rgb = mcolors.to_rgb(LINE)
grad[:, :, 0] = rgb[0]
grad[:, :, 1] = rgb[1]
grad[:, :, 2] = rgb[2]
grad[:, :, 3] = np.linspace(0.0, 0.55, 256)[:, None]  # 아래 투명 → 위 진함
im = ax.imshow(grad, aspect="auto", origin="lower",
               extent=[x.min(), x.max(), 0, YMAX], zorder=1, interpolation="bilinear")
verts = np.vstack([[x[0], 0], np.column_stack([x, y]), [x[-1], 0]])
im.set_clip_path(Polygon(verts, closed=True, transform=ax.transData))

ax.plot(df["date"], y, color=LINE, linewidth=2.0, zorder=4)

# -----------------------------------------------------------------------------
# 축
# -----------------------------------------------------------------------------
ax.set_ylim(0, YMAX)
ax.set_yticks([0, 5, 10, 15])
ax.set_yticklabels([f"{v}%" for v in [0, 5, 10, 15]])

ax.set_xlim(df["date"].min(), df["date"].max())
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

apply_style(fig, ax, "area")
ax.tick_params(axis="y", labelsize=22)
ax.tick_params(axis="x", labelsize=20)

png, svg = save_chart(fig, "cap_stcusd_apy", "outputs/charts/cap/yield")
print("saved:", png, svg)

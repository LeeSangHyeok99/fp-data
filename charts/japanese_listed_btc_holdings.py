"""
Japanese Listed Companies, Disclosed BTC Holdings
소스: BitcoinTreasuries.net (countries/japan), Metaplanet Inc.
레퍼런스(Mermaid xychart) 내재화: Metaplanet, Remixpoint, ANAP, Convano, S-Science, Gumi
four-pillars dark theme, 어두운->밝은 오렌지 2색 그라데이션.
"""
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import FuncFormatter
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, save_chart  # noqa: E402

setup_font()
TEXT = COLORS['text']
TEXT2 = COLORS['text_secondary']
BTC_ORANGE = '#f7931a'        # 밝은 오렌지 (상단)
BTC_ORANGE_DARK = '#a85f12'   # 어두운 오렌지 (하단, 같은 계열)


def gradient_bar_2color(ax, x_center, width, height, c_bottom, c_top, alpha=0.97):
    """라운드 탑 바 + 두 색(어두운 오렌지 -> 밝은 오렌지) 수직 그라데이션."""
    if height is None or height <= 0:
        return
    radius = min(width / 2, height * 0.35)
    rect_top = height - radius
    x_left, x_right = x_center - width / 2, x_center + width / 2

    theta = np.linspace(0, np.pi, 40)
    arc_x = x_center + radius * np.cos(theta)
    arc_y = rect_top + radius * np.sin(theta)
    verts = [(x_left, 0), (x_right, 0), (x_right, rect_top)]
    verts += list(zip(arc_x, arc_y))
    verts += [(x_left, rect_top), (x_left, 0)]
    codes = [MPath.MOVETO] + [MPath.LINETO] * (len(verts) - 2) + [MPath.CLOSEPOLY]
    clip = PathPatch(MPath(verts, codes), facecolor='none', edgecolor='none',
                     transform=ax.transData)
    ax.add_patch(clip)

    rb, gb, bb = mcolors.to_rgb(c_bottom)
    rt, gt, bt = mcolors.to_rgb(c_top)
    grad = np.zeros((256, 1, 4))
    for i in range(256):
        f = i / 255
        grad[i, 0] = [rb + (rt - rb) * f, gb + (gt - gb) * f, bb + (bt - bb) * f, alpha]
    im = ax.imshow(grad, aspect='auto', origin='lower',
                   extent=[x_left, x_right, 0, height], zorder=3,
                   interpolation='bilinear')
    im.set_clip_path(clip)


df = pd.read_csv('outputs/data/japanese_listed_btc_holdings.csv')
x = np.arange(len(df))

fig, ax = plt.subplots(figsize=(9.8, 5.6), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for s in ax.spines.values():
    s.set_visible(False)

W = 0.62
for xi, v in zip(x, df['btc_held']):
    gradient_bar_2color(ax, x_center=xi, width=W, height=v,
                        c_bottom=BTC_ORANGE_DARK, c_top=BTC_ORANGE)
    ax.text(xi, v + 650, f"{v:,.0f}", ha='center', va='bottom',
            color=TEXT, fontsize=11, fontweight='bold')

# 축
ax.set_xlim(-0.6, len(df) - 0.4)
ax.set_ylim(0, 42000)
ax.set_xticks(x)
ax.set_xticklabels(df['company'], rotation=0)
ax.tick_params(axis='x', colors=TEXT2, labelsize=12, length=0, pad=8)

yticks = [0, 10000, 20000, 30000, 40000]
ax.set_yticks(yticks)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v/1000:,.0f}K"))
ax.tick_params(axis='y', colors=TEXT2, labelsize=12, length=0, pad=8)
ax.grid(True, axis='y', color=TEXT2, alpha=0.18, linestyle=(0, (3.7, 1.6)), linewidth=0.9)
ax.set_axisbelow(True)

fig.subplots_adjust(left=0.10, right=0.98, top=0.96, bottom=0.10)

png, svg = save_chart(fig, 'japanese_listed_btc_holdings',
                      output_dir='outputs/charts/bitcoin/treasury')
print('saved:', png)
total = df['btc_held'].sum()
print(f"total {total:,} BTC, Metaplanet {df['btc_held'].iloc[0]/total*100:.1f}%")

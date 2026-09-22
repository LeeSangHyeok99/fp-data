"""
Solana captures more trading than asset balances: Solana share across 24 chains,
six asset classes excl. stablecoins (progress-style horizontal bars) - four-pillars 내재화.
소스: Allium (레퍼런스 이미지 수치). 투명 배경, 1600px 슬롯 폭 1:1.
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, gradient_barh  # noqa: E402

setup_font()
df = pd.read_csv('outputs/data/solana_rwa_share_metrics.csv')

W, H = 1600, 440
PX2PT = 0.72
TRACK, GREY, GREEN = '#262A2F', '#A9ADB8', '#5FA86C'
TEXT, SUB = '#D1D4DC', '#9CA3AF'
X0, X1 = 300, 1220           # 트랙 구간
BAR_H, PITCH, Y0 = 54, 112, 22

fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')

for i, r in df.iterrows():
    y = Y0 + i * PITCH; yc = y + BAR_H / 2
    color = GREEN if i == len(df) - 1 else GREY
    ax.add_patch(Rectangle((X0, y), X1 - X0, BAR_H, facecolor=TRACK, edgecolor='none', zorder=2))
    rect = Rectangle((X0, y), (X1 - X0) * r['share_pct'] / 100, BAR_H, facecolor=color, edgecolor='none', zorder=3)
    ax.add_patch(rect); gradient_barh(ax, rect, color, floor=0.78)
    ax.text(0, yc, r['metric'], ha='left', va='center', fontsize=29 * PX2PT, fontweight='bold', color=TEXT)
    ax.text(X1 + 45, yc, f"{r['share_pct']}%", ha='left', va='center', fontsize=34 * PX2PT, fontweight='bold', color=color if i == len(df) - 1 else TEXT)
    ax.text(W, yc, r['value_label'], ha='right', va='center', fontsize=27 * PX2PT, fontweight='bold', color=SUB)
ax.set_xlim(0, W); ax.set_ylim(H, 0)   # imshow가 바꾼 범위 복구

png, svg = save_chart(fig, 'solana_rwa_share_metrics', 'outputs/charts/solana/rwa', tight=False)
plt.close(fig); print(png)

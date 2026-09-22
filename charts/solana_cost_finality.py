"""
Lower transaction costs and faster finality: Solana Q2 2026 KPI (fee, non-vote tx)
+ time-to-finality bars (current consensus vs Alpenglow target).
소스: Blockworks, Solana (레퍼런스 수치). 투명 배경, 1600px 슬롯 폭 1:1.
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, gradient_barh, GRID_CONFIG  # noqa: E402

setup_font()
df = pd.read_csv('outputs/data/solana_time_to_finality.csv')

W, H = 1600, 540
PX2PT = 0.72
TEXT, SUB, GREY, GREEN, GRID = '#D1D4DC', '#9CA3AF', '#A9ADB8', '#5FA86C', GRID_CONFIG['color']
AX0, AX1, XMAX = 340, 1200, 15
BAR_H, Y_ROWS = 44, (330, 440)
px = lambda v: AX0 + (AX1 - AX0) * v / XMAX

fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')

# KPI 블록
for x, label, value, note in [
    (0, 'Q2 2026 Transaction Fee', '$0.0004', 'Quarterly Average Of Daily Medians'),
    (900, 'Q2 2026 Non-Vote Transactions', '9.8B', 'Includes Successful And Reverted Transactions'),
]:
    ax.text(x, 22, label, ha='left', va='center', fontsize=26 * PX2PT, color=SUB)
    ax.text(x, 78, value, ha='left', va='center', fontsize=46 * PX2PT, fontweight='bold', color=TEXT)
    ax.text(x, 132, note, ha='left', va='center', fontsize=26 * PX2PT, color=SUB)

# 섹션 헤더 + 단위 주석
ax.text(0, 240, 'Time To Finality', ha='left', va='center', fontsize=29 * PX2PT, fontweight='bold', color=TEXT)
ax.text(W, 268, 'Seconds; Alpenglow Is A Development Target', ha='right', va='center', fontsize=24 * PX2PT, color=SUB)

# 세로 그리드 + 눈금
ytop, ybot = Y_ROWS[0] - 30, Y_ROWS[-1] + BAR_H + 30
for t in (0, 5, 10, 15):
    ax.plot([px(t)] * 2, [ytop, ybot], color=GRID, alpha=0.45, linewidth=1, zorder=1)
    ax.text(px(t), ybot + 26, f'{t}', ha='center', va='center', fontsize=25 * PX2PT, color=SUB)

for (_, r), y in zip(df.iterrows(), Y_ROWS):
    color = GREEN if 'Alpenglow' in r['item'] else GREY
    rect = Rectangle((AX0, y), px(r['seconds']) - AX0, BAR_H, facecolor=color, edgecolor='none', zorder=3)
    ax.add_patch(rect); gradient_barh(ax, rect, color, floor=0.78)
    ax.text(0, y + BAR_H / 2, r['item'], ha='left', va='center', fontsize=29 * PX2PT, fontweight='bold', color=TEXT)
    ax.text(W, y + BAR_H / 2, f"{r['seconds']:g} sec", ha='right', va='center', fontsize=30 * PX2PT,
            fontweight='bold', color=color if color == GREEN else SUB)
ax.set_xlim(0, W); ax.set_ylim(H, 0)

png, svg = save_chart(fig, 'solana_cost_finality', 'outputs/charts/solana/performance', tight=False)
plt.close(fig); print(png)

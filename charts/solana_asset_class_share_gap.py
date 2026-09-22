"""
The gap between holdings and trading varies by asset class: Solana share of each
asset class across all chains (dumbbell, open=balances, filled=volume).
소스: Allium (레퍼런스 이미지 수치). 투명 배경, 1600px 슬롯 폭 1:1.
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, GRID_CONFIG  # noqa: E402

setup_font()
df = pd.read_csv('outputs/data/solana_asset_class_share_gap.csv')

W, H = 1600, 540
PX2PT = 0.72
GREEN, LINE, TEXT, SUB, GRID = '#5FA86C', '#A9ADB8', '#D1D4DC', '#9CA3AF', GRID_CONFIG['color']
AX0, AX1 = 375, 1375                 # 0% ~ 100%
Y0, PITCH, R = 125, 150, 11
px = lambda p: AX0 + (AX1 - AX0) * p / 100

fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')

# 마커 설명 (범례 대체)
ax.text(AX0, 22, 'Open Circle: Share Of Balances', ha='left', va='center', fontsize=24 * PX2PT, color=SUB)
ax.text(AX1, 22, 'Filled Circle: Share Of Volume', ha='right', va='center', fontsize=24 * PX2PT, fontweight='bold', color=GREEN)

# 세로 그리드 + 눈금
ytop, ybot = Y0 - 45, Y0 + (len(df) - 1) * PITCH + 45
for p in (0, 25, 50, 75, 100):
    ax.plot([px(p)] * 2, [ytop, ybot], color=GRID, alpha=0.45, linewidth=1, zorder=1)
    ax.text(px(p), ybot + 28, f'{p}%', ha='center', va='center', fontsize=25 * PX2PT, color=SUB)

for i, r in df.iterrows():
    y = Y0 + i * PITCH
    xb, xv = px(r['balance_share_pct']), px(r['volume_share_pct'])
    ax.plot([xb, xv], [y, y], color=LINE, linewidth=2, zorder=2)
    ax.scatter([xb], [y], s=(2 * R) ** 2 * 0.85, facecolor='#141414', edgecolor=TEXT, linewidth=2, zorder=3)
    ax.scatter([xv], [y], s=(2 * R) ** 2 * 0.85, facecolor=GREEN, edgecolor=GREEN, linewidth=2, zorder=3)
    ax.text(xb - R - 10, y, f"{r['balance_share_pct']}%", ha='right', va='center', fontsize=26 * PX2PT, color=SUB)
    ax.text(xv + R + 10, y, f"{r['volume_share_pct']}%", ha='left', va='center', fontsize=26 * PX2PT, fontweight='bold', color=GREEN)
    ax.text(0, y, r['asset_class'], ha='left', va='center', fontsize=29 * PX2PT, fontweight='bold', color=TEXT)
    ax.text(W, y - 20, f"Balance {r['balance_label']}", ha='right', va='center', fontsize=24 * PX2PT, color=SUB)
    ax.text(W, y + 20, f"Volume {r['volume_label']}", ha='right', va='center', fontsize=24 * PX2PT, color=SUB)

png, svg = save_chart(fig, 'solana_asset_class_share_gap', 'outputs/charts/solana/rwa', tight=False)
plt.close(fig); print(png)

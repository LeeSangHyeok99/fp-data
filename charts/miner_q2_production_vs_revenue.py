"""
Q2 2026 YoY change in BTC mined vs mining revenue (MARA, Riot, CleanSpark).
four-pillars grouped bar. No title/legend/source per chart rules; series are
identified by the value labels' color (teal = BTC mined, white = revenue).
Data: sources/data4_q2_production_vs_revenue.csv
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.colors as mcolors
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, '.claude/skills/design/four-pillars')
from config import setup_font, save_chart, COLORS, DPI, GRID_CONFIG

setup_font()

MINED_COLOR = '#2a9284'   # BTC Mined YoY
REV_COLOR = '#18243b'     # Mining Revenue YoY

df = pd.read_csv('sources/data4_q2_production_vs_revenue.csv')
x = np.arange(len(df))
W, PAD = 0.4, 0.02

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

def grad_bar(ax, xc, w, v, color, floor=0.68):
    """0 쪽이 어둡고 바 끝으로 갈수록 밝아지는 세로 그라데이션 막대."""
    r, g, b = mcolors.to_rgb(color)
    f = floor + (1 - floor) * np.linspace(0, 1, 256) ** 0.5
    if v < 0:                       # 아래로 자라는 막대는 위아래를 뒤집는다
        f = f[::-1]
    grad = np.stack([r * f, g * f, b * f, np.ones(256)], axis=-1)[:, None, :]
    ax.imshow(grad, aspect='auto', origin='lower', interpolation='bilinear',
              extent=[xc - w / 2, xc + w / 2, min(0, v), max(0, v)], zorder=3)


series = ((x - (W + PAD) / 2, 'btc_mined_yoy_pct', MINED_COLOR, MINED_COLOR),
          (x + (W + PAD) / 2, 'revenue_yoy_pct', REV_COLOR, COLORS['text']))
for xs, col, bar_color, label_color in series:
    for xc, v in zip(xs, df[col]):
        grad_bar(ax, xc, W, v, bar_color)
        ax.annotate(f'{v:+.1f}%', xy=(xc, v),
                    xytext=(0, 8 if v >= 0 else -8), textcoords='offset points',
                    ha='center', va='bottom' if v >= 0 else 'top',
                    fontsize=14, fontweight='bold', color=label_color, zorder=5)

# imshow가 축을 이미지 경계에 맞춰버리므로 xlim/ylim은 그린 뒤에 되돌린다.

ax.axhline(0, color=COLORS['text'], linewidth=1.2, zorder=4)

ax.set_ylim(-40, 20)
ax.set_yticks([-30, -20, -10, 0, 10])
ax.set_yticklabels([f'{v}%' for v in (-30, -20, -10, 0, 10)], fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(df['company'], fontweight='bold')
ax.set_xlim(-0.6, len(df) - 0.4)

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='y', length=0, colors=COLORS['text_secondary'],
               labelsize=18, pad=12)
ax.tick_params(axis='x', length=0, colors=COLORS['text'], labelsize=16, pad=10)

fig.tight_layout()
print(save_chart(fig, 'miner_q2_production_vs_revenue',
                 output_dir='outputs/charts/bitcoin/mining'))
plt.close()

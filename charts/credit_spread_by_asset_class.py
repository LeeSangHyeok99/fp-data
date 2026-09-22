import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from pathlib import Path

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, COLORS, GRID_CONFIG

df = pd.read_csv('outputs/data/credit_spreads_by_asset_class.csv')

categories = df['asset_class'].tolist()
avgs = df['avg_bps'].values
lows = df['low_bps'].values
highs = df['high_bps'].values

colors = ['#7aa3e0', '#e8984a', '#9a7fd1']

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(categories))
bar_width = 0.55

for i, (xi, h, c) in enumerate(zip(x, avgs, colors)):
    r, g, b = mcolors.to_rgb(c)
    gradient = np.zeros((256, 1, 4))
    for j in range(256):
        frac = j / 255
        factor = 0.78 + 0.22 * frac
        gradient[j, 0] = [r * factor, g * factor, b * factor, 1.0]
    ax.imshow(
        gradient,
        aspect='auto',
        origin='lower',
        extent=[xi - bar_width / 2, xi + bar_width / 2, 0, h],
        zorder=2,
        interpolation='bilinear',
    )

err_color = '#d1d4dc'
for xi, avg, lo, hi in zip(x, avgs, lows, highs):
    ax.plot([xi, xi], [lo, hi], color=err_color, linewidth=1.4, zorder=4)
    cap_w = 0.12
    ax.plot([xi - cap_w, xi + cap_w], [lo, lo], color=err_color, linewidth=1.4, zorder=4)
    ax.plot([xi - cap_w, xi + cap_w], [hi, hi], color=err_color, linewidth=1.4, zorder=4)

for xi, avg in zip(x, avgs):
    ly = avg * 1.17
    ax.scatter(xi, ly, marker='D', s=55, color='#f2f2f2',
               edgecolors=COLORS['background'], linewidths=1.0, zorder=6)
    ax.annotate(
        f'{avg} bps',
        xy=(xi, ly),
        xytext=(14, 0),
        textcoords='offset points',
        fontsize=13,
        fontweight='bold',
        color=COLORS['text'],
        va='center',
        ha='left',
        zorder=7,
    )

ax.set_ylim(0, 200)
ax.set_yticks([0, 50, 100, 150, 200])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{int(v)}'))

ax.set_xticks(x)
ax.set_xticklabels(categories)

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', labelsize=14, pad=10, length=0,
               colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=13, pad=10, length=0,
               colors=COLORS['text_secondary'])

ax.set_xlim(-0.7, len(categories) - 0.3)

fig.tight_layout()

output_dir = 'outputs/charts/credit/spreads'
Path(output_dir).mkdir(parents=True, exist_ok=True)
save_chart(fig, 'credit_spread_by_asset_class', output_dir)
plt.close(fig)
print(f'Saved to {output_dir}/credit_spread_by_asset_class.png')

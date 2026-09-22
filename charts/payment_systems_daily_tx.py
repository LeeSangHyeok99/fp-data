import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, COLORS, DPI, AXIS_CONFIG, GRID_CONFIG

mpl.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('outputs/data/payment_systems_daily_tx.csv')
labels = df['system'].tolist()
lows = df['low'].tolist()
highs = df['high'].tolist()

colors = ['#a8c8e8', '#3b82c4', '#0f3a6e']

X_MIN = 1e4
X_MAX = 1e9


def gradient_hbar(ax, y_center, height, x_left, x_right, color, alpha=0.95):
    if x_right <= x_left:
        return
    r, g, b = mcolors.to_rgb(color)
    gradient = np.zeros((1, 256, 4))
    for i in range(256):
        frac = i / 255
        factor = 0.55 + 0.45 * (frac ** 0.5)
        gradient[0, i] = [r * factor, g * factor, b * factor, alpha]
    ax.imshow(gradient, aspect='auto', origin='lower',
              extent=[x_left, x_right, y_center - height / 2, y_center + height / 2],
              zorder=3, interpolation='bilinear')


fig, ax = create_figure('horizontal_bar')
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.set_xscale('log')
ax.set_xlim(X_MIN, X_MAX)

y = np.arange(len(labels))[::-1]
bar_height = 0.55

def fmt_num(v):
    if v >= 1e9:
        return f'{v/1e9:.2f}'.rstrip('0').rstrip('.') + 'B'
    if v >= 1e6:
        return f'{v/1e6:.2f}'.rstrip('0').rstrip('.') + 'M'
    if v >= 1e3:
        return f'{v/1e3:.2f}'.rstrip('0').rstrip('.') + 'K'
    return f'{int(v)}'


for yi, lo, hi, c in zip(y, lows, highs, colors):
    gradient_hbar(ax, y_center=yi, height=bar_height, x_left=X_MIN, x_right=hi, color=c)
    ax.text(hi * 1.15, yi, f'{fmt_num(lo)}–{fmt_num(hi)}',
            ha='left', va='center', fontsize=13, fontweight='bold',
            color=COLORS['text_secondary'], zorder=5)

# X-axis ticks
def fmt_count(v, p):
    if v >= 1e9:
        return f'{int(v/1e9)}B'
    if v >= 1e6:
        return f'{int(v/1e6)}M'
    if v >= 1e3:
        return f'{int(v/1e3)}K'
    return f'{int(v)}'

ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_count))
ax.xaxis.set_major_locator(mticker.LogLocator(base=10.0, numticks=6))
ax.xaxis.set_minor_locator(mticker.NullLocator())

# Y-axis
ax.set_yticks(y)
ax.set_yticklabels(labels)
ax.set_ylim(-0.6, len(labels) - 0.4)

apply_style(fig, ax, 'horizontal_bar')

ax.tick_params(axis='y', labelsize=16, length=0, pad=15,
               colors=COLORS['text_secondary'], rotation=0)
plt.setp(ax.yaxis.get_majorticklabels(), ha='right')
ax.tick_params(axis='x', labelsize=16, length=6, width=1, pad=10,
               rotation=0, colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

ax.grid(True, axis='x', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.grid(False, axis='y')
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

output_dir = 'outputs/charts/payments/global'
Path(output_dir).mkdir(parents=True, exist_ok=True)

fig.savefig(f'{output_dir}/payment_systems_daily_tx.png', dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/payment_systems_daily_tx.svg', format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/payment_systems_daily_tx.png")

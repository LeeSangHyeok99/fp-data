import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, COLORS, DPI

import matplotlib.colors as mcolors

mpl.rcParams['axes.unicode_minus'] = False


def gradient_rect_bar(ax, x_center, width, height, color, alpha=0.95):
    """Plain rectangular bar with vertical gradient (dark bottom -> bright top)."""
    if height is None or height <= 0:
        return
    x_left = x_center - width / 2
    x_right = x_center + width / 2

    r, g, b = mcolors.to_rgb(color)
    gradient = np.zeros((256, 1, 4))
    for i in range(256):
        frac = i / 255
        factor = 0.15 + 0.85 * (frac ** 0.5)
        gradient[i, 0] = [r * factor, g * factor, b * factor, alpha]

    ax.imshow(gradient, aspect='auto', origin='lower',
              extent=[x_left, x_right, 0, height],
              zorder=3, interpolation='bilinear')

df = pd.read_csv('outputs/data/ecny_transaction_volume.csv')
labels = df['period'].tolist()
values = df['volume_trillion_cny'].tolist()

BAR_COLOR = '#e94f64'

fig, ax = create_figure('bar')
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(labels))
bar_width = 0.55

for xi, v in zip(x, values):
    gradient_rect_bar(ax, x_center=xi, width=bar_width, height=v, color=BAR_COLOR)

def trillion_formatter(v, pos):
    return f'¥{v:.0f}T'

ax.yaxis.set_major_formatter(mticker.FuncFormatter(trillion_formatter))
ax.set_ylim(0, 8)
ax.set_yticks([0, 2, 4, 6, 8])

ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_xlim(-0.5, len(labels) - 0.5)

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=18, length=0, pad=15)
ax.tick_params(axis='x', labelsize=16, length=6, width=1, pad=10,
               rotation=45, colors='#787b86')
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.grid(True, axis='y', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

output_dir = 'outputs/charts/cbdc/ecny'
Path(output_dir).mkdir(parents=True, exist_ok=True)

fig.savefig(f'{output_dir}/ecny_transaction_volume.png', dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/ecny_transaction_volume.svg', format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print(f"Saved: {output_dir}/ecny_transaction_volume.png")

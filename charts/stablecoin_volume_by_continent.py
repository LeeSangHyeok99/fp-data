import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, COLORS

df = pd.read_csv('sources/volume-by-continent.csv')
df = df[df['continent'] != 'Total'].sort_values('volume_sent_usd', ascending=True)

DOMESTIC = '#5470c6'
CROSS_BORDER = '#fc8452'


def fmt_usd(v):
    if v >= 1e9:
        return f'${v / 1e9:.2f}B'
    return f'${v / 1e6:.0f}M'


def gradient_hbar(ax, y_center, height, x0, width, color, alpha=0.95, floor=0.78):
    """수평 그라데이션 바 세그먼트. 왼쪽은 어둡고 오른쪽으로 갈수록 밝아진다."""
    if width <= 0:
        return
    y0, y1 = y_center - height / 2, y_center + height / 2
    r, g, b = mcolors.to_rgb(color)
    gradient = np.zeros((1, 256, 4))
    for i in range(256):
        factor = floor + (1.0 - floor) * (i / 255)
        gradient[0, i] = [r * factor, g * factor, b * factor, alpha]
    ax.imshow(gradient, aspect='auto', origin='lower',
              extent=[x0, x0 + width, y0, y1], zorder=3, interpolation='bilinear')


fig, ax = create_figure('horizontal_bar')
fig.set_size_inches(11.5, 5.2)

y = range(len(df))
domestic = df['domestic_usd'].to_numpy()
cross_border = df['cross_border_sent_usd'].to_numpy()
total = domestic + cross_border

max_val = total.max() / 1e9

for i, (d, c, t) in enumerate(zip(domestic, cross_border, total)):
    d_b, c_b = d / 1e9, c / 1e9
    gradient_hbar(ax, i, 0.6, 0, d_b, DOMESTIC)
    gradient_hbar(ax, i, 0.6, d_b, c_b, CROSS_BORDER)
    # segment label inside the bar, only if wide enough to hold the text
    if d_b / max_val > 0.12:
        ax.text(d_b / 2, i, fmt_usd(d), ha='center', va='center',
                fontsize=13, fontweight='bold', color='#ffffff', zorder=4)
    if c_b / max_val > 0.12:
        ax.text(d_b + c_b / 2, i, fmt_usd(c), ha='center', va='center',
                fontsize=13, fontweight='bold', color='#ffffff', zorder=4)
    # total label at bar end
    ax.text(d_b + c_b + max_val * 0.02, i, fmt_usd(t), ha='left', va='center',
            fontsize=16, fontweight='bold', color=COLORS['text'], zorder=4)

ax.set_yticks(list(y))
ax.set_yticklabels(df['continent'].tolist())

ax.set_xlim(0, 7)
ax.set_xticks([0, 2, 4, 6])
ax.set_xticklabels(['$0B', '$2B', '$4B', '$6B'])
# imshow segments each reset autoscale to their own extent instead of
# unioning, so the y-range must be pinned explicitly to cover every row
ax.set_ylim(-0.5, len(df) - 0.5)

apply_style(fig, ax, 'horizontal_bar')

# horizontal bar needs vertical gridlines instead of the default horizontal ones
ax.grid(False, axis='y')
ax.grid(True, axis='x', color=COLORS['grid'], alpha=0.5,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

ax.tick_params(axis='y', labelsize=13)
ax.tick_params(axis='x', rotation=0, labelsize=20)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

Path('outputs/charts/stablecoin/regional_volume').mkdir(parents=True, exist_ok=True)
png_path, svg_path = save_chart(fig, 'stablecoin_volume_by_continent',
                                 'outputs/charts/stablecoin/regional_volume')
plt.close(fig)

print(png_path)
print(svg_path)

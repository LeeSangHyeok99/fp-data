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

df_all = pd.read_csv('sources/domestic-share-by-country.csv')
# global average is a stat over the full country set (matches the reference's
# stated 62.6%), even though only the top 12 (through Brazil) are plotted
global_avg = (df_all['domestic_usd'].sum() / df_all['outbound_sent_usd'].sum()) * 100

df = (df_all.sort_values('domestic_pct', ascending=False).head(12)
      .sort_values('domestic_pct', ascending=True))

DOMESTIC = '#5470c6'
INTRA_REGION = '#fc8452'
OUTSIDE_REGION = '#3ba272'


def fmt_usd(v):
    if v >= 1e9:
        return f'${v / 1e9:.2f}B'
    if v >= 1e8:
        return f'${v / 1e6:.0f}M'
    return f'${v / 1e6:.1f}M'


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


n = len(df)
fig, ax = create_figure('horizontal_bar')
fig.set_size_inches(12.5, 0.42 * n + 1.1)

y = range(n)
domestic = df['domestic_pct'].to_numpy()
intra = df['intra_region_pct'].to_numpy()
outside = df['outside_region_pct'].to_numpy()
domestic_usd = df['domestic_usd'].to_numpy()

for i in range(n):
    gradient_hbar(ax, i, 0.62, 0, domestic[i], DOMESTIC)
    gradient_hbar(ax, i, 0.62, domestic[i], intra[i], INTRA_REGION)
    gradient_hbar(ax, i, 0.62, domestic[i] + intra[i], outside[i], OUTSIDE_REGION)

# single fixed x for every % label (midpoint of the shortest domestic bar),
# so labels line up in one straight column instead of drifting per bar width
label_x = domestic.min() / 2

for i, (d, du) in enumerate(zip(domestic, domestic_usd)):
    ax.text(label_x, i, f'{d:.1f}%', ha='center', va='center',
            fontsize=14, fontweight='bold', color='#ffffff', zorder=4)
    ax.text(103, i, fmt_usd(du), ha='left', va='center',
            fontsize=14, fontweight='bold', color=COLORS['text'], zorder=4)

ax.axvline(global_avg, color='#ffffff', alpha=0.9,
           linestyle=(0, (3.7, 1.6)), linewidth=1.6, zorder=6)
ax.text(global_avg, n - 0.15, f'Global Average {global_avg:.1f}%',
        ha='center', va='bottom', fontsize=14, fontweight='bold',
        color='#ffffff', zorder=4)

ax.set_yticks(list(y))
ax.set_yticklabels(df['country'].tolist())

ax.set_xlim(0, 118)
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
# imshow segments each reset autoscale to their own extent instead of
# unioning, so the y-range must be pinned explicitly to cover every row
ax.set_ylim(-0.5, n - 0.5)

apply_style(fig, ax, 'horizontal_bar')

ax.grid(False, axis='y')
ax.grid(True, axis='x', color=COLORS['grid'], alpha=0.4,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

# apply_style sets a large default tick font; shrink both axes to fit the rows
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', rotation=0, labelsize=15)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

Path('outputs/charts/stablecoin/domestic_share').mkdir(parents=True, exist_ok=True)
png_path, svg_path = save_chart(fig, 'stablecoin_domestic_share_by_country',
                                 'outputs/charts/stablecoin/domestic_share')
plt.close(fig)

print(png_path)
print(svg_path)
print(f'global_avg={global_avg:.2f}%')

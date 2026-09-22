"""
Korea Simple Payment Daily Average Volume (2017 ~ 2025 H1)
Bank of Korea data: Daily average transaction value of 간편지급 (Simple Payment) services
Bar chart, uniform width, vertical gradient fill (no rounded top distortion for short bars).
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyBboxPatch
from config import (
    create_figure, save_chart, COLORS, AXIS_CONFIG,
)

df = pd.read_csv('outputs/data/korea_simple_payment_daily_avg.csv')

bar_color = '#3182F6'
highlight_color = '#FACC15'

fig, ax = create_figure('bar')

x = np.arange(len(df))
bar_width = 0.6
values = df['daily_avg_krw_100m'].values  # unit: 100M won (억)

# Vertical gradient fill via imshow clipped to each bar rectangle.
# Same imshow extent height as bar height, identical width across all bars.
def draw_gradient_bar(ax, xc, w, h, color, alpha=0.95):
    if h is None or h <= 0:
        return
    r, g, b = mcolors.to_rgb(color)
    grad = np.zeros((256, 1, 4))
    for i in range(256):
        frac = i / 255
        factor = 0.18 + 0.82 * (frac ** 0.5)
        grad[i, 0] = [r * factor, g * factor, b * factor, alpha]
    x_left = xc - w / 2
    x_right = xc + w / 2
    im = ax.imshow(
        grad, aspect='auto', origin='lower',
        extent=[x_left, x_right, 0, h],
        zorder=3, interpolation='bilinear',
    )
    # Clip with simple rectangle (no rounded top so width stays uniform)
    from matplotlib.patches import Rectangle
    clip = Rectangle((x_left, 0), w, h, facecolor='none', edgecolor='none',
                     transform=ax.transData)
    ax.add_patch(clip)
    im.set_clip_path(clip)

for i, val in enumerate(values):
    draw_gradient_bar(ax, x[i], bar_width, val, bar_color)

# Value labels
for i, val in enumerate(values):
    is_last = (i == len(x) - 1)
    val_b = val / 10  # 100M won (억) -> billion won
    if val_b >= 1000:
        label = f'₩{val_b/1000:.2f}T'
    else:
        label = f'₩{val_b:.0f}B'
    ax.annotate(
        label,
        xy=(x[i], val),
        xytext=(0, 14),
        textcoords='offset points',
        ha='center', va='bottom',
        fontsize=15 if is_last else 12,
        fontweight='bold',
        color=highlight_color if is_last else COLORS['text'],
        zorder=6,
    )

# X-axis
ax.set_xticks(x)
ax.set_xticklabels(
    df['period'].astype(str),
    rotation=0,
    fontsize=AXIS_CONFIG['x_tick']['fontsize'],
    fontweight='bold',
    color=AXIS_CONFIG['x_tick']['color'],
)
ax.tick_params(axis='x', rotation=0, pad=10, length=0)
ax.set_xlim(-0.6, len(df) - 0.4)

# Y-axis: 0 ~ ₩1.2T (unit = 100M won; 12000 == 1.2T). Tick interval 0.3T.
ax.set_ylim(0, 14000)
ax.set_yticks([0, 3000, 6000, 9000, 12000])
ax.set_yticklabels(
    ['₩0.0T', '₩0.3T', '₩0.6T', '₩0.9T', '₩1.2T'],
    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
    fontweight='bold',
    color=AXIS_CONFIG['y_tick']['color'],
)
ax.tick_params(axis='y', pad=AXIS_CONFIG['y_tick']['pad'], length=0)

# Style
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.grid(
    True, axis='y',
    color=COLORS['grid'], alpha=0.5,
    linestyle=(0, (3.7, 1.6)), linewidth=1.0,
)
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

# Extra top margin so the highlighted ₩1.05T label never gets clipped
fig.subplots_adjust(top=0.88)
fig.tight_layout(rect=[0, 0, 1, 0.97])

output_dir = 'outputs/charts/korea/payment'
os.makedirs(output_dir, exist_ok=True)
png_path, svg_path = save_chart(fig, 'korea_simple_payment_daily_avg', output_dir)
print(f"Saved: {png_path}")
print(f"Saved: {svg_path}")
plt.close()

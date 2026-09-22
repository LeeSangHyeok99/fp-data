import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
from matplotlib.ticker import MaxNLocator
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI

mpl.rcParams['axes.unicode_minus'] = False

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/theo_monthly_returns.csv')

months = df['Month'].tolist()
series_names = ['Gold', 'S2', 'S3', 'S4']

# Colors (matching Theo brand palette from image)
GOLD_C = '#C9A84C'
GRAY_C = '#8A8D92'
TEAL_C = '#5BA5A5'
LGRAY_C = '#6A6D72'
series_colors = {'Gold': GOLD_C, 'S2': GRAY_C, 'S3': TEAL_C, 'S4': LGRAY_C}

gold_avg = df['Gold'].mean()

output_dir = 'outputs/charts/theo'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Draw functions
# =============================================================================
def draw_gradient_rounded_bar(ax, x_center, width, height, top_color, alpha=0.95):
    """Gradient bar with rounded top, clipped via imshow"""
    if pd.isna(height) or height <= 0:
        return

    radius = min(width / 2, height * 0.35)
    rect_top = height - radius
    x_left = x_center - width / 2
    x_right = x_center + width / 2

    # Rounded-top path
    theta = np.linspace(0, np.pi, 40)
    arc_x = x_center + radius * np.cos(theta)
    arc_y = rect_top + radius * np.sin(theta)

    verts = [(x_left, 0), (x_right, 0), (x_right, rect_top)]
    for px, py in zip(arc_x, arc_y):
        verts.append((px, py))
    verts.append((x_left, rect_top))
    verts.append((x_left, 0))

    codes = [MPath.MOVETO] + [MPath.LINETO] * (len(verts) - 2) + [MPath.CLOSEPOLY]
    path = MPath(verts, codes)
    clip_patch = PathPatch(path, facecolor='none', edgecolor='none', transform=ax.transData)
    ax.add_patch(clip_patch)

    # Vertical gradient
    r, g, b = mcolors.to_rgb(top_color)
    gradient = np.zeros((256, 1, 4))
    for i in range(256):
        frac = i / 255
        factor = 0.15 + 0.85 * (frac ** 0.5)
        gradient[i, 0] = [r * factor, g * factor, b * factor, alpha]

    im = ax.imshow(gradient, aspect='auto', origin='lower',
                   extent=[x_left, x_right, 0, height],
                   zorder=3, interpolation='bilinear')
    im.set_clip_path(clip_patch)


# =============================================================================
# Chart
# =============================================================================
setup_font()
fig, ax = plt.subplots(figsize=(14, 6), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

bar_width = 0.17
gap = 0.025

for mi in range(len(months)):
    # Collect active series
    active = []
    for s in series_names:
        val = df[s].iloc[mi]
        if pd.notna(val):
            active.append((s, val))

    n = len(active)
    total_w = n * bar_width + (n - 1) * gap
    start_x = mi - total_w / 2 + bar_width / 2

    for bi, (s_name, val) in enumerate(active):
        x = start_x + bi * (bar_width + gap)
        draw_gradient_rounded_bar(ax, x, bar_width, val, series_colors[s_name])


# Gold average dashed line
ax.axhline(y=gold_avg, color=GOLD_C, linestyle='--', linewidth=1.2,
           alpha=0.65, zorder=2, dash_capstyle='round')
ax.text(11.85, gold_avg, f'Gold Avg: {gold_avg:.2f}%',
        ha='right', va='bottom', fontsize=14, fontweight='bold',
        color=GOLD_C, alpha=0.85, zorder=5)

# X-axis
ax.set_xticks(range(12))
ax.set_xticklabels([f'{m}\n25' for m in months],
                    fontsize=14, fontweight='bold',
                    color='#9B9EA3')
ax.tick_params(axis='x', length=0, pad=12)

# Y-axis
ax.yaxis.set_visible(True)
ax.set_yticks([0, 4, 8, 12, 16])
ax.set_yticklabels(['0%', '4%', '8%', '12%', '16%'],
                    fontsize=12, fontweight='bold', color='#9B9EA3')
ax.tick_params(axis='y', length=0, pad=10)

# Limits
ax.set_xlim(-0.8, 12.0)
ax.set_ylim(0, 17.5)

# Grid (subtle horizontal)
ax.grid(True, axis='y', color='#787b86', alpha=0.3,
        linestyle=(0, (3.7, 1.6)), linewidth=0.8)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

# Save
fig.savefig(f'{output_dir}/theo_monthly_returns.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/theo_monthly_returns.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)

print(f"Saved: {output_dir}/theo_monthly_returns.png")
print(f"Gold Avg: {gold_avg:.2f}%")

# Stats
for s in series_names:
    vals = df[s].dropna()
    if len(vals) > 0:
        print(f"{s}: avg={vals.mean():.2f}%, min={vals.min():.2f}%, max={vals.max():.2f}%, months={len(vals)}")

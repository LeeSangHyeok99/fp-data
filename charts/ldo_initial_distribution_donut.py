"""
LDO Tokenomics — Initial Distribution (Dec 2020) — donut chart
Style: four-pillars, transparent BG, no title/legend/source.
Internalized onto brand background as a second output.
Data: outputs/data/ldo_initial_distribution.csv
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import setup_font, save_chart, COLORS, SERIES_COLORS, DPI

setup_font()

# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------
df = pd.read_csv('outputs/data/ldo_initial_distribution.csv')

labels = df['category'].tolist()
values = df['share_pct'].tolist()

# ----------------------------------------------------------------------
# Style knobs — tweak these
# ----------------------------------------------------------------------
PCT_FONTSIZE = 20          # percent label font size on slices
PCT_FONTWEIGHT = 'bold'    # percent label weight
PCT_TEXT_COLOR = '#ffffff' # unified percent label color

# Per-category brand colors
CATEGORY_COLORS = {
    'DAO Treasury':         '#00A3FF',
    'Investors':            '#0066CC',
    'Initial developers':   '#53D3FF',
    'Founders & employees': '#B8E7FF',
    'Validators & signers': '#0B1B2B',
}
colors = [CATEGORY_COLORS.get(lbl, SERIES_COLORS[i % len(SERIES_COLORS)])
          for i, lbl in enumerate(labels)]
color_map = dict(zip(labels, colors))

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
fig = plt.figure(figsize=(9.5, 9.5), dpi=DPI)
fig.patch.set_alpha(0)
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
ax.set_facecolor('none')

RING_WIDTH = 0.42
SLICE_R = 1.0 - RING_WIDTH / 2

wedges, _ = ax.pie(
    values,
    colors=colors,
    startangle=90,
    counterclock=False,
    wedgeprops={'width': RING_WIDTH, 'edgecolor': COLORS['background'],
                'linewidth': 2},
    radius=1.0,
)

# Center text
ax.text(0, 0.08, '1B LDO', ha='center', va='center',
        fontsize=22, fontweight='bold', color=COLORS['text'])
ax.text(0, -0.10, 'Dec 2020', ha='center', va='center',
        fontsize=15, fontweight='bold', color=COLORS['text_secondary'])

# ----------------------------------------------------------------------
# Labels — name + % inside larger slices, leader line for the small one
# ----------------------------------------------------------------------
INSIDE_THRESHOLD = 0.0  # legend carries names; show % inside every slice

for w, label, val in zip(wedges, labels, values):
    ang = np.deg2rad((w.theta1 + w.theta2) / 2)
    x, y = np.cos(ang), np.sin(ang)

    if val >= INSIDE_THRESHOLD:
        ax.text(SLICE_R * x, SLICE_R * y, f'{val:.1f}%',
                ha='center', va='center', fontsize=PCT_FONTSIZE,
                fontweight=PCT_FONTWEIGHT, color=PCT_TEXT_COLOR)
    else:
        ha = 'left' if x >= 0 else 'right'
        lx, ly = 1.30 * x, 1.18 * y
        ax.plot([1.02 * x, 1.16 * x], [1.02 * y, 1.12 * y],
                color=color_map[label], lw=1.4, zorder=1)
        ax.text(lx, ly, f'{val:.1f}%',
                ha=ha, va='center', fontsize=PCT_FONTSIZE,
                fontweight=PCT_FONTWEIGHT, color=PCT_TEXT_COLOR)

ax.set_xlim(-1.55, 1.55)
ax.set_ylim(-1.45, 1.45)
ax.set_aspect('equal')

out_dir = 'outputs/charts/lido/token'
png, svg = save_chart(fig, 'ldo_initial_distribution_donut', out_dir)
plt.close(fig)

# ----------------------------------------------------------------------
# Internalize: composite onto brand background
# ----------------------------------------------------------------------
from PIL import Image

PAD = 80
chart = Image.open(png).convert('RGBA')
canvas = Image.new('RGBA', (chart.width + PAD * 2, chart.height + PAD * 2),
                   COLORS['background'])
canvas.alpha_composite(chart, (PAD, PAD))
bg_png = f'{out_dir}/ldo_initial_distribution_donut_bg.png'
canvas.convert('RGB').save(bg_png)

print('saved:', png)
print('internalized:', bg_png)
print('slices:', list(zip(labels, values)))

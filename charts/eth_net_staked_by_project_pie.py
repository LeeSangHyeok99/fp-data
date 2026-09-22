"""
Net Staked by Project (ETH) — pie chart
Style: four-pillars, transparent BG, no title/legend/source.
Top 9 projects named, remainder grouped into "Other".
Data: outputs/data/eth_net_staked_by_project.csv
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
df = pd.read_csv('outputs/data/eth_net_staked_by_project.csv')
df = df.sort_values('share_pct', ascending=False).reset_index(drop=True)

TOP_N = 5
top = df.iloc[:TOP_N].copy()

labels = top['project'].tolist()
values = top['share_pct'].tolist()

# Everything not in the top N (incl. projects below the table cutoff) → Others
other_share = round(100.0 - sum(values), 1)
labels.append('Others')
values.append(other_share)

# ----------------------------------------------------------------------
# Style knobs
# ----------------------------------------------------------------------
LABEL_FONTSIZE = 22        # name + % font size on big slices
LABEL_FONTSIZE_SMALL = 18  # font size on thin slices (moved outside)
SMALL_THRESHOLD = 20       # below this %, label sits outside the ring

# Per-project brand colors (from reference image)
PROJECT_COLORS = {
    'Lido':     '#48A0F8',
    'Coinbase': '#2151F5',
    'Bitmine':  '#121826',
    'Binance':  '#EABC4E',
    'Ether.fi': '#645EA3',
    'Others':   '#4B534F',
}

colors = [PROJECT_COLORS.get(lbl, SERIES_COLORS[i % len(SERIES_COLORS)])
          for i, lbl in enumerate(labels)]
color_map = dict(zip(labels, colors))

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
fig = plt.figure(figsize=(9.6, 9.6), dpi=DPI)
fig.patch.set_alpha(0)
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
ax.set_facecolor('none')

RING_WIDTH = 0.42
SLICE_R = 1.0 - RING_WIDTH / 2  # mid-ring radius for inside labels

wedges, _ = ax.pie(
    values,
    colors=colors,
    startangle=90,
    counterclock=False,
    wedgeprops={'width': RING_WIDTH, 'edgecolor': COLORS['background'],
                'linewidth': 2},
    radius=1.0,
)

# ----------------------------------------------------------------------
# Labels — name + % outside, with short leader lines
# ----------------------------------------------------------------------
# All labels sit inside the ring; thin slices get a smaller font
for w, label, val in zip(wedges, labels, values):
    ang = np.deg2rad((w.theta1 + w.theta2) / 2)
    x, y = np.cos(ang), np.sin(ang)
    txt = f'{label}\n{val:.1f}%'

    if val >= SMALL_THRESHOLD:
        # fits inside the ring
        ax.text(SLICE_R * x, SLICE_R * y, txt,
                ha='center', va='center', fontsize=LABEL_FONTSIZE,
                fontweight='bold', color='#ffffff', linespacing=1.25)
    else:
        # thin slice → push label outside with a short leader line
        ha = 'left' if x >= 0 else 'right'
        lx, ly = 1.32 * x, 1.30 * y
        ax.plot([1.02 * x, 1.18 * x], [1.02 * y, 1.18 * y],
                color=color_map[label], lw=1.6, zorder=1)
        ax.text(lx, ly, txt, ha=ha, va='center',
                fontsize=LABEL_FONTSIZE_SMALL, fontweight='bold',
                color='#ffffff', linespacing=1.25)

ax.set_xlim(-1.45, 1.45)
ax.set_ylim(-1.40, 1.40)
ax.set_aspect('equal')  # 1:1 — round donut, no distortion

out_dir = 'outputs/charts/ethereum/staking'
png, svg = save_chart(fig, 'eth_net_staked_by_project_pie', out_dir)
plt.close(fig)

# ----------------------------------------------------------------------
# Internalize: composite the transparent chart onto the brand background
# ----------------------------------------------------------------------
from PIL import Image

PAD = 80  # px margin around the chart
chart = Image.open(png).convert('RGBA')
canvas = Image.new('RGBA', (chart.width + PAD * 2, chart.height + PAD * 2),
                   COLORS['background'])
canvas.alpha_composite(chart, (PAD, PAD))
bg_png = f'{out_dir}/eth_net_staked_by_project_pie_bg.png'
canvas.convert('RGB').save(bg_png)

print('saved:', png)
print('internalized:', bg_png)
print('slices:', list(zip(labels, values)))

"""
Japanese Security Token (ST) market — issuance amount share by asset type — donut
As of March 2026. Unit: ¥100M (oku-yen). Total ¥3,601 (≈ ¥360.1B).
Style: four-pillars donut, center total, no title/legend/source.
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import setup_font, DPI

setup_font()

# Keep text as editable <text> elements in SVG (not converted to paths)
plt.rcParams['svg.fonttype'] = 'none'

# ----------------------------------------------------------------------
# Data (table order preserved)
# ----------------------------------------------------------------------
data = [
    ('Real estate ST',       2873, 79.8),
    ('Bond ST (corporate)',   616, 17.1),
    ('Equity interest ST',    109,  3.0),
    ('Monetary claims ST',      3,  0.1),
]
df = pd.DataFrame(data, columns=['asset_type', 'amount_oku_yen', 'share_pct'])
df.to_csv('outputs/data/jp_st_issuance_share_by_asset.csv', index=False)

labels = df['asset_type'].tolist()
values = df['amount_oku_yen'].tolist()
total_label = '¥3,601'
total_sub = '≈ ¥360.1B'

color_map = {
    'Real estate ST':       '#2C6CDF',   # 블루
    'Bond ST (corporate)':  '#4b4f57',   # 차콜
    'Equity interest ST':   '#73c0de',   # 라이트 블루
    'Monetary claims ST':   '#26a69a',   # 그린
}
colors = [color_map[l] for l in labels]

LEADER_COLOR = '#9aa0aa'
LABEL_COLOR = '#d1d4dc'
LABEL_FS = 15

# ----------------------------------------------------------------------
# Figure (transparent BG — four-pillars standard)
# ----------------------------------------------------------------------
fig = plt.figure(figsize=(7.5, 7.5), dpi=DPI)
fig.patch.set_alpha(0)
ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
ax.set_facecolor('none')

wedges, _ = ax.pie(
    values,
    colors=colors,
    startangle=90,
    counterclock=False,
    wedgeprops={'width': 0.40, 'edgecolor': 'none', 'linewidth': 0},
)

# ----------------------------------------------------------------------
# Slice labels — all outside the ring with elbow leader lines (uniform)
# ----------------------------------------------------------------------
total = sum(values)
angle_start = 90
mids = {}
for label, value in zip(labels, values):
    sweep = value / total * 360
    mids[label] = angle_start - sweep / 2
    angle_start -= sweep

# Per-slice elbow landing: (break_radius, text_x, text_y, ha)
# Small top slices fanned out horizontally to avoid collision.
# Per-slice label landing: (label_x, ha). Elbow leader = short radial out
# then a small horizontal bend (ㄱ shape) to the label. Top slices fanned
# left/right so they don't collide.
R_BREAK = 1.10
landing = {
    'Real estate ST':      (0.82,  'left'),    # lower-right
    'Bond ST (corporate)': (-0.92, 'right'),   # upper-left
    'Equity interest ST':  (-0.58, 'right'),   # top, fan left
    'Monetary claims ST':  (0.46,  'left'),    # top, fan right
}

for label, value in zip(labels, values):
    pct = value / total * 100
    ar = np.radians(mids[label])
    cos_a, sin_a = np.cos(ar), np.sin(ar)
    label_x, ha = landing[label]
    slice_color = color_map[label]

    x_edge, y_edge = 1.0 * cos_a, 1.0 * sin_a          # ring outer edge
    x_br, y_br = R_BREAK * cos_a, R_BREAK * sin_a      # radial break point
    x_h = label_x + (0.05 if ha == 'right' else -0.05)  # horizontal end (gap to label)

    # ㄱ-shaped elbow: radial out, then small horizontal bend, colored by slice
    ax.plot([x_edge, x_br, x_h], [y_edge, y_br, y_br],
            color=slice_color, linewidth=1.4, zorder=4,
            solid_capstyle='round', solid_joinstyle='round')

    ax.text(label_x, y_br, f'{pct:.1f}%', ha=ha, va='center',
            fontsize=LABEL_FS, fontweight='bold', color=LABEL_COLOR, zorder=5)

# ----------------------------------------------------------------------
# Center value (single line, no "Total" label)
# ----------------------------------------------------------------------
ax.text(0, 0, total_sub.replace('≈ ', ''), ha='center', va='center',
        fontsize=27, fontweight='bold', color='#c8ccd4', zorder=5)

ax.set_aspect('equal')
ax.set_xlim(-1.45, 1.45)
ax.set_ylim(-1.45, 1.45)
ax.axis('off')

# ----------------------------------------------------------------------
# Save (transparent)
# ----------------------------------------------------------------------
output_dir = 'outputs/charts/rwa/security_token'
os.makedirs(output_dir, exist_ok=True)
png_path = os.path.join(output_dir, 'jp_st_issuance_share_by_asset.png')
svg_path = os.path.join(output_dir, 'jp_st_issuance_share_by_asset.svg')
fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none',
            bbox_inches='tight', transparent=True)
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none',
            bbox_inches='tight', transparent=True)
print(f'Saved: {png_path}')
plt.close(fig)

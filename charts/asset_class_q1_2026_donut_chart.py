"""
Q1 2026 Asset Class Volume Share — donut chart
Style: transparent BG, no title, no leader lines, thicker ring,
       all percentages labeled.
Data: outputs/data/section_3_4_asset_class.csv
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

# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------
df_raw = pd.read_csv('outputs/data/section_3_4_asset_class.csv')

df = df_raw[df_raw['Asset class'] != 'TOTAL PLATFORM Q1 2026'].copy()
df = df[df['Q1 share of platform total (%)'] > 0].copy()

total_row = df_raw[df_raw['Asset class'] == 'TOTAL PLATFORM Q1 2026'].iloc[0]
total_q1_usd = float(total_row['Cumulative volume Q1 2026 (USD)'])
total_volume_label = f'${total_q1_usd / 1e9:.2f}B USD'

# Group very small slices (< 1%) into "Other"
SMALL_THRESHOLD = 1.0
big = df[df['Q1 share of platform total (%)'] >= SMALL_THRESHOLD].copy()
small = df[df['Q1 share of platform total (%)'] < SMALL_THRESHOLD].copy()
big = big.sort_values('Q1 share of platform total (%)', ascending=False)

labels = big['Asset class'].tolist()
values = big['Q1 share of platform total (%)'].tolist()
if len(small) > 0:
    other_pct = small['Q1 share of platform total (%)'].sum()
    labels.append('Other')
    values.append(other_pct)

# Visual sizing: bump tiny slices up to a minimum sweep so % labels fit
# inside the ring. Actual percentages are preserved for label text.
MIN_DISPLAY_PCT = 4.0
display_values = []
for v in values:
    display_values.append(max(v, MIN_DISPLAY_PCT))
# Rescale so display_values still sum to 100 (preserve angular proportions
# of larger slices among themselves)
small_idx = [i for i, v in enumerate(values) if v < MIN_DISPLAY_PCT]
big_idx = [i for i, v in enumerate(values) if v >= MIN_DISPLAY_PCT]
small_sum_display = sum(display_values[i] for i in small_idx)
big_sum_actual = sum(values[i] for i in big_idx)
big_target = 100 - small_sum_display
if big_sum_actual > 0:
    scale = big_target / big_sum_actual
    for i in big_idx:
        display_values[i] = values[i] * scale

short_label = {
    'Commodities (Precious Metals)':   'Precious Metals',
    'Commodities (Energy)':            'Energy',
    'Indices (Equity)':                'Equity Indices',
    'Equities (US Single-Name)':       'US Equities',
    'Commodities (Industrial Metals)': 'Industrial Metals',
    'Forex':                           'Forex',
    'Other':                           'Other',
}

color_map = {
    'Commodities (Precious Metals)':   '#C9A84C',
    'Commodities (Energy)':            '#F37228',
    'Indices (Equity)':                '#2C6CDF',
    'Equities (US Single-Name)':       '#4F8D3F',
    'Commodities (Industrial Metals)': '#6D4EC0',
    'Forex':                           '#E5B433',
    'Other':                           '#787b86',
}
colors = [color_map.get(label, '#787b86') for label in labels]

# ----------------------------------------------------------------------
# Figure (transparent BG)
# ----------------------------------------------------------------------
fig = plt.figure(figsize=(8.5, 8.5), dpi=DPI)
fig.patch.set_alpha(0)

# Donut axes (full canvas, no title/legend/source)
ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
ax.set_facecolor('none')

# Thicker ring (0.35 → 0.45)
RING_WIDTH = 0.45

wedges, _ = ax.pie(
    display_values,
    colors=colors,
    startangle=90,
    counterclock=False,
    wedgeprops={'width': RING_WIDTH, 'edgecolor': 'none', 'linewidth': 0},
)

# ----------------------------------------------------------------------
# Slice labels (all inside the ring, using display angles)
# ----------------------------------------------------------------------
display_total = sum(display_values)
slice_meta = []
ang = 90
for label, value, dval in zip(labels, values, display_values):
    actual_pct = value  # values are already in % terms
    sweep = dval / display_total * 360
    mid_angle = ang - sweep / 2
    slice_meta.append({'label': label, 'pct': actual_pct, 'mid_angle': mid_angle})
    ang -= sweep

# Slice middle radius (depends on RING_WIDTH)
SLICE_R = 1.0 - RING_WIDTH / 2  # 0.775 with RING_WIDTH=0.45

for m in slice_meta:
    label = m['label']
    pct = m['pct']
    mid_angle = m['mid_angle']
    angle_rad = np.radians(mid_angle)
    color = colors[labels.index(label)]

    x = SLICE_R * np.cos(angle_rad)
    y = SLICE_R * np.sin(angle_rad)

    if pct >= 10:
        fs = 18
    elif pct >= 5:
        fs = 14
    else:
        fs = 11

    ax.text(x, y, f'{pct:.1f}%',
            ha='center', va='center',
            fontsize=fs, fontweight='bold',
            color='#ffffff', zorder=5)

# ----------------------------------------------------------------------
# Center text
# ----------------------------------------------------------------------
ax.text(0, 0.08, 'Q1 2026 Volume',
        ha='center', va='center',
        fontsize=13, fontweight='bold',
        color='#b0b4bb')
ax.text(0, -0.07, total_volume_label,
        ha='center', va='center',
        fontsize=24, fontweight='bold',
        color='#ffffff')

ax.set_aspect('equal')
ax.set_xlim(-1.45, 1.45)
ax.set_ylim(-1.45, 1.45)
ax.axis('off')

# ----------------------------------------------------------------------
# Save (transparent)
# ----------------------------------------------------------------------
output_dir = 'outputs/charts/platform/asset_class'
os.makedirs(output_dir, exist_ok=True)

png_path = os.path.join(output_dir, 'asset_class_q1_2026_donut_chart.png')
svg_path = os.path.join(output_dir, 'asset_class_q1_2026_donut_chart.svg')

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none',
            bbox_inches='tight', transparent=True)
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none',
            bbox_inches='tight', transparent=True)

print(f'Saved: {png_path}')
print(f'Saved: {svg_path}')
print(f'Slices: {list(zip(labels, [f"{v:.2f}%" for v in values]))}')
plt.close(fig)

"""
Domestic CEX Market Share (3 Months) — donut chart
Single donut showing Upbit / Bithumb / Coinone / Korbit / Gopax share of
3-month Korean CEX spot trading volume. Center value: $217.1B USD.
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
df = pd.read_csv('outputs/data/korea_cex_market_share.csv')

# Preserve table order (Upbit first → Gopax last) for slice arrangement
labels = df['exchange'].tolist()
values = df['share_pct'].tolist()
total_volume_label = '$217.1B USD'

# ----------------------------------------------------------------------
# Colors
# ----------------------------------------------------------------------
color_map = {
    'Upbit':   '#2C6CDF',
    'Bithumb': '#F37228',
    'Coinone': '#4F8D3F',
    'Korbit':  '#6D4EC0',
    'Gopax':   '#E5B433',
}
colors = [color_map[label] for label in labels]

# ----------------------------------------------------------------------
# Figure (dark canvas so white center text reads cleanly)
# ----------------------------------------------------------------------
BG = '#0d0d0d'
fig, ax = plt.subplots(figsize=(7.5, 7.5), dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

wedges, _ = ax.pie(
    values,
    colors=colors,
    startangle=90,
    counterclock=False,
    wedgeprops={'width': 0.35, 'edgecolor': 'none', 'linewidth': 0},
)

# ----------------------------------------------------------------------
# Slice labels
# ----------------------------------------------------------------------
total = sum(values)
angle_start = 90  # start at 12 o'clock

for label, value, wedge in zip(labels, values, wedges):
    pct = value / total * 100
    sweep = value / total * 360
    mid_angle = angle_start - sweep / 2
    angle_rad = np.radians(mid_angle)

    if pct >= 10:
        # Inside wedge label (white)
        r = 0.825
        x = r * np.cos(angle_rad)
        y = r * np.sin(angle_rad)
        ax.text(
            x, y, f'{pct:.1f}%',
            ha='center', va='center',
            fontsize=18, fontweight='bold',
            color='#ffffff',
            zorder=5,
        )
    elif pct >= 5:
        # Mid slice: inside wedge with smaller font
        r = 0.825
        x = r * np.cos(angle_rad)
        y = r * np.sin(angle_rad)
        ax.text(
            x, y, f'{pct:.1f}%',
            ha='center', va='center',
            fontsize=13, fontweight='bold',
            color='#ffffff',
            zorder=5,
        )
    else:
        # Small slice: outside wedge with leader line
        r_in = 0.82
        r_break = 1.05
        r_out = 1.18
        x_in = r_in * np.cos(angle_rad)
        y_in = r_in * np.sin(angle_rad)
        x_break = r_break * np.cos(angle_rad)
        y_break = r_break * np.sin(angle_rad)

        # Push small slices to fixed horizontal landings so they don't
        # collide near the 12 o'clock area.
        deg = mid_angle % 360
        if 0 <= deg <= 180:
            x_text = abs(r_out * np.cos(angle_rad)) + 0.05
            ha = 'left'
        else:
            x_text = -(abs(r_out * np.cos(angle_rad)) + 0.05)
            ha = 'right'
        y_text = y_break

        # Spread vertically based on slice index for top-cluster slices
        if 60 < deg < 120:
            # Top-cluster: anchor by slice index using mid_angle order
            x_text = (1.20 if mid_angle < 100 else 1.30) * np.cos(angle_rad) + (
                0.10 if np.cos(angle_rad) >= 0 else -0.10
            )
            y_text = 1.10 + (0.12 if pct < 3 else 0)

        ax.plot(
            [x_in, x_break, x_text - (0.04 if ha == 'left' else -0.04)],
            [y_in, y_break, y_text],
            color=color_map[label], linewidth=1.2, alpha=0.85,
            zorder=4,
        )
        ax.text(
            x_text, y_text, f'{pct:.1f}%',
            ha=ha, va='center',
            fontsize=13, fontweight='bold',
            color=color_map[label],
            zorder=5,
        )

    angle_start -= sweep

# ----------------------------------------------------------------------
# Center text
# ----------------------------------------------------------------------
ax.text(
    0, 0.10, 'Total Volume (3 Months)',
    ha='center', va='center',
    fontsize=13, fontweight='bold',
    color='#b0b4bb',
)
ax.text(
    0, -0.08, total_volume_label,
    ha='center', va='center',
    fontsize=24, fontweight='bold',
    color='#ffffff',
)

ax.set_aspect('equal')
ax.set_xlim(-1.35, 1.35)
ax.set_ylim(-1.35, 1.35)
ax.axis('off')

# ----------------------------------------------------------------------
# Save (transparent PNG + SVG)
# ----------------------------------------------------------------------
output_dir = 'outputs/charts/korea/cex'
os.makedirs(output_dir, exist_ok=True)

png_path = os.path.join(output_dir, 'korea_cex_market_share_donut.png')
svg_path = os.path.join(output_dir, 'korea_cex_market_share_donut.svg')

fig.savefig(png_path, dpi=DPI, facecolor=BG, edgecolor='none',
            bbox_inches='tight')
fig.savefig(svg_path, format='svg', facecolor=BG, edgecolor='none',
            bbox_inches='tight')

print(f'Saved: {png_path}')
print(f'Saved: {svg_path}')
plt.close(fig)

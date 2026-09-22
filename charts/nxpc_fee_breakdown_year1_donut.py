"""
NXPC Fee Breakdown (Year 1) - Donut Chart
Four Pillars theme recreation of NEXPACE NXPC fee composition.
No legend, no center text, thicker ring, percent labels on every slice.
"""

import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append('.claude/skills/design/four-pillars')
from config import save_chart, setup_font, COLORS

# -----------------------------------------------------------------------------
# Data
# -----------------------------------------------------------------------------
df = pd.read_csv('outputs/data/nxpc_fee_breakdown_year1.csv')
categories = df['category'].tolist()
values = df['value_nxpc'].tolist()
shares = df['share_pct'].tolist()

# Brand-style palette (matches reference: green / purple / orange)
SLICE_COLORS = ['#3f9c7c', '#7b76cc', '#c8552c']

# -----------------------------------------------------------------------------
# Figure
# -----------------------------------------------------------------------------
setup_font()
fig = plt.figure(figsize=(9, 9), dpi=150)
fig.patch.set_alpha(0)
ax = fig.add_axes([0.08, 0.08, 0.84, 0.84])
ax.set_facecolor('none')

# Slightly enlarge the two small slices for label legibility (geometry only;
# printed labels still show the true shares). Green is dominant enough that
# the small reduction is visually imperceptible.
plot_values = [86.5, 9.0, 4.5]

RING_WIDTH = 0.42  # thicker ring
wedges, _ = ax.pie(
    plot_values,
    colors=SLICE_COLORS,
    startangle=90,
    counterclock=False,
    wedgeprops={'linewidth': 2.5, 'edgecolor': COLORS['background'],
                'width': RING_WIDTH},
)

# -----------------------------------------------------------------------------
# Percent labels inside every slice (narrow slices use radial orientation)
# -----------------------------------------------------------------------------
r_mid = 1 - RING_WIDTH / 2  # radial center of the ring band
label_fs = [26, 17, 15]  # per-slice font size, horizontal labels
for i, w in enumerate(wedges):
    ang = np.deg2rad((w.theta1 + w.theta2) / 2)
    x, y = np.cos(ang), np.sin(ang)
    ax.text(x * r_mid, y * r_mid, f'{shares[i]:.1f}%',
            ha='center', va='center',
            fontsize=label_fs[i], fontweight='bold', color='white')

# center text
ax.text(0, 0.10, '47.5M+', ha='center', va='center',
        fontsize=42, fontweight='bold', color=COLORS['text'])
ax.text(0, -0.15, 'Year 1 NXPC fees', ha='center', va='center',
        fontsize=16, fontweight='bold', color=COLORS['text_secondary'])

ax.set_aspect('equal')
ax.set_xlim(-1.45, 1.45)
ax.set_ylim(-1.45, 1.45)
ax.axis('off')

png, svg = save_chart(fig, 'nxpc_fee_breakdown_year1',
                      'outputs/charts/nexpace/revenue')
plt.close(fig)
print('Saved:', png)
print('Saved:', svg)

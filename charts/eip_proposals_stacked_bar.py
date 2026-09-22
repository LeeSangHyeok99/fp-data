import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from pathlib import Path

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import (
    create_figure, apply_style, save_chart,
    SERIES_COLORS, COLORS, AXIS_CONFIG
)

# ── Data (real, Aug 2025 → Jul 2026) ──
df = pd.read_csv('outputs/data/eip_proposals_monthly.csv')

# ── Labels (Mon YYYY format) ──
month_labels = pd.to_datetime(df['month']).dt.strftime('%b %Y').tolist()

# ── Categories (stacking order: bottom → top) ──
categories = ['Core', 'ERC', 'Interface', 'Networking', 'Meta', 'Informational', 'RIP']

# ── Color mapping (pastel tones, higher saturation for clarity) ──
color_map = {
    'Core':          '#c9a0dc',   # purple
    'ERC':           '#8daae8',   # blue
    'Interface':     '#7ec8e3',   # sky blue
    'Networking':    '#6ec6a5',   # mint
    'Meta':          '#c5e17a',   # yellow-green
    'Informational': '#ffb974',   # orange
    'RIP':           '#f48fb1',   # pink
}

# ── Create figure ──
fig, ax = create_figure('stacked_bar')

x = np.arange(len(month_labels))
bar_width = 0.55

# ── Stacked bars ──
bottom = np.zeros(len(month_labels))
for cat in categories:
    values = df[cat].values.astype(float)
    ax.bar(x, values, bar_width, bottom=bottom,
           color=color_map[cat], label=cat, alpha=0.9,
           edgecolor='#1a1a1a', linewidth=0.5)
    bottom += values

# ── X-axis ──
ax.set_xticks(x)
ax.set_xticklabels(month_labels)

# ── Y-axis (max 5 ticks) ──
ax.set_ylim(0, 30)
ax.set_yticks([0, 10, 20, 30])

# ── Highlight last bar (most recent month) with green border ──
last_x = x[-1]
last_total = bottom[-1]
rect = plt.Rectangle(
    (last_x - bar_width / 2 - 0.06, -0.5),
    bar_width + 0.12,
    last_total + 1.0,
    linewidth=2.5,
    edgecolor='#26a69a',
    facecolor='none',
    zorder=10,
    clip_on=False,
)
ax.add_patch(rect)

# ── Apply four-pillars style ──
apply_style(fig, ax, 'stacked_bar')

# ── X-tick rotation (longer labels → 45deg) ──
plt.setp(ax.xaxis.get_majorticklabels(),
         rotation=45, ha='right', fontweight='bold', fontsize=20)

# ── Y-tick formatting ──
for label in ax.yaxis.get_ticklabels():
    label.set_fontweight('bold')

# ── Save ──
png_path, svg_path = save_chart(fig, 'eip_proposals_stacked_bar', 'outputs/charts/ethereum/eip')
plt.close(fig)

print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")

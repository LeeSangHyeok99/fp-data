"""
Stablecoin 1Y Net Flows - Horizontal Bar Chart (Gradient)
Data source: RWA.xyz (app.rwa.xyz/stablecoins) - Stablecoin Net Flows, Period: 1Y
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
from pathlib import Path
from config import create_figure, apply_style, save_chart, COLORS, AXIS_CONFIG

# Font
pretendard_path = Path('assets/font/Pretendard/Pretendard-Bold.ttf')
if pretendard_path.exists():
    fm.fontManager.addfont(str(pretendard_path))
    pretendard_font = fm.FontProperties(fname=str(pretendard_path))
else:
    pretendard_font = None

# ─── Gradient bar helper (imshow + clip, smooth in SVG) ────────────────
def gradient_hbar(ax, y_center, width, height, color):
    """Horizontal gradient bar using imshow for smooth SVG rendering."""
    from matplotlib.patches import Rectangle
    r, g, b = mcolors.to_rgb(color)
    # Create gradient image (1 row, 256 cols)
    gradient = np.zeros((1, 256, 4))
    for i in range(256):
        frac = i / 255
        factor = 0.25 + 0.75 * (frac ** 0.5)
        gradient[0, i] = [r * factor, g * factor, b * factor, 1.0]
    # Draw clipped image
    x0, x1 = 0, width
    y0, y1 = y_center - height / 2, y_center + height / 2
    im = ax.imshow(gradient, aspect='auto', origin='lower',
                   extent=[x0, x1, y0, y1], zorder=3, interpolation='bicubic')
    clip_rect = Rectangle((x0, y0), width, height, transform=ax.transData)
    im.set_clip_path(clip_rect)


# ─── Data (from RWA.xyz Stablecoin Net Flows, 1Y, as of 2026-04-10) ───
data = [
    ('USDT', 'Tether Holdings', 44.6, '#26a17b'),
    ('USDC', 'Circle', 18.2, '#2775ca'),
    ('USD1', 'BitGo', 4.3, '#e63946'),
    ('USDS', 'Sky', 3.6, '#1fc7a0'),
    ('PYUSD', 'Paxos', 3.5, '#003087'),
    ('DAI', 'MakerDAO', 2.3, '#f5ac37'),
    ('USDG', 'Paxos', 1.7, '#00b894'),
    ('USDf', 'Falcon Finance', 1.6, '#9a60b4'),
]

# Reverse for bar chart (top at top)
data = data[::-1]
names = [d[0] for d in data]
values = [d[2] for d in data]
colors = [d[3] for d in data]

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('horizontal_bar')

bar_height = 0.6
for i, (name, val, color) in enumerate(zip(names, values, colors)):
    gradient_hbar(ax, i, val, bar_height, color)

# Value labels
for i, (name, val) in enumerate(zip(names, values)):
    label = f'+${val:.1f}B'
    ax.text(val + 0.3, i, label, va='center', ha='left',
            fontsize=14, fontweight='bold', color=COLORS['text'],
            fontproperties=pretendard_font)

# ─── Y axis ─────────────────────────────────────────────────────────────
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=16, fontweight='bold',
                   color=COLORS['text'], fontproperties=pretendard_font)

# ─── X axis ─────────────────────────────────────────────────────────────
ax.tick_params(axis='x', labelsize=0, length=0)
ax.set_xticklabels([])

# ─── Style ──────────────────────────────────────────────────────────────
apply_style(fig, ax, 'horizontal_bar')
ax.grid(False)
ax.tick_params(axis='y', length=0, pad=10)
ax.set_xlim(0, max(values) * 1.3)

# ─── Save ───────────────────────────────────────────────────────────────
output_dir = 'outputs/charts/stablecoin/marketcap'
png_path, svg_path = save_chart(fig, 'stablecoin_1y_net_flows', output_dir)
plt.close()
print(f'Saved: {png_path}')

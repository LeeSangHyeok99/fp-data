"""
Stablecoin Market Cap by Network - Horizontal Bar Chart (Gradient)
Data source: RWA.xyz (app.rwa.xyz/stablecoins)
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

# ─── Gradient bar helper ───────────────────────────────────────────────
def gradient_hbar(ax, y_center, width, height, color):
    """Horizontal gradient bar using imshow for smooth SVG rendering."""
    from matplotlib.patches import Rectangle
    r, g, b = mcolors.to_rgb(color)
    gradient = np.zeros((1, 256, 4))
    for i in range(256):
        frac = i / 255
        factor = 0.25 + 0.75 * (frac ** 0.5)
        gradient[0, i] = [r * factor, g * factor, b * factor, 1.0]
    x0, x1 = 0, width
    y0, y1 = y_center - height / 2, y_center + height / 2
    im = ax.imshow(gradient, aspect='auto', origin='lower',
                   extent=[x0, x1, y0, y1], zorder=3, interpolation='bicubic')
    clip_rect = Rectangle((x0, y0), width, height, transform=ax.transData)
    im.set_clip_path(clip_rect)


# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/rwa_stablecoin_by_network_timeseries.csv')
df['Date'] = pd.to_datetime(df['Date'])
latest = df.iloc[-1]

cols = df.columns[3:]
vals = [(col, latest[col]) for col in cols if pd.notna(latest[col]) and latest[col] > 0]
vals.sort(key=lambda x: x[1], reverse=True)

top10 = vals[:10]
names = [v[0] for v in top10][::-1]
values = [v[1] / 1e9 for v in top10][::-1]

network_colors = {
    'Ethereum': '#627eea', 'TRON': '#ff0013', 'Solana': '#9945ff',
    'BNB Chain': '#f0b90b', 'Arbitrum': '#28a0f0', 'Base': '#0052ff',
    'Polygon': '#8247e5', 'Avalanche C-Chain': '#e84142',
    'Aptos': '#2dd8a3', 'Provenance': '#5470c6',
}

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('horizontal_bar')

# ─── Gradient Horizontal Bars ──────────────────────────────────────────
bar_height = 0.6
total = sum(v[1] for v in vals)
for i, (name, val) in enumerate(zip(names, values)):
    color = network_colors.get(name, '#787b86')
    gradient_hbar(ax, i, val, bar_height, color)

# Value labels
for i, (name, val) in enumerate(zip(names, values)):
    pct = val * 1e9 / total * 100
    label = f'${val:.1f}B ({pct:.1f}%)'
    ax.text(val + 1.5, i, label, va='center', ha='left',
            fontsize=13, fontweight='bold', color=COLORS['text'],
            fontproperties=pretendard_font)

# ─── Y axis ─────────────────────────────────────────────────────────────
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=15, fontweight='bold',
                   color=COLORS['text'], fontproperties=pretendard_font)

# ─── X axis ─────────────────────────────────────────────────────────────
ax.tick_params(axis='x', labelsize=0, length=0)
ax.set_xticklabels([])

# ─── Style ──────────────────────────────────────────────────────────────
apply_style(fig, ax, 'horizontal_bar')
ax.grid(False)
ax.tick_params(axis='y', length=0, pad=10)
ax.set_xlim(0, max(values) * 1.35)

# ─── Save ───────────────────────────────────────────────────────────────
output_dir = 'outputs/charts/stablecoin/marketcap'
png_path, svg_path = save_chart(fig, 'stablecoin_marketcap_by_network', output_dir)
plt.close()
print(f'Saved: {png_path}')

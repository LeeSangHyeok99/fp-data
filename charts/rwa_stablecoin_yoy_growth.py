"""
Stablecoin YoY Growth - Horizontal Bar Chart (Gradient)
Fastest-growing stablecoins over the past 12 months
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
df = pd.read_csv('outputs/data/rwa_stablecoin_marketcap_timeseries.csv')
df['Date'] = pd.to_datetime(df['Date'])
latest = df.iloc[-1]
y1_ago = df.iloc[max(0, len(df) - 366)]

cols = df.columns[3:]
growers = []
for col in cols:
    if col == 'All Others (55 Items)':
        continue
    v_now = latest[col] if pd.notna(latest[col]) else 0
    v_1y = y1_ago[col] if pd.notna(y1_ago[col]) else 0
    if v_now > 400e6:
        abs_growth = (v_now - v_1y) / 1e6
        if v_1y > 10e6:
            pct = (v_now / v_1y - 1) * 100
        else:
            pct = 9999
        growers.append((col, v_1y / 1e6, v_now / 1e6, abs_growth, pct))

# Sort by absolute growth (= 1Y net inflow)
# Exclude USDT/USDC (too large, distorts scale), take top 10 challengers
growers.sort(key=lambda x: x[3], reverse=True)
top = [g for g in growers if g[0] not in ['Tether USDt', 'USDC']][:10]
top = top[::-1]  # reverse for bar chart (top at top)

name_map = {
    'Tether USDt': 'USDT', 'Dai Stablecoin': 'DAI', 'Ethena USDe': 'USDe',
    'Paypal USD': 'PYUSD', 'Global Dollar': 'USDG', 'Falcon USD': 'USDf',
    'Ripple USD': 'RLUSD',
}

names = [name_map.get(g[0], g[0]) for g in top]
values = [g[3] for g in top]  # absolute growth in $M (= 1Y net inflow)
pcts = [g[4] for g in top]
current_vals = [g[2] for g in top]

# ─── Colors ─────────────────────────────────────────────────────────────
brand_colors = {
    'USDT': '#26a17b', 'USDC': '#2775ca',
    'USDS': '#1fc7a0', 'USDe': '#b8b8d1', 'DAI': '#f5ac37',
    'USD1': '#e63946', 'PYUSD': '#003087', 'USDG': '#00b894',
    'USDf': '#9a60b4', 'RLUSD': '#0052ff', 'GHO': '#5470c6',
    'EURC': '#2775ca', 'YLDS': '#73c0de',
}

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('horizontal_bar')

bar_height = 0.6
for i, (name, val) in enumerate(zip(names, values)):
    color = brand_colors.get(name, '#5470c6')
    gradient_hbar(ax, i, val, bar_height, color)

# Value labels: show 1Y net inflow amount
for i, (name, val, pct, cur) in enumerate(zip(names, values, pcts, current_vals)):
    if val >= 1000:
        inflow = f'+${val/1e3:.1f}B'
    else:
        inflow = f'+${val:.0f}M'
    if pct > 5000:
        label = f'{inflow} (NEW)'
    else:
        label = f'{inflow} (+{pct:.0f}%)'
    ax.text(val + 40, i, label, va='center', ha='left',
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
ax.set_xlim(0, max(values) * 1.5)

# ─── Save ───────────────────────────────────────────────────────────────
output_dir = 'outputs/charts/stablecoin/marketcap'
png_path, svg_path = save_chart(fig, 'stablecoin_yoy_growth', output_dir)
plt.close()
print(f'Saved: {png_path}')

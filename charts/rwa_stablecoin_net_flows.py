"""
Stablecoin 30D Net Flows - Horizontal Bar Chart (Gradient)
Data source: RWA.xyz (app.rwa.xyz/stablecoins)
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch
from pathlib import Path
from config import create_figure, apply_style, save_chart, COLORS, AXIS_CONFIG, POSITIVE_COLOR, NEGATIVE_COLOR

# Font
pretendard_path = Path('assets/font/Pretendard/Pretendard-Bold.ttf')
if pretendard_path.exists():
    fm.fontManager.addfont(str(pretendard_path))
    pretendard_font = fm.FontProperties(fname=str(pretendard_path))
else:
    pretendard_font = None

# ─── Gradient bar helper (imshow + clip, smooth in SVG) ────────────────
def gradient_hbar(ax, y_center, width, height, color, direction='right'):
    """Horizontal gradient bar using imshow for smooth SVG rendering."""
    from matplotlib.patches import Rectangle
    r, g, b = mcolors.to_rgb(color)
    gradient = np.zeros((1, 256, 4))
    for i in range(256):
        frac = i / 255
        factor = 0.3 + 0.7 * (frac ** 0.6)
        gradient[0, i] = [r * factor, g * factor, b * factor, 1.0]
    if direction == 'left':
        gradient = gradient[:, ::-1, :]  # flip for negative bars
    y0, y1 = y_center - height / 2, y_center + height / 2
    if direction == 'right':
        x0, x1 = 0, width
    else:
        x0, x1 = width, 0
    im = ax.imshow(gradient, aspect='auto', origin='lower',
                   extent=[x0, x1, y0, y1], zorder=3, interpolation='bicubic')
    clip_rect = Rectangle((min(x0, x1), y0), abs(width), height, transform=ax.transData)
    im.set_clip_path(clip_rect)


# ─── Data ───────────────────────────────────────────────────────────────
df = pd.read_csv('outputs/data/rwa_stablecoin_marketcap_timeseries.csv')
df['Date'] = pd.to_datetime(df['Date'])

latest = df.iloc[-1]
d30_ago = df.iloc[max(0, len(df) - 31)]

cols = df.columns[3:]
all_flows = []
for col in cols:
    if col == 'All Others (55 Items)':
        continue
    v_now = latest[col] if pd.notna(latest[col]) else 0
    v_then = d30_ago[col] if pd.notna(d30_ago[col]) else 0
    if v_now > 200e6 or v_then > 200e6:
        diff = v_now - v_then
        all_flows.append((col, diff / 1e6))

all_flows.sort(key=lambda x: x[1], reverse=True)
top_gainers = [f for f in all_flows if f[1] > 0][:6]
top_losers = [f for f in all_flows if f[1] < 0][-5:]
flows = sorted(top_losers + top_gainers, key=lambda x: x[1])

name_map = {
    'Tether USDt': 'USDT', 'Dai Stablecoin': 'DAI', 'Ethena USDe': 'USDe',
    'Paypal USD': 'PYUSD', 'Global Dollar': 'USDG', 'Falcon USD': 'USDf',
    'Ripple USD': 'RLUSD', 'Usual USD': 'USD0', 'First Digital USD': 'FDUSD',
    'Binance-Peg BUSD': 'BUSD', 'All Others (55 Items)': 'Others',
}

names = [name_map.get(f[0], f[0]) for f in flows]
values = [f[1] for f in flows]

# ─── Figure ─────────────────────────────────────────────────────────────
fig, ax = create_figure('horizontal_bar')

# ─── Gradient Horizontal Bars ──────────────────────────────────────────
bar_height = 0.6
for i, val in enumerate(values):
    color = POSITIVE_COLOR if val >= 0 else NEGATIVE_COLOR
    direction = 'right' if val >= 0 else 'left'
    gradient_hbar(ax, i, val, bar_height, color, direction)

# Value labels
for i, val in enumerate(values):
    if val >= 0:
        ax.text(val + 15, i, f'+${val:.0f}M', va='center', ha='left',
                fontsize=13, fontweight='bold', color=POSITIVE_COLOR,
                fontproperties=pretendard_font)
    else:
        ax.text(val - 15, i, f'${val:.0f}M', va='center', ha='right',
                fontsize=13, fontweight='bold', color=NEGATIVE_COLOR,
                fontproperties=pretendard_font)

# ─── Y axis ─────────────────────────────────────────────────────────────
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=15, fontweight='bold',
                   color=COLORS['text'], fontproperties=pretendard_font)

# ─── X axis ─────────────────────────────────────────────────────────────
ax.axvline(x=0, color=COLORS['text_secondary'], linewidth=0.8, alpha=0.5)
ax.set_xlabel('')
ax.tick_params(axis='x', labelsize=0, length=0)
ax.set_xticklabels([])

# ─── Style ──────────────────────────────────────────────────────────────
apply_style(fig, ax, 'horizontal_bar')
ax.grid(False)
ax.tick_params(axis='y', length=0, pad=10)

x_min = min(values) * 1.4
x_max = max(values) * 1.4
ax.set_xlim(x_min, x_max)

# ─── Save ───────────────────────────────────────────────────────────────
output_dir = 'outputs/charts/stablecoin/marketcap'
png_path, svg_path = save_chart(fig, 'stablecoin_30d_net_flows', output_dir)
plt.close()
print(f'Saved: {png_path}')

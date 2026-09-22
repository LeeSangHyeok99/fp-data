"""
PYUSD Supply (Stacked Area, by Chain) + Monthly Transfer Volume (Line)
Dual-axis chart. Supply + Transfer volume: rwa.xyz (Bridged Token Market Cap, monthly aggregate).
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import to_rgba
from matplotlib.patches import Polygon
from config import create_figure, save_chart, COLORS, AXIS_CONFIG


def gradient_band(ax, x_num, y_lower, y_upper, color, alpha_top=0.98, alpha_bottom=0.55, n=128, zorder=3):
    """Fill the band [y_lower, y_upper] with a vertical alpha gradient of color."""
    rgba = to_rgba(color)
    img = np.empty((n, 1, 4), dtype=float)
    img[..., 0] = rgba[0]
    img[..., 1] = rgba[1]
    img[..., 2] = rgba[2]
    img[..., 3] = np.linspace(alpha_top, alpha_bottom, n)[:, None]

    xmin, xmax = float(x_num[0]), float(x_num[-1])
    ymin, ymax = float(np.min(y_lower)), float(np.max(y_upper))
    im = ax.imshow(
        img, aspect='auto',
        extent=[xmin, xmax, ymax, ymin],
        origin='upper', interpolation='bilinear', zorder=zorder,
    )

    poly_x = np.concatenate([x_num, x_num[::-1]])
    poly_y = np.concatenate([y_upper, y_lower[::-1]])
    clip_poly = Polygon(np.column_stack([poly_x, poly_y]), closed=True, facecolor='none', edgecolor='none')
    ax.add_patch(clip_poly)
    im.set_clip_path(clip_poly)

supply = pd.read_csv('outputs/data/pyusd_supply_by_chain_monthly.csv')
volume = pd.read_csv('outputs/data/pyusd_transfer_volume_monthly.csv')

# Drop incomplete final month for both (May 2026 is partial)
supply['period'] = pd.to_datetime(supply['period'] + '-01')
volume['period'] = pd.to_datetime(volume['period'] + '-01')
supply = supply[supply['period'] < pd.Timestamp('2026-05-01')].sort_values('period').reset_index(drop=True)
volume = volume[volume['period'] < pd.Timestamp('2026-05-01')].sort_values('period').reset_index(drop=True)

series_order = ['Ethereum', 'Solana', 'Arbitrum', 'Stellar']
chain_colors = {
    'Ethereum': '#627eea',
    'Solana':   '#9945ff',
    'Arbitrum': '#28a0f0',
    'Stellar':  '#787b86',
}

fig, ax = create_figure('stacked')

x_supply = supply['period'].values
x_num = mdates.date2num(supply['period'].dt.to_pydatetime())
ys = [supply[c].values / 1e9 for c in series_order]

# Stacked area with vertical alpha gradient per layer
y_cum = np.zeros(len(x_num), dtype=float)
for c, y in zip(series_order, ys):
    y_top = y_cum + y
    gradient_band(ax, x_num, y_cum.copy(), y_top.copy(), chain_colors[c])
    y_cum = y_top

# Right axis: monthly transfer volume (line, $B)
ax2 = ax.twinx()
x_vol = volume['period'].values
y_vol = volume['transfer_volume_usd'].values / 1e9
volume_color = '#FACC15'
ax2.plot(
    x_vol, y_vol,
    color=volume_color, linewidth=2.6, zorder=5,
    marker='o', markersize=4, markerfacecolor=volume_color, markeredgecolor='none',
    clip_on=False,
)

# X-axis
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.setp(ax.get_xticklabels(),
         rotation=30,
         ha='right',
         rotation_mode='anchor',
         fontsize=AXIS_CONFIG['x_tick']['fontsize'],
         fontweight='bold',
         color=AXIS_CONFIG['x_tick']['color'])
ax.tick_params(axis='x', pad=6, length=0)

# Left Y-axis: 0 ~ $5B headroom (peak supply $4.2B Feb 2026), tick labels stay at [0,1,2,3,4]
ax.set_ylim(0, 5)
ax.set_yticks([0, 1, 2, 3, 4])
ax.set_yticklabels(
    ['$0B', '$1B', '$2B', '$3B', '$4B'],
    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
    fontweight='bold',
    color=AXIS_CONFIG['y_tick']['color'],
)
ax.tick_params(axis='y', pad=AXIS_CONFIG['y_tick']['pad'], length=0)

# Right Y-axis: ylim 75 with ticks at [0, 15, 30, 45, 60] so positions match left axis grid (every 20%).
ax2.set_ylim(0, 75)
ax2.set_yticks([0, 15, 30, 45, 60])
ax2.set_yticklabels(
    ['$0B', '$15B', '$30B', '$45B', '$60B'],
    fontsize=AXIS_CONFIG['y_tick']['fontsize'],
    fontweight='bold',
    color=volume_color,
)
ax2.tick_params(axis='y', pad=AXIS_CONFIG['y_tick']['pad'], length=0)

# Style
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax2.set_facecolor('none')
ax.grid(
    True, axis='y',
    color=COLORS['grid'], alpha=0.5,
    linestyle=(0, (3.7, 1.6)), linewidth=1.0,
)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
for spine in ax2.spines.values():
    spine.set_visible(False)

fig.tight_layout()
fig.subplots_adjust(top=0.92)

output_dir = 'outputs/charts/paypal/stablecoin'
os.makedirs(output_dir, exist_ok=True)
png_path, svg_path = save_chart(fig, 'pyusd_supply_by_chain', output_dir)
print(f"Saved: {png_path}")
print(f"Saved: {svg_path}")
plt.close()

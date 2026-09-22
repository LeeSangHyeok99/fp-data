"""
Stablecoin 30D Net Flows - rwa.xyz data (04/09/2026)
Shows USDT regaining +$1.1B while USDC losing -$1.0B in last 30 days
Contrasts with Q1 trend where USDT was declining
Source: rwa.xyz/stablecoins
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.claude', 'skills', 'design', 'four-pillars'))
from config import create_figure, apply_style, save_chart, COLORS, POSITIVE_COLOR, NEGATIVE_COLOR

# ── Data from rwa.xyz (04/09/2026) ──
assets = ['USDT', 'DAI', 'USDG', 'USDS', 'USDe', 'RLUSD', 'USD1', 'USDC']
flows_m = [1100, 652, 628, 251, -81, -182, -244, -841]  # in millions
platforms = ['Tether', 'MakerDAO', 'Paxos', 'Sky', 'Ethena', 'RLUSD', 'BitGo', 'Circle']

# Brand colors
brand_colors = {
    'USDT': '#26a17b',
    'DAI': '#f5ac37',
    'USDG': '#003087',
    'USDS': '#1bab9b',
    'USDe': '#8b5cf6',
    'USD1': '#c9a84c',
    'RLUSD': '#005baa',
    'USDC': '#2775ca',
}


def gradient_hbar(ax, y_center, height, width, color, direction='right'):
    """0에서 시작해서 끝으로 갈수록 진해지는 수평 그라데이션 바 (imshow 기반, 매끄러움)"""
    from matplotlib.patches import FancyBboxPatch
    from matplotlib.path import Path as MPath
    from matplotlib.patches import PathPatch

    r, g, b = mcolors.to_rgb(color)
    y_bottom = y_center - height / 2

    if direction == 'right':
        x0, x1 = 0, width
    else:
        x0, x1 = width, 0

    # 256-step horizontal gradient image
    gradient = np.zeros((1, 256, 4))
    for i in range(256):
        frac = i / 255
        alpha = 0.08 + 0.87 * (frac ** 1.5)
        gradient[0, i] = [r, g, b, alpha]

    if direction == 'left':
        gradient = gradient[:, ::-1, :]

    im = ax.imshow(gradient, aspect='auto', origin='lower',
                   extent=[x0, x1, y_bottom, y_bottom + height],
                   interpolation='bicubic', zorder=3)


# ── Chart ──
fig, ax = create_figure('horizontal_bar')
fig.set_size_inches(11, 5)

y_pos = np.arange(len(assets))[::-1]

# Draw gradient bars
for i, (flow, asset) in enumerate(zip(flows_m, assets)):
    color = brand_colors[asset]
    direction = 'right' if flow >= 0 else 'left'
    gradient_hbar(ax, y_pos[i], 0.55, flow, color, direction)

# Value labels
for i, (flow, asset) in enumerate(zip(flows_m, assets)):
    if flow >= 0:
        sign = '+'
        x_pos = flow + 30
        ha = 'left'
    else:
        sign = ''
        x_pos = flow - 30
        ha = 'right'

    if abs(flow) >= 1000:
        label = f'{sign}{flow/1000:.1f}B'
    else:
        label = f'{sign}{flow}M'

    ax.text(x_pos, y_pos[i],
            label,
            va='center', ha=ha, fontsize=14, fontweight='bold',
            color=COLORS['text'])

# Y axis labels: ticker only
ax.set_yticks(y_pos)
ax.set_yticklabels(assets, fontsize=14, fontweight='bold', color=COLORS['text'])

# X axis
x_ticks = [-1000, -500, 0, 500, 1000]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'{v/1000:.1f}B' if abs(v) >= 1000 else f'{v}M' if v != 0 else '0' for v in x_ticks])
ax.set_xlim(-1400, 1500)

# Zero line
ax.axvline(x=0, color=COLORS['text_secondary'], linewidth=1, alpha=0.8)

# Grid
ax.grid(True, axis='x', color=COLORS['grid'], alpha=0.5,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.grid(False, axis='y')
ax.set_axisbelow(True)

# Style
fig.patch.set_alpha(0)
ax.set_facecolor('none')
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='x', labelsize=14, pad=10, colors=COLORS['text_secondary'], length=0)
ax.tick_params(axis='y', length=0)
fig.tight_layout()

output_dir = 'outputs/charts/stablecoin/market'
save_chart(fig, 'stablecoin_rwa_net_flows_30d', output_dir)
plt.close()
print(f'Saved to {output_dir}/stablecoin_rwa_net_flows_30d.png')

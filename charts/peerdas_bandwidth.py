"""
PeerDAS Average Sustained Download Bandwidth (Estimated)
3 operator types combined: Solo Stakers (32ETH), Medium Operator (1024ETH), Supernode (4096ETH)
"""
import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from config import (create_figure, apply_style, save_chart,
                    SERIES_COLORS, COLORS, AXIS_CONFIG, GRID_CONFIG,
                    area_glow, endpoint_dot, DPI, setup_font)

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/peerdas_bandwidth.csv')

x_labels = [f"{row['blob_count']}\n{row['label']}" for _, row in df.iterrows()]
x = np.arange(len(df))

series = {
    'Solo Stakers (32 ETH)': {'col': 'solo_stakers_32eth', 'color': '#5470c6'},
    'Medium Operator (1,024 ETH)': {'col': 'medium_operator_1024eth', 'color': '#91cc75'},
    'Supernode (4,096 ETH)': {'col': 'supernode_4096eth', 'color': '#fac858'},
}

baseline = 2.5  # Pectra 6 blobs baseline

# =============================================================================
# Chart
# =============================================================================
setup_font()
fig, ax = plt.subplots(figsize=(12, 5.5), dpi=DPI)

# Baseline dashed line
ax.axhline(y=baseline, color='#ef4444', linestyle='--', linewidth=1.5, alpha=0.6, zorder=2)
ax.text(1.8, baseline + 0.4, 'Baseline (Pectra 6 blobs)',
        color='#ef4444', fontsize=14, fontweight='bold', ha='center', va='bottom', alpha=0.8)

# Plot each series
for name, cfg in series.items():
    y = df[cfg['col']].values
    color = cfg['color']

    # Area glow
    area_glow(ax, x, y, color=color, n_layers=40, max_alpha=0.12, power=2.5)

    # Main line
    ax.plot(x, y, color=color, linewidth=2.5, zorder=4, label=name)

    # Data points
    ax.scatter(x, y, color=color, s=40, zorder=5, edgecolors='none')

    # Endpoint dot (larger)
    endpoint_dot(ax, x[-1], y[-1], color=color, size=70)

    # Value label at endpoint
    ax.text(x[-1] + 0.15, y[-1], f'{y[-1]:.1f}',
            color=color, fontsize=11, fontweight='bold', va='center', ha='left')


# =============================================================================
# Axes styling
# =============================================================================
apply_style(fig, ax, chart_type='line')

# X axis
ax.set_xticks(x)
ax.set_xticklabels(x_labels, fontsize=14, fontweight='bold',
                   color=COLORS['text'], ha='center')
ax.tick_params(axis='x', rotation=0, pad=10)

# Y axis - clean ticks at 5 intervals, max ~20
y_max = 20
ax.set_ylim(-1, y_max)
y_ticks = [0, 5, 10, 15, 20]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{v}' for v in y_ticks],
                   fontsize=14, fontweight='bold', color=COLORS['text_secondary'])

# Y axis unit as tick suffix
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{int(v)} Mbps'))

# Grid
ax.grid(True, axis='y', color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'], linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# Remove x grid
ax.grid(False, axis='x')

# Margins
ax.margins(x=0.05)

fig.tight_layout()

# =============================================================================
# Save
# =============================================================================
output_dir = 'outputs/charts/ethereum/bandwidth'
png_path, svg_path = save_chart(fig, 'peerdas_bandwidth', output_dir=output_dir)
print(f"Saved: {png_path}")
print(f"Saved: {svg_path}")
plt.close()

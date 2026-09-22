import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as np

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import (
    create_figure, apply_style, save_chart,
    COLORS, GRID_CONFIG
)

# ══════════════════════════════════════════════════
# Data
# ══════════════════════════════════════════════════
df = pd.read_csv('/tmp/sui_stablecoins_weekly.csv')
df['date'] = pd.to_datetime(df['date'])

# Fill NaN with 0
for col in ['USDC', 'USDT', 'FDUSD', 'BUCK', 'USDY', 'AUSD']:
    df[col] = df[col].fillna(0)

# Convert to $M
for col in ['USDC', 'USDT', 'FDUSD', 'BUCK', 'USDY', 'AUSD']:
    df[col] = df[col] / 1e6

# Stack order (largest at bottom)
stack_order = ['USDC', 'FDUSD', 'BUCK', 'USDT', 'USDY', 'AUSD']

# Brand-inspired colors
color_map = {
    'USDC':  '#2775CA',  # Circle blue
    'USDT':  '#50AF95',  # Tether green
    'FDUSD': '#E8B84B',  # First Digital gold
    'BUCK':  '#9a60b4',  # Purple (native Sui)
    'USDY':  '#fc8452',  # Ondo orange
    'AUSD':  '#73c0de',  # Agora light blue
}

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
fig, ax = create_figure('stacked')

stack_data = [df[col].values for col in stack_order]
colors = [color_map[col] for col in stack_order]

ax.stackplot(
    df['date'],
    *stack_data,
    colors=colors,
    alpha=0.85,
)

# ══════════════════════════════════════════════════
# USDsui launch annotation (vertical dashed line)
# ══════════════════════════════════════════════════
launch_date = pd.Timestamp('2026-03-04')
ax.axvline(x=launch_date, color='#d1d4dc', linestyle='--',
           linewidth=1.2, alpha=0.7, zorder=5)
ax.text(launch_date - pd.Timedelta(days=7), 1330, 'USDsui Launch',
        color=COLORS['text'], fontsize=10, fontweight='bold',
        va='top', ha='right', zorder=6)

# ══════════════════════════════════════════════════
# Y-axis ($M, max 5 ticks)
# ══════════════════════════════════════════════════
ax.set_ylim(0, 1400)
ax.set_yticks([0, 350, 700, 1050, 1400])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f'${int(x)}M'))

# ══════════════════════════════════════════════════
# X-axis
# ══════════════════════════════════════════════════
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['date'].min(), df['date'].max() + pd.Timedelta(days=14))

# ══════════════════════════════════════════════════
# Style
# ══════════════════════════════════════════════════
apply_style(fig, ax, 'stacked')
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(fig, 'sui_stablecoin_stacked',
                                'outputs/charts/sui')
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")

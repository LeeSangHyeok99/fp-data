import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, COLORS, DPI, GRID_CONFIG

output_dir = 'outputs/charts/hyperliquid/etf'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# HYPE ETF Daily Inflows by Deployer (Stacked Bar + Cumulative Line)
# Source: https://farside.co.uk/hyp/
# =============================================================================
setup_font()

df = pd.read_csv('outputs/data/farside_hype_etf_flow.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)
df['cumulative'] = df['total'].cumsum()

# Deployer brand colors
deployer_colors = {
    'THYP': '#10b981',   # 21Shares -> HRC neon green
    'BHYP': '#00d4ff',   # Bitwise -> HRC neon cyan
}
stack_order = ['THYP', 'BHYP']

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
ax2 = ax.twinx()

# Solid HRC green background
bg_color = '#0a3a34'
fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)
ax2.set_facecolor('none')

# Bar positioning by index (avoid weekend gaps making bars too thin)
x_pos = np.arange(len(df))
bar_width = 0.65

# Stacked bars (daily inflows, left axis)
bottom = np.zeros(len(df))
for series in stack_order:
    vals = df[series].values
    ax.bar(
        x_pos, vals, bar_width,
        bottom=bottom,
        color=deployer_colors[series],
        edgecolor='none',
        zorder=3,
    )
    bottom += vals

# Cumulative line (right axis)
cum_color = '#f59e0b'  # HRC amber
ax2.plot(
    x_pos, df['cumulative'].values,
    color=cum_color, linewidth=2.5,
    marker='o', markersize=5,
    markerfacecolor=cum_color, markeredgecolor=bg_color, markeredgewidth=1.5,
    zorder=4,
)

# Total label above each bar
totals = df['total'].values
y_max_data = totals.max()
for i, total in enumerate(totals):
    if total > 0:
        ax.text(
            x_pos[i], total + y_max_data * 0.04,
            f'${total:.1f}M',
            ha='center', va='bottom',
            fontsize=9, fontweight='bold',
            color='#ffffff',
            zorder=5,
        )

# Final cumulative label
last_cum = df['cumulative'].iloc[-1]
ax2.text(
    x_pos[-1], last_cum,
    f'  ${last_cum:.0f}M',
    ha='left', va='center',
    fontsize=10, fontweight='bold',
    color=cum_color,
    zorder=6,
)

# Left Y-axis: daily inflows
y_max_left = 35
y_ticks_left = [0, 10, 20, 30]
ax.set_yticks(y_ticks_left)
ax.set_yticklabels(
    [f'${v}M' for v in y_ticks_left],
    fontsize=12, fontweight='bold', color=COLORS['text_secondary'],
)
ax.set_ylim(0, y_max_left)
ax.tick_params(axis='y', length=0, pad=10)

# Right Y-axis: cumulative — match left axis tick count (4 ticks)
n_ticks = len(y_ticks_left)
cum_max = df['cumulative'].max()
step_right = int(np.ceil(cum_max / (n_ticks - 1) / 10.0)) * 10
y_ticks_right = [step_right * i for i in range(n_ticks)]
ax2.set_yticks(y_ticks_right)
ax2.set_yticklabels(
    [f'${v}M' for v in y_ticks_right],
    fontsize=12, fontweight='bold', color=cum_color,
)
# Match left axis padding: left top tick is 30, ylim is 35 → ratio 35/30
ax2.set_ylim(0, y_ticks_right[-1] * (y_max_left / y_ticks_left[-1]))
ax2.tick_params(axis='y', length=0, pad=10)

# X-axis: show every date
ax.set_xticks(x_pos)
ax.set_xticklabels(
    [d.strftime('%b %d') for d in df['date']],
    fontsize=12, fontweight='bold', color=COLORS['text_secondary'],
)
ax.tick_params(axis='x', length=6, width=1, pad=8, colors=COLORS['text_secondary'])
side_pad = 0.8
ax.set_xlim(-side_pad, len(df) - 1 + side_pad)

# Grid (HRC dashed) on left axis only
ax.grid(
    True, axis='y',
    color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
    linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'],
)
ax.set_axisbelow(True)

# Hide spines
for spine in ax.spines.values():
    spine.set_visible(False)
for spine in ax2.spines.values():
    spine.set_visible(False)

plt.subplots_adjust(top=0.96, bottom=0.13, left=0.08, right=0.93)

# Save PNG + SVG
png_path = Path(output_dir) / 'hype_etf_daily_inflows_by_deployer.png'
svg_path = Path(output_dir) / 'hype_etf_daily_inflows_by_deployer.svg'

fig.savefig(
    png_path, dpi=DPI,
    facecolor=bg_color, edgecolor='none',
    bbox_inches='tight',
)
# SVG: transparent background
fig.patch.set_facecolor('none')
ax.set_facecolor('none')
fig.savefig(
    svg_path, format='svg',
    facecolor='none', edgecolor='none',
    bbox_inches='tight',
    transparent=True,
)

plt.close(fig)
print(f'Saved: {png_path}')
print(f'Saved: {svg_path}')

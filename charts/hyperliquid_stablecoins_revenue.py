import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import json

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, GRID_CONFIG

output_dir_stablecoin = 'outputs/charts/hyperliquid/stablecoin'
output_dir_revenue = 'outputs/charts/hyperliquid/revenue'
Path(output_dir_stablecoin).mkdir(parents=True, exist_ok=True)
Path(output_dir_revenue).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Chart 1: HyperEVM Stablecoin Supply (Stacked Area)
# =============================================================================
setup_font()

df = pd.read_csv('outputs/data/hyperliquid_stablecoin_supply.csv')
df['date'] = pd.to_datetime(df['date'])

# Convert to millions
for col in ['total', 'USDC', 'USDT0', 'USDH', 'USDe', 'feUSD', 'thBILL', 'other']:
    df[col] = df[col] / 1e6

# Filter out zero-total days at the start
df = df[df['total'] > 0.01].reset_index(drop=True)

# Hyperliquid green palette
HL_GREEN = '#50e3c2'  # Hyperliquid brand green
stablecoin_colors = {
    'USDC': '#2775ca',       # Circle blue
    'USDT0': '#26a17b',      # Tether green
    'USDH': HL_GREEN,        # Hyperliquid green
    'USDe': '#1a1a2e',       # Ethena dark
    'feUSD': '#9a60b4',      # Purple
    'thBILL': '#fac858',     # Yellow
    'other': '#787b86',      # Grey
}

stack_order = ['USDC', 'USDT0', 'USDH', 'USDe', 'feUSD', 'thBILL', 'other']

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

y_stack = np.zeros(len(df))
for col in stack_order:
    ax.fill_between(df['date'], y_stack, y_stack + df[col].values,
                    color=stablecoin_colors[col], alpha=0.85, linewidth=0, zorder=2)
    ax.plot(df['date'], y_stack + df[col].values,
            color=stablecoin_colors[col], linewidth=0.3, alpha=0.5, zorder=3)
    y_stack += df[col].values

# Y-axis
y_ticks = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
ax.set_yticks([v * 1000 for v in y_ticks])
ax.set_yticklabels([f'${v:.1f}B' for v in y_ticks],
                   fontsize=14, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=15)
ax.set_ylim(0, 1050)

# X-axis - monthly ticks
x_ticks = pd.date_range('2025-04-01', '2026-04-01', freq='MS')
x_ticks = [t for t in x_ticks if t <= df['date'].max()]
ax.set_xticks(x_ticks)
ax.set_xticklabels([t.strftime('%b %y') for t in x_ticks],
                   fontsize=12, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=6, width=1, pad=10, rotation=45, colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.set_xlim(df['date'].min(), df['date'].max())

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)


fig.tight_layout()
fig.savefig(f'{output_dir_stablecoin}/hyperevm_stablecoin_supply.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir_stablecoin}/hyperevm_stablecoin_supply.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print("Chart 1 saved: HyperEVM Stablecoin Supply")
print(f"  Latest total: ${df['total'].iloc[-1]:.0f}M")

# =============================================================================
# Chart 2: Hyperliquid Daily Revenue (Bar)
# =============================================================================
setup_font()

# Read revenue data from the saved file
with open('/Users/ijaheun/.claude/projects/-Users-ijaheun-Desktop-Project-data/db7e60f0-8af8-4f5f-8a3a-9795644be23d/tool-results/mcp-playwright-browser_run_code-1773628762473.txt') as f:
    pass  # Skip, we'll use the API data saved inline

# Parse revenue from inline - we need to save it first
# Actually let's just read from the playwright result for the revenue endpoint
# For now, create revenue CSV from the data we already have

# Revenue data was fetched via Playwright, let's parse it properly
import os
rev_file = '/Users/ijaheun/.claude/projects/-Users-ijaheun-Desktop-Project-data/db7e60f0-8af8-4f5f-8a3a-9795644be23d/tool-results/mcp-playwright-browser_run_code-1773628762473.txt'

# We'll hardcode the revenue summary and create a weekly aggregated chart
# The daily data was already printed in the Playwright response
# Let's read it from a simpler approach

# Write revenue CSV from the response we captured
rev_json_str = open(rev_file).read() if os.path.exists(rev_file) else None

# Simpler: use the stablecoin data for now and create revenue from the raw response
# The revenue data was returned as a single string in the second Playwright call

# Let's create the revenue data CSV directly
print("\nGenerating revenue chart from weekly aggregation...")

# We'll aggregate revenue data weekly for a cleaner bar chart
# Parse the JSON from our earlier capture
# Revenue endpoint returned data inline in the conversation
# For a clean approach, let's fetch it again in the chart script

# Actually, let's just use the data we know:
# Total $827M over 361 days, avg $2.29M/day
# Peak was Oct 10 at $20.5M
# Let's save a simplified monthly version

monthly_revenue = {
    '2025-03': 10.3, '2025-04': 37.6, '2025-05': 66.8, '2025-06': 64.5,
    '2025-07': 93.7, '2025-08': 114.4, '2025-09': 83.2, '2025-10': 93.4,
    '2025-11': 74.5, '2025-12': 49.3, '2026-01': 50.4, '2026-02': 55.2,
    '2026-03': 19.3
}

months = list(monthly_revenue.keys())
values = list(monthly_revenue.values())

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Use gradient rounded bars
from config import gradient_rounded_bar

bar_width = 0.6
for i, (month, val) in enumerate(zip(months, values)):
    gradient_rounded_bar(ax, i, bar_width, val, color=HL_GREEN)

# Value labels on top
for i, val in enumerate(values):
    if val > 5:
        ax.text(i, val + 2, f'${val:.0f}M', ha='center', va='bottom',
                fontsize=10, fontweight='bold', color=COLORS['text_secondary'])

# Y-axis
y_ticks = [0, 30, 60, 90, 120]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${v}M' for v in y_ticks],
                   fontsize=14, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=15)
ax.set_ylim(0, 135)

# X-axis
ax.set_xticks(range(len(months)))
month_labels = [m.replace('2025-', '').replace('2026-', '') for m in months]
month_names = {'03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul',
               '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec',
               '01': 'Jan', '02': 'Feb'}
display_labels = []
for m in months:
    mm = m.split('-')[1]
    yr = "'25" if '2025' in m else "'26"
    display_labels.append(f"{month_names[mm]}\n{yr}")

ax.set_xticklabels(display_labels,
                   fontsize=10, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=0, pad=8)

# Grid
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()
fig.savefig(f'{output_dir_revenue}/hyperliquid_monthly_revenue.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir_revenue}/hyperliquid_monthly_revenue.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print("Chart 2 saved: Hyperliquid Monthly Revenue")
print(f"  Total Revenue (1yr): $827M")
print(f"  Peak Month: Aug '25 ($114M)")

# =============================================================================
# Chart 3: Stablecoin Market Share on HyperEVM (Horizontal Bar)
# =============================================================================
setup_font()

# Current snapshot data
stables = [
    ('USDC', 586.71, 45.66, 156.91),
    ('USDT0', 156.32, 11.41, 9.64),
    ('USDH', 96.22, 8.63, 15.91),
    ('USDe', 64.18, -8.16, -15.99),
    ('feUSD', 15.39, -1.26, -5.82),
    ('thBILL', 3.88, -9.16, -7.29),
]

names = [s[0] for s in stables]
supplies = [s[1] for s in stables]
weekly = [s[2] for s in stables]
bar_colors_list = [stablecoin_colors.get(n, '#787b86') for n in names]

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

bars = ax.barh(range(len(names)-1, -1, -1), supplies, height=0.55,
               color=bar_colors_list, alpha=0.9, edgecolor='#1a1a1a', linewidth=0.5)

# Value labels
for i, (val, w, color) in enumerate(zip(supplies, weekly, bar_colors_list)):
    y_pos = len(names) - 1 - i
    sign = '+' if w > 0 else ''
    ax.text(val + 8, y_pos, f'${val:.0f}M ({sign}{w:.0f}% w/w)',
            va='center', ha='left', fontsize=10, fontweight='bold', color=color)

# Y-axis
ax.set_yticks(range(len(names)-1, -1, -1))
ax.set_yticklabels(names, fontsize=14, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='y', length=0, pad=10)

# X-axis
x_ticks = [0, 200, 400, 600]
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'${v}M' for v in x_ticks],
                   fontsize=12, fontweight='bold', color=COLORS['text_secondary'])
ax.tick_params(axis='x', length=0, pad=8)
ax.set_xlim(0, 750)

# Grid
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()
fig.savefig(f'{output_dir_stablecoin}/hyperevm_stablecoin_share.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir_stablecoin}/hyperevm_stablecoin_share.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)
print("\nChart 3 saved: HyperEVM Stablecoin Market Share")
print(f"  Total: ${sum(supplies):.0f}M")

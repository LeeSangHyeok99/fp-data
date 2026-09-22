import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, GRID_CONFIG

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/futures_oi_comparison.csv', parse_dates=['Date'])

output_dir = 'outputs/charts/theo'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Colors
GOLD_C = '#C9A84C'
BTC_C = '#CCCCCC'
ETH_C = '#5BA5A5'

# =============================================================================
# Chart
# =============================================================================
setup_font()
fig, ax = plt.subplots(figsize=(14, 6), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

dates = df['Date']
gold = df['Gold_CME']
btc = df['BTC_Total']
eth = df['ETH_Total']

# --- Gold area fill with top-weighted gradient glow ---
n_layers = 50
for i in range(n_layers):
    frac = i / n_layers  # 0=bottom, 1=top (near line)
    # Stronger alpha near the line (top), fading to near-zero at bottom
    alpha = 0.18 * (frac ** 2.5)
    lower = gold * frac
    upper = gold * (frac + 1/n_layers)
    ax.fill_between(dates, lower, upper,
                    color=GOLD_C, alpha=alpha, linewidth=0, zorder=2)

# Gold line
ax.plot(dates, gold, color=GOLD_C, linewidth=1.8, zorder=4)
# Endpoint dot
ax.scatter(dates.iloc[-1], gold.iloc[-1], color=GOLD_C, s=50, zorder=5, edgecolors='none')

# --- BTC line + fill ---
ax.fill_between(dates, 0, btc, color=BTC_C, alpha=0.15, linewidth=0, zorder=2)
ax.plot(dates, btc, color=BTC_C, linewidth=1.5, zorder=4)
ax.scatter(dates.iloc[-1], btc.iloc[-1], color=BTC_C, s=40, zorder=5, edgecolors='none')

# --- ETH line + fill ---
ax.fill_between(dates, 0, eth, color=ETH_C, alpha=0.2, linewidth=0, zorder=2)
ax.plot(dates, eth, color=ETH_C, linewidth=1.5, zorder=4)
ax.scatter(dates.iloc[-1], eth.iloc[-1], color=ETH_C, s=40, zorder=5, edgecolors='none')

# --- Y-axis ---
y_ticks = [0, 50, 100, 150, 200, 250, 300]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'${v}B' for v in y_ticks],
                    fontsize=14, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_ylim(0, 310)
ax.tick_params(axis='y', length=0, pad=15)

# --- X-axis: fixed ticks at Jan 27, Feb 10, Feb 27 ---
import datetime
tick_dates = [datetime.datetime(2026, 1, 27), datetime.datetime(2026, 2, 10),
              datetime.datetime(2026, 2, 27)]
ax.set_xticks(tick_dates)
ax.set_xticklabels(['Jan 27', 'Feb 10', 'Feb 27'],
                     fontsize=14, fontweight='bold', color=COLORS['text_secondary'],
                     rotation=45, ha='right')
ax.tick_params(axis='x', length=0, pad=8)
ax.set_xlim(dates.iloc[0], datetime.datetime(2026, 2, 27))

# --- Grid ---
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

# --- Spines ---
for spine in ax.spines.values():
    spine.set_visible(False)

# --- Save ---
fig.savefig(f'{output_dir}/futures_oi_comparison.png', dpi=DPI,
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
fig.savefig(f'{output_dir}/futures_oi_comparison.svg', format='svg',
            facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
plt.close(fig)

print(f"Saved: {output_dir}/futures_oi_comparison.png")
print(f"Gold latest: ${gold.iloc[-1]}B, BTC: ${btc.iloc[-1]}B, ETH: ${eth.iloc[-1]}B")

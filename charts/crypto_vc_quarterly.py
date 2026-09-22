import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, COLORS, DPI, GRID_CONFIG, SERIES_COLORS

output_dir = 'outputs/charts/market/funding'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/crypto_vc_quarterly.csv')

# =============================================================================
# Chart: VC Funding Bars + BTC Price Line (dual axis) — HRC theme
# =============================================================================
setup_font()

fig, ax1 = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax1.set_facecolor('none')

x = np.arange(len(df))
bar_width = 0.6

# Bars: VC funding
bars = ax1.bar(x, df['vc_funding_b'], width=bar_width,
               color=SERIES_COLORS[2], alpha=0.8, zorder=3)  # neon green

# Highlight Q1 2026 (last bar)
bars[-1].set_color(SERIES_COLORS[0])  # neon cyan
bars[-1].set_alpha(0.9)

# Annotate Q1 2026
ax1.annotate(f'${df["vc_funding_b"].iloc[-1]:.1f}B',
             xy=(x[-1], df['vc_funding_b'].iloc[-1]),
             xytext=(0, 10), textcoords='offset points',
             ha='center', va='bottom',
             fontsize=13, fontweight='bold',
             color=SERIES_COLORS[0])

# Y axis left (VC funding)
y_ticks_left = [0, 2.5, 5, 7.5, 10]
ax1.set_yticks(y_ticks_left)
ax1.set_yticklabels([f'${v:.1f}B' if v % 1 else f'${int(v)}B' for v in y_ticks_left],
                     fontsize=15, fontweight='bold',
                     color=COLORS['text_secondary'])
ax1.set_ylim(0, 11)
ax1.tick_params(axis='y', length=0, pad=10)

# BTC price line on secondary axis
ax2 = ax1.twinx()
ax2.plot(x, df['btc_price_end'] / 1000, color='#f59e0b', linewidth=2.5,
         alpha=0.9, zorder=5, marker='o', markersize=5)

# Y axis right (BTC price)
y_ticks_right = [0, 25, 50, 75, 100]
ax2.set_yticks(y_ticks_right)
ax2.set_yticklabels([f'${int(v)}K' for v in y_ticks_right],
                     fontsize=15, fontweight='bold',
                     color='#f59e0b')
ax2.set_ylim(0, 110)
ax2.tick_params(axis='y', length=0, pad=10)

# X axis
ax1.set_xticks(x)
ax1.set_xticklabels(df['quarter'], fontsize=13, fontweight='bold',
                     color=COLORS['text_secondary'],
                     rotation=45, ha='right')
ax1.tick_params(axis='x', length=6, width=1, colors=COLORS['text_secondary'])

# Grid
ax1.grid(True, axis='y',
         color=GRID_CONFIG['color'],
         alpha=GRID_CONFIG['alpha'],
         linestyle=GRID_CONFIG['linestyle'],
         linewidth=GRID_CONFIG['linewidth'])
ax1.set_axisbelow(True)

# Spines
for spine in ax1.spines.values():
    spine.set_visible(False)
for spine in ax2.spines.values():
    spine.set_visible(False)

fig.tight_layout()

# Save
for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/crypto_vc_vs_btc.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )

plt.close()
print('Done: crypto_vc_vs_btc.png / .svg')
print(f'Q1 2026: ${df["vc_funding_b"].iloc[-1]}B / BTC ${df["btc_price_end"].iloc[-1]:,.0f}')
print(f'Q4 2025: ${df["vc_funding_b"].iloc[-2]}B / BTC ${df["btc_price_end"].iloc[-2]:,.0f}')

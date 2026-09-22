"""
S&P 500 Market Potential on HIP-3
침투율별 USA500 OI 성장 시나리오
"""
import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from config import (create_figure, apply_style, save_chart,
                    COLORS, gradient_rounded_bar)

# Data
df = pd.read_csv('outputs/data/hip3_sp500/sp500_potential.csv')

fig, ax = create_figure('bar')

# Colors: current = dim, scenarios = gradient of gold
colors = ['#787b86', '#fac858', '#f0b030', '#e89820', '#d47810']

x_pos = np.arange(len(df))
bar_width = 0.5

for i, (_, row) in enumerate(df.iterrows()):
    gradient_rounded_bar(ax, x_pos[i], bar_width, row['oi_billion'], colors[i])

    # Value on top
    if row['oi_billion'] < 1:
        val_text = f"${row['oi_billion']*1000:.0f}M"
    else:
        val_text = f"${row['oi_billion']:.1f}B"

    ax.text(x_pos[i], row['oi_billion'] + 0.3, val_text,
            ha='center', va='bottom', fontsize=12, fontweight='bold',
            color=COLORS['text'], zorder=6)

# Apply style
apply_style(fig, ax, 'bar')

# X axis labels
ax.set_xticks(x_pos)
labels = df['label'].tolist()
labels[0] = 'Current'
ax.set_xticklabels(labels, fontweight='bold', color=COLORS['text_secondary'],
                    fontsize=11, rotation=0, ha='center')

# Y axis
ax.set_ylim(0, max(df['oi_billion']) * 1.3)
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
y_ticks = ax.get_yticks()
ax.set_yticklabels([f'${v:.0f}B' for v in y_ticks],
                    fontweight='bold', color=COLORS['text_secondary'])

# Arrow annotation showing growth multiplier
current_val = df.iloc[0]['oi_billion']
for i in range(1, len(df)):
    multiplier = df.iloc[i]['oi_billion'] / current_val
    ax.text(x_pos[i], df.iloc[i]['oi_billion'] * 0.5, f'{multiplier:.0f}x',
            ha='center', va='center', fontsize=10, fontweight='bold',
            color='#141414', zorder=7, alpha=0.8)

fig.tight_layout()

# Save
save_chart(fig, 'hip3_sp500_potential',
           output_dir='outputs/charts/hyperliquid/hip3_sp500')
plt.close()
print("Chart 3 saved: hip3_sp500_potential")

"""
HIP-3 vs Traditional Finance OI Penetration Rate
각 HIP-3 마켓의 전통금융 OI 대비 침투율
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
df = pd.read_csv('outputs/data/hip3_sp500/hip3_vs_tradfi.csv')
df['penetration'] = (df['hip3_oi_m'] / (df['tradfi_oi_b'] * 1000)) * 100  # percentage

# Sort by penetration
df = df.sort_values('penetration', ascending=True).reset_index(drop=True)

fig, ax = create_figure('horizontal_bar')

# Colors per market
market_colors = {
    'Nasdaq 100': '#5470c6',
    'WTI Crude Oil': '#ee6666',
    'S&P 500': '#fac858',
    'Gold': '#C9A84C',
    'Silver': '#73c0de',
}

y_pos = np.arange(len(df))
bar_height = 0.55

for i, row in df.iterrows():
    color = market_colors.get(row['market'], '#5470c6')
    ax.barh(i, row['penetration'], height=bar_height, color=color, alpha=0.9, zorder=3)

    # Value label
    label_text = f"{row['penetration']:.2f}%"
    ax.text(row['penetration'] + 0.003, i, label_text,
            va='center', ha='left', fontsize=11, fontweight='bold',
            color=COLORS['text'], zorder=5)

    # Market labels (HIP-3 name → TradFi name)
    sublabel = f"{row['hip3_label']}  vs  {row['tradfi_label']}"
    ax.text(-0.002, i, sublabel,
            va='center', ha='right', fontsize=10, fontweight='bold',
            color=COLORS['text_secondary'], zorder=5)

# Apply style
apply_style(fig, ax, 'horizontal_bar')

# Axes
ax.set_yticks([])
ax.set_xlim(0, max(df['penetration']) * 1.5)
ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
x_ticks = ax.get_xticks()
ax.set_xticklabels([f'{v:.1f}%' for v in x_ticks],
                    fontweight='bold', color=COLORS['text_secondary'])

# Vertical grid instead of horizontal
ax.grid(True, axis='x', color=COLORS['grid'], alpha=0.5,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.grid(False, axis='y')

# Extra left margin for labels
fig.subplots_adjust(left=0.32)

# Save
save_chart(fig, 'hip3_vs_tradfi_penetration',
           output_dir='outputs/charts/hyperliquid/hip3_sp500')
plt.close()
print("Chart 2 saved: hip3_vs_tradfi_penetration")

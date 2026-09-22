"""
HIP-3 OI Growth Timeline
6개월간 $0 → $1.43B (100x growth)
"""
import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from config import (create_figure, apply_style, save_chart,
                    COLORS, area_glow, endpoint_dot)

# Data
df = pd.read_csv('outputs/data/hip3_sp500/hip3_oi_growth.csv', parse_dates=['date'])

fig, ax = create_figure('line')

# Main line
color = '#50e3c2'  # Hyperliquid brand teal
ax.plot(df['date'], df['oi_million'], color=color, linewidth=2.5, zorder=4)

# Area glow
area_glow(ax, df['date'], df['oi_million'].values, color=color, max_alpha=0.22, power=2.0)

# Endpoint dot
endpoint_dot(ax, df['date'].iloc[-1], df['oi_million'].iloc[-1], color=color, size=60)

# Key milestones as annotations
milestones = [
    ('2025-10-28', 70, '$70M\nOct 28'),
    ('2026-01-27', 793, '$793M\nJan 27'),
    ('2026-03-15', 1430, '$1.43B\nMar 15'),
]
for date_str, val, label in milestones:
    date = pd.Timestamp(date_str)
    ax.annotate(
        label,
        xy=(date, val),
        xytext=(0, 18),
        textcoords='offset points',
        fontsize=10,
        fontweight='bold',
        color=COLORS['text'],
        ha='center',
        va='bottom',
        zorder=6,
    )

# Apply style
apply_style(fig, ax, 'line')

# Y axis
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
ax.set_ylim(bottom=0)
y_ticks = ax.get_yticks()
ax.set_yticklabels([f'${int(v)}M' if v < 1000 else f'${v/1000:.1f}B' for v in y_ticks],
                    fontweight='bold', color=COLORS['text_secondary'])

# X axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')

# S&P 500 license event marker
sp500_date = pd.Timestamp('2026-03-18')
ax.axvline(sp500_date, color='#fac858', linestyle='--', alpha=0.6, linewidth=1.5, zorder=3)
ax.annotate(
    'S&P 500\nLicense',
    xy=(sp500_date, ax.get_ylim()[1] * 0.65),
    fontsize=9,
    fontweight='bold',
    color='#fac858',
    ha='left',
    va='center',
    xytext=(8, 0),
    textcoords='offset points',
    zorder=6,
)

fig.tight_layout()

# Save
save_chart(fig, 'hip3_oi_growth_timeline',
           output_dir='outputs/charts/hyperliquid/hip3_sp500')
plt.close()
print("Chart 1 saved: hip3_oi_growth_timeline")
